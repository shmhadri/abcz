from pathlib import Path

from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase, override_settings

from phonics.tests.subscription_helpers import grant_active_subscription


@override_settings(DISABLE_AUTO_SEED=True)
class CommonSentencesPagesTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="common-sentences-diamond", password="StrongPass123!")
        grant_active_subscription(self.user, "diamond")
        self.client.force_login(self.user)

    def test_common_sentences_page_returns_success(self):
        response = self.client.get("/common-sentences/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "الجمل الشائعة")
        self.assertContains(response, "Common English Sentences")
        self.assertContains(response, "Good morning")
        self.assertContains(response, "Never give up")
        self.assertContains(response, "اختبار سرعة القراءة")
        self.assertContains(response, "Minute Challenge")
        self.assertContains(response, "csThemeToggle")
        self.assertContains(response, "العودة للتأسيس")
        self.assertContains(response, "common_sentences.js")
        self.assertContains(response, "COMMON_SENTENCES_PROGRESS_URL")

    def test_common_sentences_worksheet_returns_success(self):
        response = self.client.get("/common-sentences/worksheet/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ورقة عمل الجمل الشائعة")
        self.assertContains(response, "ترجم 10 جمل")
        self.assertContains(response, "تقييم المعلم")

    def test_common_sentences_static_data_has_sixty_sentences(self):
        js_path = Path(settings.BASE_DIR) / "static" / "js" / "common_sentences.js"
        content = js_path.read_text(encoding="utf-8")

        sentence_rows = [
            line for line in content.splitlines()
            if line.strip().startswith('["') and '", "' in line
        ]
        self.assertEqual(len(sentence_rows), 60)
