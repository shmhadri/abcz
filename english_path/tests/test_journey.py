import json

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from django.utils.html import escape

from english_path.models import AssessmentResult, ReviewItem, ReviewSession, UnitProgress
from english_path.services.a1_unit_1 import QUIZ
from english_path.services.a1_final import QUESTIONS as FINAL_QUESTIONS
from english_path.services.daily_mission import build_daily_mission
from english_path.services.grading import grade_quiz
from english_path.services.unit_schema import UnitSchemaError, public_unit, validate_unit
from english_path.services.units import all_a1_units, all_a2_units, get_unit_content
from phonics.tests.subscription_helpers import grant_active_subscription


class FeatureFlagTests(TestCase):
    def test_journey_is_hidden_by_default(self):
        self.assertEqual(self.client.get("/english/").status_code, 404)

    @override_settings(ENGLISH_PATH_ENABLED=True)
    def test_overview_is_public_and_legacy_route_still_resolves(self):
        self.assertEqual(self.client.get(reverse("english_path:overview")).status_code, 200)
        self.assertEqual(reverse("placement_test"), "/placement-test/")
        self.assertEqual(reverse("games_center"), "/games/")


@override_settings(ENGLISH_PATH_ENABLED=True)
class JourneyAccessTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="learner", password="safe-test-password")
        grant_active_subscription(self.user, "english_journey")

    def test_personal_pages_require_login(self):
        response = self.client.get(reverse("english_path:dashboard"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response.url)

    def test_user_cannot_answer_another_users_review_item(self):
        other = get_user_model().objects.create_user(username="other", password="safe-test-password")
        item = ReviewItem.objects.create(user=other, unit_code="A1.1", item_key="other-item", prompt="Question", answer="Answer", skill="grammar", next_review_at=timezone.now())
        self.client.force_login(self.user)
        response = self.client.post(reverse("english_path:review_answer", args=(item.id,)), data=json.dumps({"correct": True}), content_type="application/json")
        self.assertEqual(response.status_code, 404)

    def test_mastery_unlocks_next_unit_and_keeps_best_score(self):
        self.client.force_login(self.user)
        level_url = reverse("english_path:level", args=("a1",))
        self.assertContains(self.client.get(level_url), "أكمل شرط الإتقان السابق")
        UnitProgress.objects.create(user=self.user, unit_code="A1.1", score=85, status="mastered")
        content = get_unit_content("a1-2")
        answers = {question["id"]: question["answer"] for question in content["quiz"]}
        save_url = reverse("english_path:submit_unit_quiz", args=("a1-2",))
        first = self.client.post(save_url, data=json.dumps({"answers": answers, "score": 0}), content_type="application/json")
        second = self.client.post(save_url, data=json.dumps({"answers": {}}), content_type="application/json")
        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 200)
        progress = UnitProgress.objects.get(user=self.user, unit_code="A1.2")
        self.assertEqual(progress.score, 100)
        self.assertEqual(progress.attempts, 2)
        self.assertEqual(self.client.get(reverse("english_path:unit", args=("a1-3",))).status_code, 200)

    def test_invalid_progress_is_rejected(self):
        self.client.force_login(self.user)
        UnitProgress.objects.create(user=self.user, unit_code="A1.1", score=85, status="mastered")
        url = reverse("english_path:save_progress", args=("a1-2",))
        response = self.client.post(url, data=json.dumps({"score": 101, "skills": {}}), content_type="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertFalse(UnitProgress.objects.filter(unit_code="A1.2").exists())

    def test_locked_unit_cannot_be_completed_through_api(self):
        self.client.force_login(self.user)
        content = get_unit_content("a1-2")
        answers = {question["id"]: question["answer"] for question in content["quiz"]}
        url = reverse("english_path:submit_unit_quiz", args=("a1-2",))
        response = self.client.post(url, data=json.dumps({"answers": answers}), content_type="application/json")
        self.assertEqual(response.status_code, 403)
        self.assertFalse(UnitProgress.objects.exists())

    def test_a2_stays_locked_until_a1_final_unit_is_mastered(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("english_path:unit", args=("a2-1",)))
        self.assertRedirects(response, reverse("english_path:level", args=("a2",)))

    def test_mistake_is_added_to_review_queue(self):
        self.client.force_login(self.user)
        UnitProgress.objects.create(user=self.user, unit_code="A1.1", score=85, status="mastered")
        content = get_unit_content("a1-2")
        answers = {question["id"]: question["answer"] for question in content["quiz"]}
        answers["g1"] = "have"
        url = reverse("english_path:submit_unit_quiz", args=("a1-2",))
        response = self.client.post(url, data=json.dumps({"answers": answers}), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(ReviewItem.objects.filter(user=self.user, item_key="A1.2-g1", subskill="have-has").exists())

    def test_a1_unit_one_rejects_self_reported_progress(self):
        self.client.force_login(self.user)
        url = reverse("english_path:save_progress", args=("a1-1",))
        response = self.client.post(url, data=json.dumps({"score": 100, "skills": {"grammar": 100}}), content_type="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"], "verified_quiz_required")
        self.assertFalse(UnitProgress.objects.exists())

    def test_a1_unit_one_renders_complete_reference_journey(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("english_path:unit", args=("a1-1",)))
        self.assertEqual(response.status_code, 200)
        for text in ("Vocabulary", "Grammar Lab", "Listening Lab", "Speaking Studio", "Reading", "Writing Workshop", "Skill Games", "Mission", "Unit Quiz"):
            self.assertContains(response, text)
        self.assertContains(response, "سبب خطأ اختيارك")

    def test_verified_quiz_score_unlocks_next_unit(self):
        self.client.force_login(self.user)
        answers = {question["id"]: question["answer"] for question in QUIZ}
        response = self.client.post(
            reverse("english_path:submit_unit_quiz", args=("a1-1",)),
            data=json.dumps({"answers": answers, "score": 0}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["score"], 100)
        self.assertTrue(response.json()["mastered"])
        self.assertEqual(response.json()["next_unit"]["url"], reverse("english_path:unit", args=("a1-2",)))
        self.assertEqual(UnitProgress.objects.get(user=self.user, unit_code="A1.1").score, 100)
        self.assertEqual(self.client.get(reverse("english_path:unit", args=("a1-2",))).status_code, 200)

    def test_a1_unit_navigation_uses_safe_named_routes(self):
        self.client.force_login(self.user)
        UnitProgress.objects.create(user=self.user, unit_code="A1.1", score=85, status="mastered")
        response = self.client.get(reverse("english_path:unit", args=("a1-2",)))
        self.assertContains(response, f'href="{reverse("index")}"')
        self.assertContains(response, f'href="{reverse("english_path:level", args=("a1",))}"')
        self.assertContains(response, f'href="{reverse("english_path:unit", args=("a1-1",))}"')
        self.assertNotContains(response, f'href="{reverse("english_path:unit", args=("a1-3",))}"')

    def test_a1_level_has_continue_learning_with_safe_server_fallback(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("english_path:level", args=("a1",)))
        self.assertContains(response, "Continue Learning")
        self.assertContains(response, f'data-continue-link href="{reverse("english_path:unit", args=("a1-1",))}"')
        self.assertContains(response, "data-storage-scope")

    def test_phase_two_controls_and_storage_are_a1_only(self):
        self.client.force_login(self.user)
        a1 = self.client.get(reverse("english_path:unit", args=("a1-1",)))
        self.assertContains(a1, "data-section-count")
        self.assertContains(a1, "data-clear-draft")
        self.assertContains(a1, "a1_phase2.css")
        a2_level = self.client.get(reverse("english_path:level", args=("a2",)))
        self.assertNotContains(a2_level, "Continue Learning")
        self.assertNotContains(a2_level, "a1_phase2.css")

    def test_completion_cta_never_bypasses_subscription_access(self):
        free_user = get_user_model().objects.create_user(username="free-phase-two", password="safe-test-password")
        self.client.force_login(free_user)
        answers = {question["id"]: question["answer"] for question in QUIZ}
        response = self.client.post(
            reverse("english_path:submit_unit_quiz", args=("a1-1",)),
            data=json.dumps({"answers": answers}),
            content_type="application/json",
        )
        self.assertTrue(response.json()["mastered"])
        self.assertNotIn("next_unit", response.json())
        self.assertRedirects(
            self.client.get(reverse("english_path:unit", args=("a1-2",))),
            reverse("english_path:level", args=("a1",)),
        )

    def test_score_spoof_does_not_unlock_next_unit(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("english_path:submit_unit_quiz", args=("a1-1",)),
            data=json.dumps({"answers": {}, "score": 100}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["score"], 0)
        self.assertEqual(UnitProgress.objects.get(user=self.user, unit_code="A1.1").score, 0)
        self.assertRedirects(self.client.get(reverse("english_path:unit", args=("a1-2",))), reverse("english_path:level", args=("a1",)))

    def test_wrong_answer_explains_choice_and_enters_review(self):
        self.client.force_login(self.user)
        answers = {question["id"]: question["answer"] for question in QUIZ}
        answers["grammar-she"] = "am"
        response = self.client.post(
            reverse("english_path:submit_unit_quiz", args=("a1-1",)),
            data=json.dumps({"answers": answers}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        feedback = next(item for item in response.json()["feedback"] if item["id"] == "grammar-she")
        self.assertFalse(feedback["correct"])
        self.assertEqual(feedback["correct_answer"], "is")
        self.assertIn("only used with I", feedback["why_wrong"])
        self.assertIn("similar", feedback)
        self.assertTrue(ReviewItem.objects.filter(user=self.user, item_key="A1.1-grammar-she", skill="grammar").exists())

    def test_similar_question_is_checked_on_server(self):
        self.client.force_login(self.user)
        url = reverse("english_path:check_similar_question", args=("a1-1",))
        response = self.client.post(url, data=json.dumps({"question_id": "grammar-she", "answer": "is"}), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()["correct"])
        self.assertIn("He, she and it", response.json()["explanation"])

    def test_every_a1_unit_loads_and_uses_valid_schema(self):
        self.client.force_login(self.user)
        for unit in all_a1_units():
            self.assertEqual(validate_unit(unit)["code"], unit["code"])
            UnitProgress.objects.update_or_create(user=self.user, unit_code=unit["code"], defaults={"score": 100, "status": "excellent"})
            response = self.client.get(reverse("english_path:unit", args=(unit["code"].lower().replace(".", "-"),)))
            self.assertEqual(response.status_code, 200, unit["code"])
            self.assertContains(response, escape(unit["title"]))

    def test_phase_three_curriculum_contract_for_every_a1_unit(self):
        for unit in all_a1_units():
            self.assertEqual(unit["phase3_version"], 1, unit["code"])
            self.assertEqual(len(unit["can_do_statements"]), 4, unit["code"])
            self.assertTrue(all(goal.startswith("I can ") for goal in unit["can_do_statements"]), unit["code"])
            self.assertGreaterEqual(len(unit["useful_expressions"]), 3, unit["code"])
            self.assertTrue(all(item["group"] == "core" for item in unit["vocabulary"]), unit["code"])
            self.assertTrue(all(item.get("audio", {}).get("lang") == "en-GB" for item in unit["vocabulary"]), unit["code"])
            self.assertEqual(
                [item["stage"] for item in unit["grammar"]["practice"]],
                ["Choose", "Complete", "Build sentence", "Correct mistake", "Use it in context"],
                unit["code"],
            )
            self.assertEqual(len(unit["listening"]["stages"]), 3, unit["code"])
            self.assertEqual(len(unit["speaking"]["rubric"]), 4, unit["code"])
            self.assertTrue(unit["writing"]["guided"] and unit["writing"]["semi_guided"] and unit["writing"]["independent"], unit["code"])
            self.assertGreaterEqual(len(unit["games"]), 4, unit["code"])
            self.assertTrue(
                {"speaking", "listening", "vocabulary", "grammar"}.issubset(
                    set(unit["mission"]["integrated_skills"])
                )
            )

    def test_spiral_review_only_uses_earlier_a1_units_and_stays_focused(self):
        for unit in all_a1_units():
            earlier = {f"A1.{order}" for order in range(1, unit["order"])}
            self.assertTrue(set(unit["review_from"]).issubset(earlier), unit["code"])
            expected_count = 0 if unit["order"] == 1 else 2
            self.assertEqual(len(unit["spiral_review"]["items"]), expected_count, unit["code"])
            if expected_count:
                self.assertEqual(unit["spiral_review"]["ratio"], "80/20", unit["code"])

    def test_phase_three_choice_activities_have_one_unique_answer(self):
        for unit in all_a1_units():
            activities = [unit["listening"]["gist_question"], *unit["spiral_review"]["items"]]
            activities.extend(item for item in unit["grammar"]["practice"] if item.get("choices"))
            activities.extend(game for game in unit["games"] if game.get("choices"))
            for activity in activities:
                self.assertEqual(len(activity["choices"]), len(set(activity["choices"])), unit["code"])
                self.assertEqual(activity["choices"].count(activity["answer"]), 1, unit["code"])

    def test_productive_practice_is_not_reported_as_automatic_skill_score(self):
        unit = get_unit_content("a1-1")
        answers = {question["id"]: question["answer"] for question in unit["quiz"]}
        result = grade_quiz(unit, answers)
        self.assertEqual(result["score"], 100)
        self.assertEqual(result["skills"]["speaking"], 0)
        self.assertEqual(result["skills"]["writing"], 0)
        self.assertEqual(result["productive_practice"], ["speaking", "writing"])
        for question in unit["quiz"]:
            if question["skill"] in {"speaking", "writing"}:
                self.assertFalse(question["productive_score"])

    def test_phase_three_corrects_identified_language_defects(self):
        serialised = {unit["code"]: json.dumps(unit, ensure_ascii=False) for unit in all_a1_units()}
        self.assertNotIn("They takes are", serialised["A1.5"])
        self.assertIn("Would you like some juice?", serialised["A1.6"])
        self.assertNotIn("Two windows is plural", serialised["A1.7"])
        self.assertIn("swim and ride a bike", serialised["A1.9"])
        self.assertIn("Use did + base verb", serialised["A1.10"])

    def test_phase_four_removes_ungrammatical_explanation_phrases(self):
        serialised = json.dumps(all_a1_units(), ensure_ascii=False)
        banned = (
            "I takes am", "You takes are", "She takes is", "He takes is",
            "She takes doesn’t", "He takes doesn’t", "He takes Does",
            "Two windows is plural", "Three chairs is plural",
            "Plural two beds takes", "One table takes there is",
            "question takes there", "Those takes are", "they takes were",
            "We takes were", "I takes was", "She takes was",
            "takes base verb",
        )
        for phrase in banned:
            self.assertNotIn(phrase, serialised, phrase)

    def test_phase_four_removes_ambiguous_or_culturally_specific_distractors(self):
        food = get_unit_content("a1-6")
        self.assertIn("eat rather than drink", next(item for item in food["quiz"] if item["id"] == "v1")["similar_question"]["prompt"])
        self.assertNotIn("Would you like any", json.dumps(food, ensure_ascii=False))
        home = get_unit_content("a1-7")
        sleep_choices = next(item for item in home["quiz"] if item["id"] == "v2")["similar_question"]["choices"]
        self.assertEqual(sleep_choices, ("bed", "table", "window"))
        self.assertNotIn("between desk and bed", json.dumps(home, ensure_ascii=False))
        weekend = get_unit_content("a1-10")
        prompt = next(item for item in weekend["quiz"] if item["id"] == "v1")["similar_question"]["prompt"]
        self.assertNotIn("Saturday and Sunday", prompt)
        self.assertIn("تجاوز الحديقة سيرًا", json.dumps(get_unit_content("a1-8"), ensure_ascii=False))

    def test_phase_three_ui_and_readiness_review_are_a1_only(self):
        self.client.force_login(self.user)
        a1 = self.client.get(reverse("english_path:unit", args=("a1-1",)))
        for marker in ("a1_phase3.css", "Listen for gist", "data-transcript-locked", "speaking-rubric", "Guided Writing", "Auto-scored language choice"):
            self.assertContains(a1, marker)
        level = self.client.get(reverse("english_path:level", args=("a1",)))
        self.assertContains(level, "A1 Readiness Review")
        self.assertContains(level, reverse("english_path:review"))
        self.assertTrue(all("phase3_version" not in unit for unit in all_a2_units()))
        a2_level = self.client.get(reverse("english_path:level", args=("a2",)))
        self.assertNotContains(a2_level, "a1_phase3.css")
        self.assertNotContains(a2_level, "A1 Readiness Review")

    def test_every_a1_listening_quiz_has_primary_and_follow_up_audio(self):
        for unit in all_a1_units():
            listening_questions = [question for question in unit["quiz"] if question["skill"] == "listening"]
            self.assertTrue(listening_questions, unit["code"])
            for question in listening_questions:
                self.assertTrue(question.get("spoken"), f"{unit['code']} {question['id']} primary audio")
                self.assertTrue(question["similar_question"].get("spoken"), f"{unit['code']} {question['id']} follow-up audio")
                self.assertNotIn(question["spoken"], question["prompt"])

    def test_every_a1_missing_word_game_has_one_explicit_answer(self):
        for unit in all_a1_units():
            games = [game for game in unit["games"] if game["type"] == "missing_word"]
            self.assertEqual(len(games), 1, unit["code"])
            game = games[0]
            self.assertIn("___", game["prompt"])
            self.assertEqual(game["choices"].count(game["answer"]), 1)
            self.assertEqual(len(game["choices"]), len(set(game["choices"])))

    def test_wrong_listening_answer_returns_audio_for_similar_question(self):
        self.client.force_login(self.user)
        UnitProgress.objects.create(user=self.user, unit_code="A1.1", score=85, status="mastered")
        content = get_unit_content("a1-2")
        answers = {question["id"]: question["answer"] for question in content["quiz"]}
        answers["l1"] = "doctor"
        response = self.client.post(
            reverse("english_path:submit_unit_quiz", args=("a1-2",)),
            data=json.dumps({"answers": answers}),
            content_type="application/json",
        )
        feedback = next(item for item in response.json()["feedback"] if item["id"] == "l1")
        self.assertEqual(feedback["similar"]["spoken"], "Her mother is a doctor.")

    def test_public_unit_never_contains_quiz_answer_keys(self):
        safe = public_unit(get_unit_content("a1-4"))
        self.assertTrue(safe["quiz"])
        for question in safe["quiz"]:
            self.assertNotIn("answer", question)
            self.assertNotIn("why_each_wrong", question)
            self.assertNotIn("similar_question", question)

    def test_malformed_and_forged_answers_are_rejected(self):
        self.client.force_login(self.user)
        url = reverse("english_path:submit_unit_quiz", args=("a1-1",))
        self.assertEqual(self.client.post(url, data="{bad", content_type="application/json").status_code, 400)
        response = self.client.post(url, data=json.dumps({"answers": {"grammar-i": "<script>"}, "score": 100}), content_type="application/json")
        self.assertEqual(response.status_code, 400)
        self.assertFalse(UnitProgress.objects.exists())

    def test_invalid_unit_code_is_rejected(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("english_path:submit_unit_quiz", args=("a1-99",)), data=json.dumps({"answers": {}}), content_type="application/json")
        self.assertEqual(response.status_code, 400)

    def test_review_session_contains_only_current_users_due_items(self):
        other = get_user_model().objects.create_user(username="review-other", password="safe-test-password")
        mine = ReviewItem.objects.create(user=self.user, unit_code="A1.1", item_key="mine", prompt="Mine", answer="A", skill="grammar", subskill="be", next_review_at=timezone.now())
        ReviewItem.objects.create(user=other, unit_code="A1.1", item_key="other", prompt="Other", answer="B", skill="grammar", next_review_at=timezone.now())
        self.client.force_login(self.user)
        response = self.client.post(reverse("english_path:start_review_session"))
        session = ReviewSession.objects.get(user=self.user)
        self.assertEqual(session.item_ids, [mine.id])
        self.assertRedirects(response, f"{reverse('english_path:review')}?session={session.id}")

    def test_review_answer_reschedules_item(self):
        item = ReviewItem.objects.create(user=self.user, unit_code="A1.1", item_key="schedule", prompt="Question", answer="Answer", skill="grammar", next_review_at=timezone.now())
        self.client.force_login(self.user)
        response = self.client.post(reverse("english_path:review_answer", args=(item.id,)), data=json.dumps({"correct": True}), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        item.refresh_from_db()
        self.assertEqual(item.mastery, 1)
        self.assertEqual(item.interval_days, 2)
        self.assertGreater(item.next_review_at, timezone.now())

    def test_daily_mission_prioritizes_due_review_and_is_small(self):
        ReviewItem.objects.create(user=self.user, unit_code="A1.1", item_key="due", prompt="Due", answer="A", skill="listening", next_review_at=timezone.now())
        mission = build_daily_mission(self.user)
        self.assertEqual(mission["minutes"], 12)
        self.assertEqual(mission["tasks"][0]["kind"], "review")
        self.assertLessEqual(len(mission["review_item_ids"]), 5)
        self.assertLessEqual(len(mission["tasks"]), 5)

    def test_a1_final_is_independent_and_unlocks_a2_server_side(self):
        self.client.force_login(self.user)
        for order in range(1, 21):
            UnitProgress.objects.create(user=self.user, unit_code=f"A1.{order}", score=100, status="excellent")
        answers = {item["id"]: item["answer"] for item in FINAL_QUESTIONS}
        data = {**answers, "speaking": ["0", "1", "2", "3"], "writing": ["0", "1", "2", "3"]}
        response = self.client.post(reverse("english_path:submit_a1_final"), data=data)
        self.assertRedirects(response, reverse("english_path:a1_final"))
        result = AssessmentResult.objects.get(user=self.user, assessment_type="a1_final")
        self.assertEqual(result.score, 100)
        self.assertEqual(result.level, "A1 Master")
        self.assertEqual(self.client.get(reverse("english_path:unit", args=("a2-1",))).status_code, 200)

    def test_a1_final_cannot_be_submitted_before_a1_completion(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("english_path:submit_a1_final"), data={})
        self.assertEqual(response.status_code, 403)
        self.assertFalse(AssessmentResult.objects.exists())

    def test_failed_a1_final_creates_targeted_remediation_and_keeps_a2_locked(self):
        self.client.force_login(self.user)
        for order in range(1, 21):
            UnitProgress.objects.create(user=self.user, unit_code=f"A1.{order}", score=100, status="excellent")
        response = self.client.post(reverse("english_path:submit_a1_final"), data={})
        self.assertRedirects(response, reverse("english_path:a1_final"))
        self.assertEqual(ReviewItem.objects.filter(user=self.user, unit_code="A1-FINAL").count(), 10)
        self.assertRedirects(self.client.get(reverse("english_path:unit", args=("a2-1",))), reverse("english_path:level", args=("a2",)))


class UnitSchemaTests(TestCase):
    def test_incomplete_unit_fails_validation(self):
        with self.assertRaises(UnitSchemaError):
            validate_unit({"code": "A1.99"})
