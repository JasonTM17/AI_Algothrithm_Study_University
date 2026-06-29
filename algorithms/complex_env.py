"""Group 4: AND-OR, conformant belief search, and contingent belief search.

The standard puzzle remains deterministic and fully observable. These
algorithms deliberately change the transition or sensor model and therefore
return conditional, conformant, or contingent planning evidence.
"""

import time
import random
from typing import Optional
from core.puzzle import PuzzleState, GOAL_STATE, _move_blank, is_solvable, scramble
from core.heuristics import get_heuristic
from core.metrics import SearchResult, TraceStep
from algorithms.belief_search import (
    BeliefState,
    conformant_belief_search,
    contingent_belief_search,
    observe_blank_and_neighbors,
)


AND_OR_EXPANSION_CAP = 100_000


def parse_known_positions_matrix(text: str) -> dict[int, int]:
    """Parse a 4x4 observation matrix where ``_`` means unknown."""
    rows = [row.strip() for row in text.strip().splitlines() if row.strip()]
    if len(rows) != 4:
        raise ValueError("known-tile matrix must contain exactly four rows")

    known: dict[int, int] = {}
    seen_values: set[int] = set()
    for row_index, row in enumerate(rows):
        tokens = row.replace(",", " ").split()
        if len(tokens) != 4:
            raise ValueError("each known-tile matrix row must contain four values")
        for column_index, token in enumerate(tokens):
            if token == "_":
                continue
            try:
                value = int(token)
            except ValueError as exc:
                raise ValueError("known tiles must be integers in 0..15 or _") from exc
            if not 0 <= value <= 15:
                raise ValueError("known tile value must be in 0..15")
            if value in seen_values:
                raise ValueError("known tile values must be unique")
            known[row_index * 4 + column_index] = value
            seen_values.add(value)
    return known


def format_known_positions_matrix(known_positions: dict[int, int] | None) -> str:
    """Format observed tile positions as a stable 4x4 matrix."""
    known = _normalize_known_positions(known_positions)
    cells = [str(known[index]) if index in known else "_" for index in range(16)]
    return "\n".join(" ".join(cells[start:start + 4]) for start in range(0, 16, 4))


def default_known_positions(start: tuple[int, ...], count: int = 2) -> dict[int, int]:
    """Return the first visible non-blank tile positions for partial-observation demos."""
    if count <= 0:
        return {}
    known: dict[int, int] = {}
    for idx, value in enumerate(start):
        if value == 0:
            continue
        known[idx] = value
        if len(known) >= count:
            break
    return known


def _normalize_known_positions(known_positions: dict[int, int] | None) -> dict[int, int]:
    if not known_positions:
        return {}
    normalized: dict[int, int] = {}
    seen_values: set[int] = set()
    for raw_pos, raw_value in known_positions.items():
        pos = int(raw_pos)
        value = int(raw_value)
        if pos < 0 or pos >= 16:
            raise ValueError("known position must be in 0..15")
        if value < 0 or value >= 16:
            raise ValueError("known tile value must be in 0..15")
        if value in seen_values:
            raise ValueError("known tile values must be unique")
        normalized[pos] = value
        seen_values.add(value)
    return normalized


def _matches_known_positions(state: tuple[int, ...], known_positions: dict[int, int]) -> bool:
    return all(state[pos] == value for pos, value in known_positions.items())


def _sample_state_from_known_positions(
    goal: tuple[int, ...],
    rng: random.Random,
    known_positions: dict[int, int],
) -> tuple[int, ...]:
    values = [None] * 16
    for pos, value in known_positions.items():
        values[pos] = value
    remaining_positions = [idx for idx, value in enumerate(values) if value is None]
    remaining_values = [value for value in range(16) if value not in known_positions.values()]
    rng.shuffle(remaining_values)
    for pos, value in zip(remaining_positions, remaining_values):
        values[pos] = value
    candidate = tuple(int(value) for value in values)
    if set(candidate) != set(range(16)):
        raise ValueError("known positions do not define a valid 15-puzzle domain")
    return candidate


