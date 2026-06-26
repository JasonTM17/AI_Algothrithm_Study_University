"""Syllabus-facing academic coverage data for the Theory/PEAS page."""

from __future__ import annotations


SYLLABUS_COVERAGE_ROWS = [
    {
        "Syllabus topic": "Main steps of search algorithms",
        "App surface": "Theory/PEAS -> Search Foundations; Run Algorithm trace",
        "Evidence": "Frontier, reached set, expanded node, termination reason, and run certificate.",
        "Defense note": "Use this before comparing algorithms so the grader sees the common search loop.",
    },
    {
        "Syllabus topic": "Tree search and graph search",
        "App surface": "Theory/PEAS -> Tree Search vs Graph Search; Step Trace; Hand-Tracing",
        "Evidence": "Parent-child Graphviz edges plus reached/best_g duplicate handling.",
        "Defense note": "The app uses graph-search safeguards for standard solvers, while still visualizing the tree of generated edges.",
    },
    {
        "Syllabus topic": "Uninformed search algorithms",
        "App surface": "Run Algorithm and Compare -> Uninformed Search",
        "Evidence": "BFS, DFS, UCS, IDS implementations with trace and path certificates.",
        "Defense note": "BFS/UCS/IDS can prove shortest paths under unit step cost; DFS is a contrast demo.",
    },
    {
        "Syllabus topic": "Breadth-first search, Depth-first search and variants",
        "App surface": "Run Algorithm -> BFS, DFS, IDS",
        "Evidence": "Queue/stack/depth-limit behavior appears in trace, frontier, and search tree.",
        "Defense note": "IDS is the DFS variant used to recover BFS-like optimality with lower memory.",
    },
    {
        "Syllabus topic": "Best-first search",
        "App surface": "Theory/PEAS -> Informed Search; Run Algorithm -> Greedy Best-First and A*",
        "Evidence": "Priority queues ordered by h(n) for Greedy or f(n)=g(n)+h(n) for A*.",
        "Defense note": "Best-first is the family; Greedy and A* are two different evaluation rules inside it.",
    },
    {
        "Syllabus topic": "A* search",
        "App surface": "Run Algorithm, Compare, Play AI solver, Tournament reference",
        "Evidence": "A* reports g/h/f trace, path legality, goal reachability, and optimality_proven when bounded run completes.",
        "Defense note": "State the admissible/consistent heuristic condition before claiming optimality.",
    },
    {
        "Syllabus topic": "Heuristic functions generation",
        "App surface": "Theory/PEAS -> Heuristic Generation; core heuristics",
        "Evidence": "Misplaced Tiles, Manhattan Distance, and Linear Conflict with admissibility notes.",
        "Defense note": "Each heuristic comes from a relaxed or necessary-cost argument, not from arbitrary scoring.",
    },
    {
        "Syllabus topic": "Hill-climbing search",
        "App surface": "Run Algorithm -> Local Search",
        "Evidence": "Simple, steepest-ascent, stochastic, and random-restart hill climbing variants.",
        "Defense note": "Present as local optimization over h(n), not as a reliable 15-puzzle solver.",
    },
    {
        "Syllabus topic": "Issues of hill-climbing search",
        "App surface": "Theory/PEAS -> Hill-Climbing Issues; teaching preset",
        "Evidence": "Local optimum preset plus plateau, ridge, sideways, and stochastic escape notes.",
        "Defense note": "This is the main reason local search is a contrast demo in this project.",
    },
    {
        "Syllabus topic": "Local beam search",
        "App surface": "Run Algorithm -> Local Beam Search",
        "Evidence": "Beam width parameter and best-beam trajectory trace.",
        "Defense note": "Beam keeps k candidates but can still discard the solution branch.",
    },
    {
        "Syllabus topic": "Simulated annealing",
        "App surface": "Run Algorithm -> Simulated Annealing",
        "Evidence": "Temperature, cooling rate, min temperature, and stochastic seed controls.",
        "Defense note": "Accepting worse moves can escape local optima but does not give finite optimality proof.",
    },
    {
        "Syllabus topic": "AND-OR search",
        "App surface": "Advanced -> AND-OR Search (Nondeterministic)",
        "Evidence": "Conditional plan text distinguishes OR agent choices from AND outcome obligations.",
        "Defense note": "This is a nondeterministic extension; standard 15-puzzle remains deterministic.",
    },
    {
        "Syllabus topic": "Searching with no observation",
        "App surface": "Advanced -> No Observation (Belief State)",
        "Evidence": "Belief-set trace and representative action sequence.",
        "Defense note": "The sensor model is intentionally weakened, changing the state representation.",
    },
    {
        "Syllabus topic": "Searching for partially observable problems",
        "App surface": "Advanced -> Partially Observable",
        "Evidence": "Observation field and belief filtering evidence in the trace.",
        "Defense note": "Use it to discuss filtering, not shortest-path optimality.",
    },
    {
        "Syllabus topic": "Online search",
        "App surface": "Advanced -> Online Search (LRTA*)",
        "Evidence": "LRTA* updates learned H(state) while moving.",
        "Defense note": "Online agent behavior is intentionally different from offline A* planning.",
    },
    {
        "Syllabus topic": "Definition of a constraint satisfaction problem",
        "App surface": "Advanced -> CSP Definition & Propagation",
        "Evidence": "CSP=(X,D,C), time-indexed variables, domains, and constraints.",
        "Defense note": "This is a planning formulation, not the natural standard solver.",
    },
    {
        "Syllabus topic": "Constraint propagation",
        "App surface": "Advanced -> CSP Definition & Propagation",
        "Evidence": "AC-3 state-chain CSP returns exact-horizon path or domain wipe-out.",
        "Defense note": "Only claim completeness for the bounded chain/horizon being displayed.",
    },
    {
        "Syllabus topic": "Path consistency",
        "App surface": "Advanced -> Constraint Graphs & Path Consistency",
        "Evidence": "Path-consistency concept output and complexity comparison.",
        "Defense note": "Higher consistency is more expensive and is used here as a concept lab.",
    },
    {
        "Syllabus topic": "Global constraints",
        "App surface": "Theory/PEAS -> CSP; Advanced model output",
        "Evidence": "AllDifferent explanation for tile placement at each time step.",
        "Defense note": "Global constraints compactly express many pairwise not-equal constraints.",
    },
    {
        "Syllabus topic": "Backtracking search",
        "App surface": "Advanced -> Backtracking & Min-Conflicts",
        "Evidence": "Bounded DFS transition planning with heuristic value ordering.",
        "Defense note": "Do not call this MRV/forward-checking; failure is not a proof of unsolvability.",
    },
    {
        "Syllabus topic": "Min-conflicts algorithm",
        "App surface": "Advanced -> Backtracking & Min-Conflicts",
        "Evidence": "Tile-placement repair contrast with explicit non-legal-move caveat.",
        "Defense note": "Min-conflicts is more natural for N-Queens than for legal blank-slide planning.",
    },
    {
        "Syllabus topic": "Solve CSPs using constraint graphs",
        "App surface": "Advanced -> Constraint Graphs & Path Consistency",
        "Evidence": "Variable/constraint graph artifact for bounded planning horizon.",
        "Defense note": "Use it to show why the CSP representation grows quickly.",
    },
    {
        "Syllabus topic": "Minimax",
        "App surface": "Advanced -> Minimax Game; Theory/PEAS -> AI-vs-AI Tournament group",
        "Evidence": "MAX/MIN depth-limited game-tree selected variation.",
        "Defense note": "Artificial adversarial extension; 15-puzzle has no natural MIN player.",
    },
    {
        "Syllabus topic": "Alpha-Beta",
        "App surface": "Advanced -> Alpha-Beta Pruning Game",
        "Evidence": "Alpha/beta bounds and pruning count in the game-tree model.",
        "Defense note": "It preserves Minimax value only under the same fully searched finite tree assumptions.",
    },
    {
        "Syllabus topic": "Expectimax",
        "App surface": "Advanced -> Expectimax (Stochastic)",
        "Evidence": "Chance-node success probability and sampled path evidence.",
        "Defense note": "Expected utility needs a stated probability model; it is not alpha-beta pruning.",
    },
]


