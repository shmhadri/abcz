import json

from django.contrib.auth.models import User
from django.test import TestCase, override_settings

from phonics.models import BirdTutorProgress, StudentProfile
from phonics.views import FULL_ACCESS_FEATURE_KEYS, PLAN_DIAMOND, get_subscription_plan
from phonics.tests.subscription_helpers import grant_active_subscription


@override_settings(DISABLE_AUTO_SEED=True)
class DiamondPlanTests(TestCase):
    expected_features = {
        "letters_full",
        "sounds_full",
        "worksheets_level1",
        "worksheets_download_level1",
        "sounds_worksheets",
        "book_download_level1",
        "full_book_download",
        "wordwall_level1",
        "bird_tutor",
        "bird_xp",
        "leaderboard",
        "cvc_words",
        "word_families",
        "cvc_sentences",
        "cvc_stories",
        "pronouns",
        "cvc_worksheets",
        "cvc_certificate",
        "level_four",
        "level_four_full",
        "level4_foundation",
        "full_access",
    }

    def setUp(self):
        self.user = User.objects.create_user(username="diamond-user", password="StrongPass123!")
        StudentProfile.objects.create(user=self.user, student_name="Diamond Student")
        grant_active_subscription(self.user, PLAN_DIAMOND)
        self.client.force_login(self.user)

    def post_json(self, url, payload):
        return self.client.post(url, data=json.dumps(payload), content_type="application/json")

    def test_diamond_feature_keys_open_everything(self):
        self.assertEqual(get_subscription_plan(self.user), PLAN_DIAMOND)
        self.assertTrue(self.expected_features.issubset(FULL_ACCESS_FEATURE_KEYS))

    def test_pricing_page_shows_diamond_plan(self):
        response = self.client.get("/pricing/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "الماسي")
        self.assertContains(response, "50")
        self.assertContains(response, "ريال شهريًا")
        self.assertContains(response, "كل الموقع")
        self.assertContains(response, "مشترك حاليًا")

    def test_diamond_opens_all_major_level_paths(self):
        for path in [
            "/",
            "/sounds/",
            "/sounds/worksheet/",
            "/letters/worksheet/",
            "/letters/worksheets-book/",
            "/letters/A/external-games/",
            "/cvc-reading/",
            "/cvc-reading/worksheet/",
            "/level-four/",
            "/level-four/reading/",
            "/level-four/worksheets/",
            "/leaderboard/",
            "/profile/",
        ]:
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200)

    def test_diamond_opens_bird_tutor_api(self):
        response = self.post_json("/api/bird-tutor/progress/", {
            "xp_delta": 10,
            "question_type": "starts_with_letter",
            "is_correct": True,
            "letter": "A",
            "word": "ant",
        })

        self.assertEqual(response.status_code, 200)
        progress = BirdTutorProgress.objects.get(user=self.user)
        self.assertEqual(progress.xp, 10)
