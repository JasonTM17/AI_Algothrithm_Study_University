"""Streamlit surfaces for Group 6 robustness and chance lab variants."""

from __future__ import annotations

from html import escape
import json

import pandas as pd
import streamlit as st

from core.group6_variant_labs import (
    ROBUSTNESS_ALGORITHMS,
    Group6ChanceLab,
    Group6ChanceSettings,
    Group6RobustnessGame,
    Group6RobustnessSettings,
    advance_chance_lab,
    advance_robustness_game,
    create_chance_lab,
    create_robustness_game,
    run_chance_stability_sample,
)
from core.heuristics import get_heuristic
from ui.components import render_image_board, render_puzzle_board


VARIANT_STATE_KEYS = (
    "group6_robustness_game",
    "group6_robustness_auto",
    "group6_robustness_view_turn",
    "group6_chance_lab",
    "group6_chance_auto",
    "group6_chance_view_turn",
    "group6_chance_stability",
)


def _tx(t, key: str, fallback: str, **kwargs) -> str:
    try:
        value = t(key, **kwargs)
    except Exception:
        value = key
    return fallback.format(**kwargs) if value == key else value


def clear_group6_variant_lab_state() -> None:
    for key in VARIANT_STATE_KEYS:
        st.session_state.pop(key, None)


def group6_variant_needs_tick() -> bool:
    return bool(
        st.session_state.get("group6_robustness_auto")
        or st.session_state.get("group6_chance_auto")
    )


def advance_group6_variant_tick() -> None:
    game: Group6RobustnessGame | None = st.session_state.get("group6_robustness_game")
    if st.session_state.get("group6_robustness_auto") and game is not None:
        advance_robustness_game(game)
        st.session_state.group6_robustness_view_turn = len(game.frames)
        if not game.active:
            st.session_state.group6_robustness_auto = False

    lab: Group6ChanceLab | None = st.session_state.get("group6_chance_lab")
    if st.session_state.get("group6_chance_auto") and lab is not None:
        advance_chance_lab(lab)
        st.session_state.group6_chance_view_turn = len(lab.frames)
        if not lab.active:
            st.session_state.group6_chance_auto = False


def _reset_robustness() -> None:
    for key in ("group6_robustness_game", "group6_robustness_auto", "group6_robustness_view_turn"):
        st.session_state.pop(key, None)


def _reset_chance() -> None:
    for key in (
        "group6_chance_lab",
        "group6_chance_auto",
        "group6_chance_view_turn",
        "group6_chance_stability",
    ):
        st.session_state.pop(key, None)


def _robustness_settings_from_state() -> Group6RobustnessSettings:
    return Group6RobustnessSettings(
        algorithm=str(st.session_state.get("group6_robustness_algorithm", "Minimax")),
        depth=int(st.session_state.get("group6_robustness_depth", 3)),
        per_turn_timeout=float(st.session_state.get("group6_robustness_timeout", 1.0)),
        total_budget=float(st.session_state.get("group6_robustness_budget", 20.0)),
        max_turns=int(st.session_state.get("group6_robustness_max_turns", 30)),
        action_order=str(st.session_state.get("group6_robustness_action_order", "LRUD")),
        utility_penalty=float(st.session_state.get("group6_robustness_penalty", -1000.0)),
    )


def _chance_settings_from_state() -> Group6ChanceSettings:
    return Group6ChanceSettings(
        depth=int(st.session_state.get("group6_chance_depth", 3)),
        per_turn_timeout=float(st.session_state.get("group6_chance_timeout", 1.0)),
        total_budget=float(st.session_state.get("group6_chance_budget", 20.0)),
        max_turns=int(st.session_state.get("group6_chance_max_turns", 30)),
        action_order=str(st.session_state.get("group6_chance_action_order", "LRUD")),
        success_probability=float(st.session_state.get("group6_chance_probability", 0.8)),
        seed=int(st.session_state.get("group6_chance_seed", 42)),
        sample_count=int(st.session_state.get("group6_chance_sample_count", 10)),
        utility_penalty=float(st.session_state.get("group6_chance_penalty", -1000.0)),
    )


