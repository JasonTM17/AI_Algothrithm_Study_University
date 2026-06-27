"""Group 5: Constraint Satisfaction Problems — CSP modeling, propagation, backtracking, min-conflicts.

Note: 15-puzzle is traditionally a state-space search problem. This module models
it as a CSP planning problem for academic illustration.
"""

import time
import random
from typing import Optional
from algorithms.csp_ac3 import run_state_chain_ac3
from core.puzzle import PuzzleState, GOAL_STATE, _move_blank, is_solvable
from core.heuristics import get_heuristic
from core.metrics import SearchResult, TraceStep
from core.randomness import active_action_order


TRACE_LIMIT = 200


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
        goal_state=goal,
        message=msg, trace=trace, suitable_for_puzzle=False,
        is_complete=False, is_optimal=False,
    )


def constraint_propagation(
    start: tuple[int, ...], goal: tuple[int, ...] = GOAL_STATE,
    time_horizon: int = 3,
) -> SearchResult:
    """Run AC-3 on a bounded chain of full 15-puzzle state variables."""
    action_order = active_action_order()
    ac3 = run_state_chain_ac3(
        start,
        goal,
        time_horizon=time_horizon,
        action_order=action_order,
    )
    trace = [
        TraceStep(
            step=time_index,
            state=next(iter(domain)) if domain else start,
            belief_size=len(domain),
            event="revise",
            reason=f"AC-3 domain S[{time_index}] has {len(domain)} state(s)",
        )
        for time_index, domain in enumerate(ac3.domains)
    ]

    domain_sizes = ", ".join(
        f"|D(S[{index}])|={len(domain)}"
        for index, domain in enumerate(ac3.domains)
    )
    status = (
        "Arc-consistent state chain found."
        if ac3.consistent
        else "Domain wipe-out: no exact-horizon legal path exists."
    )
    msg = (
        f"AC-3 State-Chain CSP for 15-Puzzle (T={time_horizon})\n\n"
        "Variables: S[0]..S[T], where each value is a complete legal puzzle state.\n"
        "Binary constraint: consecutive values must differ by exactly one legal blank move.\n"
        "Endpoints: S[0]=start and S[T]=goal.\n"
        "This compact executable model is separate from the full X[t][p] teaching encoding.\n\n"
        f"{status}\n"
        f"Candidate states: {ac3.candidate_states}\n"
        f"Arc checks: {ac3.arc_checks}\n"
        f"Revisions: {ac3.revisions}\n"
        f"Values removed: {ac3.values_removed}\n"
        f"Final domains: {domain_sizes}\n"
        f"Action order: {action_order}\n"
    )

    return SearchResult(
        success=ac3.consistent,
        algorithm="Constraint Propagation",
        group="CSP",
        path=ac3.path,
        actions=ac3.actions,
        goal_state=goal,
        cost=len(ac3.actions),
        depth=len(ac3.actions),
        nodes_expanded=ac3.arc_checks,
        nodes_generated=ac3.candidate_states,
        reached_size=sum(len(domain) for domain in ac3.domains),
        message=msg,
        trace=trace,
        suitable_for_puzzle=False,
        is_complete=False,
        is_optimal=False,
    )


