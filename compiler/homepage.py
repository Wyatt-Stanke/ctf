"""
Homepage generator for the CTF site.

Reads ``.challenge.json`` metadata from each challenge directory and
produces a root ``index.html`` that lists all challenges with a flag
submission form that verifies flags client-side via SHA-256 hashing.
"""

from __future__ import annotations

import json
from pathlib import Path


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
        _TEMPLATE.replace("{{CARDS}}", cards_block)
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


# ---------------------------------------------------------------------------
# HTML template
# ---------------------------------------------------------------------------

_TEMPLATE = """\
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>CTF Challenges</title>
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link
      href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&family=Source+Serif+4:ital,wght@0,400;0,600;1,400&display=swap"
      rel="stylesheet"
    />
    <style>
      *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

      :root {
        --bg: #0c0e13;
        --surface: #13161d;
        --surface-2: #1a1e27;
        --border: #2a2f3a;
        --text: #c8cdd8;
        --text-dim: #6b7280;
        --accent: #e05a33;
        --accent-glow: #e05a3344;
        --green: #22c55e;
        --red: #ef4444;
        --yellow: #fbbf24;
      }

      body {
        font-family: "Source Serif 4", Georgia, serif;
        background: var(--bg);
        color: var(--text);
        min-height: 100vh;
        display: flex;
        justify-content: center;
        padding: 60px 20px;
        line-height: 1.7;
      }

      .container { max-width: 720px; width: 100%; }

      .site-header {
        margin-bottom: 40px;
      }

      .site-tag {
        display: inline-block;
        font-family: "JetBrains Mono", monospace;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 2px;
        text-transform: uppercase;
        color: var(--accent);
        background: var(--accent-glow);
        padding: 4px 12px;
        border-radius: 3px;
        margin-bottom: 12px;
      }

      h1 {
        font-family: "JetBrains Mono", monospace;
        font-size: 28px;
        font-weight: 700;
        color: #f0f2f6;
        margin-bottom: 8px;
        line-height: 1.3;
      }

      .subtitle {
        font-size: 17px;
        color: var(--text-dim);
      }

      .progress-bar {
        margin-top: 20px;
        background: var(--surface-2);
        border: 1px solid var(--border);
        border-radius: 6px;
        padding: 16px 20px;
        display: flex;
        align-items: center;
        gap: 16px;
      }

      .progress-track {
        flex: 1;
        height: 6px;
        background: var(--surface);
        border-radius: 3px;
        overflow: hidden;
      }

      .progress-fill {
        height: 100%;
        background: var(--green);
        border-radius: 3px;
        transition: width 0.4s ease;
      }

      .progress-label {
        font-family: "JetBrains Mono", monospace;
        font-size: 13px;
        color: var(--text-dim);
        white-space: nowrap;
      }

      /* Challenge cards */
      .challenge-card {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 8px;
        padding: 28px 32px;
        margin-bottom: 20px;
        transition: border-color 0.2s, box-shadow 0.2s;
      }

      .challenge-card:hover {
        border-color: var(--accent);
        box-shadow: 0 0 20px var(--accent-glow);
      }

      .challenge-card.solved {
        border-color: var(--green);
        box-shadow: 0 0 20px #22c55e22;
      }

      .card-header {
        display: flex;
        align-items: center;
        gap: 14px;
        margin-bottom: 12px;
      }

      .difficulty {
        font-family: "JetBrains Mono", monospace;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 2px;
        text-transform: uppercase;
        padding: 3px 10px;
        border-radius: 3px;
        flex-shrink: 0;
      }

      .card-title {
        font-family: "JetBrains Mono", monospace;
        font-size: 20px;
        font-weight: 700;
        color: #f0f2f6;
        text-decoration: none;
        transition: color 0.15s;
      }

      .card-title:hover { color: var(--accent); }

      .card-summary {
        font-size: 15px;
        color: var(--text-dim);
        margin-bottom: 20px;
        line-height: 1.6;
      }

      .card-footer {
        display: flex;
        flex-wrap: wrap;
        align-items: center;
        gap: 12px;
      }

      .card-link {
        font-family: "JetBrains Mono", monospace;
        font-size: 13px;
        color: var(--accent);
        text-decoration: none;
        transition: opacity 0.15s;
        margin-right: auto;
      }

      .card-link:hover { opacity: 0.8; }

      .flag-form {
        display: flex;
        gap: 8px;
        align-items: center;
      }

      .flag-input {
        font-family: "JetBrains Mono", monospace;
        font-size: 13px;
        background: var(--surface-2);
        border: 1px solid var(--border);
        border-radius: 4px;
        color: var(--text);
        padding: 7px 12px;
        width: 200px;
        outline: none;
        transition: border-color 0.15s;
      }

      .flag-input:focus { border-color: var(--accent); }

      .flag-btn {
        font-family: "JetBrains Mono", monospace;
        font-size: 12px;
        font-weight: 700;
        color: #f0f2f6;
        background: var(--accent);
        border: none;
        border-radius: 4px;
        padding: 8px 16px;
        cursor: pointer;
        transition: opacity 0.15s;
      }

      .flag-btn:hover { opacity: 0.85; }

      .flag-result {
        font-family: "JetBrains Mono", monospace;
        font-size: 12px;
        min-height: 18px;
        width: 100%;
        margin-top: 4px;
      }

      .flag-result.correct {
        color: var(--green);
      }

      .flag-result.incorrect {
        color: var(--red);
      }

      .solved-badge {
        font-family: "JetBrains Mono", monospace;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 1px;
        text-transform: uppercase;
        color: var(--green);
        background: #22c55e22;
        padding: 3px 10px;
        border-radius: 3px;
      }

      @media (max-width: 600px) {
        .card-footer { flex-direction: column; align-items: flex-start; }
        .flag-input { width: 100%; }
        .flag-form { width: 100%; }
      }
    </style>
  </head>
  <body>
    <div class="container">
      <div class="site-header">
        <div class="site-tag">Capture the Flag</div>
        <h1>Challenges</h1>
        <p class="subtitle">{{COUNT}} challenge(s) available. Submit flags below to track your progress.</p>

        <div class="progress-bar">
          <span class="progress-label" id="progressText">0 / {{COUNT}} solved</span>
          <div class="progress-track">
            <div class="progress-fill" id="progressFill" style="width: 0%"></div>
          </div>
        </div>
      </div>

{{CARDS}}
    </div>

    <script>
      const FLAG_HASHES = {
{{HASHES}}
      };

      const TOTAL = Object.keys(FLAG_HASHES).length;

      // Persist solved state in localStorage
      function _getSolved() {
        try {
          return JSON.parse(localStorage.getItem("ctf_solved") || "{}");
        } catch { return {}; }
      }

      function _setSolved(slug) {
        const s = _getSolved();
        s[slug] = true;
        localStorage.setItem("ctf_solved", JSON.stringify(s));
      }

      function _updateProgress() {
        const solved = _getSolved();
        const count = Object.keys(FLAG_HASHES).filter(k => solved[k]).length;
        document.getElementById("progressText").textContent = count + " / " + TOTAL + " solved";
        document.getElementById("progressFill").style.width = (TOTAL ? (count / TOTAL) * 100 : 0) + "%";

        // Update card styles
        for (const slug of Object.keys(FLAG_HASHES)) {
          const card = document.querySelector(`.challenge-card[data-slug="${slug}"]`);
          if (!card) continue;
          const resultEl = card.querySelector(".flag-result");
          if (solved[slug]) {
            card.classList.add("solved");
            if (resultEl && !resultEl.textContent) {
              resultEl.className = "flag-result correct";
              resultEl.innerHTML = '<span class="solved-badge">&#10003; Solved</span>';
            }
          }
        }
      }

      async function _sha256(str) {
        const buf = new TextEncoder().encode(str);
        const hash = await crypto.subtle.digest("SHA-256", buf);
        return Array.from(new Uint8Array(hash)).map(b => b.toString(16).padStart(2, "0")).join("");
      }

      async function _checkFlag(e) {
        e.preventDefault();
        const form = e.target;
        const slug = form.dataset.slug;
        const input = form.querySelector(".flag-input");
        const resultEl = document.querySelector(`[data-result="${slug}"]`);
        const value = input.value.trim();

        if (!value) return false;

        const expected = FLAG_HASHES[slug];
        if (!expected) {
          resultEl.className = "flag-result incorrect";
          resultEl.textContent = "No hash configured for this challenge.";
          return false;
        }

        const hash = await _sha256(value);

        if (hash === expected) {
          resultEl.className = "flag-result correct";
          resultEl.innerHTML = '<span class="solved-badge">&#10003; Correct!</span>';
          _setSolved(slug);
          _updateProgress();
        } else {
          resultEl.className = "flag-result incorrect";
          resultEl.textContent = "Incorrect flag. Try again.";
          input.classList.add("shake");
          setTimeout(() => input.classList.remove("shake"), 400);
        }

        return false;
      }

      // Init on load
      _updateProgress();
    </script>

    <style>
      @keyframes shake {
        0%, 100% { transform: translateX(0); }
        20%, 60% { transform: translateX(-4px); }
        40%, 80% { transform: translateX(4px); }
      }
      .shake { animation: shake 0.3s ease; }
    </style>
  </body>
</html>
"""
