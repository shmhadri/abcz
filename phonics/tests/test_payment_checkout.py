import shutil
import tempfile
from io import BytesIO
from decimal import Decimal

from django.contrib import admin as django_admin
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from PIL import Image

from phonics.admin import PaymentOrderAdmin
from phonics.models import (
    BankTransferProof,
    PaymentOrder,
    UserSubscription,
    activate_subscription_from_payment,
)
from phonics.views import PLAN_LEVEL_THREE, get_feature_keys


@override_settings(DISABLE_AUTO_SEED=True)
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

    def test_moyasar_order_creation_does_not_activate_subscription(self):
        response = self.client.post(reverse("create_payment_order", args=["silver", "moyasar"]))

        self.assertEqual(response.status_code, 302)
        order = PaymentOrder.objects.get()
        self.assertEqual(order.method, PaymentOrder.Method.MOYASAR_CARD)
        self.assertEqual(order.provider, PaymentOrder.Provider.MOYASAR)
        self.assertEqual(order.status, PaymentOrder.Status.PENDING)
        self.assertEqual(order.amount_halalas, 2700)
        self.assertEqual(UserSubscription.objects.count(), 0)
        self.assertFalse(self.user.groups.filter(name="Silver").exists())

    def test_stcpay_order_creation_does_not_activate_subscription(self):
        response = self.client.post(reverse("create_payment_order", args=["silver", "stcpay"]))

        self.assertEqual(response.status_code, 302)
        order = PaymentOrder.objects.get()
        self.assertEqual(order.method, PaymentOrder.Method.MOYASAR_STCPAY)
        self.assertEqual(order.provider, PaymentOrder.Provider.MOYASAR)
        self.assertEqual(order.status, PaymentOrder.Status.PENDING)
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
            "sender_name": "Payment User", "bank_name": "Test Bank",
            "transferred_at": timezone.localdate().isoformat(), "amount_sar": "27.00", "receipt_file": receipt,
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

        self.assertEqual(response.status_code, 202)
        order.refresh_from_db()
        self.assertEqual(order.status, PaymentOrder.Status.PENDING)
        self.assertEqual(order.provider_payment_id, "pay_123")
        self.assertEqual(UserSubscription.objects.count(), 0)

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
