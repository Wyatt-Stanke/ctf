/* ═══════════════════════════════════════════════════════════════
   Shared JS — included in both the homepage and challenge pages.
   Provides localStorage helpers, SHA-256 hashing, and the
   confetti particle engine.
   ═══════════════════════════════════════════════════════════════ */

/* ── localStorage helpers (shared key: "ctf_solved") ── */
function _getSolved() {
  try {
    return JSON.parse(localStorage.getItem("ctf_solved") || "{}");
  } catch {
    return {};
  }
}

function _setSolved(slug) {
  const s = _getSolved();
  s[slug] = true;
  localStorage.setItem("ctf_solved", JSON.stringify(s));
}

/* ── SHA-256 ── */
async function _sha256(str) {
  const buf = new TextEncoder().encode(str);
  const hash = await crypto.subtle.digest("SHA-256", buf);
  return Array.from(new Uint8Array(hash))
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
}

/* ── Confetti engine ── */
const _confetti = (() => {
  const canvas = document.getElementById("confettiCanvas");
  const ctx = canvas.getContext("2d");
  let particles = [];
  let running = false;

  function resize() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
  }
  window.addEventListener("resize", resize);
  resize();

  const COLORS = [
    "#22c55e",
    "#e05a33",
    "#fbbf24",
    "#a855f7",
    "#3b82f6",
    "#ec4899",
    "#f0f2f6",
  ];

  function spawn(x, y, count) {
    for (let i = 0; i < count; i++) {
      const angle = Math.random() * Math.PI * 2;
      const speed = 4 + Math.random() * 8;
      particles.push({
        x,
        y,
        vx: Math.cos(angle) * speed,
        vy: Math.sin(angle) * speed - 4,
        size: 4 + Math.random() * 6,
        color: COLORS[Math.floor(Math.random() * COLORS.length)],
        rotation: Math.random() * 360,
        rotSpeed: (Math.random() - 0.5) * 12,
        life: 1,
        decay: 0.008 + Math.random() * 0.012,
        shape: Math.random() > 0.5 ? "rect" : "circle",
      });
    }
    if (!running) {
      running = true;
      loop();
    }
  }

  function loop() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    for (let i = particles.length - 1; i >= 0; i--) {
      const p = particles[i];
      p.x += p.vx;
      p.y += p.vy;
      p.vy += 0.18;
      p.vx *= 0.99;
      p.rotation += p.rotSpeed;
      p.life -= p.decay;
      if (p.life <= 0) {
        particles.splice(i, 1);
        continue;
      }

      ctx.save();
      ctx.translate(p.x, p.y);
      ctx.rotate((p.rotation * Math.PI) / 180);
      ctx.globalAlpha = p.life;
      ctx.fillStyle = p.color;
      if (p.shape === "rect") {
        ctx.fillRect(-p.size / 2, -p.size / 2, p.size, p.size * 0.6);
      } else {
        ctx.beginPath();
        ctx.arc(0, 0, p.size / 2, 0, Math.PI * 2);
        ctx.fill();
      }
      ctx.restore();
    }
    if (particles.length > 0) {
      requestAnimationFrame(loop);
    } else {
      running = false;
    }
  }

  return {
    burst(el) {
      const rect = el.getBoundingClientRect();
      const cx = rect.left + rect.width / 2;
      const cy = rect.top + rect.height / 2;
      spawn(cx, cy, 60);
      setTimeout(() => spawn(cx - 60, cy - 20, 30), 100);
      setTimeout(() => spawn(cx + 60, cy - 20, 30), 200);
    },
  };
})();
