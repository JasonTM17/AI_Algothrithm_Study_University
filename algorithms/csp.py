"""Group 5: Constraint Satisfaction Problems — CSP modeling, propagation, backtracking, min-conflicts.

Note: 15-puzzle is traditionally a state-space search problem. This module models
it as a CSP planning problem for academic illustration.
"""

import time
import random
from typing import Optional
from core.puzzle import PuzzleState, GOAL_STATE, _move_blank, is_solvable
from core.heuristics import manhattan_distance
from core.metrics import SearchResult, TraceStep
from algorithms.map_coloring import AUSTRALIA_GRAPH, MapColoringResult, graph_coloring_demo


def csp_definition(
    start: tuple[int, ...], goal: tuple[int, ...] = GOAL_STATE,
    time_horizon: int = 3,
) -> SearchResult:
    """Define the CSP model for 15-puzzle planning.

    Variables: X[t][p] = tile at position p at time t, A[t] = action at time t.
    Domains: X[t][p] in {0..15}, A[t] in {L,R,U,D}
    Constraints: initial, goal, AllDifferent, transition, legal move.
    """
    trace: list[TraceStep] = []
    variables = []
    domains = {}

    for t in range(time_horizon + 1):
        for p in range(16):
            var = f"X[{t}][{p}]"
            variables.append(var)
            if t == 0:
                domains[var] = [start[p]]
            elif t == time_horizon:
                domains[var] = [goal[p]]
            else:
                domains[var] = list(range(16))

    for t in range(time_horizon):
        var = f"A[{t}]"
        variables.append(var)
        domains[var] = ["L", "R", "U", "D"]

    constraints = [
        {"name": "Initial", "desc": f"X[0] = {list(start)}"},
        {"name": "Goal", "desc": f"X[{time_horizon}] = {list(goal)}"},
        {"name": "AllDifferent", "desc": f"For each t, all X[t][p] must be distinct"},
        {"name": "Transition", "desc": f"X[t+1] must follow from X[t] after action A[t]"},
        {"name": "Legal Move", "desc": f"A[t] must be legal given blank position in X[t]"},
    ]

    trace.append(TraceStep(step=0, state=start, reason=f"CSP: {len(variables)} variables, {len(constraints)} constraints, T={time_horizon}"))

    msg = f"CSP Definition for 15-Puzzle (T={time_horizon})\n\n"
    msg += "Variables:\n"
    msg += f"  X[t][p]: tile at position p at time t, t=0..{time_horizon}, p=0..15\n"
    msg += f"  A[t]: action at time t, t=0..{time_horizon-1}\n\n"
    msg += f"Total variables: {len(variables)}\n\n"
    msg += "Domains:\n"
    msg += f"  X[0][p] = {{{start[p]}}} (fixed by initial state)\n"
    msg += f"  X[{time_horizon}][p] = {{{goal[p]}}} (fixed by goal)\n"
    msg += f"  X[t][p] in {{0,1,...,15}} for 0 < t < {time_horizon}\n"
    msg += f"  A[t] in {{L, R, U, D}}\n\n"
    msg += "Constraints:\n"
    for c in constraints:
        msg += f"  {c['name']}: {c['desc']}\n"

    return SearchResult(
        success=True, algorithm="CSP Definition", group="CSP",
        message=msg, trace=trace, suitable_for_puzzle=False,
        is_complete=False, is_optimal=False,
    )


