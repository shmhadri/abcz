from datetime import timedelta
from unittest.mock import patch

from django.contrib.auth.models import Group, User
from django.core.cache import cache
from django.test import TestCase, override_settings
from django.test.utils import CaptureQueriesContext
from django.db import connection
from django.utils import timezone

from phonics.cache_helpers import user_cache_key
from phonics.models import StudentProfile, UserSubscription
from phonics.views import PLAN_LEVEL_THREE, PLAN_SILVER, get_feature_keys


CACHE_SETTINGS = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "cache-readiness-tests",
    }
}


@override_settings(CACHES=CACHE_SETTINGS, SUBSCRIPTION_CACHE_TIMEOUT=300)
class SubscriptionCacheReadinessTests(TestCase):
    def setUp(self):
        cache.clear()

    def tearDown(self):
        cache.clear()

    def create_user(self, username="cache-user", plan_code=None):
        user = User.objects.create_user(username=username, password="secret")
        StudentProfile.objects.create(
            user=user,
            display_name=username,
            student_name=username,
            school="cache-test",
            parent_phone="",
        )
        if plan_code:
            now = timezone.now()
            UserSubscription.objects.create(
                user=user,
                plan_code=plan_code,
                status=UserSubscription.Status.ACTIVE,
                starts_at=now - timedelta(minutes=5),
                expires_at=now + timedelta(days=7),
            )
        return user

    def test_feature_keys_are_recomputed_to_honor_subscription_expiry(self):
        user = self.create_user(plan_code=PLAN_SILVER)

        with CaptureQueriesContext(connection) as first_queries:
            first_keys = get_feature_keys(user)
        with CaptureQueriesContext(connection) as second_queries:
            second_keys = get_feature_keys(user)

        self.assertIn("sounds_basic", first_keys)
        self.assertEqual(first_keys, second_keys)
        self.assertGreater(len(first_queries), 0)
        self.assertGreater(len(second_queries), 0)

    def test_feature_cache_is_isolated_per_user(self):
        silver_user = self.create_user("cache-silver", PLAN_SILVER)
        level_three_user = self.create_user("cache-level-three", PLAN_LEVEL_THREE)

        silver_keys = get_feature_keys(silver_user)
        level_three_keys = get_feature_keys(level_three_user)

        self.assertIn("sounds_basic", silver_keys)
        self.assertNotIn("cvc_words", silver_keys)
        self.assertIn("cvc_words", level_three_keys)
        self.assertNotIn("sounds_basic", level_three_keys)

    def test_subscription_save_invalidates_cached_feature_keys(self):
        user = self.create_user()
        self.assertNotIn("sounds_basic", get_feature_keys(user))

        now = timezone.now()
        with self.captureOnCommitCallbacks(execute=True):
            UserSubscription.objects.create(
                user=user,
                plan_code=PLAN_SILVER,
                status=UserSubscription.Status.ACTIVE,
                starts_at=now - timedelta(minutes=5),
                expires_at=now + timedelta(days=7),
            )

        self.assertIn("sounds_basic", get_feature_keys(user))

    def test_group_membership_alone_does_not_grant_feature_keys(self):
        user = self.create_user()
        group = Group.objects.create(name="Silver")
        self.assertNotIn("sounds_basic", get_feature_keys(user))

        with self.captureOnCommitCallbacks(execute=True):
            user.groups.add(group)

        self.assertNotIn("sounds_basic", get_feature_keys(user))

    def test_cache_failure_falls_back_to_database_calculation(self):
        user = self.create_user(plan_code=PLAN_SILVER)

        with patch("phonics.cache_helpers.cache.get", side_effect=RuntimeError("cache down")):
            with patch("phonics.cache_helpers.cache.set", side_effect=RuntimeError("cache down")):
                keys = get_feature_keys(user)

        self.assertIn("sounds_basic", keys)

    def test_feature_payload_is_not_persisted_in_shared_cache(self):
        user = self.create_user(plan_code=PLAN_SILVER)
        get_feature_keys(user)

        stored = cache.get(user_cache_key("feature-keys", user.pk))

        self.assertIsNone(stored)


@override_settings(CACHES=CACHE_SETTINGS, PUBLIC_PAGE_CACHE_TIMEOUT=600)
class PublicPageCacheTests(TestCase):
    def setUp(self):
        cache.clear()

    def tearDown(self):
        cache.clear()

    def test_pricing_page_is_not_publicly_cached_because_actions_are_user_specific(self):
        response = self.client.get("/pricing/")

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("max-age=600", response.headers.get("Cache-Control", ""))
