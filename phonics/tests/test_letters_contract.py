"""Regression safety net for the letters page refactor.

These tests lock the *contract* of templates/letters.html so JavaScript can be
moved out of the template into static/js/letters/ without silently losing a
feature. They deliberately assert on things that must survive the move:

* the page still renders for guests and for signed-in users,
* every asset the template references actually exists on disk,
* scripts load in a dependency-safe order,
* every mixin installer the app calls is still defined and still invoked,
* the Django -> JavaScript data contract is still delivered,
* the public method inventory of PhonicsGameLab does not shrink.

Assertions about JavaScript search the whole bundle (template + the scripts the
template loads), so relocating a function is not treated as deleting it.
"""
import re

from django.contrib.auth import get_user_model
from django.test import SimpleTestCase, TestCase, override_settings

from phonics.tests import letters_asset_bundle as bundle


# Every window.install* hook the application invokes. Each one must be both
# DEFINED by some script and CALLED by the application, or a feature silently
# stops installing itself onto the prototype.
REQUIRED_MIXIN_INSTALLERS = [
    "installLettersProgressSystem",
    "installLetterCompletionScreen",
    "installDragWordGame",
    "installCertificateSystem",
    "installLettersAssistantSystem",
    "installLettersMatchGame",
    "installLettersBalloonsGame",
    "installBirdTutor",
]

# Globals that scripts outside the template read. Losing any of these breaks a
# module that has no other way to reach the value.
REQUIRED_WINDOW_GLOBALS = [
    "window.LEVEL_ONE_PLAN",
    "window.LEVEL_ONE_ALLOWED_GAMES",
    "window.LEVEL_ONE_DISABLED_FEATURES",
    "window.PHONICS_USER_ID",
    "window.PHONICS_USER_EMAIL",
]

# Core methods of PhonicsGameLab that the user journey depends on. Grouped so a
# failure names the feature that broke, not just a missing identifier.
CORE_METHODS_BY_FEATURE = {
    "letter navigation": [
        "loadLetter",
        "goToLetter",
        "previousLetter",
        "nextLetter",
        "finishLetter",
        "renderLettersNav",
        "setupLetterJumpMenu",
    ],
    "words and pronunciation": [
        "renderWordsGrid",
        "speakLetter",
        "speakText",
        "listenForWord",
        "startSpeechRecognitionForWord",
        "markWordCardPronunciationCorrect",
    ],
    "pronunciation matching": [
        "normalizeSpeechInput",
        "isClosePronunciationMatch",
        "calculateSimilarity",
        "levenshteinDistance",
    ],
    "microphone": [
        "requestMicrophonePermission",
        "checkMicrophonePermission",
        "testMicrophone",
        "stopMicrophoneTest",
        "showMicStatus",
        "hideMicStatus",
    ],
    "writing practice": [
        "renderWritingBoxes",
        "createWritingBox",
        "checkWritingBox",
        "renderWritingDragPractice",
        "completeWritingDragSlot",
        "clearWritingDragSlot",
        "calculateCurrentWritingScore",
    ],
    "quiz": [
        "renderQuiz",
        "checkQuizAnswer",
        "nextQuizQuestion",
        "showQuizResults",
    ],
    "scoring and progress": [
        "updateAndCommitScores",
        "updateProgress",
        "renderAchievements",
        "ensureLetterRecord",
        "commitProgressUpdate",
    ],
    "subscription gating": [
        "isPremiumUser",
        "isFreeLetter",
        "isLetterAvailableForPlan",
        "showLetterPaywall",
        "hideLetterPaywall",
        "applyLevelOnePlanRules",
    ],
    "worksheet": [
        "generateWorksheet",
        "generateRandomLettersString",
    ],
    "parent report": [
        "showParentReport",
        "hideParentReport",
        "backFromParentReport",
        "buildCurrentLetterReportText",
        "shareCurrentLetterReportWhatsapp",
        "downloadCurrentLetterReport",
        "printCurrentLetterReport",
        "getParentReportRecommendation",
    ],
    "games lifecycle": [
        "startGame",
        "initGame",
        "closeGame",
        "endGame",
        "togglePause",
        "restartGame",
        "playAgain",
        "backToGames",
        "cleanupGameResources",
        "removeAllGameEventListeners",
        "runOptimizedGameLoop",
        "handleResize",
        "updateGameStats",
        "setupGameControls",
        "getGameName",
    ],
    "canvas games": [
        "initShootingGame",
        "initTypingGame",
        "initMemoryGame",
        "initWordSearchGame",
        "initDefaultGame",
        "canPlaceWord",
        "placeWord",
        "getCellsBetween",
        "getWordCells",
    ],
    "celebrations": [
        "launchBalloonsCelebration",
        "createConfetti",
        "createMiniCelebration",
        "showRandomEncouragement",
        "showWinGame",
        "showWinModal",
        "showGameWinMessage",
        "handleGameWin",
        "handleGameLose",
        "showMotivationModal",
    ],
    "profile and theme": [
        "openProfileModal",
        "saveProfile",
        "saveProfileToServer",
        "storeProfileLocally",
        "updateProfileDisplay",
        "getCookie",
        "setupTheme",
        "toggleTheme",
    ],
    "shell": [
        "cacheDOM",
        "bindEvents",
        "showToast",
        "showLetterInfo",
        "setupScrollTop",
        "setupTouchControls",
        "disableCopyPaste",
        "disableCopyPasteForElement",
    ],
}

