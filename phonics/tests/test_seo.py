from xml.etree import ElementTree
import re

from django.test import TestCase, override_settings
from django.urls import reverse


CANONICAL_ORIGIN = "https://www.smartlearningksa.com"
PUBLIC_ROUTES = {
    "index": "/",
    "placement_test": "/placement-test/",
    "levels": "/levels/",
    "pricing": "/pricing/",
    "letters": "/letters/",
    "curriculum": "/curriculum/",
    "about": "/about/",
    "guide": "/guide/",
    "privacy": "/privacy/",
    "terms": "/terms/",
    "seo_phonics": "/phonics/",
    "seo_cvc_reading_guide": "/cvc-reading-guide/",
    "seo_english_reading": "/english-reading-for-kids/",
    "seo_english_vocabulary": "/english-vocabulary-for-kids/",
    "seo_english_grammar": "/english-grammar-for-kids/",
    "seo_english_worksheets": "/english-worksheets-for-kids/",
    "seo_letter_sounds_guide": "/english-letter-sounds-guide/",
    "seo_cvc_words_guide": "/cvc-words-for-kids/",
    "seo_word_families_guide": "/word-families-for-kids/",
    "seo_reading_learning_guide": "/how-to-teach-english-reading-for-kids/",
}


@override_settings(DISABLE_AUTO_SEED=True)
class TechnicalSeoTests(TestCase):
    def test_sitemap_lists_only_canonical_public_pages(self):
        response = self.client.get(reverse("sitemap"), secure=True)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response["Content-Type"].startswith("application/xml"))
        root = ElementTree.fromstring(response.content)
        namespace = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        urls = {node.text for node in root.findall("sm:url/sm:loc", namespace)}
        expected = {f"{CANONICAL_ORIGIN}{path}" for path in PUBLIC_ROUTES.values()}

        self.assertEqual(urls, expected)
        for forbidden in ("/admin/", "/checkout/", "/payments/", "/api/", "/profile/"):
            self.assertFalse(any(forbidden in url for url in urls))

    def test_robots_allows_public_content_and_references_the_canonical_sitemap(self):
        response = self.client.get(reverse("robots_txt"), secure=True)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response["Content-Type"].startswith("text/plain"))
        content = response.content.decode("utf-8")
        self.assertIn("User-agent: *", content)
        self.assertIn("Allow: /", content)
        self.assertIn(f"Sitemap: {CANONICAL_ORIGIN}/sitemap.xml", content)
        for path in ("/admin/", "/accounts/", "/profile/", "/checkout/", "/payments/", "/api/"):
            self.assertIn(f"Disallow: {path}", content)

    def test_existing_google_verification_url_is_unchanged(self):
        response = self.client.get("/googlea532a5ae726057b6.html", secure=True)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.content.decode("utf-8"),
            "google-site-verification: googlea532a5ae726057b6.html",
        )

    def test_public_pages_have_canonical_title_and_description(self):
        titles = set()
        descriptions = set()
        for route_name, path in PUBLIC_ROUTES.items():
            with self.subTest(route_name=route_name):
                response = self.client.get(path, secure=True)
                self.assertEqual(response.status_code, 200)
                html = response.content.decode("utf-8")
                self.assertIn(f'<link rel="canonical" href="{CANONICAL_ORIGIN}{path}">', html)
                self.assertIn('<meta name="robots" content="index, follow">', html)
                title_match = re.search(r"<title>(.*?)</title>", html, re.DOTALL)
                description_match = re.search(r'<meta name="description" content="([^"]+)">', html)
                self.assertIsNotNone(title_match)
                self.assertIsNotNone(description_match)
                self.assertEqual(len(re.findall(r"<h1(?:\s|>)", html, re.IGNORECASE)), 1)
                self.assertNotIn(title_match.group(1), titles)
                self.assertNotIn(description_match.group(1), descriptions)
                self.assertIn("brand/favicon", html)
                self.assertIn("brand/apple-touch-icon", html)
                og_url_match = re.search(r'<meta property="og:url" content="([^"]+)">', html)
                if og_url_match:
                    self.assertEqual(og_url_match.group(1), f"{CANONICAL_ORIGIN}{path}")
                titles.add(title_match.group(1))
                descriptions.add(description_match.group(1))

    def test_root_icon_endpoints_return_valid_icon_files(self):
        expected = {
            "favicon": (b"\x00\x00\x01\x00", "image/x-icon"),
            "apple_touch_icon": (b"\x89PNG\r\n\x1a\n", "image/png"),
            "apple_touch_icon_precomposed": (b"\x89PNG\r\n\x1a\n", "image/png"),
        }
        for route_name, (signature, content_type) in expected.items():
            with self.subTest(route_name=route_name):
                response = self.client.get(reverse(route_name), secure=True)
                self.assertEqual(response.status_code, 200)
                self.assertTrue(response["Content-Type"].startswith(content_type))
                self.assertTrue(b"".join(response.streaming_content).startswith(signature))

    def test_homepage_includes_organization_and_website_schema(self):
        response = self.client.get(reverse("index"), secure=True)
        html = response.content.decode("utf-8")

        self.assertIn('type="application/ld+json"', html)
        self.assertIn('"@type": "Organization"', html)
        self.assertIn('"@type": "WebSite"', html)

    def test_learning_path_landings_are_public_and_link_to_a_conversion_action(self):
        for route_name in (
            "seo_phonics",
            "seo_cvc_reading_guide",
            "seo_english_reading",
            "seo_english_vocabulary",
            "seo_english_grammar",
            "seo_english_worksheets",
        ):
            with self.subTest(route_name=route_name):
                response = self.client.get(reverse(route_name), secure=True)
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, "<h1>")
                self.assertContains(response, reverse("placement_test"))
                self.assertContains(response, reverse("pricing"))

    def test_content_guides_are_complete_and_include_visible_breadcrumb_schema(self):
        titles = set()
        related_routes = {
            "seo_letter_sounds_guide": ("seo_phonics", "seo_cvc_words_guide"),
            "seo_cvc_words_guide": ("seo_cvc_reading_guide", "seo_word_families_guide"),
            "seo_word_families_guide": ("seo_cvc_words_guide", "seo_reading_learning_guide"),
            "seo_reading_learning_guide": ("seo_letter_sounds_guide", "seo_english_reading"),
        }
        for route_name, expected_links in related_routes.items():
            with self.subTest(route_name=route_name):
                response = self.client.get(reverse(route_name), secure=True)
                html = response.content.decode("utf-8")
                self.assertEqual(response.status_code, 200)
                self.assertIn("<h1>", html)
                self.assertIn("نصيحة لولي الأمر", html)
                self.assertIn('"@type": "BreadcrumbList"', html)
                self.assertIn("تعلم الإنجليزية للأطفال", html)
                self.assertIn(f'<link rel="canonical" href="{CANONICAL_ORIGIN}{PUBLIC_ROUTES[route_name]}">', html)
                self.assertIn('meta name="description"', html)
                self.assertIn('<meta name="robots" content="index, follow">', html)
                for expected_route in expected_links:
                    self.assertIn(reverse(expected_route), html)

                title = html.split("<title>", 1)[1].split("</title>", 1)[0]
                self.assertNotIn(title, titles)
                titles.add(title)

    def test_curriculum_links_to_the_public_learning_guides(self):
        response = self.client.get(reverse("curriculum"), secure=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse("seo_phonics"))
        self.assertContains(response, reverse("seo_reading_learning_guide"))

    def test_pricing_remains_available_to_social_crawlers(self):
        for user_agent in ("facebookexternalhit/1.1", "Facebot", "Twitterbot"):
            with self.subTest(user_agent=user_agent):
                response = self.client.get(reverse("pricing"), secure=True, HTTP_USER_AGENT=user_agent)
                self.assertEqual(response.status_code, 200)

    def test_original_subscription_gated_learning_pages_remain_protected(self):
        for route_name in (
            "sounds",
            "cvc_reading",
            "level_four_reading",
            "vocabulary_foundation",
            "grammar_foundation",
            "worksheets_center",
        ):
            with self.subTest(route_name=route_name):
                response = self.client.get(reverse(route_name), secure=True)
                self.assertEqual(response.status_code, 403)
