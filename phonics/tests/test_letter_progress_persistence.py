import json

from django.contrib.auth.models import User
from django.test import TestCase

from phonics.models import LetterProgress, StudentProfile


class LetterProgressPersistenceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="letter_user",
            email="letter@example.com",
            password="StrongPass123!",
        )
        StudentProfile.objects.create(
            user=self.user,
            display_name="Letter Student",
            student_name="Letter Student",
            is_vip=True,
        )
        self.payload = {
            "letter": "A",
            "writing_score": 20,
            "words_score": 5,
            "quiz_score": 5,
            "total_score": 30,
            "completed": True,
            "words_practiced": ["ant", "arm", "axe"],
            "mistakes": {"quiz": [], "missing_words": ["air"]},
        }

    def post_json(self, payload):
        return self.client.post(
            "/api/letter-progress/save/",
            data=json.dumps(payload),
            content_type="application/json",
        )

    def test_create_letter_progress_for_user(self):
        self.client.login(username="letter_user", password="StrongPass123!")

        response = self.post_json(self.payload)

        self.assertEqual(response.status_code, 200)
        progress = LetterProgress.objects.get(user=self.user, letter="A")
        self.assertEqual(progress.total_score, 30)
        self.assertEqual(progress.writing_score, 20)
        self.assertEqual(progress.words_practiced_json, ["ant", "arm", "axe"])
        self.assertEqual(progress.mistakes_json["missing_words"], ["air"])

    def test_update_same_letter_does_not_create_duplicate(self):
        self.client.login(username="letter_user", password="StrongPass123!")

        first = self.post_json(self.payload)
        updated = dict(self.payload, total_score=31, quiz_score=6)
        second = self.post_json(updated)

        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 200)
        self.assertEqual(LetterProgress.objects.filter(user=self.user, letter="A").count(), 1)
        progress = LetterProgress.objects.get(user=self.user, letter="A")
        self.assertEqual(progress.total_score, 31)
        self.assertEqual(progress.quiz_score, 6)

    def test_endpoint_requires_login(self):
        response = self.post_json(self.payload)

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()["error"], "login_required")

    def test_endpoint_saves_completed_true(self):
        self.client.login(username="letter_user", password="StrongPass123!")

        response = self.post_json(self.payload)

        self.assertEqual(response.status_code, 200)
        progress = LetterProgress.objects.get(user=self.user, letter="A")
        self.assertTrue(progress.completed)
        self.assertTrue(progress.passed)
        self.assertIsNotNone(progress.completed_at)

    def test_profile_shows_completed_letter_count(self):
        LetterProgress.objects.create(
            user=self.user,
            letter="A",
            writing_score=20,
            words_score=5,
            quiz_score=5,
            total_score=30,
            completed=True,
        )
        self.client.login(username="letter_user", password="StrongPass123!")

        response = self.client.get("/profile/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "الحروف المكتملة")
        self.assertContains(response, "آخر حرف مكتمل")
        self.assertContains(response, "حرف A")

    def test_profile_does_not_break_without_progress(self):
        self.client.login(username="letter_user", password="StrongPass123!")

        response = self.client.get("/profile/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ابدأ بإكمال أول حرف لتظهر إحصائيات التقدم هنا.")

    def test_letters_page_still_renders(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="finishLetter"')

    def test_games_remain_optional_in_letters_page(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "الألعاب اختيارية للتدريب ولا تمنع فتح الحرف التالي.")
        self.assertContains(response, "this.requiredGames = [];")
