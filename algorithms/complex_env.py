"""Group 4: Searching in Complex Environments — AND-OR, No Observation, Partially Observable, Online (LRTA*).

Note: Standard 15-puzzle is deterministic and fully observable.
These algorithms are modeled as extended versions for academic illustration.
"""

import time
import random
from typing import Optional
from core.puzzle import PuzzleState, GOAL_STATE, _move_blank, is_solvable, scramble
from core.heuristics import get_heuristic, manhattan_distance
from core.metrics import SearchResult, TraceStep


def and_or_search(
    start: tuple[int, ...], goal: tuple[int, ...] = GOAL_STATE,
    max_depth: int = 10, nondet_prob: float = 0.3,
    timeout: float = 60.0, action_order: str = "LRUD",
    seed: Optional[int] = None,
) -> SearchResult:
    """AND-OR Search for nondeterministic 15-puzzle.

    When agent chooses an action, the environment may execute it
    or deflect to an adjacent valid move with probability nondet_prob.
    Returns a conditional plan (IF-THEN structure), not a simple path.
    """
    t0 = time.perf_counter()
    if not 0.0 <= nondet_prob <= 1.0:
        raise ValueError("nondet_prob must be between 0 and 1")
    # AND-OR search reasons about possible outcomes, not their probability
    # magnitudes. ``nondet_prob`` controls whether deflection outcomes exist.
    del seed
    h_fn = get_heuristic("Manhattan Distance", goal)
    nodes_expanded = [0]
    nodes_generated = [1]

    def get_outcomes(state: tuple, action: str) -> list[tuple[tuple, str, str]]:
        """Return (new_state, actual_action, type) for action + possible deflections."""
        results = []
        ns = _move_blank(state, action)
        if ns is not None:
            results.append((ns, action, "intended"))

        if nondet_prob == 0.0:
            return results

        blank_idx = state.index(0)
        r, c = blank_idx // 4, blank_idx % 4
        for alt_action in action_order:
            if alt_action == action:
                continue
            ns_alt = _move_blank(state, alt_action)
            if ns_alt is not None:
                results.append((ns_alt, alt_action, f"deflected from {action}"))

        return results

    def or_search(state: tuple, depth: int, visited: set) -> Optional[dict]:
        nodes_expanded[0] += 1
        if state == goal:
            return {"type": "goal"}
        if depth <= 0 or state in visited:
            return None
        if time.perf_counter() - t0 > timeout:
            return None

        visited.add(state)
        for action in action_order:
            outcomes = get_outcomes(state, action)
            nodes_generated[0] += len(outcomes)
            if not outcomes:
                continue
            and_result = and_search(outcomes, depth - 1, visited)
            if and_result is not None:
                visited.discard(state)
                return {"type": "OR", "action": action, "outcomes": and_result, "state_h": h_fn(state)}
        visited.discard(state)
        return None

    def and_search(outcomes: list, depth: int, visited: set) -> Optional[list[dict]]:
        plans = []
        for new_state, actual_action, outcome_type in outcomes:
            plan = or_search(new_state, depth, visited)
            if plan is None:
                return None
            plans.append({
                "outcome": outcome_type,
                "actual_action": actual_action,
                "plan": plan,
                "state": new_state,
            })
        return plans

    trace: list[TraceStep] = []
    trace.append(TraceStep(step=0, state=start, reason=f"AND-OR search start, nondet_prob={nondet_prob}"))

    result = or_search(start, max_depth, set())

    if result is not None:
        def format_plan(plan, indent=0):
            lines = []
            prefix = "  " * indent
            if plan["type"] == "goal":
                lines.append(f"{prefix}GOAL reached")
            elif plan["type"] == "OR":
                lines.append(f"{prefix}OR: choose action {plan['action']} (h={plan.get('state_h', '?'):.1f})")
                if plan.get("outcomes"):
                    for oc in plan["outcomes"]:
                        lines.append(f"{prefix}  IF {oc['outcome']} (action={oc['actual_action']}):")
                        lines.extend(format_plan(oc["plan"], indent + 2))
            return lines

        plan_text = "\n".join(format_plan(result))
        trace.append(TraceStep(step=1, state=start, reason="Conditional plan found"))
        return SearchResult(
            success=True, algorithm="AND-OR Search", group="Complex Environments",
            path=[start], actions=[], cost=0, depth=0,
            nodes_expanded=nodes_expanded[0], nodes_generated=nodes_generated[0],
            runtime=time.perf_counter() - t0,
            message=(f"Conditional plan found (depth limit={max_depth}). AND-OR requires every "
                     f"possible outcome to succeed; probability magnitudes do not rank plans.\n{plan_text}"),
            trace=trace, uses_heuristic=True, uses_probability=False,
            is_complete=False, is_optimal=False, suitable_for_puzzle=False,
        )

    return SearchResult(
        success=False, algorithm="AND-OR Search", group="Complex Environments",
        nodes_expanded=nodes_expanded[0], nodes_generated=nodes_generated[0],
        runtime=time.perf_counter() - t0,
        message=f"No conditional plan found within depth {max_depth}",
        trace=trace, uses_heuristic=True, uses_probability=False,
        is_complete=False, is_optimal=False, suitable_for_puzzle=False,
    )