def _build_belief_from_known_positions(
    hidden_state: tuple[int, ...],
    goal: tuple[int, ...],
    num_belief_states: int,
    rng: random.Random,
    known_positions: dict[int, int] | None,
    *,
    include_hidden: bool = True,
) -> set[tuple[int, ...]]:
    """Build a bounded belief set from partial tile-position clues."""
    known = _normalize_known_positions(known_positions)
    target_size = max(1, num_belief_states)
    belief: set[tuple[int, ...]] = set()
    if include_hidden and _matches_known_positions(hidden_state, known) and is_solvable(hidden_state, goal):
        belief.add(hidden_state)

    attempts = 0
    max_attempts = max(400, target_size * 250)
    while len(belief) < target_size and attempts < max_attempts:
        attempts += 1
        candidate = _sample_state_from_known_positions(goal, rng, known)
        if candidate != goal and is_solvable(candidate, goal):
            belief.add(candidate)

    fill_attempts = 0
    while len(belief) < target_size and fill_attempts < target_size * 100:
        fill_attempts += 1
        candidate = scramble(goal=goal, depth=rng.randint(2, 10), seed=rng.randint(0, 999999))
        if _matches_known_positions(candidate, known) and is_solvable(candidate, goal):
            belief.add(candidate)

    return belief or {hidden_state}


