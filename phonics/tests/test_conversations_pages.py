from pathlib import Path

from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase, override_settings

from phonics.tests.subscription_helpers import grant_active_subscription


@override_settings(DISABLE_AUTO_SEED=True)
class ConversationsPagesTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="conversations-diamond", password="StrongPass123!")
        grant_active_subscription(self.user, "diamond")
        self.client.force_login(self.user)

    def test_conversations_page_returns_success(self):
        response = self.client.get("/conversations/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "المحادثات")
        self.assertContains(response, "Interactive Conversations")
        self.assertContains(response, "At school")
        self.assertContains(response, "At the restaurant")
        self.assertContains(response, "Conversation Speed Challenge")
        self.assertContains(response, "conversations.js")
        self.assertContains(response, "CONVERSATIONS_PROGRESS_URL")

    def test_conversations_worksheet_returns_success(self):
        response = self.client.get("/conversations/worksheet/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ورقة عمل المحادثات")
        self.assertContains(response, "اختر الرد الصحيح")
        self.assertContains(response, "اكتب حوارًا قصيرًا")

    def test_conversations_static_data_has_twenty_situations(self):
        js_path = Path(settings.BASE_DIR) / "static" / "js" / "conversations.js"
        content = js_path.read_text(encoding="utf-8")

        self.assertEqual(content.count("conversation({ id:"), 20)
