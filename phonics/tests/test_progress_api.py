import json

from django.test import TestCase

from phonics.models import LetterProgress, Student


class SaveProgressApiTests(TestCase):
    def post_progress(self, payload):
        return self.client.post(
            "/api/save-progress/",
            data=json.dumps(payload),
            content_type="application/json",
        )

    def test_save_valid_letter_progress_and_marks_passed(self):
        response = self.post_progress({"student": "Test Student", "letter": "A", "score": 14})

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "ok")
        self.assertTrue(data["passed"])
        self.assertEqual(data["score"], 14)

        student = Student.objects.get(name="Test Student")
        progress = LetterProgress.objects.get(student=student, letter="A")
        self.assertEqual(progress.score, 14)
        self.assertTrue(progress.passed)

    def test_rejects_score_above_backend_limit(self):
        response = self.post_progress({"student": "Test Student", "letter": "A", "score": 21})

        self.assertEqual(response.status_code, 400)
        self.assertIn("score", response.json()["error"])

    def test_rejects_invalid_letter(self):
        response = self.post_progress({"student": "Test Student", "letter": "AA", "score": 10})

        self.assertEqual(response.status_code, 400)
        self.assertIn("Letter", response.json()["error"])

    def test_rejects_next_letter_when_previous_not_passed(self):
        response = self.post_progress({"student": "Test Student", "letter": "B", "score": 20})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["error"], "previous_letter_not_passed")

    def test_allows_next_letter_after_previous_is_passed(self):
        first = self.post_progress({"student": "Test Student", "letter": "A", "score": 20})
        second = self.post_progress({"student": "Test Student", "letter": "B", "score": 20})

        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 200)
        self.assertTrue(second.json()["passed"])
