import json

from django.contrib.auth.models import User
from django.test import TestCase, override_settings

from phonics.models import BirdTutorProgress, StudentProfile
from phonics.views import VIP_FEATURE_KEYS
from phonics.tests.subscription_helpers import grant_active_subscription


@override_settings(DISABLE_AUTO_SEED=True)
class VipPlanTests(TestCase):
    required_features = {
        "letters_full",
        "letter_sounds_basic",
        "sounds_basic",
        "sounds_full",
        "vowels",
        "digraphs",
        "ending_sounds",
        "trigraphs",
        "advanced_patterns_preview",
        "sounds_mic",
        "internal_games",
        "student_progress",
        "basic_parent_report",
        "letter_certificate_basic",
        "worksheets_level1",
        "worksheets_print_level1",
        "worksheets_download_level1",
        "sounds_worksheets",
        "book_download_level1",
        "full_book_download",
        "wordwall_level1",
        "bird_tutor",
        "bird_tutor_trial",
        "bird_tutor_full",
        "bird_xp",
        "bird_error_review",
        "bird_parent_report",
        "parent_report_detailed",
        "smart_review_plan",
        "gold_certificate",
        "honor_board_consent",
        "leaderboard",
        "mistake_review",
        "improvement_report",
        "audio_question_reading",
        "step_by_step_error_review",
    }

    forbidden_features = {
        "cvc_words",
        "word_families",
        "cvc_sentences",
        "cvc_stories",
        "pronouns",
        "cvc_worksheets",
        "cvc_certificate",
        "full_access",
        "all_site_access",
        "level_four",
        "level_four_full",
        "level4_foundation",
        "all_future_features",
        "wildcard_access",
    }

    def setUp(self):
        self.user = User.objects.create_user(username="vip-user", password="StrongPass123!")
        StudentProfile.objects.create(user=self.user, student_name="VIP Student")
        grant_active_subscription(self.user, "vip")
        self.client.force_login(self.user)

    def post_json(self, url, payload):
        return self.client.post(url, data=json.dumps(payload), content_type="application/json")

    def test_vip_feature_keys_match_requested_scope(self):
        self.assertTrue(self.required_features.issubset(VIP_FEATURE_KEYS))
        self.assertTrue(self.forbidden_features.isdisjoint(VIP_FEATURE_KEYS))

    def test_pricing_page_shows_vip_without_full_access_claims(self):
        response = self.client.get("/pricing/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "VIP")
        self.assertContains(response, "39")
        self.assertContains(response, "ريال شهريًا")
        self.assertContains(response, "للمتابعة الذكية")
        self.assertContains(response, "كل مزايا Silver")
        self.assertContains(response, "مشترك حاليًا")
        self.assertContains(response, "VIP لا يشمل كل الموقع")
        self.assertNotContains(response, "Full Access")

    def test_vip_opens_allowed_vip_features(self):
        for path in [
            "/",
            "/sounds/",
            "/sounds/worksheet/",
            "/letters/worksheet/",
            "/letters/worksheets-book/",
            "/letters/A/external-games/",
            "/leaderboard/",
            "/profile/",
        ]:
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200)

    def test_vip_opens_bird_tutor_and_saves_xp(self):
        response = self.post_json("/api/bird-tutor/progress/", {
            "xp_delta": 5,
            "question_type": "starts_with_letter",
            "is_correct": True,
            "letter": "A",
            "word": "ant",
        })

        self.assertEqual(response.status_code, 200)
        progress = BirdTutorProgress.objects.get(user=self.user)
        self.assertEqual(progress.xp, 5)
        self.assertEqual(progress.total_questions, 1)

    def test_vip_opens_leaderboard_api(self):
        response = self.client.get("/api/leaderboard/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("rows", response.json())

    def test_vip_does_not_open_full_access_level_four_or_cvc(self):
        for path in ["/cvc-reading/", "/level-four/"]:
            with self.subTest(path=path):
                response = self.client.get(path)

                self.assertEqual(response.status_code, 403)
                self.assertContains(response, "هذه الميزة متاحة في الباقة الماسية", status_code=403)
