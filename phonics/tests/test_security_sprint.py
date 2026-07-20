import json
from unittest.mock import patch

from django.contrib.auth.models import User
from django.core.cache import cache
from django.test import TestCase, override_settings
from django.urls import reverse

from phonics.models import Student


class SecuritySprintTests(TestCase):
    def setUp(self):
        cache.clear()

    def test_private_certificate_rejects_anonymous_and_normal_user(self):
        student = Student.objects.create(name="Private Student")
        anonymous = self.client.get(reverse("generate_certificate", args=[student.id]))
        self.assertEqual(anonymous.status_code, 302)

        user = User.objects.create_user(username="normal", password="StrongPass123!")
        self.client.force_login(user)
        forbidden = self.client.get(reverse("generate_certificate", args=[student.id]))
        self.assertEqual(forbidden.status_code, 404)

    def test_legacy_cvc_writer_requires_login_and_never_creates_student(self):
        payload = {"student": "Injected Student", "type": "word", "points": 1000}
        anonymous = self.client.post(
            reverse("api_save_cvc_progress"), data=json.dumps(payload), content_type="application/json"
        )
        self.assertEqual(anonymous.status_code, 302)
        self.assertFalse(Student.objects.filter(name="Injected Student").exists())

        user = User.objects.create_user(username="cvc-user", password="StrongPass123!")
        self.client.force_login(user)
        retired = self.client.post(
            reverse("api_save_cvc_progress"), data=json.dumps(payload), content_type="application/json"
        )
        self.assertIn(retired.status_code, {403, 410})
        self.assertFalse(Student.objects.filter(name="Injected Student").exists())

    @override_settings(RATE_LIMIT_LOGIN=2)
    def test_login_rate_limit_returns_429(self):
        # Keep all requests in the same fixed window even on a heavily loaded test host.
        with patch("phonics.security.time.time", return_value=1_700_000_000):
            for _ in range(2):
                response = self.client.post("/accounts/login/", {"username": "missing", "password": "wrong"})
                self.assertEqual(response.status_code, 200)
            response = self.client.post("/accounts/login/", {"username": "missing", "password": "wrong"})
        self.assertEqual(response.status_code, 429)
        self.assertEqual(response.json()["error"], "rate_limited")

    @override_settings(RATE_LIMIT_LOGIN=2)
    def test_login_account_limit_is_independent_of_ip(self):
        # Keep the three requests in one deterministic fixed window.
        with patch("phonics.security.time.time", return_value=1_700_000_000):
            for ip in ["192.0.2.10", "192.0.2.11"]:
                response = self.client.post(
                    "/accounts/login/", {"username": "same-account", "password": "wrong"}, REMOTE_ADDR=ip
                )
                self.assertEqual(response.status_code, 200)
            response = self.client.post(
                "/accounts/login/", {"username": "same-account", "password": "wrong"}, REMOTE_ADDR="192.0.2.12"
            )
        self.assertEqual(response.status_code, 429)

    @override_settings(RATE_LIMIT_LOGIN=2)
    def test_login_ip_limit_is_independent_of_account(self):
        # Keep the three requests in one deterministic fixed window.
        with patch("phonics.security.time.time", return_value=1_700_000_000):
            for username in ["first-account", "second-account"]:
                response = self.client.post(
                    "/accounts/login/", {"username": username, "password": "wrong"}, REMOTE_ADDR="192.0.2.20"
                )
                self.assertEqual(response.status_code, 200)
            response = self.client.post(
                "/accounts/login/", {"username": "third-account", "password": "wrong"}, REMOTE_ADDR="192.0.2.20"
            )
        self.assertEqual(response.status_code, 429)

    def test_rate_limit_store_failure_does_not_fail_open(self):
        with patch("phonics.security.cache.add", side_effect=RuntimeError("cache unavailable")):
            response = self.client.post("/accounts/login/", {"username": "user", "password": "secret"})
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()["error"], "rate_limit_unavailable")

    def test_security_headers_are_present(self):
        response = self.client.get("/health/")
        self.assertEqual(
            response["Content-Security-Policy-Report-Only"],
            "default-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'",
        )
