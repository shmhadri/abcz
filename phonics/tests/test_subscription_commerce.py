from datetime import timedelta
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch
from zoneinfo import ZoneInfo

from django.contrib.auth.models import Group, User
from django.test import TestCase, override_settings
from django.utils import timezone

from phonics.models import (
    PaymentOrder,
    PaymentActivationReview,
    StudentProfile,
    UserSubscription,
    activate_subscription_from_payment,
)
from phonics.payments.moyasar import MoyasarInvoice
from phonics.plans import (
    PLAN_BASIC,
    PLAN_DIAMOND,
    PLAN_LEVEL_FOUR,
    PLAN_LEVEL_THREE,
    PLAN_SILVER,
    PLAN_VIP,
)
from phonics.subscriptions import (
    PurchaseNotAllowed,
    get_user_entitlements,
    purchase_options_for_user,
    quote_plan_purchase,
    subscription_dashboard_context,
    synchronize_user_subscription_compatibility,
)
from phonics.tests.subscription_helpers import grant_active_subscription
from phonics.views import CHECKOUT_PLANS, create_payment_order_for_plan


@override_settings(DISABLE_AUTO_SEED=True, SECURE_SSL_REDIRECT=False, RATE_LIMIT_PAYMENT=1000)
class SubscriptionCommercePolicyTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="commerce-user", password="StrongPass123!")
        StudentProfile.objects.create(
            user=self.user,
            student_name="Commerce Test",
            is_premium=False,
            is_vip=False,
        )

    def expire_plan(self, plan_code):
        now = timezone.now()
        return UserSubscription.objects.update_or_create(
            user=self.user,
            plan_code=plan_code,
            defaults={
                "status": UserSubscription.Status.ACTIVE,
                "starts_at": now - timedelta(days=31),
                "expires_at": now - timedelta(minutes=1),
            },
        )[0]

    def paid_order(self, target, *, source=""):
        quote = quote_plan_purchase(self.user, target)
        order = create_payment_order_for_plan(
            self.user,
            CHECKOUT_PLANS[target],
            "moyasar",
            quote=quote,
        )
        order.status = PaymentOrder.Status.PAID
        order.paid_at = timezone.now()
        order.save(update_fields=["status", "paid_at", "updated_at"])
        return order

    def assert_expired_main_denied(self, plan_code, feature):
        self.expire_plan(plan_code)
        group, _ = Group.objects.get_or_create(name=plan_code.title())
        self.user.groups.add(group)
        profile = self.user.student_profile
        profile.is_premium = True
        profile.is_vip = True
        profile.save(update_fields=["is_premium", "is_vip", "updated_at"])

        snapshot = get_user_entitlements(self.user)

        self.assertIsNone(snapshot.main_subscription)
        self.assertNotIn(feature, snapshot.entitlements)

    def test_01_expired_basic_does_not_grant_access(self):
        self.assert_expired_main_denied(PLAN_BASIC, "letters_full")

    def test_02_expired_silver_does_not_grant_access(self):
        self.assert_expired_main_denied(PLAN_SILVER, "sounds_full")

    def test_03_expired_vip_does_not_grant_access(self):
        self.assert_expired_main_denied(PLAN_VIP, "bird_tutor")

    def test_04_expired_diamond_does_not_grant_advanced_levels(self):
        self.assert_expired_main_denied(PLAN_DIAMOND, "level_four")
        self.assertNotIn("cvc_words", get_user_entitlements(self.user).entitlements)

    def test_05_groups_and_profile_flags_alone_never_grant_access(self):
        group = Group.objects.create(name="Diamond")
        self.user.groups.add(group)
        profile = self.user.student_profile
        profile.is_premium = True
        profile.is_vip = True
        profile.save(update_fields=["is_premium", "is_vip", "updated_at"])

        snapshot = get_user_entitlements(self.user)

        self.assertFalse(snapshot.entitlements)

    def test_06_compatibility_sync_removes_stale_group_and_flags(self):
        group = Group.objects.create(name="VIP")
        self.user.groups.add(group)
        profile = self.user.student_profile
        profile.is_premium = True
        profile.is_vip = True
        profile.save(update_fields=["is_premium", "is_vip", "updated_at"])

        synchronize_user_subscription_compatibility(self.user)

        profile.refresh_from_db()
        self.assertFalse(self.user.groups.filter(name="VIP").exists())
        self.assertFalse(profile.is_premium)
        self.assertFalse(profile.is_vip)

    def test_07_active_same_plan_is_blocked_and_expired_plan_can_renew(self):
        current = grant_active_subscription(self.user, PLAN_BASIC)

        with self.assertRaises(PurchaseNotAllowed) as caught:
            quote_plan_purchase(self.user, PLAN_BASIC)
        self.assertEqual(caught.exception.code, "active_subscription")

        current.expires_at = timezone.now() - timedelta(minutes=1)
        current.save(update_fields=["expires_at", "updated_at"])
        expired_quote = quote_plan_purchase(self.user, PLAN_BASIC)
        self.assertEqual(expired_quote.operation_type, PaymentOrder.OperationType.RENEWAL)

    def test_08_basic_to_silver_upgrade_charges_only_full_price_difference(self):
        current = grant_active_subscription(self.user, PLAN_BASIC)

        quote = quote_plan_purchase(self.user, PLAN_SILVER)

        self.assertEqual(quote.operation_type, PaymentOrder.OperationType.UPGRADE)
        self.assertEqual(quote.from_plan_code, PLAN_BASIC)
        self.assertEqual(quote.amount_due, Decimal("8.00"))
        self.assertEqual(quote.current_expires_at, current.expires_at)

    def test_09_lower_main_plan_is_rejected_server_side(self):
        grant_active_subscription(self.user, PLAN_VIP)

        with self.assertRaises(PurchaseNotAllowed) as caught:
            quote_plan_purchase(self.user, PLAN_SILVER)

        self.assertEqual(caught.exception.code, "lower_main_plan")

    def test_10_diamond_rejects_all_lower_main_plans(self):
        grant_active_subscription(self.user, PLAN_DIAMOND)

        for target in (PLAN_BASIC, PLAN_SILVER, PLAN_VIP):
            with self.subTest(target=target):
                with self.assertRaises(PurchaseNotAllowed) as caught:
                    quote_plan_purchase(self.user, target)
                self.assertEqual(caught.exception.code, "lower_main_plan")

    def test_11_diamond_rejects_addons_because_they_are_included(self):
        grant_active_subscription(self.user, PLAN_DIAMOND)

        for target in (PLAN_LEVEL_THREE, PLAN_LEVEL_FOUR):
            with self.subTest(target=target):
                with self.assertRaises(PurchaseNotAllowed) as caught:
                    quote_plan_purchase(self.user, target)
                self.assertEqual(caught.exception.code, "included_in_diamond")

    def test_12_standalone_level_three_purchase_is_allowed(self):
        quote = quote_plan_purchase(self.user, PLAN_LEVEL_THREE)

        self.assertEqual(quote.operation_type, PaymentOrder.OperationType.PURCHASE)
        self.assertEqual(quote.amount_due, Decimal("15.00"))

    def test_13_renewal_restarts_expired_plan_and_keeps_one_row(self):
        current = grant_active_subscription(self.user, PLAN_BASIC)
        current.expires_at = timezone.now() - timedelta(minutes=1)
        current.save(update_fields=["expires_at", "updated_at"])
        activation_floor = timezone.now()
        order = self.paid_order(PLAN_BASIC)

        renewed = activate_subscription_from_payment(order)

        self.assertGreaterEqual(renewed.starts_at, activation_floor)
        self.assertEqual(renewed.expires_at, renewed.starts_at + timedelta(days=30))
        self.assertEqual(UserSubscription.objects.filter(user=self.user, plan_code=PLAN_BASIC).count(), 1)

    def test_14_upgrade_preserves_term_and_leaves_one_active_main(self):
        source = grant_active_subscription(self.user, PLAN_BASIC)
        old_start, old_expiry = source.starts_at, source.expires_at
        order = self.paid_order(PLAN_SILVER)

        upgraded = activate_subscription_from_payment(order)

        source.refresh_from_db()
        self.assertEqual(source.status, UserSubscription.Status.CANCELED)
        self.assertEqual(upgraded.starts_at, old_start)
        self.assertEqual(upgraded.expires_at, old_expiry)
        self.assertEqual(
            UserSubscription.objects.filter(user=self.user, status=UserSubscription.Status.ACTIVE).count(),
            1,
        )

    def test_upgrade_paid_at_exact_expiry_requires_one_review_and_grants_nothing(self):
        source = grant_active_subscription(self.user, PLAN_BASIC)
        order = self.paid_order(PLAN_SILVER)
        expiry = timezone.now()
        source.expires_at = expiry
        source.save(update_fields=["expires_at", "updated_at"])
        order.current_expires_at = expiry
        order.save(update_fields=["current_expires_at", "updated_at"])

        self.assertIsNone(activate_subscription_from_payment(order))
        order.refresh_from_db()
        self.assertEqual(order.status, PaymentOrder.Status.PAID_REQUIRES_REVIEW)
        self.assertIsNone(order.activated_at)
        self.assertEqual(PaymentActivationReview.objects.filter(payment_order=order).count(), 1)
        self.assertNotIn(PLAN_SILVER, get_user_entitlements(self.user).plan_codes)
        self.assertEqual(quote_plan_purchase(self.user, PLAN_SILVER).ui_state, "payment_pending")
        self.client.force_login(self.user)
        with patch("phonics.views.create_moyasar_invoice") as create_invoice_mock:
            response = self.client.post("/checkout/silver/create/moyasar/")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/payments/pending/", response["Location"])
        create_invoice_mock.assert_not_called()
        self.assertEqual(PaymentOrder.objects.filter(user=self.user).count(), 1)

        self.assertIsNone(activate_subscription_from_payment(order))
        self.assertEqual(PaymentActivationReview.objects.filter(payment_order=order).count(), 1)

    def test_upgrade_paid_after_expiry_requires_review(self):
        source = grant_active_subscription(self.user, PLAN_BASIC)
        order = self.paid_order(PLAN_SILVER)
        expired_at = timezone.now() - timedelta(seconds=1)
        source.expires_at = expired_at
        source.save(update_fields=["expires_at", "updated_at"])
        order.current_expires_at = expired_at
        order.save(update_fields=["current_expires_at", "updated_at"])

        self.assertIsNone(activate_subscription_from_payment(order))
        order.refresh_from_db()
        self.assertEqual(order.status, PaymentOrder.Status.PAID_REQUIRES_REVIEW)
        self.assertFalse(UserSubscription.objects.filter(user=self.user, plan_code=PLAN_SILVER).exists())

    def test_15_payment_order_snapshots_are_computed_by_server(self):
        grant_active_subscription(self.user, PLAN_BASIC)

        order = create_payment_order_for_plan(
            self.user,
            CHECKOUT_PLANS[PLAN_SILVER],
            "moyasar",
        )

        self.assertEqual(order.operation_type, PaymentOrder.OperationType.UPGRADE)
        self.assertEqual(order.original_price, Decimal("19.00"))
        self.assertEqual(order.target_price, Decimal("27.00"))
        self.assertEqual(order.amount_due, Decimal("8.00"))
        self.assertEqual(order.amount_sar, Decimal("8.00"))
        self.assertEqual(order.amount_halalas, 800)

    def test_16_activation_is_idempotent_for_the_same_payment_order(self):
        current = grant_active_subscription(self.user, PLAN_BASIC)
        current.expires_at = timezone.now() - timedelta(minutes=1)
        current.save(update_fields=["expires_at", "updated_at"])
        order = self.paid_order(PLAN_BASIC)

        first = activate_subscription_from_payment(order)
        first_expiry = first.expires_at
        second = activate_subscription_from_payment(order)

        self.assertEqual(second.pk, current.pk)
        self.assertEqual(second.expires_at, first_expiry)

    def test_17_renewing_an_expired_addon_keeps_one_row(self):
        current = grant_active_subscription(self.user, PLAN_LEVEL_THREE)
        current.expires_at = timezone.now() - timedelta(minutes=1)
        current.save(update_fields=["expires_at", "updated_at"])
        activation_floor = timezone.now()
        order = self.paid_order(PLAN_LEVEL_THREE)

        renewed = activate_subscription_from_payment(order)

        self.assertGreaterEqual(renewed.starts_at, activation_floor)
        self.assertEqual(renewed.expires_at, renewed.starts_at + timedelta(days=30))
        self.assertEqual(UserSubscription.objects.filter(user=self.user, plan_code=PLAN_LEVEL_THREE).count(), 1)

    def test_18_diamond_activation_cancels_redundant_active_addons(self):
        addon = grant_active_subscription(self.user, PLAN_LEVEL_FOUR)
        order = self.paid_order(PLAN_DIAMOND)

        activate_subscription_from_payment(order)

        addon.refresh_from_db()
        self.assertEqual(addon.status, UserSubscription.Status.CANCELED)

    def test_19_profile_summary_reports_riyadh_dates_and_expired_status(self):
        expired = self.expire_plan(PLAN_SILVER)

        summary = subscription_dashboard_context(self.user)

        self.assertEqual(summary["status"], "expired")
        self.assertEqual(summary["remaining_days"], 0)
        self.assertEqual(summary["remaining_hours"], 0)
        self.assertEqual(summary["renew_plan_code"], PLAN_SILVER)
        self.assertEqual(summary["starts_at_riyadh"].tzinfo.key, "Asia/Riyadh")
        self.assertEqual(
            summary["expires_at_riyadh"].date(),
            timezone.localtime(expired.expires_at, ZoneInfo("Asia/Riyadh")).date(),
        )

    def test_20_pricing_options_expose_renew_upgrade_disabled_and_included_states(self):
        grant_active_subscription(self.user, PLAN_DIAMOND)

        options = purchase_options_for_user(self.user)
        summary = subscription_dashboard_context(self.user)

        self.assertFalse(options[PLAN_DIAMOND]["allowed"])
        self.assertEqual(options[PLAN_DIAMOND]["state"], "active_subscription")
        self.assertEqual(options[PLAN_DIAMOND]["label"], "مشترك حاليًا")
        self.assertEqual(options[PLAN_BASIC]["state"], "lower_main_plan")
        self.assertEqual(options[PLAN_LEVEL_THREE]["state"], "included_in_diamond")
        self.assertEqual(options[PLAN_LEVEL_FOUR]["state"], "included_in_diamond")
        self.assertEqual(summary["renew_plan_code"], "")

    def test_21_manual_post_cannot_bypass_lower_plan_policy(self):
        grant_active_subscription(self.user, PLAN_VIP)
        self.client.force_login(self.user)

        response = self.client.post("/checkout/silver/create/bank_transfer/", {"amount_sar": "0.01"})

        self.assertEqual(response.status_code, 403)
        self.assertFalse(PaymentOrder.objects.filter(user=self.user).exists())

    def test_22_only_the_real_reuse_setting_name_is_used(self):
        project_root = Path(__file__).resolve().parents[2]
        settings_source = (project_root / "abcz" / "settings.py").read_text(encoding="utf-8")
        views_source = (project_root / "phonics" / "views.py").read_text(encoding="utf-8")

        self.assertIn("MOYASAR_ORDER_REUSE_MINUTES", settings_source)
        self.assertIn("MOYASAR_ORDER_REUSE_MINUTES", views_source)
        self.assertNotIn("MOYASAR_INVOICE_REUSE_MINUTES", settings_source)
        self.assertNotIn("MOYASAR_INVOICE_REUSE_MINUTES", views_source)

    @override_settings(
        MOYASAR_ENABLED=True,
        MOYASAR_SECRET_KEY="sk_test_isolated_only",
        MOYASAR_ENVIRONMENT="test",
        MOYASAR_CHECKOUT_ALLOWED_HOSTS=["checkout.moyasar.com"],
    )
    @patch("phonics.views.create_moyasar_invoice")
    def test_23_every_plan_reaches_mocked_moyasar_checkout_without_integrity_error(self, invoice_mock):
        counter = iter(range(1, 7))
        expected_amounts = {
            PLAN_BASIC: (Decimal("19.00"), 1900),
            PLAN_SILVER: (Decimal("27.00"), 2700),
            PLAN_VIP: (Decimal("39.00"), 3900),
            PLAN_DIAMOND: (Decimal("50.00"), 5000),
            PLAN_LEVEL_THREE: (Decimal("15.00"), 1500),
            PLAN_LEVEL_FOUR: (Decimal("15.00"), 1500),
        }

        def invoice_result(**kwargs):
            number = next(counter)
            return MoyasarInvoice(
                invoice_id=f"inv_plan_matrix_{number}",
                checkout_url=f"https://checkout.moyasar.com/invoices/inv_plan_matrix_{number}",
                amount_halalas=kwargs["amount_halalas"],
                currency=kwargs["currency"],
                status="initiated",
            )

        invoice_mock.side_effect = invoice_result
        self.client.force_login(self.user)

        for index, plan_code in enumerate(
            (PLAN_BASIC, PLAN_SILVER, PLAN_VIP, PLAN_DIAMOND, PLAN_LEVEL_THREE, PLAN_LEVEL_FOUR),
            start=1,
        ):
            with self.subTest(plan_code=plan_code):
                checkout = self.client.get(f"/checkout/{plan_code}/")
                self.assertEqual(checkout.status_code, 200)
                response = self.client.post(
                    f"/checkout/{plan_code}/create/moyasar/",
                    REMOTE_ADDR=f"198.51.100.{index}",
                )
                self.assertEqual(response.status_code, 302)
                order = PaymentOrder.objects.get(user=self.user, plan_code=plan_code)
                self.assertEqual(order.from_plan_code, "")
                self.assertEqual(order.to_plan_code, plan_code)
                self.assertEqual(order.status, PaymentOrder.Status.INITIATED)
                self.assertEqual(order.amount_sar, expected_amounts[plan_code][0])
                self.assertEqual(order.amount_halalas, expected_amounts[plan_code][1])

        self.assertEqual(invoice_mock.call_count, 6)

    def test_24_active_diamond_blocks_same_lower_and_addon_orders(self):
        grant_active_subscription(self.user, PLAN_DIAMOND)
        self.client.force_login(self.user)

        pricing = self.client.get("/pricing/")
        self.assertEqual(pricing.status_code, 200)
        self.assertFalse(pricing.context["diamond_action"]["allowed"])
        self.assertEqual(pricing.context["diamond_action"]["state"], "active_subscription")
        self.assertEqual(pricing.context["diamond_action"]["label"], "مشترك حاليًا")

        for index, plan_code in enumerate(
            (PLAN_BASIC, PLAN_SILVER, PLAN_VIP, PLAN_DIAMOND, PLAN_LEVEL_THREE, PLAN_LEVEL_FOUR),
            start=20,
        ):
            with self.subTest(plan_code=plan_code):
                checkout = self.client.get(f"/checkout/{plan_code}/")
                self.assertEqual(checkout.status_code, 200)
                self.assertFalse(checkout.context["purchase_option"]["allowed"])
                response = self.client.post(
                    f"/checkout/{plan_code}/create/moyasar/",
                    REMOTE_ADDR=f"198.51.100.{index}",
                )
                self.assertEqual(response.status_code, 403)

        self.assertFalse(PaymentOrder.objects.filter(user=self.user).exists())

    def test_25_all_upgrade_amounts_and_snapshots_are_server_computed(self):
        cases = (
            (PLAN_BASIC, PLAN_SILVER, "8.00"),
            (PLAN_BASIC, PLAN_VIP, "20.00"),
            (PLAN_BASIC, PLAN_DIAMOND, "31.00"),
            (PLAN_SILVER, PLAN_VIP, "12.00"),
            (PLAN_SILVER, PLAN_DIAMOND, "23.00"),
            (PLAN_VIP, PLAN_DIAMOND, "11.00"),
        )
        for index, (source_code, target_code, expected_due) in enumerate(cases, start=1):
            with self.subTest(source=source_code, target=target_code):
                user = User.objects.create_user(username=f"upgrade-matrix-{index}")
                source = grant_active_subscription(user, source_code)
                order = create_payment_order_for_plan(
                    user,
                    CHECKOUT_PLANS[target_code],
                    "moyasar",
                )
                self.assertEqual(order.operation_type, PaymentOrder.OperationType.UPGRADE)
                self.assertEqual(order.from_plan_code, source_code)
                self.assertEqual(order.to_plan_code, target_code)
                self.assertEqual(order.original_price, CHECKOUT_PLANS[source_code]["price_sar"])
                self.assertEqual(order.target_price, CHECKOUT_PLANS[target_code]["price_sar"])
                self.assertEqual(order.amount_due, Decimal(expected_due))
                self.assertEqual(order.amount_sar, Decimal(expected_due))
                self.assertEqual(order.current_expires_at, source.expires_at)

    def test_26_expiry_boundary_blocks_access_and_enables_renewal(self):
        expires_at = timezone.now().replace(microsecond=0) + timedelta(days=1)
        subscription = grant_active_subscription(
            self.user,
            PLAN_BASIC,
            starts_at=expires_at - timedelta(days=30),
            expires_at=expires_at,
        )
        profile = self.user.student_profile
        profile.is_premium = True
        profile.save(update_fields=["is_premium", "updated_at"])

        before = get_user_entitlements(self.user, now=expires_at - timedelta(minutes=1))
        at_expiry = get_user_entitlements(self.user, now=expires_at)
        summary = subscription_dashboard_context(self.user, now=expires_at)
        quote = quote_plan_purchase(self.user, PLAN_BASIC, now=expires_at)

        self.assertIn("letters_full", before.entitlements)
        self.assertNotIn("letters_full", at_expiry.entitlements)
        self.assertIsNone(at_expiry.main_subscription)
        self.assertEqual(summary["status"], "expired")
        self.assertEqual(summary["renew_plan_code"], PLAN_BASIC)
        self.assertEqual(quote.operation_type, PaymentOrder.OperationType.RENEWAL)
        profile.refresh_from_db()
        self.assertFalse(profile.is_premium)
        self.assertEqual(subscription.pk, UserSubscription.objects.get(user=self.user, plan_code=PLAN_BASIC).pk)

    def test_27_profile_hides_provider_details_and_renewal_until_expiry(self):
        subscription = grant_active_subscription(self.user, PLAN_BASIC)
        order = PaymentOrder.objects.create(
            user=self.user,
            plan_code=PLAN_BASIC,
            plan_name="Basic",
            duration_days=30,
            amount_halalas=1900,
            amount_sar=Decimal("19.00"),
            currency="SAR",
            status=PaymentOrder.Status.PAID,
            method=PaymentOrder.Method.MOYASAR_CARD,
            provider=PaymentOrder.Provider.MOYASAR,
            payment_environment=PaymentOrder.Environment.TEST,
            moyasar_invoice_id="inv_private_profile_marker",
            moyasar_payment_id="pay_private_profile_marker",
            metadata={"private_marker": "metadata_private_profile_marker"},
        )
        self.client.force_login(self.user)

        active_response = self.client.get("/profile/")
        active_html = active_response.content.decode("utf-8")

        self.assertEqual(active_response.status_code, 200)
        self.assertContains(active_response, "مشترك حاليًا")
        self.assertNotIn(">تجديد</a>", active_html)
        self.assertNotIn(order.moyasar_invoice_id, active_html)
        self.assertNotIn(order.moyasar_payment_id, active_html)
        self.assertNotIn("metadata_private_profile_marker", active_html)

        subscription.expires_at = timezone.now() - timedelta(minutes=1)
        subscription.save(update_fields=["expires_at", "updated_at"])
        expired_response = self.client.get("/profile/")
        expired_html = expired_response.content.decode("utf-8")

        self.assertEqual(expired_response.status_code, 200)
        self.assertContains(expired_response, "الاشتراك منتهي")
        self.assertIn(">تجديد</a>", expired_html)
