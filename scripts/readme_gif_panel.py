"""Algorithm-specific evidence shown in README GIF side panels."""

from __future__ import annotations

import re
from dataclasses import dataclass

from core.heuristics import manhattan_distance
from core.puzzle import PuzzleState
from scripts.readme_gif_runner import DemoEvidence


@dataclass(frozen=True)
class PanelContent:
    metrics: tuple[tuple[str, str, str], ...]
    selection: str
    explanation: str


def panel_content(evidence: DemoEvidence, frame_index: int) -> PanelContent:
    spec = evidence.spec
    state = evidence.states[frame_index]
    step = evidence.state_indices[min(frame_index, len(evidence.state_indices) - 1)]
    reason = _trace_reason(evidence, frame_index)
    previous, next_action = _actions(evidence, step)

    if spec.group == "Uninformed Search":
        result = evidence.result
        return PanelContent(
            metrics=(
                ("STEP", str(step), "teal"),
                ("FRONTIER", str(result.max_frontier_size if result else 0), "blue"),
                ("REACHED", str(result.reached_size if result else 0), "gold"),
                ("EXPANDED", str(result.nodes_expanded if result else 0), "text"),
            ),
            selection=f"{previous} -> {next_action}",
            explanation=reason,
        )

    if spec.group == "Informed Search":
        h = manhattan_distance(state, spec.goal)
        result = evidence.result
        return PanelContent(
            metrics=(
                ("G(N)", str(step), "teal"),
                ("H(N)", f"{h:g}", "gold"),
                ("F(N)", f"{step + h:g}", "blue"),
                ("EXPANDED", str(result.nodes_expanded if result else 0), "text"),
            ),
            selection=f"{previous} -> {next_action}",
            explanation=(
                f"{reason} Frontier max={result.max_frontier_size if result else 0}; "
                f"reached={result.reached_size if result else 0}."
            ),
        )

    if spec.group == "Local Search":
        h = manhattan_distance(state, spec.goal)
        candidates = len(PuzzleState(state).get_neighbors())
        return PanelContent(
            metrics=(
                ("ITERATION", str(step), "teal"),
                ("CURRENT H", f"{h:g}", "gold"),
                ("CANDIDATES", str(candidates), "blue"),
                ("STATUS", _short_status(evidence.termination), "text"),
            ),
            selection=f"candidate: {previous} -> {next_action}",
            explanation=reason,
        )

    if spec.group == "Complex Environments":
        return _complex_content(evidence, step, state, reason, previous, next_action)

    if spec.group == "CSP":
        return _csp_content(evidence, step, reason)

    return _game_content(evidence, step, state, reason, previous, next_action)


def _complex_content(evidence, step, state, reason, previous, next_action) -> PanelContent:
    spec = evidence.spec
    result = evidence.result
    if spec.algorithm == "AND-OR Search":
        support = "intended" if float(spec.params.get("nondet_prob", 0.0)) <= 0 else "deflect"
        return PanelContent(
            metrics=(
                ("DEPTH", str(spec.params.get("max_depth", "-")), "teal"),
                ("OUTCOMES", support, "gold"),
                ("OUTPUT", "policy", "blue"),
                ("EXPANDED", str(result.nodes_expanded if result else 0), "text"),
            ),
            selection="AND node requires every supported outcome",
            explanation=reason,
        )
    if spec.algorithm == "LRTA*":
        h = manhattan_distance(state, spec.goal)
        update = _extract(r"h_old=([\d.]+), h_new=([\d.]+)", reason, "local H update")
        visited = _extract(r"visited=(\d+)", reason, str(result.reached_size if result else 0))
        return PanelContent(
            metrics=(
                ("ONLINE STEP", str(step), "teal"),
                ("H(N)", f"{h:g}", "gold"),
                ("VISITED", visited, "blue"),
                ("CAP", str(spec.params.get("max_steps", "-")), "text"),
            ),
            selection=f"{previous} -> {next_action}",
            explanation=f"H update: {update}. {reason}",
        )

    belief = _extract(r"belief=(\d+)", reason, "-")
    fallback = "yes" if "fallback_reason=" in reason and "fallback_reason=none" not in reason else "no"
    planner = str(spec.params.get("planner", "A* Search")).replace(" Search", "")
    return PanelContent(
        metrics=(
            ("STEP", str(step), "teal"),
            ("BELIEF", belief, "blue"),
            ("PLANNER", planner[:8], "gold"),
            ("FALLBACK", fallback, "red" if fallback == "yes" else "text"),
        ),
        selection=f"belief vote: {previous} -> {next_action}",
        explanation=reason,
    )


