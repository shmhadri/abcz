"""Shared helper that treats the letters page and its JavaScript assets as one bundle.

The letters page is being progressively refactored: JavaScript that used to live
inline inside ``templates/letters.html`` is moved into ``static/js/letters/``.
Tests that assert on behaviour must therefore search the *combination* of the
template and every script the template loads, otherwise a safe extraction would
look like a regression.

Nothing in here asserts anything by itself; it only builds the text corpus and
resolves the template's script order so tests stay location-independent.
"""
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
TEMPLATES_DIR = PROJECT_ROOT / "templates"
STATIC_DIR = PROJECT_ROOT / "static"
LETTERS_TEMPLATE = TEMPLATES_DIR / "letters.html"
LETTERS_JS_DIR = STATIC_DIR / "js" / "letters"
LETTERS_CSS = STATIC_DIR / "css" / "letters" / "letters.css"

# Matches both legacy hard-coded paths and the {% static %} form so the helper
# keeps working before, during and after the migration to {% static %}.
_SCRIPT_SRC_RE = re.compile(
    r"""<script[^>]*\bsrc\s*=\s*["']"""
    r"""(?:\{%\s*static\s*['"](?P<static>[^'"]+)['"]\s*%\}|(?P<plain>[^"']+))"""
    r"""["'][^>]*>""",
    re.IGNORECASE,
)

_STYLESHEET_RE = re.compile(
    r"""<link[^>]*\brel\s*=\s*["']stylesheet["'][^>]*\bhref\s*=\s*["']"""
    r"""(?:\{%\s*static\s*['"](?P<static>[^'"]+)['"]\s*%\}|(?P<plain>[^"']+))"""
    r"""["']""",
    re.IGNORECASE,
)


def read_text(path):
    """Read a project file as UTF-8, tolerating stray bytes like the other tests do."""
    return Path(path).read_text(encoding="utf-8", errors="ignore")


def template_html():
    """Raw text of templates/letters.html."""
    return read_text(LETTERS_TEMPLATE)


def _iter_asset_refs(pattern, html):
    for match in pattern.finditer(html):
        ref = match.group("static") or match.group("plain") or ""
        ref = ref.strip()
        if ref:
            yield ref


def is_local_asset(ref):
    """True for assets served from this project (not a CDN or data: URI)."""
    return not ref.startswith(("http://", "https://", "//", "data:"))


def static_relative_path(ref):
    """Normalise an asset reference to a path relative to the static root.

    Accepts both ``/static/js/letters/x.js`` and ``js/letters/x.js``.
    Returns None for external assets.
    """
    if not is_local_asset(ref):
        return None
    ref = ref.split("?", 1)[0].split("#", 1)[0]
    if ref.startswith("/static/"):
        ref = ref[len("/static/"):]
    return ref.lstrip("/")


def script_refs():
    """Every <script src=...> reference in the template, in document order."""
    return list(_iter_asset_refs(_SCRIPT_SRC_RE, template_html()))


def stylesheet_refs():
    """Every <link rel="stylesheet"> reference in the template, in document order."""
    return list(_iter_asset_refs(_STYLESHEET_RE, template_html()))


def local_script_paths():
    """Absolute paths of project-owned scripts the template loads, in load order."""
    paths = []
    for ref in script_refs():
        relative = static_relative_path(ref)
        if relative:
            paths.append(STATIC_DIR / relative)
    return paths


def local_script_names():
    """Basenames of project-owned scripts, in load order."""
    return [path.name for path in local_script_paths()]


def bundle_text():
    """Template plus every project-owned script it loads, concatenated.

    Use this instead of reading letters.html directly whenever a test asserts on
    JavaScript behaviour, so moving code into static/js/letters/ is not a failure.
    """
    parts = [template_html()]
    for path in local_script_paths():
        if path.is_file():
            parts.append(read_text(path))
    return "\n".join(parts)


def all_letters_js_text():
    """Every file under static/js/letters/, whether the template loads it or not."""
    parts = []
    for path in sorted(LETTERS_JS_DIR.glob("**/*.js")):
        parts.append(read_text(path))
    return "\n".join(parts)


def inline_script_text():
    """Only the inline <script> bodies of the template (no external files).

    Used to measure how much JavaScript still lives in the template.
    """
    bodies = re.findall(
        r"<script(?![^>]*\bsrc\s*=)[^>]*>(.*?)</script>",
        template_html(),
        flags=re.DOTALL | re.IGNORECASE,
    )
    return "\n".join(bodies)
