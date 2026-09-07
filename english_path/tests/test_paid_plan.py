import json
from datetime import timedelta
from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from english_path.models import ReviewItem, UnitProgress
from english_path.services.access import ENTITLEMENT, has_journey_access, has_journey_subscription, journey_plan
from english_path.services.daily_mission import build_daily_mission
from phonics.models import PaymentOrder, UserSubscription, activate_subscription_from_payment
from phonics.payments.moyasar import MoyasarInvoice
from phonics.plans import PLAN_ENGLISH_JOURNEY
from phonics.subscriptions import get_user_entitlements, quote_plan_purchase
from phonics.tests.subscription_helpers import grant_active_subscription


class HiddenJourneyCheckoutTests(TestCase):
    def test_checkout_is_not_public_while_feature_flag_is_false(self):
        user = get_user_model().objects.create_user(username="hidden-plan", password="safe-test-password")
        self.client.force_login(user)
        with override_settings(ENGLISH_PATH_ENABLED=False):
            self.assertEqual(self.client.get(reverse("checkout", args=(PLAN_ENGLISH_JOURNEY,))).status_code, 404)
            self.assertEqual(self.client.post(reverse("create_payment_order", args=(PLAN_ENGLISH_JOURNEY, "moyasar"))).status_code, 404)


@override_settings(ENGLISH_PATH_ENABLED=True, DISABLE_AUTO_SEED=True, SECURE_SSL_REDIRECT=False, RATE_LIMIT_PAYMENT=1000)
class EnglishJourneyPlanTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="journey-buyer", password="safe-test-password")
        self.client.force_login(self.user)

    def test_plan_is_single_server_priced_addon(self):
        plan = journey_plan()
        quote = quote_plan_purchase(self.user, PLAN_ENGLISH_JOURNEY)
        self.assertEqual(plan["code"], "english_journey")
        self.assertEqual(plan["price_sar"], Decimal("39.00"))
        self.assertEqual(quote.amount_due, Decimal("39.00"))
        self.assertEqual(quote.operation_type, PaymentOrder.OperationType.PURCHASE)
        with self.settings(BACK_TO_SCHOOL_ENABLED=True, BACK_TO_SCHOOL_DISCOUNT_PERCENT=90):
            self.assertEqual(quote_plan_purchase(self.user, PLAN_ENGLISH_JOURNEY).amount_due, Decimal("39.00"))
            checkout = self.client.get(reverse("checkout", args=(PLAN_ENGLISH_JOURNEY,)))
            self.assertEqual(checkout.context["campaign"]["final_price"], Decimal("39.00"))
            self.assertFalse(checkout.context["campaign"]["campaign_active"])

    def test_a1_1_is_free_but_a1_2_and_its_api_require_subscription(self):
        self.assertEqual(self.client.get(reverse("english_path:unit", args=("a1-1",))).status_code, 200)
        self.assertRedirects(self.client.get(reverse("english_path:unit", args=("a1-2",))), reverse("english_path:level", args=("a1",)))
        response = self.client.post(reverse("english_path:submit_unit_quiz", args=("a1-2",)), data=json.dumps({"answers": {}}), content_type="application/json")
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["error"], "english_journey_subscription_required")

    def test_developer_preview_group_bypasses_subscription_but_not_mastery(self):
        developer = get_user_model().objects.create_user(
            username="journey-developer",
            email="preview-user@example.com",
            password="safe-test-password",
        )
        preview_group = Group.objects.create(name="English Journey Preview")
        developer.groups.add(preview_group)
        self.client.force_login(developer)

        self.assertTrue(has_journey_access(developer))
        self.assertFalse(has_journey_subscription(developer))
        self.assertFalse(UserSubscription.objects.filter(user=developer).exists())
        self.assertNotIn(ENTITLEMENT, get_user_entitlements(developer, synchronize=False).entitlements)
        self.assertNotIn("word_games", get_user_entitlements(developer, synchronize=False).entitlements)
        overview = self.client.get(reverse("english_path:overview"))
        self.assertTrue(overview.context["preview_access"])
        self.assertTrue(overview.context["journey_access"])
        self.assertFalse(overview.context["journey_subscribed"])
        self.assertRedirects(
            self.client.get(reverse("english_path:unit", args=("a1-2",))),
            reverse("english_path:level", args=("a1",)),
        )

        UnitProgress.objects.create(user=developer, unit_code="A1.1", score=80, status="mastered")
        self.assertEqual(self.client.get(reverse("english_path:unit", args=("a1-2",))).status_code, 200)

        developer.groups.remove(preview_group)
        self.assertFalse(has_journey_access(developer))
        self.assertRedirects(
            self.client.get(reverse("english_path:unit", args=("a1-2",))),
            reverse("english_path:level", args=("a1",)),
        )

    def test_normal_user_cannot_enable_preview_through_request_or_url(self):
        self.assertFalse(has_journey_subscription(self.user))
        response = self.client.get(
            reverse("english_path:unit", args=("a1-2",)),
            {"preview_access": "true", "group": "English Journey Preview"},
        )
        self.assertRedirects(response, reverse("english_path:level", args=("a1",)))
        response = self.client.post(
            reverse("english_path:submit_unit_quiz", args=("a1-2",)),
            data=json.dumps({"answers": {}, "preview_access": True, "group": "English Journey Preview"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["error"], "english_journey_subscription_required")
        self.assertFalse(self.user.groups.exists())

    def test_preview_group_does_not_bypass_feature_flag(self):
        preview_user = get_user_model().objects.create_user(username="flag-preview", password="safe-test-password")
        preview_user.groups.create(name="English Journey Preview")
        self.client.force_login(preview_user)
        with override_settings(ENGLISH_PATH_ENABLED=False):
            self.assertEqual(self.client.get(reverse("english_path:overview")).status_code, 404)

    def test_subscription_and_mastery_are_independent_locks(self):
        grant_active_subscription(self.user, PLAN_ENGLISH_JOURNEY)
        self.assertRedirects(self.client.get(reverse("english_path:unit", args=("a1-2",))), reverse("english_path:level", args=("a1",)))
        UnitProgress.objects.create(user=self.user, unit_code="A1.1", score=80, status="mastered")
        self.assertEqual(self.client.get(reverse("english_path:unit", args=("a1-2",))).status_code, 200)

    def test_unrelated_paid_plan_does_not_grant_journey_or_phonics_leaks(self):
        grant_active_subscription(self.user, "vip")
        self.assertFalse(has_journey_subscription(self.user))
        self.assertNotIn(ENTITLEMENT, get_user_entitlements(self.user, synchronize=False).entitlements)
        other = get_user_model().objects.create_user(username="journey-only", password="safe-test-password")
        grant_active_subscription(other, PLAN_ENGLISH_JOURNEY)
        self.assertNotIn("word_games", get_user_entitlements(other, synchronize=False).entitlements)
        diamond_user = get_user_model().objects.create_user(username="diamond-and-journey", password="safe-test-password")
        grant_active_subscription(diamond_user, "diamond")
        self.assertEqual(quote_plan_purchase(diamond_user, PLAN_ENGLISH_JOURNEY).amount_due, Decimal("39.00"))

    def test_expired_subscription_revokes_paid_content(self):
        subscription = grant_active_subscription(self.user, PLAN_ENGLISH_JOURNEY)
        subscription.expires_at = timezone.now() - timedelta(seconds=1)
        subscription.save(update_fields=("expires_at", "updated_at"))
        self.assertFalse(has_journey_subscription(self.user))
        self.assertRedirects(self.client.get(reverse("english_path:unit", args=("a2-1",))), reverse("english_path:level", args=("a2",)))

    def test_daily_mission_and_mistakes_only_use_owned_content(self):
        UnitProgress.objects.create(user=self.user, unit_code="A1.1", score=100, status="excellent")
        free = ReviewItem.objects.create(user=self.user, unit_code="A1.1", item_key="free-review", prompt="FREE PROMPT", answer="A", skill="grammar", next_review_at=timezone.now())
        ReviewItem.objects.create(user=self.user, unit_code="A1.2", item_key="paid-review", prompt="PAID PROMPT", answer="B", skill="grammar", next_review_at=timezone.now())
        mission = build_daily_mission(self.user)
        self.assertEqual(mission["review_item_ids"], [free.id])
        self.assertTrue(mission["subscription_required"])
        self.assertIsNone(mission["current_unit"])
        response = self.client.get(reverse("english_path:review"))
        self.assertContains(response, "FREE PROMPT")
        self.assertNotContains(response, "PAID PROMPT")

    def test_final_challenges_require_both_subscription_and_mastery(self):
        for order in range(1, 21):
            UnitProgress.objects.create(user=self.user, unit_code=f"A1.{order}", score=100, status="excellent")
        self.assertRedirects(self.client.get(reverse("english_path:a1_final")), reverse("english_path:level", args=("a1",)))
        response = self.client.post(reverse("english_path:submit_a1_final"), data={})
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["error"], "english_journey_subscription_required")

    @override_settings(
        MOYASAR_ENABLED=True,
        MOYASAR_SECRET_KEY="sk_test_journey_only",
        MOYASAR_ENVIRONMENT="test",
        MOYASAR_CHECKOUT_ALLOWED_HOSTS=["checkout.moyasar.com"],
    )
    @patch("phonics.views.create_moyasar_invoice")
    def test_existing_checkout_creates_39_sar_order_and_activation(self, invoice_mock):
        invoice_mock.return_value = MoyasarInvoice(
            invoice_id="inv_english_journey",
            checkout_url="https://checkout.moyasar.com/invoices/inv_english_journey",
            amount_halalas=3900,
            currency="SAR",
            status="initiated",
        )
        response = self.client.post(
            reverse("create_payment_order", args=(PLAN_ENGLISH_JOURNEY, "moyasar")),
            {"amount_sar": "0.01", "price": "1"},
        )
        self.assertRedirects(response, "https://checkout.moyasar.com/invoices/inv_english_journey", fetch_redirect_response=False)
        order = PaymentOrder.objects.get(user=self.user, plan_code=PLAN_ENGLISH_JOURNEY)
        self.assertEqual((order.amount_sar, order.amount_halalas, order.currency), (Decimal("39.00"), 3900, "SAR"))
        self.assertEqual(invoice_mock.call_args.kwargs["amount_halalas"], 3900)
        order.status = PaymentOrder.Status.PAID
        order.paid_at = timezone.now()
        order.save(update_fields=("status", "paid_at", "updated_at"))
        subscription = activate_subscription_from_payment(order)
        self.assertEqual(subscription.plan_code, PLAN_ENGLISH_JOURNEY)
        self.assertTrue(has_journey_subscription(self.user))
