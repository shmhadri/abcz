"""Parse-checks the JavaScript the letters page actually ships.

Moving code out of the template is only safe if what the browser receives still
parses. These tests render the page through Django (so every template tag is
resolved) and run each inline script plus every loaded module through Node's
syntax checker.

If Node is not installed the tests skip rather than fail, so CI without a Node
toolchain is unaffected.
"""
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from django.test import TestCase, override_settings

from phonics.tests import letters_asset_bundle as bundle


NODE = shutil.which("node")


def check_syntax(source, label):
    """Return an error string if Node cannot parse `source`, else None."""
    with tempfile.TemporaryDirectory() as tmp:
        script = Path(tmp) / "candidate.js"
        script.write_text(source, encoding="utf-8")
        result = subprocess.run(
            [NODE, "--check", str(script)],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            return f"{label}: {result.stderr.strip()[:600]}"
    return None


@override_settings(DISABLE_AUTO_SEED=True)
class LettersJavaScriptSyntaxTests(TestCase):
    def setUp(self):
        if not NODE:
            self.skipTest("node is not available on PATH")

    def test_every_loaded_module_parses(self):
        failures = []
        for path in bundle.local_script_paths():
            if not path.is_file():
                failures.append(f"{path.name}: file is missing")
                continue
            error = check_syntax(bundle.read_text(path), path.name)
            if error:
                failures.append(error)
        self.assertEqual(failures, [])

    def test_rendered_inline_scripts_parse(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        html = response.content.decode("utf-8")

        bodies = re.findall(
            r"<script(?![^>]*\bsrc\s*=)[^>]*>(.*?)</script>",
            html,
            flags=re.DOTALL | re.IGNORECASE,
        )
        self.assertGreater(len(bodies), 0, "the page rendered no inline scripts at all")

        failures = []
        for index, body in enumerate(bodies):
            error = check_syntax(body, f"inline script #{index + 1}")
            if error:
                failures.append(error)
        self.assertEqual(failures, [])

    def test_rendered_page_has_no_unresolved_template_syntax(self):
        response = self.client.get("/")
        html = response.content.decode("utf-8")
        self.assertNotIn("{%", html)
        self.assertNotIn("{{", html)


# Methods each extracted module must actually install onto the prototype.
# This is executed, not grepped: the module is really loaded and really called.
EXTRACTED_MODULE_CONTRACTS = {
    "canvas_games.js": (
        "installLettersCanvasGames",
        [
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
    ),
    "celebrations.js": (
        "installLettersCelebrations",
        [
            "launchBalloonsCelebration",
            "createConfetti",
            "handleGameWin",
            "handleGameLose",
            "showGameWinMessage",
            "showWinGame",
            "showWinModal",
        ],
    ),
    "worksheet.js": (
        "installLettersWorksheet",
        ["generateWorksheet", "generateRandomLettersString"],
    ),
    "parent_report.js": (
        "installLettersParentReport",
        [
            "showParentReport",
            "hideParentReport",
            "backFromParentReport",
            "buildCurrentLetterReportText",
            "shareCurrentLetterReportWhatsapp",
            "downloadCurrentLetterReport",
            "printCurrentLetterReport",
            "getParentReportRecommendation",
        ],
    ),
}

# Minimal browser shim: enough for a module to define itself and install its
# mixin. No DOM work happens at install time, so this stays tiny on purpose.
INSTALL_HARNESS = """
const window = globalThis;
window.LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ".split("");
window.LETTER_DATA = { A: { words: [{ word: "ant", emoji: "x", translation: "y" }], quiz: [] } };

__MODULE_SOURCE__

class Host {}
const installer = window["__INSTALLER__"];
if (typeof installer !== "function") {
    console.error("MISSING_INSTALLER");
    process.exit(2);
}
installer(Host);

const expected = __EXPECTED__;
const missing = expected.filter((name) => typeof Host.prototype[name] !== "function");
if (missing.length > 0) {
    console.error("MISSING_METHODS:" + missing.join(","));
    process.exit(3);
}

// Installing twice must stay idempotent; the app may re-run boot logic.
installer(Host);
const stillMissing = expected.filter((name) => typeof Host.prototype[name] !== "function");
if (stillMissing.length > 0) {
    console.error("NOT_IDEMPOTENT:" + stillMissing.join(","));
    process.exit(4);
}

console.log("OK");
"""


class ExtractedModuleInstallTests(TestCase):
    """Proves extracted modules really attach their methods to the prototype."""

    def setUp(self):
        if not NODE:
            self.skipTest("node is not available on PATH")

    def _run_install(self, module_name, installer, expected):
        module_path = bundle.LETTERS_JS_DIR / module_name
        self.assertTrue(module_path.is_file(), f"{module_name} does not exist")

        harness = (
            INSTALL_HARNESS.replace("__MODULE_SOURCE__", bundle.read_text(module_path))
            .replace("__INSTALLER__", installer)
            .replace("__EXPECTED__", repr(expected).replace("'", '"'))
        )

        with tempfile.TemporaryDirectory() as tmp:
            script = Path(tmp) / "harness.js"
            script.write_text(harness, encoding="utf-8")
            result = subprocess.run(
                [NODE, str(script)],
                capture_output=True,
                text=True,
                timeout=60,
            )

        self.assertEqual(
            result.returncode,
            0,
            f"{module_name} failed to install: {result.stderr.strip()[:600]}",
        )
        self.assertIn("OK", result.stdout)

    def test_extracted_modules_install_their_methods(self):
        for module_name, (installer, expected) in EXTRACTED_MODULE_CONTRACTS.items():
            with self.subTest(module=module_name):
                self._run_install(module_name, installer, expected)