def _new_robustness_game(start: tuple[int, ...], goal: tuple[int, ...]) -> Group6RobustnessGame:
    game = create_robustness_game(
        start=start,
        goal=goal,
        settings=_robustness_settings_from_state(),
    )
    st.session_state.group6_robustness_game = game
    st.session_state.group6_robustness_view_turn = 0
    return game


def _new_chance_lab(start: tuple[int, ...], goal: tuple[int, ...]) -> Group6ChanceLab:
    lab = create_chance_lab(
        start=start,
        goal=goal,
        settings=_chance_settings_from_state(),
    )
    st.session_state.group6_chance_lab = lab
    st.session_state.group6_chance_view_turn = 0
    return lab


def _render_board(
    t,
    label: str,
    state: tuple[int, ...],
    *,
    goal: tuple[int, ...],
    image_tiles: dict,
    key_prefix: str,
) -> None:
    st.markdown(f"#### {escape(label)}")
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
        st.caption(
            _tx(
                t,
                "group6_image_missing_hint",
                "Chọn ảnh mẫu hoặc upload ảnh để xem puzzle ảnh không gắn số.",
            )
        )


def _history_state(history: list[tuple[int, ...]], view_turn: int) -> tuple[int, ...]:
    return history[min(max(0, view_turn), len(history) - 1)]


def _metric_grid(rows: list[tuple[str, object]]) -> None:
    for offset in range(0, len(rows), 4):
        columns = st.columns(4)
        for col, (label, value) in zip(columns, rows[offset : offset + 4]):
            col.metric(label, value)


def _frames_table(frames) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "Turn": frame.turn,
                "Role": frame.role,
                "Action": frame.realized_action,
                "Intended": frame.intended_action,
                "Utility": frame.utility,
                "Expected utility": frame.expected_utility,
                "Root value": frame.root_value,
                "Probability": frame.probability,
                "Expanded": frame.expanded,
                "Generated": frame.generated,
                "Pruned": frame.pruned,
                "Runtime": frame.runtime,
                "Stop": frame.termination,
                "Cycle": frame.repeated_state,
            }
            for frame in frames
        ]
    )


def _render_variant_charts(t, frames, *, title_prefix: str) -> None:
    if not frames:
        return
    if len(frames) < 2:
        st.caption(
            _tx(
                t,
                "group6_chart_waiting",
                "Chart appears after at least two recorded turns.",
            )
        )
        return
    frame = pd.DataFrame(
        {
            "Turn": [item.turn for item in frames],
            "Utility": [item.utility for item in frames],
            "Expanded": [item.expanded for item in frames],
            "Generated": [item.generated for item in frames],
            "Pruned": [item.pruned for item in frames],
        }
    )
    columns = st.columns(2)
    with columns[0]:
        st.markdown(f"**{title_prefix}: utility theo lượt**")
        st.line_chart(frame, x="Turn", y="Utility")
    with columns[1]:
        st.markdown(f"**{title_prefix}: expanded/generated/pruned**")
        st.line_chart(frame, x="Turn", y=["Expanded", "Generated", "Pruned"])


