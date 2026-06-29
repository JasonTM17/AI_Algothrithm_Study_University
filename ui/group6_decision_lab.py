"""Streamlit controls and evidence surfaces for Group 6 decision models."""

from __future__ import annotations

from dataclasses import replace
from html import escape
import json
from statistics import mean, pstdev

import pandas as pd
import streamlit as st

from core.group6_decision_lab import (
    GROUP6_LAB_ALGORITHMS,
    Group6LabResult,
    Group6LabSettings,
    compare_minimax_alpha_beta,
    run_group6_algorithm,
)
from ui.components import render_image_board, render_puzzle_board
from ui.group6_tree_viewer import TREE_MODES, render_group6_tree_viewer


_CLEAR_KEYS = (
    "group6_lab_result",
    "group6_lab_results",
    "group6_lab_index",
    "group6_lab_auto",
    "group6_lab_auto_pending",
    "group6_lab_slider_version",
    "group6_sweep_active",
    "group6_sweep_queue",
    "group6_sweep_rows",
    "group6_sweep_settings",
    "group6_sweep_start",
    "group6_sweep_goal",
    "group6_sweep_runtime_total",
    "group6_stability_rows",
)


def _text(t, key: str, fallback: str, **kwargs) -> str:
    try:
        value = t(key, **kwargs)
    except Exception:
        value = key
    if not isinstance(value, str) or value == key:
        return fallback.format(**kwargs)
    return value


def clear_group6_lab_state() -> None:
    """Remove evidence tied to a previous Start/Goal contract."""
    for key in _CLEAR_KEYS:
        st.session_state.pop(key, None)


def group6_lab_needs_tick() -> bool:
    return bool(
        st.session_state.get("group6_lab_auto")
        or st.session_state.get("group6_sweep_active")
    )


def _set_replay_index(index: int) -> None:
    previous = int(st.session_state.get("group6_lab_index", 0))
    st.session_state.group6_lab_index = index
    if previous != index:
        st.session_state.group6_lab_slider_version = (
            int(st.session_state.get("group6_lab_slider_version", 0)) + 1
        )


def _invalidate_current_result() -> None:
    """Hide evidence that no longer matches the visible controls."""
    st.session_state.pop("group6_lab_result", None)
    st.session_state.group6_lab_index = 0
    st.session_state.group6_lab_auto = False
    st.session_state.group6_sweep_active = False


def _current_settings() -> Group6LabSettings:
    return Group6LabSettings(
        depth=int(st.session_state.get("group6_depth", 3)),
        timeout=float(st.session_state.get("group6_timeout", 5.0)),
        heuristic="Manhattan Distance",
        action_order=str(st.session_state.get("group6_action_order", "LRUD")),
        success_probability=float(st.session_state.get("group6_probability", 0.8)),
        seed=int(st.session_state.get("group6_seed", 42)),
    )


def _sweep_row(lab_result: Group6LabResult) -> dict[str, object]:
    result = lab_result.result
    return {
        "Algorithm": lab_result.algorithm,
        "Depth": lab_result.settings.depth,
        "Runtime (s)": float(result.runtime),
        "Expanded": int(result.nodes_expanded),
        "Generated": int(result.nodes_generated),
        "Pruned": int(lab_result.prune_count),
        "Root value": lab_result.root_value,
        "Final h": float(lab_result.final_manhattan),
        "Branching proxy": float(lab_result.empirical_branching_factor),
        "Termination": result.termination_reason,
        "Comparable fingerprint": lab_result.baseline_fingerprint,
    }


