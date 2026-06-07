"""UI styles for 15-Puzzle AI academic dashboard."""

STYLES = """
<style>
/* Design tokens */
:root {
    color-scheme: dark;
    --bg-app: #0b1118;
    --bg-surface: #111923;
    --bg-elevated: #172232;
    --bg-panel: #101820;
    --accent: #2dd4bf;
    --accent-hover: #5eead4;
    --accent-glow: rgba(20,184,166,0.22);
    --accent-secondary: #f4b55f;
    --accent-tertiary: #93a4ff;
    --success: #22c55e;
    --success-glow: rgba(34,197,94,0.18);
    --error: #ef4444;
    --text-primary: #f8fafc;
    --text-secondary: #cbd5e1;
    --text-muted: #94a3b8;
    --border-subtle: rgba(148,163,184,0.22);
    --radius-sm: 6px;
    --radius-md: 8px;
    --radius-lg: 10px;
    --shadow-sm: 0 2px 4px rgba(0,0,0,0.4);
    --shadow-md: 0 8px 18px rgba(0,0,0,0.32);
    --shadow-lg: 0 18px 42px rgba(0,0,0,0.38);
    --font-stack: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    --transition-fast: 0.1s ease;
}

*, *::before, *::after {
    box-sizing: border-box;
}

html {
    touch-action: manipulation;
}

/* Global */
.stApp {
    background:
        linear-gradient(180deg, rgba(45,212,191,0.04), transparent 260px),
        var(--bg-app);
    font-family: var(--font-stack);
}
h1, h2, h3, h4, h5, h6 {
    color: var(--text-primary) !important;
    font-family: var(--font-stack);
    font-weight: 700 !important;
    letter-spacing: 0 !important;
    text-wrap: balance;
}
h1 {
    font-size: clamp(34px, 4vw, 46px) !important;
    line-height: 1.08 !important;
    margin-bottom: 16px !important;
}
p, li, label, div {
    color: var(--text-primary);
}
div[data-testid="stMainBlockContainer"] {
    max-width: 1120px;
    padding-top: 44px;
}
.stMetric label {
    color: var(--text-secondary) !important;
    font-size: 12px !important;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
.stMetric [data-testid="stMetricValue"] {
    font-size: 24px !important;
    font-weight: 700;
    color: var(--accent) !important;
    font-variant-numeric: tabular-nums;
}
div[data-testid="stMetric"] {
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-md);
    background: rgba(15,23,42,0.46);
    padding: 12px 14px;
}
button, input, textarea, select, [role="button"], [role="radio"], [role="checkbox"] {
    touch-action: manipulation;
}
button:focus-visible,
[role="button"]:focus-visible,
input:focus-visible,
textarea:focus-visible,
select:focus-visible,
[tabindex]:focus-visible {
    outline: 3px solid var(--accent-hover) !important;
    outline-offset: 3px !important;
    box-shadow: 0 0 0 4px rgba(20,184,166,0.18) !important;
}
button:disabled {
    cursor: not-allowed !important;
    opacity: 0.72 !important;
}

/* Academic dashboard panels */
.academic-hero {
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-lg);
    padding: 16px 18px;
    margin: 0 0 14px;
    background:
        linear-gradient(135deg, rgba(45,212,191,0.15), rgba(244,181,95,0.07)),
        rgba(16,24,32,0.92);
    box-shadow: var(--shadow-md);
}
.academic-kicker {
    color: var(--accent-hover) !important;
    font-size: 12px;
    font-weight: 800;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 6px;
}
.academic-hero h2 {
    margin: 0 0 6px !important;
    font-size: 25px !important;
    line-height: 1.22 !important;
}
.academic-hero p {
    color: var(--text-secondary) !important;
    margin: 0 !important;
    max-width: 900px;
    line-height: 1.55;
}
.academic-card {
    border: 1px solid var(--border-subtle);
    border-radius: 8px;
    background: rgba(16,24,32,0.84);
    padding: 14px 16px;
    min-height: 112px;
    box-shadow: var(--shadow-sm);
}
.academic-card-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(min(220px, 100%), 1fr));
    gap: 12px;
    margin: 8px 0 14px;
    max-width: 100%;
    min-width: 0;
    overflow: hidden;
}
.academic-record-card {
    border: 1px solid var(--border-subtle);
    border-radius: 8px;
    background: rgba(16,24,32,0.88);
    padding: 13px 14px;
    min-height: 104px;
    max-width: 100%;
    min-width: 0;
    overflow: hidden;
    overflow-wrap: anywhere;
}
.academic-record-card *,
.academic-card * {
    max-width: 100%;
    min-width: 0;
    overflow-wrap: anywhere;
}
.academic-record-card h4 {
    margin: 0 0 8px !important;
    font-size: 15px !important;
    line-height: 1.3 !important;
}
.academic-record-row {
    border-top: 1px solid rgba(148,163,184,0.14);
    padding-top: 7px;
    margin-top: 7px;
    font-size: 13px;
    line-height: 1.45;
}
.academic-record-label {
    color: var(--accent-hover) !important;
    display: block;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    margin-bottom: 2px;
}
.academic-card-title {
    color: var(--accent-hover) !important;
    font-weight: 800;
    font-size: 13px;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 8px;
}
.academic-card-body {
    color: var(--text-primary) !important;
    font-size: 14px;
    line-height: 1.55;
}
.exam-path {
    display: grid;
    grid-template-columns: repeat(5, minmax(0, 1fr));
    gap: 8px;
    margin: 2px 0 18px;
}
.exam-path-step {
    border: 1px solid rgba(148,163,184,0.2);
    border-radius: 8px;
    background: rgba(15,23,42,0.52);
    padding: 10px 11px;
    min-width: 0;
}
.exam-path-step.active {
    border-color: rgba(45,212,191,0.74);
    background: rgba(20,184,166,0.14);
    box-shadow: 0 0 0 1px rgba(45,212,191,0.12);
}
.exam-path-index {
    color: var(--accent-hover) !important;
    font-size: 11px;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}
.exam-path-title {
    color: var(--text-primary) !important;
    font-size: 13px;
    font-weight: 800;
    line-height: 1.25;
    margin-top: 3px;
}
.exam-path-note {
    color: var(--text-muted) !important;
    font-size: 12px;
    line-height: 1.35;
    margin-top: 4px;
}
.role-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    border-radius: 999px;
    padding: 5px 10px;
    font-size: 12px;
    font-weight: 800;
    letter-spacing: 0.02em;
    border: 1px solid rgba(255,255,255,0.18);
}
.role-real-solver { background: rgba(34,197,94,0.16); color: #bbf7d0 !important; }
.role-contrast-demo { background: rgba(245,158,11,0.18); color: #fde68a !important; }
.role-illustrative-extension { background: rgba(129,140,248,0.18); color: #c7d2fe !important; }
.role-stochastic-game-demo { background: rgba(244,114,182,0.18); color: #fbcfe8 !important; }
.academic-warning {
    border-left: 4px solid var(--accent-secondary);
    border-radius: 8px;
    background: rgba(245,158,11,0.12);
    padding: 12px 14px;
    color: var(--text-primary) !important;
    margin: 12px 0 16px;
}

@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
        animation-duration: 0.001ms !important;
        animation-iteration-count: 1 !important;
        scroll-behavior: auto !important;
        transition-duration: 0.001ms !important;
    }
}

@media (max-width: 640px) {
    div[data-testid="stMainBlockContainer"] {
        padding-left: 86px !important;
        padding-right: 12px !important;
        padding-top: 30px !important;
    }
    h1 {
        font-size: 28px !important;
        line-height: 1.18 !important;
        overflow-wrap: anywhere;
    }
    .academic-hero {
        padding: 14px 12px;
    }
    .academic-hero h2 {
        font-size: 21px !important;
        line-height: 1.25 !important;
    }
    .academic-card {
        min-height: auto;
        margin-bottom: 10px;
        overflow-wrap: anywhere;
    }
    .academic-card-grid {
        grid-template-columns: minmax(0, 1fr) !important;
    }
    .academic-record-card {
        min-height: auto;
    }
    .exam-path {
        grid-template-columns: minmax(0, 1fr);
    }
    section[data-testid="stSidebar"] {
        width: min(88vw, 340px) !important;
        min-width: min(88vw, 340px) !important;
        max-width: min(88vw, 340px) !important;
    }
    section[data-testid="stSidebar"] > div {
        width: 100% !important;
    }
    section[data-testid="stSidebar"][aria-expanded="false"] {
        pointer-events: none !important;
    }
    section[data-testid="stSidebar"][aria-expanded="true"] {
        pointer-events: auto !important;
    }
    section[data-testid="stSidebar"] [role="radiogroup"] label {
        white-space: normal !important;
        overflow-wrap: anywhere !important;
    }
    .puzzle-grid {
        width: min(100%, 280px);
        max-width: 280px;
        box-sizing: border-box;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 6px;
        padding: 10px;
        border-width: 6px;
    }
    .puzzle-tile {
        width: 100%;
        height: auto;
        aspect-ratio: 1 / 1;
        min-width: 0;
        font-size: 22px;
        box-sizing: border-box;
    }
    .puzzle-cell {
        width: 100% !important;
        max-width: 100% !important;
        height: auto !important;
        aspect-ratio: 1 / 1;
        min-width: 0;
        box-sizing: border-box;
        font-size: clamp(16px, 5vw, 22px) !important;
    }
}

/* ── Puzzle Board ───────────────────────────────────────────── */
.puzzle-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 8px;
    max-width: 348px;
    margin: 0 auto 16px;
    background: #020617;
    padding: 12px;
    border-radius: 12px;
    border: 7px solid #1c2736;
    box-shadow:
        0 16px 30px rgba(0,0,0,0.46),
        inset 0 6px 12px rgba(0,0,0,0.8),
        0 3px 0 #0f172a;
}

/* ── Game Tile (Tactile Wood) ─────────────────────────────────── */
.puzzle-tile {
    width: 72px;
    height: 72px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: 'Georgia', 'Playfair Display', serif;
    font-size: 28px;
    font-weight: 800;
    border-radius: 8px;
    user-select: none;
    position: relative;
    overflow: hidden;
    cursor: pointer;
    transition: transform 0.08s ease, box-shadow 0.08s ease;
    text-shadow: 0 1px 0 rgba(255,255,255,0.4);
}

.puzzle-tile.row-0 {
    background: linear-gradient(145deg, #99f6e4, #14b8a6) !important;
    color: #042f2e !important;
    box-shadow:
        0 4px 8px rgba(0,0,0,0.4),
        inset 0 1px 0 rgba(255,255,255,0.3);
    border-top: 1px solid rgba(255,255,255,0.3) !important;
    border-left: 1px solid rgba(255,255,255,0.1) !important;
    border-bottom: 3px solid #0f766e !important;
    border-right: 3px solid #0f766e !important;
}
.puzzle-tile.row-1 {
    background: linear-gradient(145deg, #bfdbfe, #3b82f6) !important;
    color: #0f172a !important;
    box-shadow:
        0 4px 8px rgba(0,0,0,0.4),
        inset 0 1px 0 rgba(255,255,255,0.25);
    border-top: 1px solid rgba(255,255,255,0.25) !important;
    border-left: 1px solid rgba(255,255,255,0.1) !important;
    border-bottom: 3px solid #1d4ed8 !important;
    border-right: 3px solid #1d4ed8 !important;
}
.puzzle-tile.row-2 {
    background: linear-gradient(145deg, #fde68a, #f59e0b) !important;
    color: #1f2937 !important;
    box-shadow:
        0 4px 8px rgba(0,0,0,0.4),
        inset 0 1px 0 rgba(255,255,255,0.2);
    border-top: 1px solid rgba(255,255,255,0.2) !important;
    border-left: 1px solid rgba(255,255,255,0.1) !important;
    border-bottom: 3px solid #b45309 !important;
    border-right: 3px solid #b45309 !important;
}
.puzzle-tile.row-3 {
    background: linear-gradient(145deg, #c4b5fd, #8b5cf6) !important;
    color: #f8fafc !important;
    box-shadow:
        0 4px 8px rgba(0,0,0,0.4),
        inset 0 1px 0 rgba(255,255,255,0.15);
    border-top: 1px solid rgba(255,255,255,0.15) !important;
    border-left: 1px solid rgba(255,255,255,0.08) !important;
    border-bottom: 3px solid #6d28d9 !important;
    border-right: 3px solid #6d28d9 !important;
    text-shadow: 0 -1px 0 rgba(0,0,0,0.5) !important;
}

.puzzle-tile:hover {
    transform: translateY(-2px);
    box-shadow:
        0 6px 12px rgba(0,0,0,0.5),
        inset 0 1px 0 rgba(255,255,255,0.4) !important;
}
.puzzle-tile:active {
    transform: scale(0.96);
    box-shadow: 0 2px 4px rgba(0,0,0,0.3) !important;
}

/* Correct position tiles (jade green) */
.puzzle-tile.correct {
    background: linear-gradient(145deg, #557c55, #3b5249) !important;
    color: #f7f4eb !important;
    box-shadow:
        0 4px 8px rgba(0,0,0,0.4),
        inset 0 1px 0 rgba(255,255,255,0.2) !important;
    border-top: 1px solid rgba(255,255,255,0.2) !important;
    border-left: 1px solid rgba(255,255,255,0.1) !important;
    border-bottom: 3px solid #283732 !important;
    border-right: 3px solid #283732 !important;
    text-shadow: 0 -1px 1px rgba(0,0,0,0.4) !important;
}

/* Blank tile with recessed design */
.puzzle-tile.blank {
    background: #1a100a !important;
    box-shadow: inset 0 5px 12px rgba(0,0,0,0.7) !important;
    border: 1px solid #140b07;
    cursor: default;
}
.puzzle-tile.blank::after {
    display: none;
}
.puzzle-tile.blank:hover {
    transform: none;
}

/* Slide animation */
@keyframes tileSlideFrom {
    from { transform: translate(var(--slide-from-x, 0), var(--slide-from-y, 0)); opacity: 0.9; }
    to   { transform: translate(0, 0); opacity: 1; }
}
.puzzle-tile.slide-anim {
    animation: tileSlideFrom 0.12s cubic-bezier(0.25, 1, 0.5, 1);
}

/* Goal pulse */
@keyframes goalPulse {
    0%, 100% { box-shadow: 0 4px 8px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.2); }
    50%      { box-shadow: 0 4px 16px #557c55, 0 0 8px #557c55, inset 0 1px 0 rgba(255,255,255,0.3); }
}
.puzzle-tile.correct.goal-flash { animation: goalPulse 0.4s ease-in-out 3; }

/* Board entrance */
@keyframes boardFadeIn {
    from { opacity: 0; transform: scale(0.98); }
    to   { opacity: 1; transform: scale(1); }
}
.puzzle-grid { animation: boardFadeIn 0.3s ease-out; }

/* ── Legacy puzzle-cell (for static displays like trace tables) ─ */
.puzzle-cell {
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: 'Georgia', 'Playfair Display', serif;
    font-weight: 800;
    border-radius: 8px;
    user-select: none;
    position: relative;
    overflow: hidden;
    text-shadow: 0 1px 1px rgba(255,255,255,0.4);
}
.puzzle-cell.filled {
    background: linear-gradient(145deg, #e8c59c, #be9c70);
    color: #3e220f;
    box-shadow: 
        0 4px 8px rgba(0,0,0,0.4),
        inset 0 1px 0 rgba(255,255,255,0.2);
    border-top: 1px solid rgba(255,255,255,0.3);
    border-left: 1px solid rgba(255,255,255,0.15);
    border-bottom: 3px solid #6b4d2e;
    border-right: 3px solid #6b4d2e;
}
.puzzle-cell.blank {
    background: #1a100a !important;
    box-shadow: inset 0 4px 10px rgba(0,0,0,0.7) !important;
    border: 1px solid #140b07 !important;
    color: transparent !important;
}
.puzzle-cell.correct {
    background: linear-gradient(145deg, #557c55, #3b5249) !important;
    color: #f7f4eb !important;
    box-shadow: 
        0 4px 8px rgba(0,0,0,0.4),
        inset 0 1px 0 rgba(255,255,255,0.2) !important;
    border-top: 1px solid rgba(255,255,255,0.2) !important;
    border-left: 1px solid rgba(255,255,255,0.1) !important;
    border-bottom: 3px solid #283732 !important;
    border-right: 3px solid #283732 !important;
    text-shadow: 0 -1px 1px rgba(0,0,0,0.4) !important;
}
.puzzle-cell img.tile-img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    border-radius: 6px;
    position: absolute;
    top: 0;
    left: 0;
}
@keyframes slideIn {
    from { transform: scale(0.9); opacity: 0.7; }
    to   { transform: scale(1); opacity: 1; }
}
.puzzle-cell.slide-in { animation: slideIn 0.1s ease-out; }

/* ── Mini puzzle grid (trace tables) ────────────────────────── */
.puzzle-grid-mini {
    display: inline-grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 2px;
    background: #1a100a;
    padding: 4px;
    border-radius: 6px;
    font-size: 8px;
    margin: 2px 0;
    border: 1px solid #3c2415;
}
.puzzle-grid-mini .mc {
    width: 18px; height: 18px;
    display: flex; align-items: center; justify-content: center;
    border-radius: 3px;
    font-weight: 700;
    font-size: 8px;
}
.puzzle-grid-mini .mc.f { 
    background: linear-gradient(135deg, #e8c59c, #be9c70); 
    color: #3e220f; 
    border-bottom: 1px solid #6b4d2e;
}
.puzzle-grid-mini .mc.b { 
    background: transparent; 
}
.puzzle-grid-mini .mc.c { 
    background: linear-gradient(135deg, #557c55, #3b5249); 
    color: #f7f4eb; 
    border-bottom: 1px solid #283732;
}

/* ── Result cards ────────────────────────────────────────────── */
.result-success {
    border-left: 4px solid var(--success);
    background: linear-gradient(90deg, rgba(85,124,85,0.12), transparent);
    padding: 12px 16px;
    border-radius: var(--radius-sm);
    margin: 8px 0;
}
.result-failure {
    border-left: 4px solid var(--error);
    background: linear-gradient(90deg, rgba(175,77,77,0.12), transparent);
    padding: 12px 16px;
    border-radius: var(--radius-sm);
    margin: 8px 0;
}

/* ── Group badges ────────────────────────────────────────────── */
.group-badge {
    display: inline-block;
    padding: 4px 14px;
    border-radius: 16px;
    font-size: 11px;
    font-weight: 700;
    margin-right: 6px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
.group-uninformed { background: linear-gradient(135deg, #705335, #503820); color: #f0e6dc; }
.group-informed  { background: linear-gradient(135deg, #a67f56, #805c36); color: #f0e6dc; }
.group-local      { background: linear-gradient(135deg, #a35d46, #80402b); color: #f0e6dc; }
.group-complex    { background: linear-gradient(135deg, #7c587f, #5a3c5d); color: #f0e6dc; }
.group-csp        { background: linear-gradient(135deg, #5c7e5a, #405c3e); color: #f0e6dc; }
.group-adversarial { background: linear-gradient(135deg, #a84444, #7f2b2b); color: #f0e6dc; }

/* ── Scrollbar ───────────────────────────────────────────────── */
.scroll-container {
    max-height: 400px;
    overflow-y: auto;
    padding-right: 8px;
}
.scroll-container::-webkit-scrollbar { width: 6px; }
.scroll-container::-webkit-scrollbar-track { background: var(--bg-surface); border-radius: 3px; }
.scroll-container::-webkit-scrollbar-thumb { background: var(--accent); border-radius: 3px; }
.scroll-container::-webkit-scrollbar-thumb:hover { background: var(--accent-hover); }

/* ── Sidebar ─────────────────────────────────────────────────── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0e151d 0%, #0a0f14 100%) !important;
    border-right: 1px solid rgba(148,163,184,0.16);
}
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    letter-spacing: 0 !important;
}
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] p {
    font-size: 13px !important;
    line-height: 1.35 !important;
}
section[data-testid="stSidebar"] [role="radiogroup"] label {
    border-radius: 7px;
    padding: 3px 6px;
}
section[data-testid="stSidebar"] [role="radiogroup"] label:hover {
    background: rgba(45,212,191,0.08);
}

/* ── Section dividers ────────────────────────────────────────── */
.section-divider {
    border: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--accent), transparent);
    margin: 20px 0;
}

/* ── Detail grid text (monospace for trace) ──────────────────── */
.detail-grid-text {
    font-family: 'Cascadia Code', 'Fira Code', 'Consolas', monospace;
    font-size: 11px;
    line-height: 1.4;
    color: var(--text-primary);
    background: var(--bg-app);
    padding: 8px 10px;
    border-radius: var(--radius-sm);
    margin: 3px 0;
}

/* ── Interactive Play Board alignment and styles ── */
div.interactive-board-container-number, div.interactive-board-container-image {
    display: none;
}

div[data-testid="stVerticalBlock"]:has(.interactive-board-container-number) button {
    width: 100% !important;
    aspect-ratio: 1 !important;
    height: auto !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    font-family: 'Georgia', 'Playfair Display', serif !important;
    font-size: 28px !important;
    font-weight: 800 !important;
    border-radius: 10px !important;
    margin: 0 !important;
    padding: 0 !important;
    color: #3e220f !important;
    background: linear-gradient(145deg, #f3d4af, #caa97e) !important;
    box-shadow: 
        0 6px 12px rgba(0,0,0,0.4),
        inset 0 1px 0 rgba(255,255,255,0.3) !important;
    border-top: 1px solid rgba(255,255,255,0.4) !important;
    border-left: 1px solid rgba(255,255,255,0.2) !important;
    border-bottom: 4px solid #6b4c2e !important;
    border-right: 4px solid #6b4c2e !important;
    transition: transform 0.08s ease, box-shadow 0.08s ease !important;
    text-shadow: 0 1px 0 rgba(255,255,255,0.4) !important;
    cursor: pointer !important;
}

div[data-testid="stVerticalBlock"]:has(.interactive-board-container-number) button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 
        0 8px 16px rgba(0,0,0,0.5),
        inset 0 1px 0 rgba(255,255,255,0.4) !important;
    background: linear-gradient(145deg, #f7dfbe, #d4b58b) !important;
}

div[data-testid="stVerticalBlock"]:has(.interactive-board-container-number) button:active {
    transform: scale(0.96) translateY(2px) !important;
    border-bottom: 1px solid #503720 !important;
    border-right: 1px solid #503720 !important;
    box-shadow: 0 2px 4px rgba(0,0,0,0.3) !important;
}

/* Ensure puzzle tiles in the number container are responsive squares */
div[data-testid="stVerticalBlock"]:has(.interactive-board-container-number) .puzzle-tile {
    width: 100% !important;
    aspect-ratio: 1 !important;
    height: auto !important;
    margin: 0 !important;
}

/* Styles for image board buttons (tactile low-profile tabs) */
div[data-testid="stVerticalBlock"]:has(.interactive-board-container-image) button {
    width: 100% !important;
    height: 28px !important;
    line-height: 28px !important;
    margin-top: 4px !important;
    padding: 0 !important;
    background: #4a3319 !important;
    border: 1px solid #36220f !important;
    color: #e6dfd5 !important;
    border-radius: 6px !important;
    font-size: 12px !important;
    font-weight: 600 !important;
    box-shadow: 0 2px 4px rgba(0,0,0,0.3) !important;
}
div[data-testid="stVerticalBlock"]:has(.interactive-board-container-image) button:hover:not(:disabled) {
    background: #624629 !important;
    color: #ffffff !important;
    transform: translateY(-1px) !important;
}
div[data-testid="stVerticalBlock"]:has(.interactive-board-container-image) button:disabled {
    visibility: hidden !important;
}

/* Premium AI Solver Card */
.ai-solver-card {
    background: linear-gradient(135deg, #251e19 0%, #1c1511 100%) !important;
    border: 1px solid rgba(200, 149, 108, 0.25) !important;
    border-radius: 12px !important;
    padding: 16px 20px !important;
    margin: 16px 0 !important;
    box-shadow: 0 8px 24px rgba(0,0,0,0.5) !important;
}
.ai-solver-header {
    display: flex !important;
    align-items: center !important;
    justify-content: space-between !important;
    border-bottom: 1px solid rgba(200, 149, 108, 0.15) !important;
    padding-bottom: 10px !important;
    margin-bottom: 12px !important;
}
.ai-solver-title-container {
    display: flex !important;
    align-items: center !important;
    gap: 8px !important;
}
.ai-solver-title-container h3 {
    margin: 0 !important;
    font-size: 18px !important;
    font-weight: 700 !important;
    color: #f0e6dc !important;
    letter-spacing: 0.5px !important;
}
.ai-solver-badge {
    background: rgba(200, 149, 108, 0.15) !important;
    border: 1px solid #c8956c !important;
    color: #c8956c !important;
    font-size: 10px !important;
    font-weight: 800 !important;
    padding: 2px 8px !important;
    border-radius: 4px !important;
    letter-spacing: 0.5px !important;
    text-transform: uppercase !important;
}
.ai-solver-desc {
    font-size: 13.5px !important;
    color: #a6988f !important;
    line-height: 1.5 !important;
    margin: 0 !important;
}
</style>
"""

