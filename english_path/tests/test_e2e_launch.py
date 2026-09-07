import json
from datetime import timedelta
from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.db import connection
from django.test import TestCase, override_settings
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from django.utils import timezone

from english_path.models import AssessmentResult, ReviewItem, ReviewSession, UnitProgress
from english_path.services.access import has_journey_subscription
from english_path.services.daily_mission import build_daily_mission
from english_path.services.units import get_unit_content
from phonics.models import PaymentOrder, UserSubscription, activate_subscription_from_payment
from phonics.payments.moyasar import MoyasarInvoice
from phonics.payments.reconciliation import reconcile_payment_order
from phonics.plans import PLAN_ENGLISH_JOURNEY
from phonics.subscriptions import quote_plan_purchase
from phonics.tests.subscription_helpers import grant_active_subscription
from phonics.views import CHECKOUT_PLANS, create_payment_order_for_plan


SKILLS = ("vocabulary", "grammar", "reading", "listening", "speaking", "writing")


@override_settings(
    ENGLISH_PATH_ENABLED=True,
    DISABLE_AUTO_SEED=True,
    SECURE_SSL_REDIRECT=False,
    RATE_LIMIT_PAYMENT=1000,
    RATE_LIMIT_WRITE=1000,
    RATE_LIMIT_REGISTER=100,
    MOYASAR_ENVIRONMENT="test",
)
class EnglishJourneyLaunchE2ETests(TestCase):
    def create_user(self, username):
        return get_user_model().objects.create_user(
            username=username,
            email=f"{username}@example.com",
            password="StrongPass123!",
        )

    def master_units(self, user, level, through=10):
        for number in range(1, through + 1):
            UnitProgress.objects.update_or_create(
                user=user,
                unit_code=f"{level}.{number}",
                defaults={"score": 100, "status": UnitProgress.Status.EXCELLENT},
            )

    def make_order(self, user, suffix="1", method="moyasar"):
        order = create_payment_order_for_plan(
            user,
            CHECKOUT_PLANS[PLAN_ENGLISH_JOURNEY],
            method,
        )
        if method == "moyasar":
            order.moyasar_invoice_id = f"inv_journey_{suffix}"
            order.status = PaymentOrder.Status.INITIATED
            order.save(update_fields=("moyasar_invoice_id", "status", "updated_at"))
        return order

    def invoice_for(self, order, *, status="paid", amount=3900, currency="SAR", payment_id=None):
        invoice = {
            "id": order.moyasar_invoice_id,
            "status": status,
            "amount": amount,
            "currency": currency,
            "live": False,
            "metadata": {
                "payment_order_id": str(order.id),
                "user_id": str(order.user_id),
                "plan_code": PLAN_ENGLISH_JOURNEY,
                "operation_type": order.operation_type,
                "quote_reference": str(order.idempotency_key),
            },
            "payments": [],
        }
        if status == "paid":
            invoice["payments"] = [{
                "id": payment_id or f"pay_{order.id}",
                "status": "paid",
                "invoice_id": order.moyasar_invoice_id,
                "amount": amount,
                "currency": currency,
                "live": False,
            }]
        return invoice

    def test_new_user_free_unit_paywall_checkout_verified_payment_and_progression(self):
        registration = self.client.post(reverse("register"), {
            "username": "new-journey-user",
            "email": "new-journey@example.com",
            "student_name": "New Learner",
            "parent_phone": "0501234567",
            "city": "Riyadh",
            "password1": "StrongPass123!",
            "password2": "StrongPass123!",
        })
        self.assertRedirects(registration, reverse("letters"))
        user = get_user_model().objects.get(username="new-journey-user")

        self.assertEqual(self.client.get(reverse("english_path:overview")).status_code, 200)
        self.assertEqual(self.client.get(reverse("english_path:unit", args=("a1-1",))).status_code, 200)
        content = get_unit_content("a1-1")
        answers = {question["id"]: question["answer"] for question in content["quiz"]}
        graded = self.client.post(
            reverse("english_path:submit_unit_quiz", args=("a1-1",)),
            data=json.dumps({
                "answers": answers,
                "score": 0,
                "user_id": 999999,
                "subscription_id": 999999,
                "unit_code": "A2.10",
            }),
            content_type="application/json",
        )
        self.assertEqual(graded.status_code, 200)
        self.assertGreaterEqual(graded.json()["score"], 80)
        self.assertEqual(UnitProgress.objects.get(user=user, unit_code="A1.1").score, 100)
        self.assertFalse(UnitProgress.objects.filter(user=user).exclude(unit_code="A1.1").exists())

        paid_content = get_unit_content("a1-2")
        secret_answer = paid_content["quiz"][0]["answer"]
        locked = self.client.get(reverse("english_path:unit", args=("a1-2",)), follow=True)
        self.assertRedirects(locked, reverse("english_path:level", args=("a1",)))
        self.assertNotContains(locked, paid_content["reading"]["passage"])
        self.assertNotContains(locked, secret_answer)
        self.assertContains(locked, "English Journey A1")
        self.assertContains(locked, "39")
        blocked_api = self.client.post(
            reverse("english_path:submit_unit_quiz", args=("a1-2",)),
            data=json.dumps({"answers": {}}),
            content_type="application/json",
        )
        self.assertEqual(blocked_api.status_code, 403)

        with override_settings(
            MOYASAR_ENABLED=True,
            MOYASAR_SECRET_KEY="sk_test_launch",
            MOYASAR_CHECKOUT_ALLOWED_HOSTS=["checkout.moyasar.com"],
        ), patch("phonics.views.create_moyasar_invoice") as invoice_mock:
            invoice_mock.return_value = MoyasarInvoice(
                invoice_id="inv_journey_e2e",
                checkout_url="https://checkout.moyasar.com/invoices/inv_journey_e2e",
                amount_halalas=3900,
                currency="SAR",
                status="initiated",
            )
            checkout = self.client.post(
                reverse("create_payment_order", args=(PLAN_ENGLISH_JOURNEY, "moyasar")),
                {
                    "price": "0.01",
                    "amount": "1",
                    "amount_sar": "0.01",
                    "plan": "vip",
                    "duration": "999",
                    "entitlement": "word_games",
                    "user_id": "999999",
                },
            )
        self.assertRedirects(
            checkout,
            "https://checkout.moyasar.com/invoices/inv_journey_e2e",
            fetch_redirect_response=False,
        )
        order = PaymentOrder.objects.get(user=user)
        self.assertEqual(order.plan_code, PLAN_ENGLISH_JOURNEY)
        self.assertEqual(order.to_plan_code, PLAN_ENGLISH_JOURNEY)
        self.assertEqual(order.amount_sar, Decimal("39.00"))
        self.assertEqual(order.amount_halalas, 3900)
        self.assertEqual(order.currency, "SAR")
        self.assertEqual(order.duration_days, 30)
        self.assertEqual(order.metadata["user_id"], user.id)
        self.assertEqual(order.metadata["plan_code"], PLAN_ENGLISH_JOURNEY)
        self.assertFalse(has_journey_subscription(user))

        trusted_invoice = self.invoice_for(order, payment_id="pay_journey_e2e")
        with patch("phonics.payments.reconciliation.fetch_invoice", return_value=trusted_invoice):
            first = reconcile_payment_order(order.id)
            first_expiry = UserSubscription.objects.get(user=user, plan_code=PLAN_ENGLISH_JOURNEY).expires_at
            second = reconcile_payment_order(order.id)
        self.assertEqual((first.status, second.status), ("paid", "paid"))
        self.assertEqual(second.code, "already_paid")
        self.assertEqual(UserSubscription.objects.filter(user=user, plan_code=PLAN_ENGLISH_JOURNEY).count(), 1)
        self.assertEqual(UserSubscription.objects.get(user=user, plan_code=PLAN_ENGLISH_JOURNEY).expires_at, first_expiry)
        self.assertEqual(self.client.get(reverse("english_path:unit", args=("a1-2",))).status_code, 200)
        self.assertRedirects(
            self.client.get(reverse("english_path:unit", args=("a1-3",))),
            reverse("english_path:level", args=("a1",)),
        )

    def test_callback_query_cannot_claim_success_without_server_verification(self):
        user = self.create_user("callback-attacker")
        self.client.force_login(user)
        order = self.make_order(user, "callback")
        pending_invoice = self.invoice_for(order, status="initiated")
        with patch("phonics.payments.reconciliation.fetch_invoice", return_value=pending_invoice):
            response = self.client.get(
                reverse("moyasar_callback"),
                {
                    "order": order.id,
                    "status": "paid",
                    "amount": "3900",
                    "plan": PLAN_ENGLISH_JOURNEY,
                    "payment_order_id": order.id,
                },
            )
        self.assertRedirects(
            response,
            f"{reverse('payment_pending')}?order={order.id}",
            fetch_redirect_response=False,
        )
        self.assertFalse(has_journey_subscription(user))

    def test_nonpaid_and_mismatched_provider_results_never_activate(self):
        user = self.create_user("provider-statuses")
        for index, status in enumerate(("initiated", "failed", "canceled"), start=1):
            order = self.make_order(user, f"status_{index}")
            with patch(
                "phonics.payments.reconciliation.fetch_invoice",
                return_value=self.invoice_for(order, status=status),
            ):
                reconcile_payment_order(order.id)
            self.assertFalse(has_journey_subscription(user))

        wrong_amount = self.make_order(user, "wrong_amount")
        with patch(
            "phonics.payments.reconciliation.fetch_invoice",
            return_value=self.invoice_for(wrong_amount, amount=1),
        ):
            result = reconcile_payment_order(wrong_amount.id)
        self.assertEqual((result.status, result.code), ("mismatch", "invoice_amount_mismatch"))

        wrong_currency = self.make_order(user, "wrong_currency")
        with patch(
            "phonics.payments.reconciliation.fetch_invoice",
            return_value=self.invoice_for(wrong_currency, currency="USD"),
        ):
            result = reconcile_payment_order(wrong_currency.id)
        self.assertEqual((result.status, result.code), ("mismatch", "invoice_currency_mismatch"))
        self.assertFalse(has_journey_subscription(user))

    def test_cross_user_objects_and_results_are_enforced_server_side(self):
        owner = self.create_user("journey-owner")
        attacker = self.create_user("journey-attacker")
        order = self.make_order(owner, "owner", method="bank_transfer")
        grant_active_subscription(owner, PLAN_ENGLISH_JOURNEY)
        self.master_units(owner, "A1")
        AssessmentResult.objects.create(
            user=owner,
            assessment_type="a1_final",
            level="A1 Master",
            score=100,
            skill_scores={skill: 100 for skill in SKILLS},
        )
        self.master_units(owner, "A2")
        AssessmentResult.objects.create(
            user=owner,
            assessment_type="a2_final",
            level="A2 Master",
            score=100,
            skill_scores={skill: 100 for skill in SKILLS},
        )
        review_item = ReviewItem.objects.create(
            user=owner,
            unit_code="A1.2",
            item_key="owner-only-review",
            prompt="OWNER PRIVATE PROMPT",
            answer="private",
            skill="grammar",
            next_review_at=timezone.now(),
        )
        review_session = ReviewSession.objects.create(user=owner, item_ids=[review_item.id])
        self.client.force_login(attacker)
        for status_url in ("payment_success", "payment_pending", "payment_failed"):
            self.assertEqual(self.client.get(reverse(status_url), {"order": order.id}).status_code, 404)
        self.assertEqual(self.client.get(reverse("bank_transfer_proof", args=(order.id,))).status_code, 404)
        self.assertEqual(
            self.client.get(reverse("english_path:review"), {"session": review_session.id}).status_code,
            404,
        )
        self.assertEqual(
            self.client.post(
                reverse("english_path:review_answer", args=(review_item.id,)),
                data=json.dumps({"correct": True}),
                content_type="application/json",
            ).status_code,
            404,
        )
        self.assertRedirects(
            self.client.get(reverse("english_path:unit", args=("a1-2",))),
            reverse("english_path:level", args=("a1",)),
        )
        self.assertFalse(UnitProgress.objects.filter(user=attacker).exists())
        self.assertRedirects(
            self.client.get(reverse("english_path:journey_completion")),
            reverse("english_path:level", args=("a2",)),
        )

    def test_expiry_hides_paid_reviews_and_report_then_renewal_restores_progress(self):
        user = self.create_user("expiry-learner")
        subscription = grant_active_subscription(user, PLAN_ENGLISH_JOURNEY)
        self.master_units(user, "A1")
        AssessmentResult.objects.create(
            user=user,
            assessment_type="a1_final",
            level="A1 Master",
            score=100,
            skill_scores={skill: 100 for skill in SKILLS},
        )
        self.master_units(user, "A2")
        AssessmentResult.objects.create(
            user=user,
            assessment_type="a2_final",
            level="A2 Master",
            score=100,
            skill_scores={skill: 100 for skill in SKILLS},
        )
        paid_review = ReviewItem.objects.create(
            user=user,
            unit_code="A1.2",
            item_key="expired-paid-review",
            prompt="EXPIRED PAID PROMPT",
            answer="answer",
            skill="grammar",
            next_review_at=timezone.now(),
        )
        saved_progress_ids = list(UnitProgress.objects.filter(user=user).values_list("id", flat=True))
        subscription.expires_at = timezone.now() - timedelta(seconds=1)
        subscription.save(update_fields=("expires_at", "updated_at"))
        self.client.force_login(user)

        self.assertEqual(self.client.get(reverse("english_path:unit", args=("a1-1",))).status_code, 200)
        self.assertRedirects(
            self.client.get(reverse("english_path:unit", args=("a1-2",))),
            reverse("english_path:level", args=("a1",)),
        )
        self.assertNotContains(self.client.get(reverse("english_path:review")), "EXPIRED PAID PROMPT")
        expired_mission = build_daily_mission(user)
        self.assertIsNone(expired_mission["current_unit"])
        self.assertNotIn(paid_review.id, expired_mission["review_item_ids"])
        blocked_review = self.client.post(
            reverse("english_path:review_answer", args=(paid_review.id,)),
            data=json.dumps({"correct": True}),
            content_type="application/json",
        )
        self.assertEqual(blocked_review.status_code, 403)
        self.assertRedirects(
            self.client.get(reverse("english_path:journey_completion")),
            reverse("english_path:level", args=("a2",)),
        )
        self.assertEqual(list(UnitProgress.objects.filter(user=user).values_list("id", flat=True)), saved_progress_ids)
        self.assertEqual(quote_plan_purchase(user, PLAN_ENGLISH_JOURNEY).operation_type, PaymentOrder.OperationType.RENEWAL)

        renewal_order = self.make_order(user, "renewal")
        self.assertEqual(renewal_order.operation_type, PaymentOrder.OperationType.RENEWAL)
        with patch(
            "phonics.payments.reconciliation.fetch_invoice",
            return_value=self.invoice_for(renewal_order, payment_id="pay_journey_renewal"),
        ):
            self.assertEqual(reconcile_payment_order(renewal_order.id).status, "paid")
        self.assertEqual(self.client.get(reverse("english_path:unit", args=("a1-2",))).status_code, 200)
        self.assertContains(self.client.get(reverse("english_path:review")), "EXPIRED PAID PROMPT")
        self.assertEqual(self.client.get(reverse("english_path:journey_completion")).status_code, 200)
        self.assertEqual(list(UnitProgress.objects.filter(user=user).values_list("id", flat=True)), saved_progress_ids)

    def test_dual_lock_matrix_and_a1_to_a2_objective_threshold(self):
        cases = (
            ("none", False, False, False),
            ("mastery-only", False, True, False),
            ("subscription-only", True, False, False),
            ("both", True, True, True),
        )
        for username, subscribed, mastered, allowed in cases:
            user = self.create_user(username)
            if subscribed:
                grant_active_subscription(user, PLAN_ENGLISH_JOURNEY)
            if mastered:
                UnitProgress.objects.create(user=user, unit_code="A1.1", score=80, status="mastered")
            self.client.force_login(user)
            response = self.client.get(reverse("english_path:unit", args=("a1-2",)))
            self.assertEqual(response.status_code, 200 if allowed else 302)
            level = self.client.get(reverse("english_path:level", args=("a1",)))
            a1_2 = next(unit for unit in level.context["units"] if unit["code"] == "A1.2")
            self.assertEqual(a1_2["subscription_locked"], not subscribed)
            self.assertEqual(a1_2["locked"], not mastered)

        user = self.create_user("a1-threshold")
        grant_active_subscription(user, PLAN_ENGLISH_JOURNEY)
        self.master_units(user, "A1")
        self.client.force_login(user)
        weak_result = AssessmentResult.objects.create(
            user=user,
            assessment_type="a1_final",
            level="A1 Developing",
            score=90,
            skill_scores={**{skill: 90 for skill in SKILLS}, "listening": 59},
        )
        self.assertRedirects(
            self.client.get(reverse("english_path:unit", args=("a2-1",))),
            reverse("english_path:level", args=("a2",)),
        )
        weak_result.delete()
        AssessmentResult.objects.create(
            user=user,
            assessment_type="a1_final",
            level="A1 Master",
            score=80,
            skill_scores={skill: 60 for skill in SKILLS},
        )
        self.assertEqual(self.client.get(reverse("english_path:unit", args=("a2-1",))).status_code, 200)
        self.assertRedirects(
            self.client.get(reverse("english_path:unit", args=("a2-2",))),
            reverse("english_path:level", args=("a2",)),
        )

    def test_direct_url_policy_for_anonymous_free_paid_unmastered_and_expired_users(self):
        protected_gets = (
            reverse("english_path:unit", args=("a1-2",)),
            reverse("english_path:unit", args=("a1-10",)),
            reverse("english_path:a1_final"),
            reverse("english_path:unit", args=("a2-1",)),
            reverse("english_path:unit", args=("a2-10",)),
            reverse("english_path:a2_final"),
            reverse("english_path:journey_completion"),
            reverse("english_path:review"),
        )
        for url in protected_gets:
            self.assertEqual(self.client.get(url).status_code, 302)

        user = self.create_user("direct-url")
        self.client.force_login(user)
        paid_unit_posts = (
            reverse("english_path:submit_unit_quiz", args=("a1-2",)),
            reverse("english_path:check_similar_question", args=("a1-2",)),
            reverse("english_path:submit_a1_final"),
            reverse("english_path:submit_a2_final"),
        )
        for url in paid_unit_posts:
            response = self.client.post(url, data=json.dumps({"answers": {}}), content_type="application/json")
            self.assertEqual(response.status_code, 403)
        grant_active_subscription(user, PLAN_ENGLISH_JOURNEY)
        for unit_slug in ("a1-2", "a1-10", "a2-1", "a2-10"):
            self.assertEqual(self.client.get(reverse("english_path:unit", args=(unit_slug,))).status_code, 302)
        subscription = UserSubscription.objects.get(user=user, plan_code=PLAN_ENGLISH_JOURNEY)
        subscription.expires_at = timezone.now() - timedelta(seconds=1)
        subscription.save(update_fields=("expires_at", "updated_at"))
        for url in paid_unit_posts:
            response = self.client.post(url, data=json.dumps({"answers": {}}), content_type="application/json")
            self.assertEqual(response.status_code, 403)

    @override_settings(BANK_TRANSFER_ENABLED=True)
    def test_bank_transfer_snapshot_no_early_activation_double_activation_and_ownership(self):
        user = self.create_user("bank-journey")
        other = self.create_user("bank-other")
        self.client.force_login(user)
        response = self.client.post(
            reverse("create_payment_order", args=(PLAN_ENGLISH_JOURNEY, "bank_transfer")),
            {"amount": "1", "price": "0.01", "duration": "999", "plan": "vip"},
        )
        order = PaymentOrder.objects.get(user=user)
        self.assertRedirects(response, reverse("bank_transfer_proof", args=(order.id,)))
        self.assertEqual((order.amount_sar, order.amount_halalas, order.duration_days), (Decimal("39.00"), 3900, 30))
        self.assertFalse(has_journey_subscription(user))

        self.client.force_login(other)
        self.assertEqual(self.client.get(reverse("bank_transfer_proof", args=(order.id,))).status_code, 404)
        order.status = PaymentOrder.Status.BANK_APPROVED
        order.save(update_fields=("status", "updated_at"))
        first = activate_subscription_from_payment(order)
        first_expiry = first.expires_at
        second = activate_subscription_from_payment(order)
        self.assertEqual(first.pk, second.pk)
        self.assertEqual(second.expires_at, first_expiry)
        self.assertEqual(UserSubscription.objects.filter(user=user, plan_code=PLAN_ENGLISH_JOURNEY).count(), 1)
        self.assertFalse(has_journey_subscription(other))

    def test_paywall_and_checkout_show_one_product_without_campaign_or_old_price(self):
        user = self.create_user("paywall-ux")
        self.client.force_login(user)
        pricing = self.client.get(reverse("pricing"))
        for text in (
            "English Journey A1–A2",
            "30 وحدة إجمالًا",
            "30 يومًا",
            "Vocabulary",
            "Grammar",
            "Listening",
            "Speaking",
            "Reading",
            "Writing",
            "Interactive Games",
            "Smart Review",
            "Final Challenges",
        ):
            self.assertContains(pricing, text)
        self.assertContains(
            pricing,
            f'href="{reverse("checkout", args=(PLAN_ENGLISH_JOURNEY,))}"',
            count=1,
        )
        level = self.client.get(reverse("english_path:level", args=("a1",)))
        for text in (
            "English Journey A1",
            "A1.1",
            "39",
            "إجمالي الرحلة 30 وحدة",
            "Vocabulary",
            "Grammar",
            "Listening",
            "Speaking",
            "Reading",
            "Writing",
            "Games",
            "Smart Review",
            "Final Challenges",
        ):
            self.assertContains(level, text)
        self.assertContains(level, "ابدأ الرحلة الكاملة", count=1)
        checkout_href = reverse("checkout", args=(PLAN_ENGLISH_JOURNEY,))
        self.assertContains(level, f'href="{checkout_href}"', count=1)

        with override_settings(BACK_TO_SCHOOL_ENABLED=True, BACK_TO_SCHOOL_DISCOUNT_PERCENT=90):
            checkout = self.client.get(reverse("checkout", args=(PLAN_ENGLISH_JOURNEY,)))
        self.assertEqual(checkout.context["plan"]["code"], PLAN_ENGLISH_JOURNEY)
        self.assertContains(checkout, "A1–A2")
        self.assertContains(checkout, "39")
        self.assertContains(checkout, "30")
        self.assertNotContains(checkout, "90%")
        self.assertFalse(checkout.context["campaign"]["campaign_active"])
        self.assertIn("@media (max-width: 820px)", checkout.content.decode())

    def test_subscription_query_count_does_not_scale_with_units_or_reviews(self):
        user = self.create_user("query-audit")
        grant_active_subscription(user, PLAN_ENGLISH_JOURNEY)
        self.client.force_login(user)
        self.client.get(reverse("english_path:level", args=("a1",)))
        with CaptureQueriesContext(connection) as empty_level:
            self.client.get(reverse("english_path:level", args=("a1",)))
        self.master_units(user, "A1")
        with CaptureQueriesContext(connection) as full_level:
            self.client.get(reverse("english_path:level", args=("a1",)))
        self.assertLessEqual(len(full_level), len(empty_level) + 1)

        with CaptureQueriesContext(connection) as empty_review:
            self.client.get(reverse("english_path:review"))
        for index in range(20):
            ReviewItem.objects.create(
                user=user,
                unit_code="A1.1",
                item_key=f"query-review-{index}",
                prompt=f"Prompt {index}",
                answer="Answer",
                skill="grammar",
                next_review_at=timezone.now(),
            )
        with CaptureQueriesContext(connection) as full_review:
            self.client.get(reverse("english_path:review"))
        self.assertLessEqual(len(full_review), len(empty_review) + 1)

    def test_actual_feature_flag_default_remains_closed(self):
        user = self.create_user("flag-default")
        self.client.force_login(user)
        with override_settings(ENGLISH_PATH_ENABLED=False):
            self.assertEqual(self.client.get(reverse("english_path:overview")).status_code, 404)
            self.assertEqual(self.client.get(reverse("checkout", args=(PLAN_ENGLISH_JOURNEY,))).status_code, 404)
            self.assertNotContains(self.client.get(reverse("pricing")), "English Journey A1–A2")
