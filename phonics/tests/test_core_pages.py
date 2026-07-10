from django.test import TestCase, override_settings

from phonics.models import LetterProgress, Student


@override_settings(DISABLE_AUTO_SEED=True)
class CorePagesTests(TestCase):
    def test_core_pages_return_success(self):
        paths = [
            "/",
            "/pricing/",
            "/curriculum/",
            "/phonics-foundation/",
            "/about/",
            "/guide/",
            "/privacy/",
            "/terms/",
            "/cvc-reading/",
        ]

        for path in paths:
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200)

    def test_curriculum_pages_return_success(self):
        paths = [
            "/curriculum/",
            "/phonics-foundation/",
        ]

        for path in paths:
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, "Phonics Game Lab")

    def test_pricing_page_contains_subscription_plans(self):
        response = self.client.get("/pricing/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "A-Z")
        self.assertContains(response, "VIP")

    def test_leaderboard_page_is_blocked_in_level_one_policy(self):
        student = Student.objects.create(name="Leaderboard Student", grade="Grade 3", school="Test School")
        LetterProgress.objects.create(student=student, letter="A", score=15, passed=True)

        response = self.client.get("/leaderboard/")

        self.assertEqual(response.status_code, 403)
        html = response.content.decode("utf-8")
        self.assertNotIn("leaderboard-hero", html)
        self.assertNotIn("Leaderboard Student", html)
        self.assertNotIn("Test School", html)

    def test_leaderboard_api_is_blocked_in_level_one_policy(self):
        student = Student.objects.create(name="API Leaderboard Student", grade="Grade 2", school="Hidden School")
        LetterProgress.objects.create(student=student, letter="B", score=20, passed=False)

        response = self.client.get("/api/leaderboard/")

        self.assertEqual(response.status_code, 403)
        payload = response.json()
        self.assertEqual(payload["error"], "feature_unavailable")
        self.assertNotIn("rows", payload)

    def test_curriculum_page_redirects_home(self):
        response = self.client.get("/curriculum/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Level 1: Letters A-Z")

    def test_curriculum_preview_redirects_home(self):
        response = self.client.get("/curriculum/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Level 2: Sounds and Phonics")

    def test_phonics_foundation_page_redirects_home(self):
        response = self.client.get("/phonics-foundation/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Level 3: CVC Reading")

    def test_letters_page_links_to_curriculum(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "/curriculum/")
