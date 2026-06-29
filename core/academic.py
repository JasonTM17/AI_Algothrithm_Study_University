"""Academic presentation data for the 15-puzzle AI simulator."""

from __future__ import annotations

from dataclasses import dataclass


REAL_SOLVER = "real_solver"
CONTRAST_DEMO = "contrast_demo"
ILLUSTRATIVE_EXTENSION = "illustrative_extension"
STOCHASTIC_GAME_DEMO = "stochastic_game_demo"

VERIFIED_PATH = "verified_path"
PARTIAL_TRAJECTORY = "partial_trajectory"
CONDITIONAL_PLAN = "conditional_plan"
CONFORMANT_PLAN = "conformant_plan"
CONTINGENT_POLICY = "contingent_policy"
CSP_ASSIGNMENT_SEARCH = "csp_assignment_search"
CSP_PROPAGATION = "csp_propagation"
CSP_LOCAL_REPAIR = "csp_local_repair"
DECISION_POLICY = "decision_policy"
SCORED_BENCHMARK = "scored_benchmark"

ROLE_LABELS = {
    REAL_SOLVER: "Real Solver",
    CONTRAST_DEMO: "Contrast Demo",
    ILLUSTRATIVE_EXTENSION: "Illustrative Extension",
    STOCHASTIC_GAME_DEMO: "Tournament/Game Demo",
}


@dataclass(frozen=True)
class AlgorithmTaxonomy:
    role: str
    environment: str
    guarantee: str
    exam_note: str
    capability: str


ALGORITHM_TAXONOMY: dict[str, AlgorithmTaxonomy] = {
    "BFS": AlgorithmTaxonomy(REAL_SOLVER, "deterministic", "Complete, optimal with unit step cost.", "Good for proving optimality, but memory grows exponentially.", VERIFIED_PATH),
    "DFS": AlgorithmTaxonomy(CONTRAST_DEMO, "deterministic", "Not optimal; bounded runs may stop before the goal.", "Use to contrast LIFO exploration against poor solution guarantees.", VERIFIED_PATH),
    "UCS": AlgorithmTaxonomy(REAL_SOLVER, "deterministic", "Complete and optimal for positive costs.", "Equivalent to BFS in 15-puzzle because each move costs 1.", VERIFIED_PATH),
    "IDS": AlgorithmTaxonomy(REAL_SOLVER, "deterministic", "Complete and optimal with unit step cost.", "Best uninformed teaching choice when memory matters.", VERIFIED_PATH),
    "Greedy Best-First": AlgorithmTaxonomy(CONTRAST_DEMO, "deterministic", "Not complete or optimal in graph search practice.", "Fast heuristic-only baseline; compare against A* to show suboptimality.", VERIFIED_PATH),
    "A*": AlgorithmTaxonomy(REAL_SOLVER, "deterministic", "Complete and optimal with admissible, consistent heuristic.", "Primary reference solver for final-exam explanation.", VERIFIED_PATH),
    "IDA*": AlgorithmTaxonomy(REAL_SOLVER, "deterministic", "Optimal with admissible heuristic and bounded branching.", "A* quality with much lower memory, useful for deeper puzzles.", VERIFIED_PATH),
    "Simple Hill Climbing": AlgorithmTaxonomy(CONTRAST_DEMO, "deterministic", "Not complete or optimal.", "Shows local optimum failure clearly.", PARTIAL_TRAJECTORY),
    "Steepest-Ascent Hill Climbing": AlgorithmTaxonomy(CONTRAST_DEMO, "deterministic", "Not complete or optimal.", "Shows best-neighbor choice still cannot guarantee solution.", PARTIAL_TRAJECTORY),
    "Stochastic Hill Climbing": AlgorithmTaxonomy(CONTRAST_DEMO, "deterministic", "Not complete or optimal.", "Adds randomness but still may get stuck.", PARTIAL_TRAJECTORY),
    "Random-Restart Hill Climbing": AlgorithmTaxonomy(CONTRAST_DEMO, "deterministic", "Not optimal; probabilistic success only.", "Useful for explaining restarts, not a reliable 15-puzzle solver.", PARTIAL_TRAJECTORY),
    "Local Beam Search": AlgorithmTaxonomy(CONTRAST_DEMO, "deterministic", "Not complete or optimal.", "Shows multiple-state local search as a stronger contrast case.", PARTIAL_TRAJECTORY),
    "Simulated Annealing": AlgorithmTaxonomy(CONTRAST_DEMO, "deterministic", "No finite optimality guarantee.", "Good for explaining escape from local minima through temperature.", PARTIAL_TRAJECTORY),
    "AND-OR Search": AlgorithmTaxonomy(ILLUSTRATIVE_EXTENSION, "nondeterministic", "Returns a conditional plan in a fully observable nondeterministic model.", "Every supported outcome needs a subplan; this is not a linear solution path.", CONDITIONAL_PLAN),
    "Searching with no observation": AlgorithmTaxonomy(ILLUSTRATIVE_EXTENSION, "no_observation", "Searches belief states for one conformant action sequence.", "The decision must not inspect the hidden physical state.", CONFORMANT_PLAN),
    "Searching for partially observable problems": AlgorithmTaxonomy(ILLUSTRATIVE_EXTENSION, "partial_observable", "Returns a contingent policy over observation branches.", "Prediction and observation update operate on belief states.", CONTINGENT_POLICY),
    "Backtracking": AlgorithmTaxonomy(ILLUSTRATIVE_EXTENSION, "planning_csp", "Finds an exact-horizon state-chain assignment within resource bounds.", "A bounded CSP encoding, not a global shortest-path certificate.", CSP_ASSIGNMENT_SEARCH),
    "Backtracking + Forward Checking": AlgorithmTaxonomy(ILLUSTRATIVE_EXTENSION, "planning_csp", "Backtracking with domain pruning after each assignment.", "Compare assignment checks and pruned values against plain backtracking.", CSP_ASSIGNMENT_SEARCH),
    "AC-3": AlgorithmTaxonomy(ILLUSTRATIVE_EXTENSION, "planning_csp", "Enforces arc consistency on a bounded state-chain CSP.", "Arc-consistent domains are not automatically a solved puzzle.", CSP_PROPAGATION),
    "Min-Conflicts": AlgorithmTaxonomy(ILLUSTRATIVE_EXTENSION, "planning_csp", "Repairs a complete bounded CSP assignment; no completeness guarantee.", "Only a zero-conflict legal chain is a replayable puzzle path.", CSP_LOCAL_REPAIR),
    "AI-vs-AI Tournament": AlgorithmTaxonomy(STOCHASTIC_GAME_DEMO, "scored_competition", "Scores two solver agents against an A* reference.", "Use to compare AI outputs without claiming 15-puzzle has an opponent.", SCORED_BENCHMARK),
    "Minimax": AlgorithmTaxonomy(STOCHASTIC_GAME_DEMO, "worst_case_robustness", "Worst-case game-tree utility demo, not a standard solver.", "15-puzzle has no opponent; MIN is a robustness branch over legal moves.", DECISION_POLICY),
    "Alpha-Beta Pruning": AlgorithmTaxonomy(STOCHASTIC_GAME_DEMO, "worst_case_robustness", "Same minimax value with pruning when the worst-case tree is fully searched.", "Use to explain pruning, not puzzle optimality.", DECISION_POLICY),
    "Expectimax": AlgorithmTaxonomy(STOCHASTIC_GAME_DEMO, "stochastic", "Expected-utility demo under chance outcomes.", "Use only for stochastic action extensions.", DECISION_POLICY),
}

