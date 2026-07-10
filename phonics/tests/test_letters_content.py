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
        self.bird_tutor_partial = self.project_root / "templates" / "letters" / "_bird_tutor.html"
        self.completion_partial = self.project_root / "templates" / "letters" / "_completion_modal.html"
        self.letter_data_js = self.project_root / "static" / "js" / "letters" / "letter_data.js"
        self.progress_js = self.project_root / "static" / "js" / "letters" / "progress.js"
        self.letter_completion_js = self.project_root / "static" / "js" / "letters" / "letter_completion.js"
        self.certificate_js = self.project_root / "static" / "js" / "letters" / "certificate.js"
        self.letters_css = self.project_root / "static" / "css" / "letters" / "letters.css"

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
                    self.assertTrue(
                        word.lower().startswith(letter.lower()),
                        f"{word} should start with {letter}",
                    )
                    self.assertNotIn(word.lower(), BANNED_WORDS)

    def test_letters_page_loads_extracted_letter_data(self):
        html = self.letters_html.read_text(encoding="utf-8", errors="ignore")

        self.assertIn('/static/js/letters/letter_data.js', html)
        self.assertTrue(self.letter_data_js.exists())

    def test_letter_x_uses_expected_words(self):
        text = self.letter_data_js.read_text(encoding="utf-8", errors="ignore")
        block_match = re.search(r"X:\s*\[(.*?)^\s*\]", text, flags=re.DOTALL | re.MULTILINE)

        self.assertIsNotNone(block_match, "X words block was not found")
        words = re.findall(r'word:\s*"([^"]+)"', block_match.group(1))

        self.assertEqual(words, ["xray", "xmas", "xbox", "xeno", "xyst"])

    def test_letters_page_links_to_external_games(self):
        html = self.letters_html.read_text(encoding="utf-8", errors="ignore")

        self.assertIn('id="externalGamesLink"', html)
        self.assertIn('/letters/A/external-games/', html)
        self.assertIn('/letters/${letter}/external-games/', html)

    def test_letters_layout_uses_four_learning_levels(self):
        html = self.letters_html.read_text(encoding="utf-8", errors="ignore")
        css = self.letters_css.read_text(encoding="utf-8", errors="ignore")

        self.assertIn('class="learning-levels-nav"', html)
        self.assertEqual(html.count('class="learning-level-link'), 4)
        self.assertEqual(html.count("data-learning-level="), 4)
        self.assertEqual(html.count("data-menu-learning-level="), 4)
        self.assertIn("المستوى الأول", html)
        self.assertIn("الحروف الإنجليزية", html)
        self.assertIn("المستوى الثاني", html)
        self.assertIn("الصوتيات", html)
        self.assertIn("المستوى الثالث", html)
        self.assertIn("قراءة CVC", html)
        self.assertIn("المستوى الرابع", html)
        self.assertIn("التأسيس الإنجليزي", html)
        self.assertIn("{% url 'sounds' %}", html)
        self.assertIn("{% url 'cvc_reading' %}", html)
        self.assertIn("{% url 'level_four' %}", html)
        self.assertIn('class="menu-item learning-menu-item is-active"', html)
        self.assertIn("learning-level-link", css)
        self.assertIn("learning-menu-item.is-active", css)
        self.assertIn("touch-action: manipulation", css)
        self.assertIn("min-height: 44px", css)

    def test_letters_page_contains_free_letter_gate(self):
        html = self.letters_html.read_text(encoding="utf-8", errors="ignore")

        self.assertIn("const IS_PREMIUM_USER = {{ is_premium_user|yesno:", html)
        self.assertIn('id="letterPaywallModal"', html)
        self.assertIn('href="/pricing/"', html)

    def test_letters_page_contains_bird_tutor(self):
        html = self.letters_html.read_text(encoding="utf-8", errors="ignore")
        partial = self.bird_tutor_partial.read_text(encoding="utf-8", errors="ignore")

        self.assertIn('{% include "letters/_bird_tutor.html" %}', html)
        self.assertIn('id="birdTutor"', partial)
        self.assertIn('id="birdLottie"', partial)
        self.assertIn('id="birdAskBtn"', partial)
        self.assertIn('id="birdLessonIntro"', partial)
        self.assertIn('id="birdVisualQuestion"', partial)
        self.assertIn("/static/js/letters/bird_tutor_content.js", html)
        self.assertIn("/static/js/letters/bird_tutor.js", html)
        self.assertIn("window.installBirdTutor(PhonicsGameLab)", html)
        self.assertIn("lottie-web/5.12.2/lottie.min.js", html)

    def test_letter_games_are_optional_after_core_lesson(self):
        html = self.letters_html.read_text(encoding="utf-8", errors="ignore")
        progress = self.progress_js.read_text(encoding="utf-8", errors="ignore")

        self.assertIn("this.requiredGames = [];", html)
        self.assertIn("this.mandatoryGames = [];", html)
        self.assertIn("const missingGames = [];", html)
        self.assertIn("الألعاب اختيارية للتدريب ولا تمنع فتح الحرف التالي.", html)
        self.assertIn("const fullyCompleted = exercisesDone && scoreReached;", progress)
        self.assertIn("return passedExercises && passedScore;", progress)
        self.assertIn("return [];", progress)

        for game in ["shooting", "balloons", "memory", "wordsearch", "typing", "match"]:
            with self.subTest(game=game):
                self.assertIn(f'data-game="{game}"', html)

    def test_required_score_remains_thirteen(self):
        html = self.letters_html.read_text(encoding="utf-8", errors="ignore")

        self.assertIn("this.REQUIRED_SCORE = 13;", html)
        self.assertIn("(latestEntry.score || 0) < this.REQUIRED_SCORE", html)

    def test_letter_completion_screen_is_available_and_accessible(self):
        html = self.letters_html.read_text(encoding="utf-8", errors="ignore")
        partial = self.completion_partial.read_text(encoding="utf-8", errors="ignore")
        script = self.letter_completion_js.read_text(encoding="utf-8", errors="ignore")

        self.assertTrue(self.completion_partial.exists())
        self.assertTrue(self.letter_completion_js.exists())
        self.assertIn('{% include "letters/_completion_modal.html" %}', html)
        self.assertIn("/static/js/letters/letter_completion.js", html)
        self.assertIn("window.installLetterCompletionScreen(PhonicsGameLab)", html)
        self.assertIn('id="letterCompletionModal"', partial)
        self.assertIn('role="dialog"', partial)
        self.assertIn('aria-modal="true"', partial)
        self.assertIn('id="completionNextLetter"', partial)
        self.assertIn('id="completionOptionalGames"', partial)
        self.assertIn('id="completionParentReport"', partial)
        self.assertIn("bindActivation", script)
        self.assertIn("showLetterCompletion", script)
        self.assertIn("openCompletionParentReport", script)

    def test_letter_completion_replaces_auto_game_gate(self):
        html = self.letters_html.read_text(encoding="utf-8", errors="ignore")

        self.assertIn("this.showLetterCompletion(currentLetter, latestEntry);", html)
        self.assertNotIn("setTimeout(() => this.loadLetter(nextIndex), 1200);", html)
        self.assertIn("const missingGames = [];", html)

    def test_letters_certificate_design_and_print_assets(self):
        html = self.letters_html.read_text(encoding="utf-8", errors="ignore")
        css = self.letters_css.read_text(encoding="utf-8", errors="ignore")
        script = self.certificate_js.read_text(encoding="utf-8", errors="ignore")

        self.assertIn('id="certificateModal"', html)
        self.assertIn("Certificate of Achievement", html)
        self.assertIn("شهادة إنجاز", html)
        self.assertIn("Completed", html)
        self.assertIn("مكتمل", html)
        self.assertIn("26</span> / 26", html)
        self.assertIn('id="certificate-id"', html)
        self.assertIn("PGL-LETTERS", script)
        self.assertIn("buildCertificateId", script)
        self.assertIn("certificate-actions", css)
        self.assertIn("no-print", css)
        self.assertIn("@media print", css)
        self.assertIn("@page", css)

    def test_letter_quiz_state_is_scoped_to_current_letter(self):
        html = self.letters_html.read_text(encoding="utf-8", errors="ignore")
        progress = self.progress_js.read_text(encoding="utf-8", errors="ignore")

        self.assertIn("ensureCurrentLetterQuizState", html)
        self.assertIn("quizContainer.dataset.quizLetter", html)
        self.assertIn("questionData.letter && questionData.letter !== letter", html)
        self.assertIn("letter_knowledge_quiz_${letter}", html)
        self.assertIn("letter_knowledge_quiz_${letter}", progress)
        self.assertIn("const quizBelongsToLetter = quizState.letter === letter;", progress)
        self.assertIn("quizBelongsToLetter &&", progress)

    def test_letter_quiz_questions_are_generated_for_the_current_letter(self):
        html = self.letters_html.read_text(encoding="utf-8", errors="ignore")

        self.assertIn("const soundDistractorLetters = LETTERS", html)
        self.assertIn("soundCorrectIndex", html)
        self.assertIn("LETTER_DATA[otherLetter]?.words?.[0]?.word", html)
        self.assertIn("id: `${letter}-knowledge-${index + 1}`", html)
        self.assertNotIn('options: ["/b/ كما في bat", "/ɑ:/ كما في arm", "/eɪ/ كما في ace", "/ɪ/ كما في ink"]', html)
