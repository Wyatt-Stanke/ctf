"""
Homepage generator for the CTF site.

Reads ``.challenge.json`` metadata from each challenge directory and
produces a root ``index.html`` that lists all challenges with a flag
submission form that verifies flags client-side via SHA-256 hashing.

Challenges are rendered in collapsible groups based on the directory
structure (group directories contain ``.group.json``).

The HTML template lives in ``compiler/homepage.html`` alongside this module.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from compiler.cli import ChallengeGroup

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


def _build_card_html(cdir: Path) -> tuple[str, str | None]:
    """Return (card_html, js_hash_entry_or_None) for a single challenge."""
    meta = _load_challenge_meta(cdir)
    if meta is None:
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

    card = (
        f'          <div class="challenge-card" data-slug="{slug}">\n'
        f'            <div class="card-header">\n'
        f'              <span class="difficulty" style="color:{diff_color};background:{diff_color}22">{_escape(difficulty)}</span>\n'
        f'              <a class="card-title" href="./{slug}/challenge/">{title}</a>\n'
        f"            </div>\n"
        f'            <p class="card-summary">{summary}</p>\n'
        f'            <div class="card-footer">\n'
        f'              <a class="card-link" href="./{slug}/challenge/" target="_blank">Open challenge &rarr;</a>\n'
        f'              <form class="flag-form" data-slug="{slug}" onsubmit="return _checkFlag(event)">\n'
        f'                <input type="text" class="flag-input" placeholder="flag{{...}}" autocomplete="off" spellcheck="false" />\n'
        f'                <button type="submit" class="flag-btn">Submit</button>\n'
        f"              </form>\n"
        f'              <div class="flag-result" data-result="{slug}"></div>\n'
        f"            </div>\n"
        f"          </div>"
    )

    js_entry = f'    "{slug}": "{flag_hash}"' if flag_hash else None
    return card, js_entry


def generate_homepage(groups: list[ChallengeGroup], dest: Path) -> None:
    """Generate ``dest/index.html`` with collapsible grouped challenge cards.

    *groups* comes from ``compiler.cli._discover_groups()``.
    """
    sections_html = []
    all_js_entries = []
    total_challenges = 0

    for group in groups:
        cards = []
        for cdir in group.challenges:
            card_html, js_entry = _build_card_html(cdir)
            cards.append(card_html)
            if js_entry:
                all_js_entries.append(js_entry)
            total_challenges += 1

        cards_block = "\n".join(cards)
        count = len(group.challenges)
        desc_html = (
            f'\n          <p class="group-description">{_escape(group.description)}</p>'
            if group.description
            else ""
        )

        sections_html.append(
            f'        <div class="group" data-group="{_escape(group.slug)}">\n'
            f'          <div class="group-header" onclick="_toggleGroup(this)">\n'
            f'            <div class="group-header-left">\n'
            f'              <span class="group-chevron">&#9662;</span>\n'
            f'              <h2 class="group-title">{_escape(group.name)}</h2>\n'
            f'              <span class="group-count">{count}</span>\n'
            f"            </div>\n"
            f'            <span class="group-progress" data-group-progress="{_escape(group.slug)}"></span>\n'
            f"          </div>{desc_html}\n"
            f'          <div class="group-body">\n'
            f"{cards_block}\n"
            f"          </div>\n"
            f"        </div>"
        )

    groups_block = "\n\n".join(sections_html)
    hashes_js = ",\n".join(all_js_entries)

    # Build group membership map for JS: { slug: [challenge1, ...] }
    group_map_entries = []
    for group in groups:
        slugs = ", ".join(f'"{c.name}"' for c in group.challenges)
        group_map_entries.append(f'    "{_escape(group.slug)}": [{slugs}]')
    group_map_js = ",\n".join(group_map_entries)

    html = (
        _load_template()
        .replace("{{GROUPS}}", groups_block)
        .replace("{{HASHES}}", hashes_js)
        .replace("{{COUNT}}", str(total_challenges))
        .replace("{{GROUP_MAP}}", group_map_js)
    )

    dest.mkdir(parents=True, exist_ok=True)
    (dest / "index.html").write_text(html, encoding="utf-8")
    print(
        f"  homepage  index.html  ({total_challenges} challenge(s) in {len(groups)} group(s))"
    )


def _escape(text: str) -> str:
    """Minimal HTML escaping."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )
