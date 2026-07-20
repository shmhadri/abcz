from django.contrib.auth.models import User
from django.test import TestCase, override_settings

from phonics.tests.subscription_helpers import grant_active_subscription


@override_settings(DISABLE_AUTO_SEED=True)
class WorksheetsCenterTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="worksheets-diamond", password="StrongPass123!")
        grant_active_subscription(self.user, "diamond")
        self.client.force_login(self.user)

    def test_worksheets_center_returns_success(self):
        response = self.client.get("/worksheets/")

        self.assertEqual(response.status_code, 200)

    def test_worksheets_center_contains_required_content(self):
        response = self.client.get("/worksheets/")

        self.assertContains(response, "أوراق العمل")
        self.assertContains(response, "Printable Worksheets Center")
        self.assertContains(response, "Vocabulary Worksheet")
        self.assertContains(response, "Grammar Worksheet")
        self.assertContains(response, "Mixed Review Worksheet")

    def test_mixed_review_returns_success(self):
        response = self.client.get("/worksheets/mixed-review/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ورقة مراجعة شاملة")

    def test_worksheets_center_has_no_speech_controls(self):
        response = self.client.get("/worksheets/")

        self.assertNotContains(response, "مايك")
        self.assertNotContains(response, "استماع")