def no_observation_search(
    start: tuple[int, ...], goal: tuple[int, ...] = GOAL_STATE,
    num_belief_states: int = 5, max_steps: int = 20,
    timeout: float = 60.0, action_order: str = "LRUD",
    seed: Optional[int] = None,
) -> SearchResult:
    """Searching with No Observation using belief states.

    Agent cannot observe the state at all. Maintains a set of possible states.
    """
    t0 = time.perf_counter()
    rng = random.Random(seed)
    h_fn = manhattan_distance

    belief = set()
    belief.add(start)
    while len(belief) < num_belief_states:
        s = scramble(depth=rng.randint(3, 8), seed=rng.randint(0, 999999))
        if is_solvable(s) and s != goal:
            belief.add(s)

    initial_belief = frozenset(belief)
    trace: list[TraceStep] = []
    trace.append(TraceStep(step=0, state=start, reason=f"Initial belief size={len(belief)}",
                           belief_size=len(belief)))

    for step in range(max_steps):
        if time.perf_counter() - t0 > timeout:
            break

        # Choose action that reduces average h in belief
        best_action = None
        best_avg_h = float("inf")

        for action in action_order:
            total_h = 0
            new_belief = set()
            valid = True
            for state in belief:
                ns = _move_blank(state, action)
                if ns is not None:
                    new_belief.add(ns)
                    total_h += h_fn(ns)
                else:
                    new_belief.add(state)
                    total_h += h_fn(state)
            avg_h = total_h / len(belief) if belief else float("inf")
            if avg_h < best_avg_h:
                best_avg_h = avg_h
                best_action = action
                best_new_belief = new_belief

        if best_action is None:
            break

        # Apply best_action to all states in belief to get new belief
        new_belief = set()
        for state in belief:
            ns = _move_blank(state, best_action)
            if ns is not None:
                new_belief.add(ns)
            else:
                new_belief.add(state)
        belief = new_belief

        if len(trace) < 200:
            trace.append(TraceStep(step=step + 1, state=start, action=best_action,
                                   belief_size=len(belief),
                                   reason=f"Action {best_action}, belief={len(belief)}, avg_h={best_avg_h:.1f}"))

        # Check if all belief states are goal
        if all(s == goal for s in belief):
            return SearchResult(
                success=True, algorithm="No Observation Search", group="Complex Environments",
                path=[], actions=[], cost=0, depth=0,
                nodes_expanded=step + 1, nodes_generated=step + 1,
                runtime=time.perf_counter() - t0,
                message="All belief states reached goal",
                trace=trace, is_complete=False, is_optimal=False, suitable_for_puzzle=False,
            )

    return SearchResult(
        success=False, algorithm="No Observation Search", group="Complex Environments",
        nodes_expanded=max_steps, nodes_generated=max_steps,
        runtime=time.perf_counter() - t0,
        message=f"Belief size={len(belief)} after {max_steps} steps. No observation is harder than standard search.",
        trace=trace, is_complete=False, is_optimal=False, suitable_for_puzzle=False,
    )


def partially_observable_search(
    start: tuple[int, ...], goal: tuple[int, ...] = GOAL_STATE,
    num_belief_states: int = 5, max_steps: int = 20,
    timeout: float = 60.0, action_order: str = "LRUD",
    seed: Optional[int] = None,
) -> SearchResult:
    """Searching with Partial Observability.

    Agent observes: blank position + tiles adjacent to blank only.
    Uses belief update based on action + observation.
    """
    t0 = time.perf_counter()
    rng = random.Random(seed)
    h_fn = manhattan_distance

    def observe(state: tuple) -> str:
        """Partial observation: blank position + adjacent tiles."""
        blank = state.index(0)
        r, c = blank // 4, blank % 4
        adj = []
        for dr, dc, name in [(-1, 0, "U"), (1, 0, "D"), (0, -1, "L"), (0, 1, "R")]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < 4 and 0 <= nc < 4:
                adj.append(f"{name}:{state[nr * 4 + nc]}")
        return f"blank=({r},{c}) adj=[{', '.join(adj)}]"

    # Initialize belief states
    belief = set()
    belief.add(start)
    while len(belief) < num_belief_states:
        s = scramble(depth=rng.randint(2, 6), seed=rng.randint(0, 999999))
        if is_solvable(s) and s != goal:
            belief.add(s)

    actual_state = start
    trace: list[TraceStep] = []
    trace.append(TraceStep(step=0, state=actual_state, observation=observe(actual_state),
                           belief_size=len(belief), reason=f"Initial belief={len(belief)}"))

    for step in range(max_steps):
        if time.perf_counter() - t0 > timeout:
            break

        action = action_order[0]  # Simplified: choose first valid action
        for a in action_order:
            if _move_blank(actual_state, a) is not None:
                action = a
                break

        # Move actual state
        ns = _move_blank(actual_state, action)
        if ns is not None:
            actual_state = ns

        # Get observation
        obs = observe(actual_state)

        # Update belief
        new_belief = set()
        for state in belief:
            ns_b = _move_blank(state, action)
            if ns_b is not None:
                new_belief.add(ns_b)
            else:
                new_belief.add(state)

        # Filter by observation
        filtered = set()
        for state in new_belief:
            if observe(state) == obs:
                filtered.add(state)

        belief = filtered if filtered else new_belief

        if len(trace) < 200:
            trace.append(TraceStep(step=step + 1, state=actual_state, action=action,
                                   observation=obs, belief_size=len(belief),
                                   reason=f"Obs filter: belief={len(belief)} after {action}"))

        if actual_state == goal:
            return SearchResult(
                success=True, algorithm="Partially Observable Search", group="Complex Environments",
                path=[], actions=[], cost=0, depth=0,
                nodes_expanded=step + 1, nodes_generated=step + 1,
                runtime=time.perf_counter() - t0,
                message="Actual state reached goal",
                trace=trace, is_complete=False, is_optimal=False, suitable_for_puzzle=False,
            )

    return SearchResult(
        success=False, algorithm="Partially Observable Search", group="Complex Environments",
        nodes_expanded=max_steps, nodes_generated=max_steps,
        runtime=time.perf_counter() - t0,
        message=f"Belief={len(belief)} after {max_steps} steps. Partial observation narrows belief via filtering.",
        trace=trace, is_complete=False, is_optimal=False, suitable_for_puzzle=False,
    )


