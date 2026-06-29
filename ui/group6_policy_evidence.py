"""Evidence render helpers for the Group 6 policy-comparison UI."""

from __future__ import annotations

import streamlit as st

from core.group6_policy_comparison import (
    Group6PolicyComparison,
    Group6PolicyLane,
    Group6PolicyTurn,
)


def _tx(t, key: str, fallback: str, **kwargs) -> str:
    try:
        value = t(key, **kwargs)
    except Exception:
        value = key
    return fallback.format(**kwargs) if value == key else value


def latest_turn(lane: Group6PolicyLane) -> Group6PolicyTurn | None:
    return lane.turns[-1] if lane.turns else None


def format_value(value: object, *, digits: int | None = None, suffix: str = "") -> str:
    if value is None:
        return "-"
    if isinstance(value, float):
        precision = 6 if digits is None else digits
        return f"{value:.{precision}f}{suffix}"
    return f"{value}{suffix}"


def format_action(turn: Group6PolicyTurn | None) -> str:
    if turn is None:
        return "-"
    return f"{turn.intended_action} → {turn.realized_action}"


def render_last_decision_evidence(
    t,
    lane: Group6PolicyLane,
) -> None:
    turn = latest_turn(lane)
    st.markdown(
        f"**{_tx(t, 'group6_policy_last_decision', 'Last decision evidence')}**"
    )
    if turn is None:
        st.caption(
            _tx(
                t,
                "group6_policy_no_decision",
                "No root decision has been applied in this lane yet.",
            )
        )
        return

    goal_reached = (
        _tx(t, "tc_yes", "Yes")
        if lane.goal_turn is not None
        else _tx(t, "tc_no", "No")
    )
    row = st.columns(3)
    row[0].metric(
        _tx(t, "group6_root_value", "Root value"),
        format_value(turn.root_value, digits=6),
    )
    row[1].metric(
        _tx(t, "group6_policy_turn_runtime", "Turn runtime"),
        format_value(turn.runtime, digits=6, suffix="s"),
    )
    row[2].metric(
        _tx(t, "group6_policy_last_action", "Last action"),
        format_action(turn),
    )
    row = st.columns(3)
    row[0].metric(
        _tx(t, "group6_policy_probability", "Probability"),
        format_value(turn.probability, digits=6),
    )
    row[1].metric(_tx(t, "group6_policy_stop_reason", "Stop reason"), lane.status)
    row[2].metric(
        _tx(t, "group6_policy_goal_reached", "Goal reached"),
        goal_reached,
    )


def comparison_rows(
    comparison: Group6PolicyComparison,
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for label, lane in (("A", comparison.lane_a), ("B", comparison.lane_b)):
        latest = latest_turn(lane)
        rows.append(
            {
                "Lane": label,
                "Algorithm": lane.algorithm,
                "Status": lane.status,
                "Turns": len(lane.turns),
                "Runtime (s)": lane.cumulative_runtime,
                "Expanded": lane.cumulative_expanded,
                "Generated": lane.cumulative_generated,
                "Pruned": lane.cumulative_pruned,
                "Goal turn": lane.goal_turn,
                "Goal reached": lane.goal_turn is not None,
                "Last root value": format_value(
                    None if latest is None else latest.root_value,
                    digits=6,
                ),
                "Last turn runtime (s)": format_value(
                    None if latest is None else latest.runtime,
                    digits=6,
                ),
                "Last action": format_action(latest),
                "Stop reason": lane.status,
            }
        )
    return rows


def turn_evidence_rows(
    comparison: Group6PolicyComparison,
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for label, lane in (("A", comparison.lane_a), ("B", comparison.lane_b)):
        for item in lane.turns:
            rows.append(
                {
                    "Lane": label,
                    "Algorithm": lane.algorithm,
                    "Turn": item.turn,
                    "Intended": item.intended_action,
                    "Realized": item.realized_action,
                    "Root value": format_value(item.root_value, digits=6),
                    "Turn runtime (s)": format_value(item.runtime, digits=6),
                    "Expanded": item.nodes_expanded,
                    "Generated": item.nodes_generated,
                    "Pruned": item.pruned,
                    "Final Manhattan": format_value(
                        item.final_manhattan,
                        digits=2,
                    ),
                    "Probability": format_value(item.probability, digits=6),
                    "Termination": item.termination,
                }
            )
    return rows