def and_or_search(
    start: tuple[int, ...], goal: tuple[int, ...] = GOAL_STATE,
    max_depth: int = 10, nondet_prob: float = 0.3,
    timeout: float = 60.0, action_order: str = "LRUD",
    seed: Optional[int] = None,
) -> SearchResult:
    """AND-OR Search for nondeterministic 15-puzzle.

    When the agent chooses an action, the environment support set may contain
    only the intended outcome or all legal deflections. ``nondet_prob`` remains
    in the signature for compatibility: 0 means intended-only, any value above
    0 enables deflection support. AND-OR does not weight outcomes by probability.
    Returns a conditional plan (IF-THEN structure), not a simple path.
    """
    t0 = time.perf_counter()
    if not 0.0 <= nondet_prob <= 1.0:
        raise ValueError("nondet_prob must be between 0 and 1")
    # AND-OR search reasons about possible outcomes, not their probability
    # magnitudes. ``nondet_prob`` controls whether deflection outcomes exist.
    deflection_enabled = nondet_prob > 0.0
    del seed
    h_fn = get_heuristic("Manhattan Distance", goal)
    nodes_expanded = [0]
    nodes_generated = [1]
    stop_reason: list[str | None] = [None]

    class _SearchStopped(RuntimeError):
        pass

    def check_budget() -> None:
        if time.perf_counter() - t0 >= timeout:
            stop_reason[0] = "timeout"
            raise _SearchStopped
        if nodes_expanded[0] >= AND_OR_EXPANSION_CAP:
            stop_reason[0] = "resource_limit"
            raise _SearchStopped

    def get_outcomes(state: tuple, action: str) -> list[tuple[tuple, str, str]]:
        """Return (new_state, actual_action, type) for action + possible deflections."""
        results = []
        ns = _move_blank(state, action)
        if ns is not None:
            results.append((ns, action, "intended"))

        if not deflection_enabled:
            return results

        for alt_action in action_order:
            if alt_action == action:
                continue
            ns_alt = _move_blank(state, alt_action)
            if ns_alt is not None:
                results.append((ns_alt, alt_action, f"deflected from {action}"))

        return results

    def or_search(state: tuple, depth: int, visited: set) -> Optional[dict]:
        check_budget()
        nodes_expanded[0] += 1
        if state == goal:
            return {"type": "goal"}
        if depth <= 0 or state in visited:
            return None

        visited.add(state)
        ordered_actions = sorted(
            (
                (h_fn(next_state), order_index, action)
                for order_index, action in enumerate(action_order)
                if (next_state := _move_blank(state, action)) is not None
            ),
            key=lambda item: (item[0], item[1]),
        )
        for _, _, action in ordered_actions:
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
    support_mode = "include all legal deflections" if deflection_enabled else "intended outcome only"
    trace.append(TraceStep(
        step=0,
        state=start,
        reason=(
            f"AND-OR search start; deflection support={support_mode}. "
            f"nondet_prob={nondet_prob} is treated as a binary support switch, not a probability weight."
        ),
    ))

    try:
        result = or_search(start, max_depth, set())
    except _SearchStopped:
        result = None

    if result is not None:
        def format_plan(plan, indent=0):
            lines = []
            prefix = "  " * indent
            if plan["type"] == "goal":
                lines.append(f"{prefix}GOAL reached")
            elif plan["type"] == "OR":
                state_h = plan.get('state_h')
                h_str = f"{state_h:.1f}" if state_h is not None else "?"
                lines.append(f"{prefix}OR: choose action {plan['action']} (h={h_str})")
                if plan.get("outcomes"):
                    for oc in plan["outcomes"]:
                        lines.append(f"{prefix}  IF {oc['outcome']} (action={oc['actual_action']}):")
                        lines.extend(format_plan(oc["plan"], indent + 2))
            return lines

        plan_text = "\n".join(format_plan(result))
        trace.append(TraceStep(step=1, state=start, reason="Conditional plan found"))
        return SearchResult(
            success=True, algorithm="AND-OR Search", group="Complex Environments",
            goal_state=goal, cost=0, depth=0,
            nodes_expanded=nodes_expanded[0], nodes_generated=nodes_generated[0],
            runtime=time.perf_counter() - t0,
            message=(f"Conditional plan found (depth limit={max_depth}). AND-OR requires every "
                     f"supported outcome to succeed. Deflection support={support_mode}; "
                     f"nondet_prob>0 adds all legal deflections, not probability-weighted branches.\n{plan_text}"),
            capability="conditional_plan",
            model_evidence={
                "conditional_plan": result,
                "deflection_support": support_mode,
                "probability_weighting": False,
            },
            trace=trace, uses_heuristic=True, uses_probability=False,
            is_complete=False, is_optimal=False, suitable_for_puzzle=False,
        )

    if stop_reason[0] == "timeout":
        failure_message = (
            f"AND-OR stopped after the {timeout:g}s timeout before proving or disproving a "
            f"conditional plan at depth {max_depth}. Deflection support={support_mode}."
        )
    elif stop_reason[0] == "resource_limit":
        failure_message = (
            f"AND-OR stopped at the {AND_OR_EXPANSION_CAP:,}-node safety cap before proving or "
            f"disproving a conditional plan at depth {max_depth}. "
            f"Deflection support={support_mode}."
        )
    else:
        failure_message = (
            f"No conditional plan found within depth {max_depth}. "
            f"Deflection support={support_mode}; AND-OR requires a subplan for every supported outcome."
        )
    trace.append(TraceStep(
        step=1,
        state=start,
        reason=failure_message,
        frontier_size=0,
        reached_size=nodes_expanded[0],
    ))
    return SearchResult(
        success=False, algorithm="AND-OR Search", group="Complex Environments",
        goal_state=goal,
        nodes_expanded=nodes_expanded[0], nodes_generated=nodes_generated[0],
        runtime=time.perf_counter() - t0,
        message=failure_message,
        capability="conditional_plan",
        model_evidence={
            "conditional_plan": None,
            "deflection_support": support_mode,
            "probability_weighting": False,
        },
        trace=trace, uses_heuristic=True, uses_probability=False,
        is_complete=False, is_optimal=False, suitable_for_puzzle=False,
        termination_reason=stop_reason[0] or "depth_limit",
    )


