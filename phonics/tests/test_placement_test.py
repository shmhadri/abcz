import json

from django.test import TestCase, override_settings

from phonics.views import PLACEMENT_TEST_QUESTIONS


@override_settings(DISABLE_AUTO_SEED=True)
class PlacementTestTests(TestCase):
    def correct_answers(self):
        return {
            question["id"]: question["answer"]
            for question in PLACEMENT_TEST_QUESTIONS
        }

    def wrong_answer_for(self, question):
        for option in question["options"]:
            if option != question["answer"]:
                return option
        return ""

    def post_answers(self, answers):
        return self.client.post(
            "/placement-test/",
            data=json.dumps({"answers": answers}),
            content_type="application/json",
        )

    def test_start_page_shows_two_main_routes(self):
        response = self.client.get("/start/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "أعرف مستواي في اللغة الإنجليزية")
        self.assertContains(response, "أريد اختبار تحديد مستوى")
        self.assertContains(response, "/levels/")
        self.assertContains(response, "/placement-test/")

    def test_levels_page_shows_level_subscriptions(self):
        response = self.client.get("/levels/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "المستوى الثالث")
        self.assertContains(response, "المستوى الرابع")
        self.assertContains(response, "15 ريال شهريا")
        self.assertContains(response, "/placement-test/")

    def test_pricing_page_links_to_placement_test_and_level_prices(self):
        response = self.client.get("/pricing/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "/placement-test/")
        self.assertContains(response, "level-3-plan")
        self.assertContains(response, "level-4-plan")
        self.assertContains(response, "15")

    def test_placement_page_has_twenty_questions_without_answer_key(self):
        response = self.client.get("/placement-test/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(PLACEMENT_TEST_QUESTIONS), 20)
        self.assertContains(response, "اختبار تحديد المستوى")
        self.assertContains(response, "data-placement-form", html=False)
        self.assertNotContains(response, '"answer"')

    def test_low_letter_score_recommends_level_one(self):
        answers = {
            question["id"]: self.wrong_answer_for(question)
            for question in PLACEMENT_TEST_QUESTIONS
        }

        response = self.post_answers(answers)

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["recommended_level"], "level_1")
        self.assertEqual(payload["recommended_title"], "المستوى الأول")

    def test_phonics_gap_recommends_level_two_even_with_other_correct_answers(self):
        answers = self.correct_answers()
        for question in PLACEMENT_TEST_QUESTIONS:
            if question["section"] in {"letter_sounds", "phonics"}:
                answers[question["id"]] = self.wrong_answer_for(question)

        response = self.post_answers(answers)

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["recommended_level"], "level_2")
        self.assertEqual(payload["recommended_title"], "المستوى الثاني")

    def test_mid_score_with_prerequisites_recommends_level_three(self):
        answers = {
            question["id"]: self.wrong_answer_for(question)
            for question in PLACEMENT_TEST_QUESTIONS
        }
        for question in PLACEMENT_TEST_QUESTIONS[:14]:
            answers[question["id"]] = question["answer"]

        response = self.post_answers(answers)

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["recommended_level"], "level_3")
        self.assertEqual(payload["recommended_title"], "المستوى الثالث")
        self.assertIn("#level-3-plan", payload["cta_url"])

    def test_strong_score_recommends_level_four(self):
        response = self.post_answers(self.correct_answers())

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["recommended_level"], "level_4")
        self.assertEqual(payload["recommended_title"], "المستوى الرابع")
        self.assertIn("#level-4-plan", payload["cta_url"])
