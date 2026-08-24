from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse


@override_settings(DISABLE_AUTO_SEED=True)
class LandingPageTests(TestCase):
    def test_root_renders_the_marketing_landing_page(self):
        response = self.client.get(reverse("index"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "landing.html")
        self.assertContains(response, "<title>Smart Learning | تأسيس اللغة الإنجليزية للأطفال</title>")
        self.assertContains(response, 'rel="canonical" href="https://www.smartlearningksa.com/"')
        self.assertContains(response, "static/css/landing.css")
        self.assertContains(response, "static/js/landing.js")
        self.assertNotContains(response, "letters/letters.css")
        self.assertNotContains(response, "bird_tutor.js")

    def test_letters_experience_remains_available_at_its_own_url(self):
        response = self.client.get(reverse("letters"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "letters.html")
        self.assertContains(response, "letters/letters.css")

    def test_landing_ctas_use_existing_routes(self):
        response = self.client.get(reverse("index"))

        for route_name in (
            "placement_test", "levels", "pricing", "login", "register", "letters",
            "sounds", "cvc_reading", "level_four", "curriculum", "privacy", "terms",
        ):
            with self.subTest(route_name=route_name):
                self.assertContains(response, reverse(route_name))

    def test_landing_has_the_existing_letters_whatsapp_contact_link(self):
        response = self.client.get(reverse("index"))

        self.assertContains(response, 'href="https://wa.me/966530637886"')
        self.assertContains(response, 'rel="noopener noreferrer"')
        self.assertContains(response, 'class="landing-whatsapp-contact"')
        self.assertNotContains(response, '0530 637 886')

    def test_landing_does_not_expose_test_answers_or_sensitive_payment_content(self):
        html = self.client.get(reverse("index")).content.decode("utf-8").lower()

        for forbidden in ('"answer"', "moyasar", "cvv", "secret", "sk_"):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, html)

    def test_authenticated_navigation_uses_existing_learning_and_profile_routes(self):
        user = get_user_model().objects.create_user(
            username="landing-user", password="landing-pass-123"
        )
        self.client.force_login(user)

        response = self.client.get(reverse("index"))

        self.assertContains(response, reverse("profile_dashboard"))
        self.assertContains(response, reverse("letters"))
        self.assertNotContains(response, reverse("login"))
        self.assertNotContains(response, reverse("register"))
