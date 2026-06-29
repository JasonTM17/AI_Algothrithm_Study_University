"""Streamlit surface for two independent Group 6 decision-policy lanes."""

from __future__ import annotations

from html import escape
import json

import pandas as pd
import streamlit as st

from core.group6_decision_lab import GROUP6_LAB_ALGORITHMS
from core.group6_policy_comparison import (
    Group6PolicyComparison,
    Group6PolicyLane,
    Group6PolicySettings,
    advance_policy_comparison,
    create_policy_comparison,
)
from core.heuristics import get_heuristic
from ui.components import render_image_board, render_puzzle_board
from ui.group6_policy_evidence import (
    comparison_rows,
    render_last_decision_evidence,
    turn_evidence_rows,
)


POLICY_STATE_KEYS = (
    "group6_policy_comparison",
    "group6_policy_auto",
    "group6_policy_view_turn",
)


def _tx(t, key: str, fallback: str, **kwargs) -> str:
    try:
        value = t(key, **kwargs)
    except Exception:
        value = key
    return fallback.format(**kwargs) if value == key else value


def clear_group6_policy_state() -> None:
    for key in POLICY_STATE_KEYS:
        st.session_state.pop(key, None)


def group6_policy_needs_tick() -> bool:
    return bool(st.session_state.get("group6_policy_auto"))


def advance_group6_policy_tick() -> None:
    if not st.session_state.get("group6_policy_auto"):
        return
    comparison: Group6PolicyComparison | None = st.session_state.get(
        "group6_policy_comparison"
    )
    if comparison is None or comparison.complete:
        st.session_state.group6_policy_auto = False
        return
    advance_policy_comparison(comparison)
    st.session_state.group6_policy_view_turn = comparison.turn
    if comparison.complete:
        st.session_state.group6_policy_auto = False


def _settings_from_state() -> Group6PolicySettings:
    return Group6PolicySettings(
        depth=int(st.session_state.get("group6_policy_depth", 3)),
        per_decision_timeout=float(
            st.session_state.get("group6_policy_timeout", 1.0)
        ),
        total_budget=float(st.session_state.get("group6_policy_budget", 20.0)),
        max_turns=int(st.session_state.get("group6_policy_max_turns", 30)),
        action_order=str(st.session_state.get("group6_policy_action_order", "LRUD")),
        success_probability=float(
            st.session_state.get("group6_policy_probability", 0.8)
        ),
        base_seed=int(st.session_state.get("group6_policy_seed", 42)),
    )


def _reset_for_control_change() -> None:
    clear_group6_policy_state()


def _new_comparison(
    start: tuple[int, ...],
    goal: tuple[int, ...],
) -> Group6PolicyComparison:
    comparison = create_policy_comparison(
        start=start,
        goal=goal,
        algorithm_a=str(st.session_state.get("group6_policy_algorithm_a", "Minimax")),
        algorithm_b=str(
            st.session_state.get(
                "group6_policy_algorithm_b",
                "Alpha-Beta Pruning",
            )
        ),
        settings=_settings_from_state(),
    )
    st.session_state.group6_policy_comparison = comparison
    st.session_state.group6_policy_view_turn = 0
    return comparison


def _state_at_turn(lane: Group6PolicyLane, turn: int) -> tuple[int, ...]:
    return lane.history[min(max(0, turn), len(lane.history) - 1)]


def _render_lane_board(
    t,
    lane_label: str,
    lane: Group6PolicyLane,
    state: tuple[int, ...],
    *,
    goal: tuple[int, ...],
    image_tiles: dict,
    key_prefix: str,
) -> None:
    st.markdown(f"#### {escape(lane_label)}")
    st.caption(f"{lane.algorithm} | status={lane.status}")
    if image_tiles:
        render_image_board(
            state,
            image_tiles,
            key_prefix=key_prefix,
            highlight_correct=True,
            on_click_fn=None,
            show_numbers=False,
            goal=goal,
        )
    else:
        render_puzzle_board(state, highlight_correct=True, goal=goal)
        st.caption(_tx(t, "group6_policy_image_hint", "Tải hoặc chọn ảnh mẫu để xem hai policy bằng puzzle ảnh."))


def _render_lane_metrics(
    t,
    lane: Group6PolicyLane,
    *,
    goal: tuple[int, ...],
) -> None:
    h_fn = get_heuristic("Manhattan Distance", goal)
    cols = st.columns(3)
    cols[0].metric(_tx(t, "group6_policy_turns", "Lượt"), len(lane.turns))
    cols[1].metric(
        _tx(t, "group6_policy_runtime_total", "Runtime tích lũy"),
        f"{lane.cumulative_runtime:.6f}s",
    )
    cols[2].metric(
        _tx(t, "group6_final_manhattan", "Final Manhattan"),
        f"{h_fn(lane.current_state):.1f}",
    )
    cols = st.columns(3)
    cols[0].metric(
        _tx(t, "group6_expanded", "Expanded"),
        lane.cumulative_expanded,
    )
    cols[1].metric(
        _tx(t, "group6_generated", "Generated"),
        lane.cumulative_generated,
    )
    cols[2].metric(
        _tx(t, "group6_pruned", "Pruned"),
        lane.cumulative_pruned,
    )
    render_last_decision_evidence(t, lane)


