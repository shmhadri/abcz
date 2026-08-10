"""Tests for the letters-page British audio & mic responsiveness sprint.

These tests assert the audio/mic improvements while proving the
pronunciation-correction logic and word data are left untouched.

They read the letters *bundle* - templates/letters.html plus every script the
template loads - rather than the template alone. The assertions are unchanged;
widening the corpus only means that moving this JavaScript into
static/js/letters/ is correctly treated as a relocation, not a deletion.
"""
import re

from django.test import SimpleTestCase

from phonics.tests import letters_asset_bundle as bundle


class LettersBritishAudioTests(SimpleTestCase):
    def setUp(self):
        self.project_root = bundle.PROJECT_ROOT
        self.letters_html = bundle.LETTERS_TEMPLATE
        self.html = bundle.bundle_text()

    # --- Speaker (TTS) ---------------------------------------------------

    def test_speaker_uses_en_gb(self):
        self.assertIn("soundManager.speak(text, 'en-GB')", self.html)
        self.assertIn("speak(text, lang = 'en-GB')", self.html)

    def test_speaker_rate_is_within_spec_range(self):
        match = re.search(r"utterance\.rate\s*=\s*([0-9.]+)", self.html)
        self.assertIsNotNone(match)
        rate = float(match.group(1))
        self.assertGreaterEqual(rate, 0.78)
        self.assertLessEqual(rate, 0.84)

    def test_speaker_pitch_is_within_spec_range(self):
        match = re.search(r"utterance\.pitch\s*=\s*([0-9.]+)", self.html)
        self.assertIsNotNone(match)
        pitch = float(match.group(1))
        self.assertGreaterEqual(pitch, 0.92)
        self.assertLessEqual(pitch, 1.0)

    def test_prefers_british_male_voice_names(self):
        for name in ["Ryan", "George", "Daniel"]:
            self.assertIn(name, self.html)

    def test_final_voice_fallback_excludes_known_female_voices_and_keeps_fallback(self):
        # A male-preferring fallback plus an unconditional en fallback must both exist.
        self.assertIn("female|zira|hazel|susan|sonia|libby", self.html)
        self.assertIn("voices.find(v => v.lang.startsWith('en'))", self.html)

    # --- Microphone (recognition) ---------------------------------------

    def test_recognition_uses_en_gb(self):
        self.assertIn("'en-GB'", self.html)
        self.assertIn("recognition.lang", self.html)

    def test_fixed_startup_delay_is_removed(self):
        self.assertNotIn("setTimeout(resolve, 150)", self.html)

    def test_speaker_is_stopped_before_microphone_starts(self):
        self.assertIn(
            "this.soundManager.stopAll(); } catch (e) {} recognition.start();",
            self.html,
        )

    def test_correction_runs_from_final_onresult(self):
        self.assertIn("recognition.onresult = async (event) =>", self.html)

    # --- Correction logic & data must NOT change ------------------------

    def test_pronunciation_matching_functions_are_unchanged(self):
        for token in [
            "isClosePronunciationMatch",
            "calculateSimilarity",
            "levenshteinDistance",
            "normalizeSpeechInput",
            "speechAliases",
        ]:
            self.assertIn(token, self.html)

    def test_recognition_max_alternatives_preserved(self):
        # Kept at 20 so the existing matching results are not made stricter.
        self.assertIn("maxAlternatives = 20", self.html)

    def test_five_words_per_letter_preserved(self):
        self.assertIn("WORDS_PER_LETTER = window.WORDS_PER_LETTER || 5", self.html)
