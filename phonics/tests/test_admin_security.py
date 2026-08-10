from decimal import Decimal
from io import StringIO
from types import SimpleNamespace

from django.contrib import admin
from django.contrib.auth.models import Group, User
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse

from phonics.admin_audit import log_admin_action
from phonics.models import (
    AdminAuditLog,
    PaymentOrder,
    PaymentWebhookEvent,
    UserSubscription,
)


class AdminSecuritySprintTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("setup_admin_roles", stdout=StringIO(), verbosity=0)
        cls.superuser = User.objects.create_superuser(
            username="security-admin",
            email="security-admin@example.com",
            password="StrongPass123!",
        )
        cls.customer = User.objects.create_user(
            username="dashboard-customer",
            email="dashboard-customer@example.com",
            password="StrongPass123!",
        )
        cls.marketing_user = cls._staff_user("marketing-viewer", "Marketing Viewer")
        cls.payment_manager = cls._staff_user("payment-manager", "Payment Manager")
        cls.support_agent = cls._staff_user("support-agent", "Support Agent")
        cls.order = PaymentOrder.objects.create(
            user=cls.customer,
            plan_code="silver",
            plan_name="Silver",
            duration_days=30,
            amount_halalas=2700,
            amount_sar=Decimal("27.00"),
            currency="SAR",
            method=PaymentOrder.Method.MOYASAR_CARD,
            provider=PaymentOrder.Provider.MOYASAR,
            provider_payment_id="provider-sensitive-reference-123456",
            status=PaymentOrder.Status.INITIATED,
        )
        cls.subscription = UserSubscription.objects.create(
            user=cls.customer,
            plan_code="silver",
            status=UserSubscription.Status.PENDING_PAYMENT,
        )
        cls.webhook = PaymentWebhookEvent.objects.create(
            provider=PaymentOrder.Provider.MOYASAR,
            event_id="evt-admin-security",
            event_type="payment_paid",
            payment_order=cls.order,
            payload_hash="a" * 64,
        )

    @classmethod
    def _staff_user(cls, username, group_name):
        user = User.objects.create_user(
            username=username,
            email=f"{username}@example.com",
            password="StrongPass123!",
            is_staff=True,
        )
        user.groups.add(Group.objects.get(name=group_name))
        return user

    def test_role_setup_is_idempotent_and_marketing_is_dashboard_only(self):
        call_command("setup_admin_roles", stdout=StringIO(), verbosity=0)

        self.assertEqual(
            set(Group.objects.filter(name__in={
                "Super Admin",
                "Payment Manager",
                "Marketing Viewer",
                "Support Agent",
                "Content Editor",
                "Read-only Analyst",
            }).values_list("name", flat=True)),
            {
                "Super Admin",
                "Payment Manager",
                "Marketing Viewer",
                "Support Agent",
                "Content Editor",
                "Read-only Analyst",
            },
        )
        marketing_permissions = set(
            Group.objects.get(name="Marketing Viewer")
            .permissions.values_list("codename", flat=True)
        )
        self.assertEqual(marketing_permissions, {"view_operations_dashboard"})

    def test_roles_do_not_receive_protected_model_mutation_permissions(self):
        protected_permissions = {
            f"{action}_{model_name}"
            for action in ("add", "change", "delete")
            for model_name in (
                "adminauditlog",
                "paymentactivationreview",
                "paymentorder",
                "paymentwebhookevent",
                "usersubscription",
            )
        }
        roles = Group.objects.filter(name__in={
            "Super Admin",
            "Payment Manager",
            "Marketing Viewer",
            "Support Agent",
            "Content Editor",
            "Read-only Analyst",
        }).prefetch_related("permissions")

        for role in roles:
            role_permissions = set(
                role.permissions.filter(content_type__app_label="phonics")
                .values_list("codename", flat=True)
            )
            self.assertTrue(
                role_permissions.isdisjoint(protected_permissions),
                f"{role.name} has protected mutation permissions",
            )

    def test_marketing_viewer_sees_only_aggregate_dashboard(self):
        self.client.force_login(self.marketing_user)

        response = self.client.get(reverse("admin_operations_dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Users today")
        self.assertContains(response, "MarketingAttribution")
        self.assertNotContains(response, self.customer.email)
        self.assertNotContains(response, self.order.provider_payment_id)
        self.assertNotContains(response, "Latest payment orders")

    def test_marketing_viewer_cannot_view_or_change_payment_order(self):
        self.client.force_login(self.marketing_user)
        change_url = reverse("admin:phonics_paymentorder_change", args=[self.order.pk])

        self.assertEqual(self.client.get(change_url).status_code, 403)
        self.assertEqual(
            self.client.post(change_url, {"status": PaymentOrder.Status.PAID}).status_code,
            403,
        )

    def test_payment_manager_cannot_change_delete_or_manually_activate_order(self):
        self.client.force_login(self.payment_manager)
        change_url = reverse("admin:phonics_paymentorder_change", args=[self.order.pk])
        delete_url = reverse("admin:phonics_paymentorder_delete", args=[self.order.pk])

        self.assertEqual(self.client.get(change_url).status_code, 200)
        self.assertEqual(
            self.client.post(change_url, {"status": PaymentOrder.Status.PAID}).status_code,
            403,
        )
        self.assertEqual(self.client.get(delete_url).status_code, 403)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, PaymentOrder.Status.INITIATED)
        self.assertIsNone(self.order.activated_at)
        self.assertEqual(
            UserSubscription.objects.filter(status=UserSubscription.Status.ACTIVE).count(),
            0,
        )

    def test_support_agent_sees_reduced_payment_fields(self):
        self.client.force_login(self.support_agent)

        response = self.client.get(
            reverse("admin:phonics_paymentorder_change", args=[self.order.pk])
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.order.reference)
        self.assertNotContains(response, self.order.provider_payment_id)
        self.assertNotContains(response, "Idempotency key")

    def test_payment_webhook_event_is_view_only(self):
        request = RequestFactory().get("/admin/phonics/paymentwebhookevent/")
        request.user = self.payment_manager
        model_admin = admin.site._registry[PaymentWebhookEvent]

        self.assertTrue(model_admin.has_view_permission(request, self.webhook))
        self.assertFalse(model_admin.has_add_permission(request))
        self.assertFalse(model_admin.has_change_permission(request, self.webhook))
        self.assertFalse(model_admin.has_delete_permission(request, self.webhook))
        self.assertEqual(model_admin.get_actions(request), {})

    def test_payment_order_and_subscription_cannot_be_deleted(self):
        request = RequestFactory().get("/admin/")
        request.user = self.superuser

        for model, instance in (
            (PaymentOrder, self.order),
            (UserSubscription, self.subscription),
        ):
            model_admin = admin.site._registry[model]
            self.assertFalse(model_admin.has_delete_permission(request, instance))
            self.assertFalse(model_admin.has_change_permission(request, instance))

    def test_sensitive_user_change_creates_append_only_audit_entry(self):
        request = RequestFactory().post("/admin/auth/user/")
        request.user = self.superuser
        model_admin = admin.site._registry[User]
        target = User.objects.get(pk=self.customer.pk)
        target.is_active = False

        model_admin.save_model(request, target, SimpleNamespace(), change=True)

        entry = AdminAuditLog.objects.get(action="user_security_changed")
        self.assertEqual(entry.actor, self.superuser)
        self.assertEqual(entry.target_id, str(target.pk))
        self.assertTrue(entry.before_status["is_active"])
        self.assertFalse(entry.after_status["is_active"])
        entry.note = "changed"
        with self.assertRaises(ValidationError):
            entry.save()
        with self.assertRaises(ValidationError):
            AdminAuditLog.objects.filter(pk=entry.pk).delete()

    def test_audit_log_admin_is_view_only(self):
        request = RequestFactory().get("/admin/phonics/adminauditlog/")
        request.user = self.superuser
        entry = log_admin_action(
            request,
            action="security_test",
            target=self.order,
        )
        model_admin = admin.site._registry[AdminAuditLog]

        self.assertFalse(model_admin.has_add_permission(request))
        self.assertFalse(model_admin.has_change_permission(request, entry))
        self.assertFalse(model_admin.has_delete_permission(request, entry))

    @override_settings(
        MOYASAR_SECRET_KEY="private-test-secret",
        MOYASAR_WEBHOOK_SECRET="webhook-test-secret",
    )
    def test_admin_pages_do_not_render_payment_secrets_or_tracking(self):
        self.client.force_login(self.payment_manager)

        response = self.client.get(
            reverse("admin:phonics_paymentorder_change", args=[self.order.pk])
        )
        content = response.content.decode("utf-8")

        self.assertNotIn("private-test-secret", content)
        self.assertNotIn("webhook-test-secret", content)
        for token in ("googletagmanager", "fbq(", "ttq.", "dataLayer"):
            self.assertNotIn(token, content)
