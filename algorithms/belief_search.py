"""Belief-state search primitives for the complex-environment teaching models."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
import time

from core.metrics import TraceStep
from core.puzzle import _move_blank


State = tuple[int, ...]
BeliefState = frozenset[State]


def observe_blank_and_neighbors(state: State) -> str:
    """Return the deterministic local percept used by the partial sensor demo."""
    blank = state.index(0)
    row, col = divmod(blank, 4)
    adjacent: list[str] = []
    for dr, dc, label in ((-1, 0, "U"), (1, 0, "D"), (0, -1, "L"), (0, 1, "R")):
        next_row, next_col = row + dr, col + dc
        if 0 <= next_row < 4 and 0 <= next_col < 4:
            adjacent.append(f"{label}:{state[next_row * 4 + next_col]}")
    return f"blank=({row},{col}) adj=[{', '.join(adjacent)}]"


def predict_belief(belief: BeliefState, action: str) -> BeliefState:
    """Apply one action to every possible state; illegal moves are explicit no-ops."""
    return frozenset(_move_blank(state, action) or state for state in belief)


def partition_by_observation(
    belief: BeliefState,
) -> dict[str, BeliefState]:
    """Partition a predicted belief under the deterministic local sensor."""
    groups: dict[str, set[State]] = {}
    for state in belief:
        observation = observe_blank_and_neighbors(state)
        groups.setdefault(observation, set()).add(state)
    return {
        observation: frozenset(states)
        for observation, states in sorted(groups.items())
    }


def _belief_payload(belief: BeliefState, sample_size: int = 4) -> dict[str, object]:
    states = sorted(belief)
    return {
        "size": len(states),
        "sample": [list(state) for state in states[:sample_size]],
        "omitted": max(0, len(states) - sample_size),
    }


@dataclass
class BeliefSearchOutcome:
    success: bool
    termination_reason: str
    actions: list[str] = field(default_factory=list)
    trace: list[TraceStep] = field(default_factory=list)
    nodes_expanded: int = 0
    nodes_generated: int = 0
    max_frontier: int = 0
    reached_size: int = 0
    evidence: dict[str, object] = field(default_factory=dict)


def conformant_belief_search(
    initial_belief: BeliefState,
    goal: State,
    *,
    max_depth: int,
    max_beliefs: int,
    timeout: float,
    action_order: str,
) -> BeliefSearchOutcome:
    """Find one fixed action sequence that sends every possible state to the goal."""
    started = time.perf_counter()
    if not initial_belief:
        return BeliefSearchOutcome(
            False,
            "invalid_belief",
            evidence={"initial_belief": _belief_payload(initial_belief)},
        )
    if all(state == goal for state in initial_belief):
        return BeliefSearchOutcome(
            True,
            "model_success",
            trace=[],
            nodes_expanded=0,
            nodes_generated=1,
            max_frontier=1,
            reached_size=1,
            evidence={
                "initial_belief": _belief_payload(initial_belief),
                "belief_history": [_belief_payload(initial_belief)],
                "goal_coverage": len(initial_belief),
            },
        )

    frontier = deque([(initial_belief, [], [initial_belief])])
    reached = {initial_belief}
    trace: list[TraceStep] = []
    expanded = 0
    generated = 1
    max_frontier = 1

    while frontier:
        if time.perf_counter() - started >= timeout:
            return BeliefSearchOutcome(
                False, "timeout", trace=trace, nodes_expanded=expanded,
                nodes_generated=generated, max_frontier=max_frontier,
                reached_size=len(reached),
                evidence={"initial_belief": _belief_payload(initial_belief)},
            )
        belief, actions, history = frontier.popleft()
        if all(state == goal for state in belief):
            return BeliefSearchOutcome(
                True, "model_success", actions=actions, trace=trace,
                nodes_expanded=expanded, nodes_generated=generated,
                max_frontier=max_frontier, reached_size=len(reached),
                evidence={
                    "initial_belief": _belief_payload(initial_belief),
                    "belief_history": [_belief_payload(item) for item in history],
                    "goal_coverage": len(belief),
                },
            )
        if len(actions) >= max_depth:
            continue

        expanded += 1
        for action in action_order:
            predicted = predict_belief(belief, action)
            generated += 1
            accepted = predicted not in reached
            over_budget = accepted and len(reached) + 1 > max_beliefs
            if accepted and not over_budget:
                reached.add(predicted)
                frontier.append((predicted, actions + [action], history + [predicted]))
                max_frontier = max(max_frontier, len(frontier))
            if len(trace) < 200:
                representative = min(predicted)
                trace.append(
                    TraceStep(
                        step=expanded,
                        state=representative,
                        action=action,
                        event=(
                            "resource_limit_belief"
                            if over_budget
                            else "generate_belief"
                            if accepted
                            else "reject_duplicate_belief"
                        ),
                        belief_size=len(predicted),
                        frontier_size=len(frontier),
                        reached_size=len(reached),
                        reason=(
                            f"Predict(B,{action}); belief {len(belief)}->{len(predicted)}; "
                            f"goal_coverage={sum(state == goal for state in predicted)}/{len(predicted)}"
                        ),
                    )
                )
            if over_budget:
                return BeliefSearchOutcome(
                    False, "resource_limit", trace=trace,
                    nodes_expanded=expanded, nodes_generated=generated,
                    max_frontier=max_frontier, reached_size=len(reached),
                    evidence={"initial_belief": _belief_payload(initial_belief)},
                )

    return BeliefSearchOutcome(
        False, "depth_limit", trace=trace, nodes_expanded=expanded,
        nodes_generated=generated, max_frontier=max_frontier,
        reached_size=len(reached),
        evidence={"initial_belief": _belief_payload(initial_belief)},
    )


def contingent_belief_search(
    initial_belief: BeliefState,
    goal: State,
    *,
    max_depth: int,
    max_beliefs: int,
    timeout: float,
    action_order: str,
) -> BeliefSearchOutcome:
    """Build a bounded policy whose branches cover every possible observation."""
    started = time.perf_counter()
    if not initial_belief:
        return BeliefSearchOutcome(
            False,
            "invalid_belief",
            evidence={
                "initial_belief": _belief_payload(initial_belief),
                "policy": None,
                "sensor": "blank position and tiles adjacent to the blank",
            },
        )
    trace: list[TraceStep] = []
    expanded = 0
    generated = 1
    seen_beliefs: set[BeliefState] = set()
    stopped: str | None = None

    def check_budget() -> bool:
        nonlocal stopped
        if time.perf_counter() - started >= timeout:
            stopped = "timeout"
            return False
        if len(seen_beliefs) >= max_beliefs:
            stopped = "resource_limit"
            return False
        return True

    def or_search(
        belief: BeliefState,
        depth: int,
        path: frozenset[BeliefState],
    ) -> dict[str, object] | None:
        nonlocal expanded, generated
        if not belief:
            return None
        if all(state == goal for state in belief):
            return {"type": "goal", "belief": _belief_payload(belief)}
        if not check_budget():
            return None
        if depth <= 0 or belief in path:
            return None

        seen_beliefs.add(belief)
        expanded += 1
        for action in action_order:
            predicted = predict_belief(belief, action)
            partitions = partition_by_observation(predicted)
            generated += 1 + len(partitions)
            if len(trace) < 200:
                trace.append(
                    TraceStep(
                        step=expanded,
                        state=min(predicted),
                        action=action,
                        event="predict",
                        belief_size=len(predicted),
                        observation=f"{len(partitions)} possible percept(s)",
                        reached_size=len(seen_beliefs),
                        reason=(
                            f"Predict belief {len(belief)}->{len(predicted)}; "
                            f"partition into {len(partitions)} observation branch(es)"
                        ),
                    )
                )

            branches: dict[str, object] = {}
            valid = True
            for observation, updated in partitions.items():
                child = or_search(updated, depth - 1, path | {belief})
                if len(trace) < 200:
                    trace.append(
                        TraceStep(
                            step=expanded,
                            state=min(updated),
                            action=action,
                            event="observation_branch",
                            belief_size=len(updated),
                            observation=observation,
                            reason=(
                                f"Update(Predict(B,{action}), observation); "
                                f"branch belief={len(updated)}"
                            ),
                        )
                    )
                if child is None:
                    valid = False
                    break
                branches[observation] = child
            if valid:
                return {
                    "type": "OR",
                    "action": action,
                    "belief": _belief_payload(belief),
                    "predicted_belief": _belief_payload(predicted),
                    "observation_branches": branches,
                }
        return None

    policy = or_search(initial_belief, max_depth, frozenset())
    success = policy is not None
    return BeliefSearchOutcome(
        success=success,
        termination_reason="model_success" if success else stopped or "depth_limit",
        trace=trace,
        nodes_expanded=expanded,
        nodes_generated=generated,
        reached_size=len(seen_beliefs),
        evidence={
            "initial_belief": _belief_payload(initial_belief),
            "policy": policy,
            "sensor": "blank position and tiles adjacent to the blank",
        },
    )
