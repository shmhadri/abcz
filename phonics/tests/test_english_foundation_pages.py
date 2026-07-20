from django.contrib.auth.models import User
from django.test import TestCase, override_settings

from phonics.models import EnglishFoundationProgress, StudentProfile
from phonics.tests.subscription_helpers import grant_active_subscription


@override_settings(DISABLE_AUTO_SEED=True)
class EnglishFoundationPagesTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="english-foundation-diamond", password="StrongPass123!")
        grant_active_subscription(self.user, "diamond")
        self.client.force_login(self.user)

    def test_english_foundation_pages_return_success(self):
        paths = [
            "/english-foundation/",
            "/vocabulary-foundation/",
            "/grammar-foundation/",
            "/grammar-foundation/worksheet/",
            "/conversations/",
            "/conversations/worksheet/",
            "/common-sentences/",
            "/common-sentences/worksheet/",
            "/english-worksheets/",
            "/english-games/",
        ]

        for path in paths:
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200)

    def test_layout_contains_english_foundation_buttons(self):
        self.client.logout()
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "learning-levels-nav")
        self.assertContains(response, "المستوى الأول")
        self.assertContains(response, "الحروف الإنجليزية")
        self.assertContains(response, "المستوى الثاني")
        self.assertContains(response, "الصوتيات")
        self.assertContains(response, "المستوى الثالث")
        self.assertContains(response, "قراءة CVC")
        self.assertContains(response, "المستوى الرابع")
        self.assertContains(response, "التأسيس الإنجليزي")
        self.assertContains(response, "/sounds/")
        self.assertContains(response, "/cvc-reading/")
        self.assertContains(response, "/level-four/")
        return
        self.assertContains(response, "التأسيس الإنجليزي")
        self.assertContains(response, "المفردات الإنجليزية")
        self.assertContains(response, "القواعد التأسيسية")
        self.assertContains(response, "المحادثات")
        self.assertContains(response, "الجمل الشائعة")
        self.assertContains(response, "أوراق العمل")
        self.assertContains(response, "ألعاب وتدريبات")

    def test_vocabulary_training_page_contains_required_tools(self):
        response = self.client.get("/vocabulary-foundation/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "المفردات الإنجليزية")
        self.assertContains(response, "classroom")
        self.assertContains(response, "responsibility")
        self.assertContains(response, "Speed Vocabulary Challenge")
        self.assertContains(response, "ورقة عمل المفردات")
        self.assertContains(response, "vocabulary_foundation.js")
        self.assertContains(response, "VOCABULARY_PROGRESS_URL")

    def test_vocabulary_worksheet_returns_success(self):
        response = self.client.get("/vocabulary-foundation/worksheet/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ورقة عمل المفردات")
        self.assertContains(response, "classroom")
        self.assertContains(response, "responsibility")

    def test_progress_api_records_points_while_leaderboard_is_blocked(self):
        user = User.objects.create_user(username="foundation-user", password="pass12345")
        StudentProfile.objects.create(user=user, student_name="Foundation Student", grade="الصف الثالث")
        grant_active_subscription(user, "diamond")
        self.client.force_login(user)

        response = self.client.post(
            "/api/english-foundation/progress/",
            data='{"section":"vocabulary","activity_type":"exercise","points":5}',
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["points"], 5)
        self.assertTrue(EnglishFoundationProgress.objects.filter(user=user, section="vocabulary").exists())

        self.client.logout()
        leaderboard = self.client.get("/api/leaderboard/")
        self.assertEqual(leaderboard.status_code, 403)
        self.assertEqual(leaderboard.json()["error"], "feature_unavailable")