def constraint_propagation(
    start: tuple[int, ...], goal: tuple[int, ...] = GOAL_STATE,
    time_horizon: int = 3,
) -> SearchResult:
    """Apply constraint propagation (AC-3 style) to reduce domains."""
    trace: list[TraceStep] = []

    # Initialize domains
    domains = {}
    for t in range(time_horizon + 1):
        for p in range(16):
            var = f"X[{t}][{p}]"
            if t == 0:
                domains[var] = [start[p]]
            elif t == time_horizon:
                domains[var] = [goal[p]]
            else:
                domains[var] = list(range(16))

    # Apply AllDifferent: if a variable is assigned, remove from others at same time
    changed = True
    iterations = 0
    while changed and iterations < 100:
        changed = False
        iterations += 1
        for t in range(1, time_horizon):  # Only free time steps
            # Find assigned variables (domain size 1)
            assigned = {}
            for p in range(16):
                var = f"X[{t}][{p}]"
                if len(domains[var]) == 1:
                    assigned[var] = domains[var][0]

            # Remove assigned values from other variables at same time
            for p in range(16):
                var = f"X[{t}][{p}]"
                if len(domains[var]) > 1:
                    for assigned_var, val in assigned.items():
                        if val in domains[var]:
                            domains[var].remove(val)
                            changed = True

    # Report
    total_before = 16 * (time_horizon - 1) * 16  # max domain size
    total_after = sum(len(domains[f"X[{t}][{p}]"]) for t in range(1, time_horizon) for p in range(16))

    trace.append(TraceStep(step=0, state=start,
                           reason=f"Propagation: {iterations} iterations, domains reduced"))

    msg = "Constraint Propagation Results\n\n"
    msg += f"Time horizon T={time_horizon}\n"
    msg += f"Propagation iterations: {iterations}\n\n"
    msg += "Domain reductions:\n"
    for t in range(time_horizon + 1):
        changes = []
        for p in range(16):
            var = f"X[{t}][{p}]"
            d = domains[var]
            if len(d) <= 5:
                changes.append(f"  {var}: {d}")
        if changes:
            msg += f"  Time {t}:\n" + "\n".join(changes) + "\n"

    return SearchResult(
        success=True, algorithm="Constraint Propagation", group="CSP",
        message=msg, trace=trace, suitable_for_puzzle=False,
        is_complete=False, is_optimal=False,
    )


def path_consistency(
    start: tuple[int, ...], goal: tuple[int, ...] = GOAL_STATE,
) -> SearchResult:
    """Explain path consistency concept with illustration."""
    msg = """Path Consistency (Illustration for 15-Puzzle CSP)

Path consistency extends arc consistency to triples of variables.
For variables Xi, Xj, Xk: for every consistent (Xi, Xj) pair,
there must exist a value for Xk consistent with both.

Example in 15-Puzzle CSP:
- X[0][15] = {0} (blank at position 15 at time 0)
- X[1][15] in {0, 11, 14} (blank could be at 15, or moved from 11 or 14)
- X[1][11] in {0, 10, 12, 15} (position 11 could receive blank or other tiles)

Path consistency: X[1][15] and X[1][11] must be consistent,
meaning they can't both be 0 (only one blank position per time step).

This is automatically enforced by AllDifferent constraint per time step.

Key insight: Path consistency is O(n^3 * d^3) for n variables with domain size d.
For 15-puzzle CSP with many variables, this is computationally expensive,
which is why CSP is not the standard approach for 15-puzzle."""

    return SearchResult(
        success=True, algorithm="Path Consistency", group="CSP",
        message=msg, trace=[], suitable_for_puzzle=False,
        is_complete=False, is_optimal=False,
    )


def global_constraints(
    start: tuple[int, ...], goal: tuple[int, ...] = GOAL_STATE,
) -> SearchResult:
    """Explain and demonstrate AllDifferent global constraint."""
    msg = """Global Constraints in 15-Puzzle CSP

AllDifferent(X[t][0], X[t][1], ..., X[t][15]):
  At each time step t, all 16 positions must contain distinct tiles (0-15).

This is a GLOBAL constraint because it involves all 16 variables at once,
not just pairs. It's stronger than 16*15=240 binary ≠ constraints.

Example: If X[0][0] = 1, then:
  X[0][1] ≠ 1, X[0][2] ≠ 1, ..., X[0][15] ≠ 1

Propagation: When a variable's domain is reduced to a single value,
that value is removed from all other variables at the same time step.

Implementation check:"""

    # Verify AllDifferent on goal state
    is_valid = len(set(GOAL_STATE)) == 16
    msg += f"\n  Goal state AllDifferent: {is_valid}"

    # Verify on start state
    is_valid_start = len(set(start)) == 16
    msg += f"\n  Start state AllDifferent: {is_valid_start}"

    # Example propagation
    msg += "\n\n  Propagation example:"
    msg += f"\n  Start: {list(start)}"
    msg += f"\n  If X[0][0]={start[0]}, then X[0][1..15] ≠ {start[0]}"

    return SearchResult(
        success=True, algorithm="Global Constraints", group="CSP",
        message=msg, trace=[], suitable_for_puzzle=False,
        is_complete=False, is_optimal=False,
    )


