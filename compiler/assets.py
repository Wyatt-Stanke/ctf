"""
Shared asset loader for the CTF compiler.

Reads ``shared.css`` and ``shared.js`` once and caches them so both
the homepage generator and the challenge-page directive can inline
them into their templates via ``{{SHARED_CSS}}`` and ``{{SHARED_JS}}``
placeholders.
"""

from __future__ import annotations

from pathlib import Path

_DIR = Path(__file__).parent

_css_cache: str | None = None
_js_cache: str | None = None


def shared_css() -> str:
    """Return the contents of ``shared.css``."""
    global _css_cache
    if _css_cache is None:
        _css_cache = (_DIR / "shared.css").read_text(encoding="utf-8")
    return _css_cache


def shared_js() -> str:
    """Return the contents of ``shared.js``."""
    global _js_cache
    if _js_cache is None:
        _js_cache = (_DIR / "shared.js").read_text(encoding="utf-8")
    return _js_cache


def apply_shared_placeholders(html: str) -> str:
    """Replace ``{{SHARED_CSS}}`` and ``{{SHARED_JS}}`` in *html*."""
    return html.replace("{{SHARED_CSS}}", shared_css()).replace(
        "{{SHARED_JS}}", shared_js()
    )
