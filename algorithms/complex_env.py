"""Group 4: Searching in Complex Environments — AND-OR, No Observation, Partially Observable, Online (LRTA*).

Note: Standard 15-puzzle is deterministic and fully observable.
These algorithms are modeled as extended versions for academic illustration.
"""

import time
import random
from dataclasses import dataclass
from typing import Optional
from core.puzzle import PuzzleState, GOAL_STATE, _move_blank, is_solvable, scramble
from core.heuristics import get_heuristic
from core.metrics import SearchResult, TraceStep


BELIEF_PLANNERS = ("BFS", "A* Search", "Stochastic Hill Climbing")
AND_OR_EXPANSION_CAP = 100_000


@dataclass(frozen=True)
class _PlannerProposal:
    action: str | None
    requested_planner: str
    used_planner: str
    used_fallback: bool
    reason: str


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


def _best_heuristic_action(
    state: tuple[int, ...],
    goal: tuple[int, ...],
    action_order: str,
    h_fn,
) -> str | None:
    best_action = None
    best_h = float("inf")
    for ns, action, _ in PuzzleState(state).get_neighbors(action_order):
        h_val = h_fn(ns)
        if h_val < best_h:
            best_h = h_val
            best_action = action
    return best_action


def _first_planned_action(
    state: tuple[int, ...],
    goal: tuple[int, ...],
    planner: str,
    action_order: str,
    h_fn,
    *,
    seed: int | None = None,
) -> _PlannerProposal:
    """Use a group 1/2/3 algorithm to propose the first action from a belief state."""
    if state == goal:
        return _PlannerProposal(None, planner, planner, False, "state already matches goal")
    planner_name = planner if planner in BELIEF_PLANNERS else "A* Search"
    normalized_fallback = planner_name != planner
    try:
        if planner_name == "BFS":
            from algorithms.uninformed import bfs
            result = bfs(state, goal=goal, max_nodes=6000, timeout=0.25, action_order=action_order)
        elif planner_name == "Stochastic Hill Climbing":
            from algorithms.local_search import stochastic_hill_climbing
            result = stochastic_hill_climbing(
                state, goal=goal, max_iterations=1600, timeout=0.25,
                seed=seed, action_order=action_order,
            )
        else:
            from algorithms.informed import a_star
            result = a_star(
                state, goal=goal, heuristic="Manhattan Distance",
                max_nodes=6000, timeout=0.25, action_order=action_order,
            )
        if result.actions:
            reason = (
                f"unsupported planner={planner}; normalized to A* Search"
                if normalized_fallback
                else f"planner={planner_name} returned a planned action"
            )
            return _PlannerProposal(
                result.actions[0], planner, planner_name, normalized_fallback, reason,
            )
        fallback_reason = (
            f"planner={planner_name} returned no action "
            f"(termination={result.termination_reason or 'unknown'})"
        )
    except Exception as exc:
        fallback_reason = f"planner={planner_name} raised {type(exc).__name__}"

    return _PlannerProposal(
        _best_heuristic_action(state, goal, action_order, h_fn),
        planner,
        "Greedy heuristic fallback",
        True,
        fallback_reason,
    )