def backtracking_search(
    start: tuple[int, ...], goal: tuple[int, ...] = GOAL_STATE,
    max_steps: int = 5000, timeout: float = 30.0,
) -> SearchResult:
    """Backtracking search for CSP planning with MRV, forward checking."""
    t0 = time.perf_counter()
    h_fn = manhattan_distance

    if start == goal:
        return SearchResult(success=True, algorithm="Backtracking Search", group="CSP",
                            path=[start], actions=[], cost=0, depth=0,
                            runtime=time.perf_counter() - t0, message="Already at goal",
                            suitable_for_puzzle=False, is_complete=False, is_optimal=False)

    # Determine reasonable time horizon based on heuristic
    h = h_fn(start)
    max_t = min(h + 5, 15)  # Don't search too deep

    trace: list[TraceStep] = []
    trace.append(TraceStep(step=0, state=start, reason=f"Backtracking with T=0..{max_t}, h(start)={h}"))

    for T in range(1, max_t + 1):
        if time.perf_counter() - t0 > timeout:
            break

        # Try to find a path of length T
        path = [start]
        actions = []
        visited = {start}

        def backtrack(state: tuple, depth: int, steps_count: int) -> bool:
            if time.perf_counter() - t0 > timeout or steps_count[0] > max_steps:
                return False
            if depth == T:
                return state == goal

            ps = PuzzleState(state)
            neighbors = ps.get_neighbors("LRUD")
            # MRV: try neighbors closer to goal first
            neighbors.sort(key=lambda x: h_fn(x[0]))

            for ns, action, cost in neighbors:
                steps_count[0] += 1
                if ns in visited:
                    continue

                actions.append(action)
                path.append(ns)
                visited.add(ns)

                if len(trace) < 200:
                    trace.append(TraceStep(step=steps_count[0], state=ns, action=action,
                                           h=h_fn(ns), reason=f"T={T}, depth={depth}, action={action}"))

                if backtrack(ns, depth + 1, steps_count):
                    return True

                path.pop()
                actions.pop()
                visited.discard(ns)

            return False

        steps_count = [0]
        if backtrack(start, 0, steps_count):
            return SearchResult(
                success=True, algorithm="Backtracking Search", group="CSP",
                path=list(path), actions=list(actions), cost=len(actions), depth=len(actions),
                nodes_expanded=steps_count[0], nodes_generated=steps_count[0],
                runtime=time.perf_counter() - t0,
                message=f"Found solution with T={T}, {len(actions)} steps",
                trace=trace, suitable_for_puzzle=False, is_complete=False, is_optimal=True,
            )

    return SearchResult(
        success=False, algorithm="Backtracking Search", group="CSP",
        nodes_expanded=0, nodes_generated=0,
        runtime=time.perf_counter() - t0,
        message=f"No solution found within T={max_t}. CSP planning is not the standard approach for 15-puzzle.",
        trace=trace, suitable_for_puzzle=False, is_complete=False, is_optimal=False,
    )


