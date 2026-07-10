import json

from django.contrib.auth.models import User
from django.test import TestCase, override_settings

from phonics.models import BirdReviewItem, BirdTutorProgress, StudentProfile


@override_settings(DISABLE_AUTO_SEED=True)
class BirdTutorApiTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="birdvip", password="StrongPass123!")
        StudentProfile.objects.create(user=self.user, student_name="Bird VIP", is_vip=True)

    def login(self):
        self.client.login(username="birdvip", password="StrongPass123!")

    def post_json(self, url, payload):
        return self.client.post(
            url,
            data=json.dumps(payload),
            content_type="application/json",
        )

    def test_progress_endpoint_requires_login(self):
        response = self.post_json("/api/bird-tutor/progress/", {
            "xp_delta": 5,
            "question_type": "starts_with_letter",
            "is_correct": True,
            "letter": "A",
            "word": "ant",
        })

        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response["Location"])

    def test_review_endpoint_requires_login(self):
        response = self.client.get("/api/bird-tutor/review/")

        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response["Location"])

    def test_creates_bird_tutor_progress_and_increases_xp(self):
        self.login()

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
        self.assertEqual(progress.correct_answers, 1)
        self.assertEqual(progress.wrong_answers, 0)

    def test_tracks_wrong_answer_progress(self):
        self.login()

        response = self.post_json("/api/bird-tutor/progress/", {
            "xp_delta": 0,
            "question_type": "choose_word_for_letter",
            "is_correct": False,
            "letter": "B",
            "word": "bat",
        })

        self.assertEqual(response.status_code, 200)
        progress = BirdTutorProgress.objects.get(user=self.user)
        self.assertEqual(progress.xp, 0)
        self.assertEqual(progress.total_questions, 1)
        self.assertEqual(progress.correct_answers, 0)
        self.assertEqual(progress.wrong_answers, 1)

    def test_creates_review_item_after_wrong_answer(self):
        self.login()

        response = self.post_json("/api/bird-tutor/review/", {
            "letter": "C",
            "word": "cat",
            "question_type": "listen_and_choose",
            "is_correct": False,
        })

        self.assertEqual(response.status_code, 200)
        item = BirdReviewItem.objects.get(user=self.user, letter="C", word="cat")
        self.assertEqual(item.question_type, "listen_and_choose")
        self.assertEqual(item.mistakes_count, 1)
        self.assertEqual(item.success_count, 0)
        self.assertFalse(item.mastered)

    def test_review_item_is_mastered_after_two_successes(self):
        self.login()
        BirdReviewItem.objects.create(
            user=self.user,
            letter="D",
            word="dog",
            question_type="starts_with_letter",
            mistakes_count=1,
        )

        first = self.post_json("/api/bird-tutor/review/", {
            "letter": "D",
            "word": "dog",
            "question_type": "starts_with_letter",
            "is_correct": True,
        })
        second = self.post_json("/api/bird-tutor/review/", {
            "letter": "D",
            "word": "dog",
            "question_type": "starts_with_letter",
            "is_correct": True,
        })

        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 200)
        item = BirdReviewItem.objects.get(user=self.user, letter="D", word="dog")
        self.assertEqual(item.success_count, 2)
        self.assertTrue(item.mastered)

    def test_review_get_returns_unmastered_items_only(self):
        self.login()
        BirdReviewItem.objects.create(user=self.user, letter="A", word="ant", mistakes_count=1)
        BirdReviewItem.objects.create(user=self.user, letter="B", word="bat", mistakes_count=1, mastered=True)

        response = self.client.get("/api/bird-tutor/review/")

        self.assertEqual(response.status_code, 200)
        items = response.json()["items"]
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["word"], "ant")

    def test_vip_page_shows_bird_tutor(self):
        self.login()

        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="birdTutor"')
        self.assertContains(response, 'id="birdAskBtn"')
        self.assertContains(response, 'id="birdReviewBtn"')
        self.assertNotContains(response, 'id="birdTutorLocked"')

    def test_non_vip_page_hides_locked_bird(self):
        user = User.objects.create_user(username="notvip", password="StrongPass123!")
        StudentProfile.objects.create(user=user, student_name="Not VIP", is_vip=False)
        self.client.login(username="notvip", password="StrongPass123!")

        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'id="birdTutorLocked"')
        self.assertNotContains(response, 'id="birdTutor" aria-label="Phonics Bird Tutor"')

    def test_profile_dashboard_requires_login(self):
        response = self.client.get("/profile/")

        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response["Location"])

    def test_vip_profile_dashboard_shows_bird_stats(self):
        self.login()
        BirdTutorProgress.objects.create(
            user=self.user,
            xp=21,
            total_questions=5,
            correct_answers=4,
            wrong_answers=1,
        )

        response = self.client.get("/profile/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "VIP: نشط")
        self.assertContains(response, "Bird XP")
        self.assertContains(response, "21")
        self.assertContains(response, "عدد الأسئلة")
        self.assertContains(response, "نسبة النجاح")
        self.assertContains(response, "80%")

    def test_non_vip_profile_dashboard_shows_upgrade_prompt(self):
        user = User.objects.create_user(username="profile_notvip", password="StrongPass123!")
        StudentProfile.objects.create(user=user, student_name="Profile Not VIP", is_vip=False)
        self.client.login(username="profile_notvip", password="StrongPass123!")

        response = self.client.get("/profile/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "VIP: غير نشط")
        self.assertContains(response, "فعّل VIP لفتح العصفور الذكي وتقارير المراجعة")
        self.assertContains(response, "/pricing/")

    def test_profile_dashboard_shows_review_and_mastered_words(self):
        self.login()
        BirdTutorProgress.objects.create(
            user=self.user,
            xp=10,
            total_questions=2,
            correct_answers=1,
            wrong_answers=1,
        )
        BirdReviewItem.objects.create(
            user=self.user,
            letter="A",
            word="ant",
            mistakes_count=2,
            mastered=False,
        )
        BirdReviewItem.objects.create(
            user=self.user,
            letter="B",
            word="bat",
            success_count=2,
            mastered=True,
        )

        response = self.client.get("/profile/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "كلمات تحتاج مراجعة")
        self.assertContains(response, "A - ant")
        self.assertContains(response, "كلمات تم إتقانها")
        self.assertContains(response, "B - bat")
