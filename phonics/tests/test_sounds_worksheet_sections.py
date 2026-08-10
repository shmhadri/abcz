"""Regression tests for the Level 2 (sounds) worksheet page.

The worksheet page renders every lesson as a `<section data-sheet="...">` and
builds its filter bar from a `sheetFilters` list in JavaScript. Selecting a
filter adds `.filtering` to the sheet and `.active-sheet` to matching sections;
`.sheet.filtering > section:not(.active-sheet)` is then hidden.

That design has one sharp edge: a filter key with no matching section hides
*every* section and leaves the learner staring at a blank page. These tests pin
the invariant that each filter button has a section behind it, and that the
worksheets generated from the vocabulary and grammar data are actually present.
"""
import re
from pathlib import Path

from django.contrib.auth import get_user_model
from django.test import SimpleTestCase, TestCase, override_settings
from django.utils.html import escape

from phonics.plans import PLAN_VIP
from phonics.tests.subscription_helpers import grant_active_subscription
from phonics.views import (
    FOUNDATION_VOCABULARY_CATEGORIES,
    LEVEL_TWO_GRAMMAR_LESSONS,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
WORKSHEET_TEMPLATE = PROJECT_ROOT / "templates" / "sounds_worksheet.html"


def template_text():
    return WORKSHEET_TEMPLATE.read_text(encoding="utf-8", errors="ignore")


def declared_filter_keys(html):
    """Filter keys the JavaScript builds nav buttons from, in order."""
    block = re.search(r"const sheetFilters\s*=\s*\[(.*?)\];", html, re.DOTALL)
    if not block:
        return []
    return re.findall(r'key:\s*"([^"]+)"', block.group(1))


def section_keys(html):
    """data-sheet values that exist as real sections."""
    return set(re.findall(r'<section[^>]*data-sheet="([^"]+)"', html))


class SoundsWorksheetDataTests(SimpleTestCase):
    """Checks that need no rendering: the worksheet keys in the source data.

    Structural checks about sections deliberately live in the render tests
    below. Several sections are produced by `{% for %}` loops whose data-sheet
    value is a template variable, so the raw template text cannot answer
    "does a section exist for this key?" — only the rendered page can.
    """

    def test_worksheet_keys_in_data_are_unique(self):
        keys = [c["worksheet"] for c in FOUNDATION_VOCABULARY_CATEGORIES]
        keys += [lesson["worksheet"] for lesson in LEVEL_TWO_GRAMMAR_LESSONS]
        duplicates = sorted({key for key in keys if keys.count(key) > 1})
        self.assertEqual(duplicates, [], "two lessons claim the same worksheet key")

    def test_every_data_entry_declares_a_worksheet_key(self):
        missing = [
            entry.get("id", "?")
            for entry in list(FOUNDATION_VOCABULARY_CATEGORIES) + list(LEVEL_TWO_GRAMMAR_LESSONS)
            if not entry.get("worksheet")
        ]
        self.assertEqual(missing, [], "data entries with no worksheet key are unreachable")

    def test_filter_keys_are_unique(self):
        keys = declared_filter_keys(template_text())
        duplicates = sorted({key for key in keys if keys.count(key) > 1})
        self.assertEqual(duplicates, [], "duplicate filter keys produce duplicate buttons")

    def test_all_filter_is_first(self):
        keys = declared_filter_keys(template_text())
        self.assertTrue(keys, "sheetFilters list was not found")
        self.assertEqual(keys[0], "all")


@override_settings(DISABLE_AUTO_SEED=True)
class SoundsWorksheetRenderTests(TestCase):
    """The rendered page must contain a usable worksheet for every filter."""

    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(
            username="worksheet-tester",
            email="worksheet-tester@example.com",
            password="worksheet-pass-123",
        )
        grant_active_subscription(self.user, PLAN_VIP)
        self.client.login(username="worksheet-tester", password="worksheet-pass-123")

    def get_page(self):
        response = self.client.get("/sounds/worksheet/")
        self.assertEqual(response.status_code, 200)
        return response.content.decode("utf-8")

    def test_page_renders_for_entitled_user(self):
        html = self.get_page()
        self.assertIn("ورقة عمل الصوتيات", html)
        self.assertNotIn("{%", html)
        self.assertNotIn("{{", html)

    def test_rendered_page_has_a_section_for_every_filter(self):
        # A filter with no section adds .filtering while nothing gets
        # .active-sheet, so every section is hidden and the learner sees a
        # blank page.
        html = self.get_page()
        filters = [key for key in declared_filter_keys(html) if key != "all"]
        sections = section_keys(html)
        dead = [key for key in filters if key not in sections]
        self.assertEqual(dead, [], "filters with no rendered section: " + ", ".join(dead))

    def test_every_rendered_section_is_reachable_from_a_filter(self):
        html = self.get_page()
        filters = set(declared_filter_keys(html))
        orphans = sorted(section_keys(html) - filters)
        self.assertEqual(
            orphans,
            [],
            "worksheets exist but no button reaches them: " + ", ".join(orphans),
        )

    def test_every_vocabulary_category_renders_a_section(self):
        sections = section_keys(self.get_page())
        missing = [
            category["worksheet"]
            for category in FOUNDATION_VOCABULARY_CATEGORIES
            if category["worksheet"] not in sections
        ]
        self.assertEqual(missing, [], "vocabulary categories without a worksheet")

    def test_every_grammar_lesson_renders_a_section(self):
        sections = section_keys(self.get_page())
        missing = [
            lesson["worksheet"]
            for lesson in LEVEL_TWO_GRAMMAR_LESSONS
            if lesson["worksheet"] not in sections
        ]
        self.assertEqual(missing, [], "grammar lessons without a worksheet")

    def test_vocabulary_worksheets_render_their_words(self):
        html = self.get_page()
        for category in FOUNDATION_VOCABULARY_CATEGORIES:
            key = category["worksheet"]
            with self.subTest(worksheet=key):
                match = re.search(
                    rf'<section[^>]*data-sheet="{re.escape(key)}"(.*?)</section>',
                    html,
                    re.DOTALL,
                )
                self.assertIsNotNone(match, f"no section rendered for {key}")
                body = match.group(1)
                # The first few words of the category must appear in its worksheet.
                for word in [w["word"] for w in category["words"][:3]]:
                    self.assertIn(word, body, f"{key} worksheet is missing '{word}'")

    def test_grammar_worksheets_render_their_terms(self):
        html = self.get_page()
        for lesson in LEVEL_TWO_GRAMMAR_LESSONS:
            key = lesson["worksheet"]
            with self.subTest(worksheet=key):
                match = re.search(
                    rf'<section[^>]*data-sheet="{re.escape(key)}"(.*?)</section>',
                    html,
                    re.DOTALL,
                )
                self.assertIsNotNone(match, f"no section rendered for {key}")
                body = match.group(1)
                # Django escapes apostrophes, so compare against escaped text.
                self.assertIn(escape(lesson["structure"]), body)
                first_group = lesson["groups"][0]
                self.assertIn(escape(first_group["entries"][0]["term"]), body)

    def test_every_worksheet_section_has_a_heading(self):
        html = self.get_page()
        # The print controls attach to each section's <h2>; a section without one
        # silently loses its "print this lesson" button.
        for match in re.finditer(
            r'<section[^>]*data-sheet="([^"]+)"(.*?)</section>', html, re.DOTALL
        ):
            with self.subTest(worksheet=match.group(1)):
                self.assertIn("<h2", match.group(2))

    def test_worksheet_is_blocked_without_entitlement(self):
        self.client.logout()
        response = self.client.get("/sounds/worksheet/")
        self.assertNotEqual(response.status_code, 200)