# localStorage keys the page reads or writes. Renaming one silently discards a
# returning learner's saved progress, so they are pinned.
REQUIRED_STORAGE_KEYS = [
    "letterProgress",
    "nightMode",
    "soundEnabled",
    "studentName",
    "studentCity",
    "studentEmail",
    "parentPhone",
]

# Server endpoints the page talks to.
REQUIRED_ENDPOINTS = [
    "/accounts/profile/",
    "/api/letter-progress/save/",
]

# DOM ids that JavaScript looks up but the markup never defines. Every one of
# these lookups is already null-guarded, so they are harmless dead lookups that
# predate this refactor. They are pinned here so the orphan check still fails
# loudly if the refactor introduces a NEW one.
KNOWN_ORPHAN_DOM_IDS = {
    "ai-typing",            # assistant.js, created at runtime while the bot "types"
    "app",                  # progress.js, optional host element probe
    "phonicsApp",           # progress.js, optional host element probe
    "birdListeningStatus",  # bird_tutor.js, optional status line
    "certificateDate",      # letters.html, certificate uses certificate-date instead
    "closePrivacyModal",    # letters.html, privacy modal markup is not on this page
    "privacyModal",         # letters.html, same
    "privacyPolicyBtn",     # letters.html, same
    "game-canvas",          # letters.html, canvas id is gameCanvas
    "progressValue",        # letters.html, guarded by `if (this.progressValueEl)`
    "studentName",          # letters.html, replaced by the profile modal input
    "viewInstructions",     # letters.html, guarded menu entry
    "backToGamesBtn",       # letters.html, injected into the win screen at runtime
}


class LettersAssetContractTests(SimpleTestCase):
    """Static-file and load-order guarantees. No database needed."""

    def test_every_referenced_local_script_exists_on_disk(self):
        missing = [
            str(path.relative_to(bundle.PROJECT_ROOT))
            for path in bundle.local_script_paths()
            if not path.is_file()
        ]
        self.assertEqual(missing, [], "letters.html references script files that do not exist")

    def test_every_referenced_local_stylesheet_exists_on_disk(self):
        missing = []
        for ref in bundle.stylesheet_refs():
            relative = bundle.static_relative_path(ref)
            if relative and not (bundle.STATIC_DIR / relative).is_file():
                missing.append(relative)
        self.assertEqual(missing, [], "letters.html references stylesheets that do not exist")

    def test_letter_data_loads_before_any_script_that_consumes_it(self):
        # LETTERS / LETTER_DATA are published by letter_data.js and read by the
        # application, so it has to come first among local scripts.
        names = bundle.local_script_names()
        self.assertIn("letter_data.js", names)
        self.assertEqual(names[0], "letter_data.js")

    def test_bird_tutor_content_loads_before_bird_tutor(self):
        names = bundle.local_script_names()
        self.assertIn("bird_tutor_content.js", names)
        self.assertIn("bird_tutor.js", names)
        self.assertLess(
            names.index("bird_tutor_content.js"),
            names.index("bird_tutor.js"),
            "bird_tutor.js reads BIRD_TUTOR_CONTENT and must load after it",
        )

    def test_local_scripts_are_not_loaded_with_async(self):
        # async does not preserve execution order; these files depend on each other.
        html = bundle.template_html()
        for tag in re.findall(r"<script[^>]*\bsrc\s*=[^>]*>", html, re.IGNORECASE):
            if "cdnjs" in tag or "http" in tag:
                continue
            with self.subTest(tag=tag.strip()[:120]):
                self.assertNotRegex(tag, r"\basync\b")

    def test_no_duplicate_script_includes(self):
        names = bundle.local_script_names()
        duplicates = sorted({name for name in names if names.count(name) > 1})
        self.assertEqual(duplicates, [], "a script is included more than once")


