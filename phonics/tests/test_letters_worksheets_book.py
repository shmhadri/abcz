from pathlib import Path
from io import BytesIO
from zipfile import ZipFile

import fitz
from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from pypdf import PdfReader

from phonics.models import StudentProfile
from phonics.tests.subscription_helpers import grant_active_subscription


@override_settings(DISABLE_AUTO_SEED=True)
class LettersWorksheetsBookTests(TestCase):
    def login_plan_user(self, plan_name="VIP"):
        user = User.objects.create_user(username=f"letters-book-{plan_name.lower()}", password="StrongPass123!")
        StudentProfile.objects.create(user=user, student_name=f"Letters Book {plan_name}")
        grant_active_subscription(user, plan_name.lower())
        self.client.force_login(user)
        return user

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

    def test_letters_worksheets_book_downloads_are_blocked_without_book_feature(self):
        for path in [
            "/letters/worksheets-book/pdf/",
            "/letters/worksheets-book/word/",
        ]:
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 403)

    def test_letters_worksheets_book_does_not_render_book_pages(self):
        response = self.client.get("/letters/worksheets-book/")
        html = response.content.decode("utf-8")

        self.assertEqual(response.status_code, 403)
        self.assertEqual(html.count('class="book-page letter-worksheet-page"'), 0)
        self.assertEqual(html.count("data-book-letter="), 0)

    def test_vip_book_page_exposes_working_toolbar_controls(self):
        self.login_plan_user("VIP")

        response = self.client.get("/letters/worksheets-book/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'href="/"')
        self.assertContains(response, 'id="printLettersBook"')
        self.assertContains(response, 'id="downloadLettersBookPdf"')
        self.assertContains(response, 'href="/letters/worksheets-book/pdf/"')
        self.assertContains(response, 'id="downloadLettersBookWord"')
        self.assertContains(response, 'href="/letters/worksheets-book/word/"')
        self.assertContains(response, "letters_worksheets_book.js")
        self.assertNotContains(response, "html2pdf.bundle.min.js")
        self.assertContains(response, "English Letters Worksheets Book")
        self.assertContains(response, "Letter A")
        self.assertContains(response, "Letter Z")

    def test_vip_word_download_contains_full_a_to_z_book(self):
        self.login_plan_user("VIP")

        response = self.client.get("/letters/worksheets-book/word/")
        docx_bytes = bytes(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response["Content-Type"],
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
        self.assertIn('filename="english_letters_worksheets_book.docx"', response["Content-Disposition"])
        self.assertTrue(docx_bytes.startswith(b"PK"))
        self.assertGreater(len(docx_bytes), 7000)

        with ZipFile(BytesIO(docx_bytes)) as archive:
            names = set(archive.namelist())
            self.assertIn("word/document.xml", names)
            self.assertIn("word/styles.xml", names)
            document_xml = archive.read("word/document.xml").decode("utf-8")

        self.assertIn("English Letters Worksheets Book", document_xml)
        self.assertIn("Trace and Write:", document_xml)
        self.assertIn("Trace the Words:", document_xml)
        self.assertIn("Find and Circle the letter", document_xml)
        self.assertNotIn("Certificate of Completion", document_xml)
        self.assertEqual(document_xml.count('<w:br w:type="page"/>'), 26)
        for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            self.assertIn(f"Letter {letter} Worksheet", document_xml)

    def test_vip_pdf_download_contains_full_a_to_z_book(self):
        self.login_plan_user("VIP")

        response = self.client.get("/letters/worksheets-book/pdf/")
        pdf_bytes = bytes(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")
        self.assertIn('filename="english_letters_worksheets_book.pdf"', response["Content-Disposition"])
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))
        self.assertGreater(len(pdf_bytes), 10000)

        reader = PdfReader(BytesIO(pdf_bytes))
        self.assertEqual(len(reader.pages), 27)
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
        self.assertIn("English Letters Worksheets Book", text)
        for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            self.assertIn(f"Letter {letter}", text)

        document = fitz.open(stream=pdf_bytes, filetype="pdf")
        for page_index in [0, 1, 26]:
            pixmap = document.load_page(page_index).get_pixmap(matrix=fitz.Matrix(0.25, 0.25), alpha=False)
            samples = pixmap.samples
            pixels = pixmap.width * pixmap.height
            nonwhite = sum(
                1
                for index in range(0, len(samples), 3)
                if samples[index] < 245 or samples[index + 1] < 245 or samples[index + 2] < 245
            )
            self.assertGreater(nonwhite / pixels, 0.02)

    def test_letters_worksheets_book_static_assets_exist(self):
        css = Path("static/css/letters_worksheets_book.css")
        js = Path("static/js/letters_worksheets_book.js")

        self.assertTrue(css.exists())
        self.assertTrue(js.exists())
        self.assertIn("@media print", css.read_text(encoding="utf-8"))
        script = js.read_text(encoding="utf-8")
        self.assertIn('getElementById("printLettersBook")', script)
        self.assertIn("window.print()", script)
        self.assertNotIn("html2pdf", script)
        self.assertNotIn("new Blob", script)
        self.assertNotIn("window.location.assign", script)
