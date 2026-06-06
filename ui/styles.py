"""UI Styles for 15-Puzzle AI — Professional dark theme, slate/indigo palette."""

STYLES = """
<style>
/* ── Design Tokens ──────────────────────────────────────────── */
:root {
    --bg-app: #15110e;
    --bg-surface: #221a15;
    --bg-elevated: #2d231d;
    --accent: #c8956c;
    --accent-hover: #e3b68e;
    --accent-glow: rgba(200,149,108,0.2);
    --success: #557c55;
    --success-glow: rgba(85,124,85,0.2);
    --error: #af4d4d;
    --text-primary: #f0e6dc;
    --text-secondary: #a6988f;
    --border-subtle: rgba(200,149,108,0.1);
    --radius-sm: 6px;
    --radius-md: 10px;
    --radius-lg: 14px;
    --shadow-sm: 0 2px 4px rgba(0,0,0,0.4);
    --shadow-md: 0 6px 16px rgba(0,0,0,0.5);
    --shadow-lg: 0 12px 32px rgba(0,0,0,0.6);
    --font-stack: 'Georgia', 'Playfair Display', -apple-system, sans-serif;
    --transition-fast: 0.1s ease;
}

/* ── Global ─────────────────────────────────────────────────── */
.stApp {
    background: var(--bg-app);
    font-family: var(--font-stack);
}
h1, h2, h3, h4, h5, h6 {
    color: var(--text-primary) !important;
    font-family: var(--font-stack);
    font-weight: 700 !important;
}
p, li, label, div {
    color: var(--text-primary);
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
}

/* ── Puzzle Board ───────────────────────────────────────────── */
.puzzle-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 8px;
    max-width: 380px;
    margin: 0 auto 12px;
    background: #1a100a;
    padding: 16px;
    border-radius: 16px;
    border: 12px solid #3c2415;
    box-shadow:
        0 16px 36px rgba(0,0,0,0.6),
        inset 0 6px 12px rgba(0,0,0,0.8),
        0 4px 0 #23140a;
}

/* ── Game Tile (Tactile Wood) ─────────────────────────────────── */
.puzzle-tile {
    width: 80px;
    height: 80px;
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

/* Row-based wood finishes */
.puzzle-tile.row-0 {
    background: linear-gradient(145deg, #f0cfad, #cfa87c) !important;
    color: #422510 !important;
    box-shadow:
        0 4px 8px rgba(0,0,0,0.4),
        inset 0 1px 0 rgba(255,255,255,0.3);
    border-top: 1px solid rgba(255,255,255,0.3) !important;
    border-left: 1px solid rgba(255,255,255,0.1) !important;
    border-bottom: 3px solid #6b4d2e !important;
    border-right: 3px solid #6b4d2e !important;
}
.puzzle-tile.row-1 {
    background: linear-gradient(145deg, #d38d72, #ab5d43) !important;
    color: #3b170c !important;
    box-shadow:
        0 4px 8px rgba(0,0,0,0.4),
        inset 0 1px 0 rgba(255,255,255,0.25);
    border-top: 1px solid rgba(255,255,255,0.25) !important;
    border-left: 1px solid rgba(255,255,255,0.1) !important;
    border-bottom: 3px solid #5a2717 !important;
    border-right: 3px solid #5a2717 !important;
}
.puzzle-tile.row-2 {
    background: linear-gradient(145deg, #ab6a50, #80432c) !important;
    color: #2e0f06 !important;
    box-shadow:
        0 4px 8px rgba(0,0,0,0.4),
        inset 0 1px 0 rgba(255,255,255,0.2);
    border-top: 1px solid rgba(255,255,255,0.2) !important;
    border-left: 1px solid rgba(255,255,255,0.1) !important;
    border-bottom: 3px solid #4a190a !important;
    border-right: 3px solid #4a190a !important;
}
.puzzle-tile.row-3 {
    background: linear-gradient(145deg, #825f44, #573b26) !important;
    color: #e6dfd5 !important;
    box-shadow:
        0 4px 8px rgba(0,0,0,0.4),
        inset 0 1px 0 rgba(255,255,255,0.15);
    border-top: 1px solid rgba(255,255,255,0.15) !important;
    border-left: 1px solid rgba(255,255,255,0.08) !important;
    border-bottom: 3px solid #362214 !important;
    border-right: 3px solid #362214 !important;
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
    background: linear-gradient(180deg, #1d1714 0%, #100c0a 100%) !important;
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
    {"Group": "Local", "Algorithm": "Random-Restart HC", "Complete": "Asymptotic", "Optimal": "No", "Heuristic": "h(n)", "Random": "Yes", "Suitable": "May find solution"},
    {"Group": "Local", "Algorithm": "Beam Search", "Complete": "No", "Optimal": "No", "Heuristic": "h(n)", "Random": "No", "Suitable": "Better than HC"},
    {"Group": "Local", "Algorithm": "Sim. Annealing", "Complete": "No", "Optimal": "No", "Heuristic": "h(n)", "Random": "Yes", "Suitable": "Unreliable"},
    {"Group": "Complex", "Algorithm": "AND-OR", "Complete": "Yes", "Optimal": "No", "Heuristic": "No", "Random": "No", "Suitable": "Nondeterministic"},
    {"Group": "Complex", "Algorithm": "No Observation", "Complete": "No", "Optimal": "No", "Heuristic": "h(n)", "Random": "No", "Suitable": "Academic"},
    {"Group": "Complex", "Algorithm": "Partial Obs.", "Complete": "No", "Optimal": "No", "Heuristic": "h(n)", "Random": "No", "Suitable": "Academic"},
    {"Group": "Complex", "Algorithm": "LRTA*", "Complete": "Yes", "Optimal": "No", "Heuristic": "h(n)", "Random": "No", "Suitable": "Online learning"},
    {"Group": "CSP", "Algorithm": "CSP Definition", "Complete": "-", "Optimal": "-", "Heuristic": "No", "Random": "No", "Suitable": "Illustrative"},
    {"Group": "CSP", "Algorithm": "Propagation", "Complete": "-", "Optimal": "-", "Heuristic": "No", "Random": "No", "Suitable": "Illustrative"},
    {"Group": "CSP", "Algorithm": "Path Consistency", "Complete": "-", "Optimal": "-", "Heuristic": "No", "Random": "No", "Suitable": "Illustrative"},
    {"Group": "CSP", "Algorithm": "Global Constraints", "Complete": "-", "Optimal": "-", "Heuristic": "No", "Random": "No", "Suitable": "Illustrative"},
    {"Group": "CSP", "Algorithm": "Constraint Graphs", "Complete": "-", "Optimal": "-", "Heuristic": "No", "Random": "No", "Suitable": "Illustrative"},
    {"Group": "CSP", "Algorithm": "Backtracking", "Complete": "Yes", "Optimal": "Yes", "Heuristic": "MRV+LCV", "Random": "No", "Suitable": "Not standard"},
    {"Group": "CSP", "Algorithm": "Min-Conflicts", "Complete": "No", "Optimal": "No", "Heuristic": "Conflicts", "Random": "Yes", "Suitable": "N-Queens better"},
    {"Group": "Adversarial", "Algorithm": "Minimax", "Complete": "Yes", "Optimal": "Yes", "Heuristic": "No", "Random": "No", "Suitable": "2-player game"},
    {"Group": "Adversarial", "Algorithm": "Alpha-Beta", "Complete": "Yes", "Optimal": "Yes", "Heuristic": "No", "Random": "No", "Suitable": "2-player (faster)"},
    {"Group": "Adversarial", "Algorithm": "Expectimax", "Complete": "Yes", "Optimal": "Yes", "Heuristic": "No", "Random": "No", "Suitable": "Stochastic env"},
]

NOTES = """
* Optimal with unit cost. UCS = BFS for 15-puzzle (all moves cost 1).
  Greedy may find optimal path by chance but does NOT guarantee it.
  Hill Climbing variants typically get stuck at local optima on 15-puzzle.
  CSP algorithms are academic simulations (15-puzzle is not a natural CSP).
"""
