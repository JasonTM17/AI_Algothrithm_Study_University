"""Structured within-group complexity comparison for the academic UI."""

from __future__ import annotations


def _row(
    group: str,
    algorithm: str,
    step_rule: str,
    time_complexity: str,
    space_complexity: str,
    steps_output: str,
    guarantee: str,
) -> dict[str, str]:
    return {
        "Group": group,
        "Algorithm": algorithm,
        "Step rule": step_rule,
        "Time": time_complexity,
        "Space": space_complexity,
        "Steps / output": steps_output,
        "Guarantee": guarantee,
    }


ALGORITHM_COMPARISON_ROWS = [
    _row("Uninformed Search", "BFS", "FIFO by depth", "O(b^d)", "O(b^d)", "Shortest depth d", "Complete; optimal for unit cost"),
    _row("Uninformed Search", "DFS", "LIFO plus best-depth reached map", "O(b^m)", "O(frontier + reached)", "Goal path or bounded search evidence", "Not optimal; sensitive to ordering and limits"),
    _row("Uninformed Search", "UCS", "Minimum g(n)", "O(b^(1+C*/eps))", "Same order as time", "Optimal cost C*", "Complete and optimal for positive costs"),
    _row("Uninformed Search", "IDS", "Repeated depth-limited DFS", "O(b^d)", "O(bd)", "Shortest depth d; repeats shallow nodes", "Complete; optimal for unit cost"),
    _row("Informed Search", "Greedy Best-First", "Minimum h(n)", "O(b^m) worst case", "O(b^m)", "Heuristic-selected path", "No completeness/optimality guarantee here"),
    _row("Informed Search", "A*", "Minimum f=g+h", "O(b^d) worst case", "O(b^d)", "Optimal depth/cost with valid h", "Complete and optimal with admissible consistent h"),
    _row("Informed Search", "IDA*", "Increasing f threshold", "O(b^d)", "O(bd)", "Optimal path; repeated thresholds", "Optimal with admissible h"),
    _row("Local Search", "Simple Hill Climbing", "First lower-h neighbor", "O(Ib)", "O(I) audit path", "At most I accepted moves", "May stop at local optimum"),
    _row("Local Search", "Steepest-Ascent Hill Climbing", "Best lower-h neighbor", "O(Ib)", "O(I) audit path", "At most I accepted moves", "May stop at local optimum"),
    _row("Local Search", "Stochastic Hill Climbing", "Random lower-h neighbor", "O(Ib)", "O(I) audit path", "Seeded accepted trajectory", "Probabilistic; not complete/optimal"),
    _row("Local Search", "Random-Restart Hill Climbing", "Legal random walk then hill climb", "O(RIb)", "O(I+walk)", "Best certified restart trajectory", "Probabilistic success only"),
    _row("Local Search", "Local Beam Search", "Keep k lowest-h states", "O(Ikb)", "O(kI) audited paths", "Best beam trajectory", "Beam can discard a solution branch"),
    _row("Local Search", "Simulated Annealing", "Accept by exp(-delta/T)", "O(I)", "O(I) audit path", "Seeded accepted trajectory", "Schedule-dependent; no finite guarantee"),
    _row("Complex Environments", "AND-OR Search", "OR chooses; AND covers all outcomes", "O((bo)^d)", "O((bo)^d)", "Conditional plan", "Bounded nondeterministic model"),
    _row("Complex Environments", "Searching with no observation", "Graph search over Predict(B,a)", "O(|belief graph| x |A| x |B|)", "O(frontier + reached beliefs)", "Conformant action sequence", "Every initial belief state must reach goal"),
    _row("Complex Environments", "Searching for partially observable problems", "OR action; AND observation partitions", "Exponential in policy depth", "O(policy tree + beliefs)", "Contingent observation policy", "Every observation branch needs a subpolicy"),
    _row("CSP", "Backtracking", "Chronological state-chain assignment", "O(D^T)", "O(T + domains)", "Exact-T legal path or bounded failure", "No shortest-path claim from one horizon"),
    _row("CSP", "Backtracking + Forward Checking", "Assign then prune unsupported next values", "O(D^T) worst case", "O(TD)", "Exact-T legal path or domain wipe-out", "No more assignments than Backtracking under same ordering"),
    _row("CSP", "AC-3", "REVISE directed state-chain arcs", "O(ED^3)", "O(VD+E)", "Arc consistency; replay only if exact path", "Arc consistency alone is not a solution"),
    _row("CSP", "Min-Conflicts", "Repair a conflicted state variable", "O(ITD)", "O(TD)", "Exact path or repair evidence", "Seeded local repair; not complete or optimal"),
    _row("AI-vs-AI Tournament", "AI-vs-AI Tournament", "A* oracle then two solver runs", "O(R(ref+A+B))", "Sum of three runs", "Shared replay max(|path A|, |path B|)", "Valid only with proven reference"),
    _row("AI-vs-AI Tournament", "Minimax", "MAX then worst-case MIN branch", "O(b^m)", "O(bm)", "Principal variation length <= m", "Worst-case robustness extension"),
    _row("AI-vs-AI Tournament", "Alpha-Beta Pruning", "Worst-case tree with alpha/beta cutoffs", "Worst O(b^m), best O(b^(m/2))", "O(bm)", "Same root choice when fully searched", "Preserves Minimax value under assumptions"),
    _row("AI-vs-AI Tournament", "Expectimax", "MAX plus probability-weighted CHANCE", "O((bo)^m)", "O(bom)", "Seeded sample path length <= m", "Expected utility under stated probabilities"),
]


def comparison_rows_for_group(group: str) -> list[dict[str, str]]:
    """Return all comparison rows for one displayed algorithm group."""
    return [row for row in ALGORITHM_COMPARISON_ROWS if row["Group"] == group]


GROUP6_ROBUSTNESS_COMPARISON_ROWS = [
    {
        "Dimension": "MIN / chance assumption",
        "Minimax": "Worst-case MIN branch",
        "Alpha-Beta": "Worst-case MIN branch",
        "Expectimax": "No MIN; CHANCE outcomes",
    },
    {
        "Dimension": "Mechanism",
        "Minimax": "Evaluate the full depth-limited tree",
        "Alpha-Beta": "Prune branches that cannot affect the root value",
        "Expectimax": "Compute probability-weighted expected value",
    },
    {
        "Dimension": "Root result",
        "Minimax": "Worst-case value at depth m",
        "Alpha-Beta": "Same as Minimax when fully searched",
        "Expectimax": "Expected value, often different from Minimax",
    },
    {
        "Dimension": "Node visited",
        "Minimax": "O(b^m)",
        "Alpha-Beta": "Best O(b^(m/2)), worst O(b^m)",
        "Expectimax": "O(b^m) or more with outcome branching",
    },
    {
        "Dimension": "Can prune?",
        "Minimax": "No",
        "Alpha-Beta": "Yes",
        "Expectimax": "No; all outcomes affect expectation",
    },
    {
        "Dimension": "Best fit",
        "Minimax": "Two-player games / robustness analysis",
        "Alpha-Beta": "Two-player games with searchable bounds",
        "Expectimax": "MDP-style stochastic decisions",
    },
]


def group6_robustness_comparison_rows() -> list[dict[str, str]]:
    """Return the dedicated Minimax / Alpha-Beta / Expectimax comparison."""
    return GROUP6_ROBUSTNESS_COMPARISON_ROWS
