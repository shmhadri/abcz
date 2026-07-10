from django.test import TestCase, override_settings


@override_settings(DISABLE_AUTO_SEED=True)
class WorksheetsCenterTests(TestCase):
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
