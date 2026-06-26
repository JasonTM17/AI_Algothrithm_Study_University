"""Proof cards, exam templates, and benchmark methodology data."""

from __future__ import annotations

from core.puzzle import GOAL_STATE, scramble


def _benchmark_preset(
    *,
    depth: int,
    seed: int,
    max_nodes: int,
    timeout: int,
    heuristic: str,
    comparison_goal: str,
    recommended_algorithms: tuple[str, ...],
    caveat: str,
    expected_outcome: str,
    goal_state: tuple[int, ...] = GOAL_STATE,
    action_order: str = "LRUD",
) -> dict[str, object]:
    """Build a deterministic, bounded benchmark case with explicit start/goal."""
    return {
        "depth": depth,
        "seed": seed,
        "start_state": scramble(goal=goal_state, depth=depth, seed=seed),
        "goal_state": goal_state,
        "max_nodes": max_nodes,
        "timeout": timeout,
        "heuristic": heuristic,
        "action_order": action_order,
        "comparison_goal": comparison_goal,
        "recommended_algorithms": recommended_algorithms,
        "recommended_groups": tuple(
            group
            for group, algorithms in {
                "Uninformed Search": ("BFS", "DFS", "UCS", "IDS"),
                "Informed Search": ("Greedy Best-First", "A*", "IDA*"),
                "Local Search": (
                    "Simple Hill Climbing",
                    "Steepest-Ascent Hill Climbing",
                    "Stochastic Hill Climbing",
                    "Random-Restart Hill Climbing",
                    "Local Beam Search",
                    "Simulated Annealing",
                ),
            }.items()
            if any(algorithm in recommended_algorithms for algorithm in algorithms)
        ),
        "caveat": caveat,
        "expected_outcome": expected_outcome,
    }


PROOF_CARDS = {
    "BFS/UCS optimality": {
        "claim": "BFS and UCS return shortest paths on the standard 15-puzzle.",
        "reason": "Every legal slide has unit cost. BFS expands by depth; UCS expands by path cost g(n). With unit costs, both expand all cheaper paths before any more expensive path.",
        "exam_use": "Use this to justify optimality for shallow deterministic puzzles.",
    },
    "Manhattan admissible": {
        "claim": "Manhattan Distance never overestimates the true remaining cost.",
        "reason": "A tile must move at least its row distance plus column distance to reach its goal position. Other tiles can only add constraints, not reduce this minimum.",
        "exam_use": "Use this to justify A* optimality with Manhattan Distance.",
    },
    "Manhattan consistent": {
        "claim": "Manhattan Distance is consistent for unit-cost sliding moves.",
        "reason": "One slide changes the Manhattan sum by at most 1, so h(n) <= 1 + h(n') for every neighbor n'.",
        "exam_use": "Use this to explain why A* graph search does not need to reopen settled states under this heuristic.",
    },
    "Linear Conflict admissible": {
        "claim": "Linear Conflict remains admissible when added to Manhattan Distance.",
        "reason": "Two conflicting tiles in the same goal row or column cannot both reach goal without at least one tile moving out and back, adding a necessary cost of 2.",
        "exam_use": "Use this to explain why Linear Conflict is stronger than Manhattan while preserving optimality.",
    },
    "Solvability parity": {
        "claim": "Only half of 15-puzzle permutations are solvable.",
        "reason": "For a 4x4 puzzle, solvability depends on inversion parity plus the blank row counted from the bottom. Legal moves preserve the required parity class.",
        "exam_use": "Use this to justify rejecting impossible manual inputs before running search.",
    },
    "Greedy/Hill Climbing failure": {
        "claim": "Greedy and Hill Climbing can fail or return suboptimal paths.",
        "reason": "They optimize h(n) locally and do not account for full path cost or future traps. Local minima, plateaus, and misleading heuristics can stop progress.",
        "exam_use": "Use teaching presets to demonstrate suboptimality and local-optimum behavior.",
    },
}