def _render_history_chart(t, comparison: Group6PolicyComparison) -> None:
    rows = []
    for label, lane in (("A", comparison.lane_a), ("B", comparison.lane_b)):
        runtime = 0.0
        for item in lane.turns:
            runtime += item.runtime
            rows.append(
                {
                    "Lane": f"{label} - {lane.algorithm}",
                    "Turn": item.turn,
                    "Cumulative runtime (s)": runtime,
                    "Manhattan": item.final_manhattan,
                    "Expanded": item.nodes_expanded,
                    "Generated": item.nodes_generated,
                }
            )
    if not rows:
        return
    frame = pd.DataFrame(rows)
    if frame["Turn"].nunique() < 2:
        st.caption(
            _tx(
                t,
                "group6_chart_waiting",
                "Chart appears after at least two recorded turns.",
            )
        )
        return
    charts = st.columns(2)
    with charts[0]:
        st.markdown(f"**{_tx(t, 'group6_policy_runtime_chart', 'Runtime tích lũy theo lượt')}**")
        st.line_chart(
            frame,
            x="Turn",
            y="Cumulative runtime (s)",
            color="Lane",
        )
    with charts[1]:
        st.markdown(f"**{_tx(t, 'group6_policy_manhattan_chart', 'Manhattan theo lượt')}**")
        st.line_chart(frame, x="Turn", y="Manhattan", color="Lane")