SEARCH_FOUNDATION_ROWS = [
    {
        "Step": "1. Initial state",
        "What to check": "A valid permutation of 0..15 and a selected goal.",
        "App evidence": "Start/Goal contract shown on Play, Run, Compare, and Advanced.",
    },
    {
        "Step": "2. Goal test",
        "What to check": "Whether the current state equals the selected goal.",
        "App evidence": "goal_reached is reported separately from path legality and success.",
    },
    {
        "Step": "3. Frontier selection",
        "What to check": "Queue, stack, g(n), h(n), f(n), beam, or temperature rule.",
        "App evidence": "Run trace and within-group comparison show each selection rule.",
    },
    {
        "Step": "4. Expansion",
        "What to check": "Legal L/R/U/D blank moves only.",
        "App evidence": "Search tree edges are recorded only when action(parent)=child.",
    },
    {
        "Step": "5. Reached handling",
        "What to check": "Duplicate states and better paths are handled explicitly.",
        "App evidence": "Graph-search solvers show reached set or best_g trace fields.",
    },
    {
        "Step": "6. Termination/certificate",
        "What to check": "Goal, timeout, node cap, model success, or failure.",
        "App evidence": "SearchResult exposes termination_reason, path_verified, goal_reached, and optimality_proven.",
    },
]


