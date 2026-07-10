from datetime import timedelta

from django.contrib.auth.models import Group, User
from django.test import TestCase, override_settings
from django.utils import timezone

from phonics.models import UserSubscription
from phonics.views import PLAN_LEVEL_FOUR, PLAN_LEVEL_THREE


@override_settings(DISABLE_AUTO_SEED=True)
class SubscriptionAccessControlTests(TestCase):
    def activate_plan(self, user, plan_code):
        now = timezone.now()
        return UserSubscription.objects.create(
            user=user,
            plan_code=plan_code,
            status=UserSubscription.Status.ACTIVE,
            starts_at=now - timedelta(minutes=1),
            expires_at=now + timedelta(days=30),
        )

    def create_logged_in_user(self, username, *, group_name=None, plan_code=None):
        user = User.objects.create_user(username=username, password="StrongPass123!")
        if group_name:
            group, _ = Group.objects.get_or_create(name=group_name)
            user.groups.add(group)
        if plan_code:
            self.activate_plan(user, plan_code)
        self.client.force_login(user)
        return user

    def test_level_three_subscription_opens_cvc_only(self):
        self.create_logged_in_user("level-three-user", plan_code=PLAN_LEVEL_THREE)

        for path in ["/cvc-reading/", "/cvc-reading/worksheet/", "/api/cvc-words/"]:
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200)

        for path in ["/sounds/", "/level-four/"]:
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 403)

    def test_level_four_subscription_opens_level_four_only(self):
        self.create_logged_in_user("level-four-user", plan_code=PLAN_LEVEL_FOUR)

        for path in ["/level-four/", "/level-four/reading/", "/english-foundation/"]:
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200)

        for path in ["/sounds/", "/cvc-reading/"]:
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 403)

    def test_silver_opens_sounds_but_not_cvc_or_level_four(self):
        self.create_logged_in_user("silver-access-user", group_name="Silver")

        for path in ["/sounds/", "/sounds/worksheet/", "/api/sounds/progress/"]:
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200)

        for path in ["/cvc-reading/", "/level-four/", "/english-foundation/"]:
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 403)

