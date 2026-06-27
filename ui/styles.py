"""UI styles for 15-Puzzle AI academic dashboard."""

STYLES = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Be+Vietnam+Pro:wght@400;500;600;700;800&family=Fira+Code:wght@400;500;600;700&display=swap');

/* Design tokens: tactile solver laboratory */
:root {
    color-scheme: dark;
    --bg-app: #0e1110;
    --bg-surface: #151817;
    --bg-elevated: #1c211f;
    --bg-panel: #121514;
    --surface-ink: #0a0d0c;
    --surface-paper: #211d17;
    --surface-copper: #332618;
    --accent: #d6a15f;
    --accent-hover: #f0c989;
    --accent-glow: rgba(214,161,95,0.18);
    --accent-secondary: #c69053;
    --accent-tertiary: #8ca18e;
    --success: #7aa66a;
    --success-glow: rgba(122,166,106,0.18);
    --error: #d66a5f;
    --warning: #d6a15f;
    --text-primary: #f4efe5;
    --text-secondary: #d2c7b8;
    --text-muted: #9f9588;
    --text-faint: #70685f;
    --border-subtle: rgba(214,196,166,0.18);
    --border-strong: rgba(240,201,137,0.38);
    --radius-sm: 5px;
    --radius-md: 9px;
    --radius-lg: 15px;
    --radius-xl: 22px;
    --shadow-sm: 0 2px 0 rgba(255,255,255,0.03), 0 10px 24px rgba(4,7,6,0.26);
    --shadow-md: 0 1px 0 rgba(255,255,255,0.05) inset, 0 18px 40px rgba(4,7,6,0.34);
    --shadow-lg: 0 1px 0 rgba(255,255,255,0.06) inset, 0 28px 70px rgba(4,7,6,0.48);
    --font-stack: "Be Vietnam Pro", "Fira Sans", Aptos, "Segoe UI", ui-sans-serif, sans-serif;
    --font-mono: "Fira Code", "Cascadia Code", "JetBrains Mono", Consolas, monospace;
    --font-display: "Be Vietnam Pro", "Fira Sans", Aptos, "Segoe UI", ui-sans-serif, sans-serif;
    --ease-lab: cubic-bezier(0.22, 1, 0.36, 1);
    --transition-fast: 0.16s var(--ease-lab);
    --transition-med: 0.24s var(--ease-lab);
    --z-base: 0;
    --z-grain: 1;
    --z-sticky: 100;
}

*, *::before, *::after {
    box-sizing: border-box;
}

html {
    touch-action: manipulation;
    background: var(--bg-app);
}

/* Global */
.stApp {
    background:
        radial-gradient(circle at 18% 8%, rgba(214,161,95,0.10), transparent 310px),
        radial-gradient(circle at 84% 4%, rgba(140,161,142,0.10), transparent 280px),
        linear-gradient(135deg, rgba(244,239,229,0.035), transparent 34%),
        var(--bg-app);
    font-family: var(--font-stack);
    letter-spacing: 0;
}
.stApp::before {
    content: "";
    position: fixed;
    inset: 0;
    z-index: var(--z-grain);
    pointer-events: none;
    opacity: 0.055;
    background-image:
        repeating-linear-gradient(0deg, rgba(255,255,255,0.035) 0 1px, transparent 1px 4px),
        repeating-linear-gradient(90deg, rgba(214,161,95,0.025) 0 1px, transparent 1px 6px);
    mix-blend-mode: overlay;
}
h1, h2, h3, h4, h5, h6 {
    color: var(--text-primary) !important;
    font-family: var(--font-display);
    font-weight: 650 !important;
    letter-spacing: 0;
    text-wrap: balance;
}
h1 {
    font-size: clamp(36px, 5vw, 58px) !important;
    line-height: 0.98 !important;
    margin-bottom: 18px !important;
    max-width: 880px;
}
p, li, label, div {
    color: var(--text-primary);
}
body, button, input, textarea, select {
    font-family: var(--font-stack) !important;
}
div[data-testid="stMainBlockContainer"] {
    max-width: 1220px;
    padding-top: 48px;
    position: relative;
}
.stMetric label {
    color: var(--text-secondary) !important;
    font-size: 11px !important;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0;
    white-space: normal !important;
    overflow: visible !important;
    text-overflow: clip !important;
    line-height: 1.25 !important;
}
.stMetric [data-testid="stMetricValue"] {
    font-family: var(--font-mono) !important;
    font-size: clamp(18px, 2.1vw, 26px) !important;
    font-weight: 650;
    color: var(--accent) !important;
    font-variant-numeric: tabular-nums;
    white-space: normal !important;
    overflow-wrap: anywhere !important;
}
.stMetric [data-testid="stMetricLabel"],
.stMetric [data-testid="stMetricLabel"] p {
    max-width: 100%;
    white-space: normal !important;
    overflow: visible !important;
    text-overflow: clip !important;
}
div[data-testid="stMetric"] {
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-md);
    background:
        linear-gradient(180deg, rgba(244,239,229,0.045), transparent),
        rgba(21,24,23,0.76);
    padding: 13px 15px;
    box-shadow: var(--shadow-sm);
}
.stMarkdown, .stCaption, div[data-testid="stMarkdownContainer"] {
    color: var(--text-secondary) !important;
}
div[data-testid="stMarkdownContainer"] strong {
    color: var(--text-primary) !important;
}
div[data-testid="stDataFrame"], div[data-testid="stTable"] {
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-lg);
    max-width: 100%;
    overflow: auto;
    background: rgba(18,21,20,0.86);
    box-shadow: var(--shadow-sm);
}
div[data-testid="stDataFrame"] > div,
div[data-testid="stTable"] > div {
    max-width: 100%;
}
div[data-testid="stMarkdownContainer"] {
    max-width: 100%;
    overflow-wrap: anywhere;
}
div[data-testid="stMarkdownContainer"] table {
    display: block;
    max-width: 100%;
    overflow-x: auto;
    border-collapse: collapse;
}
div[data-testid="stMarkdownContainer"] th,
div[data-testid="stMarkdownContainer"] td {
    white-space: normal;
    overflow-wrap: anywhere;
}
div[data-testid="stMarkdownContainer"] pre,
div[data-testid="stMarkdownContainer"] code,
div[data-testid="stException"] pre,
div[data-testid="stException"] code {
    max-width: 100%;
    white-space: pre-wrap !important;
    overflow-wrap: anywhere;
}
div[data-testid="stCode"] {
    max-width: 100%;
    overflow-x: auto;
}
div[data-testid="stCode"] pre,
div[data-testid="stCode"] code,
div[data-testid="stCode"] code span {
    max-width: 100%;
    white-space: pre-wrap !important;
    overflow-wrap: anywhere;
    word-break: break-word;
}
div[data-testid="stGraphVizChart"],
div[data-testid="stGraphVizChart"] svg {
    max-width: 100%;
    overflow-x: auto;
}
div[data-testid="stExpander"] {
    border: 1px solid var(--border-subtle) !important;
    border-radius: var(--radius-md) !important;
    background: rgba(18,21,20,0.72) !important;
}
div[data-testid="stSelectbox"] label p {
    color: var(--accent) !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.5px !important;
}
div[data-testid="stSelectbox"] div[data-baseweb="select"] {
    border: 1px solid var(--border-subtle) !important;
    border-radius: var(--radius-md) !important;
    background-color: rgba(18, 21, 20, 0.72) !important;
}
div[data-testid="stSelectbox"] div[data-baseweb="select"]:hover {
    border-color: var(--accent) !important;
}
div[data-testid="stFileUploaderDropzone"] {
    border: 1px dashed rgba(214,161,95,0.38) !important;
    border-radius: var(--radius-lg) !important;
    background: rgba(18,21,20,0.78) !important;
}
div[data-testid="stFileUploaderDropzone"] svg {
    color: var(--accent) !important;
}
button, input, textarea, select, [role="button"], [role="radio"], [role="checkbox"] {
    touch-action: manipulation;
}
button {
    transition: transform var(--transition-fast), box-shadow var(--transition-fast), border-color var(--transition-fast), background var(--transition-fast) !important;
}
button:hover:not(:disabled) {
    transform: translateY(-1px);
}
button:active:not(:disabled) {
    transform: translateY(1px) scale(0.99);
}
input, textarea, select {
    color: var(--text-primary) !important;
    background: rgba(10,13,12,0.72) !important;
    border-color: var(--border-subtle) !important;
    font-size: 16px !important;
}
button:focus-visible,
[role="button"]:focus-visible,
input:focus-visible,
textarea:focus-visible,
select:focus-visible,
[tabindex]:focus-visible {
    outline: 3px solid var(--accent) !important;
    outline-offset: 3px !important;
    box-shadow: 0 0 0 5px rgba(214,161,95,0.18) !important;
}
button:disabled {
    cursor: not-allowed !important;
    opacity: 0.54 !important;
}