def advance_group6_lab_tick() -> None:
    """Advance one replay frame or one depth-sweep run per fragment tick."""
    if st.session_state.get("group6_lab_auto"):
        if st.session_state.pop("group6_lab_auto_pending", False):
            return
        result: Group6LabResult | None = st.session_state.get("group6_lab_result")
        if result is None:
            st.session_state.group6_lab_auto = False
            return
        index = int(st.session_state.get("group6_lab_index", 0))
        if index >= len(result.frames):
            st.session_state.group6_lab_auto = False
        else:
            _set_replay_index(index + 1)
            if index + 1 >= len(result.frames):
                st.session_state.group6_lab_auto = False

    if not st.session_state.get("group6_sweep_active"):
        return
    queue = list(st.session_state.get("group6_sweep_queue") or [])
    total_runtime = float(st.session_state.get("group6_sweep_runtime_total", 0.0))
    total_budget = 20.0
    if not queue or total_runtime >= total_budget:
        st.session_state.group6_sweep_active = False
        return

    task = queue.pop(0)
    settings: Group6LabSettings = st.session_state.group6_sweep_settings
    remaining = max(0.05, total_budget - total_runtime)
    run_settings = replace(
        settings,
        depth=int(task["depth"]),
        timeout=min(float(settings.timeout), remaining),
    )
    lab_result = run_group6_algorithm(
        str(task["algorithm"]),
        start=tuple(st.session_state.group6_sweep_start),
        goal=tuple(st.session_state.group6_sweep_goal),
        settings=run_settings,
    )
    rows = list(st.session_state.get("group6_sweep_rows") or [])
    rows.append(_sweep_row(lab_result))
    st.session_state.group6_sweep_rows = rows
    st.session_state.group6_sweep_queue = queue
    st.session_state.group6_sweep_runtime_total = total_runtime + float(
        lab_result.result.runtime
    )
    if not queue:
        st.session_state.group6_sweep_active = False