class LettersJavaScriptContractTests(SimpleTestCase):
    """Behavioural contract, asserted against template + loaded scripts."""

    def setUp(self):
        self.bundle = bundle.bundle_text()

    def test_all_mixin_installers_are_defined(self):
        # An installer may live in any loaded script.
        undefined = [
            name
            for name in REQUIRED_MIXIN_INSTALLERS
            if f"window.{name}" not in self.bundle
        ]
        self.assertEqual(undefined, [], "mixin installer is no longer defined")

    def test_all_mixin_installers_are_actually_invoked(self):
        # Defining an installer without calling it means the feature never installs.
        not_invoked = [
            name
            for name in REQUIRED_MIXIN_INSTALLERS
            if not re.search(rf"{re.escape(name)}\s*\(\s*\w", self.bundle)
        ]
        self.assertEqual(not_invoked, [], "mixin installer is defined but never called")

    def test_core_methods_are_present_for_every_feature(self):
        for feature, methods in CORE_METHODS_BY_FEATURE.items():
            missing = [
                method
                for method in methods
                if not re.search(rf"\b{re.escape(method)}\b", self.bundle)
            ]
            with self.subTest(feature=feature):
                self.assertEqual(missing, [], f"{feature}: methods disappeared")

    def test_application_class_and_single_boot_are_preserved(self):
        self.assertIn("class PhonicsGameLab", self.bundle)
        # Exactly one construction site keeps the app from being booted twice.
        constructions = re.findall(r"new\s+PhonicsGameLab\s*\(", self.bundle)
        self.assertEqual(
            len(constructions),
            1,
            "PhonicsGameLab must be constructed exactly once",
        )

    def test_django_to_javascript_globals_are_published(self):
        html = bundle.template_html()
        missing = [name for name in REQUIRED_WINDOW_GLOBALS if name not in html]
        self.assertEqual(missing, [], "template no longer publishes a required global")

    def test_level_one_disabled_feature_flags_are_all_delivered(self):
        html = bundle.template_html()
        for flag in [
            "wordwall",
            "letterWorksheets",
            "worksheetBook",
            "leaderboard",
            "smartBird",
            "parentReport",
            "certificate",
        ]:
            with self.subTest(flag=flag):
                self.assertIn(flag, html)

    def test_subscription_context_values_are_rendered(self):
        html = bundle.template_html()
        for token in ["is_authenticated", "is_premium_user", "is_vip_user", "level_one_plan"]:
            with self.subTest(token=token):
                self.assertIn(token, html)

    def test_storage_keys_are_stable(self):
        missing = [key for key in REQUIRED_STORAGE_KEYS if f"'{key}'" not in self.bundle]
        self.assertEqual(missing, [], "a localStorage key was renamed; saved progress would be lost")

    def test_endpoints_are_stable(self):
        missing = [endpoint for endpoint in REQUIRED_ENDPOINTS if endpoint not in self.bundle]
        self.assertEqual(missing, [], "an API endpoint reference was changed")

    def test_dom_ids_used_by_javascript_exist_in_markup(self):
        html = bundle.template_html()
        partials = "".join(
            bundle.read_text(path)
            for path in (bundle.TEMPLATES_DIR / "letters").glob("*.html")
        )
        markup = html + partials
        declared = set(re.findall(r'id="([A-Za-z0-9_-]+)"', markup))
        looked_up = set(re.findall(r"getElementById\(\s*'([A-Za-z0-9_-]+)'\s*\)", self.bundle))
        looked_up |= set(re.findall(r'getElementById\(\s*"([A-Za-z0-9_-]+)"\s*\)', self.bundle))
        orphans = sorted(looked_up - declared - KNOWN_ORPHAN_DOM_IDS)
        self.assertEqual(
            orphans,
            [],
            "the refactor introduced DOM id lookups that the markup does not define",
        )

    def test_speech_recognition_support_is_feature_detected(self):
        # Browsers without the API must be handled, not crash.
        self.assertIn("webkitSpeechRecognition", self.bundle)
        self.assertRegex(
            self.bundle,
            r"window\.SpeechRecognition\s*\|\|\s*window\.webkitSpeechRecognition",
        )

    def test_microphone_errors_are_all_handled(self):
        for error in ["not-allowed", "audio-capture", "no-speech", "network", "aborted"]:
            with self.subTest(error=error):
                self.assertIn(error, self.bundle)

    def test_media_stream_tracks_are_released(self):
        self.assertRegex(
            self.bundle,
            r"getTracks\(\)\s*\.forEach\(\s*(?:\(?\s*track\s*\)?)\s*=>\s*track\.stop\(\)\s*\)",
        )

    def test_speaker_is_stopped_before_microphone_starts(self):
        # The page must not record its own voice prompt.
        self.assertRegex(self.bundle, r"stopAll\(\)[\s\S]{0,120}?recognition\.start\(\)")

    def test_game_cleanup_releases_animation_frames_and_timers(self):
        self.assertIn("cancelAnimationFrame", self.bundle)
        self.assertIn("clearInterval", self.bundle)
        self.assertIn("removeAllGameEventListeners", self.bundle)

    def test_voice_selection_never_matches_female_as_male(self):
        # "female".includes("male") is true, so a bare substring test on "male"
        # would happily select "Google UK English Female".
        bare_substring_tests = re.findall(
            r"[^\n]*includes\(\s*['\"]male['\"]\s*\)[^\n]*", self.bundle
        )
        offending = [
            line.strip()
            for line in bare_substring_tests
            if not re.search(r"female", line, re.IGNORECASE)
        ]
        self.assertEqual(
            offending,
            [],
            "a bare includes('male') test also matches 'female' voices",
        )

    def test_a_male_voice_predicate_exists_and_excludes_female(self):
        # Guards against "fixing" the previous test by deleting the filter.
        self.assertIn("isMaleVoiceName", self.bundle)
        predicate = re.search(
            r"isMaleVoiceName\s*\([^)]*\)\s*\{(?P<body>[\s\S]{0,400}?)\n\s{0,16}\}",
            self.bundle,
        )
        self.assertIsNotNone(predicate, "isMaleVoiceName body was not found")
        body = predicate.group("body")
        self.assertRegex(body, r"male", "predicate must test for a male voice")
        self.assertRegex(body, r"female", "predicate must exclude female voices")

    def test_recognition_sessions_are_guarded_against_stale_callbacks(self):
        # A result arriving from an aborted attempt must not repaint the UI of a
        # newer one.
        self.assertIn("micSessionId", self.bundle)
        self.assertIn("isCurrentSession", self.bundle)
        for handler in ["onresult", "onerror", "onend", "onstart"]:
            with self.subTest(handler=handler):
                block = re.search(
                    rf"recognition\.{handler}\s*=\s*(?:async\s*)?\([^)]*\)\s*=>\s*\{{"
                    rf"(?P<body>[\s\S]{{0,400}})",
                    self.bundle,
                )
                self.assertIsNotNone(block, f"recognition.{handler} was not found")
                self.assertIn(
                    "isCurrentSession",
                    block.group("body"),
                    f"recognition.{handler} does not check the session id",
                )

    def test_extra_error_codes_are_handled(self):
        for error in ["service-not-allowed", "language-not-supported"]:
            with self.subTest(error=error):
                self.assertIn(error, self.bundle)

    def test_microphone_permission_is_not_requested_twice_per_tap(self):
        # The word-card click handler must not run its own permission check; the
        # duplicate opened and closed a second stream before recognition started.
        handler = re.search(
            r"micBtn\.addEventListener\('click'[\s\S]{0,1500}?listenForWord",
            self.bundle,
        )
        self.assertIsNotNone(handler, "the word-card mic handler was not found")
        self.assertNotIn(
            "requestMicrophonePermission",
            handler.group(0),
            "the mic click handler re-checks permission, costing an extra stream",
        )

    def test_mic_button_is_released_on_every_early_return(self):
        self.assertIn("releaseMicButton", self.bundle)

    def test_audio_context_is_shared_not_created_per_sound(self):
        # A fresh context per sound hits the browser's concurrent-context cap.
        self.assertIn("getAudioContext", self.bundle)
        play_sound = re.search(
            r"playSound\s*\(\s*type\s*\)\s*\{(?P<body>[\s\S]*?)\n\s{12}\}\n",
            self.bundle,
        )
        self.assertIsNotNone(play_sound, "playSound was not found")
        self.assertNotIn(
            "new (window.AudioContext",
            play_sound.group("body"),
            "playSound still constructs its own AudioContext",
        )

    def test_game_loop_does_not_accumulate_animation_frame_ids(self):
        loop = re.search(
            r"runOptimizedGameLoop\([^)]*\)\s*\{(?P<body>[\s\S]{0,900}?)\n\s{0,16}\}",
            self.bundle,
        )
        self.assertIsNotNone(loop, "runOptimizedGameLoop was not found")
        self.assertIn(
            "activeAnimations.delete",
            loop.group("body"),
            "the game loop adds frame ids without ever removing them",
        )

    def test_voice_selection_falls_back_to_any_english_voice(self):
        # A missing preferred voice must never silence the page.
        self.assertRegex(
            self.bundle,
            r"voices\.find\(\s*v(?:oice)?\s*=>\s*v(?:oice)?\.lang\.startsWith\(\s*'en'\s*\)\s*\)",
        )