GROUP_COLORS = {
    "Uninformed Search": {"badge": "group-uninformed", "color": "#6366f1", "bg": "#4f46e5",
                           "icon": "Search", "emoji": ""},
    "Informed Search": {"badge": "group-informed", "color": "#818cf8", "bg": "#6366f1",
                        "icon": "Lightbulb", "emoji": ""},
    "Local Search": {"badge": "group-local", "color": "#e11d48", "bg": "#e11d48",
                     "icon": "Terrain", "emoji": ""},
    "Complex Environments": {"badge": "group-complex", "color": "#7c3aed", "bg": "#7c3aed",
                             "icon": "Globe", "emoji": ""},
    "CSP": {"badge": "group-csp", "color": "#22c55e", "bg": "#22c55e",
            "icon": "Grid", "emoji": ""},
    "Adversarial/Stochastic": {"badge": "group-adversarial", "color": "#ef4444", "bg": "#ef4444",
                               "icon": "Sword", "emoji": ""},
}

ALGORITHM_GROUPS = {
    "Uninformed Search": ["BFS", "DFS", "UCS", "IDS"],
    "Informed Search": ["Greedy Best-First", "A*", "IDA*"],
    "Local Search": ["Simple Hill Climbing", "Steepest-Ascent Hill Climbing",
                     "Stochastic Hill Climbing", "Random-Restart Hill Climbing",
                     "Local Beam Search", "Simulated Annealing"],
    "Complex Environments": ["AND-OR Search", "No Observation Search",
                            "Partially Observable Search", "LRTA*"],
    "CSP": ["CSP Definition", "Constraint Propagation", "Path Consistency",
            "Global Constraints", "Backtracking Search", "Min-Conflicts",
            "Constraint Graphs"],
    "Adversarial/Stochastic": ["Minimax", "Alpha-Beta Pruning", "Expectimax"],
}

