from datetime import timedelta
from decimal import Decimal
from io import StringIO

from django.contrib.auth.models import User
from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import connection
from django.test import TestCase, override_settings
from django.test.utils import CaptureQueriesContext
from django.utils import timezone

from phonics.models import PaymentOrder, UserSubscription


@override_settings(DISABLE_AUTO_SEED=True)
class PaymentSubscriptionMigrationAuditTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="audit-user", password="StrongPass123!")

    def run_audit(self):
        stdout, stderr = StringIO(), StringIO()
        with CaptureQueriesContext(connection) as queries:
            call_command("audit_payment_subscription_migrations", stdout=stdout, stderr=stderr)
        self.assertFalse(any(
            query["sql"].lstrip().upper().startswith(("INSERT", "UPDATE", "DELETE"))
            for query in queries.captured_queries
        ))
        return stdout.getvalue(), stderr.getvalue()

    def test_clean_database_passes_without_writes(self):
        output, errors = self.run_audit()
        self.assertIn("preflight: clean", output)
        self.assertEqual(errors, "")

    def test_invalid_payment_reports_only_ids_and_fails(self):
        order = PaymentOrder.objects.create(
            user=self.user,
            plan_code="basic",
            plan_name="Basic",
            amount_halalas=100,
            amount_sar=Decimal("1.00"),
            currency="USD",
            status=PaymentOrder.Status.PENDING,
            method=PaymentOrder.Method.BANK_TRANSFER,
            provider=PaymentOrder.Provider.MANUAL_BANK,
        )
        stdout, stderr = StringIO(), StringIO()
        with self.assertRaises(CommandError):
            call_command("audit_payment_subscription_migrations", stdout=stdout, stderr=stderr)
        self.assertIn(str(order.id), stderr.getvalue())
        self.assertNotIn(self.user.username, stderr.getvalue())

    def test_overlapping_active_main_subscriptions_fail(self):
        now = timezone.now()
        for code in ("basic", "silver"):
            UserSubscription.objects.create(
                user=self.user,
                plan_code=code,
                status=UserSubscription.Status.ACTIVE,
                starts_at=now - timedelta(days=1),
                expires_at=now + timedelta(days=29),
            )
        with self.assertRaises(CommandError):
            call_command("audit_payment_subscription_migrations", stdout=StringIO(), stderr=StringIO())
