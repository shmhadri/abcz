from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth.models import User
from django.core.cache import cache
from django.db import connection
from django.test import Client, TestCase, override_settings
from django.test.utils import CaptureQueriesContext
from django.utils import timezone

from phonics.models import (
    BirdTutorProgress,
    CVCReadingProgress,
    CVCSentence,
    CVCStory,
    CVCWord,
    LetterProgress,
    SoundPracticeProgress,
    StudentProfile,
    UserSubscription,
)
from phonics.views import PLAN_DIAMOND, PLAN_LEVEL_THREE


@override_settings(DISABLE_AUTO_SEED=True)
class BigOReadPathTests(TestCase):
    def setUp(self):
        cache.clear()

    def activate_plan(self, user, plan_code):
        now = timezone.now()
        return UserSubscription.objects.create(
            user=user,
            plan_code=plan_code,
            status=UserSubscription.Status.ACTIVE,
            starts_at=now - timedelta(minutes=1),
            expires_at=now + timedelta(days=30),
        )

    def login_user(self, username, plan_code):
        user = User.objects.create_user(username=username, password="StrongPass123!")
        StudentProfile.objects.create(user=user, student_name=username, grade="Grade 3")
        self.activate_plan(user, plan_code)
        self.client.force_login(user)
        return user

    def create_cvc_words(self, count=125):
        for index in range(count):
            CVCWord.objects.create(
                word=f"w{index:03d}",
                arabic_meaning=f"word {index}",
                order=index,
                difficulty_level=(index % 5) + 1,
            )

    def test_cvc_words_api_paginates_and_preserves_legacy_key(self):
        self.login_user("level-three-pagination", PLAN_LEVEL_THREE)
        self.create_cvc_words(125)

        first = self.client.get("/api/cvc-words/?page_size=100").json()
        second = self.client.get("/api/cvc-words/?page=2&page_size=100").json()

        self.assertEqual(first["count"], 125)
        self.assertEqual(first["page"], 1)
        self.assertEqual(first["page_size"], 100)
        self.assertEqual(first["total_pages"], 2)
        self.assertEqual(len(first["results"]), 100)
        self.assertEqual(first["results"], first["words"])
        self.assertEqual(len(second["results"]), 25)
        self.assertTrue(set(item["id"] for item in first["results"]).isdisjoint(
            item["id"] for item in second["results"]
        ))

    def test_cvc_words_api_clamps_invalid_pagination(self):
        self.login_user("level-three-clamp", PLAN_LEVEL_THREE)
        self.create_cvc_words(3)

        payload = self.client.get("/api/cvc-words/?page=-4&page_size=9999").json()

        self.assertEqual(payload["page"], 1)
        self.assertEqual(payload["page_size"], 100)
        self.assertEqual(payload["count"], 3)
        self.assertEqual(len(payload["results"]), 3)

    def test_cvc_stories_summary_payload_can_avoid_full_content(self):
        self.login_user("level-three-story-summary", PLAN_LEVEL_THREE)
        CVCStory.objects.create(
            title="The Cat",
            content="cat sat mat " * 20,
            arabic_explanation="Arabic explanation",
            order=1,
            difficulty=1,
        )

        summary = self.client.get("/api/cvc-stories/?summary=1").json()["results"][0]
        full = self.client.get("/api/cvc-stories/").json()["results"][0]

        self.assertIn("summary", summary)
        self.assertIn("word_count", summary)
        self.assertNotIn("content", summary)
        self.assertIn("content", full)
        self.assertIn("quiz_data", full)

    def test_cvc_api_error_response_does_not_leak_exception_details(self):
        self.login_user("level-three-error", PLAN_LEVEL_THREE)

        with patch("phonics.views.logger.exception") as log_exception, patch(
            "phonics.views.paginate_queryset",
            side_effect=RuntimeError("secret database path"),
        ):
            response = self.client.get("/api/cvc-words/")

        self.assertEqual(response.status_code, 500)
        self.assertTrue(log_exception.called)
        payload = response.json()
        self.assertEqual(payload["error"], "Failed to fetch CVC words")
        self.assertNotIn("details", payload)
        self.assertNotIn("secret", str(payload))

    def test_leaderboard_api_avoids_n_plus_one_progress_queries(self):
        viewer = self.login_user("diamond-leaderboard-viewer", PLAN_DIAMOND)
        for index in range(30):
            user = User.objects.create_user(username=f"leader-user-{index}", password="StrongPass123!")
            StudentProfile.objects.create(user=user, student_name=f"Student {index}", grade="Grade 3")
            SoundPracticeProgress.objects.create(user=user, completed_items=[f"item:{index}"])
            CVCReadingProgress.objects.create(user=user, words_mastered=[f"w{index}"])
            BirdTutorProgress.objects.create(user=user, xp=index)
            LetterProgress.objects.create(user=user, letter="A", total_score=index, completed=index % 2 == 0)

        client = Client()
        client.force_login(viewer)
        cache.clear()

        with CaptureQueriesContext(connection) as queries:
            response = client.get("/api/leaderboard/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("rows", response.json())
        self.assertLessEqual(len(queries), 35)

        with CaptureQueriesContext(connection) as cached_queries:
            cached_response = client.get("/api/leaderboard/")

        self.assertEqual(cached_response.status_code, 200)
        self.assertLess(len(cached_queries), len(queries))