ALGORITHM_FN_MAP = {
    "BFS": "bfs", "DFS": "dfs", "UCS": "ucs", "IDS": "ids",
    "Greedy Best-First": "greedy_best_first", "A*": "a_star", "IDA*": "ida_star",
    "Simple Hill Climbing": "simple_hill_climbing",
    "Steepest-Ascent Hill Climbing": "steepest_ascent_hill_climbing",
    "Stochastic Hill Climbing": "stochastic_hill_climbing",
    "Random-Restart Hill Climbing": "random_restart_hill_climbing",
    "Local Beam Search": "local_beam_search",
    "Simulated Annealing": "simulated_annealing",
    "AND-OR Search": "and_or_search",
    "No Observation Search": "no_observation_search",
    "Partially Observable Search": "partially_observable_search",
    "LRTA*": "online_search_lrta",
    "CSP Definition": "csp_definition",
    "Constraint Propagation": "constraint_propagation",
    "Path Consistency": "path_consistency",
    "Global Constraints": "global_constraints",
    "Backtracking Search": "backtracking_search",
    "Min-Conflicts": "min_conflicts",
    "Constraint Graphs": "solve_csp_constraint_graphs",
    "Minimax": "minimax",
    "Alpha-Beta Pruning": "alpha_beta_pruning",
    "Expectimax": "expectimax",
}

