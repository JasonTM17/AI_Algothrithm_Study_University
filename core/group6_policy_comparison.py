"""Two-lane receding-horizon comparison for the Group 6 decision policies."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field, replace
import hashlib
import json

from core.group6_decision_lab import (
    GROUP6_LAB_ALGORITHMS,
    Group6LabResult,
    Group6LabSettings,
    run_group6_algorithm,
)
from core.heuristics import get_heuristic
from core.puzzle import _move_blank


State = tuple[int, ...]
TERMINAL_STATUSES = {
    "goal",
    "cycle",
    "timeout",
    "no_action",
    "invalid_transition",
    "turn_limit",
    "total_budget",
}


@dataclass(frozen=True)
class Group6PolicySettings:
    """Shared comparison settings for both independent policy lanes."""

    depth: int = 3
    per_decision_timeout: float = 1.0
    total_budget: float = 20.0
    max_turns: int = 30
    heuristic: str = "Manhattan Distance"
    action_order: str = "LRUD"
    success_probability: float = 0.8
    base_seed: int = 42

    def validate(self) -> None:
        Group6LabSettings(
            depth=self.depth,
            timeout=self.per_decision_timeout,
            heuristic=self.heuristic,
            action_order=self.action_order,
            success_probability=self.success_probability,
            seed=self.base_seed,
        ).validate()
        if self.total_budget <= 0:
            raise ValueError("total_budget must be positive")
        if self.max_turns < 1:
            raise ValueError("max_turns must be positive")


@dataclass(frozen=True)
class Group6PolicyTurn:
    """One applied root decision for a policy lane."""

    turn: int
    before_state: State
    after_state: State
    intended_action: str
    realized_action: str
    root_value: float | None
    runtime: float
    nodes_expanded: int
    nodes_generated: int
    pruned: int
    final_manhattan: float
    probability: float | None
    termination: str


@dataclass
class Group6PolicyLane:
    """Mutable accumulated state for one independently acting policy."""

    algorithm: str
    current_state: State
    history: list[State]
    turns: list[Group6PolicyTurn] = field(default_factory=list)
    status: str = "ready"
    cumulative_runtime: float = 0.0
    cumulative_expanded: int = 0
    cumulative_generated: int = 0
    cumulative_pruned: int = 0
    goal_turn: int | None = None
    last_decision: Group6LabResult | None = None

    @property
    def active(self) -> bool:
        return self.status not in TERMINAL_STATUSES


@dataclass
class Group6PolicyComparison:
    """Complete two-lane comparison state stored by the Streamlit session."""

    start: State
    goal: State
    settings: Group6PolicySettings
    lane_a: Group6PolicyLane
    lane_b: Group6PolicyLane
    fingerprint: str
    turn: int = 0
    winner: str | None = None
    running: bool = False

    @property
    def complete(self) -> bool:
        return not self.lane_a.active and not self.lane_b.active

    def export_summary(self) -> dict[str, object]:
        def lane_payload(lane: Group6PolicyLane) -> dict[str, object]:
            return {
                "algorithm": lane.algorithm,
                "status": lane.status,
                "goal_turn": lane.goal_turn,
                "cumulative_runtime": lane.cumulative_runtime,
                "cumulative_expanded": lane.cumulative_expanded,
                "cumulative_generated": lane.cumulative_generated,
                "cumulative_pruned": lane.cumulative_pruned,
                "history": [list(state) for state in lane.history],
                "turns": [
                    {
                        **asdict(item),
                        "before_state": list(item.before_state),
                        "after_state": list(item.after_state),
                    }
                    for item in lane.turns
                ],
            }

        return {
            "fingerprint": self.fingerprint,
            "start": list(self.start),
            "goal": list(self.goal),
            "settings": asdict(self.settings),
            "turn": self.turn,
            "winner": self.winner,
            "lane_a": lane_payload(self.lane_a),
            "lane_b": lane_payload(self.lane_b),
        }


def _fingerprint(
    start: State,
    goal: State,
    settings: Group6PolicySettings,
) -> str:
    payload = {
        "start": list(start),
        "goal": list(goal),
        "settings": asdict(settings),
        "seed_schedule": "base_seed + turn_index",
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()[:16]


def create_policy_comparison(
    *,
    start: State,
    goal: State,
    algorithm_a: str = "Minimax",
    algorithm_b: str = "Alpha-Beta Pruning",
    settings: Group6PolicySettings | None = None,
) -> Group6PolicyComparison:
    """Create two lanes at the same immutable baseline."""
    if algorithm_a not in GROUP6_LAB_ALGORITHMS:
        raise ValueError(f"Unsupported Group 6 algorithm: {algorithm_a}")
    if algorithm_b not in GROUP6_LAB_ALGORITHMS:
        raise ValueError(f"Unsupported Group 6 algorithm: {algorithm_b}")
    settings = settings or Group6PolicySettings()
    settings.validate()
    start = tuple(start)
    goal = tuple(goal)
    initial_status = "goal" if start == goal else "ready"
    return Group6PolicyComparison(
        start=start,
        goal=goal,
        settings=settings,
        lane_a=Group6PolicyLane(
            algorithm=algorithm_a,
            current_state=start,
            history=[start],
            status=initial_status,
            goal_turn=0 if start == goal else None,
        ),
        lane_b=Group6PolicyLane(
            algorithm=algorithm_b,
            current_state=start,
            history=[start],
            status=initial_status,
            goal_turn=0 if start == goal else None,
        ),
        fingerprint=_fingerprint(start, goal, settings),
    )


def _lab_settings(
    settings: Group6PolicySettings,
    turn: int,
) -> Group6LabSettings:
    return Group6LabSettings(
        depth=settings.depth,
        timeout=settings.per_decision_timeout,
        heuristic=settings.heuristic,
        action_order=settings.action_order,
        success_probability=settings.success_probability,
        seed=settings.base_seed + turn,
    )


def _advance_lane(
    lane: Group6PolicyLane,
    *,
    goal: State,
    settings: Group6PolicySettings,
    turn: int,
) -> None:
    if not lane.active:
        return
    if len(lane.turns) >= settings.max_turns:
        lane.status = "turn_limit"
        return

    decision = run_group6_algorithm(
        lane.algorithm,
        start=lane.current_state,
        goal=goal,
        settings=_lab_settings(settings, turn),
    )
    lane.last_decision = decision
    lane.cumulative_runtime += float(decision.result.runtime)
    lane.cumulative_expanded += int(decision.result.nodes_expanded)
    lane.cumulative_generated += int(decision.result.nodes_generated)
    lane.cumulative_pruned += int(decision.prune_count)

    if decision.timed_out:
        lane.status = "timeout"
        return
    if not decision.result.actions:
        lane.status = "no_action"
        return

    intended = decision.result.actions[0]
    realized = intended
    probability: float | None = None
    if decision.frames:
        frame = decision.frames[0]
        intended = frame.intended_action or intended
        realized = frame.realized_action or frame.action or intended
        probability = frame.probability

    next_state = _move_blank(lane.current_state, realized)
    if next_state is None:
        lane.status = "invalid_transition"
        return
    before = lane.current_state
    h_fn = get_heuristic(settings.heuristic, goal)
    lane.current_state = next_state
    lane.history.append(next_state)
    lane.turns.append(
        Group6PolicyTurn(
            turn=turn,
            before_state=before,
            after_state=next_state,
            intended_action=intended,
            realized_action=realized,
            root_value=decision.root_value,
            runtime=float(decision.result.runtime),
            nodes_expanded=int(decision.result.nodes_expanded),
            nodes_generated=int(decision.result.nodes_generated),
            pruned=int(decision.prune_count),
            final_manhattan=float(h_fn(next_state)),
            probability=probability,
            termination="applied",
        )
    )
    if next_state == goal:
        lane.status = "goal"
        lane.goal_turn = turn
    elif next_state in lane.history[:-1]:
        lane.status = "cycle"
    else:
        lane.status = "running"


def _update_winner(comparison: Group6PolicyComparison) -> None:
    candidates = [
        (lane.goal_turn, lane.cumulative_runtime, label)
        for label, lane in (("A", comparison.lane_a), ("B", comparison.lane_b))
        if lane.goal_turn is not None
    ]
    if not candidates:
        comparison.winner = None
        return
    candidates.sort(key=lambda item: (item[0], item[1], item[2]))
    comparison.winner = candidates[0][2]


def advance_policy_comparison(
    comparison: Group6PolicyComparison,
) -> Group6PolicyComparison:
    """Advance each active lane by at most one verified root action."""
    comparison.settings.validate()
    if comparison.complete:
        comparison.running = False
        return comparison

    comparison.turn += 1
    order = (
        (comparison.lane_a, comparison.lane_b)
        if comparison.turn % 2
        else (comparison.lane_b, comparison.lane_a)
    )
    for lane in order:
        _advance_lane(
            lane,
            goal=comparison.goal,
            settings=comparison.settings,
            turn=comparison.turn,
        )

    total_runtime = (
        comparison.lane_a.cumulative_runtime
        + comparison.lane_b.cumulative_runtime
    )
    if total_runtime >= comparison.settings.total_budget:
        for lane in (comparison.lane_a, comparison.lane_b):
            if lane.active:
                lane.status = "total_budget"
    _update_winner(comparison)
    comparison.running = comparison.running and not comparison.complete
    return comparison

