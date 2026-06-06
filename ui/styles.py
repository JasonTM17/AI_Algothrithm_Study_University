"""UI Styles for 15-Puzzle AI — Professional dark theme, slate/indigo palette."""

STYLES = """
<style>
/* ── Design Tokens ──────────────────────────────────────────── */
:root {
    --bg-app: #0f1117;
    --bg-surface: #1a1d27;
    --bg-elevated: #222636;
    --accent: #6366f1;
    --accent-hover: #818cf8;
    --accent-glow: rgba(99,102,241,0.35);
    --success: #22c55e;
    --success-glow: rgba(34,197,94,0.35);
    --error: #ef4444;
    --text-primary: #e2e8f0;
    --text-secondary: #94a3b8;
    --border-subtle: rgba(255,255,255,0.06);
    --radius-sm: 8px;
    --radius-md: 12px;
    --radius-lg: 16px;
    --shadow-sm: 0 1px 3px rgba(0,0,0,0.3);
    --shadow-md: 0 4px 14px rgba(0,0,0,0.4);
    --shadow-lg: 0 8px 30px rgba(0,0,0,0.5);
    --font-stack: 'Inter', 'Segoe UI', system-ui, -apple-system, sans-serif;
    --transition-fast: 0.15s cubic-bezier(0.4, 0, 0.2, 1);
}

/* ── Global ─────────────────────────────────────────────────── */
.stApp {
    background: var(--bg-app);
    font-family: var(--font-stack);
}
h1, h2, h3, h4, h5, h6 {
    color: var(--text-primary) !important;
    font-family: var(--font-stack);
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
}

/* ── Puzzle Board ───────────────────────────────────────────── */
.puzzle-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 6px;
    max-width: 380px;
    margin: 0 auto 12px;
    background: linear-gradient(145deg, #16162a, #1a1d27);
    padding: 14px;
    border-radius: 18px;
    box-shadow:
        0 12px 40px rgba(0,0,0,0.5),
        inset 0 1px 0 rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.05);
}

/* ── Game Tile (3D style) ───────────────────────────────────── */
.puzzle-tile {
    width: 80px;
    height: 80px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 30px;
    font-weight: 800;
    border-radius: 14px;
    user-select: none;
    position: relative;
    overflow: hidden;
    cursor: pointer;
    transition: transform 0.12s ease, box-shadow 0.12s ease;
    text-shadow: 0 2px 4px rgba(0,0,0,0.3);
}

/* Row-based color palette */
.puzzle-tile.row-0 {
    background: linear-gradient(145deg, #7c3aed, #5b21b6);
    box-shadow:
        0 6px 20px rgba(124,58,237,0.35),
        0 2px 6px rgba(0,0,0,0.3),
        inset 0 2px 0 rgba(255,255,255,0.18),
        inset 0 -2px 4px rgba(0,0,0,0.12);
}
.puzzle-tile.row-1 {
    background: linear-gradient(145deg, #6366f1, #4f46e5);
    box-shadow:
        0 6px 20px rgba(99,102,241,0.35),
        0 2px 6px rgba(0,0,0,0.3),
        inset 0 2px 0 rgba(255,255,255,0.18),
        inset 0 -2px 4px rgba(0,0,0,0.12);
}
.puzzle-tile.row-2 {
    background: linear-gradient(145deg, #0891b2, #0e7490);
    box-shadow:
        0 6px 20px rgba(8,145,178,0.35),
        0 2px 6px rgba(0,0,0,0.3),
        inset 0 2px 0 rgba(255,255,255,0.18),
        inset 0 -2px 4px rgba(0,0,0,0.12);
}
.puzzle-tile.row-3 {
    background: linear-gradient(145deg, #db2777, #be185d);
    box-shadow:
        0 6px 20px rgba(219,39,119,0.35),
        0 2px 6px rgba(0,0,0,0.3),
        inset 0 2px 0 rgba(255,255,255,0.18),
        inset 0 -2px 4px rgba(0,0,0,0.12);
}

.puzzle-tile:hover {
    transform: translateY(-3px);
    box-shadow:
        0 10px 28px rgba(0,0,0,0.45),
        0 4px 10px rgba(0,0,0,0.3),
        inset 0 2px 0 rgba(255,255,255,0.22),
        inset 0 -2px 4px rgba(0,0,0,0.1) !important;
}
.puzzle-tile:active {
    transform: scale(0.94);
    box-shadow:
        0 2px 8px rgba(0,0,0,0.4),
        inset 0 1px 0 rgba(255,255,255,0.08) !important;
}

/* Correct position tiles */
.puzzle-tile.correct {
    background: linear-gradient(145deg, #22c55e, #15803d) !important;
    box-shadow:
        0 6px 20px rgba(34,197,94,0.35),
        0 2px 6px rgba(0,0,0,0.25),
        inset 0 2px 0 rgba(255,255,255,0.18),
        inset 0 -2px 4px rgba(0,0,0,0.1) !important;
}

/* Blank tile with checkerboard */
.puzzle-tile.blank {
    background: #1a1d27 !important;
    box-shadow: inset 0 4px 16px rgba(0,0,0,0.55) !important;
    border: 1px dashed rgba(255,255,255,0.06);
    cursor: default;
}
.puzzle-tile.blank::after {
    content: '';
    position: absolute;
    inset: 0;
    background-image:
        linear-gradient(45deg, rgba(255,255,255,0.025) 25%, transparent 25%),
        linear-gradient(-45deg, rgba(255,255,255,0.025) 25%, transparent 25%),
        linear-gradient(45deg, transparent 75%, rgba(255,255,255,0.025) 75%),
        linear-gradient(-45deg, transparent 75%, rgba(255,255,255,0.025) 75%);
    background-size: 16px 16px;
    background-position: 0 0, 0 8px, 8px -8px, -8px 0;
    border-radius: 14px;
}
.puzzle-tile.blank:hover {
    transform: none;
}

/* Slide animation */
@keyframes tileSlideFrom {
    from { transform: translate(var(--slide-from-x, 0), var(--slide-from-y, 0)); opacity: 0.8; }
    to   { transform: translate(0, 0); opacity: 1; }
}
.puzzle-tile.slide-anim {
    animation: tileSlideFrom 0.18s cubic-bezier(0.4, 0, 0.2, 1);
}

/* Goal pulse */
@keyframes goalPulse {
    0%, 100% { box-shadow: 0 6px 20px rgba(34,197,94,0.35), 0 2px 6px rgba(0,0,0,0.25), inset 0 2px 0 rgba(255,255,255,0.18), inset 0 -2px 4px rgba(0,0,0,0.1); }
    50%      { box-shadow: 0 6px 32px rgba(34,197,94,0.55), 0 0 20px rgba(34,197,94,0.25), inset 0 2px 0 rgba(255,255,255,0.22), inset 0 -2px 4px rgba(0,0,0,0.1); }
}
.puzzle-tile.correct.goal-flash { animation: goalPulse 0.5s ease-in-out 3; }

/* Board entrance */
@keyframes boardFadeIn {
    from { opacity: 0; transform: scale(0.96); }
    to   { opacity: 1; transform: scale(1); }
}
.puzzle-grid { animation: boardFadeIn 0.35s ease-out; }

/* ── Legacy puzzle-cell (for static displays like trace tables) ─ */
.puzzle-cell {
    width: 80px;
    height: 80px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 28px;
    font-weight: 800;
    border-radius: var(--radius-md);
    transition: transform var(--transition-fast), box-shadow var(--transition-fast);
    user-select: none;
    position: relative;
    overflow: hidden;
}
.puzzle-cell.filled {
    background: linear-gradient(145deg, var(--accent), #4f46e5);
    color: #ffffff;
    box-shadow: 0 4px 14px var(--accent-glow), inset 0 1px 0 rgba(255,255,255,0.12);
    border: 1px solid rgba(255,255,255,0.08);
}
.puzzle-cell.blank {
    background: transparent;
    box-shadow: inset 0 3px 12px rgba(0,0,0,0.5);
    border: 1px dashed rgba(255,255,255,0.06);
}
.puzzle-cell.correct {
    background: linear-gradient(145deg, var(--success), #16a34a);
    box-shadow: 0 4px 14px var(--success-glow), inset 0 1px 0 rgba(255,255,255,0.12);
    border: 1px solid rgba(255,255,255,0.1);
}
.puzzle-cell img.tile-img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    border-radius: 10px;
    position: absolute;
    top: 0;
    left: 0;
}
@keyframes slideIn {
    from { transform: scale(0.8); opacity: 0.5; }
    to   { transform: scale(1); opacity: 1; }
}
.puzzle-cell.slide-in { animation: slideIn 0.15s ease-out; }

/* ── Mini puzzle grid (trace tables) ────────────────────────── */
.puzzle-grid-mini {
    display: inline-grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1px;
    background: var(--bg-surface);
    padding: 3px;
    border-radius: 6px;
    font-size: 8px;
    margin: 2px 0;
    border: 1px solid var(--border-subtle);
}
.puzzle-grid-mini .mc {
    width: 18px; height: 18px;
    display: flex; align-items: center; justify-content: center;
    border-radius: 3px;
    font-weight: 700;
    font-size: 7px;
}
.puzzle-grid-mini .mc.f { background: linear-gradient(135deg, var(--accent), #4f46e5); color: #fff; }
.puzzle-grid-mini .mc.b { background: transparent; border: 1px dashed rgba(255,255,255,0.06); }
.puzzle-grid-mini .mc.c { background: linear-gradient(135deg, var(--success), #16a34a); color: #fff; }

/* ── Result cards ────────────────────────────────────────────── */
.result-success {
    border-left: 4px solid var(--success);
    background: linear-gradient(90deg, rgba(34,197,94,0.08), transparent);
    padding: 12px 16px;
    border-radius: var(--radius-sm);
    margin: 8px 0;
}
.result-failure {
    border-left: 4px solid var(--error);
    background: linear-gradient(90deg, rgba(239,68,68,0.08), transparent);
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
.group-uninformed { background: linear-gradient(135deg, #4f46e5, var(--accent)); color: white; }
.group-informed  { background: linear-gradient(135deg, var(--accent), #818cf8); color: white; }
.group-local      { background: linear-gradient(135deg, #e11d48, #be123c); color: white; }
.group-complex    { background: linear-gradient(135deg, #7c3aed, #6d28d9); color: white; }
.group-csp        { background: linear-gradient(135deg, var(--success), #16a34a); color: #0f1117; }
.group-adversarial { background: linear-gradient(135deg, var(--error), #dc2626); color: white; }

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
    background: linear-gradient(180deg, #16162a 0%, var(--bg-app) 100%) !important;
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
    border: 1px solid var(--border-subtle);
    white-space: pre;
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
    {"Group": "Local", "Algorithm": "Sim. Annealing", "Complete": "No", "Optimal": "No", "Heuristic": "h(n)", "Random": "Yes", "Suitable": "Unreliable"},
    {"Group": "Complex", "Algorithm": "AND-OR", "Complete": "Yes", "Optimal": "No", "Heuristic": "No", "Random": "No", "Suitable": "Nondeterministic"},
    {"Group": "Complex", "Algorithm": "LRTA*", "Complete": "Yes", "Optimal": "No", "Heuristic": "h(n)", "Random": "No", "Suitable": "Online learning"},
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
