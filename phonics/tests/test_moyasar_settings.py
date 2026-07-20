import os
import subprocess
import sys

from django.test import SimpleTestCase


class MoyasarSettingsValidationTests(SimpleTestCase):
    maxDiff = None

    def load_settings(self, **overrides):
        environment = os.environ.copy()
        environment.update({
            "DJANGO_ENV": "development",
            "RENDER": "False",
            "DEBUG": "True",
            "SECRET_KEY": "settings-validation-only-not-a-real-secret",
            "ALLOWED_HOSTS": "payments.example.com",
            "MOYASAR_ENABLED": "False",
            "MOYASAR_ENVIRONMENT": "test",
            "MOYASAR_PUBLISHABLE_KEY": "",
            "MOYASAR_SECRET_KEY": "",
            "MOYASAR_WEBHOOK_SECRET": "",
            "MOYASAR_CALLBACK_URL": "",
            "MOYASAR_WEBHOOK_URL": "",
            "MOYASAR_API_URL": "https://api.moyasar.com/v1",
            "MOYASAR_CHECKOUT_ALLOWED_HOSTS": "checkout.moyasar.com",
        })
        environment.update(overrides)
        return subprocess.run(
            [sys.executable, "-c", "import abcz.settings; print('settings_loaded')"],
            cwd=str(settings_root()),
            env=environment,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )

    def assert_settings_rejected(self, result):
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("ImproperlyConfigured", result.stderr)

    def test_live_with_missing_keys_fails_closed(self):
        result = self.load_settings(MOYASAR_ENVIRONMENT="live", MOYASAR_ENABLED="True")
        self.assert_settings_rejected(result)

    def test_live_rejects_test_keys(self):
        result = self.load_settings(
            MOYASAR_ENVIRONMENT="live",
            MOYASAR_ENABLED="True",
            MOYASAR_PUBLISHABLE_KEY="pk_test_settings_fixture",
            MOYASAR_SECRET_KEY="sk_test_settings_fixture",
        )
        self.assert_settings_rejected(result)

    def test_test_rejects_live_keys(self):
        result = self.load_settings(
            MOYASAR_ENVIRONMENT="test",
            MOYASAR_PUBLISHABLE_KEY="pk_live_settings_fixture",
            MOYASAR_SECRET_KEY="sk_live_settings_fixture",
        )
        self.assert_settings_rejected(result)

    def test_complete_live_configuration_loads(self):
        result = self.load_settings(
            MOYASAR_ENVIRONMENT="live",
            MOYASAR_ENABLED="True",
            MOYASAR_PUBLISHABLE_KEY="pk_live_settings_fixture",
            MOYASAR_SECRET_KEY="sk_live_settings_fixture",
            MOYASAR_WEBHOOK_SECRET="webhook-settings-fixture",
            MOYASAR_CALLBACK_URL="https://payments.example.com/payments/moyasar/callback/",
            MOYASAR_WEBHOOK_URL="https://payments.example.com/payments/moyasar/webhook/",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "settings_loaded")


def settings_root():
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