def online_search_lrta(
    start: tuple[int, ...], goal: tuple[int, ...] = GOAL_STATE,
    heuristic: str = "Manhattan Distance",
    max_steps: int = 10000, timeout: float = 60.0,
    action_order: str = "LRUD",
) -> SearchResult:
    """Online search using LRTA* (Learning Real-Time A*).

    Agent doesn't know the full space. At each state, chooses neighbor
    with lowest estimated cost (g + H), then updates H(current).
    """
    t0 = time.perf_counter()
    h_fn = get_heuristic(heuristic, goal)

    H: dict[tuple, float] = {}
    current = start
    path = [current]
    actions_taken: list[str] = []
    visited_states: set = set()
    trace: list[TraceStep] = []
    nodes_expanded = 0

    for step in range(max_steps):
        if time.perf_counter() - t0 > timeout:
            return SearchResult(success=False, algorithm="LRTA*", group="Complex Environments",
                                path=path, actions=actions_taken, depth=len(actions_taken),
                                nodes_expanded=nodes_expanded, nodes_generated=nodes_expanded,
                                runtime=time.perf_counter() - t0, message="Timeout", trace=trace,
                                uses_heuristic=True, is_complete=False, is_optimal=False, suitable_for_puzzle=False)

        if current not in H:
            H[current] = h_fn(current)

        if current == goal:
            return SearchResult(success=True, algorithm="LRTA*", group="Complex Environments",
                                path=path, actions=actions_taken, cost=len(actions_taken), depth=len(actions_taken),
                                nodes_expanded=nodes_expanded, nodes_generated=nodes_expanded,
                                runtime=time.perf_counter() - t0, message="Goal reached online", trace=trace,
                                uses_heuristic=True, is_complete=False, is_optimal=False, suitable_for_puzzle=False)

        visited_states.add(current)
        ps = PuzzleState(current)
        neighbors = ps.get_neighbors(action_order)
        nodes_expanded += 1

        if not neighbors:
            return SearchResult(success=False, algorithm="LRTA*", group="Complex Environments",
                                path=path, actions=actions_taken,
                                nodes_expanded=nodes_expanded,
                                runtime=time.perf_counter() - t0, message="No valid moves", trace=trace,
                                uses_heuristic=True, is_complete=False, is_optimal=False, suitable_for_puzzle=False)

        # Choose neighbor with lowest estimated cost
        best_ns, best_action, best_cost = None, None, float("inf")
        for ns, action, cost in neighbors:
            h_val = H.get(ns, h_fn(ns))
            total = cost + h_val
            if total < best_cost:
                best_cost = total
                best_ns, best_action = ns, action

        # Update H(current) = min(cost + H(neighbor))
        old_h = H[current]
        H[current] = best_cost if best_cost > old_h else old_h

        if len(trace) < 200:
            trace.append(TraceStep(
                step=step, state=current, action=best_action,
                h=H.get(current, h_fn(current)),
                reason=f"LRTA*: h_old={old_h:.1f}, h_new={H[current]:.1f}, action={best_action}, visited={len(visited_states)}",
            ))

        if best_ns is not None:
            current = best_ns
            path.append(current)
            actions_taken.append(best_action)
        else:
            break

    return SearchResult(success=False, algorithm="LRTA*", group="Complex Environments",
                        path=path, actions=actions_taken, depth=len(actions_taken),
                        nodes_expanded=nodes_expanded, nodes_generated=nodes_expanded,
                        runtime=time.perf_counter() - t0, message=f"Max steps reached, visited {len(visited_states)} states",
                        trace=trace, uses_heuristic=True, is_complete=False, is_optimal=False, suitable_for_puzzle=False)