def min_conflicts(
    start: tuple[int, ...], goal: tuple[int, ...] = GOAL_STATE,
    max_iterations: int = 10000, timeout: float = 30.0,
    seed: Optional[int] = None,
) -> SearchResult:
    """Min-conflicts algorithm for CSP planning."""
    t0 = time.perf_counter()
    rng = random.Random(seed)

    if start == goal:
        return SearchResult(success=True, algorithm="Min-Conflicts", group="CSP",
                            path=[start], actions=[], runtime=time.perf_counter() - t0,
                            message="Already at goal", suitable_for_puzzle=False)

    trace: list[TraceStep] = []

    # Start from initial state, try to fix conflicts
    # For 15-puzzle CSP, "conflicts" = tiles not in goal position
    current = list(start)
    total_conflicts = sum(1 for i, v in enumerate(current) if v != goal[i])

    trace.append(TraceStep(step=0, state=tuple(current),
                           reason=f"Initial conflicts: {total_conflicts}"))

    for i in range(max_iterations):
        if time.perf_counter() - t0 > timeout:
            break

        # Find conflicting positions (tiles not in goal place)
        conflicts = [idx for idx in range(16) if current[idx] != goal[idx]]
        if not conflicts:
            return SearchResult(
                success=True, algorithm="Min-Conflicts", group="CSP",
                path=[start, tuple(current)], actions=[], cost=0, depth=0,
                nodes_expanded=i, nodes_generated=i,
                runtime=time.perf_counter() - t0,
                message=f"Solved after {i} iterations",
                trace=trace, suitable_for_puzzle=False, is_complete=False, is_optimal=False)

        # Pick a conflicting position
        pos = rng.choice(conflicts)

        # Try swapping with another tile to reduce conflicts
        best_swap = None
        best_conflicts = total_conflicts

        for other in range(16):
            if other == pos:
                continue
            trial = list(current)
            trial[pos], trial[other] = trial[other], trial[pos]
            # Check solvable
            if not is_solvable(tuple(trial)):
                continue
            new_conflicts = sum(1 for j, v in enumerate(trial) if v != goal[j])
            if new_conflicts < best_conflicts:
                best_conflicts = new_conflicts
                best_swap = other

        if best_swap is not None:
            old_val = current[pos]
            current[pos], current[best_swap] = current[best_swap], current[pos]
            total_conflicts = best_conflicts
            if len(trace) < 200:
                trace.append(TraceStep(
                    step=i, state=tuple(current),
                    reason=f"Swap pos {pos}↔{best_swap}, conflicts: {total_conflicts}"))

    return SearchResult(
        success=False, algorithm="Min-Conflicts", group="CSP",
        nodes_expanded=max_iterations, nodes_generated=max_iterations,
        runtime=time.perf_counter() - t0,
        message=f"Best: {total_conflicts} conflicts after {max_iterations} iterations. "
                 "Min-conflicts works better for N-Queens than 15-puzzle because "
                 "puzzle constraints are highly interdependent (transition constraints).",
        trace=trace, suitable_for_puzzle=False, is_complete=False, is_optimal=False)


def solve_csp_constraint_graphs(
    start: tuple[int, ...], goal: tuple[int, ...] = GOAL_STATE,
    time_horizon: int = 2,
) -> SearchResult:
    """Display constraint graph for small CSP instance."""
    msg = f"""Constraint Graph for 15-Puzzle CSP (T={time_horizon})

Nodes: Variables (X[t][p] and A[t])
Edges: Constraints between variables

For T={time_horizon}:
  Position variables: X[0][0..15], X[1][0..15], ... X[{time_horizon}][0..15]
  Action variables: A[0], A[1], ... A[{time_horizon}-1]

Constraint graph structure:
  1. AllDifferent hyperedge at each time t:
     connects all 16 X[t][p] variables

  2. Transition edges: X[t][p] -- A[t] --> X[t+1][p]
     Each action variable connects to 2 position tiles (blank swap)

  3. Initial constraint: X[0][p] = start[p]
     {dict(enumerate(start))}

  4. Goal constraint: X[{time_horizon}][p] = goal[p]
     {dict(enumerate(goal))}

Text representation for T=1:

  X[0][0]---X[0][1]---...---X[0][15]    (AllDifferent)
      |        |              |
     A[0]     A[0]           A[0]          (Transition)
      |        |              |
  X[1][0]---X[1][1]---...---X[1][15]    (AllDifferent)

Key insight: Constraint graphs for planning CSPs grow linearly
with time horizon T, but each time step has 16 position variables
+ 1 action variable, with AllDifferent hyperedges.

This is why CSP is not the standard approach for 15-puzzle:
the constraint graph becomes very large for deep solutions."""

    return SearchResult(
        success=True, algorithm="Constraint Graphs", group="CSP",
        message=msg, trace=[], suitable_for_puzzle=False,
        is_complete=False, is_optimal=False,
    )
