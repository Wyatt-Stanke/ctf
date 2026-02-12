"""
Directive detection and processing.

Supported directives (placed as the very first line of a file):
  HTML:  <!-- COMPILER: directory_listing -->
         <!-- COMPILER: html_minify -->
  JSON:  // COMPILER: json_minify
  Skip:  // COMPILER: no_include          (file is excluded from output)
  Bundle:// COMPILER: base64_bundle <file> (base64-encodes referenced file
                                            and appends eval(atob(...)))
"""

from __future__ import annotations

import base64
import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from compiler.assets import apply_shared_placeholders

# Hidden markdown files (e.g. .foo.md) are excluded from directory listings.
_HIDDEN_MD_RE = re.compile(r"^\..+\.md$", re.IGNORECASE)

# ---------------------------------------------------------------------------
# Directive detection
# ---------------------------------------------------------------------------

_HTML_DIRECTIVE_RE = re.compile(r"\A\s*<!--\s*COMPILER:\s*(\w+)\s*-->", re.IGNORECASE)
_JSON_DIRECTIVE_RE = re.compile(r"\A\s*//\s*COMPILER:\s*(\w+)", re.IGNORECASE)

KNOWN_DIRECTIVES = {
    "directory_listing",
    "html_minify",
    "json_minify",
    "no_include",
    "base64_bundle",
    "challenge_page",
}


def detect_directive(file_path: Path) -> Optional[str]:
    """Return the directive name found on the first line, or *None*."""
    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as fh:
            first_line = fh.readline()
    except (OSError, UnicodeDecodeError):
        return None

    m = _HTML_DIRECTIVE_RE.match(first_line) or _JSON_DIRECTIVE_RE.match(first_line)
    if m:
        name = m.group(1).lower()
        if name in KNOWN_DIRECTIVES:
            return name
    return None


# ---------------------------------------------------------------------------
# directory_listing
# ---------------------------------------------------------------------------


def _fmt_size(size: int) -> str:
    """Right-align an integer byte size into a 7-char column (nginx style)."""
    return str(size).rjust(7)


def _fmt_date(ts: float) -> str:
    """Format a timestamp as ``dd-Mon-yyyy HH:MM``."""
    dt = datetime.fromtimestamp(ts, tz=timezone.utc)
    return dt.strftime("%d-%b-%Y %H:%M")


def apply_directory_listing(file_path: Path, url_prefix: str = "/") -> str:
    """Generate an nginx-style directory listing for *file_path*'s directory.

    *url_prefix* is the URL path that corresponds to the directory (used in
    the ``<title>`` and heading).  It should end with ``/``.
    """
    directory = file_path.parent

    # Collect entries (skip the index file itself and hidden markdown files)
    entries: list[tuple[str, bool, float, int]] = []
    for child in sorted(directory.iterdir(), key=lambda p: p.name.lower()):
        if child.name == file_path.name:
            continue
        if _HIDDEN_MD_RE.match(child.name):
            continue
        is_dir = child.is_dir()
        stat = child.stat()
        entries.append((child.name, is_dir, stat.st_mtime, stat.st_size))

    # Build the <pre> block lines
    lines: list[str] = []
    lines.append('<a href="../">../</a>')

    # Directories first, then files — matching typical nginx behaviour
    dirs = [(n, d, m, s) for n, d, m, s in entries if d]
    files = [(n, d, m, s) for n, d, m, s in entries if not d]

    for name, _is_dir, mtime, size in dirs + files:
        display_name = name + "/" if _is_dir else name
        href = display_name
        # Pad name to 50 chars (nginx uses ~50 cols)
        padded_name = display_name.ljust(50)
        date_str = _fmt_date(mtime)
        size_str = "   -" if _is_dir else _fmt_size(size)
        link = f'<a href="{href}">{padded_name}</a>'
        # The visible columns after the link close tag
        padding = " " * max(1, 51 - len(display_name))
        lines.append(f"{link}{padding}{date_str} {size_str}")

    pre_block = "\n".join(lines)

    if not url_prefix.endswith("/"):
        url_prefix += "/"

    return (
        "<!doctype html>\n"
        "<html>\n"
        "  <head>\n"
        f"    <title>Index of {url_prefix}</title>\n"
        "  </head>\n"
        "  <body>\n"
        f"    <h1>Index of {url_prefix}</h1>\n"
        "    <hr />\n"
        f"    <pre>{pre_block}\n"
        "</pre>\n"
        "    <hr />\n"
        "    <address>nginx/1.25.3</address>\n"
        "  </body>\n"
        "</html>\n"
    )


# ---------------------------------------------------------------------------
# html_minify
# ---------------------------------------------------------------------------


def _strip_html_comments(html: str) -> str:
    """Remove HTML comments, but preserve conditional comments (<!--[if)."""
    return re.sub(r"<!--(?!\[).*?-->", "", html, flags=re.DOTALL)


def apply_html_minify(file_path: Path) -> str:
    """Return a minified version of the HTML file at *file_path*.

    This is intentionally a lightweight minifier (no external deps):
    - strips the directive comment
    - removes HTML comments
    - collapses runs of whitespace (outside <pre>/<script>/<style>)
    - trims lines
    """
    with open(file_path, "r", encoding="utf-8") as fh:
        content = fh.read()

    # Strip the directive line
    content = _HTML_DIRECTIVE_RE.sub("", content, count=1)

    # Separate <pre>, <script>, <style> blocks so we don't mangle them
    protected: dict[str, str] = {}
    counter = 0

    def _protect(m: re.Match) -> str:
        nonlocal counter
        key = f"\x00PROTECT_{counter}\x00"
        counter += 1
        protected[key] = m.group(0)
        return key

    content = re.sub(
        r"(<(?:pre|script|style|textarea)\b[^>]*>)(.*?)(</(?:pre|script|style|textarea)>)",
        _protect,
        content,
        flags=re.DOTALL | re.IGNORECASE,
    )

    # Strip comments
    content = _strip_html_comments(content)

    # Collapse whitespace
    content = re.sub(r"\s+", " ", content)

    # Remove spaces around tags
    content = re.sub(r"\s*>\s*", ">", content)
    content = re.sub(r"\s*<\s*", "<", content)

    # Restore protected blocks
    for key, val in protected.items():
        content = content.replace(key, val)

    return content.strip() + "\n"


