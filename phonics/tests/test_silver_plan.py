import json

from django.contrib.auth.models import Group, User
from django.test import TestCase, override_settings

from phonics.models import StudentProfile
from phonics.views import SILVER_FEATURE_KEYS


@override_settings(DISABLE_AUTO_SEED=True)
class SilverPlanTests(TestCase):
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
    }

    forbidden_features = {
        "book_download_level1",
        "full_book_download",
        "wordwall_level1",
        "bird_tutor",
        "bird_tutor_trial",
        "bird_tutor_full",
        "bird_xp",
        "bird_parent_report",
        "cvc_words",
        "word_families",
        "cvc_sentences",
        "cvc_stories",
        "pronouns",
        "cvc_worksheets",
        "cvc_certificate",
        "level_four",
        "full_access",
    }

    def setUp(self):
        self.user = User.objects.create_user(username="silver-user", password="StrongPass123!")
        StudentProfile.objects.create(user=self.user, student_name="Silver Student")
        silver_group = Group.objects.create(name="Silver")
        self.user.groups.add(silver_group)
        self.client.force_login(self.user)

    def test_silver_feature_keys_are_exact_for_requested_scope(self):
        self.assertTrue(self.required_features.issubset(SILVER_FEATURE_KEYS))
        self.assertTrue(self.forbidden_features.isdisjoint(SILVER_FEATURE_KEYS))

    def test_pricing_page_shows_silver_plan(self):
        response = self.client.get("/pricing/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Silver")
        self.assertContains(response, "27")
        self.assertContains(response, "ريال شهريًا")
        self.assertContains(response, "قيمة أعلى")
        self.assertContains(response, "اختيار Silver")

    def test_silver_opens_level_one_level_two_and_worksheets(self):
        for path in ["/", "/sounds/", "/sounds/worksheet/", "/letters/worksheet/"]:
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200)

    def test_silver_page_flags_allow_worksheets_and_keep_locked_features(self):
        response = self.client.get("/")
        html = response.content.decode("utf-8")

        self.assertEqual(response.status_code, 200)
        self.assertIn('window.LEVEL_ONE_PLAN = "silver"', html)
        self.assertIn("letterWorksheets: false", html)
        self.assertIn('id="letterWorksheetBtn"', html)
        self.assertNotIn('id="letterWorksheetBtn" type="button" hidden', html)
        self.assertIn("certificate: false", html)
        self.assertIn("worksheetBook: true", html)
        self.assertIn("wordwall: true", html)
        self.assertIn("smartBird: true", html)

    def test_silver_cannot_open_book_wordwall_bird_cvc_or_level_four(self):
        blocked_get_paths = [
            "/letters/worksheets-book/",
            "/letters/A/external-games/",
            "/cvc-reading/",
            "/level-four/",
        ]

        for path in blocked_get_paths:
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 403)
                self.assertContains(response, "هذه الميزة", status_code=403)

        response = self.client.post(
            "/api/bird-tutor/progress/",
            data=json.dumps({
                "xp_delta": 5,
                "question_type": "starts_with_letter",
                "is_correct": True,
                "letter": "A",
                "word": "ant",
            }),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["error"], "feature_unavailable")
        self.assertEqual(response.json()["message"], "هذه الميزة متاحة في VIP أو الباقة الماسية.")
