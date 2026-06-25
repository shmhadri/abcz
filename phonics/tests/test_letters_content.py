import re
from pathlib import Path

from django.test import SimpleTestCase


BANNED_WORDS = {"pig", "zip", "zap"}
BANNED_TEXT = {"\u062e\u0646\u0632\u064a\u0631"}
MAX_WORDS_PER_LETTER = 5
MAX_WORD_LENGTH = 4


class LettersContentTests(SimpleTestCase):
    def setUp(self):
        self.project_root = Path(__file__).resolve().parents[2]
        self.letters_html = self.project_root / "templates" / "letters.html"
        self.letter_data_js = self.project_root / "static" / "js" / "letters" / "letter_data.js"

    def test_letters_page_does_not_contain_banned_words(self):
        content_paths = [
            self.project_root / "templates",
            self.project_root / "phonics" / "templates",
            self.project_root / "phonics" / "management" / "commands",
            self.project_root / "static" / "js",
            self.project_root / "add_cvc_data.py",
        ]

        failures = []
        for path in content_paths:
            files = [path] if path.is_file() else path.rglob("*")
            for file_path in files:
                if not file_path.is_file() or file_path.suffix.lower() not in {".html", ".py", ".js"}:
                    continue
                text = file_path.read_text(encoding="utf-8", errors="ignore")
                lower_text = text.lower()
                for word in BANNED_WORDS:
                    if re.search(rf"\b{re.escape(word)}\b", lower_text):
                        failures.append(f"{file_path.relative_to(self.project_root)} contains {word}")
                for text_value in BANNED_TEXT:
                    if text_value in text:
                        failures.append(f"{file_path.relative_to(self.project_root)} contains banned Arabic text")

        self.assertEqual(failures, [])

    def test_short_letter_words_are_limited_and_non_empty(self):
        text = self.letter_data_js.read_text(encoding="utf-8", errors="ignore")
        block_match = re.search(
            r"const\s+SHORT_LETTER_WORDS\s*=\s*{(?P<body>.*?)^\s*};",
            text,
            flags=re.DOTALL | re.MULTILINE,
        )
        self.assertIsNotNone(block_match, "SHORT_LETTER_WORDS block was not found")

        body = block_match.group("body")
        entries = dict(
            (match.group(1), re.findall(r'word:\s*"([^"]+)"', match.group(2)))
            for match in re.finditer(r"^\s*([A-Z]):\s*\[(.*?)^\s*\]", body, flags=re.DOTALL | re.MULTILINE)
        )

        self.assertEqual(set(entries.keys()), {chr(code) for code in range(ord("A"), ord("Z") + 1)})

        for letter, words in entries.items():
            with self.subTest(letter=letter):
                self.assertEqual(len(words), MAX_WORDS_PER_LETTER)
                for word in words:
                    self.assertTrue(word.strip())
                    self.assertLessEqual(len(word), MAX_WORD_LENGTH)
                    self.assertNotIn(word.lower(), BANNED_WORDS)

    def test_letters_page_loads_extracted_letter_data(self):
        html = self.letters_html.read_text(encoding="utf-8", errors="ignore")

        self.assertIn('/static/js/letters/letter_data.js', html)
        self.assertTrue(self.letter_data_js.exists())
