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
    _row("Uninformed Search", "DFS", "LIFO / deepest first", "O(b^m)", "O(bm)", "At most depth limit m", "Not optimal; bounded implementation"),
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
    _row("Complex Environments", "Searching with no observation", "Minimize average belief h", "O(SAB)", "O(B)", "Action sequence over belief", "Model evidence, not standard optimal path"),
    _row("Complex Environments", "Searching for partially observable problems", "Belief action + observation filter", "O(SAB)", "O(B)", "Actual path plus observations", "Sensor-model demonstration"),
    _row("Complex Environments", "LRTA*", "Min c+H then update H", "O(Sb)", "O(V+S) audit path", "Online trajectory up to S", "Can revisit; not optimal"),
    _row("CSP", "CSP Definition", "Construct X[t][p], A[t], constraints", "O(Tn)", "O(TnD)", "Model only", "No solving guarantee"),
    _row("CSP", "Constraint Propagation", "AC-3 revise adjacent state domains", "O(ED^3)", "O(VD+E)", "Exact-T path or domain wipe-out", "Complete for the bounded chain CSP"),
    _row("CSP", "Path Consistency", "Check variable triples", "O(V^3D^3)", "O(V^2D^2)", "Consistency evidence", "Too expensive for deep planning CSP"),
    _row("CSP", "Global Constraints", "AllDifferent propagation", "Propagator-dependent", "O(VD)", "Domain filtering", "Modeling aid"),
    _row("CSP", "Backtracking Search", "Depth-first ordering by Manhattan Distance", "O(b^T)", "O(T)", "Legal path within horizon", "Incomplete under horizon/resource bounds"),
    _row("CSP", "Min-Conflicts", "Repair a conflicting position", "O(I n)", "O(n)", "Assignment repair, not blank-move path", "Not a legal 15-puzzle planner"),
    _row("CSP", "Constraint Graphs", "Build variable/constraint edges", "O(V+E)", "O(V+E)", "Graph artifact", "Analysis only"),
    _row("AI-vs-AI Tournament", "AI-vs-AI Tournament", "A* oracle then two solver runs", "O(R(ref+A+B))", "Sum of three runs", "Shared replay max(|path A|, |path B|)", "Valid only with proven reference"),
    _row("AI-vs-AI Tournament", "Minimax", "Alternate MAX/MIN", "O(b^m)", "O(bm)", "Principal variation length <= m", "Artificial adversarial extension"),
    _row("AI-vs-AI Tournament", "Alpha-Beta Pruning", "Minimax with alpha/beta cutoffs", "Worst O(b^m), best O(b^(m/2))", "O(bm)", "Same root choice when fully searched", "Preserves Minimax value under assumptions"),
    _row("AI-vs-AI Tournament", "Expectimax", "MAX plus probability-weighted CHANCE", "O((bo)^m)", "O(bom)", "Seeded sample path length <= m", "Expected utility under stated probabilities"),
]


def comparison_rows_for_group(group: str) -> list[dict[str, str]]:
    """Return all comparison rows for one displayed algorithm group."""
    return [row for row in ALGORITHM_COMPARISON_ROWS if row["Group"] == group]
