import json
import shutil
import threading
import tempfile
import traceback
from datetime import timedelta
from io import BytesIO
from decimal import Decimal
from unittest import skipUnless
from unittest.mock import Mock, patch

from django.conf import settings
from django.contrib import admin as django_admin
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import IntegrityError, close_old_connections, connection, transaction
from django.test import RequestFactory, SimpleTestCase
from django.test import TestCase, TransactionTestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from PIL import Image

from phonics.admin import PaymentOrderAdmin
from phonics.models import (
    BankTransferProof,
    PaymentOrder,
    PaymentActivationReview,
    PaymentWebhookEvent,
    UserSubscription,
    activate_subscription_from_payment,
)
from phonics.views import PLAN_LEVEL_THREE, get_feature_keys
from phonics.payments.moyasar import (
    MoyasarAPIError,
    MoyasarConfigurationError,
    MoyasarInvalidResponseError,
    MoyasarInvoice,
    MoyasarNetworkError,
    MoyasarUnsafeCheckoutURLError,
    create_invoice,
    fetch_invoice,
    validate_amounts,
)
from phonics.payments.reconciliation import reconcile_payment_order


@override_settings(DISABLE_AUTO_SEED=True, RATE_LIMIT_PAYMENT=1000)
class PaymentCheckoutTests(TestCase):
    def setUp(self):
        self.media_root = tempfile.mkdtemp()
        self.media_override = override_settings(MEDIA_ROOT=self.media_root)
        self.media_override.enable()
        self.addCleanup(self.media_override.disable)
        self.addCleanup(lambda: shutil.rmtree(self.media_root, ignore_errors=True))

        self.user = User.objects.create_user(username="payment-user", password="StrongPass123!")
        self.client.force_login(self.user)

    def create_order(self, **overrides):
        defaults = {
            "user": self.user,
            "plan_code": "silver",
            "plan_name": "Silver",
            "duration_days": 30,
            "amount_halalas": 2700,
            "amount_sar": Decimal("27.00"),
            "currency": "SAR",
            "status": PaymentOrder.Status.PENDING,
            "method": PaymentOrder.Method.MOYASAR_CARD,
            "provider": PaymentOrder.Provider.MOYASAR,
        }
        defaults.update(overrides)
        return PaymentOrder.objects.create(**defaults)

    def test_checkout_requires_login(self):
        self.client.logout()

        response = self.client.get(reverse("checkout", args=["silver"]))

        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response["Location"])

    def test_checkout_page_returns_200_for_logged_in_user(self):
        response = self.client.get(reverse("checkout", args=["silver"]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "إكمال الاشتراك")
        self.assertContains(response, "الدفع عبر ميسر")
        self.assertContains(response, "STC Pay")
        self.assertContains(response, "تحويل بنكي")

    def test_level_checkout_accepts_public_hyphen_slugs(self):
        for path in ["/checkout/level-3/", "/checkout/level-4/"]:
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, "إكمال الاشتراك")
                self.assertContains(response, "15")

    def test_invalid_plan_returns_404(self):
        response = self.client.get(reverse("checkout", args=["unknown-plan"]))

        self.assertEqual(response.status_code, 404)

    @override_settings(
        MOYASAR_ENABLED=True,
        MOYASAR_SECRET_KEY="sk_test_unit_only",
        MOYASAR_ENVIRONMENT="test",
        MOYASAR_CHECKOUT_ALLOWED_HOSTS=["checkout.moyasar.com"],
    )
    @patch("phonics.views.create_moyasar_invoice")
    def test_moyasar_order_creation_does_not_activate_subscription(self, create_invoice_mock):
        create_invoice_mock.return_value = MoyasarInvoice(
            invoice_id="inv_test_123",
            checkout_url="https://checkout.moyasar.com/invoices/inv_test_123",
            amount_halalas=2700,
            currency="SAR",
            status="initiated",
        )
        response = self.client.post(reverse("create_payment_order", args=["silver", "moyasar"]))

        self.assertEqual(response.status_code, 302)
        order = PaymentOrder.objects.get()
        self.assertEqual(order.method, PaymentOrder.Method.MOYASAR_CARD)
        self.assertEqual(order.provider, PaymentOrder.Provider.MOYASAR)
        self.assertEqual(order.status, PaymentOrder.Status.INITIATED)
        self.assertEqual(order.amount_halalas, 2700)
        self.assertEqual(order.moyasar_invoice_id, "inv_test_123")
        self.assertEqual(response["Location"], order.checkout_url)
        self.assertEqual(UserSubscription.objects.count(), 0)
        self.assertFalse(self.user.groups.filter(name="Silver").exists())

    @override_settings(
        MOYASAR_ENABLED=True,
        MOYASAR_SECRET_KEY="sk_test_unit_only",
        MOYASAR_ENVIRONMENT="test",
    )
    @patch("phonics.views.create_moyasar_invoice")
    def test_stcpay_order_creation_does_not_activate_subscription(self, create_invoice_mock):
        create_invoice_mock.return_value = MoyasarInvoice(
            invoice_id="inv_stc_123",
            checkout_url="https://checkout.moyasar.com/invoices/inv_stc_123",
            amount_halalas=2700,
            currency="SAR",
            status="initiated",
        )
        response = self.client.post(reverse("create_payment_order", args=["silver", "stcpay"]))

        self.assertEqual(response.status_code, 302)
        order = PaymentOrder.objects.get()
        self.assertEqual(order.method, PaymentOrder.Method.MOYASAR_STCPAY)
        self.assertEqual(order.provider, PaymentOrder.Provider.MOYASAR)
        self.assertEqual(order.status, PaymentOrder.Status.INITIATED)
        self.assertEqual(UserSubscription.objects.count(), 0)

    def test_bank_transfer_order_routes_to_receipt_upload(self):
        response = self.client.post(reverse("create_payment_order", args=["silver", "bank_transfer"]))

        self.assertEqual(response.status_code, 302)
        order = PaymentOrder.objects.get()
        self.assertEqual(order.method, PaymentOrder.Method.BANK_TRANSFER)
        self.assertEqual(order.provider, PaymentOrder.Provider.MANUAL_BANK)
        self.assertEqual(order.status, PaymentOrder.Status.AWAITING_BANK_REVIEW)
        self.assertIn(reverse("bank_transfer_proof", args=[order.id]), response["Location"])
        self.assertEqual(UserSubscription.objects.count(), 0)

    def test_bank_transfer_receipt_upload_accepts_jpg_png_and_pdf(self):
        cases = [
            ("receipt.jpg", b"\xff\xd8\xff", "image/jpeg"),
            ("receipt.png", b"\x89PNG\r\n\x1a\n", "image/png"),
            ("receipt.pdf", b"%PDF-1.4\n", "application/pdf"),
        ]

        for filename, content, content_type in cases:
            with self.subTest(filename=filename):
                order = self.create_order(
                    method=PaymentOrder.Method.BANK_TRANSFER,
                    provider=PaymentOrder.Provider.MANUAL_BANK,
                    status=PaymentOrder.Status.AWAITING_BANK_REVIEW,
                )
                receipt = SimpleUploadedFile(filename, content, content_type=content_type)

                response = self.client.post(reverse("bank_transfer_proof", args=[order.id]), {
                    "sender_name": "Payment User",
                    "bank_name": "Test Bank",
                    "transfer_reference": f"TRX-{order.id}",
                    "sender_account_last_digits": "1234",
                    "transferred_at": timezone.localdate().isoformat(),
                    "amount_sar": "27.00",
                    "receipt_file": receipt,
                })

                self.assertEqual(response.status_code, 302)
                proof = BankTransferProof.objects.get(payment_order=order)
                self.assertEqual(proof.status, BankTransferProof.Status.PENDING_REVIEW)
                order.refresh_from_db()
                self.assertEqual(order.provider_status, "bank_receipt_uploaded")

    def test_bank_transfer_rejects_disallowed_file_type(self):
        order = self.create_order(
            method=PaymentOrder.Method.BANK_TRANSFER,
            provider=PaymentOrder.Provider.MANUAL_BANK,
            status=PaymentOrder.Status.AWAITING_BANK_REVIEW,
        )
        receipt = SimpleUploadedFile("receipt.exe", b"bad", content_type="application/octet-stream")

        response = self.client.post(reverse("bank_transfer_proof", args=[order.id]), {
            "sender_name": "Payment User",
            "bank_name": "Test Bank",
            "transferred_at": timezone.localdate().isoformat(),
            "amount_sar": "27.00",
            "receipt_file": receipt,
        })

        self.assertEqual(response.status_code, 400)
        self.assertEqual(BankTransferProof.objects.count(), 0)

    def test_bank_transfer_rejects_fake_jpg_content(self):
        order = self.create_order(
            method=PaymentOrder.Method.BANK_TRANSFER,
            provider=PaymentOrder.Provider.MANUAL_BANK,
            status=PaymentOrder.Status.AWAITING_BANK_REVIEW,
        )
        receipt = SimpleUploadedFile("receipt.jpg", b"<html>not an image</html>", content_type="image/jpeg")
        response = self.client.post(reverse("bank_transfer_proof", args=[order.id]), {
            "sender_name": "Payment User",
            "bank_name": "Test Bank",
            "transferred_at": timezone.localdate().isoformat(),
            "amount_sar": "27.00",
            "receipt_file": receipt,
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual(BankTransferProof.objects.count(), 0)

    def test_bank_transfer_accepts_real_generated_png(self):
        image_bytes = BytesIO()
        Image.new("RGB", (8, 8), color="blue").save(image_bytes, format="PNG")
        order = self.create_order(
            method=PaymentOrder.Method.BANK_TRANSFER,
            provider=PaymentOrder.Provider.MANUAL_BANK,
            status=PaymentOrder.Status.AWAITING_BANK_REVIEW,
        )
        receipt = SimpleUploadedFile("../ odd receipt ..png", image_bytes.getvalue(), content_type="text/plain")
        response = self.client.post(reverse("bank_transfer_proof", args=[order.id]), {
            "sender_name": "Payment User", "bank_name": "Test Bank",
            "transferred_at": timezone.localdate().isoformat(), "amount_sar": "27.00", "receipt_file": receipt,
        })
        self.assertEqual(response.status_code, 302)
        stored_name = BankTransferProof.objects.get(payment_order=order).receipt_file.name
        self.assertNotIn("..", stored_name)
        self.assertNotIn("odd", stored_name)

    def test_bank_transfer_rejects_html_named_pdf_and_signature_extension_mismatch(self):
        for filename, content in [
            ("receipt.pdf", b"<html>fake</html>"),
            ("receipt.jpg", b"%PDF-1.4\n"),
        ]:
            with self.subTest(filename=filename):
                order = self.create_order(
                    method=PaymentOrder.Method.BANK_TRANSFER,
                    provider=PaymentOrder.Provider.MANUAL_BANK,
                    status=PaymentOrder.Status.AWAITING_BANK_REVIEW,
                )
                receipt = SimpleUploadedFile(filename, content, content_type="application/octet-stream")
                response = self.client.post(reverse("bank_transfer_proof", args=[order.id]), {
                    "sender_name": "Payment User", "bank_name": "Test Bank",
                    "transferred_at": timezone.localdate().isoformat(), "amount_sar": "27.00", "receipt_file": receipt,
                })
                self.assertEqual(response.status_code, 400)
                self.assertFalse(BankTransferProof.objects.filter(payment_order=order).exists())

    def test_bank_transfer_rejects_large_file(self):
        order = self.create_order(
            method=PaymentOrder.Method.BANK_TRANSFER,
            provider=PaymentOrder.Provider.MANUAL_BANK,
            status=PaymentOrder.Status.AWAITING_BANK_REVIEW,
        )
        receipt = SimpleUploadedFile(
            "receipt.pdf",
            b"x" * ((5 * 1024 * 1024) + 1),
            content_type="application/pdf",
        )

        response = self.client.post(reverse("bank_transfer_proof", args=[order.id]), {
            "sender_name": "Payment User",
            "bank_name": "Test Bank",
            "transferred_at": timezone.localdate().isoformat(),
            "amount_sar": "27.00",
            "receipt_file": receipt,
        })

        self.assertEqual(response.status_code, 400)
        self.assertEqual(BankTransferProof.objects.count(), 0)

    def test_user_cannot_view_another_users_bank_transfer_order(self):
        order = self.create_order(
            method=PaymentOrder.Method.BANK_TRANSFER,
            provider=PaymentOrder.Provider.MANUAL_BANK,
            status=PaymentOrder.Status.AWAITING_BANK_REVIEW,
        )
        other = User.objects.create_user(username="other-user", password="StrongPass123!")
        self.client.force_login(other)

        response = self.client.get(reverse("bank_transfer_proof", args=[order.id]))

        self.assertEqual(response.status_code, 404)

    def test_paid_payment_activates_subscription_once(self):
        order = self.create_order(status=PaymentOrder.Status.PAID)

        subscription = activate_subscription_from_payment(order)
        first_expires_at = subscription.expires_at
        subscription_again = activate_subscription_from_payment(order)

        self.assertEqual(subscription.id, subscription_again.id)
        self.assertEqual(UserSubscription.objects.count(), 1)
        subscription.refresh_from_db()
        self.assertEqual(subscription.expires_at, first_expires_at)
        self.assertTrue(self.user.groups.filter(name="Silver").exists())
        self.assertIn("sounds_worksheets", get_feature_keys(self.user))

    def test_bank_approved_activates_and_rejected_does_not(self):
        approved = self.create_order(
            method=PaymentOrder.Method.BANK_TRANSFER,
            provider=PaymentOrder.Provider.MANUAL_BANK,
            status=PaymentOrder.Status.BANK_APPROVED,
        )
        activate_subscription_from_payment(approved)
        self.assertEqual(UserSubscription.objects.count(), 1)

        rejected = self.create_order(
            plan_code=PLAN_LEVEL_THREE,
            plan_name="Level 3",
            amount_halalas=1500,
            amount_sar=Decimal("15.00"),
            method=PaymentOrder.Method.BANK_TRANSFER,
            provider=PaymentOrder.Provider.MANUAL_BANK,
            status=PaymentOrder.Status.BANK_REJECTED,
        )
        with self.assertRaises(ValidationError):
            activate_subscription_from_payment(rejected)
        self.assertEqual(UserSubscription.objects.count(), 1)

    def test_admin_approve_and_reject_bank_transfer_actions(self):
        admin_user = User.objects.create_superuser(
            username="admin-review",
            email="admin@example.com",
            password="StrongPass123!",
        )
        model_admin = PaymentOrderAdmin(PaymentOrder, django_admin.site)
        model_admin.message_user = lambda *args, **kwargs: None
        request = RequestFactory().post("/admin/phonics/paymentorder/")
        request.user = admin_user

        approved = self.create_order(
            method=PaymentOrder.Method.BANK_TRANSFER,
            provider=PaymentOrder.Provider.MANUAL_BANK,
            status=PaymentOrder.Status.AWAITING_BANK_REVIEW,
        )
        model_admin.approve_bank_transfer(request, PaymentOrder.objects.filter(pk=approved.pk))
        approved.refresh_from_db()
        subscription = UserSubscription.objects.get(user=self.user, plan_code="silver")
        first_expires_at = subscription.expires_at
        self.assertEqual(approved.status, PaymentOrder.Status.BANK_APPROVED)

        model_admin.approve_bank_transfer(request, PaymentOrder.objects.filter(pk=approved.pk))
        subscription.refresh_from_db()
        self.assertEqual(UserSubscription.objects.filter(user=self.user, plan_code="silver").count(), 1)
        self.assertEqual(subscription.expires_at, first_expires_at)

        rejected = self.create_order(
            plan_code=PLAN_LEVEL_THREE,
            plan_name="Level 3",
            amount_halalas=1500,
            amount_sar=Decimal("15.00"),
            method=PaymentOrder.Method.BANK_TRANSFER,
            provider=PaymentOrder.Provider.MANUAL_BANK,
            status=PaymentOrder.Status.AWAITING_BANK_REVIEW,
        )
        model_admin.reject_bank_transfer(request, PaymentOrder.objects.filter(pk=rejected.pk))
        rejected.refresh_from_db()
        self.assertEqual(rejected.status, PaymentOrder.Status.BANK_REJECTED)
        self.assertFalse(UserSubscription.objects.filter(user=self.user, plan_code=PLAN_LEVEL_THREE).exists())

    def test_level_three_subscription_opens_only_level_three_features(self):
        order = self.create_order(
            plan_code=PLAN_LEVEL_THREE,
            plan_name="Level 3",
            amount_halalas=1500,
            amount_sar=Decimal("15.00"),
            status=PaymentOrder.Status.PAID,
        )

        activate_subscription_from_payment(order)

        feature_keys = get_feature_keys(self.user)
        self.assertIn("cvc_words", feature_keys)
        self.assertIn("cvc_worksheets", feature_keys)
        self.assertNotIn("level_four", feature_keys)

    def test_moyasar_callback_does_not_trust_query_status(self):
        order = self.create_order(provider_payment_id="")

        response = self.client.get(
            reverse("moyasar_callback"),
            {"order": order.id, "id": "pay_123", "status": "paid"},
        )

        self.assertEqual(response.status_code, 302)
        order.refresh_from_db()
        self.assertEqual(order.status, PaymentOrder.Status.PENDING)
        self.assertEqual(order.provider_payment_id, "")
        self.assertEqual(order.moyasar_payment_id, None)
        self.assertEqual(UserSubscription.objects.count(), 0)

    @override_settings(MOYASAR_WEBHOOK_SECRET="")
    def test_moyasar_webhook_is_present_but_disabled_until_secret_exists(self):
        response = self.client.post(reverse("moyasar_webhook"), data="{}", content_type="application/json")

        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()["status"], "webhook_disabled")

    def test_payment_status_pages_work(self):
        order = self.create_order()

        for name in ["payment_success", "payment_failed", "payment_pending"]:
            with self.subTest(name=name):
                response = self.client.get(reverse(name), {"order": order.id})
                self.assertEqual(response.status_code, 200)

    @override_settings(MOYASAR_WEBHOOK_SECRET="webhook_test_secret")
    def test_webhook_rejects_untrusted_header_without_shared_secret(self):
        order = self.create_order()
        response = self.client.post(
            reverse("moyasar_webhook"),
            data='{"id":"evt_1","type":"payment_paid"}',
            content_type="application/json",
            HTTP_X_MOYASAR_SIGNATURE="untrusted",
        )
        self.assertEqual(response.status_code, 403)
        order.refresh_from_db()
        self.assertEqual(order.status, PaymentOrder.Status.PENDING)
        self.assertEqual(UserSubscription.objects.count(), 0)

    def test_callback_rejects_another_users_order(self):
        order = self.create_order()
        other = User.objects.create_user(username="callback-other", password="StrongPass123!")
        self.client.force_login(other)
        response = self.client.get(reverse("moyasar_callback"), {"order": order.id})
        self.assertEqual(response.status_code, 202)
        self.assertContains(response, "الدفع قيد التحقق", status_code=202)

    def test_callback_missing_order_returns_safe_pending_page(self):
        response = self.client.get(
            reverse("moyasar_callback"),
            {"order": "999999", "id": "inv_callback_missing_123456"},
        )
        self.assertEqual(response.status_code, 202)
        self.assertContains(response, "لم يتم منح أي صلاحية", status_code=202)
        self.assertNotContains(response, "inv_callback_missing_123456", status_code=202)
        self.assertEqual(UserSubscription.objects.count(), 0)

    def test_pending_order_never_looks_paid_on_success_page(self):
        order = self.create_order(status=PaymentOrder.Status.PENDING)
        response = self.client.get(reverse("payment_success"), {"order": order.id})
        self.assertContains(response, "جاري التحقق من عملية الدفع")
        self.assertNotContains(response, "تم الدفع بنجاح")

    def test_checkout_template_contains_no_card_inputs(self):
        response = self.client.get(reverse("checkout", args=["silver"]))
        content = response.content.decode("utf-8").lower()
        self.assertNotIn('name="card', content)
        self.assertNotIn('name="cvc', content)
        self.assertNotIn('name="cvv', content)
        self.assertNotIn('name="otp', content)
        self.assertNotIn('name="expiry', content)

    @override_settings(
        MOYASAR_ENABLED=True,
        MOYASAR_SECRET_KEY="sk_test_unit_only",
        MOYASAR_ENVIRONMENT="test",
    )
    @patch("phonics.views.create_moyasar_invoice")
    def test_browser_amount_is_ignored(self, create_invoice_mock):
        create_invoice_mock.return_value = MoyasarInvoice(
            invoice_id="inv_server_price",
            checkout_url="https://checkout.moyasar.com/invoices/inv_server_price",
            amount_halalas=2700,
            currency="SAR",
            status="initiated",
        )
        self.client.post(
            reverse("create_payment_order", args=["silver", "moyasar"]),
            {"amount_sar": "0.01", "amount_halalas": "1"},
        )
        kwargs = create_invoice_mock.call_args.kwargs
        self.assertEqual(kwargs["amount_sar"], Decimal("27.00"))
        self.assertEqual(kwargs["amount_halalas"], 2700)

    @override_settings(
        MOYASAR_ENABLED=True,
        MOYASAR_SECRET_KEY="sk_test_unit_only",
        MOYASAR_ENVIRONMENT="test",
    )
    @patch("phonics.views.create_moyasar_invoice")
    def test_repeated_click_reuses_initiated_invoice(self, create_invoice_mock):
        create_invoice_mock.return_value = MoyasarInvoice(
            invoice_id="inv_reused",
            checkout_url="https://checkout.moyasar.com/invoices/inv_reused",
            amount_halalas=2700,
            currency="SAR",
            status="initiated",
        )
        url = reverse("create_payment_order", args=["silver", "moyasar"])
        first = self.client.post(url)
        second = self.client.post(url)
        self.assertEqual(first["Location"], second["Location"])
        self.assertEqual(PaymentOrder.objects.count(), 1)
        self.assertEqual(create_invoice_mock.call_count, 1)

    @override_settings(MOYASAR_ENABLED=True)
    @patch("phonics.views.create_moyasar_invoice")
    def test_paid_order_does_not_create_another_invoice(self, create_invoice_mock):
        paid = self.create_order(status=PaymentOrder.Status.PAID)
        response = self.client.post(reverse("create_payment_order", args=["silver", "moyasar"]))
        self.assertIn(f"order={paid.id}", response["Location"])
        self.assertEqual(PaymentOrder.objects.count(), 1)
        create_invoice_mock.assert_not_called()

    @override_settings(MOYASAR_ENABLED=True)
    @patch("phonics.views.create_moyasar_invoice", side_effect=MoyasarNetworkError("network"))
    def test_timeout_does_not_activate_subscription(self, create_invoice_mock):
        response = self.client.post(reverse("create_payment_order", args=["silver", "moyasar"]))
        self.assertEqual(response.status_code, 302)
        order = PaymentOrder.objects.get()
        self.assertEqual(order.status, PaymentOrder.Status.INVOICE_CREATION_UNKNOWN)
        self.assertEqual(order.failure_code, "network_error")
        self.assertEqual(UserSubscription.objects.count(), 0)

    @override_settings(MOYASAR_ENABLED=True, MOYASAR_SECRET_KEY="", MOYASAR_ENVIRONMENT="test")
    def test_missing_secret_key_returns_safe_checkout_error(self):
        response = self.client.post(reverse("create_payment_order", args=["silver", "moyasar"]), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "تعذر فتح صفحة الدفع حاليًا. حاول مرة أخرى.")
        self.assertEqual(UserSubscription.objects.count(), 0)


@override_settings(
    DISABLE_AUTO_SEED=True,
    MOYASAR_SECRET_KEY="sk_test_unit_only",
    MOYASAR_ENVIRONMENT="test",
    MOYASAR_WEBHOOK_SECRET="webhook_test_secret",
)
class MoyasarReconciliationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="reconcile-user", password="StrongPass123!")
        self.client.force_login(self.user)
        self.order = PaymentOrder.objects.create(
            user=self.user,
            plan_code="silver",
            plan_name="Silver",
            duration_days=30,
            amount_halalas=2700,
            amount_sar=Decimal("27.00"),
            currency="SAR",
            status=PaymentOrder.Status.INITIATED,
            method=PaymentOrder.Method.MOYASAR_CARD,
            provider=PaymentOrder.Provider.MOYASAR,
            payment_environment=PaymentOrder.Environment.TEST,
            moyasar_invoice_id="inv_reconcile_1",
            checkout_url="https://checkout.moyasar.com/invoices/inv_reconcile_1",
        )

    def invoice(self, **overrides):
        data = {
            "id": self.order.moyasar_invoice_id,
            "status": "paid",
            "amount": 2700,
            "currency": "SAR",
            "metadata": {
                "payment_order_id": str(self.order.id),
                "user_id": str(self.user.id),
                "plan_code": self.order.to_plan_code or self.order.plan_code,
                "operation_type": self.order.operation_type,
                "quote_reference": str(self.order.idempotency_key),
            },
            "payments": [{
                "id": "pay_reconcile_1",
                "invoice_id": self.order.moyasar_invoice_id,
                "status": "paid",
                "amount": 2700,
                "currency": "SAR",
                "live": False,
            }],
        }
        data.update(overrides)
        return data

    def webhook_payload(self, **overrides):
        payload = {
            "id": "evt_reconcile_1",
            "type": "payment_paid",
            "live": False,
            "secret_token": "webhook_test_secret",
            "data": {"invoice_id": self.order.moyasar_invoice_id, "status": "paid"},
        }
        payload.update(overrides)
        return payload

    @patch("phonics.payments.reconciliation.fetch_invoice")
    def test_paid_callback_activates_once_and_ignores_query_financial_data(self, fetch_mock):
        fetch_mock.return_value = self.invoice()
        url = reverse("moyasar_callback")
        first = self.client.get(url, {
            "order": self.order.id, "status": "failed", "amount": "1", "currency": "USD",
        })
        second = self.client.get(url, {"order": self.order.id, "status": "paid"})
        self.order.refresh_from_db()
        self.assertIn(reverse("payment_success"), first["Location"])
        self.assertIn(reverse("payment_success"), second["Location"])
        self.assertEqual(self.order.status, PaymentOrder.Status.PAID)
        self.assertEqual(self.order.moyasar_payment_id, "pay_reconcile_1")
        self.assertIsNotNone(self.order.activated_at)
        self.assertEqual(UserSubscription.objects.count(), 1)
        self.assertEqual(fetch_mock.call_count, 1)

    @patch("phonics.payments.reconciliation.fetch_invoice")
    def test_webhook_then_callback_is_idempotent(self, fetch_mock):
        fetch_mock.return_value = self.invoice()
        webhook = self.client.post(
            reverse("moyasar_webhook"),
            data=json.dumps(self.webhook_payload()),
            content_type="application/json",
        )
        callback = self.client.get(reverse("moyasar_callback"), {"order": self.order.id})
        self.assertEqual(webhook.status_code, 200)
        self.assertIn(reverse("payment_success"), callback["Location"])
        self.assertEqual(fetch_mock.call_count, 1)
        self.assertEqual(UserSubscription.objects.count(), 1)

    @patch("phonics.payments.reconciliation.fetch_invoice")
    def test_late_upgrade_webhook_then_callback_creates_one_review(self, fetch_mock):
        expired_at = timezone.now() - timedelta(seconds=1)
        UserSubscription.objects.create(
            user=self.user,
            plan_code="basic",
            status=UserSubscription.Status.ACTIVE,
            starts_at=expired_at - timedelta(days=30),
            expires_at=expired_at,
        )
        self.order.operation_type = PaymentOrder.OperationType.UPGRADE
        self.order.from_plan_code = "basic"
        self.order.to_plan_code = "silver"
        self.order.current_expires_at = expired_at
        self.order.save(update_fields=[
            "operation_type", "from_plan_code", "to_plan_code",
            "current_expires_at", "updated_at",
        ])
        fetch_mock.return_value = self.invoice()

        webhook = self.client.post(
            reverse("moyasar_webhook"),
            data=json.dumps(self.webhook_payload(id="evt_late_upgrade")),
            content_type="application/json",
        )
        callback = self.client.get(reverse("moyasar_callback"), {"order": self.order.id})

        self.order.refresh_from_db()
        self.assertEqual(webhook.status_code, 200)
        self.assertIn(reverse("payment_pending"), callback["Location"])
        self.assertEqual(self.order.status, PaymentOrder.Status.PAID_REQUIRES_REVIEW)
        self.assertIsNone(self.order.activated_at)
        self.assertEqual(PaymentActivationReview.objects.filter(payment_order=self.order).count(), 1)
        self.assertEqual(fetch_mock.call_count, 1)

    @patch("phonics.payments.reconciliation.fetch_invoice")
    def test_callback_then_webhook_is_idempotent(self, fetch_mock):
        fetch_mock.return_value = self.invoice()
        self.client.get(reverse("moyasar_callback"), {"order": self.order.id})
        response = self.client.post(
            reverse("moyasar_webhook"),
            data=json.dumps(self.webhook_payload()),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(fetch_mock.call_count, 1)
        self.assertEqual(UserSubscription.objects.count(), 1)

    @patch("phonics.payments.reconciliation.fetch_invoice")
    def test_duplicate_webhook_event_returns_2xx_without_reprocessing(self, fetch_mock):
        fetch_mock.return_value = self.invoice(status="initiated", payments=[])
        body = json.dumps(self.webhook_payload())
        first = self.client.post(reverse("moyasar_webhook"), data=body, content_type="application/json")
        second = self.client.post(reverse("moyasar_webhook"), data=body, content_type="application/json")
        self.assertEqual(first.status_code, 202)
        self.assertEqual(second.status_code, 200)
        self.assertEqual(second.json()["status"], "duplicate")
        self.assertEqual(fetch_mock.call_count, 1)
        self.assertEqual(PaymentWebhookEvent.objects.count(), 1)

    def test_webhook_authentication_validation_and_body_limit(self):
        cases = [
            ({"secret_token": "wrong"}, 403),
            ({"secret_token": None}, 403),
            ({"live": True}, 403),
            ({"type": "unknown"}, 400),
            ({"id": ""}, 400),
        ]
        for overrides, expected_status in cases:
            with self.subTest(overrides=overrides):
                payload = self.webhook_payload(**overrides)
                response = self.client.post(
                    reverse("moyasar_webhook"), data=json.dumps(payload), content_type="application/json"
                )
                self.assertEqual(response.status_code, expected_status)
        with override_settings(MOYASAR_WEBHOOK_MAX_BODY_BYTES=1024):
            oversized = json.dumps(self.webhook_payload(extra="x" * 2000))
            response = self.client.post(
                reverse("moyasar_webhook"), data=oversized, content_type="application/json"
            )
            self.assertEqual(response.status_code, 413)
        self.assertEqual(PaymentWebhookEvent.objects.count(), 0)

    @patch("phonics.views.reconcile_payment_order")
    def test_webhook_invalid_json_returns_400_without_side_effects(self, reconcile_mock):
        invalid_body = '{"secret_token":"' + settings.MOYASAR_WEBHOOK_SECRET + '",'
        response = self.client.post(
            reverse("moyasar_webhook"),
            data=invalid_body,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["status"], "invalid_json")
        self.assertEqual(PaymentWebhookEvent.objects.count(), 0)
        reconcile_mock.assert_not_called()

    @patch("phonics.payments.reconciliation.fetch_invoice")
    def test_payment_failed_webhook_reconciles_without_activation(self, fetch_mock):
        fetch_mock.return_value = self.invoice(status="failed", payments=[])
        payload = self.webhook_payload(id="evt_payment_failed", type="payment_failed")
        response = self.client.post(
            reverse("moyasar_webhook"),
            data=json.dumps(payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.order.refresh_from_db()
        event = PaymentWebhookEvent.objects.get(event_id="evt_payment_failed")
        self.assertEqual(self.order.status, PaymentOrder.Status.FAILED)
        self.assertEqual(event.processing_status, PaymentWebhookEvent.ProcessingStatus.PROCESSED)
        self.assertEqual(UserSubscription.objects.count(), 0)
        self.assertFalse(hasattr(event, "payload"))

    @patch("phonics.payments.reconciliation.fetch_invoice")
    def test_webhook_secret_never_appears_in_response_or_logs(self, fetch_mock):
        fetch_mock.return_value = self.invoice(status="initiated", payments=[])
        secret = settings.MOYASAR_WEBHOOK_SECRET
        payload = self.webhook_payload(id="evt_secret_redaction")
        with (
            patch("phonics.views.payment_logger") as view_logger,
            patch("phonics.payments.reconciliation.logger") as reconciliation_logger,
        ):
            response = self.client.post(
                reverse("moyasar_webhook"),
                data=json.dumps(payload),
                content_type="application/json",
            )
        self.assertNotIn(secret, response.content.decode("utf-8"))
        self.assertNotIn(secret, str(view_logger.mock_calls))
        self.assertNotIn(secret, str(reconciliation_logger.mock_calls))

    @patch("phonics.payments.reconciliation.fetch_invoice")
    def test_financial_and_reference_mismatches_never_activate(self, fetch_mock):
        mismatch_cases = [
            {"id": "inv_other"},
            {"amount": 2800},
            {"currency": "USD"},
            {"metadata": {**self.invoice()["metadata"], "payment_order_id": "999"}},
            {"metadata": {**self.invoice()["metadata"], "user_id": "999"}},
            {"metadata": {**self.invoice()["metadata"], "plan_code": "level_4"}},
            {"metadata": {**self.invoice()["metadata"], "plan_code": ""}},
            {"metadata": {**self.invoice()["metadata"], "operation_type": "renewal"}},
            {"metadata": {**self.invoice()["metadata"], "quote_reference": "wrong"}},
            {"live": True},
            {"payments": []},
        ]
        for overrides in mismatch_cases:
            with self.subTest(overrides=overrides):
                self.order.status = PaymentOrder.Status.INITIATED
                self.order.provider_status = ""
                self.order.failure_code = None
                self.order.save(update_fields=["status", "provider_status", "failure_code", "updated_at"])
                fetch_mock.return_value = self.invoice(**overrides)
                result = reconcile_payment_order(self.order.id)
                self.order.refresh_from_db()
                self.assertEqual(result.status, "mismatch")
                self.assertNotEqual(self.order.status, PaymentOrder.Status.PAID)
                self.assertEqual(UserSubscription.objects.count(), 0)

    @patch("phonics.payments.reconciliation.fetch_invoice")
    def test_same_price_level_four_invoice_cannot_activate_level_three_order(self, fetch_mock):
        self.order.plan_code = "level_3"
        self.order.to_plan_code = "level_3"
        self.order.plan_name = "Level 3"
        self.order.amount_halalas = 1500
        self.order.amount_sar = Decimal("15.00")
        self.order.amount_due = Decimal("15.00")
        self.order.save(update_fields=[
            "plan_code", "to_plan_code", "plan_name", "amount_halalas",
            "amount_sar", "amount_due", "updated_at",
        ])
        invoice = self.invoice(amount=1500)
        invoice["metadata"]["plan_code"] = "level_4"
        invoice["payments"][0]["amount"] = 1500
        fetch_mock.return_value = invoice

        result = reconcile_payment_order(self.order.id)

        self.order.refresh_from_db()
        self.assertEqual(result.code, "metadata_plan_mismatch")
        self.assertEqual(self.order.status, PaymentOrder.Status.INITIATED)
        self.assertEqual(UserSubscription.objects.count(), 0)

    @patch("phonics.payments.reconciliation.fetch_invoice")
    def test_pending_failed_expired_and_canceled_statuses(self, fetch_mock):
        expected = {
            "initiated": PaymentOrder.Status.INITIATED,
            "failed": PaymentOrder.Status.FAILED,
            "expired": PaymentOrder.Status.EXPIRED,
            "canceled": PaymentOrder.Status.CANCELED,
        }
        for provider_status, local_status in expected.items():
            with self.subTest(provider_status=provider_status):
                self.order.status = PaymentOrder.Status.INITIATED
                self.order.failed_at = None
                self.order.canceled_at = None
                self.order.save(update_fields=["status", "failed_at", "canceled_at", "updated_at"])
                fetch_mock.return_value = self.invoice(status=provider_status, payments=[])
                reconcile_payment_order(self.order.id)
                self.order.refresh_from_db()
                self.assertEqual(self.order.status, local_status)
                self.assertEqual(UserSubscription.objects.count(), 0)

    @patch("phonics.payments.reconciliation.fetch_invoice")
    def test_transient_fetch_failures_remain_nonterminal(self, fetch_mock):
        errors = [
            MoyasarNetworkError("timeout"),
            MoyasarAPIError(status_code=404),
            MoyasarAPIError(status_code=429),
            MoyasarAPIError(status_code=500),
        ]
        for error in errors:
            with self.subTest(error=type(error).__name__, status=getattr(error, "status_code", None)):
                self.order.status = PaymentOrder.Status.INITIATED
                self.order.save(update_fields=["status", "updated_at"])
                fetch_mock.side_effect = error
                result = reconcile_payment_order(self.order.id)
                self.order.refresh_from_db()
                self.assertEqual(result.status, "pending")
                self.assertEqual(self.order.status, PaymentOrder.Status.INITIATED)
                self.assertEqual(UserSubscription.objects.count(), 0)

    @patch("phonics.payments.reconciliation.fetch_invoice")
    def test_duplicate_payment_id_is_rejected(self, fetch_mock):
        PaymentOrder.objects.create(
            user=self.user, plan_code="basic", plan_name="Basic", duration_days=30,
            amount_halalas=1000, amount_sar=Decimal("10.00"), currency="SAR",
            status=PaymentOrder.Status.PAID, method=PaymentOrder.Method.MOYASAR_CARD,
            provider=PaymentOrder.Provider.MOYASAR, moyasar_invoice_id="inv_existing",
            moyasar_payment_id="pay_reconcile_1", provider_payment_id="pay_reconcile_1",
        )
        fetch_mock.return_value = self.invoice()
        result = reconcile_payment_order(self.order.id)
        self.order.refresh_from_db()
        self.assertEqual(result.status, "mismatch")
        self.assertEqual(self.order.status, PaymentOrder.Status.INITIATED)
        self.assertEqual(UserSubscription.objects.count(), 0)

    def test_invoice_id_cannot_be_linked_to_another_order(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                PaymentOrder.objects.create(
                    user=self.user, plan_code="basic", plan_name="Basic", duration_days=30,
                    amount_halalas=1000, amount_sar=Decimal("10.00"), currency="SAR",
                    status=PaymentOrder.Status.INITIATED, method=PaymentOrder.Method.MOYASAR_CARD,
                    provider=PaymentOrder.Provider.MOYASAR,
                    moyasar_invoice_id=self.order.moyasar_invoice_id,
                )

    @patch("phonics.payments.reconciliation.activate_subscription_from_payment")
    @patch("phonics.payments.reconciliation.fetch_invoice")
    def test_payment_update_and_activation_are_atomic(self, fetch_mock, activate_mock):
        fetch_mock.return_value = self.invoice()

        def assert_atomic(order):
            self.assertTrue(any(
                not getattr(block, "_from_testcase", False)
                for block in connection.atomic_blocks
            ))
            return activate_subscription_from_payment(order)

        activate_mock.side_effect = assert_atomic
        reconcile_payment_order(self.order.id)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, PaymentOrder.Status.PAID)
        self.assertIsNotNone(self.order.activated_at)

    @patch("phonics.payments.reconciliation.activate_subscription_from_payment", side_effect=RuntimeError("boom"))
    @patch("phonics.payments.reconciliation.fetch_invoice")
    def test_activation_failure_rolls_back_paid_state(self, fetch_mock, activate_mock):
        fetch_mock.return_value = self.invoice()
        with self.assertRaises(RuntimeError):
            reconcile_payment_order(self.order.id)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, PaymentOrder.Status.INITIATED)
        self.assertIsNone(self.order.moyasar_payment_id)
        self.assertEqual(UserSubscription.objects.count(), 0)

    def test_bank_order_does_not_use_moyasar_reconciliation(self):
        self.order.method = PaymentOrder.Method.BANK_TRANSFER
        self.order.provider = PaymentOrder.Provider.MANUAL_BANK
        self.order.save(update_fields=["method", "provider", "updated_at"])
        with patch("phonics.payments.reconciliation.fetch_invoice") as fetch_mock:
            result = reconcile_payment_order(self.order.id)
        self.assertEqual(result.status, "invalid")
        fetch_mock.assert_not_called()
        response = self.client.get(reverse("moyasar_callback"), {"order": self.order.id})
        self.assertEqual(response.status_code, 202)

    def test_models_do_not_store_card_or_raw_webhook_payload(self):
        payment_fields = {field.name.lower() for field in PaymentOrder._meta.fields}
        webhook_fields = {field.name.lower() for field in PaymentWebhookEvent._meta.fields}
        for forbidden in {"card", "cvc", "cvv", "otp", "three_ds", "payload"}:
            self.assertNotIn(forbidden, payment_fields)
            self.assertNotIn(forbidden, webhook_fields)

    @override_settings(
        MOYASAR_ENABLED=True,
        MOYASAR_CHECKOUT_ALLOWED_HOSTS=["checkout.moyasar.com"],
    )
    @patch("phonics.views.create_moyasar_invoice")
    def test_invoice_http_call_occurs_outside_atomic_block(self, create_mock):
        self.order.delete()

        def provider_call(**kwargs):
            self.assertFalse(any(
                not getattr(block, "_from_testcase", False)
                for block in connection.atomic_blocks
            ))
            return MoyasarInvoice(
                invoice_id="inv_no_lock", checkout_url="https://checkout.moyasar.com/invoices/inv_no_lock",
                amount_halalas=2700, currency="SAR", status="initiated",
            )

        create_mock.side_effect = provider_call
        response = self.client.post(reverse("create_payment_order", args=["silver", "moyasar"]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(PaymentOrder.objects.get().status, PaymentOrder.Status.INITIATED)

    def test_profile_dashboard_lists_only_current_users_payment_orders(self):
        other = User.objects.create_user(username="profile-other", password="StrongPass123!")
        PaymentOrder.objects.create(
            user=other, plan_code="silver", plan_name="Other secret plan", duration_days=30,
            amount_halalas=2700, amount_sar=Decimal("27.00"), currency="SAR",
            status=PaymentOrder.Status.PENDING, method=PaymentOrder.Method.MOYASAR_CARD,
            provider=PaymentOrder.Provider.MOYASAR,
        )
        response = self.client.get(reverse("profile_dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Silver")
        self.assertNotContains(response, "Other secret plan")


@override_settings(
    DISABLE_AUTO_SEED=True,
    MOYASAR_SECRET_KEY="sk_test_unit_only",
    MOYASAR_ENVIRONMENT="test",
)
class MoyasarReconciliationRaceTests(TransactionTestCase):
    reset_sequences = True

    def create_race_order_and_invoice(self):
        user = User.objects.create_user(username="race-user", password="StrongPass123!")
        order = PaymentOrder.objects.create(
            user=user, plan_code="silver", plan_name="Silver", duration_days=30,
            amount_halalas=2700, amount_sar=Decimal("27.00"), currency="SAR",
            status=PaymentOrder.Status.INITIATED, method=PaymentOrder.Method.MOYASAR_CARD,
            provider=PaymentOrder.Provider.MOYASAR, payment_environment=PaymentOrder.Environment.TEST,
            moyasar_invoice_id="inv_race_1",
        )
        invoice = {
            "id": "inv_race_1", "status": "paid", "amount": 2700, "currency": "SAR",
            "metadata": {
                "payment_order_id": str(order.id),
                "user_id": str(user.id),
                "plan_code": order.to_plan_code or order.plan_code,
                "operation_type": order.operation_type,
                "quote_reference": str(order.idempotency_key),
            },
            "payments": [{
                "id": "pay_race_1", "invoice_id": "inv_race_1", "status": "paid",
                "amount": 2700, "currency": "SAR", "live": False,
            }],
        }
        return user, order, invoice

    def test_repeated_reconciliation_is_idempotent(self):
        user, order, invoice = self.create_race_order_and_invoice()
        with patch("phonics.payments.reconciliation.fetch_invoice", return_value=invoice) as fetch_mock:
            first = reconcile_payment_order(order.id)
            second = reconcile_payment_order(order.id)

        order.refresh_from_db()
        self.assertEqual(first.status, "paid")
        self.assertEqual(second.status, "paid")
        self.assertEqual(order.status, PaymentOrder.Status.PAID)
        self.assertIsNotNone(order.activated_at)
        self.assertEqual(order.moyasar_payment_id, "pay_race_1")
        self.assertEqual(UserSubscription.objects.filter(user=user, plan_code="silver").count(), 1)
        self.assertEqual(fetch_mock.call_count, 1)

    @skipUnless(connection.vendor == "postgresql", "PostgreSQL row-lock integration test")
    def test_postgresql_concurrent_reconciliation_never_activates_twice(self):
        user, order, invoice = self.create_race_order_and_invoice()
        barrier = threading.Barrier(2)
        results = []
        errors = []

        def fetched_invoice(_invoice_id):
            barrier.wait(timeout=5)
            return invoice

        def worker():
            close_old_connections()
            try:
                results.append(reconcile_payment_order(order.id))
            except Exception as exc:
                errors.append("".join(traceback.format_exception(exc)))
            finally:
                close_old_connections()

        with patch("phonics.payments.reconciliation.fetch_invoice", side_effect=fetched_invoice):
            threads = [threading.Thread(target=worker) for _ in range(2)]
            for thread in threads:
                thread.start()
            for thread in threads:
                thread.join(timeout=10)

        self.assertTrue(all(not thread.is_alive() for thread in threads))
        self.assertFalse(errors, "Unexpected reconciliation thread errors:\n" + "\n".join(errors))
        order.refresh_from_db()
        self.assertEqual(order.status, PaymentOrder.Status.PAID)
        self.assertIsNotNone(order.activated_at)
        self.assertEqual(order.moyasar_payment_id, "pay_race_1")
        self.assertEqual(UserSubscription.objects.filter(user=user, plan_code="silver").count(), 1)
        self.assertEqual(len(results), 2)

    @skipUnless(connection.vendor == "postgresql", "PostgreSQL row-lock integration test")
    def test_postgresql_two_different_main_payments_leave_one_active_main(self):
        user = User.objects.create_user(username="two-plan-race", password="StrongPass123!")
        orders = [
            PaymentOrder.objects.create(
                user=user,
                plan_code=code,
                to_plan_code=code,
                plan_name=code.title(),
                duration_days=30,
                operation_type=PaymentOrder.OperationType.PURCHASE,
                amount_halalas=amount,
                amount_sar=Decimal(amount) / 100,
                amount_due=Decimal(amount) / 100,
                target_price=Decimal(amount) / 100,
                currency="SAR",
                status=PaymentOrder.Status.PAID,
                method=PaymentOrder.Method.MOYASAR_CARD,
                provider=PaymentOrder.Provider.MOYASAR,
                payment_environment=PaymentOrder.Environment.TEST,
                paid_at=timezone.now(),
            )
            for code, amount in (("basic", 1900), ("silver", 2700))
        ]
        barrier = threading.Barrier(2)
        errors = []

        def worker(order_id):
            close_old_connections()
            try:
                barrier.wait(timeout=5)
                activate_subscription_from_payment(PaymentOrder.objects.get(pk=order_id))
            except Exception as exc:
                errors.append("".join(traceback.format_exception(exc)))
            finally:
                close_old_connections()

        threads = [threading.Thread(target=worker, args=(order.id,)) for order in orders]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(timeout=10)

        self.assertTrue(all(not thread.is_alive() for thread in threads))
        self.assertFalse(errors, "Unexpected activation thread errors:\n" + "\n".join(errors))
        self.assertEqual(
            UserSubscription.objects.filter(
                user=user,
                status=UserSubscription.Status.ACTIVE,
                starts_at__lte=timezone.now(),
                expires_at__gt=timezone.now(),
            ).count(),
            1,
        )
        self.assertEqual(PaymentActivationReview.objects.filter(payment_order__user=user).count(), 1)


@override_settings(
    MOYASAR_SECRET_KEY="sk_test_unit_only",
    MOYASAR_ENVIRONMENT="test",
    MOYASAR_API_URL="https://api.moyasar.com/v1",
    MOYASAR_CONNECT_TIMEOUT=5,
    MOYASAR_READ_TIMEOUT=15,
    MOYASAR_CHECKOUT_ALLOWED_HOSTS=["checkout.moyasar.com"],
)
class MoyasarServiceTests(SimpleTestCase):
    def valid_response(self, **overrides):
        data = {
            "id": "inv_123",
            "url": "https://checkout.moyasar.com/invoices/inv_123?lang=ar",
            "amount": 2700,
            "currency": "SAR",
            "status": "initiated",
        }
        data.update(overrides)
        response = Mock(status_code=201, headers={"X-Request-ID": "req_123"})
        response.json.return_value = data
        return response

    def invoice_kwargs(self, **overrides):
        data = {
            "payment_order_id": 10,
            "user_id": 20,
            "plan_code": "silver",
            "operation_type": "purchase",
            "quote_reference": "quote-unit-10",
            "amount_sar": Decimal("27.00"),
            "amount_halalas": 2700,
            "currency": "SAR",
            "description": "ABCZ Silver subscription",
            "success_url": "https://example.com/payments/return/",
            "back_url": "https://example.com/checkout/silver/",
            "callback_url": "https://example.com/payments/webhook/",
        }
        data.update(overrides)
        return data

    def test_decimal_to_halalas_is_exact(self):
        self.assertEqual(validate_amounts(Decimal("27.00"), 2700), 2700)

    @patch("phonics.payments.moyasar.requests.post")
    def test_amount_mismatch_is_rejected_before_network(self, post_mock):
        with self.assertRaises(ValueError):
            create_invoice(**self.invoice_kwargs(amount_halalas=2699))
        post_mock.assert_not_called()

    @override_settings(MOYASAR_SECRET_KEY="")
    def test_missing_key_is_a_safe_configuration_error(self):
        with self.assertRaises(MoyasarConfigurationError) as caught:
            create_invoice(**self.invoice_kwargs())
        self.assertNotIn("sk_", str(caught.exception))

    @override_settings(MOYASAR_SECRET_KEY="sk_test_wrong_mode", MOYASAR_ENVIRONMENT="live")
    def test_test_key_is_rejected_in_live_environment(self):
        with self.assertRaises(MoyasarConfigurationError):
            create_invoice(**self.invoice_kwargs())

    @override_settings(MOYASAR_SECRET_KEY="sk_live_wrong_mode", MOYASAR_ENVIRONMENT="test")
    def test_live_key_is_rejected_in_test_environment(self):
        with self.assertRaises(MoyasarConfigurationError):
            create_invoice(**self.invoice_kwargs())

    @patch("phonics.payments.moyasar.requests.post")
    def test_success_response_is_validated_and_returned(self, post_mock):
        post_mock.return_value = self.valid_response()
        invoice = create_invoice(**self.invoice_kwargs())
        self.assertEqual(invoice.invoice_id, "inv_123")
        self.assertEqual(invoice.amount_halalas, 2700)
        request_kwargs = post_mock.call_args.kwargs
        self.assertEqual(request_kwargs["auth"], ("sk_test_unit_only", ""))
        self.assertEqual(request_kwargs["timeout"], (5, 15))
        self.assertFalse(request_kwargs["allow_redirects"])
        self.assertEqual(request_kwargs["json"]["metadata"], {
            "payment_order_id": "10",
            "user_id": "20",
            "plan_code": "silver",
            "operation_type": "purchase",
            "quote_reference": "quote-unit-10",
        })

    @patch("phonics.payments.moyasar.requests.post")
    def test_api_errors_are_safe_and_do_not_log_secret(self, post_mock):
        for status_code in (401, 429, 500):
            with self.subTest(status_code=status_code):
                post_mock.return_value = Mock(status_code=status_code, headers={}, json=Mock())
                with self.assertLogs("abcz.payments.moyasar", level="INFO") as logs:
                    with self.assertRaises(MoyasarAPIError) as caught:
                        create_invoice(**self.invoice_kwargs())
                output = " ".join(logs.output) + str(caught.exception)
                self.assertNotIn("sk_test_unit_only", output)
                self.assertEqual(caught.exception.status_code, status_code)

    @patch("phonics.payments.moyasar.requests.post")
    def test_network_timeout_is_wrapped_safely(self, post_mock):
        import requests
        post_mock.side_effect = requests.Timeout("contains no credentials")
        with self.assertRaises(MoyasarNetworkError):
            create_invoice(**self.invoice_kwargs())

    @patch("phonics.payments.moyasar.requests.post")
    def test_missing_invoice_id_is_rejected(self, post_mock):
        post_mock.return_value = self.valid_response(id="")
        with self.assertRaises(MoyasarInvalidResponseError):
            create_invoice(**self.invoice_kwargs())

    @patch("phonics.payments.moyasar.requests.post")
    def test_missing_checkout_url_is_rejected(self, post_mock):
        post_mock.return_value = self.valid_response(url="")
        with self.assertRaises(MoyasarInvalidResponseError):
            create_invoice(**self.invoice_kwargs())

    @patch("phonics.payments.moyasar.requests.post")
    def test_http_checkout_url_is_rejected(self, post_mock):
        post_mock.return_value = self.valid_response(url="http://checkout.moyasar.com/invoices/inv_123")
        with self.assertRaises(MoyasarUnsafeCheckoutURLError):
            create_invoice(**self.invoice_kwargs())

    @patch("phonics.payments.moyasar.requests.post")
    def test_unapproved_checkout_host_is_rejected(self, post_mock):
        post_mock.return_value = self.valid_response(url="https://evil.example/invoices/inv_123")
        with self.assertRaises(MoyasarUnsafeCheckoutURLError):
            create_invoice(**self.invoice_kwargs())

    @patch("phonics.payments.moyasar.requests.post")
    def test_response_amount_mismatch_is_rejected(self, post_mock):
        post_mock.return_value = self.valid_response(amount=1)
        with self.assertRaises(MoyasarInvalidResponseError):
            create_invoice(**self.invoice_kwargs())

    @patch("phonics.payments.moyasar.requests.post")
    def test_response_currency_mismatch_is_rejected(self, post_mock):
        post_mock.return_value = self.valid_response(currency="USD")
        with self.assertRaises(MoyasarInvalidResponseError):
            create_invoice(**self.invoice_kwargs())

    @patch("phonics.payments.moyasar.requests.get")
    def test_fetch_invoice_uses_safe_authenticated_get(self, get_mock):
        payload = {
            "id": "inv_123", "status": "paid", "amount": 2700, "currency": "SAR",
            "metadata": {"payment_order_id": "10", "user_id": "20"}, "payments": [],
        }
        response = Mock(status_code=200, headers={"X-Request-ID": "req_fetch"})
        response.json.return_value = payload
        get_mock.return_value = response
        self.assertEqual(fetch_invoice("inv_123"), payload)
        args, kwargs = get_mock.call_args
        self.assertEqual(args[0], "https://api.moyasar.com/v1/invoices/inv_123")
        self.assertEqual(kwargs["auth"], ("sk_test_unit_only", ""))
        self.assertEqual(kwargs["timeout"], (5, 15))
        self.assertFalse(kwargs["allow_redirects"])

    @patch("phonics.payments.moyasar.requests.get")
    def test_fetch_invoice_classifies_http_and_invalid_responses(self, get_mock):
        for status_code in (401, 403, 404, 429, 500):
            with self.subTest(status_code=status_code):
                get_mock.return_value = Mock(status_code=status_code, headers={})
                with self.assertRaises(MoyasarAPIError) as caught:
                    fetch_invoice("inv_123")
                self.assertEqual(caught.exception.status_code, status_code)
        response = Mock(status_code=200, headers={})
        response.json.return_value = {
            "id": "inv_123", "status": "paid", "amount": True, "currency": "SAR",
            "metadata": {}, "payments": [],
        }
        get_mock.return_value = response
        with self.assertRaises(MoyasarInvalidResponseError):
            fetch_invoice("inv_123")

    @patch("phonics.payments.moyasar.requests.get")
    def test_fetch_invoice_rejects_unsafe_stored_id_before_network(self, get_mock):
        with self.assertRaises(MoyasarInvalidResponseError):
            fetch_invoice("../invoice")
        get_mock.assert_not_called()
