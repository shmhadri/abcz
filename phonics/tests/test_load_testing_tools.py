import os
from pathlib import Path
from tempfile import TemporaryDirectory
from io import StringIO
from unittest.mock import patch

from load_tests.analyze_results import summarize_stats_csv
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase

from load_tests.config import get_config, validate_base_url
from load_tests.scenarios import SCENARIO_WEIGHTS, SILVER_PAGES, csrf_token_from_client, json_headers
from phonics.management.commands.create_load_test_data import LOAD_TEST_EMAIL_DOMAIN, LOAD_TEST_SCHOOL
from phonics.models import (
    CVCReadingProgress,
    EnglishFoundationProgress,
    SoundPracticeProgress,
    StudentProfile,
    UserSubscription,
)


class LoadTestDataCommandTests(TestCase):
    prefix = "loadtest_case_"
    password = "LoadTestPass123!"

    def test_create_load_test_data_builds_isolated_users(self):
        output = StringIO()
        call_command(
            "create_load_test_data",
            users=2,
            prefix=self.prefix,
            password=self.password,
            stdout=output,
        )

        User = get_user_model()
        users = User.objects.filter(username__startswith=self.prefix)
        self.assertEqual(users.count(), 10)
        self.assertTrue(users.filter(email__endswith=f"@{LOAD_TEST_EMAIL_DOMAIN}").exists())
        self.assertEqual(
            StudentProfile.objects.filter(user__username__startswith=self.prefix, school=LOAD_TEST_SCHOOL).count(),
            10,
        )
        self.assertEqual(UserSubscription.objects.filter(user__username__startswith=self.prefix).count(), 8)
        self.assertEqual(SoundPracticeProgress.objects.filter(user__username__startswith=self.prefix).count(), 4)
        self.assertEqual(CVCReadingProgress.objects.filter(user__username__startswith=self.prefix).count(), 4)
        self.assertEqual(EnglishFoundationProgress.objects.filter(user__username__startswith=self.prefix).count(), 16)

    def test_cleanup_is_dry_run_without_yes(self):
        call_command("create_load_test_data", users=1, prefix=self.prefix, password=self.password, stdout=StringIO())
        call_command("cleanup_load_test_data", prefix=self.prefix, stdout=StringIO())
        User = get_user_model()
        self.assertEqual(User.objects.filter(username__startswith=self.prefix).count(), 5)

    def test_cleanup_deletes_only_marked_load_test_users(self):
        User = get_user_model()
        safe_user = User.objects.create_user(
            username=f"{self.prefix}real_0001",
            email="real@example.com",
            password="secret",
        )
        call_command("create_load_test_data", users=1, prefix=self.prefix, password=self.password, stdout=StringIO())

        call_command("cleanup_load_test_data", prefix=self.prefix, yes=True, stdout=StringIO())

        self.assertTrue(User.objects.filter(pk=safe_user.pk).exists())
        self.assertEqual(
            User.objects.filter(username__startswith=self.prefix, email__endswith=f"@{LOAD_TEST_EMAIL_DOMAIN}").count(),
            0,
        )

    def test_unsafe_prefixes_are_rejected(self):
        with self.assertRaises(SystemExit):
            call_command("create_load_test_data", users=1, prefix="user_", stdout=StringIO())
        with self.assertRaises(SystemExit):
            call_command("cleanup_load_test_data", prefix="user_", stdout=StringIO())


class LoadTestConfigTests(TestCase):
    def test_production_url_is_blocked_by_default(self):
        with self.assertRaisesMessage(ValueError, "Refusing to run load tests against production"):
            validate_base_url("https://abcz-epbz.onrender.com")

    def test_production_url_can_be_allowed_explicitly(self):
        self.assertEqual(
            validate_base_url("https://abcz-epbz.onrender.com/", allow_production=True),
            "https://abcz-epbz.onrender.com",
        )

    def test_config_rejects_unsafe_prefix(self):
        env = {
            "LOAD_TEST_BASE_URL": "http://127.0.0.1:8000",
            "LOAD_TEST_USERNAME_PREFIX": "real_",
        }
        with patch.dict(os.environ, env, clear=True):
            with self.assertRaisesMessage(ValueError, "LOAD_TEST_USERNAME_PREFIX"):
                get_config()

    def test_config_reads_safe_environment(self):
        env = {
            "LOAD_TEST_BASE_URL": "http://127.0.0.1:8000/",
            "LOAD_TEST_USERNAME_PREFIX": "loadtest_env_",
            "LOAD_TEST_PASSWORD": "pw",
            "LOAD_TEST_RUN_ID": "case-1",
        }
        with patch.dict(os.environ, env, clear=True):
            config = get_config()
        self.assertEqual(config.base_url, "http://127.0.0.1:8000")
        self.assertEqual(config.username_prefix, "loadtest_env_")
        self.assertEqual(config.password, "pw")
        self.assertEqual(config.run_id, "case-1")


class LoadTestScenarioTests(TestCase):
    def test_scenario_weights_match_required_mix(self):
        self.assertEqual(SCENARIO_WEIGHTS["visitor"], 30)
        self.assertEqual(SCENARIO_WEIGHTS["silver"], 30)
        self.assertEqual(SCENARIO_WEIGHTS["level3"], 15)
        self.assertEqual(SCENARIO_WEIGHTS["level4"], 15)
        self.assertEqual(SCENARIO_WEIGHTS["diamond"], 10)
        self.assertEqual(sum(SCENARIO_WEIGHTS.values()), 100)

    def test_silver_scenario_uses_silver_allowed_worksheet_routes(self):
        silver_paths = {step.path for step in SILVER_PAGES}
        self.assertIn("/sounds/worksheet/", silver_paths)
        self.assertIn("/letters/worksheet/", silver_paths)
        self.assertNotIn("/worksheets/", silver_paths)

    def test_csrf_helpers_support_plain_cookie_values(self):
        class Client:
            cookies = {"csrftoken": "abc123"}

        self.assertEqual(csrf_token_from_client(Client()), "abc123")
        self.assertEqual(json_headers(Client())["X-CSRFToken"], "abc123")


class LoadTestAnalysisTests(TestCase):
    def test_summarize_locust_stats_csv(self):
        with TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "sample_stats.csv"
            path.write_text(
                "\n".join([
                    "Type,Name,Request Count,Failure Count,Average Response Time,Requests/s,95%",
                    "GET,visitor:index,100,0,120,10,220",
                    "GET,silver:sounds,80,2,300,8,750",
                    ",Aggregated,180,2,200,18,600",
                ]),
                encoding="utf-8",
            )

            summary = summarize_stats_csv(path)

        self.assertEqual(summary.requests, 180)
        self.assertEqual(summary.failures, 2)
        self.assertEqual(summary.failure_rate, 1.11)
        self.assertEqual(summary.requests_per_second, 18)
        self.assertEqual(summary.p95_response_ms, 600)
        self.assertEqual(summary.slowest_name, "silver:sounds")
        self.assertEqual(summary.slowest_p95_ms, 750)