def path_consistency(
    start: tuple[int, ...], goal: tuple[int, ...] = GOAL_STATE,
) -> SearchResult:
    """Explain path consistency concept with illustration."""
    msg = """Path Consistency (Illustration for 15-Puzzle CSP)

Path consistency extends arc consistency to triples of variables.
For variables Xi, Xj, Xk, every allowed (Xi, Xj) pair must have a
supporting value of Xk that satisfies both connecting constraints.

For state-chain variables S[t], consider S[0]=start and S[2]=goal.
An allowed endpoint pair needs an intermediate state S[1] that is one
legal blank move from S[0] and one legal blank move from S[2]. If no
such support exists, the pair is path-inconsistent for that horizon.

This function explains the consistency concept; it does not execute a
path-consistency solver or claim a shortest 15-puzzle path.

Key insight: a direct path-consistency procedure can require
O(n^3 * d^3) work for n variables with domain size d. For a planning
CSP whose domain values are complete puzzle states, that cost is large,
which is why graph search is the standard 15-puzzle formulation."""

    return SearchResult(
        success=True, algorithm="Path Consistency", group="CSP",
        goal_state=goal,
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

This is a GLOBAL constraint because it involves all 16 variables at once.
A binary decomposition has 120 undirected pairwise inequalities, or
240 directed arcs when represented for an AC-3 queue. A dedicated
AllDifferent propagator can infer more than treating those arcs independently.

Example: If X[0][0] = 1, then:
  X[0][1] ≠ 1, X[0][2] ≠ 1, ..., X[0][15] ≠ 1

Propagation: When a variable's domain is reduced to a single value,
that value is removed from all other variables at the same time step.

Implementation check:"""

    # Verify AllDifferent on goal state
    is_valid = len(set(goal)) == 16
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
        goal_state=goal,
        message=msg, trace=[], suitable_for_puzzle=False,
        is_complete=False, is_optimal=False,
    )


def backtracking_search(
    start: tuple[int, ...], goal: tuple[int, ...] = GOAL_STATE,
    max_steps: int = 5000, timeout: float = 30.0,
) -> SearchResult:
    """Illustrate bounded transition-CSP planning with depth-first backtracking.

    The state representation is not an explicit variable/domain CSP, so this
    demo uses heuristic value ordering rather than claiming MRV or forward
    checking. It remains an educational formulation, not the standard solver path.
    """
    t0 = time.perf_counter()
    h_fn = get_heuristic("Manhattan Distance", goal)

    if start == goal:
        return SearchResult(success=True, algorithm="Backtracking Search", group="CSP",
                            path=[start], actions=[], goal_state=goal, cost=0, depth=0,
                            runtime=time.perf_counter() - t0, message="Already at goal",
                            suitable_for_puzzle=False, is_complete=False, is_optimal=False)

    # Determine reasonable time horizon based on heuristic
    h = h_fn(start)
    max_t = min(h + 5, 15)  # Don't search too deep

    trace: list[TraceStep] = []
    trace.append(TraceStep(
        step=0, state=start,
        reason=f"Bounded transition planning: T=1..{max_t}, heuristic value ordering, h(start)={h}",
    ))
    total_steps = 0
    total_generated = 1

    for T in range(1, max_t + 1):
        if time.perf_counter() - t0 > timeout:
            break

        # Try to find a path of length T
        path = [start]
        actions = []
        visited = {start}

        def backtrack(state: tuple, depth: int, steps_count: list[int]) -> bool:
            nonlocal total_generated
            if time.perf_counter() - t0 > timeout or steps_count[0] > max_steps:
                return False
            if depth == T:
                return state == goal

            ps = PuzzleState(state)
            neighbors = ps.get_neighbors(active_action_order())
            # Heuristic value ordering: try neighbors closer to goal first.
            neighbors.sort(key=lambda x: h_fn(x[0]))
            total_generated += len(neighbors)

            for ns, action, cost in neighbors:
                steps_count[0] += 1
                is_ancestor = ns in visited
                if len(trace) < TRACE_LIMIT and not is_ancestor:
                    nh = h_fn(ns)
                    trace.append(TraceStep(
                        step=steps_count[0],
                        state=ns,
                        action=action,
                        g=depth + 1,
                        h=nh,
                        f=nh,
                        depth=depth + 1,
                        node_state=state,
                        frontier_size=sum(1 for child, _, _ in neighbors if child not in visited),
                        frontier_states=[child for child, _, _ in neighbors if child not in visited],
                        event="generate",
                        reason=(
                            f"T={T}, depth={depth}, generated child action={action}, "
                            f"Manhattan h={nh:.1f}"
                        ),
                    ))
                if is_ancestor:
                    continue

                actions.append(action)
                path.append(ns)
                visited.add(ns)

                if backtrack(ns, depth + 1, steps_count):
                    return True

                path.pop()
                actions.pop()
                visited.discard(ns)

            return False

        steps_count = [0]
        solved = backtrack(start, 0, steps_count)
        total_steps += steps_count[0]
        if solved:
            return SearchResult(
                success=True, algorithm="Backtracking Search", group="CSP",
                path=list(path), actions=list(actions), goal_state=goal,
                cost=len(actions), depth=len(actions),
                nodes_expanded=total_steps, nodes_generated=total_generated,
                runtime=time.perf_counter() - t0,
                message=(f"Bounded transition-planning demo found a path with T={T}. "
                         "This run orders child nodes by Manhattan Distance heuristic, not MRV/forward checking."),
                trace=trace, suitable_for_puzzle=False, is_complete=False, is_optimal=False,
            )

    return SearchResult(
        success=False, algorithm="Backtracking Search", group="CSP",
        goal_state=goal,
        nodes_expanded=total_steps, nodes_generated=total_generated,
        runtime=time.perf_counter() - t0,
        message=(f"No path found within bounded horizon T={max_t}. This is not a proof of "
                 "unsolvability; graph search is the standard 15-puzzle formulation."),
        trace=trace, suitable_for_puzzle=False, is_complete=False, is_optimal=False,
    )


def min_conflicts(
    start: tuple[int, ...], goal: tuple[int, ...] = GOAL_STATE,
    max_iterations: int = 10000, timeout: float = 30.0,
    seed: Optional[int] = None,
) -> SearchResult:
    """Tile-placement min-conflicts concept demo, not a legal move planner."""
    t0 = time.perf_counter()
    rng = random.Random(seed)

    if start == goal:
        return SearchResult(success=True, algorithm="Min-Conflicts", group="CSP",
                            path=[start], actions=[], goal_state=goal,
                            random_seed=seed,
                            runtime=time.perf_counter() - t0,
                            message="Already at goal", uses_randomness=True,
                            suitable_for_puzzle=False)

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
                path=[], actions=[], goal_state=goal, cost=0, depth=0,
                random_seed=seed,
                nodes_expanded=i, nodes_generated=i,
                runtime=time.perf_counter() - t0,
                message=(f"Goal reached after {i} iterations via tile swaps. "
                         "This is a CSP repair trace, NOT a sequence of legal 15-puzzle moves."),
                trace=trace, uses_randomness=True, suitable_for_puzzle=False,
                path_verified=False,
                is_complete=False, is_optimal=False)

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
            if not is_solvable(tuple(trial), goal):
                continue
            new_conflicts = sum(1 for j, v in enumerate(trial) if v != goal[j])
            if new_conflicts < best_conflicts:
                best_conflicts = new_conflicts
                best_swap = other

        if best_swap is not None:
            current[pos], current[best_swap] = current[best_swap], current[pos]
            total_conflicts = best_conflicts
            if len(trace) < 200:
                trace.append(TraceStep(
                    step=i, state=tuple(current),
                    reason=f"Swap pos {pos}↔{best_swap}, conflicts: {total_conflicts}"))

    return SearchResult(
        success=False, algorithm="Min-Conflicts", group="CSP",
        goal_state=goal,
        random_seed=seed,
        nodes_expanded=max_iterations, nodes_generated=max_iterations,
        runtime=time.perf_counter() - t0,
        message=f"Best: {total_conflicts} conflicts after {max_iterations} iterations. "
                 "Min-conflicts works better for N-Queens than 15-puzzle because "
                 "puzzle constraints are highly interdependent (transition constraints).",
        trace=trace, uses_randomness=True, suitable_for_puzzle=False,
        is_complete=False, is_optimal=False)


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

  2. Transition factor:
     A high-arity transition constraint connects A[t], X[t][0..15], and X[t+1][0..15].
     A decomposed encoding may add auxiliary blank-position or swap variables;
     it is not sixteen independent same-position edges.

  3. Initial constraint: X[0][p] = start[p]
     {dict(enumerate(start))}

  4. Goal constraint: X[{time_horizon}][p] = goal[p]
     {dict(enumerate(goal))}

Text representation for T=1:

  X[0][0]---X[0][1]---...---X[0][15]    (AllDifferent)
       \\__________ A[0] __________/
                    |
  X[1][0]---X[1][1]---...---X[1][15]    (AllDifferent)

Key insight: Constraint graphs for planning CSPs grow linearly
with time horizon T, but each time step has 16 position variables
+ 1 action variable, with AllDifferent hyperedges.

This is why CSP is not the standard approach for 15-puzzle:
the constraint graph becomes very large for deep solutions."""

    return SearchResult(
        success=True, algorithm="Constraint Graphs", group="CSP",
        goal_state=goal,
        message=msg, trace=[], suitable_for_puzzle=False,
        is_complete=False, is_optimal=False,
    )