def render_group6_controls(
    t,
    *,
    start: tuple[int, ...],
    goal: tuple[int, ...],
) -> None:
    """Render compact controls; full evidence is rendered below the workbench."""
    st.markdown(
        f"""
        <div class="ai-solver-card">
          <div class="ai-solver-header">
            <div class="ai-solver-title-container">
              <span class="ai-solver-badge">GROUP 6</span>
              <h3>{escape(_text(t, "group6_lab_title", "AI Duel & Robustness Lab"))}</h3>
            </div>
          </div>
          <p class="ai-solver-desc">{escape(_text(
              t,
              "group6_lab_desc",
              "Decision-tree analysis on the current puzzle; not a natural two-player game.",
          ))}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.warning(
        _text(
            t,
            "group6_lab_guardrail",
            "Decision-tree model, not a natural two-player 15-puzzle game.",
        )
    )

    algorithm = st.selectbox(
        _text(t, "group6_algorithm", "Decision model"),
        GROUP6_LAB_ALGORITHMS,
        key="group6_algorithm",
        on_change=_invalidate_current_result,
    )
    param_cols = st.columns(2)
    with param_cols[0]:
        st.number_input(
            _text(t, "group6_depth", "Search depth / ply"),
            min_value=1,
            max_value=8,
            value=3,
            key="group6_depth",
            on_change=_invalidate_current_result,
        )
        st.selectbox(
            _text(t, "group6_action_order", "Action order"),
            ("LRUD", "UDLR", "RLDU", "DURL"),
            key="group6_action_order",
            on_change=_invalidate_current_result,
        )
    with param_cols[1]:
        st.number_input(
            _text(t, "group6_timeout", "Timeout per run (seconds)"),
            min_value=0.1,
            max_value=30.0,
            value=5.0,
            step=0.5,
            key="group6_timeout",
            on_change=_invalidate_current_result,
        )
        st.number_input(
            _text(t, "group6_seed", "Seed"),
            min_value=0,
            max_value=2**31 - 1,
            value=42,
            key="group6_seed",
            disabled=algorithm != "Expectimax",
            on_change=_invalidate_current_result,
        )
    st.slider(
        _text(t, "group6_probability", "Intended-action success probability"),
        min_value=0.0,
        max_value=1.0,
        value=0.8,
        step=0.05,
        key="group6_probability",
        disabled=algorithm != "Expectimax",
        on_change=_invalidate_current_result,
    )

    formula = {
        "Minimax": "V(s)=max_a min_b V(Result(s,a,b))",
        "Alpha-Beta Pruning": "V(s)=Minimax(s), with alpha >= beta cutoffs",
        "Expectimax": "V(s)=max_a sum_o P(o|s,a) V(o)",
    }[algorithm]
    st.code(
        f"U(goal)=+1000\nU(other)=-Manhattan(state, goal)\n{formula}",
        language="text",
    )
    st.caption(
        _text(
            t,
            "group6_formula_note",
            "Manhattan Distance, action ordering and the chance model are part of the run contract shown above.",
        )
    )

    if st.button(
        _text(t, "group6_run", "Run decision analysis"),
        key="btn_group6_run",
        type="primary",
        width="stretch",
    ):
        settings = _current_settings()
        with st.spinner(
            _text(t, "group6_running", "Evaluating the selected decision tree...")
        ):
            lab_result = run_group6_algorithm(
                algorithm,
                start=tuple(start),
                goal=tuple(goal),
                settings=settings,
            )
        results = dict(st.session_state.get("group6_lab_results") or {})
        comparable = {
            name: item
            for name, item in results.items()
            if item.baseline_fingerprint == lab_result.baseline_fingerprint
        }
        comparable[algorithm] = lab_result
        st.session_state.group6_lab_results = comparable
        st.session_state.group6_lab_result = lab_result
        st.session_state.group6_lab_index = 0
        st.session_state.group6_lab_auto = False
        st.session_state.group6_lab_slider_version = (
            int(st.session_state.get("group6_lab_slider_version", 0)) + 1
        )


def _render_role_board(
    label: str,
    state: tuple[int, ...],
    *,
    key_prefix: str,
    board_mode: str,
    image_tiles: dict,
    goal: tuple[int, ...],
) -> None:
    st.markdown(f"**{escape(label)}**")
    if board_mode == "image" and image_tiles:
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


def _current_frame_states(
    lab_result: Group6LabResult,
    index: int,
    start: tuple[int, ...],
) -> tuple[tuple[int, ...], tuple[int, ...]]:
    if index <= 0 or not lab_result.frames:
        return start, start
    frame = lab_result.frames[min(index, len(lab_result.frames)) - 1]
    return frame.before_state, frame.after_state


def _render_replay(
    t,
    lab_result: Group6LabResult,
    *,
    start: tuple[int, ...],
    goal: tuple[int, ...],
    board_mode: str,
    image_tiles: dict,
) -> None:
    index = min(
        int(st.session_state.get("group6_lab_index", 0)),
        len(lab_result.frames),
    )
    before, after = _current_frame_states(lab_result, index, start)
    current_frame = lab_result.frames[index - 1] if index > 0 else None

    if lab_result.algorithm == "Expectimax":
        left_label = _text(t, "group6_max_intended", "MAX - Intended action")
        right_label = _text(t, "group6_chance_outcome", "CHANCE - Realized outcome")
    else:
        left_label = _text(t, "group6_max_solver", "MAX - Solver decision")
        right_label = _text(
            t, "group6_worst_case", "MIN - Worst-case continuation"
        )

    board_cols = st.columns(2, gap="large")
    with board_cols[0]:
        _render_role_board(
            left_label,
            before,
            key_prefix="group6_left_image",
            board_mode=board_mode,
            image_tiles=image_tiles,
            goal=goal,
        )
    with board_cols[1]:
        _render_role_board(
            right_label,
            after,
            key_prefix="group6_right_image",
            board_mode=board_mode,
            image_tiles=image_tiles,
            goal=goal,
        )

    if current_frame is None:
        st.info(
            _text(
                t,
                "group6_replay_start",
                "Ply 0: both views start from the same puzzle state.",
            )
        )
    else:
        details = [
            f"role={current_frame.role}",
            f"intended={current_frame.intended_action}",
            f"realized={current_frame.realized_action}",
            (
                "value=-"
                if current_frame.utility is None
                else f"value={current_frame.utility:.2f}"
            ),
        ]
        if current_frame.probability is not None:
            details.append(f"P={current_frame.probability:.2f}")
        if current_frame.alpha is not None or current_frame.beta is not None:
            details.append(
                f"alpha={current_frame.alpha}, beta={current_frame.beta}"
            )
        st.markdown(
            f"**Ply {index}/{len(lab_result.frames)}** | " + " | ".join(details)
        )
        st.caption(current_frame.reason)
        if current_frame.repeated_state:
            st.warning(
                _text(
                    t,
                    "group6_cycle",
                    "This variation revisits an earlier state; it is not proof of progress toward the goal.",
                )
            )

    controls = st.columns(4)
    with controls[0]:
        if st.button(
            _text(t, "play_prev_step", "Previous"),
            key="btn_group6_prev",
            disabled=index == 0,
            width="stretch",
        ):
            _set_replay_index(index - 1)
            st.rerun()
    with controls[1]:
        if st.button(
            _text(t, "play_next_step", "Next"),
            key="btn_group6_next",
            disabled=index >= len(lab_result.frames),
            width="stretch",
        ):
            _set_replay_index(index + 1)
            st.rerun()
    with controls[2]:
        if st.button(
            _text(t, "play_auto_run", "Auto"),
            key="btn_group6_auto",
            disabled=index >= len(lab_result.frames),
            width="stretch",
        ):
            st.session_state.group6_lab_auto = True
            st.session_state.group6_lab_auto_pending = True
            st.rerun()
    with controls[3]:
        if st.button(
            _text(t, "play_stop_run", "Stop"),
            key="btn_group6_stop",
            disabled=not st.session_state.get("group6_lab_auto", False),
            width="stretch",
        ):
            st.session_state.group6_lab_auto = False
            st.rerun()

    slider_key = (
        f"group6_lab_slider_{st.session_state.get('group6_lab_slider_version', 0)}"
    )
    slider_value = st.slider(
        _text(t, "group6_ply_slider", "Selected game-tree ply"),
        0,
        len(lab_result.frames),
        index,
        key=slider_key,
    )
    if slider_value != index:
        _set_replay_index(slider_value)
        st.rerun()


def _result_rows(results: dict[str, Group6LabResult]) -> list[dict[str, object]]:
    rows = []
    for item in results.values():
        rows.append(
            {
                "Algorithm": item.algorithm,
                "Runtime (s)": round(float(item.result.runtime), 6),
                "Variation ply": len(item.frames),
                "Root value": item.root_value,
                "Final h": item.final_manhattan,
                "Expanded": item.result.nodes_expanded,
                "Generated": item.result.nodes_generated,
                "Pruned": item.prune_count,
                "Tree/trace nodes": item.captured_trace_nodes,
                "Completed depth": item.completed_depth,
                "Frontier / Reached": "N/A",
                "Legal variation": item.result.path_verified,
                "Goal reached": item.result.goal_reached,
                "Termination": item.result.termination_reason,
            }
        )
    return rows


def _render_comparison(t, results: dict[str, Group6LabResult]) -> None:
    if not results:
        return
    st.subheader(_text(t, "group6_comparison", "Group 6 evidence comparison"))
    st.dataframe(pd.DataFrame(_result_rows(results)), hide_index=True, width="stretch")
    equality = compare_minimax_alpha_beta(
        results.get("Minimax"),
        results.get("Alpha-Beta Pruning"),
    )
    if equality is True:
        st.success(
            _text(
                t,
                "group6_root_equal",
                "Minimax and Alpha-Beta preserve the same completed root value for this fingerprint.",
            )
        )
    elif equality is False:
        st.error(
            _text(
                t,
                "group6_root_mismatch",
                "Root values differ under a comparable completed configuration; this requires review.",
            )
        )
    else:
        st.caption(
            _text(
                t,
                "group6_root_not_comparable",
                "Run completed Minimax and Alpha-Beta analyses with the same fingerprint to verify root-value equality.",
            )
        )


def _start_sweep(
    start: tuple[int, ...],
    goal: tuple[int, ...],
    settings: Group6LabSettings,
) -> None:
    st.session_state.group6_sweep_queue = [
        {"algorithm": algorithm, "depth": depth}
        for depth in range(1, 6)
        for algorithm in GROUP6_LAB_ALGORITHMS
    ]
    st.session_state.group6_sweep_rows = []
    st.session_state.group6_sweep_settings = settings
    st.session_state.group6_sweep_start = tuple(start)
    st.session_state.group6_sweep_goal = tuple(goal)
    st.session_state.group6_sweep_runtime_total = 0.0
    st.session_state.group6_sweep_active = True


def _render_sweep(
    t,
    *,
    start: tuple[int, ...],
    goal: tuple[int, ...],
    settings: Group6LabSettings,
) -> None:
    st.markdown(f"#### {_text(t, 'group6_profiler', 'Depth 1-5 complexity profiler')}")
    st.caption(
        _text(
            t,
            "group6_profiler_note",
            "Empirical evidence on one fixed state complements, but does not prove, asymptotic complexity.",
        )
    )
    control_cols = st.columns(2)
    with control_cols[0]:
        if st.button(
            _text(t, "group6_start_sweep", "Run depth sweep"),
            key="btn_group6_sweep",
            disabled=st.session_state.get("group6_sweep_active", False),
            width="stretch",
        ):
            _start_sweep(start, goal, settings)
            st.rerun()
    with control_cols[1]:
        if st.button(
            _text(t, "group6_stop_sweep", "Stop sweep"),
            key="btn_group6_sweep_stop",
            disabled=not st.session_state.get("group6_sweep_active", False),
            width="stretch",
        ):
            st.session_state.group6_sweep_active = False
            st.rerun()

    rows = list(st.session_state.get("group6_sweep_rows") or [])
    remaining = len(st.session_state.get("group6_sweep_queue") or [])
    if st.session_state.get("group6_sweep_active"):
        st.progress((15 - remaining) / 15, text=f"{15 - remaining}/15 runs")
    if not rows:
        return

    frame = pd.DataFrame(rows)
    st.dataframe(frame, hide_index=True, width="stretch")
    chart_cols = st.columns(2)
    with chart_cols[0]:
        st.markdown(f"**{_text(t, 'group6_runtime_by_depth', 'Runtime by depth')}**")
        st.line_chart(frame, x="Depth", y="Runtime (s)", color="Algorithm")
    with chart_cols[1]:
        st.markdown(
            f"**{_text(t, 'group6_expanded_by_depth', 'Expanded nodes by depth')}**"
        )
        st.line_chart(frame, x="Depth", y="Expanded", color="Algorithm")

    pivot = frame.pivot_table(
        index="Depth",
        columns="Algorithm",
        values="Expanded",
        aggfunc="last",
    )
    if {"Minimax", "Alpha-Beta Pruning"}.issubset(pivot.columns):
        reduction = (
            100.0
            * (pivot["Minimax"] - pivot["Alpha-Beta Pruning"])
            / pivot["Minimax"].replace(0, pd.NA)
        )
        st.dataframe(
            pd.DataFrame(
                {
                    "Depth": reduction.index,
                    "Alpha-Beta node reduction (%)": reduction.values,
                }
            ),
            hide_index=True,
            width="stretch",
        )
    st.download_button(
        _text(t, "group6_export_csv", "Download complexity CSV"),
        data=frame.to_csv(index=False).encode("utf-8"),
        file_name="group6-complexity.csv",
        mime="text/csv",
        key="btn_group6_export_csv",
    )


def _render_stability(
    t,
    *,
    start: tuple[int, ...],
    goal: tuple[int, ...],
    settings: Group6LabSettings,
) -> None:
    st.markdown(f"#### {_text(t, 'group6_stability', 'Expectimax multi-seed stability')}")
    samples = st.number_input(
        _text(t, "group6_seed_count", "Seed count"),
        min_value=2,
        max_value=30,
        value=10,
        key="group6_seed_count",
    )
    if st.button(
        _text(t, "group6_run_stability", "Run stability sample"),
        key="btn_group6_stability",
        width="stretch",
    ):
        rows = []
        bounded = replace(settings, timeout=min(settings.timeout, 1.0))
        with st.spinner(
            _text(t, "group6_stability_running", "Running seeded samples...")
        ):
            for seed in range(int(samples)):
                sample = run_group6_algorithm(
                    "Expectimax",
                    start=start,
                    goal=goal,
                    settings=replace(bounded, seed=seed),
                )
                rows.append(
                    {
                        "Seed": seed,
                        "Runtime (s)": sample.result.runtime,
                        "Final h": sample.final_manhattan,
                        "Root expected value": sample.root_value,
                        "Termination": sample.result.termination_reason,
                    }
                )
        st.session_state.group6_stability_rows = rows

    rows = list(st.session_state.get("group6_stability_rows") or [])
    if not rows:
        return
    frame = pd.DataFrame(rows)
    st.dataframe(frame, hide_index=True, width="stretch")
    h_values = [float(row["Final h"]) for row in rows]
    runtimes = [float(row["Runtime (s)"]) for row in rows]
    metrics = st.columns(4)
    metrics[0].metric(
        _text(t, "group6_mean_final_h", "Mean final h"),
        f"{mean(h_values):.2f}",
    )
    metrics[1].metric(
        _text(t, "group6_final_h_range", "Final h range"),
        f"{min(h_values):.1f}-{max(h_values):.1f}",
    )
    metrics[2].metric(
        _text(t, "group6_mean_runtime", "Mean runtime"),
        f"{mean(runtimes):.6f}s",
    )
    metrics[3].metric(
        _text(t, "group6_runtime_sd", "Runtime SD"),
        f"{pstdev(runtimes):.6f}s",
    )


def render_group6_evidence(
    t,
    *,
    start: tuple[int, ...],
    goal: tuple[int, ...],
    board_mode: str,
    image_tiles: dict,
) -> None:
    """Render two role boards, metrics, tree evidence and optional profiling."""
    lab_result: Group6LabResult | None = st.session_state.get("group6_lab_result")
    if lab_result is None:
        st.info(
            _text(
                t,
                "group6_empty",
                "Run a Group 6 model to inspect its exact role-based variation.",
            )
        )
        return

    st.subheader(
        _text(
            t,
            "group6_evidence_title",
            "{algorithm}: role-based decision evidence",
            algorithm=lab_result.algorithm,
        )
    )
    _render_replay(
        t,
        lab_result,
        start=start,
        goal=goal,
        board_mode=board_mode,
        image_tiles=image_tiles,
    )

    result = lab_result.result
    metrics = st.columns(4)
    metrics[0].metric(
        _text(t, "group6_root_value", "Root value"),
        "-" if lab_result.root_value is None else f"{lab_result.root_value:.2f}",
    )
    metrics[1].metric(
        _text(t, "group6_variation_ply", "Variation ply"),
        len(lab_result.frames),
    )
    metrics[2].metric(
        _text(t, "group6_expanded_generated", "Expanded / Generated"),
        f"{result.nodes_expanded} / {result.nodes_generated}",
    )
    metrics[3].metric(
        _text(t, "group6_runtime", "Runtime"),
        f"{result.runtime:.6f}s",
    )
    metrics = st.columns(4)
    metrics[0].metric(
        _text(t, "group6_final_manhattan", "Final Manhattan"),
        f"{lab_result.final_manhattan:.1f}",
    )
    metrics[1].metric(
        _text(t, "group6_pruned", "Pruned"),
        lab_result.prune_count,
    )
    metrics[2].metric(
        _text(t, "group6_tree_trace_nodes", "Tree / trace nodes"),
        lab_result.captured_trace_nodes,
    )
    metrics[3].metric(
        _text(t, "group6_frontier_reached", "Frontier / Reached"),
        _text(t, "group6_not_applicable", "N/A"),
    )
    metrics = st.columns(2)
    metrics[0].metric(
        _text(t, "group6_completed_depth", "Completed depth"),
        lab_result.completed_depth,
    )
    metrics[1].metric(
        _text(t, "group6_branching_proxy", "Empirical branching proxy"),
        f"{lab_result.empirical_branching_factor:.3f}",
    )
    st.caption(
        _text(
            t,
            "group6_fingerprint",
            "Comparable fingerprint: {fingerprint}",
            fingerprint=lab_result.baseline_fingerprint,
        )
    )
    st.caption(
        _text(
            t,
            "group6_space_proxy",
            "Space proxy uses generated nodes, captured trace/tree events, depth and pruning. It is not measured MB.",
        )
    )

    tree_mode = st.segmented_control(
        _text(t, "group6_tree_filter", "Tree evidence filter"),
        TREE_MODES,
        default="Principal variation",
        key="group6_tree_mode",
        width="stretch",
    )
    render_group6_tree_viewer(
        lab_result,
        current_index=int(st.session_state.get("group6_lab_index", 0)),
        mode=tree_mode or "Principal variation",
    )

    results = dict(st.session_state.get("group6_lab_results") or {})
    _render_comparison(t, results)
    st.download_button(
        _text(t, "group6_export_json", "Download current evidence JSON"),
        data=json.dumps(
            lab_result.export_summary(),
            indent=2,
            ensure_ascii=False,
        ).encode("utf-8"),
        file_name=f"group6-{lab_result.algorithm.lower().replace(' ', '-')}.json",
        mime="application/json",
        key="btn_group6_export_json",
    )

    with st.expander(
        _text(t, "group6_advanced", "Advanced complexity analysis"),
        expanded=False,
    ):
        st.markdown(
            _text(
                t,
                "group6_complexity_table",
                """
            | Model | Time | Textbook space interpretation |
            |---|---|---|
            | Minimax | `O(b^m)` | Depth-first game tree; retained evidence increases actual app storage |
            | Alpha-Beta | worst `O(b^m)`, best near `O(b^(m/2))` | Same decision value, fewer evaluated branches with good ordering |
            | Expectimax | `O((a*o)^d)` | MAX actions multiplied by CHANCE outcomes |
            """,
            )
        )
        settings = _current_settings()
        _render_sweep(t, start=start, goal=goal, settings=settings)
        _render_stability(t, start=start, goal=goal, settings=settings)
