"""Academic presentation data for the 15-puzzle AI simulator."""

from __future__ import annotations

from dataclasses import dataclass


REAL_SOLVER = "real_solver"
CONTRAST_DEMO = "contrast_demo"
ILLUSTRATIVE_EXTENSION = "illustrative_extension"
STOCHASTIC_GAME_DEMO = "stochastic_game_demo"

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


ALGORITHM_TAXONOMY: dict[str, AlgorithmTaxonomy] = {
    "BFS": AlgorithmTaxonomy(REAL_SOLVER, "deterministic", "Complete, optimal with unit step cost.", "Good for proving optimality, but memory grows exponentially."),
    "DFS": AlgorithmTaxonomy(CONTRAST_DEMO, "deterministic", "Not optimal; complete only with strict depth/visited limits.", "Use to contrast low memory against poor solution guarantees."),
    "UCS": AlgorithmTaxonomy(REAL_SOLVER, "deterministic", "Complete and optimal for positive costs.", "Equivalent to BFS in 15-puzzle because each move costs 1."),
    "IDS": AlgorithmTaxonomy(REAL_SOLVER, "deterministic", "Complete and optimal with unit step cost.", "Best uninformed teaching choice when memory matters."),
    "Greedy Best-First": AlgorithmTaxonomy(CONTRAST_DEMO, "deterministic", "Not complete or optimal in graph search practice.", "Fast heuristic-only baseline; compare against A* to show suboptimality."),
    "A*": AlgorithmTaxonomy(REAL_SOLVER, "deterministic", "Complete and optimal with admissible, consistent heuristic.", "Primary reference solver for final-exam explanation."),
    "IDA*": AlgorithmTaxonomy(REAL_SOLVER, "deterministic", "Optimal with admissible heuristic and bounded branching.", "A* quality with much lower memory, useful for deeper puzzles."),
    "Simple Hill Climbing": AlgorithmTaxonomy(CONTRAST_DEMO, "deterministic", "Not complete or optimal.", "Shows local optimum failure clearly."),
    "Steepest-Ascent Hill Climbing": AlgorithmTaxonomy(CONTRAST_DEMO, "deterministic", "Not complete or optimal.", "Shows best-neighbor choice still cannot guarantee solution."),
    "Stochastic Hill Climbing": AlgorithmTaxonomy(CONTRAST_DEMO, "deterministic", "Not complete or optimal.", "Adds randomness but still may get stuck."),
    "Random-Restart Hill Climbing": AlgorithmTaxonomy(CONTRAST_DEMO, "deterministic", "Not optimal; probabilistic success only.", "Useful for explaining restarts, not a reliable 15-puzzle solver."),
    "Local Beam Search": AlgorithmTaxonomy(CONTRAST_DEMO, "deterministic", "Not complete or optimal.", "Shows multiple-state local search as a stronger contrast case."),
    "Simulated Annealing": AlgorithmTaxonomy(CONTRAST_DEMO, "deterministic", "No finite optimality guarantee.", "Good for explaining escape from local minima through temperature."),
    "AND-OR Search": AlgorithmTaxonomy(ILLUSTRATIVE_EXTENSION, "nondeterministic", "Returns conditional plans in an extended model.", "Not natural for standard deterministic 15-puzzle."),
    "No Observation Search": AlgorithmTaxonomy(ILLUSTRATIVE_EXTENSION, "no_observation", "Belief-state demo, not a practical standard solver.", "Use only to explain sensor limitations."),
    "Searching with no observation": AlgorithmTaxonomy(ILLUSTRATIVE_EXTENSION, "no_observation", "Belief-state demo, not a practical standard solver.", "Use only to explain sensor limitations."),
    "Partially Observable Search": AlgorithmTaxonomy(ILLUSTRATIVE_EXTENSION, "partial_observable", "Belief update demo, not a natural solver.", "Shows how partial sensors change the state representation."),
    "Searching for partially observable problems": AlgorithmTaxonomy(ILLUSTRATIVE_EXTENSION, "partial_observable", "Belief update demo, not a natural solver.", "Shows how partial sensors change the state representation."),
    "LRTA*": AlgorithmTaxonomy(ILLUSTRATIVE_EXTENSION, "online", "Online learning demo; path may be non-optimal.", "Good for agent-learning discussion, not benchmark solving."),
    "CSP Definition": AlgorithmTaxonomy(ILLUSTRATIVE_EXTENSION, "planning_csp", "Modeling aid, not a search guarantee.", "Use to show X, D, C formulation."),
    "Constraint Propagation": AlgorithmTaxonomy(ILLUSTRATIVE_EXTENSION, "planning_csp", "Pruning aid, not a solver alone.", "Explain AC-style domain reduction."),
    "Path Consistency": AlgorithmTaxonomy(ILLUSTRATIVE_EXTENSION, "planning_csp", "Consistency concept, not a natural solver.", "Useful for comparing arc/path/global consistency."),
    "Global Constraints": AlgorithmTaxonomy(ILLUSTRATIVE_EXTENSION, "planning_csp", "Constraint modeling concept.", "AllDifferent is valid but CSP planning is large."),
    "Backtracking Search": AlgorithmTaxonomy(ILLUSTRATIVE_EXTENSION, "planning_csp", "Not complete under bounded horizon/limits.", "Bounded transition-planning illustration ordered by Manhattan Distance heuristic; it does not implement MRV/forward checking."),
    "Min-Conflicts": AlgorithmTaxonomy(ILLUSTRATIVE_EXTENSION, "planning_csp", "Not complete or optimal here.", "Better for N-Queens than transition-heavy 15-puzzle."),
    "Constraint Graphs": AlgorithmTaxonomy(ILLUSTRATIVE_EXTENSION, "planning_csp", "Analysis artifact.", "Use to visualize why CSP planning grows quickly."),
    "AI-vs-AI Tournament": AlgorithmTaxonomy(STOCHASTIC_GAME_DEMO, "scored_competition", "Scores two solver agents against an A* reference.", "Use to compare AI outputs without claiming 15-puzzle has an opponent."),
    "Minimax": AlgorithmTaxonomy(STOCHASTIC_GAME_DEMO, "adversarial_extension", "Game-tree utility demo, not a standard solver.", "15-puzzle has no opponent; MAX/MIN is an educational extension."),
    "Alpha-Beta Pruning": AlgorithmTaxonomy(STOCHASTIC_GAME_DEMO, "adversarial_extension", "Same minimax value with pruning when model applies.", "Use to explain pruning, not puzzle optimality."),
    "Expectimax": AlgorithmTaxonomy(STOCHASTIC_GAME_DEMO, "stochastic", "Expected-utility demo under chance outcomes.", "Use only for stochastic action extensions."),
}


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
        "Use": "CSP, AND-OR, LRTA*, AI-vs-AI Tournament, Minimax, Expectimax",
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
            "Guarantee": item.guarantee,
            "Exam note": item.exam_note,
        }
        for name, item in ALGORITHM_TAXONOMY.items()
    ]