# ---------------------------------------------------------------------------
# json_minify
# ---------------------------------------------------------------------------


def apply_json_minify(file_path: Path) -> str:
    """Return a minified (compact) version of the JSON file at *file_path*.

    The ``// COMPILER: json_minify`` comment line is stripped before parsing.
    """
    with open(file_path, "r", encoding="utf-8") as fh:
        raw = fh.read()

    # Strip the directive line
    raw = _JSON_DIRECTIVE_RE.sub("", raw, count=1).lstrip("\n")

    data = json.loads(raw)
    return json.dumps(data, separators=(",", ":")) + "\n"


# ---------------------------------------------------------------------------
# Dispatch
# ---------------------------------------------------------------------------

# Regex to extract the filename argument from a base64_bundle directive line
_BASE64_BUNDLE_ARG_RE = re.compile(
    r"\A\s*//\s*COMPILER:\s*base64_bundle\s+(\S+)", re.IGNORECASE
)


def apply_base64_bundle(file_path: Path) -> str:
    """Read the referenced file, base64-encode it, and append an eval(atob(...)).

    The source file should look like::

        // COMPILER: base64_bundle _ci-runner-src.js
        /**
         * ... comment block preserved in output ...
         */

    The directive line is stripped.  Everything after it (the comment block)
    is kept verbatim, and ``eval(atob("..."));`` is appended.
    """
    with open(file_path, "r", encoding="utf-8") as fh:
        first_line = fh.readline()
        rest = fh.read()

    m = _BASE64_BUNDLE_ARG_RE.match(first_line)
    if not m:
        raise ValueError(
            f"base64_bundle directive in {file_path} is missing a filename argument"
        )

    ref_name = m.group(1)
    ref_path = file_path.parent / ref_name

    if not ref_path.is_file():
        raise FileNotFoundError(f"base64_bundle: referenced file not found: {ref_path}")

    with open(ref_path, "r", encoding="utf-8") as fh:
        src = fh.read()

    # Strip a leading no_include directive line from the source if present
    src = re.sub(r"\A\s*//\s*COMPILER:\s*no_include[^\n]*\n?", "", src, count=1)

    encoded = base64.b64encode(src.encode("utf-8")).decode("ascii")
    return rest + f'eval(atob("{encoded}"));\n'


# ---------------------------------------------------------------------------
# challenge_page
# ---------------------------------------------------------------------------

_CHALLENGE_TEMPLATE_PATH = Path(__file__).with_name("challenge.html")

_DIFFICULTY_COLORS = {
    "easy": "#22c55e",
    "medium": "#e05a33",
    "hard": "#ef4444",
    "insane": "#a855f7",
}


def apply_challenge_page(file_path: Path) -> str:
    """Wrap challenge body content in the shared challenge page template.

    The source file should start with ``<!-- COMPILER: challenge_page -->``
    followed by the challenge-specific HTML body content (briefing, notes,
    hints, etc.).  The template provides the full page shell including
    back button, status badge, flag submission form, and confetti.

    Metadata is read from ``.challenge.json`` in the challenge root
    (expected at ``file_path.parent.parent``).
    """
    with open(file_path, "r", encoding="utf-8") as fh:
        first_line = fh.readline()
        body = fh.read().strip()

    # Find .challenge.json — challenge root is parent of challenge/
    challenge_root = file_path.parent.parent
    meta_file = challenge_root / ".challenge.json"
    meta: dict = {}
    if meta_file.exists():
        try:
            meta = json.loads(meta_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass

    slug = challenge_root.name
    title = meta.get("title", slug.replace("-", " ").replace("_", " ").title())
    difficulty = meta.get("difficulty", "Unknown")
    diff_color = _DIFFICULTY_COLORS.get(difficulty.lower(), "#6b7280")
    flag_hash = meta.get("flag_hash", "")

    template = _CHALLENGE_TEMPLATE_PATH.read_text(encoding="utf-8")

    html = (
        template
        .replace("{{TITLE}}", _html_escape(title))
        .replace("{{DIFFICULTY}}", _html_escape(difficulty))
        .replace("{{DIFF_COLOR}}", diff_color)
        .replace("{{SLUG}}", _html_escape(slug))
        .replace("{{FLAG_HASH}}", flag_hash)
        .replace("{{BODY}}", body)
    )

    return apply_shared_placeholders(html)


def _html_escape(text: str) -> str:
    """Minimal HTML/JS-safe escaping."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def apply_directive(
    file_path: Path,
    directive: str,
    url_prefix: str = "/",
) -> str:
    """Apply *directive* to *file_path* and return the transformed content."""
    if directive == "directory_listing":
        return apply_directory_listing(file_path, url_prefix)
    if directive == "html_minify":
        return apply_html_minify(file_path)
    if directive == "json_minify":
        return apply_json_minify(file_path)
    if directive == "base64_bundle":
        return apply_base64_bundle(file_path)
    if directive == "challenge_page":
        return apply_challenge_page(file_path)
    if directive == "no_include":
        # Should be handled by the caller (builder / server) — never applied.
        raise ValueError("no_include files should be skipped, not applied")
    raise ValueError(f"Unknown directive: {directive!r}")