def _csp_content(evidence, step, reason) -> PanelContent:
    spec = evidence.spec
    result = evidence.result
    facts = " | ".join(evidence.facts)
    variables = _extract(r"(\d+) variables", facts, "-")
    constraints = _extract(r"(\d+) constraints", facts, "-")
    domain = _extract(r"domain [^ ]+ has (\d+)", reason, "-")
    horizon = str(spec.params.get("time_horizon", _extract(r"T=(\d+)", facts, "bounded")))
    return PanelContent(
        metrics=(
            ("HORIZON", horizon, "teal"),
            ("VARIABLES", variables, "blue"),
            ("DOMAIN", domain, "gold"),
            ("EXPANDED", str(result.nodes_expanded if result else 0), "text"),
        ),
        selection=f"constraint evidence at step {step}",
        explanation=f"{reason} Constraints={constraints}; termination={evidence.termination}.",
    )


def _game_content(evidence, step, state, reason, previous, next_action) -> PanelContent:
    spec = evidence.spec
    result = evidence.result
    if spec.algorithm == "AI-vs-AI Tournament":
        score_a = _extract(r"A\*: (\d+) pts", " | ".join(evidence.facts), "-")
        score_b = _extract(r"Greedy: (\d+) pts", " | ".join(evidence.facts), "-")
        winner = _extract(r"winner=([^|]+)", " | ".join(evidence.facts), "-").strip()
        return PanelContent(
            metrics=(
                ("A* SCORE", score_a, "teal"),
                ("GREEDY", score_b, "gold"),
                ("WINNER", winner[:8], "blue"),
                ("ROUNDS", "1", "text"),
            ),
            selection="Same start, goal and A* reference",
            explanation=reason,
        )

    role = "CHANCE" if "CHANCE" in reason else "MIN" if "MIN" in reason else "MAX"
    utility = _extract(r"utility=([-\d.]+)", reason, "-")
    pruned = sum(
        1 for trace_step in (result.trace if result else ())
        if "prun" in (trace_step.reason or "").lower() or "cutoff" in (trace_step.reason or "").lower()
    )
    h = manhattan_distance(state, spec.goal)
    return PanelContent(
        metrics=(
            ("NODE", role, "teal"),
            ("UTILITY", utility, "gold"),
            ("H(N)", f"{h:g}", "blue"),
            ("PRUNED", str(pruned), "red" if pruned else "text"),
        ),
        selection=f"root choice: {previous} -> {next_action}",
        explanation=reason,
    )


def _trace_reason(evidence: DemoEvidence, frame_index: int) -> str:
    trace = evidence.result.trace if evidence.result else []
    if trace:
        denominator = max(len(evidence.states) - 1, 1)
        index = round(frame_index * (len(trace) - 1) / denominator)
        return (trace[index].reason or trace[index].event or evidence.spec.evidence)[:180]
    return evidence.facts[min(frame_index, len(evidence.facts) - 1)][:180]


def _actions(evidence: DemoEvidence, step: int) -> tuple[str, str]:
    previous = "Initialize" if step == 0 or not evidence.actions else evidence.actions[min(step - 1, len(evidence.actions) - 1)]
    next_action = "Goal" if step >= len(evidence.actions) else evidence.actions[step]
    return previous, next_action


def _extract(pattern: str, text: str, default: str) -> str:
    match = re.search(pattern, text, flags=re.IGNORECASE)
    if not match:
        return default
    return "/".join(group for group in match.groups() if group is not None)


def _short_status(value: str) -> str:
    return value.replace("resource_limit", "limit").replace("model_success", "model")[:8]
