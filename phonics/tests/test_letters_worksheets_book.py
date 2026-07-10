from pathlib import Path

from django.test import TestCase, override_settings


@override_settings(DISABLE_AUTO_SEED=True)
class LettersWorksheetsBookTests(TestCase):
    def test_letters_page_exposes_level_one_disabled_worksheet_policy(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "window.LEVEL_ONE_DISABLED_FEATURES")
        self.assertContains(response, "letterWorksheets: true")
        self.assertContains(response, "worksheetBook: true")
        self.assertContains(response, 'id="letterWorksheetBtn"', html=False)
        self.assertContains(response, 'id="letterWorksheetBtn" type="button" hidden', html=False)

    def test_letters_worksheets_book_page_is_blocked_in_level_one_policy(self):
        response = self.client.get("/letters/worksheets-book/")

        self.assertEqual(response.status_code, 403)
        html = response.content.decode("utf-8")
        self.assertNotIn("English Letters Worksheets Book", html)
        self.assertNotIn("Letter A", html)
        self.assertNotIn("Letter Z", html)
        self.assertNotIn("Certificate of Completion", html)

    def test_letters_worksheets_book_does_not_render_book_pages(self):
        response = self.client.get("/letters/worksheets-book/")
        html = response.content.decode("utf-8")

        self.assertEqual(response.status_code, 403)
        self.assertEqual(html.count('class="book-page letter-worksheet-page"'), 0)
        self.assertEqual(html.count("data-book-letter="), 0)

    def test_letters_worksheets_book_static_assets_exist(self):
        css = Path("static/css/letters_worksheets_book.css")
        js = Path("static/js/letters_worksheets_book.js")

        self.assertTrue(css.exists())
        self.assertTrue(js.exists())
        self.assertIn("@media print", css.read_text(encoding="utf-8"))
        script = js.read_text(encoding="utf-8")
        self.assertIn("english_letters_worksheets_book.pdf", script)
        self.assertIn("english_letters_worksheets_book.doc", script)
