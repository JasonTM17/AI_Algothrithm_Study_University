"""Structured runner for the Play page Group 6 decision lab."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import hashlib
import json
import math
from typing import Callable

from algorithms.adversarial import alpha_beta_pruning, expectimax, minimax
from core.heuristics import get_heuristic
from core.metrics import SearchResult, TraceStep


GROUP6_LAB_ALGORITHMS = (
    "Minimax",
    "Alpha-Beta Pruning",
    "Expectimax",
)

_RUNNERS: dict[str, Callable[..., SearchResult]] = {
    "Minimax": minimax,
    "Alpha-Beta Pruning": alpha_beta_pruning,
    "Expectimax": expectimax,
}

_ROLE_EVENTS = {"select_action", "worst_case", "chance_outcome"}


@dataclass(frozen=True)
class Group6LabSettings:
    """Comparable settings shared by Group 6 decision models."""

    depth: int = 3
    timeout: float = 5.0
    heuristic: str = "Manhattan Distance"
    action_order: str = "LRUD"
    success_probability: float = 0.8
    seed: int = 42

    def validate(self) -> None:
        if not 1 <= self.depth <= 8:
            raise ValueError("depth must be between 1 and 8")
        if self.timeout <= 0:
            raise ValueError("timeout must be positive")
        if not 0.0 <= self.success_probability <= 1.0:
            raise ValueError("success_probability must be between 0 and 1")
        if sorted(self.action_order) != ["D", "L", "R", "U"]:
            raise ValueError("action_order must contain L, R, U and D exactly once")


@dataclass(frozen=True)
class Group6RoleFrame:
    """One exact edge of the selected game-tree variation."""

    index: int
    role: str
    before_state: tuple[int, ...]
    after_state: tuple[int, ...]
    action: str
    intended_action: str
    realized_action: str
    utility: float | None = None
    alpha: float | None = None
    beta: float | None = None
    probability: float | None = None
    reason: str = ""
    repeated_state: bool = False


@dataclass
class Group6LabResult:
    """A SearchResult plus role frames and decision-model evidence."""

    algorithm: str
    result: SearchResult
    settings: Group6LabSettings
    baseline_fingerprint: str
    run_fingerprint: str
    frames: list[Group6RoleFrame] = field(default_factory=list)
    root_value: float | None = None
    completed_depth: int = 0
    prune_count: int = 0
    captured_trace_nodes: int = 0
    final_manhattan: float = 0.0
    empirical_branching_factor: float = 0.0

    @property
    def timed_out(self) -> bool:
        return self.result.termination_reason == "timeout"

    @property
    def space_proxy(self) -> dict[str, int]:
        return {
            "generated_nodes": int(self.result.nodes_generated),
            "captured_trace_events": int(len(self.result.trace)),
            "captured_tree_nodes": int(self.captured_trace_nodes),
            "maximum_depth": int(self.completed_depth),
            "pruned_branches": int(self.prune_count),
        }

    def export_summary(self) -> dict[str, object]:
        """Return JSON-safe evidence without image or uploaded-file content."""
        return {
            "algorithm": self.algorithm,
            "settings": asdict(self.settings),
            "baseline_fingerprint": self.baseline_fingerprint,
            "run_fingerprint": self.run_fingerprint,
            "root_value": self.root_value,
            "completed_depth": self.completed_depth,
            "prune_count": self.prune_count,
            "captured_trace_nodes": self.captured_trace_nodes,
            "final_manhattan": self.final_manhattan,
            "empirical_branching_factor": self.empirical_branching_factor,
            "runtime_seconds": float(self.result.runtime),
            "nodes_expanded": int(self.result.nodes_expanded),
            "nodes_generated": int(self.result.nodes_generated),
            "variation_plies": len(self.frames),
            "path_verified": bool(self.result.path_verified),
            "goal_reached": bool(self.result.goal_reached),
            "optimality_proven": bool(self.result.optimality_proven),
            "termination_reason": self.result.termination_reason,
            "space_proxy": self.space_proxy,
            "frames": [
                {
                    **asdict(frame),
                    "before_state": list(frame.before_state),
                    "after_state": list(frame.after_state),
                }
                for frame in self.frames
            ],
        }


def _fingerprint(payload: dict[str, object]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()[:16]


def _baseline_payload(
    start: tuple[int, ...],
    goal: tuple[int, ...],
    settings: Group6LabSettings,
) -> dict[str, object]:
    return {
        "start": list(start),
        "goal": list(goal),
        "depth": settings.depth,
        "timeout": settings.timeout,
        "heuristic": settings.heuristic,
        "action_order": settings.action_order,
        "success_probability": settings.success_probability,
        "seed": settings.seed,
    }


def _root_value(trace: list[TraceStep]) -> float | None:
    root = next(
        (step for step in reversed(trace) if step.event == "root_summary"),
        None,
    )
    return None if root is None or root.utility is None else float(root.utility)


def _role_frames(trace: list[TraceStep]) -> list[Group6RoleFrame]:
    frames: list[Group6RoleFrame] = []
    seen: set[tuple[int, ...]] = set()
    for step in trace:
        if step.event not in _ROLE_EVENTS or step.node_state is None or not step.action:
            continue
        before = tuple(step.node_state)
        after = tuple(step.state)
        if not seen:
            seen.add(before)
        repeated = after in seen
        seen.add(after)
        frames.append(
            Group6RoleFrame(
                index=len(frames) + 1,
                role=step.node_type or "MAX",
                before_state=before,
                after_state=after,
                action=step.action,
                intended_action=step.intended_action or step.action,
                realized_action=step.realized_action or step.action,
                utility=None if step.utility is None else float(step.utility),
                alpha=step.alpha,
                beta=step.beta,
                probability=step.probability,
                reason=step.reason,
                repeated_state=repeated,
            )
        )
    return frames


def run_group6_algorithm(
    algorithm: str,
    *,
    start: tuple[int, ...],
    goal: tuple[int, ...],
    settings: Group6LabSettings | None = None,
) -> Group6LabResult:
    """Run one Group 6 model and preserve its decision semantics."""
    if algorithm not in _RUNNERS:
        raise ValueError(f"Unsupported Group 6 algorithm: {algorithm}")
    settings = settings or Group6LabSettings()
    settings.validate()

    kwargs = {
        "start": tuple(start),
        "goal": tuple(goal),
        "depth": int(settings.depth),
        "heuristic": settings.heuristic,
        "timeout": float(settings.timeout),
        "action_order": settings.action_order,
    }
    if algorithm == "Expectimax":
        kwargs["success_prob"] = float(settings.success_probability)
        kwargs["seed"] = int(settings.seed)

    result = _RUNNERS[algorithm](**kwargs)
    frames = _role_frames(result.trace)
    baseline_payload = _baseline_payload(tuple(start), tuple(goal), settings)
    run_payload = {**baseline_payload, "algorithm": algorithm}
    h_fn = get_heuristic(settings.heuristic, tuple(goal))
    final_state = result.path[-1] if result.path else tuple(start)
    selected_variation_depth = max((frame.index for frame in frames), default=0)
    completed_depth = (
        selected_variation_depth
        if result.termination_reason == "timeout"
        else int(settings.depth)
    )
    generated = max(1, int(result.nodes_generated))
    effective_depth = max(1, completed_depth or settings.depth)

    return Group6LabResult(
        algorithm=algorithm,
        result=result,
        settings=settings,
        baseline_fingerprint=_fingerprint(baseline_payload),
        run_fingerprint=_fingerprint(run_payload),
        frames=frames,
        root_value=_root_value(result.trace),
        completed_depth=completed_depth,
        prune_count=sum(1 for step in result.trace if step.event == "prune"),
        captured_trace_nodes=sum(
            1
            for step in result.trace
            if step.event
            in {
                "generate",
                "evaluate_action",
                "chance_outcome_evaluated",
                "prune",
            }
        ),
        final_manhattan=float(h_fn(final_state)),
        empirical_branching_factor=generated ** (1.0 / effective_depth),
    )


def compare_minimax_alpha_beta(
    minimax_result: Group6LabResult | None,
    alpha_beta_result: Group6LabResult | None,
    *,
    tolerance: float = 1e-9,
) -> bool | None:
    """Check the root-value invariant only for comparable completed runs."""
    if minimax_result is None or alpha_beta_result is None:
        return None
    if minimax_result.baseline_fingerprint != alpha_beta_result.baseline_fingerprint:
        return None
    if minimax_result.timed_out or alpha_beta_result.timed_out:
        return None
    if minimax_result.root_value is None or alpha_beta_result.root_value is None:
        return None
    return math.isclose(
        minimax_result.root_value,
        alpha_beta_result.root_value,
        rel_tol=tolerance,
        abs_tol=tolerance,
    )
