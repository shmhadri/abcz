import json
from collections import Counter

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from english_path.models import AssessmentResult, ReviewItem, UnitProgress
from english_path.services.a2_final import QUESTIONS
from english_path.services.daily_mission import build_daily_mission
from english_path.services.progress import select_due_review_items
from english_path.services.unit_schema import public_unit, validate_unit
from english_path.services.units import all_a1_units, all_a2_units, get_unit_content
from phonics.tests.subscription_helpers import grant_active_subscription


@override_settings(ENGLISH_PATH_ENABLED=True)
class A2JourneyTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="a2-learner", password="safe-test-password")
        grant_active_subscription(self.user, "english_journey")

    def pass_a1(self):
        for order in range(1, 21):
            UnitProgress.objects.create(user=self.user, unit_code=f"A1.{order}", score=100, status="excellent")
        AssessmentResult.objects.create(user=self.user, assessment_type="a1_final", level="A1 Master", score=100, skill_scores={skill: 100 for skill in ("vocabulary", "grammar", "reading", "listening", "speaking", "writing")})

    def pass_a2_units(self):
        self.pass_a1()
        for order in range(1, 11):
            UnitProgress.objects.create(user=self.user, unit_code=f"A2.{order}", score=100, status="excellent")

    def test_a2_first_unit_is_locked_until_a1_final_requirements(self):
        self.client.force_login(self.user)
        self.assertRedirects(self.client.get(reverse("english_path:unit", args=("a2-1",))), reverse("english_path:level", args=("a2",)))
        self.pass_a1()
        self.assertEqual(self.client.get(reverse("english_path:unit", args=("a2-1",))).status_code, 200)

    def test_every_a2_unit_has_valid_rich_schema_and_fade_metadata(self):
        expected = ["clear-toggle"] * 3 + ["optional"] * 3 + ["minimal-on-demand"] * 3 + ["english-first"]
        for content, support in zip(all_a2_units(), expected):
            self.assertEqual(validate_unit(content)["code"], content["code"])
            self.assertEqual(content["arabic_support"], support)
            self.assertTrue(content["review_from"])
            self.assertGreaterEqual(len(content["reading"]["passage"]), 250)
            self.assertTrue(content["speaking"]["independent"])

    def test_a2_progression_uses_server_graded_answers(self):
        self.pass_a1()
        self.client.force_login(self.user)
        content = get_unit_content("a2-1")
        answers = {item["id"]: item["answer"] for item in content["quiz"]}
        response = self.client.post(reverse("english_path:submit_unit_quiz", args=("a2-1",)), data=json.dumps({"answers": answers, "score": 0}), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["score"], 100)
        self.assertEqual(UnitProgress.objects.get(user=self.user, unit_code="A2.1").score, 100)
        self.assertEqual(self.client.get(reverse("english_path:unit", args=("a2-2",))).status_code, 200)
        self.assertEqual(build_daily_mission(self.user)["current_unit"]["code"], "A2.2")

    def test_spoof_invalid_and_malformed_a2_payloads_are_safe(self):
        self.pass_a1()
        self.client.force_login(self.user)
        url = reverse("english_path:submit_unit_quiz", args=("a2-1",))
        response = self.client.post(url, data=json.dumps({"answers": {}, "score": 100}), content_type="application/json")
        self.assertEqual(response.json()["score"], 0)
        self.assertEqual(self.client.post(url, data="{bad", content_type="application/json").status_code, 400)
        self.assertEqual(self.client.post(url, data=json.dumps({"answers": {"g1": "forged"}}), content_type="application/json").status_code, 400)

    def test_later_a2_unit_cannot_be_opened_or_posted_directly(self):
        self.pass_a1()
        self.client.force_login(self.user)
        self.assertRedirects(self.client.get(reverse("english_path:unit", args=("a2-4",))), reverse("english_path:level", args=("a2",)))
        content = get_unit_content("a2-4")
        answers = {item["id"]: item["answer"] for item in content["quiz"]}
        self.assertEqual(self.client.post(reverse("english_path:submit_unit_quiz", args=("a2-4",)), data=json.dumps({"answers": answers}), content_type="application/json").status_code, 403)

    def test_public_a2_payload_omits_final_quiz_keys(self):
        safe = public_unit(get_unit_content("a2-10"))
        for question in safe["quiz"]:
            self.assertNotIn("answer", question)
            self.assertNotIn("why_each_wrong", question)
            self.assertNotIn("similar_question", question)

    def test_repeated_subskill_priority_has_diversity_cap(self):
        for index in range(7):
            ReviewItem.objects.create(user=self.user, unit_code="A2.1", item_key=f"repeat-{index}", prompt="P", answer="A", skill="grammar", subskill="repeated", error_count=10-index, next_review_at=timezone.now())
        for index in range(3):
            ReviewItem.objects.create(user=self.user, unit_code="A2.2", item_key=f"other-{index}", prompt="P", answer="A", skill="listening", subskill=f"other-{index}", error_count=1, next_review_at=timezone.now())
        chosen = select_due_review_items(self.user, 5)
        counts = Counter(item.subskill for item in chosen)
        self.assertEqual(len(chosen), 5)
        self.assertLessEqual(counts["repeated"], 2)
        mission = build_daily_mission(self.user)
        self.assertEqual(set(mission["review_item_ids"]), {item.id for item in chosen})

    def test_a2_final_is_locked_until_all_units_are_mastered(self):
        self.pass_a1()
        self.client.force_login(self.user)
        self.assertRedirects(self.client.get(reverse("english_path:a2_final")), reverse("english_path:level", args=("a2",)))
        self.assertEqual(self.client.post(reverse("english_path:submit_a2_final"), data={}).status_code, 403)

    def test_a2_final_has_balanced_24_questions_and_grades_server_side(self):
        self.pass_a2_units()
        self.client.force_login(self.user)
        self.assertEqual(len(QUESTIONS), 24)
        self.assertEqual(Counter(item["skill"] for item in QUESTIONS), {"vocabulary": 6, "grammar": 6, "reading": 6, "listening": 6})
        data = {item["id"]: item["answer"] for item in QUESTIONS}
        data.update({"speaking": ["0", "1", "2", "3"], "writing": ["0", "1", "2", "3"]})
        response = self.client.post(reverse("english_path:submit_a2_final"), data=data)
        self.assertRedirects(response, reverse("english_path:a2_final"))
        result = AssessmentResult.objects.get(user=self.user, assessment_type="a2_final")
        self.assertEqual((result.score, result.level), (100, "A2 Master"))

    def test_journey_report_requires_a_passed_a2_final_and_is_user_scoped(self):
        self.pass_a2_units()
        self.client.force_login(self.user)
        self.assertRedirects(self.client.get(reverse("english_path:journey_completion")), reverse("english_path:level", args=("a2",)))
        AssessmentResult.objects.create(user=self.user, assessment_type="a2_final", level="A2 Master", score=100, skill_scores={skill: 100 for skill in ("vocabulary", "grammar", "reading", "listening", "speaking", "writing")})
        response = self.client.get(reverse("english_path:journey_completion"))
        self.assertContains(response, "You completed the Smart English Journey A1–A2.")
        self.assertNotContains(response, "Official CEFR Certificate")

    def test_anonymous_final_and_report_redirect_to_login(self):
        self.assertIn("/accounts/login/", self.client.get(reverse("english_path:a2_final")).url)
        self.assertIn("/accounts/login/", self.client.get(reverse("english_path:journey_completion")).url)

    def test_a1_content_remains_registered(self):
        self.assertEqual(len(all_a1_units()), 20)
        self.assertEqual(get_unit_content("a1-1")["code"], "A1.1")


class A2FeatureFlagTests(TestCase):
    def test_a2_is_hidden_while_feature_flag_is_false(self):
        user = get_user_model().objects.create_user(username="hidden-a2", password="safe-test-password")
        self.client.force_login(user)
        with override_settings(ENGLISH_PATH_ENABLED=False):
            self.assertEqual(self.client.get(reverse("english_path:unit", args=("a2-1",))).status_code, 404)
            self.assertEqual(self.client.get(reverse("english_path:a2_final")).status_code, 404)