def render_group6_robustness_lab(
    t,
    *,
    start: tuple[int, ...],
    goal: tuple[int, ...],
    image_tiles: dict,
) -> None:
    st.warning(
        _tx(
            t,
            "group6_robustness_guardrail",
            "Đây là robustness game variant để học Minimax/Alpha-Beta. MIN là worst-case environment branch, không phải người chơi thật của 15-puzzle.",
        )
    )
    st.markdown(
        _tx(
            t,
            "group6_robustness_formula",
            "**Utility:** `U(goal)=+1000`, `U(other)=-Manhattan(state, goal)`, `U(cycle/timeout)=penalty`.",
        )
    )

    st.selectbox(
        _tx(t, "group6_robustness_algorithm", "Thuật toán robustness"),
        ROBUSTNESS_ALGORITHMS,
        key="group6_robustness_algorithm",
        on_change=_reset_robustness,
    )
    with st.expander(_tx(t, "group6_policy_settings", "Cấu hình chung"), expanded=False):
        row = st.columns(4)
        row[0].number_input(_tx(t, "group6_depth", "Depth / ply"), 1, 8, 3, key="group6_robustness_depth", on_change=_reset_robustness)
        row[1].number_input(_tx(t, "group6_turn_timeout", "Timeout mỗi lượt"), 0.1, 10.0, 1.0, 0.1, key="group6_robustness_timeout", on_change=_reset_robustness)
        row[2].number_input(_tx(t, "group6_max_turns", "Giới hạn lượt"), 1, 100, 30, key="group6_robustness_max_turns", on_change=_reset_robustness)
        row[3].number_input(_tx(t, "group6_total_budget", "Tổng budget (giây)"), 1.0, 120.0, 20.0, 1.0, key="group6_robustness_budget", on_change=_reset_robustness)
        row = st.columns(2)
        row[0].selectbox(_tx(t, "group6_action_order", "Thứ tự action"), ("LRUD", "UDLR", "RLDU", "DURL"), key="group6_robustness_action_order", on_change=_reset_robustness)
        row[1].number_input(_tx(t, "group6_penalty", "Penalty cycle/timeout"), -10000.0, -1.0, -1000.0, 100.0, key="group6_robustness_penalty", on_change=_reset_robustness)

    game: Group6RobustnessGame | None = st.session_state.get("group6_robustness_game")
    if game is None or game.start != tuple(start) or game.goal != tuple(goal):
        game = _new_robustness_game(start, goal)

    view_turn = min(
        int(st.session_state.get("group6_robustness_view_turn", len(game.frames))),
        len(game.frames),
    )
    board_state = _history_state(game.history, view_turn)
    _render_board(
        t,
        "Robustness board - MAX/MIN luân phiên",
        board_state,
        goal=goal,
        image_tiles=image_tiles,
        key_prefix="group6_robustness_board",
    )
    next_role = "MAX" if len(game.frames) % 2 == 0 else "MIN"
    _metric_grid(
        [
            ("Status", game.status),
            ("Next role", next_role if game.active else "-"),
            ("Runtime", f"{game.cumulative_runtime:.6f}s"),
            ("Expanded", game.cumulative_expanded),
            ("Generated", game.cumulative_generated),
            ("Pruned", game.cumulative_pruned),
            ("Manhattan", f"{get_heuristic('Manhattan Distance', goal)(game.current_state):.1f}"),
            ("Turns", len(game.frames)),
        ]
    )

    controls = st.columns(5)
    if controls[0].button(_tx(t, "group6_start_over", "Bắt đầu lại"), key="btn_group6_robustness_start", width="stretch"):
        _new_robustness_game(start, goal)
        st.session_state.group6_robustness_auto = False
        st.rerun()
    if controls[1].button(_tx(t, "play_next_step", "Bước tiếp"), key="btn_group6_robustness_next", disabled=not game.active, width="stretch"):
        advance_robustness_game(game)
        st.session_state.group6_robustness_view_turn = len(game.frames)
        st.rerun()
    if controls[2].button(_tx(t, "play_auto_run", "Chạy tự động"), key="btn_group6_robustness_auto", disabled=not game.active, width="stretch"):
        game.running = True
        st.session_state.group6_robustness_auto = True
        st.rerun()
    if controls[3].button(_tx(t, "play_stop_run", "Dừng"), key="btn_group6_robustness_stop", disabled=not st.session_state.get("group6_robustness_auto", False), width="stretch"):
        game.running = False
        st.session_state.group6_robustness_auto = False
        st.rerun()
    if controls[4].button(_tx(t, "play_reset", "Reset"), key="btn_group6_robustness_reset", width="stretch"):
        _reset_robustness()
        st.rerun()

    if game.frames:
        selected = st.slider(
            _tx(t, "group6_turn_view", "Lượt đang xem"),
            0,
            len(game.frames),
            view_turn,
            key=f"group6_robustness_timeline_{len(game.frames)}",
        )
        if selected != view_turn:
            st.session_state.group6_robustness_view_turn = selected
            st.rerun()
        st.dataframe(_frames_table(game.frames), hide_index=True, width="stretch")
        _render_variant_charts(t, game.frames, title_prefix="Robustness")
    else:
        st.caption(
            _tx(
                t,
                "group6_robustness_empty",
                "Nhấn Bước tiếp để MAX tính quyết định gốc, sau đó MIN chọn continuation tệ nhất.",
            )
        )

    st.download_button(
        _tx(t, "group6_export_json", "Tải evidence JSON"),
        data=json.dumps(game.export_summary(), ensure_ascii=False, indent=2).encode("utf-8"),
        file_name="group6-robustness-game.json",
        mime="application/json",
        key="btn_group6_robustness_export",
    )


