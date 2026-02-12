"""
Homepage generator for the CTF site.

Reads ``.challenge.json`` metadata from each challenge directory and
produces a root ``index.html`` that lists all challenges with a flag
submission form that verifies flags client-side via SHA-256 hashing.

The HTML template lives in ``compiler/homepage.html`` alongside this module.
"""

from __future__ import annotations

import json
from pathlib import Path

_TEMPLATE_PATH = Path(__file__).with_name("homepage.html")


def _load_template() -> str:
    """Read the HTML template from disk."""
    return _TEMPLATE_PATH.read_text(encoding="utf-8")


def _load_challenge_meta(challenge_dir: Path) -> dict | None:
    """Return parsed ``.challenge.json`` or *None* if it doesn't exist."""
    meta_file = challenge_dir / ".challenge.json"
    if not meta_file.exists():
        return None
    try:
        with open(meta_file, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except (json.JSONDecodeError, OSError):
        return None


_DIFFICULTY_COLORS = {
    "easy": "#22c55e",
    "medium": "#e05a33",
    "hard": "#ef4444",
    "insane": "#a855f7",
}


def generate_homepage(challenges: list[Path], dest: Path) -> None:
    """Generate ``dest/index.html`` listing all *challenges*.

    Each challenge directory should contain a ``.challenge.json`` file with
    keys: ``title``, ``difficulty``, ``summary``, ``flag_hash`` (SHA-256).
    """
    cards_html = []
    challenge_js_entries = []

    for cdir in sorted(challenges, key=lambda p: p.name):
        meta = _load_challenge_meta(cdir)
        if meta is None:
            # Minimal fallback card
            meta = {
                "title": cdir.name.replace("-", " ").replace("_", " ").title(),
                "difficulty": "Unknown",
                "summary": "No description available.",
                "flag_hash": "",
            }

        slug = cdir.name
        title = _escape(meta.get("title", slug))
        difficulty = meta.get("difficulty", "Unknown")
        diff_lower = difficulty.lower()
        diff_color = _DIFFICULTY_COLORS.get(diff_lower, "#6b7280")
        summary = _escape(meta.get("summary", ""))
        flag_hash = meta.get("flag_hash", "")

        cards_html.append(f"""\
        <div class="challenge-card" data-slug="{slug}">
          <div class="card-header">
            <span class="difficulty" style="color:{diff_color};background:{diff_color}22">{_escape(difficulty)}</span>
            <a class="card-title" href="/{slug}/challenge/">{title}</a>
          </div>
          <p class="card-summary">{summary}</p>
          <div class="card-footer">
            <a class="card-link" href="/{slug}/" target="_blank">Open challenge &rarr;</a>
            <form class="flag-form" data-slug="{slug}" onsubmit="return _checkFlag(event)">
              <input type="text" class="flag-input" placeholder="flag{{...}}" autocomplete="off" spellcheck="false" />
              <button type="submit" class="flag-btn">Submit</button>
            </form>
            <div class="flag-result" data-result="{slug}"></div>
          </div>
        </div>""")

        if flag_hash:
            challenge_js_entries.append(f'    "{slug}": "{flag_hash}"')

    cards_block = "\n".join(cards_html)
    hashes_js = ",\n".join(challenge_js_entries)

    html = (
        _load_template()
        .replace("{{CARDS}}", cards_block)
        .replace("{{HASHES}}", hashes_js)
        .replace("{{COUNT}}", str(len(challenges)))
    )

    dest.mkdir(parents=True, exist_ok=True)
    (dest / "index.html").write_text(html, encoding="utf-8")
    print(f"  homepage  index.html  ({len(challenges)} challenge(s))")


def _escape(text: str) -> str:
    """Minimal HTML escaping."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )
