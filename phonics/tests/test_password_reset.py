from django.contrib.auth.models import User
from django.core import mail
from django.core.cache import cache
from django.test import TestCase, override_settings
from django.urls import reverse


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    RATE_LIMIT_PASSWORD_RESET=5,
    PASSWORD_RESET_TIMEOUT=3600,
)
class PasswordResetTests(TestCase):
    def setUp(self):
        cache.clear()
        self.user = User.objects.create_user(
            username="reset-user",
            email="reset@example.com",
            password="OldStrongPass123!",
        )

    def reset_url_from_email(self):
        body = mail.outbox[-1].body
        return next(line.strip() for line in body.splitlines() if "/accounts/password-reset/confirm/" in line)

    def test_invalid_email_returns_generic_success_without_email(self):
        response = self.client.post(reverse("password_reset"), {"email": "missing@example.com"})
        self.assertRedirects(response, reverse("password_reset_done"))
        self.assertEqual(len(mail.outbox), 0)

    def test_valid_email_sends_temporary_reset_link(self):
        response = self.client.post(reverse("password_reset"), {"email": self.user.email})
        self.assertRedirects(response, reverse("password_reset_done"))
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("/accounts/password-reset/confirm/", mail.outbox[0].body)
        self.assertNotIn("OldStrongPass123!", mail.outbox[0].body)

    def test_invalid_token_is_rejected(self):
        response = self.client.get(
            reverse("password_reset_confirm", kwargs={"uidb64": "invalid", "token": "invalid"})
        )
        self.assertContains(response, "الرابط غير صالح")

    def test_successful_reset_invalidates_old_password_and_link(self):
        self.client.post(reverse("password_reset"), {"email": self.user.email})
        link = self.reset_url_from_email()
        response = self.client.get(link)
        self.assertEqual(response.status_code, 302)
        response = self.client.post(response["Location"], {
            "new_password1": "NewStrongPass456!",
            "new_password2": "NewStrongPass456!",
        })
        self.assertRedirects(response, reverse("password_reset_complete"))
        self.assertFalse(self.client.login(username=self.user.username, password="OldStrongPass123!"))
        self.assertTrue(self.client.login(username=self.user.username, password="NewStrongPass456!"))
        self.client.logout()
        self.assertContains(self.client.get(link), "الرابط غير صالح")

    @override_settings(PASSWORD_RESET_TIMEOUT=-1)
    def test_expired_token_is_rejected(self):
        self.client.post(reverse("password_reset"), {"email": self.user.email})
        self.assertContains(self.client.get(self.reset_url_from_email()), "الرابط غير صالح")

    @override_settings(RATE_LIMIT_PASSWORD_RESET=1)
    def test_rate_limit(self):
        self.client.post(reverse("password_reset"), {"email": self.user.email})
        response = self.client.post(reverse("password_reset"), {"email": self.user.email})
        self.assertEqual(response.status_code, 429)
        self.assertEqual(response["Retry-After"], "3600")