THEORY_KEY_MAP = {
    "BFS": "BFS", "DFS": "DFS", "UCS": "UCS", "IDS": "IDS",
    "Greedy Best-First": "Greedy", "A*": "A*", "IDA*": "IDA*",
    "Simple Hill Climbing": "Simple HC",
    "Steepest-Ascent Hill Climbing": "Steepest Ascent HC",
    "Stochastic Hill Climbing": "Stochastic HC",
    "Random-Restart Hill Climbing": "Random-Restart HC",
    "Local Beam Search": "Local Beam Search",
    "Simulated Annealing": "Simulated Annealing",
    "AND-OR Search": "AND-OR",
    "No Observation Search": "No Observation",
    "Partially Observable Search": "Partially Observable",
    "LRTA*": "LRTA*",
    "CSP Definition": "CSP Definition",
    "Constraint Propagation": "Constraint Propagation",
    "Path Consistency": "Path Consistency",
    "Global Constraints": "Global Constraints",
    "Backtracking Search": "Backtracking Search",
    "Min-Conflicts": "Min-Conflicts",
    "Constraint Graphs": "Constraint Graphs",
    "Minimax": "Minimax",
    "Alpha-Beta Pruning": "Alpha-Beta",
    "Expectimax": "Expectimax",
}

COMPARISON_TABLE = [
    {"Group": "Uninformed", "Algorithm": "BFS", "Complete": "Yes", "Optimal": "Yes*", "Heuristic": "No", "Random": "No", "Suitable": "Limited (memory)"},
    {"Group": "Uninformed", "Algorithm": "DFS", "Complete": "No", "Optimal": "No", "Heuristic": "No", "Random": "No", "Suitable": "No"},
    {"Group": "Uninformed", "Algorithm": "UCS", "Complete": "Yes", "Optimal": "Yes", "Heuristic": "No", "Random": "No", "Suitable": "Same as BFS"},
    {"Group": "Uninformed", "Algorithm": "IDS", "Complete": "Yes", "Optimal": "Yes*", "Heuristic": "No", "Random": "No", "Suitable": "Good (low memory)"},
    {"Group": "Informed", "Algorithm": "Greedy", "Complete": "No", "Optimal": "No", "Heuristic": "h(n)", "Random": "No", "Suitable": "Fast, suboptimal"},
    {"Group": "Informed", "Algorithm": "A*", "Complete": "Yes", "Optimal": "Yes", "Heuristic": "g+h", "Random": "No", "Suitable": "Best choice"},
    {"Group": "Informed", "Algorithm": "IDA*", "Complete": "Yes", "Optimal": "Yes", "Heuristic": "g+h", "Random": "No", "Suitable": "Memory efficient"},
    {"Group": "Local", "Algorithm": "Hill Climbing", "Complete": "No", "Optimal": "No", "Heuristic": "h(n)", "Random": "No", "Suitable": "Gets stuck"},
    {"Group": "Local", "Algorithm": "Steepest HC", "Complete": "No", "Optimal": "No", "Heuristic": "h(n)", "Random": "No", "Suitable": "Gets stuck"},
    {"Group": "Local", "Algorithm": "Stochastic HC", "Complete": "No", "Optimal": "No", "Heuristic": "h(n)", "Random": "Yes", "Suitable": "Gets stuck"},
    {"Group": "Local", "Algorithm": "Random-Restart HC", "Complete": "No", "Optimal": "No", "Heuristic": "h(n)", "Random": "Yes", "Suitable": "May find solution"},
    {"Group": "Local", "Algorithm": "Beam Search", "Complete": "No", "Optimal": "No", "Heuristic": "h(n)", "Random": "No", "Suitable": "Better than HC"},
    {"Group": "Local", "Algorithm": "Sim. Annealing", "Complete": "No", "Optimal": "No", "Heuristic": "h(n)", "Random": "Yes", "Suitable": "Unreliable"},
    {"Group": "Complex", "Algorithm": "AND-OR", "Complete": "No", "Optimal": "No", "Heuristic": "h(n)", "Random": "No", "Suitable": "Extended env"},
    {"Group": "Complex", "Algorithm": "No Observation", "Complete": "No", "Optimal": "No", "Heuristic": "h(n)", "Random": "No", "Suitable": "Illustrative"},
    {"Group": "Complex", "Algorithm": "Partial Obs.", "Complete": "No", "Optimal": "No", "Heuristic": "h(n)", "Random": "No", "Suitable": "Illustrative"},
    {"Group": "Complex", "Algorithm": "LRTA*", "Complete": "No", "Optimal": "No", "Heuristic": "h(n)", "Random": "No", "Suitable": "Online demo"},
    {"Group": "CSP", "Algorithm": "CSP Definition", "Complete": "-", "Optimal": "-", "Heuristic": "No", "Random": "No", "Suitable": "Illustrative"},
    {"Group": "CSP", "Algorithm": "Propagation", "Complete": "-", "Optimal": "-", "Heuristic": "No", "Random": "No", "Suitable": "Illustrative"},
    {"Group": "CSP", "Algorithm": "Path Consistency", "Complete": "-", "Optimal": "-", "Heuristic": "No", "Random": "No", "Suitable": "Illustrative"},
    {"Group": "CSP", "Algorithm": "Global Constraints", "Complete": "-", "Optimal": "-", "Heuristic": "No", "Random": "No", "Suitable": "Illustrative"},
    {"Group": "CSP", "Algorithm": "Constraint Graphs", "Complete": "-", "Optimal": "-", "Heuristic": "No", "Random": "No", "Suitable": "Illustrative"},
    {"Group": "CSP", "Algorithm": "Backtracking", "Complete": "No", "Optimal": "No", "Heuristic": "MRV+LCV", "Random": "No", "Suitable": "Planning demo"},
    {"Group": "CSP", "Algorithm": "Min-Conflicts", "Complete": "No", "Optimal": "No", "Heuristic": "Conflicts", "Random": "Yes", "Suitable": "N-Queens better"},
    {"Group": "Adversarial", "Algorithm": "Minimax", "Complete": "No", "Optimal": "No", "Heuristic": "utility h", "Random": "No", "Suitable": "Game demo"},
    {"Group": "Adversarial", "Algorithm": "Alpha-Beta", "Complete": "No", "Optimal": "No", "Heuristic": "utility h", "Random": "No", "Suitable": "Pruning demo"},
    {"Group": "Adversarial", "Algorithm": "Expectimax", "Complete": "No", "Optimal": "No", "Heuristic": "utility h", "Random": "Chance", "Suitable": "Stochastic demo"},
]

NOTES = """
* Optimal with unit cost. UCS = BFS for 15-puzzle (all moves cost 1).
  Greedy may find optimal path by chance but does NOT guarantee it.
  Hill Climbing variants typically get stuck at local optima on 15-puzzle.
  CSP, complex-environment, Minimax, Alpha-Beta, and Expectimax entries are illustrative extensions, not natural 15-puzzle solvers.
"""