/* Academic dashboard panels */
.academic-hero {
    border: 1px solid var(--border-subtle);
    border-top-color: var(--border-strong);
    border-radius: var(--radius-xl);
    padding: clamp(18px, 3vw, 30px);
    margin: 0 0 18px;
    background:
        linear-gradient(120deg, rgba(214,161,95,0.14), transparent 42%),
        linear-gradient(180deg, rgba(244,239,229,0.052), rgba(244,239,229,0.014)),
        rgba(18,21,20,0.94);
    box-shadow: var(--shadow-lg);
    position: relative;
    overflow: hidden;
}
.academic-hero::after {
    content: "";
    position: absolute;
    right: -60px;
    top: 18px;
    width: 230px;
    height: 230px;
    border: 1px solid rgba(214,161,95,0.12);
    border-radius: 50%;
    box-shadow: inset 0 0 0 18px rgba(214,161,95,0.026);
    pointer-events: none;
}
.academic-kicker {
    color: var(--accent) !important;
    font-family: var(--font-mono);
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 0;
    text-transform: uppercase;
    margin-bottom: 10px;
}
.academic-hero h2 {
    margin: 0 0 9px !important;
    font-size: clamp(26px, 3.4vw, 40px) !important;
    line-height: 1.04 !important;
}
.academic-hero p {
    color: var(--text-secondary) !important;
    margin: 0 !important;
    max-width: 840px;
    line-height: 1.68;
}
.academic-card {
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-lg);
    background:
        linear-gradient(180deg, rgba(244,239,229,0.05), rgba(244,239,229,0.012)),
        rgba(21,24,23,0.88);
    padding: 16px 18px;
    min-height: 116px;
    box-shadow: var(--shadow-sm);
}
.academic-card-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(min(235px, 100%), 1fr));
    gap: 14px;
    margin: 10px 0 18px;
    max-width: 100%;
    min-width: 0;
    overflow: hidden;
}
.academic-record-card {
    border: 1px solid var(--border-subtle);
    border-left: 3px solid rgba(214,161,95,0.46);
    border-radius: var(--radius-md);
    background: rgba(18,21,20,0.90);
    padding: 14px 15px;
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
    font-size: 15.5px !important;
    line-height: 1.3 !important;
    letter-spacing: 0;
}
.academic-record-row {
    border-top: 1px solid rgba(214,196,166,0.12);
    padding-top: 8px;
    margin-top: 8px;
    font-size: 13.5px;
    line-height: 1.52;
}
.academic-record-label {
    color: var(--accent) !important;
    display: block;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 0;
    text-transform: uppercase;
    margin-bottom: 3px;
}
.academic-card-title {
    color: var(--accent) !important;
    font-family: var(--font-mono);
    font-weight: 800;
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0;
    margin-bottom: 10px;
}
.academic-card-body {
    color: var(--text-primary) !important;
    font-size: 14.5px;
    line-height: 1.62;
}
.exam-path {
    display: grid;
    grid-template-columns: 1.25fr repeat(4, minmax(0, 1fr));
    gap: 10px;
    margin: 4px 0 22px;
}
.exam-path-step {
    border: 1px solid rgba(214,196,166,0.18);
    border-radius: var(--radius-md);
    background: rgba(18,21,20,0.68);
    padding: 12px 12px;
    min-width: 0;
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.035);
}
.exam-path-step.active {
    border-color: rgba(214,161,95,0.78);
    background:
        linear-gradient(180deg, rgba(214,161,95,0.16), rgba(214,161,95,0.055)),
        rgba(30,25,18,0.82);
    box-shadow: inset 0 1px 0 rgba(255,255,255,0.06), 0 12px 32px rgba(4,7,6,0.30);
}
.exam-path-index {
    color: var(--accent) !important;
    font-family: var(--font-mono);
    font-size: 11px;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0;
}
.exam-path-title {
    color: var(--text-primary) !important;
    font-size: 13.5px;
    font-weight: 800;
    line-height: 1.25;
    margin-top: 3px;
}
.exam-path-note {
    color: var(--text-muted) !important;
    font-size: 12.5px;
    line-height: 1.42;
    margin-top: 5px;
}
.role-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    border-radius: 5px;
    padding: 5px 9px;
    font-family: var(--font-mono);
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 0;
    text-transform: uppercase;
    border: 1px solid rgba(244,239,229,0.18);
}
.role-real-solver { background: rgba(122,166,106,0.18); color: #d8f0c5 !important; border-left: 3px solid var(--success); }
.role-contrast-demo { background: rgba(214,161,95,0.16); color: #f6d6a7 !important; border-left: 3px solid var(--accent); }
.role-illustrative-extension { background: rgba(140,161,142,0.16); color: #d8e5d7 !important; border-left: 3px solid var(--accent-tertiary); }
.role-stochastic-game-demo { background: rgba(214,106,95,0.16); color: #f2c1ba !important; border-left: 3px solid var(--error); }
.academic-warning {
    border: 1px solid rgba(214,161,95,0.24);
    border-left: 4px solid var(--accent-secondary);
    border-radius: var(--radius-md);
    background: linear-gradient(90deg, rgba(214,161,95,0.13), rgba(214,161,95,0.032));
    padding: 13px 15px;
    color: var(--text-primary) !important;
    margin: 14px 0 18px;
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
        padding-left: 12px !important;
        padding-right: 12px !important;
        padding-top: 56px !important;
    }
    input, textarea, select, button {
        font-size: 16px !important;
    }
    h1 {
        font-size: 30px !important;
        line-height: 1.05 !important;
        overflow-wrap: anywhere;
    }
    .academic-hero {
        padding: 16px 14px;
        border-radius: 14px;
    }
    .academic-hero h2 {
        font-size: 23px !important;
        line-height: 1.12 !important;
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
        width: 0 !important;
        min-width: 0 !important;
        max-width: 0 !important;
        overflow: hidden !important;
        border-right: 0 !important;
        box-shadow: none !important;
        pointer-events: none !important;
    }
    section[data-testid="stSidebar"][aria-expanded="true"] {
        pointer-events: auto !important;
    }
    button[data-testid="stExpandSidebarButton"] {
        position: fixed !important;
        top: 14px !important;
        left: 14px !important;
        z-index: calc(var(--z-sticky) + 20) !important;
        background: rgba(18,21,20,0.92) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: var(--radius-sm) !important;
        box-shadow: var(--shadow-sm) !important;
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
        font-size: 22px !important;
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

/* Puzzle Board */
.puzzle-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 9px;
    max-width: 356px;
    margin: 0 auto 18px;
    background:
        linear-gradient(145deg, #1f211e, #080b0a),
        var(--surface-ink);
    padding: 14px;
    border-radius: 18px;
    border: 1px solid rgba(214,196,166,0.22);
    box-shadow:
        inset 0 0 0 6px rgba(4,7,6,0.70),
        inset 0 1px 0 rgba(255,255,255,0.06),
        0 24px 54px rgba(4,7,6,0.54),
        0 4px 0 #080b0a;
    position: relative;
    animation: boardFadeIn 0.36s var(--ease-lab);
}
.puzzle-grid::before {
    content: "";
    position: absolute;
    inset: 8px;
    border-radius: 12px;
    border: 1px dashed rgba(214,196,166,0.10);
    pointer-events: none;
}

/* Game Tile (tactile solver keys) */
.puzzle-tile {
    width: 72px;
    height: 72px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: var(--font-mono);
    font-size: 26px;
    font-weight: 700;
    border-radius: 11px;
    user-select: none;
    position: relative;
    overflow: hidden;
    cursor: pointer;
    transition: transform var(--transition-fast), box-shadow var(--transition-fast), filter var(--transition-fast);
    text-shadow: 0 1px 0 rgba(255,255,255,0.25);
}
.puzzle-tile::before {
    content: "";
    position: absolute;
    inset: 1px;
    border-radius: 9px;
    border: 1px solid rgba(255,255,255,0.10);
    pointer-events: none;
}

.puzzle-tile.tile-band-0,
.puzzle-tile.tile-band-1,
.puzzle-tile.tile-band-2,
.puzzle-tile.tile-band-3 {
    background: linear-gradient(145deg, #b8b5a6, #898b7f) !important;
    color: #111411 !important;
    box-shadow:
        0 5px 12px rgba(4,7,6,0.48),
        inset 0 1px 0 rgba(255,255,255,0.22);
    border-top: 1px solid rgba(255,255,255,0.18) !important;
    border-left: 1px solid rgba(255,255,255,0.09) !important;
    border-bottom: 4px solid #474d43 !important;
    border-right: 4px solid #474d43 !important;
    text-shadow: 0 1px 0 rgba(255,255,255,0.12) !important;
}
.puzzle-tile.tile-band-1 { background: linear-gradient(145deg, #adab9d, #7f8579) !important; }
.puzzle-tile.tile-band-2 { background: linear-gradient(145deg, #a2a394, #747e72) !important; }
.puzzle-tile.tile-band-3 { background: linear-gradient(145deg, #949d90, #657166) !important; }

.puzzle-tile:hover {
    transform: translateY(-3px) rotate(-0.25deg);
    filter: saturate(1.06);
    box-shadow:
        0 12px 22px rgba(4,7,6,0.58),
        inset 0 1px 0 rgba(255,255,255,0.38) !important;
}
.puzzle-tile:active {
    transform: translateY(1px) scale(0.975);
    box-shadow: 0 3px 8px rgba(4,7,6,0.42) !important;
}

/* Correct position tiles use an indicator only; tile color stays tied to tile identity. */
.puzzle-tile.correct {
    box-shadow:
        0 5px 12px rgba(4,7,6,0.48),
        inset 0 0 0 2px rgba(244,239,229,0.24),
        0 0 0 2px rgba(122,166,106,0.48),
        inset 0 1px 0 rgba(255,255,255,0.24) !important;
}
.puzzle-tile.correct::after {
    content: "";
    position: absolute;
    right: 8px;
    top: 8px;
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: #263b23;
    box-shadow: 0 0 0 2px rgba(244,239,229,0.26);
}

/* Blank tile with recessed design */
.puzzle-tile.blank {
    background:
        radial-gradient(circle at 50% 45%, rgba(214,161,95,0.08), transparent 55%),
        #080b0a !important;
    box-shadow: inset 0 8px 16px rgba(0,0,0,0.74), inset 0 0 0 1px rgba(214,196,166,0.08) !important;
    border: 1px dashed rgba(214,196,166,0.14);
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
.puzzle-tile.slide-anim,
.puzzle-cell.slide-anim {
    animation: tileSlideFrom 0.22s cubic-bezier(0.22, 1, 0.36, 1);
    will-change: transform;
}

/* Goal pulse */
@keyframes goalPulse {
    0%, 100% { box-shadow: 0 5px 12px rgba(4,7,6,0.48), inset 0 1px 0 rgba(255,255,255,0.2); }
    50%      { box-shadow: 0 8px 24px rgba(122,166,106,0.34), inset 0 0 0 2px rgba(244,239,229,0.28); }
}
.puzzle-tile.correct.goal-flash { animation: goalPulse 0.4s ease-in-out 3; }

/* Board entrance */
@keyframes boardFadeIn {
    from { opacity: 0; transform: scale(0.98); }
    to   { opacity: 1; transform: scale(1); }
}
.puzzle-grid { animation: boardFadeIn 0.36s var(--ease-lab); }
.puzzle-grid:has(.puzzle-cell.slide-anim) { animation: none; }

/* Legacy puzzle-cell (for static displays like trace tables) */
.puzzle-cell {
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: var(--font-mono);
    font-weight: 800;
    border-radius: 9px;
    user-select: none;
    position: relative;
    overflow: hidden;
    text-shadow: 0 1px 1px rgba(255,255,255,0.18);
}
.puzzle-cell.filled {
    background: linear-gradient(145deg, #b8b5a6, #898b7f);
    color: #111411;
    box-shadow: 
        0 4px 8px rgba(0,0,0,0.4),
        inset 0 1px 0 rgba(255,255,255,0.2);
    border-top: 1px solid rgba(255,255,255,0.3);
    border-left: 1px solid rgba(255,255,255,0.15);
    border-bottom: 3px solid #474d43;
    border-right: 3px solid #474d43;
}
.puzzle-cell.blank {
    background: #080b0a !important;
    box-shadow: inset 0 4px 10px rgba(0,0,0,0.76) !important;
    border: 1px dashed rgba(214,196,166,0.10) !important;
    color: transparent !important;
}
.puzzle-cell.correct {
    background: linear-gradient(145deg, #b8b5a6, #898b7f) !important;
    color: #111411 !important;
    box-shadow: 
        0 4px 8px rgba(0,0,0,0.4),
        inset 0 1px 0 rgba(255,255,255,0.2) !important;
    border-top: 1px solid rgba(255,255,255,0.2) !important;
    border-left: 1px solid rgba(255,255,255,0.1) !important;
    border-bottom: 3px solid #3d5139 !important;
    border-right: 3px solid #3d5139 !important;
    outline: 2px solid rgba(122,166,106,0.44);
    text-shadow: 0 1px 1px rgba(255,255,255,0.18) !important;
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

/* Mini puzzle grid (trace tables) */
.puzzle-grid-mini {
    display: inline-grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 2px;
    background: #080b0a;
    padding: 5px;
    border-radius: 7px;
    font-size: 8px;
    margin: 2px 0;
    border: 1px solid rgba(214,196,166,0.14);
}
.puzzle-grid-mini .mc {
    width: 18px; height: 18px;
    display: flex; align-items: center; justify-content: center;
    border-radius: 3px;
    font-weight: 700;
    font-size: 8px;
}
.puzzle-grid-mini .mc.f {
    background: linear-gradient(135deg, #b8b5a6, #898b7f);
    color: #111411;
    border-bottom: 1px solid #474d43;
}
.puzzle-grid-mini .mc.b {
    background: transparent;
}
.puzzle-grid-mini .mc.c {
    background: linear-gradient(135deg, #b8b5a6, #898b7f);
    color: #111411;
    border-bottom: 1px solid #3d5139;
    outline: 1px solid rgba(122,166,106,0.46);
}

/* Parsed Start/Goal previews beside the matrix editors. */
.start-goal-matrix-preview {
    display: grid;
    gap: 7px;
    align-content: start;
    padding-top: 2px;
}
.state-matrix-preview-label {
    color: var(--text-secondary);
    font-size: 12px;
    font-weight: 700;
}
.state-matrix-preview-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(22px, 1fr));
    gap: 3px;
    width: min(100%, 150px);
    aspect-ratio: 1;
}
.state-matrix-preview-cell {
    display: grid;
    place-items: center;
    min-width: 0;
    border: 1px solid rgba(214, 196, 166, 0.22);
    border-radius: 4px;
    background: #202621;
    color: var(--text-primary);
    font-size: 12px;
    font-weight: 750;
}
.state-matrix-preview-cell.blank {
    background: #080b0a;
    border-style: dashed;
}

/* Result cards */
.result-success {
    border: 1px solid rgba(122,166,106,0.22);
    border-left: 4px solid var(--success);
    background: linear-gradient(90deg, rgba(122,166,106,0.14), rgba(122,166,106,0.028));
    padding: 13px 16px;
    border-radius: var(--radius-md);
    margin: 10px 0;
    box-shadow: var(--shadow-sm);
}
.result-failure {
    border: 1px solid rgba(214,106,95,0.24);
    border-left: 4px solid var(--error);
    background: linear-gradient(90deg, rgba(214,106,95,0.14), rgba(214,106,95,0.028));
    padding: 13px 16px;
    border-radius: var(--radius-md);
    margin: 10px 0;
    box-shadow: var(--shadow-sm);
}

/* Group badges */
.group-badge {
    display: inline-block;
    padding: 5px 11px;
    border-radius: 5px;
    font-family: var(--font-mono);
    font-size: 11px;
    font-weight: 800;
    margin-right: 6px;
    text-transform: uppercase;
    letter-spacing: 0;
    border: 1px solid rgba(244,239,229,0.16);
}
.group-uninformed { background: rgba(214,161,95,0.14); color: #f6d6a7; border-left: 3px solid #d6a15f; }
.group-informed  { background: rgba(122,166,106,0.14); color: #d8f0c5; border-left: 3px solid #7aa66a; }
.group-local      { background: rgba(198,144,83,0.14); color: #f0c989; border-left: 3px solid #c69053; }
.group-complex    { background: rgba(140,161,142,0.14); color: #d8e5d7; border-left: 3px solid #8ca18e; }
.group-csp        { background: rgba(111,142,96,0.16); color: #d8f0c5; border-left: 3px solid #6f8e60; }
.group-adversarial { background: rgba(214,106,95,0.14); color: #f2c1ba; border-left: 3px solid #d66a5f; }

/* Scrollbar */
.scroll-container {
    max-height: 400px;
    overflow-y: auto;
    padding-right: 8px;
}
.scroll-container::-webkit-scrollbar { width: 6px; }
.scroll-container::-webkit-scrollbar-track { background: var(--bg-surface); border-radius: 3px; }
.scroll-container::-webkit-scrollbar-thumb { background: var(--accent); border-radius: 3px; }
.scroll-container::-webkit-scrollbar-thumb:hover { background: var(--accent-hover); }

/* Sidebar */
section[data-testid="stSidebar"] {
    background:
        radial-gradient(circle at 20% 0%, rgba(214,161,95,0.10), transparent 220px),
        linear-gradient(180deg, #151817 0%, #090c0b 100%) !important;
    border-right: 1px solid rgba(214,196,166,0.16);
    box-shadow: 12px 0 36px rgba(4,7,6,0.25);
}
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    letter-spacing: 0;
}
section[data-testid="stSidebar"] h1 {
    font-size: 26px !important;
    line-height: 1.08 !important;
    margin-bottom: 8px !important;
    max-width: 100%;
}
section[data-testid="stSidebar"] h3 {
    font-size: 18px !important;
    line-height: 1.24 !important;
}
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] p {
    color: var(--text-secondary) !important;
    font-size: 13.5px !important;
    line-height: 1.38 !important;
}
section[data-testid="stSidebar"] div[data-testid="stExpander"] {
    margin: 0 0 10px !important;
    border-color: rgba(214,196,166,0.18) !important;
    background:
        linear-gradient(180deg, rgba(244,239,229,0.035), transparent),
        rgba(10,13,12,0.34) !important;
}
section[data-testid="stSidebar"] div[data-testid="stExpander"] details summary {
    min-height: 44px;
    align-items: center;
}
section[data-testid="stSidebar"] div[data-testid="stExpander"] details summary p {
    color: var(--text-primary) !important;
    font-weight: 800 !important;
}
section[data-testid="stSidebar"] [role="radiogroup"] label {
    border-radius: var(--radius-sm);
    padding: 5px 7px;
    transition: background var(--transition-fast), color var(--transition-fast), transform var(--transition-fast);
}
section[data-testid="stSidebar"] [role="radiogroup"] label:hover {
    background: rgba(214,161,95,0.10);
    transform: translateX(1px);
}
section[data-testid="stSidebar"] hr {
    border-color: rgba(214,196,166,0.12) !important;
}
section[data-testid="stSidebar"] .puzzle-grid {
    width: 100%;
    max-width: 172px;
    gap: 4px;
    padding: 8px;
    border-radius: 12px;
    margin: 0 0 10px;
}
section[data-testid="stSidebar"] .puzzle-grid::before {
    inset: 5px;
    border-radius: 8px;
}
section[data-testid="stSidebar"] .puzzle-cell {
    width: 100% !important;
    height: auto !important;
    aspect-ratio: 1 / 1;
    min-width: 0;
    font-size: 13px !important;
}

/* Section dividers */
.section-divider {
    border: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(214,161,95,0.64), transparent);
    margin: 20px 0;
}

/* Detail grid text (monospace for trace) */
.detail-grid-text {
    font-family: var(--font-mono);
    font-size: 11.5px;
    line-height: 1.48;
    color: var(--text-primary);
    background: rgba(8,11,10,0.78);
    border: 1px solid rgba(214,196,166,0.12);
    padding: 9px 11px;
    border-radius: var(--radius-md);
    margin: 3px 0;
}

/* Interactive Play Board alignment and styles */
div.interactive-board-container-number, div.interactive-board-container-image {
    display: none;
}

div[class*="number_board"] {
    margin: 0 0 6px !important;
}

div[class*="number_board"] div[data-testid="stHorizontalBlock"] {
    display: grid !important;
    grid-template-columns: repeat(4, minmax(0, 1fr)) !important;
    gap: clamp(6px, 1.1vw, 10px) !important;
    width: min(100%, 448px) !important;
    max-width: 448px !important;
    margin-left: auto !important;
    margin-right: auto !important;
}

div[class*="number_board"] div[data-testid="stHorizontalBlock"] > div[data-testid="stColumn"] {
    width: auto !important;
    min-width: 0 !important;
    max-width: none !important;
    flex: none !important;
    align-self: stretch !important;
}

div[class*="number_board"] div[data-testid="stColumn"] > div,
div[class*="number_board"] div[data-testid="stVerticalBlock"],
div[class*="number_board"] div[data-testid="stElementContainer"],
div[class*="number_board"] div[data-testid="stButton"],
div[class*="number_board"] div[data-testid="stMarkdown"],
div[class*="number_board"] div[data-testid="stMarkdownContainer"] {
    width: 100% !important;
    max-width: 100% !important;
}

div[class*="number_board"] button {
    width: 100% !important;
    aspect-ratio: 1 !important;
    height: auto !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    font-family: var(--font-mono) !important;
    font-size: 26px !important;
    font-weight: 700 !important;
    border-radius: 11px !important;
    margin: 0 !important;
    padding: 0 !important;
    color: #111411 !important;
    background: linear-gradient(145deg, #b8b5a6, #898b7f) !important;
    box-shadow: 
        0 5px 12px rgba(4,7,6,0.48),
        inset 0 1px 0 rgba(255,255,255,0.35) !important;
    border-top: 1px solid rgba(255,255,255,0.28) !important;
    border-left: 1px solid rgba(255,255,255,0.12) !important;
    border-bottom: 4px solid #474d43 !important;
    border-right: 4px solid #474d43 !important;
    transition: transform var(--transition-fast), box-shadow var(--transition-fast), filter var(--transition-fast) !important;
    text-shadow: 0 1px 0 rgba(255,255,255,0.25) !important;
    cursor: pointer !important;
    transform: translateZ(0) !important;
    will-change: transform, box-shadow;
    -webkit-tap-highlight-color: transparent;
    touch-action: pan-y pinch-zoom;
}

div[class*="number_board"] button p,
div[class*="number_board"] button div,
div[class*="number_board"] button span {
    color: inherit !important;
    font: inherit !important;
    line-height: 1 !important;
    margin: 0 !important;
}

div[class*="number_board"] button:hover {
    transform: translateY(-3px) rotate(-0.25deg) !important;
    box-shadow: 
        0 12px 22px rgba(4,7,6,0.58),
        inset 0 1px 0 rgba(255,255,255,0.38) !important;
    background: linear-gradient(145deg, #c0bdad, #939689) !important;
}

div[class*="number_board"] button:active {
    transform: translateY(1px) scale(0.985) !important;
    border-bottom-color: #3d3024 !important;
    border-right-color: #3d3024 !important;
    box-shadow: 0 3px 8px rgba(4,7,6,0.42) !important;
}

@media (hover: none) {
    div[class*="number_board"] button {
        transition: transform 90ms ease-out, box-shadow 90ms ease-out, filter 90ms ease-out !important;
    }
    div[class*="number_board"] button:hover {
        transform: translateZ(0) !important;
        background: linear-gradient(145deg, #b8b5a6, #898b7f) !important;
        box-shadow:
            0 5px 12px rgba(4,7,6,0.48),
            inset 0 1px 0 rgba(255,255,255,0.35) !important;
    }
    div[class*="number_board"] button:active {
        transform: translateY(1px) scale(0.99) !important;
    }
}

/* Ensure puzzle tiles in the number container are responsive squares */
div[class*="number_board"] .puzzle-tile {
    width: 100% !important;
    aspect-ratio: 1 !important;
    height: auto !important;
    margin: 0 !important;
}

/* Premium game board for the Play tab */
.play-game-panel {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 18px;
    margin: 14px 0 18px;
    padding: 16px 18px;
    border: 1px solid rgba(214,161,95,0.28);
    border-radius: 8px;
    background:
        linear-gradient(135deg, rgba(214,161,95,0.16), transparent 42%),
        rgba(12,15,14,0.94);
    box-shadow: 0 18px 42px rgba(2,5,4,0.34);
}
.play-game-panel h3 {
    margin: 3px 0 5px;
    color: var(--text-primary);
    font-size: 21px;
    letter-spacing: 0;
}
.play-game-panel p {
    margin: 0;
    max-width: 760px;
    color: var(--text-muted);
    line-height: 1.52;
    font-size: 13.5px;
}
.play-game-kicker,
.play-game-status {
    color: var(--accent-hover);
    font-family: var(--font-mono);
    font-size: 11px;
    font-weight: 850;
    letter-spacing: 0;
    text-transform: uppercase;
}
.play-game-status {
    flex: 0 0 auto;
    padding: 8px 10px;
    border: 1px solid rgba(214,161,95,0.3);
    border-radius: 6px;
    background: rgba(214,161,95,0.09);
}
.play-board-shell {
    padding: clamp(10px, 1.8vw, 16px);
    border: 1px solid rgba(214,196,166,0.2);
    border-radius: 8px;
    background:
        radial-gradient(circle at 50% 0%, rgba(214,161,95,0.15), transparent 42%),
        linear-gradient(145deg, rgba(21,25,23,0.98), rgba(5,8,7,0.98));
    box-shadow:
        0 24px 48px rgba(0,0,0,0.42),
        inset 0 1px 0 rgba(255,255,255,0.04);
}
.play-image-game-frame {
    width: min(100%, 620px);
    margin: 0 auto;
    padding: clamp(8px, 1.4vw, 14px);
    border: 1px solid rgba(214,196,166,0.20);
    border-radius: 8px;
    background:
        radial-gradient(circle at 50% 0%, rgba(214,161,95,0.12), transparent 44%),
        linear-gradient(145deg, rgba(21,25,23,0.98), rgba(5,8,7,0.98));
    box-shadow:
        0 24px 48px rgba(0,0,0,0.38),
        inset 0 1px 0 rgba(255,255,255,0.04);
    overflow: hidden;
}
.play-image-game-frame div[data-testid="stHorizontalBlock"] {
    gap: clamp(6px, 1vw, 10px) !important;
}
.play-image-game-frame button {
    min-height: 44px !important;
}
.play-board-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: clamp(7px, 1vw, 10px);
    width: min(100%, 680px);
    margin: 0 auto;
}
.play-image-cell {
    position: relative;
    display: block;
    aspect-ratio: 1 / 1;
    overflow: hidden;
    border: 3px solid rgba(184,121,62,0.85);
    border-radius: 8px;
    background-color: #080b0a;
    background-position: center;
    background-size: cover;
    box-shadow:
        0 10px 18px rgba(0,0,0,0.34),
        inset 0 1px 0 rgba(255,255,255,0.12);
    transform: translateZ(0);
    color: inherit;
    min-height: 44px;
    -webkit-tap-highlight-color: transparent;
    touch-action: manipulation;
    transition:
        transform 150ms ease,
        box-shadow 150ms ease,
        border-color 150ms ease,
        filter 150ms ease;
}
.play-image-cell img {
    display: block;
    width: 100%;
    height: 100%;
    object-fit: cover;
    pointer-events: none;
    user-select: none;
}
.play-image-cell.is-correct {
    border-color: rgba(122,166,106,0.9);
}
.play-image-cell.is-clickable {
    cursor: pointer;
    text-decoration: none;
}
.play-image-cell.is-clickable:hover {
    transform: translateY(-4px) scale(1.015);
    border-color: rgba(239,196,119,0.98);
    filter: saturate(1.08) brightness(1.05);
    box-shadow:
        0 18px 30px rgba(0,0,0,0.44),
        0 0 0 2px rgba(214,161,95,0.15);
}
.play-image-cell.is-clickable:active {
    transform: translateY(1px) scale(0.99);
}
.play-image-cell.is-clickable:focus-visible {
    outline: 3px solid var(--accent-hover);
    outline-offset: 3px;
}
.play-image-cell-blank {
    border: 1px dashed rgba(214,196,166,0.18);
    background:
        radial-gradient(circle at 50% 45%, rgba(214,161,95,0.09), transparent 56%),
        repeating-linear-gradient(135deg, rgba(255,255,255,0.02) 0 8px, transparent 8px 16px),
        #050706;
    box-shadow: inset 0 12px 22px rgba(0,0,0,0.68);
}
.play-image-cell-missing {
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--text-muted);
    font-family: var(--font-mono);
    font-weight: 800;
}
.play-tile-number {
    position: absolute;
    top: 7px;
    left: 7px;
    z-index: 3;
    min-width: 24px;
    padding: 2px 7px;
    border: 1px solid rgba(214,161,95,0.42);
    border-radius: 5px;
    background: rgba(3,6,5,0.84);
    color: var(--text-primary);
    font-family: var(--font-mono);
    font-size: 12px;
    font-weight: 850;
    line-height: 1.25;
    text-align: center;
}
.play-tile-shine {
    position: absolute;
    inset: 0;
    z-index: 1;
    pointer-events: none;
    background:
        linear-gradient(135deg, rgba(255,255,255,0.18), transparent 24%),
        linear-gradient(0deg, rgba(0,0,0,0.22), transparent 46%);
}
.play-move-chip {
    position: absolute;
    left: 8px;
    right: 8px;
    bottom: 8px;
    z-index: 4;
    padding: 7px 8px;
    border: 1px solid rgba(255,221,160,0.24);
    border-radius: 6px;
    background: rgba(28,19,12,0.82);
    color: #fff7e8;
    font-size: clamp(11px, 1.3vw, 13px);
    font-weight: 800;
    line-height: 1.2;
    text-align: center;
    backdrop-filter: blur(8px);
}
.play-preview-card {
    padding: 12px;
    border: 1px solid rgba(214,196,166,0.18);
    border-radius: 8px;
    background: rgba(12,15,14,0.86);
    box-shadow: 0 18px 34px rgba(0,0,0,0.32);
}
.play-victory-banner {
    margin: 18px 0;
    padding: 18px 20px;
    border: 1px solid rgba(122,166,106,0.42);
    border-radius: 8px;
    background:
        radial-gradient(circle at 12% 10%, rgba(122,166,106,0.26), transparent 34%),
        linear-gradient(135deg, rgba(38,62,45,0.94), rgba(14,18,16,0.96));
    box-shadow:
        0 18px 40px rgba(0,0,0,0.36),
        inset 0 1px 0 rgba(255,255,255,0.08);
}
.play-victory-kicker {
    color: #b8d8a7;
    font-family: var(--font-mono);
    font-size: 11px;
    font-weight: 900;
    letter-spacing: 0;
    text-transform: uppercase;
}
.play-victory-title {
    margin-top: 6px;
    color: var(--text-primary);
    font-size: clamp(20px, 2.2vw, 28px);
    font-weight: 850;
    line-height: 1.2;
}
.play-victory-subtitle {
    margin-top: 8px;
    color: var(--text-secondary);
    font-size: 13.5px;
    line-height: 1.5;
}

@media (max-width: 760px) {
    .play-game-panel {
        align-items: flex-start;
        flex-direction: column;
    }
    .play-game-status {
        width: 100%;
        text-align: center;
    }
    .play-board-shell {
        padding: 8px;
    }
    .play-image-game-frame {
        width: min(100%, 430px);
        padding: 8px;
    }
    .play-board-grid {
        gap: 6px;
    }
    .play-move-chip {
        padding: 5px 4px;
        font-size: 10px;
    }
}

@media (max-width: 420px) {
    .play-image-game-frame {
        padding: 6px;
    }
    .play-image-game-frame div[data-testid="stHorizontalBlock"] {
        gap: 5px !important;
    }
}

/* Premium AI Solver Card */
.ai-solver-card {
    background:
        linear-gradient(135deg, rgba(214,161,95,0.12), transparent 42%),
        rgba(18,21,20,0.94) !important;
    border: 1px solid rgba(214,161,95,0.26) !important;
    border-radius: var(--radius-lg) !important;
    padding: 18px 20px !important;
    margin: 18px 0 !important;
    box-shadow: var(--shadow-md) !important;
}
.ai-solver-header {
    display: flex !important;
    align-items: center !important;
    justify-content: space-between !important;
    border-bottom: 1px solid rgba(214,196,166,0.14) !important;
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
    font-weight: 750 !important;
    color: var(--text-primary) !important;
    letter-spacing: 0;
}
.ai-solver-badge {
    background: rgba(214,161,95,0.16) !important;
    border: 1px solid rgba(214,161,95,0.55) !important;
    color: var(--accent-hover) !important;
    font-family: var(--font-mono) !important;
    font-size: 10px !important;
    font-weight: 800 !important;
    padding: 2px 8px !important;
    border-radius: 5px !important;
    letter-spacing: 0;
    text-transform: uppercase !important;
}
.ai-solver-desc {
    font-size: 13.5px !important;
    color: var(--text-muted) !important;
    line-height: 1.58 !important;
    margin: 0 !important;
}
.ai-contract-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 8px;
    margin: 0 0 16px;
}
.ai-contract-row {
    min-width: 0;
    padding: 10px 11px;
    border: 1px solid rgba(214,196,166,0.18);
    border-radius: 7px;
    background: rgba(18,21,20,0.72);
}
.ai-contract-row span {
    display: block;
    color: var(--text-muted);
    font-family: var(--font-mono);
    font-size: 10.5px;
    font-weight: 800;
    line-height: 1.25;
    text-transform: uppercase;
}
.ai-contract-row strong {
    display: block;
    margin-top: 4px;
    color: var(--text-primary);
    font-size: 13.5px;
    font-weight: 800;
    line-height: 1.3;
    overflow-wrap: anywhere;
}
.solution-step-table-wrap {
    max-height: 380px;
    overflow-y: auto;
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-md);
    background: rgba(12,15,14,0.88);
    margin: 10px 0 16px;
    padding: 10px;
}
.solution-step-list {
    display: grid;
    gap: 10px;
}
.solution-step-card {
    display: grid;
    grid-template-columns: minmax(86px, 0.38fr) minmax(130px, 1fr);
    gap: 12px;
    align-items: center;
    padding: 10px;
    border: 1px solid rgba(214,196,166,0.13);
    border-radius: var(--radius-sm);
    background: rgba(18,21,20,0.82);
}
.solution-step-card.is-current {
    border-color: rgba(122,166,106,0.62);
    box-shadow: inset 3px 0 0 rgba(122,166,106,0.86);
    background: linear-gradient(90deg, rgba(122,166,106,0.12), rgba(18,21,20,0.88));
}
.solution-step-meta {
    display: grid;
    gap: 7px;
    align-content: center;
}
.solution-step-index-pill {
    width: fit-content;
    min-width: 34px;
    padding: 4px 9px;
    border-radius: 999px;
    background: rgba(214,161,95,0.14);
    color: var(--accent);
    font-family: var(--font-mono);
    font-size: 13px;
    font-weight: 850;
    text-align: center;
}
.solution-step-action-name {
    color: var(--text-primary);
    font-size: 16px;
    line-height: 1.25;
}
.solution-step-board {
    min-width: 0;
    display: flex;
    justify-content: center;
}
.solution-step-board .puzzle-grid-mini {
    transform-origin: center;
}
.solution-step-mode-image .solution-step-card {
    grid-template-columns: minmax(92px, 0.34fr) minmax(150px, 1fr);
}
.solution-step-mode-image .puzzle-grid-mini-image .mc {
    width: 34px;
    height: 34px;
}
.search-tree-readable {
    margin-top: 12px;
    padding: 14px;
    border: 1px solid rgba(214,196,166,0.14);
    border-radius: var(--radius-md);
    background: rgba(12,15,14,0.78);
}
.search-tree-legend {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin-bottom: 12px;
    color: var(--text-secondary);
    font-size: 13px;
    line-height: 1.3;
}
.search-tree-legend span {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    min-width: 0;
}
.search-tree-legend i {
    width: 12px;
    height: 12px;
    border-radius: 999px;
    border: 1px solid rgba(255,255,255,0.32);
    flex: 0 0 auto;
}
.legend-solution {
    background: #7aa66a;
}
.legend-explored {
    background: #8ea0ff;
}
.legend-frontier {
    background: #d6a15f;
}
.search-tree-readable-summary {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 8px;
    margin-bottom: 12px;
}
.search-tree-readable-summary span {
    padding: 8px 10px;
    border-radius: var(--radius-sm);
    background: rgba(18,21,20,0.92);
    color: var(--text-secondary);
    font-size: 12px;
    line-height: 1.25;
}
.search-tree-readable-summary strong {
    color: var(--text-primary);
    font-family: var(--font-mono);
    font-size: 15px;
}
.search-tree-readable-context {
    display: grid;
    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 10px;
    margin-bottom: 12px;
}
.search-tree-snapshot-panel {
    min-width: 0;
    border: 1px solid rgba(214,196,166,0.12);
    border-radius: var(--radius-sm);
    padding: 10px;
    background: rgba(18,21,20,0.7);
}
.search-tree-snapshot-panel strong,
.search-tree-snapshot-panel span {
    display: block;
}
.search-tree-snapshot-panel strong {
    color: var(--text-primary);
    font-size: 13px;
    margin-bottom: 2px;
}
.search-tree-snapshot-panel span {
    color: var(--text-muted);
    font-size: 12px;
    margin-bottom: 8px;
}
.search-tree-snapshot-boards {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}
.search-tree-snapshot-board {
    max-width: 100%;
}
.search-tree-snapshot-empty {
    color: var(--text-muted);
    font-size: 12px;
}
.search-tree-readable-spine {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(156px, 1fr));
    gap: 12px;
}
.search-tree-readable-card {
    min-width: 0;
    padding: 10px;
    border: 1px solid rgba(142,160,255,0.26);
    border-radius: var(--radius-sm);
    background: linear-gradient(180deg, rgba(142,160,255,0.08), rgba(18,21,20,0.86));
}
.search-tree-readable-card.is-solution {
    border-color: rgba(122,166,106,0.55);
    background: linear-gradient(180deg, rgba(122,166,106,0.16), rgba(18,21,20,0.88));
    box-shadow: inset 0 0 0 1px rgba(122,166,106,0.18);
}
.search-tree-readable-meta {
    display: grid;
    grid-template-columns: 1fr;
    gap: 8px;
    margin-bottom: 7px;
    color: var(--text-muted);
    font-size: 11px;
    line-height: 1.2;
}
.search-tree-readable-meta strong {
    color: var(--accent);
    font-size: 12px;
    overflow-wrap: anywhere;
}
.search-tree-readable-board {
    display: flex;
    justify-content: center;
}
.search-tree-readable .puzzle-grid-mini {
    transform: scale(1.12);
    transform-origin: center;
    margin: 7px 0;
}
.search-tree-readable.is-image .puzzle-grid-mini-image .mc {
    width: 36px;
    height: 36px;
}
.search-tree-readable-card.is-more {
    min-height: 118px;
    display: grid;
    place-items: center;
    text-align: center;
    color: var(--text-secondary);
}
.search-tree-readable-card.is-more strong {
    color: var(--accent);
    font-size: 24px;
}
.play-compact-strip {
    border: 1px solid rgba(214,161,95,0.24);
    border-radius: var(--radius-md);
    padding: 14px 16px;
    margin: 0 0 16px;
    background:
        linear-gradient(90deg, rgba(214,161,95,0.13), rgba(140,161,142,0.05)),
        rgba(18,21,20,0.86);
    box-shadow: var(--shadow-sm);
}
div[data-testid="stElementContainer"]:has(h1):has(~ div[data-testid="stElementContainer"] .play-compact-strip),
div[data-testid="stElementContainer"]:has(h1):has(~ div[data-testid="stElementContainer"] .play-compact-strip) h1 {
    position: absolute !important;
    width: 1px !important;
    height: 1px !important;
    padding: 0 !important;
    margin: -1px !important;
    overflow: hidden !important;
    clip: rect(0, 0, 0, 0) !important;
    white-space: nowrap !important;
    border: 0 !important;
}
.play-compact-strip h2 {
    margin: 2px 0 6px !important;
    font-size: 26px !important;
    line-height: 1.18 !important;
}
.play-compact-strip p {
    margin: 0 !important;
    color: var(--text-secondary) !important;
    font-size: 13.5px;
    line-height: 1.55;
}
.play-compact-kicker,
.play-panel-kicker {
    color: var(--accent-hover) !important;
    font-family: var(--font-mono);
    font-size: 11px;
    font-weight: 850;
    letter-spacing: 0;
    text-transform: uppercase;
}
.play-panel-heading {
    margin: 2px 0 12px;
}
.play-panel-heading h2 {
    margin: 2px 0 5px !important;
    font-size: clamp(24px, 2.6vw, 34px) !important;
    line-height: 1.08 !important;
}
.play-panel-heading p {
    margin: 0 !important;
    color: var(--text-secondary) !important;
    font-size: 13.5px;
    line-height: 1.5;
}
.play-status-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 10px;
    margin: 14px 0 10px;
}
.play-status-card {
    min-height: 78px;
    border: 1px solid rgba(214,196,166,0.18);
    border-radius: var(--radius-sm);
    padding: 11px 12px;
    background:
        linear-gradient(180deg, rgba(244,239,229,0.055), rgba(244,239,229,0.012)),
        rgba(18,21,20,0.88);
}
.play-status-label {
    color: var(--text-secondary);
    font-family: var(--font-mono);
    font-size: 11px;
    font-weight: 800;
    line-height: 1.25;
    text-transform: uppercase;
}
.play-status-value {
    color: var(--text-primary);
    font-family: var(--font-mono);
    font-size: 28px;
    font-weight: 850;
    line-height: 1.15;
    margin-top: 9px;
}
.action-state {
    border: 1px solid rgba(214,161,95,0.30);
    border-left: 4px solid var(--accent);
    border-radius: var(--radius-md);
    padding: 16px 18px;
    margin: 14px 0 18px;
    background:
        linear-gradient(120deg, rgba(214,161,95,0.12), rgba(140,161,142,0.06)),
        rgba(18,21,20,0.88);
    box-shadow: var(--shadow-sm);
}
.action-state-kicker {
    color: var(--accent-hover) !important;
    font-family: var(--font-mono);
    font-size: 11px;
    font-weight: 850;
    letter-spacing: 0;
    text-transform: uppercase;
}
.action-state h3 {
    margin: 4px 0 7px !important;
    font-size: 19px !important;
    line-height: 1.25 !important;
}
.action-state p,
.action-state li {
    color: var(--text-secondary) !important;
    font-size: 13.5px;
    line-height: 1.55;
}
.action-state ul {
    margin: 10px 0 0;
    padding-left: 18px;
}
.advanced-mode-card {
    min-height: 224px;
    border: 1px solid rgba(214,196,166,0.18);
    border-radius: var(--radius-md);
    padding: 15px;
    margin: 8px 0 10px;
    background:
        linear-gradient(180deg, rgba(244,239,229,0.055), rgba(244,239,229,0.012)),
        rgba(18,21,20,0.88);
    box-shadow: var(--shadow-sm);
}
.advanced-mode-card h3 {
    margin: 0 0 8px !important;
    font-size: 16px !important;
    line-height: 1.25 !important;
}
.advanced-mode-card p {
    margin: 0 0 10px !important;
    color: var(--text-secondary) !important;
    font-size: 13px;
    line-height: 1.48;
}
.advanced-mode-row {
    display: grid;
    grid-template-columns: 82px minmax(0, 1fr);
    gap: 8px;
    border-top: 1px solid rgba(214,196,166,0.12);
    padding-top: 8px;
    margin-top: 8px;
    font-size: 12px;
    line-height: 1.35;
}
.advanced-mode-row strong {
    color: var(--accent) !important;
    font-family: var(--font-mono);
    font-size: 10.5px;
    text-transform: uppercase;
}
.advanced-mode-row span {
    color: var(--text-secondary) !important;
    overflow-wrap: anywhere;
}
.image-preview-title {
    color: var(--accent) !important;
    font-family: var(--font-mono);
    font-size: 12px;
    font-weight: 800;
    letter-spacing: 0;
    margin: 0 0 10px;
    text-align: center;
    text-transform: uppercase;
}
div[data-testid="stImage"] img {
    border: 1px solid rgba(214,196,166,0.18);
    border-radius: var(--radius-lg);
    box-shadow: var(--shadow-sm);
}
div[data-testid="stAlert"] {
    border-radius: var(--radius-md) !important;
    border: 1px solid rgba(214,196,166,0.16) !important;
}

@media (max-width: 900px) {
    .play-compact-strip,
    .action-state,
    .advanced-mode-card {
        padding: 13px 14px;
    }
    .advanced-mode-card {
        min-height: auto;
    }
    .play-status-grid {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }
}

@media (max-width: 640px) {
    div[data-testid="stHorizontalBlock"]:has(.play-panel-heading):has(.ai-solver-card) {
        gap: 8px !important;
    }
    div[class*="number_board"] div[data-testid="stHorizontalBlock"] {
        width: min(100%, 296px) !important;
        gap: 6px !important;
    }
    div[class*="number_board"] button,
    div[class*="number_board"] .puzzle-tile {
        font-size: 22px !important;
        border-radius: 9px !important;
    }
    .play-compact-strip {
        padding: 8px 11px;
        margin-bottom: 10px;
    }
    .play-compact-strip h2 {
        font-size: 17px !important;
        margin-bottom: 0 !important;
    }
    .play-compact-strip p {
        display: none;
    }
    .play-panel-heading {
        margin-bottom: 6px;
    }
    .play-panel-heading h2 {
        font-size: 20px !important;
        margin-bottom: 0 !important;
    }
    .play-panel-heading p {
        display: none;
    }
    .ai-solver-card {
        padding: 10px 11px !important;
        margin: 7px 0 !important;
        border-radius: var(--radius-md) !important;
    }
    .ai-solver-header {
        border-bottom: 0 !important;
        padding-bottom: 0 !important;
        margin-bottom: 0 !important;
    }
    .ai-solver-title-container {
        align-items: flex-start !important;
        flex-direction: column !important;
        gap: 5px !important;
    }
    .ai-solver-title-container h3 {
        font-size: 17px !important;
    }
    .ai-solver-desc {
        display: none;
    }
    .ai-contract-grid {
        grid-template-columns: 1fr;
    }
    .solution-step-card,
    .solution-step-mode-image .solution-step-card {
        grid-template-columns: 1fr;
    }
    .solution-step-meta {
        grid-template-columns: auto 1fr;
        align-items: center;
    }
    .search-tree-readable-summary {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }
    .search-tree-readable-context {
        grid-template-columns: 1fr;
    }
    .search-tree-readable-spine {
        grid-template-columns: 1fr;
    }
    .search-tree-readable .puzzle-grid-mini {
        transform: none;
        margin: 0;
    }
    .play-status-grid {
        gap: 8px;
    }
    .play-status-card {
        min-height: 68px;
        padding: 9px 10px;
    }
    .play-status-value {
        font-size: 22px;
        margin-top: 6px;
    }
    .advanced-mode-row {
        grid-template-columns: minmax(0, 1fr);
        gap: 3px;
    }
    div[data-testid="stMetric"] {
        padding: 10px 11px;
    }
}
/* Prevent grey out/dimming of stale elements during script rerun/autoplay */
div[data-stale="true"],
div[stale-data="true"],
.st-stale,
[data-stale="true"],
[stale-data="true"] {
    opacity: 1 !important;
    filter: none !important;
}
[data-stale="true"] *,
[stale-data="true"] *,
.st-stale * {
    opacity: 1 !important;
    filter: none !important;
}
</style>
"""

GROUP_COLORS = {
    "Uninformed Search": {"badge": "group-uninformed", "color": "#d6a15f", "bg": "#6e4324",
                           "icon": "Search", "emoji": ""},
    "Informed Search": {"badge": "group-informed", "color": "#7aa66a", "bg": "#3d5139",
                         "icon": "Lightbulb", "emoji": ""},
    "Local Search": {"badge": "group-local", "color": "#c69053", "bg": "#674020",
                      "icon": "Terrain", "emoji": ""},
    "Complex Environments": {"badge": "group-complex", "color": "#8ca18e", "bg": "#405246",
                              "icon": "Globe", "emoji": ""},
    "CSP": {"badge": "group-csp", "color": "#6f8e60", "bg": "#344435",
             "icon": "Grid", "emoji": ""},
    "AI-vs-AI Tournament": {"badge": "group-adversarial", "color": "#d66a5f", "bg": "#6f332e",
                             "icon": "Trophy", "emoji": ""},
}

ALGORITHM_GROUPS = {
    "Uninformed Search": ["BFS", "DFS", "UCS", "IDS"],
    "Informed Search": ["Greedy Best-First", "A*", "IDA*"],
    "Local Search": ["Simple Hill Climbing", "Steepest-Ascent Hill Climbing",
                     "Stochastic Hill Climbing", "Random-Restart Hill Climbing",
                     "Local Beam Search", "Simulated Annealing"],
    "Complex Environments": ["AND-OR Search", "Searching with no observation",
                            "Searching for partially observable problems", "LRTA*"],
    "CSP": ["CSP Definition", "Constraint Propagation", "Path Consistency",
            "Global Constraints", "Backtracking Search", "Min-Conflicts",
            "Constraint Graphs"],
    "AI-vs-AI Tournament": ["AI-vs-AI Tournament", "Minimax", "Alpha-Beta Pruning", "Expectimax"],
}

# Standard deterministic 15-puzzle pages use this subset. Extensions remain
# available in the Advanced concept lab and in the full theory taxonomy.
SOLVER_GROUPS = {
    name: algorithms
    for name, algorithms in ALGORITHM_GROUPS.items()
    if name in {"Uninformed Search", "Informed Search", "Local Search"}
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
    "Searching with no observation": "no_observation_search",
    "Searching for partially observable problems": "partially_observable_search",
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
    "AI-vs-AI Tournament": "ai_vs_ai_tournament",
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
    "Searching with no observation": "No Observation",
    "Searching for partially observable problems": "Partially Observable",
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
    "AI-vs-AI Tournament": "AI-vs-AI Tournament",
}

COMPARISON_TABLE = [
    {"Group": "Uninformed", "Algorithm": "BFS", "Complete": "Yes", "Optimal": "Yes*", "Heuristic": "No", "Random": "No", "Suitable": "Limited (memory)"},
    {"Group": "Uninformed", "Algorithm": "DFS", "Complete": "No", "Optimal": "No", "Heuristic": "No", "Random": "No", "Suitable": "No"},
    {"Group": "Uninformed", "Algorithm": "UCS", "Complete": "Yes", "Optimal": "Yes", "Heuristic": "No", "Random": "No", "Suitable": "Same as BFS"},
    {"Group": "Uninformed", "Algorithm": "IDS", "Complete": "Yes", "Optimal": "Yes*", "Heuristic": "No", "Random": "No", "Suitable": "Good (low memory)"},
    {"Group": "Informed", "Algorithm": "Greedy Best-First", "Complete": "No", "Optimal": "No", "Heuristic": "h(n)", "Random": "No", "Suitable": "Fast, suboptimal"},
    {"Group": "Informed", "Algorithm": "A*", "Complete": "Yes", "Optimal": "Yes", "Heuristic": "g+h", "Random": "No", "Suitable": "Best choice"},
    {"Group": "Informed", "Algorithm": "IDA*", "Complete": "Yes", "Optimal": "Yes", "Heuristic": "g+h", "Random": "No", "Suitable": "Memory efficient"},
    {"Group": "Local", "Algorithm": "Simple Hill Climbing", "Complete": "No", "Optimal": "No", "Heuristic": "h(n)", "Random": "No", "Suitable": "Gets stuck"},
    {"Group": "Local", "Algorithm": "Steepest-Ascent Hill Climbing", "Complete": "No", "Optimal": "No", "Heuristic": "h(n)", "Random": "No", "Suitable": "Gets stuck"},
    {"Group": "Local", "Algorithm": "Stochastic Hill Climbing", "Complete": "No", "Optimal": "No", "Heuristic": "h(n)", "Random": "Yes", "Suitable": "Gets stuck"},
    {"Group": "Local", "Algorithm": "Random-Restart Hill Climbing", "Complete": "No", "Optimal": "No", "Heuristic": "h(n)", "Random": "Yes", "Suitable": "May find solution"},
    {"Group": "Local", "Algorithm": "Local Beam Search", "Complete": "No", "Optimal": "No", "Heuristic": "h(n)", "Random": "No", "Suitable": "Better than HC"},
    {"Group": "Local", "Algorithm": "Simulated Annealing", "Complete": "No", "Optimal": "No", "Heuristic": "h(n)", "Random": "Yes", "Suitable": "Unreliable"},
    {"Group": "Complex", "Algorithm": "AND-OR Search", "Complete": "No", "Optimal": "No", "Heuristic": "h(n)", "Random": "No", "Suitable": "Extended env"},
    {"Group": "Complex", "Algorithm": "Searching with no observation", "Complete": "No", "Optimal": "No", "Heuristic": "h(n)", "Random": "No", "Suitable": "Illustrative"},
    {"Group": "Complex", "Algorithm": "Searching for partially observable problems", "Complete": "No", "Optimal": "No", "Heuristic": "h(n)", "Random": "No", "Suitable": "Illustrative"},
    {"Group": "Complex", "Algorithm": "LRTA*", "Complete": "No", "Optimal": "No", "Heuristic": "h(n)", "Random": "No", "Suitable": "Online demo"},
    {"Group": "CSP", "Algorithm": "CSP Definition", "Complete": "-", "Optimal": "-", "Heuristic": "No", "Random": "No", "Suitable": "Illustrative"},
    {"Group": "CSP", "Algorithm": "Constraint Propagation", "Complete": "-", "Optimal": "-", "Heuristic": "No", "Random": "No", "Suitable": "Illustrative"},
    {"Group": "CSP", "Algorithm": "Path Consistency", "Complete": "-", "Optimal": "-", "Heuristic": "No", "Random": "No", "Suitable": "Illustrative"},
    {"Group": "CSP", "Algorithm": "Global Constraints", "Complete": "-", "Optimal": "-", "Heuristic": "No", "Random": "No", "Suitable": "Illustrative"},
    {"Group": "CSP", "Algorithm": "Constraint Graphs", "Complete": "-", "Optimal": "-", "Heuristic": "No", "Random": "No", "Suitable": "Illustrative"},
    {"Group": "CSP", "Algorithm": "Backtracking Search", "Complete": "No", "Optimal": "No", "Heuristic": "Manhattan Distance", "Random": "No", "Suitable": "Planning demo"},
    {"Group": "CSP", "Algorithm": "Min-Conflicts", "Complete": "No", "Optimal": "No", "Heuristic": "Conflicts", "Random": "Yes", "Suitable": "N-Queens better"},
    {"Group": "AI-vs-AI", "Algorithm": "AI-vs-AI Tournament", "Complete": "Reference-bound", "Optimal": "Scored by A*", "Heuristic": "Depends on agents", "Random": "Optional", "Suitable": "Competition demo"},
    {"Group": "Game/Chance", "Algorithm": "Minimax", "Complete": "No", "Optimal": "No", "Heuristic": "utility h", "Random": "No", "Suitable": "Artificial extension"},
    {"Group": "Game/Chance", "Algorithm": "Alpha-Beta Pruning", "Complete": "No", "Optimal": "No", "Heuristic": "utility h", "Random": "No", "Suitable": "Pruning demo"},
    {"Group": "Game/Chance", "Algorithm": "Expectimax", "Complete": "No", "Optimal": "No", "Heuristic": "utility h", "Random": "Chance", "Suitable": "Stochastic demo"},
]

NOTES = """
* Optimal with unit cost. UCS = BFS for 15-puzzle (all moves cost 1).
  Greedy may find optimal path by chance but does NOT guarantee it.
  Hill Climbing variants typically get stuck at local optima on 15-puzzle.
  CSP, complex-environment, Minimax, Alpha-Beta, and Expectimax entries are illustrative extensions, not natural 15-puzzle solvers.
  AI-vs-AI Tournament is a scoring layer over solver outputs, not a natural adversarial PEAS model.
"""