def no_observation_search(
    start: tuple[int, ...],
    goal: tuple[int, ...] = GOAL_STATE,
    num_belief_states: int = 5,
    max_steps: int = 20,
    timeout: float = 60.0,
    action_order: str = "LRUD",
    seed: Optional[int] = None,
    known_positions: dict[int, int] | None = None,
    belief_planner: str = "Belief BFS",
    max_beliefs: int = 5_000,
) -> SearchResult:
    """Search belief states for one conformant action sequence."""
    started = time.perf_counter()
    rng = random.Random(seed)
    known = _normalize_known_positions(known_positions)
    initial = BeliefState(
        _build_belief_from_known_positions(
            start,
            goal,
            num_belief_states,
            rng,
            known,
            include_hidden=True,
        )
    )
    outcome = conformant_belief_search(
        initial,
        tuple(goal),
        max_depth=max_steps,
        max_beliefs=max_beliefs,
        timeout=timeout,
        action_order=action_order,
    )
    del belief_planner
    return SearchResult(
        success=outcome.success,
        algorithm="Searching with no observation",
        group="Complex Environments",
        actions=outcome.actions,
        goal_state=goal,
        cost=len(outcome.actions),
        depth=len(outcome.actions),
        random_seed=seed,
        nodes_expanded=outcome.nodes_expanded,
        nodes_generated=outcome.nodes_generated,
        max_frontier_size=outcome.max_frontier,
        reached_size=outcome.reached_size,
        runtime=time.perf_counter() - started,
        message=(
            "Conformant belief-state search found one fixed action sequence "
            "that sends every represented state to the goal."
            if outcome.success
            else (
                f"Conformant belief-state search stopped with "
                f"{outcome.termination_reason}. Bounded failure is not a "
                "global impossibility proof."
            )
        ),
        capability="conformant_plan",
        model_evidence={
            **outcome.evidence,
            "actions": outcome.actions,
            "known_positions": known,
            "finite_belief_approximation": True,
            "illegal_action_semantics": "no-op",
            "hidden_state_used_for_policy": False,
        },
        trace=outcome.trace,
        termination_reason=outcome.termination_reason,
        uses_randomness=True,
        is_complete=False,
        is_optimal=False,
        suitable_for_puzzle=False,
    )


def partially_observable_search(
    start: tuple[int, ...],
    goal: tuple[int, ...] = GOAL_STATE,
    num_belief_states: int = 5,
    max_steps: int = 20,
    timeout: float = 60.0,
    action_order: str = "LRUD",
    seed: Optional[int] = None,
    known_positions: dict[int, int] | None = None,
    belief_planner: str = "Belief AND-OR",
    max_beliefs: int = 5_000,
) -> SearchResult:
    """Build a contingent policy over deterministic local observations."""
    started = time.perf_counter()
    rng = random.Random(seed)
    known = _normalize_known_positions(known_positions)
    candidates = _build_belief_from_known_positions(
        start,
        goal,
        num_belief_states,
        rng,
        known,
        include_hidden=True,
    )
    initial_observation = observe_blank_and_neighbors(tuple(start))
    filtered = {
        state
        for state in candidates
        if observe_blank_and_neighbors(state) == initial_observation
    }
    initial = BeliefState(filtered or {tuple(start)})
    outcome = contingent_belief_search(
        initial,
        tuple(goal),
        max_depth=max_steps,
        max_beliefs=max_beliefs,
        timeout=timeout,
        action_order=action_order,
    )
    del belief_planner
    return SearchResult(
        success=outcome.success,
        algorithm="Searching for partially observable problems",
        group="Complex Environments",
        goal_state=goal,
        random_seed=seed,
        nodes_expanded=outcome.nodes_expanded,
        nodes_generated=outcome.nodes_generated,
        reached_size=outcome.reached_size,
        runtime=time.perf_counter() - started,
        message=(
            "Contingent belief-state AND-OR search found a policy covering "
            "every represented observation branch."
            if outcome.success
            else (
                f"Contingent belief-state search stopped with "
                f"{outcome.termination_reason}. No A* fallback was used."
            )
        ),
        capability="contingent_policy",
        model_evidence={
            **outcome.evidence,
            "initial_observation": initial_observation,
            "known_positions": known,
            "finite_belief_approximation": True,
            "hidden_state_used_for_policy": False,
        },
        trace=outcome.trace,
        termination_reason=outcome.termination_reason,
        uses_randomness=True,
        is_complete=False,
        is_optimal=False,
        suitable_for_puzzle=False,
    )
