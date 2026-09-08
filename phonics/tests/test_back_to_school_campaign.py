from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse

from phonics.campaigns import campaign_price
from phonics.plans import PLAN_CATALOG
from phonics.subscriptions import quote_plan_purchase
from phonics.tests.subscription_helpers import grant_active_subscription
from phonics.views import CHECKOUT_PLANS, create_payment_order_for_plan


@override_settings(DISABLE_AUTO_SEED=True, BACK_TO_SCHOOL_ENABLED=True)
class BackToSchoolCampaignTests(TestCase):
    expected_prices = {
        "basic": ("19.00", "15"), "silver": ("27.00", "21"),
        "vip": ("39.00", "31"), "diamond": ("50.00", "40"),
        "level_3": ("15.00", "12"), "level_4": ("15.00", "12"),
    }

    def setUp(self):
        self.user = User.objects.create_user(username="campaign", password="StrongPass123!")

    def test_catalog_prices_use_decimal_and_round_down(self):
        for code, (original, final) in self.expected_prices.items():
            with self.subTest(code=code):
                price = campaign_price(PLAN_CATALOG[code]["price"])
                self.assertEqual(price.original_price, Decimal(original))
                self.assertEqual(price.final_price, Decimal(final))
                self.assertIsInstance(price.final_price, Decimal)

    def test_disabled_campaign_restores_original_price(self):
        with self.settings(BACK_TO_SCHOOL_ENABLED=False):
            self.assertEqual(campaign_price(Decimal("39.00")).final_price, Decimal("39.00"))

    def test_checkout_and_order_use_server_side_discounted_amounts(self):
        for code, (_, final) in self.expected_prices.items():
            with self.subTest(code=code):
                quote = quote_plan_purchase(self.user, code)
                self.assertEqual(quote.amount_due, Decimal(final))
                order = create_payment_order_for_plan(self.user, CHECKOUT_PLANS[code], "moyasar", quote=quote)
                self.assertEqual(order.amount_halalas, int(final) * 100)

    def test_pricing_and_checkout_show_whole_sar_campaign_details(self):
        pricing = self.client.get(reverse("pricing"))
        self.assertContains(pricing, "عرض اليوم الوطني")
        self.assertNotContains(pricing, "عرض العودة للمدارس")
        self.assertContains(pricing, "خصم 20%")
        self.client.force_login(self.user)
        checkout = self.client.get(reverse("checkout", args=["vip"]))
        self.assertContains(checkout, "عرض اليوم الوطني")
        self.assertContains(checkout, "السعر الأصلي")
        self.assertContains(checkout, "39 ريال")
        self.assertContains(checkout, "31 ريال")

    def test_word_games_are_available_to_every_active_paid_subscription(self):
        for code in self.expected_prices:
            with self.subTest(code=code):
                user = User.objects.create_user(username=f"word-{code}", password="StrongPass123!")
                grant_active_subscription(user, code)
                self.client.force_login(user)
                self.assertEqual(self.client.get(reverse("games_center")).status_code, 200)
                self.assertEqual(self.client.get(reverse("external_games_by_letter", args=["A"])).status_code, 200)

    def test_word_games_remain_locked_without_active_subscription(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(reverse("games_center")).status_code, 403)
        self.assertEqual(self.client.get(reverse("external_games_by_letter", args=["A"])).status_code, 403)
