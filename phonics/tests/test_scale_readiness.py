import re
from datetime import timedelta

from django.contrib.auth.models import User
from django.db import connection
from django.test import Client, TestCase, override_settings
from django.test.utils import CaptureQueriesContext
from django.utils import timezone

from phonics.models import StudentProfile, UserSubscription
from phonics.views import PLAN_LEVEL_THREE


REQUEST_ID_RE = re.compile(r"^[A-Za-z0-9._-]{1,64}$")


@override_settings(DISABLE_AUTO_SEED=True, SECURE_SSL_REDIRECT=False)
class ScaleReadinessMiddlewareTests(TestCase):
    def test_request_id_is_generated(self):
        response = self.client.get("/")

        request_id = response["X-Request-ID"]
        self.assertRegex(request_id, REQUEST_ID_RE)

    def test_valid_proxy_request_id_is_preserved(self):
        response = self.client.get("/", HTTP_X_REQUEST_ID="proxy-request-123")

        self.assertEqual(response["X-Request-ID"], "proxy-request-123")

    def test_invalid_proxy_request_id_is_rejected(self):
        response = self.client.get("/", HTTP_X_REQUEST_ID="bad request id " + ("x" * 80))

        self.assertRegex(response["X-Request-ID"], REQUEST_ID_RE)
        self.assertNotEqual(response["X-Request-ID"], "bad request id " + ("x" * 80))

    @override_settings(ENABLE_SERVER_TIMING_HEADER=True)
    def test_server_timing_header_can_be_enabled(self):
        response = self.client.get("/")

        self.assertIn("Server-Timing", response)
        self.assertRegex(response["Server-Timing"], r"^app;dur=\d+(\.\d+)?$")


@override_settings(DISABLE_AUTO_SEED=True, SECURE_SSL_REDIRECT=False)
class SubscriptionQueryCacheTests(TestCase):
    def create_user_with_group(self, username, group_name):
        user = User.objects.create_user(username=username, password="StrongPass123!")
        StudentProfile.objects.create(user=user, student_name=username)
        self.activate_plan(user, group_name.lower())
        return user

    def activate_plan(self, user, plan_code):
        now = timezone.now()
        UserSubscription.objects.create(
            user=user,
            plan_code=plan_code,
            status=UserSubscription.Status.ACTIVE,
            starts_at=now - timedelta(minutes=1),
            expires_at=now + timedelta(days=30),
        )

    def create_user_with_plan(self, username, plan_code):
        user = User.objects.create_user(username=username, password="StrongPass123!")
        StudentProfile.objects.create(user=user, student_name=username)
        self.activate_plan(user, plan_code)
        return user

    def test_silver_homepage_uses_bounded_subscription_queries(self):
        user = self.create_user_with_group("scale-silver", "Silver")
        client = Client()
        client.force_login(user)

        with CaptureQueriesContext(connection) as ctx:
            response = client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertLessEqual(len(ctx.captured_queries), 15)
        subscription_queries = [
            query["sql"]
            for query in ctx.captured_queries
            if "phonics_usersubscription" in query["sql"].lower()
        ]
        profile_queries = [
            query["sql"]
            for query in ctx.captured_queries
            if "phonics_studentprofile" in query["sql"].lower()
        ]
        group_queries = [
            query["sql"]
            for query in ctx.captured_queries
            if "auth_group" in query["sql"].lower()
        ]
        self.assertLessEqual(len(subscription_queries), 2)
        self.assertLessEqual(len(profile_queries), 3)
        self.assertLessEqual(len(group_queries), 3)

    def test_subscription_access_behavior_is_unchanged(self):
        anonymous = Client()
        self.assertEqual(anonymous.get("/sounds/").status_code, 403)

        silver_client = Client()
        silver_client.force_login(self.create_user_with_group("scale-silver-access", "Silver"))
        self.assertEqual(silver_client.get("/sounds/").status_code, 200)
        self.assertEqual(silver_client.get("/cvc-reading/").status_code, 403)

        level_three_client = Client()
        level_three_client.force_login(self.create_user_with_plan("scale-level-three", PLAN_LEVEL_THREE))
        self.assertEqual(level_three_client.get("/cvc-reading/").status_code, 200)
        self.assertEqual(level_three_client.get("/sounds/").status_code, 403)

    def test_sound_progress_api_schema_is_unchanged(self):
        client = Client()
        client.force_login(self.create_user_with_group("scale-silver-api", "Silver"))

        response = client.get("/api/sounds/progress/")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["authenticated"])
        self.assertIn("completed_items", payload)
        self.assertIn("quiz_attempts", payload)
        self.assertIn("vowel_mastery_percentage", payload)

    def test_sound_progress_duplicate_post_is_noop(self):
        client = Client()
        client.force_login(self.create_user_with_group("scale-silver-sound-noop", "Silver"))
        payload = {
            "completed_items": ["digraph:sh"],
            "quiz_attempts": 1,
            "quiz_correct": 1,
            "mic_attempts": 1,
            "mic_success": 1,
            "last_item": "ship",
            "last_payload": {"page": "sounds", "completed_count": 1},
        }

        first = client.post("/api/sounds/progress/", payload, content_type="application/json")
        second = client.post("/api/sounds/progress/", payload, content_type="application/json")

        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 200)
        self.assertTrue(first.json()["changed"])
        self.assertFalse(second.json()["changed"])