def render_group6_chance_lab(
    t,
    *,
    start: tuple[int, ...],
    goal: tuple[int, ...],
    image_tiles: dict,
) -> None:
    st.warning(
        _tx(
            t,
            "group6_chance_guardrail",
            "Expectimax là chance model, không phải đối thủ. Kết quả phụ thuộc probability model và seed.",
        )
    )
    st.markdown(
        _tx(
            t,
            "group6_chance_formula",
            "**Expected Utility** = `Σ P(outcome) × Utility(outcome)`.",
        )
    )

    with st.expander(_tx(t, "group6_policy_settings", "Cấu hình chung"), expanded=False):
        row = st.columns(4)
        row[0].number_input(_tx(t, "group6_depth", "Depth / ply"), 1, 8, 3, key="group6_chance_depth", on_change=_reset_chance)
        row[1].number_input(_tx(t, "group6_turn_timeout", "Timeout mỗi lượt"), 0.1, 10.0, 1.0, 0.1, key="group6_chance_timeout", on_change=_reset_chance)
        row[2].number_input(_tx(t, "group6_max_turns", "Giới hạn lượt"), 1, 100, 30, key="group6_chance_max_turns", on_change=_reset_chance)
        row[3].number_input(_tx(t, "group6_total_budget", "Tổng budget (giây)"), 1.0, 120.0, 20.0, 1.0, key="group6_chance_budget", on_change=_reset_chance)
        row = st.columns(4)
        row[0].selectbox(_tx(t, "group6_action_order", "Thứ tự action"), ("LRUD", "UDLR", "RLDU", "DURL"), key="group6_chance_action_order", on_change=_reset_chance)
        row[1].slider(_tx(t, "group6_probability", "P intended action"), 0.0, 1.0, 0.8, 0.05, key="group6_chance_probability", on_change=_reset_chance)
        row[2].number_input(_tx(t, "group6_seed", "Seed"), 0, 2**31 - 1, 42, key="group6_chance_seed", on_change=_reset_chance)
        row[3].number_input(_tx(t, "group6_seed_count", "Multi-seed samples"), 1, 100, 10, key="group6_chance_sample_count", on_change=_reset_chance)

    lab: Group6ChanceLab | None = st.session_state.get("group6_chance_lab")
    if lab is None or lab.start != tuple(start) or lab.goal != tuple(goal):
        lab = _new_chance_lab(start, goal)

    view_turn = min(
        int(st.session_state.get("group6_chance_view_turn", len(lab.frames))),
        len(lab.frames),
    )
    board_state = _history_state(lab.history, view_turn)
    board_col, evidence_col = st.columns([1.05, 0.95], gap="large")
    with board_col:
        _render_board(
            t,
            "Chance board - Expectimax",
            board_state,
            goal=goal,
            image_tiles=image_tiles,
            key_prefix="group6_chance_board",
        )
    with evidence_col:
        latest = lab.frames[view_turn - 1] if view_turn > 0 and lab.frames else None
        st.markdown(f"#### {_tx(t, 'group6_intended_realized', 'Intended vs Realized')}")
        if latest is None:
            st.info(
                _tx(
                    t,
                    "group6_chance_empty",
                    "Nhấn Bước tiếp để Expectimax chọn intended action, rồi CHANCE sample realized outcome.",
                )
            )
        else:
            st.markdown(
                f"""
                <div class="ai-contract-card">
                  <span>Turn {latest.turn}</span>
                  <h3>{escape(latest.intended_action)} → {escape(latest.realized_action)}</h3>
                  <p>Probability={latest.probability:.3f} | Expected Utility={latest.expected_utility:.3f}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
    _metric_grid(
        [
            ("Algorithm", "Expectimax"),
            ("Status", lab.status),
            ("Runtime", f"{lab.cumulative_runtime:.6f}s"),
            ("Expanded", lab.cumulative_expanded),
            ("Generated", lab.cumulative_generated),
            ("Manhattan", f"{get_heuristic('Manhattan Distance', goal)(lab.current_state):.1f}"),
            ("Turns", len(lab.frames)),
            ("Seed", lab.settings.seed),
        ]
    )

    controls = st.columns(6)
    if controls[0].button(_tx(t, "group6_start_over", "Bắt đầu lại"), key="btn_group6_chance_start", width="stretch"):
        _new_chance_lab(start, goal)
        st.session_state.group6_chance_auto = False
        st.rerun()
    if controls[1].button(_tx(t, "play_next_step", "Bước tiếp"), key="btn_group6_chance_next", disabled=not lab.active, width="stretch"):
        advance_chance_lab(lab)
        st.session_state.group6_chance_view_turn = len(lab.frames)
        st.rerun()
    if controls[2].button(_tx(t, "play_auto_run", "Chạy tự động"), key="btn_group6_chance_auto", disabled=not lab.active, width="stretch"):
        lab.running = True
        st.session_state.group6_chance_auto = True
        st.rerun()
    if controls[3].button(_tx(t, "play_stop_run", "Dừng"), key="btn_group6_chance_stop", disabled=not st.session_state.get("group6_chance_auto", False), width="stretch"):
        lab.running = False
        st.session_state.group6_chance_auto = False
        st.rerun()
    if controls[4].button(_tx(t, "play_reset", "Reset"), key="btn_group6_chance_reset", width="stretch"):
        _reset_chance()
        st.rerun()
    if controls[5].button(_tx(t, "group6_run_stability", "Chạy nhiều seed"), key="btn_group6_chance_stability", width="stretch"):
        st.session_state.group6_chance_stability = run_chance_stability_sample(
            start=start,
            goal=goal,
            settings=_chance_settings_from_state(),
        )

    if lab.frames:
        selected = st.slider(
            _tx(t, "group6_turn_view", "Lượt đang xem"),
            0,
            len(lab.frames),
            view_turn,
            key=f"group6_chance_timeline_{len(lab.frames)}",
        )
        if selected != view_turn:
            st.session_state.group6_chance_view_turn = selected
            st.rerun()
        st.dataframe(_frames_table(lab.frames), hide_index=True, width="stretch")
        _render_variant_charts(t, lab.frames, title_prefix="Chance")

    stability = st.session_state.get("group6_chance_stability")
    if stability:
        st.markdown(f"#### {_tx(t, 'group6_stability', 'Multi-seed stability')}")
        stats = stability["stats"]
        _metric_grid(
            [
                ("Mean runtime", f"{stats['mean_runtime']:.6f}s"),
                ("Runtime min/max", f"{stats['min_runtime']:.6f}/{stats['max_runtime']:.6f}"),
                ("Runtime std", f"{stats['std_runtime']:.6f}"),
                ("Mean final h", f"{stats['mean_final_manhattan']:.2f}"),
                ("Final h min/max", f"{stats['min_final_manhattan']:.1f}/{stats['max_final_manhattan']:.1f}"),
                ("Final h std", f"{stats['std_final_manhattan']:.2f}"),
                ("Goal reached", stats["goal_reached_count"]),
            ]
        )
        st.dataframe(pd.DataFrame(stability["rows"]), hide_index=True, width="stretch")

    st.download_button(
        _tx(t, "group6_export_json", "Tải evidence JSON"),
        data=json.dumps(lab.export_summary(), ensure_ascii=False, indent=2).encode("utf-8"),
        file_name="group6-chance-outcome.json",
        mime="application/json",
        key="btn_group6_chance_export",
    )
