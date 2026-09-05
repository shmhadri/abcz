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
from english_path.services.unit_schema import UnitSchemaError, public_unit, validate_unit
from english_path.services.units import all_a1_units, get_unit_content
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
        self.assertEqual(UnitProgress.objects.get(user=self.user, unit_code="A1.1").score, 100)
        self.assertEqual(self.client.get(reverse("english_path:unit", args=("a1-2",))).status_code, 200)

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
        for order in range(1, 11):
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
        for order in range(1, 11):
            UnitProgress.objects.create(user=self.user, unit_code=f"A1.{order}", score=100, status="excellent")
        response = self.client.post(reverse("english_path:submit_a1_final"), data={})
        self.assertRedirects(response, reverse("english_path:a1_final"))
        self.assertEqual(ReviewItem.objects.filter(user=self.user, unit_code="A1-FINAL").count(), 10)
        self.assertRedirects(self.client.get(reverse("english_path:unit", args=("a2-1",))), reverse("english_path:level", args=("a2",)))


class UnitSchemaTests(TestCase):
    def test_incomplete_unit_fails_validation(self):
        with self.assertRaises(UnitSchemaError):
            validate_unit({"code": "A1.99"})