ALGORITHM_CAPABILITIES = {
    name: taxonomy.capability for name, taxonomy in ALGORITHM_TAXONOMY.items()
}


def algorithm_capability(algorithm: str) -> str:
    """Return the canonical output contract for a displayed algorithm."""
    return ALGORITHM_CAPABILITIES.get(algorithm, "")


PEAS_TABLE = [
    {
        "PEAS": "Performance",
        "Academic meaning": "Objective function used to judge the agent.",
        "15-puzzle instance": "Reach the goal state, minimize moves, expanded nodes, memory, and runtime.",
        "Exam emphasis": "Optimal solvers minimize path cost; efficient solvers reduce search effort.",
    },
    {
        "PEAS": "Environment",
        "Academic meaning": "World in which the agent acts.",
        "15-puzzle instance": "4x4 discrete, deterministic, fully observable, static, sequential, single-agent board.",
        "Exam emphasis": "CSP/game/uncertainty modes are explicit extensions, not the base environment.",
    },
    {
        "PEAS": "Actuators",
        "Academic meaning": "Actions the agent can execute.",
        "15-puzzle instance": "Slide the blank by applying L, R, U, or D when the move is legal.",
        "Exam emphasis": "Each legal action has unit cost in the standard solver model.",
    },
    {
        "PEAS": "Sensors",
        "Academic meaning": "Information available to the agent.",
        "15-puzzle instance": "Full board configuration, blank position, legal moves, and heuristic estimates.",
        "Exam emphasis": "No-observation and partial-observation demos deliberately weaken sensors.",
    },
]


RECOMMENDATION_RUBRIC = [
    {
        "Need": "Prove shortest path on shallow puzzle",
        "Use": "BFS or UCS",
        "Avoid": "DFS, Greedy, local search",
        "Reason": "Unit-cost breadth/cost expansion gives optimality, but memory is high.",
    },
    {
        "Need": "Best standard 15-puzzle solver demo",
        "Use": "A* with Manhattan or Linear Conflict",
        "Avoid": "Greedy as final answer",
        "Reason": "A* balances path cost g(n) and heuristic h(n) with optimality guarantees.",
    },
    {
        "Need": "Deeper puzzle with lower memory",
        "Use": "IDA*",
        "Avoid": "BFS/UCS",
        "Reason": "Iterative f-cost thresholds reduce memory pressure.",
    },
    {
        "Need": "Show heuristic failure modes",
        "Use": "Greedy or Hill Climbing presets",
        "Avoid": "Calling them reliable solvers",
        "Reason": "They expose suboptimal paths and local optima.",
    },
    {
        "Need": "Discuss PEAS extensions",
        "Use": "CSP, AND-OR, belief-state search, AI-vs-AI Tournament, Minimax, Expectimax",
        "Avoid": "Benchmarking them as natural solvers",
        "Reason": "They teach alternate agent models and environments.",
    },
    {
        "Need": "Compare two AI agents on the same puzzle",
        "Use": "AI-vs-AI Tournament with A* reference scoring",
        "Avoid": "Claiming standard 15-puzzle has a MIN player",
        "Reason": "The tournament is an evaluation layer; the 15-puzzle environment stays single-agent.",
    },
]


def taxonomy_rows() -> list[dict[str, str]]:
    """Return taxonomy data in dataframe-friendly shape."""
    return [
        {
            "Algorithm": name,
            "Role": ROLE_LABELS[item.role],
            "Environment": item.environment,
            "Capability": item.capability,
            "Guarantee": item.guarantee,
            "Exam note": item.exam_note,
        }
        for name, item in ALGORITHM_TAXONOMY.items()
    ]