@override_settings(DISABLE_AUTO_SEED=True)
class LettersPageRenderTests(TestCase):
    """The page must actually render, for both guest and authenticated users."""

    def test_page_renders_for_anonymous_visitor(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "letters.html")

    def test_page_renders_for_authenticated_user(self):
        user_model = get_user_model()
        user_model.objects.create_user(
            username="letters-contract-user",
            email="letters-contract@example.com",
            password="contract-pass-123",
        )
        self.client.login(username="letters-contract-user", password="contract-pass-123")

        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "letters.html")

    def test_rendered_page_carries_the_javascript_bootstrap_data(self):
        response = self.client.get("/")
        html = response.content.decode("utf-8")

        # Django template tags must be fully resolved, never shipped raw.
        self.assertNotIn("{%", html)
        self.assertNotIn("{{", html)

        for global_name in REQUIRED_WINDOW_GLOBALS:
            with self.subTest(global_name=global_name):
                self.assertIn(global_name, html)

    def test_rendered_page_loads_every_local_script(self):
        response = self.client.get("/")
        html = response.content.decode("utf-8")

        for name in bundle.local_script_names():
            with self.subTest(script=name):
                self.assertIn(name, html)

    def test_guest_sees_login_entry_points_and_no_logout(self):
        response = self.client.get("/")
        html = response.content.decode("utf-8")
        self.assertIn("/accounts/login/", html)
        self.assertNotIn('action="/accounts/logout/"', html)

    def test_key_interactive_elements_are_present(self):
        response = self.client.get("/")
        html = response.content.decode("utf-8")

        for element_id in [
            "lettersNav",
            "wordsGrid",
            "capitalWriting",
            "smallWriting",
            "capitalDragWriting",
            "smallDragWriting",
            "wordWritingList",
            "quizOptions",
            "gameCanvas",
            "gamesGrid",
            "micStatus",
            "parentReportModal",
            "certificateModal",
            "letterPaywallModal",
            "motivationModal",
            "toast",
        ]:
            with self.subTest(element_id=element_id):
                self.assertIn(f'id="{element_id}"', html)
