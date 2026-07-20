from pathlib import Path

from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase, override_settings

from phonics.tests.subscription_helpers import grant_active_subscription


@override_settings(DISABLE_AUTO_SEED=True)
class GrammarFoundationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="grammar-diamond", password="StrongPass123!")
        grant_active_subscription(self.user, "diamond")
        self.client.force_login(self.user)

    def test_grammar_foundation_page_returns_success(self):
        response = self.client.get("/grammar-foundation/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "القواعد التأسيسية")
        self.assertContains(response, "Subject Pronouns")
        self.assertContains(response, "Present Simple")
        self.assertContains(response, "Comparative and Superlative")
        self.assertContains(response, "Grammar Speed Challenge")
        self.assertContains(response, "العودة للتأسيس")
        self.assertContains(response, "gfThemeToggle")
        self.assertContains(response, "grammar_foundation.js")
        self.assertContains(response, "GRAMMAR_PROGRESS_URL")

    def test_grammar_worksheet_returns_success(self):
        response = self.client.get("/grammar-foundation/worksheet/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ورقة عمل القواعد")
        self.assertContains(response, "اختر الإجابة الصحيحة")
        self.assertContains(response, "صحح الخطأ")

    def test_grammar_static_data_has_thirty_lessons(self):
        js_path = Path(settings.BASE_DIR) / "static" / "js" / "grammar_foundation.js"
        content = js_path.read_text(encoding="utf-8")

        self.assertEqual(content.count("lesson({ id:"), 30)