def render_group6_policy_comparison(
    t,
    *,
    start: tuple[int, ...],
    goal: tuple[int, ...],
    image_tiles: dict,
) -> None:
    """Render selectors, two always-visible boards, controls, and evidence."""
    st.warning(
        _tx(
            t,
            "group6_policy_guardrail",
            "Hai policy chạy trên hai bản sao độc lập của cùng puzzle; đây không phải game hai người cùng tác động lên một board.",
        )
    )
    st.caption(
        _tx(
            t,
            "group6_policy_metric_note",
            "Root value is the depth-limited decision utility. Runtime is empirical per decision, not an optimal solver certificate.",
        )
    )
    st.info(
        _tx(
            t,
            "group6_policy_independent_note",
            "This screen does not run adversarial algorithms against each other. Lane A and lane B each receive a cloned puzzle; use Robustness Game Variant for the MAX/MIN worst-case environment.",
        )
    )
    selectors = st.columns(2)
    with selectors[0]:
        st.selectbox(
            _tx(t, "group6_policy_a", "Policy A (independent copy)"),
            GROUP6_LAB_ALGORITHMS,
            index=0,
            key="group6_policy_algorithm_a",
            on_change=_reset_for_control_change,
        )
    with selectors[1]:
        st.selectbox(
            _tx(t, "group6_policy_b", "Policy B (independent copy)"),
            GROUP6_LAB_ALGORITHMS,
            index=1,
            key="group6_policy_algorithm_b",
            on_change=_reset_for_control_change,
        )

    with st.expander(
        _tx(t, "group6_policy_settings", "Cấu hình chung"),
        expanded=False,
    ):
        row = st.columns(4)
        row[0].number_input(
            _tx(t, "group6_depth", "Độ sâu / ply"),
            1,
            8,
            3,
            key="group6_policy_depth",
            on_change=_reset_for_control_change,
        )
        row[1].number_input(
            _tx(t, "group6_policy_timeout", "Timeout mỗi quyết định"),
            0.1,
            10.0,
            1.0,
            0.1,
            key="group6_policy_timeout",
            on_change=_reset_for_control_change,
        )
        row[2].number_input(
            _tx(t, "group6_policy_max_turns", "Giới hạn lượt"),
            1,
            100,
            30,
            key="group6_policy_max_turns",
            on_change=_reset_for_control_change,
        )
        row[3].number_input(
            _tx(t, "group6_policy_budget", "Tổng budget (giây)"),
            1.0,
            120.0,
            20.0,
            1.0,
            key="group6_policy_budget",
            on_change=_reset_for_control_change,
        )
        row = st.columns(3)
        row[0].selectbox(
            _tx(t, "group6_action_order", "Thứ tự action"),
            ("LRUD", "UDLR", "RLDU", "DURL"),
            key="group6_policy_action_order",
            on_change=_reset_for_control_change,
        )
        row[1].number_input(
            _tx(t, "group6_seed", "Seed"),
            0,
            2**31 - 1,
            42,
            key="group6_policy_seed",
            on_change=_reset_for_control_change,
        )
        row[2].slider(
            _tx(t, "group6_probability", "P intended action"),
            0.0,
            1.0,
            0.8,
            0.05,
            key="group6_policy_probability",
            on_change=_reset_for_control_change,
        )

    comparison: Group6PolicyComparison | None = st.session_state.get(
        "group6_policy_comparison"
    )
    if comparison is None:
        comparison = _new_comparison(start, goal)

    max_view_turn = comparison.turn
    view_turn = min(
        int(st.session_state.get("group6_policy_view_turn", max_view_turn)),
        max_view_turn,
    )
    board_columns = st.columns(2, gap="large")
    with board_columns[0]:
        _render_lane_board(
            t,
            _tx(t, "group6_policy_lane_a_title", "Policy A / independent copy"),
            comparison.lane_a,
            _state_at_turn(comparison.lane_a, view_turn),
            goal=goal,
            image_tiles=image_tiles,
            key_prefix="group6_policy_a_board",
        )
        _render_lane_metrics(t, comparison.lane_a, goal=goal)
    with board_columns[1]:
        _render_lane_board(
            t,
            _tx(t, "group6_policy_lane_b_title", "Policy B / independent copy"),
            comparison.lane_b,
            _state_at_turn(comparison.lane_b, view_turn),
            goal=goal,
            image_tiles=image_tiles,
            key_prefix="group6_policy_b_board",
        )
        _render_lane_metrics(t, comparison.lane_b, goal=goal)

    controls = st.columns(5)
    if controls[0].button(
        _tx(t, "group6_policy_start", "Bắt đầu lại"),
        key="btn_group6_policy_start",
        width="stretch",
    ):
        comparison = _new_comparison(start, goal)
        st.session_state.group6_policy_auto = False
        st.rerun()
    if controls[1].button(
        _tx(t, "play_next_step", "Bước tiếp"),
        key="btn_group6_policy_next",
        disabled=comparison.complete,
        width="stretch",
    ):
        advance_policy_comparison(comparison)
        st.session_state.group6_policy_view_turn = comparison.turn
        st.rerun()
    if controls[2].button(
        _tx(t, "play_auto_run", "Chạy tự động"),
        key="btn_group6_policy_auto",
        disabled=comparison.complete,
        width="stretch",
    ):
        comparison.running = True
        st.session_state.group6_policy_auto = True
        st.rerun()
    if controls[3].button(
        _tx(t, "play_stop_run", "Dừng"),
        key="btn_group6_policy_stop",
        disabled=not st.session_state.get("group6_policy_auto", False),
        width="stretch",
    ):
        comparison.running = False
        st.session_state.group6_policy_auto = False
        st.rerun()
    if controls[4].button(
        _tx(t, "play_reset", "Đặt lại"),
        key="btn_group6_policy_reset",
        width="stretch",
    ):
        clear_group6_policy_state()
        st.rerun()

    if max_view_turn == 0:
        st.caption(
            f"{_tx(t, 'group6_policy_timeline', 'Lượt đang xem')}: 0/0"
        )
    else:
        selected_turn = st.slider(
            _tx(t, "group6_policy_timeline", "Lượt đang xem"),
            0,
            max_view_turn,
            view_turn,
            key=f"group6_policy_timeline_{max_view_turn}",
        )
        if selected_turn != view_turn:
            st.session_state.group6_policy_view_turn = selected_turn
            st.rerun()

    if comparison.winner:
        st.success(f"Policy {comparison.winner} tới goal trước.")
    elif comparison.complete:
        st.info(_tx(t, "group6_policy_no_winner", "Hai lane đã dừng nhưng chưa có policy nào tới goal."))
    st.dataframe(
        pd.DataFrame(comparison_rows(comparison)),
        hide_index=True,
        width="stretch",
    )
    st.markdown(
        f"**{_tx(t, 'group6_policy_turn_evidence', 'Per-turn policy evidence')}**"
    )
    turn_rows = turn_evidence_rows(comparison)
    if turn_rows:
        st.dataframe(
            pd.DataFrame(turn_rows),
            hide_index=True,
            width="stretch",
        )
    else:
        st.caption(
            _tx(
                t,
                "group6_policy_turn_evidence_empty",
                "Press Next to record per-turn root value, runtime, action and termination evidence.",
            )
        )
    _render_history_chart(t, comparison)
    st.download_button(
        _tx(t, "group6_policy_export", "Tải evidence JSON"),
        data=json.dumps(
            comparison.export_summary(),
            ensure_ascii=False,
            indent=2,
        ).encode("utf-8"),
        file_name="group6-policy-comparison.json",
        mime="application/json",
        key="btn_group6_policy_export",
    )
