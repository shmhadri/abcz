from django.test import TestCase, override_settings

from phonics.models import LetterProgress, Student


@override_settings(DISABLE_AUTO_SEED=True)
class CorePagesTests(TestCase):
    def test_core_pages_return_success(self):
        paths = [
            "/",
            "/leaderboard/",
            "/cvc-reading/",
            "/grade-2-unit-1/",
            "/grade-3-unit-1/",
            "/grade-4-unit-1/",
            "/top-goal-6-unit-1/",
        ]

        for path in paths:
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200)

    def test_leaderboard_uses_progress_entries_scores(self):
        student = Student.objects.create(name="Leaderboard Student", school="Test School")
        LetterProgress.objects.create(student=student, letter="A", score=15, passed=True)

        response = self.client.get("/leaderboard/")

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("error", response.context)
        self.assertContains(response, "Leaderboard Student")
        self.assertContains(response, "15")