def _choose_belief_action(
    belief: set[tuple[int, ...]],
    goal: tuple[int, ...],
    action_order: str,
    planner: str,
    h_fn,
    *,
    seed: int | None = None,
) -> tuple[str | None, str]:
    votes = {action: 0 for action in action_order}
    planner_votes = {action: 0 for action in action_order}
    fallback_votes = {action: 0 for action in action_order}
    fallback_reasons: list[str] = []
    for idx, state in enumerate(sorted(belief)):
        proposal = _first_planned_action(
            state, goal, planner, action_order, h_fn,
            seed=None if seed is None else seed + idx,
        )
        action = proposal.action
        if action in votes:
            votes[action] += 1
            vote_bucket = fallback_votes if proposal.used_fallback else planner_votes
            vote_bucket[action] += 1
        if proposal.used_fallback and proposal.reason not in fallback_reasons:
            fallback_reasons.append(proposal.reason)

    scored: list[tuple[int, float, int, str]] = []
    for order_idx, action in enumerate(action_order):
        next_states = [_move_blank(state, action) or state for state in belief]
        avg_h = sum(h_fn(state) for state in next_states) / max(1, len(next_states))
        scored.append((-votes[action], avg_h, order_idx, action))
    if not scored:
        return None, (
            f"No legal belief action; planner={planner}, planner_votes={planner_votes}, "
            f"fallback_votes={fallback_votes}"
        )
    scored.sort()
    action = scored[0][3]
    fallback_note = (
        f", fallback_reason={' | '.join(fallback_reasons[:3])}"
        if fallback_reasons else ", fallback_reason=none"
    )
    return action, (
        f"planner={planner}, votes={votes}, planner_votes={planner_votes}, "
        f"fallback_votes={fallback_votes}, avg_h={scored[0][1]:.1f}"
        f"{fallback_note}"
    )


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
            path=[start], actions=[], goal_state=goal, cost=0, depth=0,
            nodes_expanded=nodes_expanded[0], nodes_generated=nodes_generated[0],
            runtime=time.perf_counter() - t0,
            message=(f"Conditional plan found (depth limit={max_depth}). AND-OR requires every "
                     f"supported outcome to succeed. Deflection support={support_mode}; "
                     f"nondet_prob>0 adds all legal deflections, not probability-weighted branches.\n{plan_text}"),
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
        trace=trace, uses_heuristic=True, uses_probability=False,
        is_complete=False, is_optimal=False, suitable_for_puzzle=False,
        termination_reason=stop_reason[0] or "depth_limit",
    )


def no_observation_search(
    start: tuple[int, ...], goal: tuple[int, ...] = GOAL_STATE,
    num_belief_states: int = 5, max_steps: int = 20,
    timeout: float = 60.0, action_order: str = "LRUD",
    seed: Optional[int] = None,
    known_positions: dict[int, int] | None = None,
    belief_planner: str = "A* Search",
) -> SearchResult:
    """Searching with No Observation using belief states.

    Agent cannot observe the state at all. Maintains a set of possible states.
    """
    t0 = time.perf_counter()
    rng = random.Random(seed)
    h_fn = get_heuristic("Manhattan Distance", goal)
    known = _normalize_known_positions(known_positions)
    belief = _build_belief_from_known_positions(
        start, goal, num_belief_states, rng, known, include_hidden=True,
    )

    representative = start
    representative_path = [start]
    actions_taken: list[str] = []
    representative_path_valid = True
    trace: list[TraceStep] = []
    trace.append(TraceStep(
        step=0,
        state=start,
        reason=(
            f"Blind initial belief size={len(belief)}; known positions={len(known)}; "
            f"candidate states reconstructed by bounded backtracking; planner={belief_planner}. "
            "Trace state is the hidden actual state for debugging; action selection uses belief."
        ),
        belief_size=len(belief),
    ))
    steps_completed = 0
    timed_out = False

    for step in range(max_steps):
        if time.perf_counter() - t0 > timeout:
            timed_out = True
            break

        best_action, planner_reason = _choose_belief_action(
            belief, goal, action_order, belief_planner, h_fn, seed=seed,
        )

        if best_action is None:
            break
        best_new_belief = {
            _move_blank(state, best_action) or state
            for state in belief
        }
        best_avg_h = sum(h_fn(state) for state in best_new_belief) / max(1, len(best_new_belief))
        actions_taken.append(best_action)
        if representative_path_valid:
            next_representative = _move_blank(representative, best_action)
            if next_representative is None:
                representative_path_valid = False
                representative_path = []
            else:
                representative = next_representative
                representative_path.append(representative)

        belief = best_new_belief
        steps_completed = step + 1

        if len(trace) < 200:
            trace.append(TraceStep(step=step + 1, state=representative, action=best_action,
                                   belief_size=len(belief),
                                   reason=(
                                       f"Blind action {best_action}; belief={len(belief)}, "
                                       f"avg_h={best_avg_h:.1f}; {planner_reason}. "
                                       "Trace state is the hidden actual state after the action; "
                                       "the decision itself uses belief."
                                   )))

        # Check if all belief states are goal
        if all(s == goal for s in belief):
            return SearchResult(
                success=True, algorithm="Searching with no observation", group="Complex Environments",
                path=representative_path if representative_path_valid else [],
                actions=actions_taken if representative_path_valid else [],
                goal_state=goal, cost=len(actions_taken), depth=len(actions_taken),
                random_seed=seed,
                nodes_expanded=step + 1, nodes_generated=step + 1,
                runtime=time.perf_counter() - t0,
                message=("All belief states reached goal. Returned path, when present, is the "
                         "representative trajectory from the hidden start state."),
                trace=trace, uses_randomness=True,
                is_complete=False, is_optimal=False, suitable_for_puzzle=False,
            )

    message = (
        f"Timeout after {steps_completed} belief-action step(s)."
        if timed_out
        else (
            f"Belief size={len(belief)} after {steps_completed} steps. "
            f"No observation keeps a belief set; planner={belief_planner} cannot safely collapse it."
        )
    )
    return SearchResult(
        success=False, algorithm="Searching with no observation", group="Complex Environments",
        path=representative_path if representative_path_valid else [],
        actions=actions_taken if representative_path_valid else [],
        goal_state=goal, depth=len(actions_taken), random_seed=seed,
        nodes_expanded=steps_completed, nodes_generated=steps_completed,
        runtime=time.perf_counter() - t0,
        message=message,
        trace=trace, uses_randomness=True,
        is_complete=False, is_optimal=False, suitable_for_puzzle=False,
    )


