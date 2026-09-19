from decimal import Decimal

from django.conf import settings
from django.contrib.auth.models import User
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from phonics.models import PaymentOrder


PIXEL_ID = "DAA8AD3C77UES9749L1G"


@override_settings(
    TIKTOK_PIXEL_ID=PIXEL_ID,
    DISABLE_AUTO_SEED=True,
    RATE_LIMIT_REGISTER=100,
)
class TikTokTrackingTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="analytics-user",
            password="StrongPass123!",
        )

    def assert_base_pixel_once(self, response):
        html = response.content.decode("utf-8")
        self.assertEqual(html.count(PIXEL_ID), 1)
        self.assertEqual(html.count("tiktok-pixel-config"), 1)
        self.assertEqual(html.count("js/tiktok-pixel.js"), 1)
        self.assertEqual(html.count("js/tiktok-events.js"), 1)
        self.assertEqual(html.count("js/tiktok-consent.js"), 1)
        self.assertEqual(html.count("tiktok-consent-banner"), 1)
        self.assertNotIn("ttq.identify", html)
        self.assertNotIn("phone_number", html)

    def create_order(self, status, *, payment_id=None, activated=False):
        now = timezone.now()
        return PaymentOrder.objects.create(
            user=self.user,
            plan_code="silver",
            plan_name="Silver",
            duration_days=30,
            amount_halalas=2700,
            amount_sar=Decimal("27.00"),
            currency="SAR",
            status=status,
            method=PaymentOrder.Method.MOYASAR_CARD,
            provider=PaymentOrder.Provider.MOYASAR,
            payment_environment=PaymentOrder.Environment.TEST,
            moyasar_invoice_id=f"invoice-{status}-{PaymentOrder.objects.count()}",
            moyasar_payment_id=payment_id,
            provider_payment_id=payment_id or "",
            paid_at=now if status == PaymentOrder.Status.PAID else None,
            activated_at=now if activated else None,
        )

    def test_pixel_is_enabled_once_and_pageview_bootstrap_exists(self):
        for url in (reverse("letters"), reverse("pricing"), reverse("register"), reverse("index")):
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)
                self.assert_base_pixel_once(response)

        self.client.force_login(self.user)
        self.assert_base_pixel_once(self.client.get(reverse("checkout", args=["silver"])))

        pixel_source = (settings.BASE_DIR / "static" / "js" / "tiktok-pixel.js").read_text()
        self.assertIn("ttq.page()", pixel_source)
        self.assertIn("smartlearning_analytics_marketing_consent_v1", pixel_source)
        self.assertIn('=== "granted"', pixel_source)
        self.assertNotIn("ttq.identify(", pixel_source)

        consent_source = (settings.BASE_DIR / "static" / "js" / "tiktok-consent.js").read_text()
        self.assertIn('saveChoice("granted")', consent_source)
        self.assertIn('saveChoice("denied")', consent_source)
        self.assertIn("initializeTikTokPixel", consent_source)

    @override_settings(TIKTOK_PIXEL_ID="")
    def test_empty_pixel_setting_disables_rendering(self):
        response = self.client.get(reverse("pricing"))
        self.assertNotContains(response, "tiktok-pixel-config")
        self.assertNotContains(response, "js/tiktok-pixel.js")

    def test_pricing_view_content_uses_backend_catalog_values(self):
        response = self.client.get(reverse("pricing"))
        self.assertContains(response, "ViewContent")
        self.assertContains(response, '"content_id": "basic"')
        self.assertContains(response, '"content_name": "Basic"')
        self.assertContains(response, '"currency": "SAR"')

    def test_valid_checkout_tracks_view_and_initiation_with_server_quote(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("checkout", args=["silver"]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "ViewContent")
        self.assertContains(response, "InitiateCheckout")
        self.assertContains(response, '"content_id": "silver"')
        self.assertContains(response, '"content_name": "Silver"')
        self.assertContains(response, '"value": 27.0')
        self.assertContains(response, '"currency": "SAR"')

        invalid = self.client.get(reverse("checkout", args=["unknown-plan"]))
        self.assertEqual(invalid.status_code, 404)
        self.assertNotContains(invalid, "InitiateCheckout", status_code=404)

    def test_registration_tracks_only_after_success_and_only_once(self):
        get_response = self.client.get(reverse("register"))
        self.assertNotContains(get_response, "CompleteRegistration")

        invalid = self.client.post(reverse("register"), {})
        self.assertEqual(invalid.status_code, 200)
        self.assertNotContains(invalid, "CompleteRegistration")

        response = self.client.post(reverse("register"), {
            "username": "new-analytics-user",
            "email": "new-analytics@example.com",
            "student_name": "Analytics Student",
            "parent_phone": "0500000000",
            "city": "Riyadh",
            "password1": "StrongPass123!",
            "password2": "StrongPass123!",
        })
        self.assertEqual(response.status_code, 302)

        destination = self.client.get(response["Location"])
        self.assertContains(destination, "CompleteRegistration")
        refreshed = self.client.get(response["Location"])
        self.assertNotContains(refreshed, "CompleteRegistration")

    def test_purchase_requires_confirmed_activation_and_deduplicates_globally(self):
        self.client.force_login(self.user)
        for status in (
            PaymentOrder.Status.INITIATED,
            PaymentOrder.Status.PENDING,
            PaymentOrder.Status.FAILED,
            PaymentOrder.Status.CANCELED,
        ):
            with self.subTest(status=status):
                order = self.create_order(status)
                response = self.client.get(reverse("payment_success"), {"order": order.id})
                self.assertNotContains(response, reverse("tiktok_purchase", args=[order.id]))

        paid = self.create_order(
            PaymentOrder.Status.PAID,
            payment_id="pay-confirmed-1",
            activated=True,
        )
        claim_url = reverse("tiktok_purchase", args=[paid.id])
        page = self.client.get(reverse("payment_success"), {"order": paid.id})
        self.assertContains(page, claim_url)
        self.assertNotContains(page, '"name": "Purchase"')
        self.assertNotContains(page, "pay-confirmed-1")

        consent_headers = {"HTTP_X_ANALYTICS_MARKETING_CONSENT": "granted"}
        self.assertEqual(self.client.post(claim_url).status_code, 204)
        first = self.client.post(claim_url, **consent_headers)
        self.assertEqual(first.status_code, 200)
        self.assertEqual(first.json()["event"]["name"], "Purchase")
        self.assertEqual(first.json()["event"]["payload"]["value"], 27.0)
        self.assertNotContains(first, "pay-confirmed-1")
        self.assertNotContains(first, '"name": "CompletePayment"')

        paid.refresh_from_db()
        self.assertIsNotNone(paid.tiktok_purchase_claimed_at)
        self.assertEqual(self.client.post(claim_url, **consent_headers).status_code, 204)
        self.assertNotContains(
            self.client.get(reverse("payment_success"), {"order": paid.id}),
            claim_url,
        )

    def test_success_query_without_owned_verified_order_never_offers_payment_claim(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("payment_success"))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "/analytics/tiktok/purchase/")

    def test_other_user_cannot_claim_purchase(self):
        paid = self.create_order(
            PaymentOrder.Status.PAID,
            payment_id="pay-owned-1",
            activated=True,
        )
        other = User.objects.create_user(username="other-user", password="StrongPass123!")
        self.client.force_login(other)
        response = self.client.post(
            reverse("tiktok_purchase", args=[paid.id]),
            HTTP_X_ANALYTICS_MARKETING_CONSENT="granted",
        )
        self.assertEqual(response.status_code, 204)
        paid.refresh_from_db()
        self.assertIsNone(paid.tiktok_purchase_claimed_at)

    def test_purchase_claim_requires_csrf_cookie(self):
        paid = self.create_order(
            PaymentOrder.Status.PAID,
            payment_id="pay-csrf-1",
            activated=True,
        )
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.user)
        claim_url = reverse("tiktok_purchase", args=[paid.id])

        self.assertEqual(
            client.post(claim_url, HTTP_X_ANALYTICS_MARKETING_CONSENT="granted").status_code,
            403,
        )
        page = client.get(reverse("payment_success"), {"order": paid.id})
        token = page.cookies["csrftoken"].value
        self.assertEqual(
            client.post(
                claim_url,
                HTTP_X_ANALYTICS_MARKETING_CONSENT="granted",
                HTTP_X_CSRFTOKEN=token,
            ).status_code,
            200,
        )

    def test_placement_test_uses_custom_start_and_complete_events(self):
        response = self.client.get(reverse("placement_test"))
        self.assertEqual(response.status_code, 200)
        self.assert_base_pixel_once(response)

        source = (settings.BASE_DIR / "static" / "js" / "placement_test.js").read_text()
        self.assertIn('trackTikTokEvent?.("StartTest"', source)
        self.assertIn('trackTikTokEvent?.("CompleteTest"', source)
        self.assertIn("intentional custom events", source)
        self.assertLess(source.index("renderResult(result);"), source.index("trackTestComplete(result);"))