TREE_GRAPH_SEARCH_ROWS = [
    {
        "Model": "Tree search",
        "Core idea": "Treat every generated path as a separate node, even if states repeat.",
        "Risk": "Can revisit cycles and blow up quickly.",
        "App connection": "Graphviz search tree shows generated parent-child evidence.",
    },
    {
        "Model": "Graph search",
        "Core idea": "Remember reached states or best known g(n) to avoid dominated duplicates.",
        "Risk": "Needs memory and correct duplicate policy.",
        "App connection": "BFS/UCS/A*/Greedy/IDS traces expose reached or best_g behavior.",
    },
    {
        "Model": "Hand tracing",
        "Core idea": "The learner chooses the next frontier node and the app checks the selection rule.",
        "Risk": "Tie-break mistakes can change the expansion order.",
        "App connection": "Hand-Tracing records explicit graph edges and frontier choices.",
    },
]


HEURISTIC_GENERATION_ROWS = [
    {
        "Heuristic": "Misplaced Tiles",
        "Generation idea": "Relax distance and count each non-blank tile outside its goal square.",
        "Formula/example": "h(n)=number of misplaced non-blank tiles.",
        "Guarantee": "Admissible but weak because one tile may be many moves away.",
    },
    {
        "Heuristic": "Manhattan Distance",
        "Generation idea": "Relax blocking tiles; each tile still must pay row plus column distance.",
        "Formula/example": "sum(abs(row-row_goal)+abs(col-col_goal)).",
        "Guarantee": "Admissible and consistent for unit-cost sliding moves.",
    },
    {
        "Heuristic": "Linear Conflict",
        "Generation idea": "Add necessary extra moves when two goal-row/goal-column tiles block each other.",
        "Formula/example": "Manhattan + 2 * maximum disjoint linear conflicts.",
        "Guarantee": "Stronger than Manhattan while preserving admissibility in the app.",
    },
]


HILL_CLIMBING_ISSUE_ROWS = [
    {
        "Issue": "Local optimum",
        "What happens": "Every neighbor has h >= current h, so hill climbing stops before the goal.",
        "App evidence": "Teaching preset: Hill Climbing stuck: local optimum h=4.",
        "Mitigation/demo": "Random restart or simulated annealing can try to escape, without proof.",
    },
    {
        "Issue": "Plateau / shoulder",
        "What happens": "Many neighbors have equal h, so strict improvement gives no direction.",
        "App evidence": "Local-search theory labels these runs as contrast demos.",
        "Mitigation/demo": "Sideways moves or stochastic choice are educational variants, not optimal solvers.",
    },
    {
        "Issue": "Ridge",
        "What happens": "Progress may require a sequence of sideways or temporarily worse moves.",
        "App evidence": "Simulated Annealing exposes temperature-based acceptance of worse moves.",
        "Mitigation/demo": "Annealing may cross a ridge when temperature is still high.",
    },
    {
        "Issue": "Randomness dependence",
        "What happens": "Different seeds can produce different accepted trajectories.",
        "App evidence": "Stochastic HC, Random-Restart HC, and Simulated Annealing show run seeds.",
        "Mitigation/demo": "Report seed, max iterations, and restart/temperature parameters.",
    },
]


REQUIRED_SYLLABUS_TOPICS = tuple(row["Syllabus topic"] for row in SYLLABUS_COVERAGE_ROWS)