def partially_observable_search(
    start: tuple[int, ...], goal: tuple[int, ...] = GOAL_STATE,
    num_belief_states: int = 5, max_steps: int = 20,
    timeout: float = 60.0, action_order: str = "LRUD",
    seed: Optional[int] = None,
    known_positions: dict[int, int] | None = None,
    belief_planner: str = "A* Search",
) -> SearchResult:
    """Searching with Partial Observability.

    Agent observes: blank position + tiles adjacent to blank only.
    Uses belief update based on action + observation.
    """
    t0 = time.perf_counter()
    rng = random.Random(seed)
    h_fn = get_heuristic("Manhattan Distance", goal)
    known = _normalize_known_positions(known_positions)

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

    actual_state = start
    actual_path = [start]
    actual_actions: list[str] = []
    initial_observation = observe(actual_state)
    candidate_belief = _build_belief_from_known_positions(
        actual_state, goal, num_belief_states, rng, known, include_hidden=True,
    )
    observed_belief = {
        state for state in candidate_belief
        if observe(state) == initial_observation
    }
    belief = observed_belief or {actual_state}
    trace: list[TraceStep] = []
    trace.append(TraceStep(
        step=0,
        state=actual_state,
        observation=initial_observation,
        belief_size=len(belief),
        reason=(
            f"Initial partial belief={len(belief)} from {len(candidate_belief)} reconstructed "
            f"candidate state(s); known positions={len(known)}; planner={belief_planner}. "
            "Trace state is actual hidden state for audit; action selection uses belief."
        ),
    ))

    if actual_state == goal:
        return SearchResult(
            success=True, algorithm="Searching for partially observable problems", group="Complex Environments",
            path=actual_path, actions=actual_actions, goal_state=goal,
            cost=0, depth=0, random_seed=seed,
            nodes_expanded=0, nodes_generated=0,
            runtime=time.perf_counter() - t0,
            message="Actual state already at goal",
            trace=trace, uses_randomness=True,
            is_complete=False, is_optimal=False, suitable_for_puzzle=False,
        )

    steps_completed = 0
    timed_out = False
    for step in range(max_steps):
        if time.perf_counter() - t0 > timeout:
            timed_out = True
            break

        action, planner_reason = _choose_belief_action(
            belief, goal, action_order, belief_planner, h_fn, seed=seed,
        )
        if action is None:
            break

        # Move actual state
        ns = _move_blank(actual_state, action)
        if ns is not None:
            actual_state = ns
            actual_actions.append(action)
            actual_path.append(actual_state)

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
        steps_completed = step + 1

        if len(trace) < 200:
            trace.append(TraceStep(step=step + 1, state=actual_state, action=action,
                                   observation=obs, belief_size=len(belief),
                                   reason=(
                                       f"Obs filter after {action}: belief={len(belief)}; "
                                       f"{planner_reason}. Trace state is actual hidden state for audit."
                                   )))

        if len(belief) == 1 and actual_state in belief and actual_state != goal:
            from algorithms.informed import a_star
            planned = a_star(
                actual_state, goal=goal, heuristic="Manhattan Distance",
                max_nodes=6000, timeout=max(0.25, timeout - (time.perf_counter() - t0)),
                action_order=action_order,
            )
            if planned.success and planned.actions:
                actual_path.extend(planned.path[1:])
                actual_actions.extend(planned.actions)
                trace.append(TraceStep(
                    step=step + 1,
                    state=actual_state,
                    belief_size=1,
                    observation=obs,
                    reason=(
                        "Belief collapsed to one state; hand off to A* Search "
                        "to finish the reconstructed state path."
                    ),
                ))
                return SearchResult(
                    success=True,
                    algorithm="Searching for partially observable problems",
                    group="Complex Environments",
                    path=actual_path, actions=actual_actions, goal_state=goal,
                    cost=len(actual_actions), depth=len(actual_actions), random_seed=seed,
                    nodes_expanded=step + 1 + planned.nodes_expanded,
                    nodes_generated=step + 1 + planned.nodes_generated,
                    runtime=time.perf_counter() - t0,
                    message=(
                        "Partial observation collapsed the belief to the hidden state; "
                        "A* Search finished the path from the reconstructed state."
                    ),
                    trace=trace, uses_randomness=True, uses_heuristic=True,
                    is_complete=False, is_optimal=False, suitable_for_puzzle=False,
                )

        if actual_state == goal:
            return SearchResult(
                success=True, algorithm="Searching for partially observable problems", group="Complex Environments",
                path=actual_path, actions=actual_actions, goal_state=goal,
                cost=len(actual_actions), depth=len(actual_actions), random_seed=seed,
                nodes_expanded=step + 1, nodes_generated=step + 1,
                runtime=time.perf_counter() - t0,
                message="Actual state reached goal",
                trace=trace, uses_randomness=True,
                is_complete=False, is_optimal=False, suitable_for_puzzle=False,
            )

    message = (
        f"Timeout after {steps_completed} partial-observation step(s)."
        if timed_out
        else (
            f"Belief={len(belief)} after {steps_completed} steps. "
            f"Partial observation narrows belief via filtering; planner={belief_planner}."
        )
    )
    return SearchResult(
        success=False, algorithm="Searching for partially observable problems", group="Complex Environments",
        path=actual_path, actions=actual_actions, goal_state=goal,
        depth=len(actual_actions), random_seed=seed,
        nodes_expanded=steps_completed, nodes_generated=steps_completed,
        runtime=time.perf_counter() - t0,
        message=message,
        trace=trace, uses_randomness=True,
        is_complete=False, is_optimal=False, suitable_for_puzzle=False,
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
    nodes_generated = 1

    for step in range(max_steps):
        if time.perf_counter() - t0 > timeout:
            return SearchResult(success=False, algorithm="LRTA*", group="Complex Environments",
                                path=path, actions=actions_taken, depth=len(actions_taken),
                                goal_state=goal,
                                nodes_expanded=nodes_expanded, nodes_generated=nodes_generated,
                                runtime=time.perf_counter() - t0, message="Timeout", trace=trace,
                                uses_heuristic=True, is_complete=False, is_optimal=False, suitable_for_puzzle=False)

        if current not in H:
            H[current] = h_fn(current)

        if current == goal:
            return SearchResult(success=True, algorithm="LRTA*", group="Complex Environments",
                                path=path, actions=actions_taken, cost=len(actions_taken), depth=len(actions_taken),
                                goal_state=goal,
                                nodes_expanded=nodes_expanded, nodes_generated=nodes_generated,
                                runtime=time.perf_counter() - t0, message="Goal reached online", trace=trace,
                                uses_heuristic=True, is_complete=False, is_optimal=False, suitable_for_puzzle=False)

        visited_states.add(current)
        ps = PuzzleState(current)
        neighbors = ps.get_neighbors(action_order)
        nodes_expanded += 1
        nodes_generated += len(neighbors)

        if not neighbors:
            return SearchResult(success=False, algorithm="LRTA*", group="Complex Environments",
                                path=path, actions=actions_taken,
                                goal_state=goal,
                                nodes_expanded=nodes_expanded,
                                nodes_generated=nodes_generated,
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
                        goal_state=goal,
                        nodes_expanded=nodes_expanded, nodes_generated=nodes_generated,
                        runtime=time.perf_counter() - t0, message=f"Max steps reached, visited {len(visited_states)} states",
                        trace=trace, uses_heuristic=True, is_complete=False, is_optimal=False, suitable_for_puzzle=False)