EXAM_ANSWER_TEMPLATES = {
    "Uninformed Search": {
        "goal": "Explore state space without heuristic knowledge.",
        "frontier": "Queue for BFS, stack/depth limit for DFS/IDS, priority queue by g(n) for UCS.",
        "evaluation": "No h(n); priority is depth or path cost.",
        "guarantee": "BFS/UCS/IDS are complete and optimal under unit cost; DFS is not optimal.",
        "when_to_use": "Use for shallow puzzles or proving search properties.",
        "when_not_to_use": "Avoid for deep 15-puzzle instances due to memory/time growth.",
    },
    "Informed Search": {
        "goal": "Use heuristic estimates to guide search toward the goal.",
        "frontier": "Priority queue ordered by h(n) for Greedy or f(n)=g(n)+h(n) for A*.",
        "evaluation": "A* uses g+h; IDA* uses increasing f-cost thresholds.",
        "guarantee": "A*/IDA* are optimal with admissible, consistent heuristics.",
        "when_to_use": "Use as the primary real solver demonstration.",
        "when_not_to_use": "Avoid Greedy as a final optimal solver because it ignores g(n).",
    },
    "Local Search": {
        "goal": "Improve a single or small set of states according to heuristic value.",
        "frontier": "No full frontier; keeps current state, restarts, or beam states.",
        "evaluation": "Usually minimizes h(n) or accepts probabilistic moves.",
        "guarantee": "No finite completeness or optimality guarantee for this app.",
        "when_to_use": "Use to demonstrate local optima, plateaus, and stochastic escape.",
        "when_not_to_use": "Do not present it as a reliable 15-puzzle solver.",
    },
    "Complex Environments": {
        "goal": "Explain search under nondeterminism, limited sensors, or online learning.",
        "frontier": "Conditional plans, belief states, or learned heuristic table.",
        "evaluation": "Uses h(n), belief filtering, or LRTA* heuristic updates.",
        "guarantee": "Educational extension, not a natural standard solver.",
        "when_to_use": "Use for PEAS/environment discussion; AND-OR appears in Run as Group 3 alias for the syllabus.",
        "when_not_to_use": "Do not compare as if the environment matches standard 15-puzzle.",
    },
    "CSP": {
        "goal": "Model planning as variables, domains, and constraints.",
        "frontier": "Assignments, domains, and constraint graph rather than ordinary states.",
        "evaluation": "MRV, propagation, conflicts, and consistency checks.",
        "guarantee": "Illustrative in this app; bounded horizon/limits restrict completeness.",
        "when_to_use": "Use to show alternative AI problem formulation.",
        "when_not_to_use": "Do not claim it is the standard 15-puzzle approach.",
    },
    "AI-vs-AI Tournament": {
        "goal": "Compare two AI solver agents on identical 15-puzzle rounds.",
        "frontier": "Each agent uses its own solver frontier; tournament logic only scores outputs.",
        "evaluation": "A* reference cost, path legality, goal reachability, excess cost, runtime, and nodes.",
        "guarantee": "Scoring is valid only when the A* reference proves optimal cost for the round.",
        "when_to_use": "Use to show optimal, suboptimal, failed, and illegal solver behavior side by side.",
        "when_not_to_use": "Do not describe it as a natural adversarial PEAS model with a MIN player.",
    },
}


BENCHMARK_PRESETS = {
    "Shallow proof case": _benchmark_preset(
        depth=6,
        seed=7,
        max_nodes=5000,
        timeout=10,
        heuristic="Manhattan Distance",
        comparison_goal="Prove shortest-path behavior on a tiny deterministic start/goal pair.",
        recommended_algorithms=("BFS", "UCS", "IDS", "A*"),
        caveat="Good for BFS/UCS/IDS/A* optimality comparison with low resource limits.",
        expected_outcome="All recommended solvers reach the preset goal and prove optimality.",
    ),
    "Medium heuristic case": _benchmark_preset(
        depth=10,
        seed=42,
        max_nodes=10000,
        timeout=15,
        heuristic="Linear Conflict",
        comparison_goal="Compare uninformed expansion cost against heuristic guidance.",
        recommended_algorithms=("BFS", "UCS", "IDS", "Greedy Best-First", "A*", "IDA*"),
        caveat="Good for showing informed search efficiency while every recommended solver still finishes.",
        expected_outcome="All recommended solvers reach the preset goal; informed search expands far fewer nodes.",
    ),
    "Heuristic failure case": _benchmark_preset(
        depth=15,
        seed=1,
        max_nodes=12000,
        timeout=15,
        heuristic="Manhattan Distance",
        comparison_goal="Show that Greedy can find a longer path than A* on the same start/goal pair.",
        recommended_algorithms=("Greedy Best-First", "A*", "IDA*"),
        caveat="Greedy can be suboptimal while A* and IDA* remain optimal with the admissible heuristic.",
        expected_outcome="Greedy reaches the goal with more moves; A* and IDA* prove the shorter path.",
    ),
    "Memory pressure case": _benchmark_preset(
        depth=12,
        seed=18,
        max_nodes=20000,
        timeout=15,
        heuristic="Linear Conflict",
        comparison_goal="Show memory-growth pressure without forcing a timeout or resource failure.",
        recommended_algorithms=("BFS", "UCS", "A*", "IDA*"),
        caveat="Use to discuss why BFS/UCS expand much more than A*/IDA* even when the case still finishes.",
        expected_outcome="All recommended solvers reach the goal; BFS/UCS report much larger reached/frontier sizes.",
    ),
}


DECISION_GUIDE = [
    {"Question": "Need a real optimal solver?", "Use": "A* or IDA*", "Why": "They use g(n)+h(n) and preserve optimality with admissible heuristics."},
    {"Question": "Need a shallow proof of optimality?", "Use": "BFS/UCS/IDS", "Why": "They expose complete/optimal uninformed search behavior under unit cost."},
    {"Question": "Need to show heuristic failure?", "Use": "Greedy or Hill Climbing", "Why": "They visibly fail when local or heuristic-only choices mislead the search."},
    {"Question": "Need to compare two AI agents?", "Use": "AI-vs-AI Tournament", "Why": "It scores both agents against the same A* optimal reference without changing PEAS."},
    {"Question": "Need to explain PEAS variations?", "Use": "CSP/Complex/Game demos", "Why": "They change problem formulation or environment assumptions for teaching."},
]
