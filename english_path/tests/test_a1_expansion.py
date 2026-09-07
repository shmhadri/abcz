from collections import Counter

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from english_path.models import UnitProgress
from english_path.services.a1_final import QUESTIONS as A1_FINAL_QUESTIONS
from english_path.services.a1_phase3 import A1_READINESS_REVIEW
from english_path.services.access import FREE_UNIT_CODES
from english_path.services.curriculum import LEVELS
from english_path.services.progress import a1_course_complete
from english_path.services.unit_schema import validate_unit
from english_path.services.units import all_a1_units, all_a2_units
from phonics.tests.subscription_helpers import grant_active_subscription


@override_settings(ENGLISH_PATH_ENABLED=True)
class A1ExpansionTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="a1-expanded-learner", password="safe-test-password"
        )
        grant_active_subscription(self.user, "english_journey")
        self.client.force_login(self.user)

    def test_a1_has_twenty_ordered_units_and_a2_is_unchanged(self):
        units = all_a1_units()
        self.assertEqual([unit["code"] for unit in units], [f"A1.{order}" for order in range(1, 21)])
        self.assertEqual([row[0] for row in LEVELS["a1"]["units"]], [unit["code"] for unit in units])
        self.assertEqual(len(all_a2_units()), 10)

    def test_each_expanded_unit_has_the_complete_rich_contract(self):
        for unit in all_a1_units()[10:]:
            with self.subTest(unit=unit["code"]):
                self.assertEqual(validate_unit(unit)["code"], unit["code"])
                self.assertEqual(len(unit["vocabulary"]), 10)
                self.assertGreaterEqual(len(unit["useful_expressions"]), 4)
                self.assertEqual(len(unit["can_do_statements"]), 4)
                self.assertEqual(len(unit["listening"]["questions"]), 3)
                self.assertTrue(unit["listening"]["hide_transcript_until_attempt"])
                self.assertEqual(len(unit["games"]), 4)
                self.assertEqual(len(unit["quiz"]), 10)
                self.assertTrue(all(item["audio"]["lang"] == "en-GB" for item in unit["vocabulary"]))
                listening_items = [item for item in unit["quiz"] if item["skill"] == "listening"]
                self.assertTrue(all(item.get("spoken") for item in listening_items))
                productive = [item for item in unit["quiz"] if item["skill"] in {"speaking", "writing"}]
                self.assertTrue(all(item["productive_score"] is False for item in productive))

    def test_spiral_review_only_points_backwards(self):
        order_by_code = {unit["code"]: unit["order"] for unit in all_a1_units()}
        for unit in all_a1_units()[10:]:
            with self.subTest(unit=unit["code"]):
                self.assertTrue(unit["review_from"])
                self.assertTrue(all(order_by_code[code] < unit["order"] for code in unit["review_from"]))

    def test_a1_final_now_requires_all_twenty_units(self):
        for order in range(1, 20):
            UnitProgress.objects.create(
                user=self.user, unit_code=f"A1.{order}", score=100, status="excellent"
            )
        self.assertFalse(a1_course_complete(self.user))
        self.assertRedirects(
            self.client.get(reverse("english_path:a1_final")),
            reverse("english_path:level", args=("a1",)),
        )
        UnitProgress.objects.create(
            user=self.user, unit_code="A1.20", score=80, status="mastered"
        )
        self.assertTrue(a1_course_complete(self.user))
        self.assertEqual(self.client.get(reverse("english_path:a1_final")).status_code, 200)

    def test_a1_11_respects_mastery_sequence(self):
        self.assertRedirects(
            self.client.get(reverse("english_path:unit", args=("a1-11",))),
            reverse("english_path:level", args=("a1",)),
        )
        for order in range(1, 11):
            UnitProgress.objects.create(
                user=self.user, unit_code=f"A1.{order}", score=80, status="mastered"
            )
        self.assertEqual(self.client.get(reverse("english_path:unit", args=("a1-11",))).status_code, 200)

    def test_real_life_challenge_is_integrated_and_not_the_final(self):
        challenge = all_a1_units()[-1]
        self.assertEqual(challenge["code"], "A1.20")
        self.assertIn("no new grammar", challenge["grammar"]["title"].lower())
        self.assertIn("does not replace", challenge["mission"]["real_world_task"])
        self.assertIn("listening", challenge["mission"]["integrated_skills"])
        self.assertIn("writing", challenge["mission"]["integrated_skills"])
        challenge_prompts = {item["prompt"] for item in challenge["quiz"]}
        final_prompts = {item["prompt"] for item in A1_FINAL_QUESTIONS}
        self.assertTrue(challenge_prompts.isdisjoint(final_prompts))

    def test_final_keeps_balanced_length_and_samples_both_halves_of_a1(self):
        self.assertEqual(len(A1_FINAL_QUESTIONS), 12)
        self.assertEqual(
            Counter(item["skill"] for item in A1_FINAL_QUESTIONS),
            {"vocabulary": 3, "grammar": 3, "reading": 3, "listening": 3},
        )
        sampled = {
            code for item in A1_FINAL_QUESTIONS for code in item.get("source_units", ())
        }
        self.assertTrue(any(int(code.split(".")[1]) <= 10 for code in sampled))
        self.assertTrue(any(int(code.split(".")[1]) >= 11 for code in sampled))

    def test_readiness_review_explicitly_covers_all_twenty_units(self):
        self.assertEqual(len(A1_READINESS_REVIEW), 6)
        self.assertIn("A1.1–A1.20", A1_READINESS_REVIEW[0]["mode"])
        self.assertIn("A1.1–A1.20", A1_READINESS_REVIEW[1]["mode"])
        combined_tasks = " ".join(item["task"] for item in A1_READINESS_REVIEW)
        for concept in ("dates", "weather", "shopping", "school", "jobs", "communication"):
            self.assertIn(concept, combined_tasks)

    def test_free_policy_and_direct_url_protection_are_unchanged(self):
        self.assertEqual(FREE_UNIT_CODES, frozenset({"A1.1"}))
        unpaid = get_user_model().objects.create_user(
            username="unpaid-expanded-learner", password="safe-test-password"
        )
        for order in range(1, 20):
            UnitProgress.objects.create(
                user=unpaid, unit_code=f"A1.{order}", score=100, status="excellent"
            )
        self.client.force_login(unpaid)
        self.assertEqual(self.client.get(reverse("english_path:unit", args=("a1-1",))).status_code, 200)
        for slug in ("a1-2", "a1-11", "a1-20"):
            with self.subTest(slug=slug):
                self.assertRedirects(
                    self.client.get(reverse("english_path:unit", args=(slug,))),
                    reverse("english_path:level", args=("a1",)),
                )

    def test_navigation_and_continue_learning_cross_expansion_boundaries(self):
        for order in range(1, 11):
            UnitProgress.objects.create(
                user=self.user, unit_code=f"A1.{order}", score=80, status="mastered"
            )
        unit_ten = self.client.get(reverse("english_path:unit", args=("a1-10",)))
        self.assertContains(unit_ten, reverse("english_path:unit", args=("a1-11",)))
        for order in range(11, 20):
            UnitProgress.objects.create(
                user=self.user, unit_code=f"A1.{order}", score=80, status="mastered"
            )
        level = self.client.get(reverse("english_path:level", args=("a1",)))
        self.assertEqual(level.context["continue_unit"]["code"], "A1.20")
        final_unit = self.client.get(reverse("english_path:unit", args=("a1-20",)))
        self.assertContains(final_unit, reverse("english_path:unit", args=("a1-19",)))
        self.assertNotContains(final_unit, "التالية بعد الإتقان")

    def test_public_copy_explains_the_thirty_unit_total(self):
        pricing = self.client.get(reverse("pricing"))
        self.assertContains(pricing, "30 وحدة إجمالًا: 20 A1 + 10 A2")
        unpaid = get_user_model().objects.create_user(
            username="copy-check-learner", password="safe-test-password"
        )
        self.client.force_login(unpaid)
        level = self.client.get(reverse("english_path:level", args=("a1",)))
        self.assertContains(level, "إجمالي الرحلة 30 وحدة: 20 وحدة A1 + 10 وحدات A2")
