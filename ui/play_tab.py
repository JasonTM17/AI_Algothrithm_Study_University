"""Play tab for the Streamlit app."""

from html import escape
import random

import streamlit as st

from algorithms.informed import a_star
from core.gameplay import score_challenge, validate_player_run
from core.heuristics import HEURISTICS
from core.puzzle import GOAL_STATE, is_solvable, _move_blank
from ui.academic_panels import render_exam_path
from ui.components import (
    process_uploaded_image,
    render_clickable_board,
    render_image_board,
    render_puzzle_board,
    render_search_detail_table,
    render_search_tree,
)

VICTORY_MESSAGE_KEYS = (
    "play_victory_1",
    "play_victory_2",
    "play_victory_3",
    "play_victory_4",
    "play_victory_5",
)

def _clear_victory_state() -> None:
    st.session_state.pop("play_victory_signature", None)
    st.session_state.pop("play_victory_message_key", None)
    st.session_state.pop("play_victory_balloons_pending", None)


def _handle_play_slide(direction: str) -> None:
    ns = _move_blank(st.session_state.play_state, direction)
    if ns:
        _clear_victory_state()
        _clear_ai_replay()
        st.session_state.play_state = ns
        st.session_state.play_moves += 1
        st.session_state.play_history.append(ns)


def _clear_ai_replay() -> None:
    """Clear stale solver replay state after manual play diverges."""
    st.session_state.play_solution_path = None
    st.session_state.play_solution_actions = None
    st.session_state.play_solution_idx = 0
    st.session_state.play_solution_res = None
    st.session_state.play_solution_base_history = None
    st.session_state.play_solution_base_moves = 0
    st.session_state.play_auto_run = False
    st.session_state.play_replay_speed = st.session_state.get("play_replay_speed", 0.35)
    st.session_state.pop("play_auto_done_pending", None)
    st.session_state.pop("play_slider_val", None)


def _store_ai_replay_result(result) -> None:
    """Persist an AI solution together with the manual history it extends."""
    st.session_state.play_solution_path = result.path
    st.session_state.play_solution_actions = result.actions
    st.session_state.play_solution_idx = 0
    st.session_state.play_solution_res = result
    st.session_state.play_solution_base_history = list(st.session_state.play_history)
    st.session_state.play_solution_base_moves = st.session_state.play_moves


def _apply_ai_replay_step(index: int) -> None:
    """Move the board to a solver replay step while keeping challenge history truthful."""
    path = st.session_state.play_solution_path
    if not path:
        return
    bounded_index = max(0, min(index, len(path) - 1))
    base_history = list(st.session_state.get("play_solution_base_history") or [path[0]])
    base_moves = st.session_state.get("play_solution_base_moves", max(0, len(base_history) - 1))
    if not base_history or base_history[-1] != path[0]:
        base_history = [path[0]]
        base_moves = 0

    st.session_state.play_solution_idx = bounded_index
    st.session_state.play_state = path[bounded_index]
    st.session_state.play_history = base_history + list(path[1:bounded_index + 1])
    st.session_state.play_moves = base_moves + bounded_index
    if bounded_index > 0:
        st.session_state.play_assisted = True


def _render_victory_notice(t) -> None:
    """Show a varied, stable win message when the live board matches the goal."""
    goal = st.session_state.get("goal_state", GOAL_STATE)
    if st.session_state.play_state != goal:
        return

    signature = (
        tuple(st.session_state.get("play_history", ())),
        int(st.session_state.get("play_moves", 0)),
        bool(st.session_state.get("play_assisted", False)),
    )
    if st.session_state.get("play_victory_signature") != signature:
        st.session_state.play_victory_signature = signature
        st.session_state.play_victory_message_key = random.choice(VICTORY_MESSAGE_KEYS)
        st.session_state.play_victory_balloons_pending = True

    if st.session_state.get("play_victory_balloons_pending", False):
        st.balloons()
        st.session_state.play_victory_balloons_pending = False

    message_key = st.session_state.get("play_victory_message_key", "play_solved_success")
    message = t(message_key, moves=st.session_state.play_moves)
    st.markdown(
        f"""
        <div class="play-victory-banner">
            <div class="play-victory-kicker">{escape(t("play_victory_kicker"))}</div>
            <div class="play-victory-title">{escape(message)}</div>
            <div class="play-victory-subtitle">{escape(t("play_victory_subtitle"))}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _ensure_play_state(goal) -> None:
    """Initialize and reset the live play board when start or goal changes."""
    if "play_state" not in st.session_state:
        st.session_state.play_state = st.session_state.start_state
        st.session_state.play_moves = 0
        st.session_state.play_history = [st.session_state.start_state]
    if "play_history" not in st.session_state:
        st.session_state.play_history = [st.session_state.play_state]
    if "play_assisted" not in st.session_state:
        st.session_state.play_assisted = False

    if "play_start_ref" not in st.session_state:
        st.session_state.play_start_ref = st.session_state.start_state
    if "play_goal_ref" not in st.session_state:
        st.session_state.play_goal_ref = goal
    if (
        st.session_state.play_start_ref != st.session_state.start_state
        or st.session_state.play_goal_ref != goal
    ):
        st.session_state.play_state = st.session_state.start_state
        st.session_state.play_moves = 0
        st.session_state.play_history = [st.session_state.start_state]
        st.session_state.play_assisted = False
        st.session_state.play_start_ref = st.session_state.start_state
        st.session_state.play_goal_ref = goal
        _clear_ai_replay()
        _clear_victory_state()
        st.session_state.pop("play_optimal_result", None)


def _ensure_ai_replay_state() -> None:
    if "play_solution_path" not in st.session_state:
        st.session_state.play_solution_path = None
    if "play_solution_actions" not in st.session_state:
        st.session_state.play_solution_actions = None
    if "play_solution_idx" not in st.session_state:
        st.session_state.play_solution_idx = 0
    if "play_solution_res" not in st.session_state:
        st.session_state.play_solution_res = None
    if "play_auto_run" not in st.session_state:
        st.session_state.play_auto_run = False
    if "play_replay_speed" not in st.session_state:
        st.session_state.play_replay_speed = 0.35


def _advance_auto_replay_one_step() -> None:
    """Advance one solver frame; Streamlit fragments call this repeatedly."""
    if not st.session_state.get("play_auto_run", False):
        return
    path = st.session_state.get("play_solution_path")
    if not path:
        st.session_state.play_auto_run = False
        return

    idx = int(st.session_state.get("play_solution_idx", 0))
    if idx >= len(path) - 1:
        st.session_state.play_auto_run = False
        st.session_state["play_auto_done_pending"] = True
        return

    _apply_ai_replay_step(idx + 1)
    if idx + 1 >= len(path) - 1:
        st.session_state.play_auto_run = False
        st.session_state["play_auto_done_pending"] = True


def _reset_play_board() -> None:
    st.session_state.play_state = st.session_state.start_state
    st.session_state.play_moves = 0
    st.session_state.play_history = [st.session_state.start_state]
    st.session_state.play_assisted = False
    _clear_ai_replay()
    _clear_victory_state()


def _undo_play_step() -> None:
    if len(st.session_state.play_history) <= 1:
        return
    st.session_state.play_history.pop()
    st.session_state.play_state = st.session_state.play_history[-1]
    st.session_state.play_moves = max(0, st.session_state.play_moves - 1)
    _clear_ai_replay()
    _clear_victory_state()


def _direction_label(t, action: str) -> str:
    dir_labels = {
        "L": t("dir_L").split(" ")[0],
        "R": t("dir_R").split(" ")[0],
        "U": t("dir_U").split(" ")[0],
        "D": t("dir_D").split(" ")[0],
    }
    return dir_labels.get(action, action)


def _render_play_board_panel(t, goal, solvable: bool) -> None:
    st.markdown(
        f"""
        <div class="play-panel-heading">
            <div class="play-panel-kicker">{escape(t("play_board_kicker"))}</div>
            <h2>{escape(t("play_board_title"))}</h2>
            <p>{escape(t("play_board_desc"))}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    render_clickable_board(
        st.session_state.play_state,
        key_prefix="play_main",
        highlight_correct=True,
        on_click_fn=_handle_play_slide,
        goal=goal,
    )


def _render_play_status_controls(t, goal, solvable: bool) -> None:
    h_play = HEURISTICS["Manhattan Distance"](st.session_state.play_state, goal=goal)
    correct = sum(1 for i, v in enumerate(st.session_state.play_state) if v == goal[i] and v != 0)
    status_items = [
        (t("play_moves"), st.session_state.play_moves),
        (t("play_manhattan"), h_play),
        (t("play_tiles_correct"), f"{correct}/15"),
        (t("play_solvable_label"), t("tc_yes") if solvable else t("tc_no")),
    ]
    status_markup = "".join(
        '<div class="play-status-card">'
        f'<div class="play-status-label">{escape(str(label))}</div>'
        f'<div class="play-status-value">{escape(str(value))}</div>'
        "</div>"
        for label, value in status_items
    )
    st.markdown(
        f'<div class="play-status-grid">{status_markup}</div>',
        unsafe_allow_html=True,
    )

    _render_victory_notice(t)

    reset_col, undo_col = st.columns(2)
    with reset_col:
        if st.button(t("play_reset_board"), key="btn_play_reset", width="stretch"):
            _reset_play_board()
            st.rerun()
    with undo_col:
        if st.button(
            t("play_undo"),
            key="btn_play_undo",
            disabled=len(st.session_state.play_history) <= 1,
            width="stretch",
        ):
            _undo_play_step()
            st.rerun()


def _render_solver_evidence(t, res) -> None:
    with st.expander(t("play_ai_evidence_title"), expanded=False):
        st.caption(t("play_ai_evidence_desc"))
        if st.session_state.get("play_auto_run"):
            st.info(t("play_ai_evidence_pause_hint"))
            return
        render_search_detail_table(res.trace, max_rows=24, key="play_ai_detail_step_slider")
        render_search_tree(res, max_nodes=24)


def _render_ai_solver_panel(t, goal) -> None:
    """Render A* controls that replay directly on the main puzzle board."""
    _ensure_ai_replay_state()

    st.markdown(
        f"""
        <div class="ai-solver-card">
            <div class="ai-solver-header">
                <div class="ai-solver-title-container">
                    <span class="ai-solver-badge">A* + Manhattan</span>
                    <h3>{escape(t("play_ai_solver"))}</h3>
                </div>
            </div>
            <p class="ai-solver-desc">{escape(t("play_ai_desc"))}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.session_state.pop("play_auto_done_pending", False):
        st.success(t("play_auto_done"))

    solve_col, clear_col = st.columns([1, 1])
    with solve_col:
        if st.button(t("play_ai_solve_btn"), key="btn_ai_solve", type="primary", width="stretch"):
            if st.session_state.play_state == goal:
                st.info(t("play_ai_already_goal"))
            elif not is_solvable(st.session_state.play_state, goal):
                st.error(t("play_ai_unsolvable"))
            else:
                with st.spinner(t("play_ai_running")):
                    result = a_star(
                        start=st.session_state.play_state,
                        goal=goal,
                        heuristic="Manhattan Distance",
                        timeout=30.0,
                    )
                if result.success:
                    _store_ai_replay_result(result)
                    st.success(t("play_ai_solved_msg", steps=len(result.actions)))
                else:
                    st.error(t("play_ai_error", error=result.message))
    with clear_col:
        if st.session_state.play_solution_path:
            if st.button(t("play_ai_clear_btn"), key="btn_ai_clear", width="stretch"):
                _clear_ai_replay()
                st.rerun()

    path = st.session_state.play_solution_path
    res = st.session_state.play_solution_res
    idx = int(st.session_state.get("play_solution_idx", 0))
    replay_state = path[idx] if path else st.session_state.play_state

    if not path or not res:
        st.caption(t("play_ai_replay_hint"))
        return

    metric_cols = st.columns(2)
    metric_cols[0].metric(t("play_solution_steps"), len(res.actions))
    metric_cols[1].metric(t("mc_expanded"), res.nodes_expanded)
    metric_cols = st.columns(2)
    metric_cols[0].metric(t("mc_max_f"), res.max_frontier_size)
    metric_cols[1].metric(t("mc_runtime"), f"{res.runtime:.4f}s")

    st.markdown(
        t(
            "play_ai_step_summary",
            step=idx,
            total=len(res.actions),
            moves=len(res.actions),
            manhattan=HEURISTICS["Manhattan Distance"](replay_state, goal=goal),
        )
    )

    if idx < len(res.actions):
        st.markdown(t("play_ai_next_action", act=_direction_label(t, res.actions[idx])))
    else:
        st.success(t("play_ai_reached_goal"))

    ctrl_col1, ctrl_col2, ctrl_col3, ctrl_col4 = st.columns(4)
    with ctrl_col1:
        if st.button(
            t("play_prev_step"),
            key="btn_play_prev",
            disabled=(idx == 0),
            width="stretch",
        ):
            _apply_ai_replay_step(idx - 1)
            st.rerun()
    with ctrl_col2:
        if st.button(
            t("play_next_step"),
            key="btn_play_next",
            disabled=(idx >= len(path) - 1),
            width="stretch",
        ):
            _apply_ai_replay_step(idx + 1)
            st.rerun()
    with ctrl_col3:
        if st.button(
            t("play_auto_run"),
            key="btn_play_auto",
            disabled=(idx >= len(path) - 1),
            width="stretch",
        ):
            st.session_state.play_auto_run = True
            _advance_auto_replay_one_step()
            st.rerun()
    with ctrl_col4:
        if st.button(
            t("play_stop_run"),
            key="btn_play_pause",
            disabled=not st.session_state.get("play_auto_run", False),
            width="stretch",
        ):
            st.session_state.play_auto_run = False
            st.rerun()

    speed_options = {
        t("anim_per_step", sec=value): value
        for value in (0.15, 0.25, 0.35, 0.5, 0.8)
    }
    speed_labels = list(speed_options)
    default_speed = st.session_state.get("play_replay_speed", 0.35)
    default_idx = list(speed_options.values()).index(default_speed) if default_speed in speed_options.values() else 2
    speed_label = st.selectbox(
        t("anim_speed"),
        speed_labels,
        index=default_idx,
        key="play_replay_speed_label",
    )
    st.session_state.play_replay_speed = speed_options[speed_label]

    slider_val = st.slider(t("play_curr_step"), 0, len(res.actions), idx, key="play_slider_val")
    if slider_val != idx:
        _apply_ai_replay_step(slider_val)
        st.rerun()

    if 0 < idx <= len(res.actions):
        act_label = _direction_label(t, res.actions[idx - 1])
        st.markdown(t("play_action_performed", step=idx, total=len(res.actions), act=act_label))

    _render_solver_evidence(t, res)


def _render_play_workbench_content(t, goal, solvable: bool) -> None:
    _advance_auto_replay_one_step()
    board_col, solver_col = st.columns([1.08, 0.92], gap="large")
    with board_col:
        _render_play_board_panel(t, goal, solvable)
    with solver_col:
        _render_ai_solver_panel(t, goal)
    _render_play_status_controls(t, goal, solvable)


def _render_play_workbench(t, goal, solvable: bool) -> None:
    run_every = (
        st.session_state.get("play_replay_speed", 0.35)
        if st.session_state.get("play_auto_run", False)
        else None
    )
    st.fragment(run_every=run_every)(_render_play_workbench_content)(t, goal, solvable)


def _render_start_goal_reference(t, goal, solvable: bool) -> None:
    with st.expander(t("play_start_goal_reference"), expanded=False):
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            st.caption(t("play_start"))
            render_puzzle_board(st.session_state.start_state, size="small", goal=goal)
        with col2:
            st.caption(t("play_goal"))
            render_puzzle_board(goal, highlight_correct=False, size="small", goal=goal)
        with col3:
            start_h = HEURISTICS["Manhattan Distance"](st.session_state.start_state, goal=goal)
            st.metric(t("play_manhattan"), start_h)
            st.metric(t("play_solvable_label"), t("tc_yes") if solvable else t("tc_no"))
        render_exam_path("Play", t=t)


def _render_optional_image_panel(t, goal) -> None:
    with st.expander(t("play_optional_image_panel"), expanded=False):
        st.caption(t("play_upload_desc"))
        uploaded_img = st.file_uploader(
            t("play_upload_label"),
            type=["png", "jpg", "jpeg", "webp"],
            key="puzzle_img",
        )
        if uploaded_img:
            tiles = process_uploaded_image(uploaded_img)
            if tiles:
                st.session_state.image_tiles = tiles
                st.session_state.image_active = True
                st.success(t("play_img_loaded", count=len(tiles)))
            else:
                st.error(t("play_img_failed"))
        if st.button(t("play_remove_img"), key="remove_img"):
            st.session_state.image_tiles = {}
            st.session_state.image_active = False

        has_image = bool(st.session_state.get("image_tiles"))
        if not has_image:
            st.info(t("play_preview_none"))
            return

        col_board, col_preview = st.columns([1.18, 0.82], gap="large")
        with col_board:
            st.markdown('<div class="play-image-game-frame">', unsafe_allow_html=True)
            render_image_board(
                st.session_state.play_state,
                st.session_state.image_tiles,
                key_prefix="play_image",
                highlight_correct=True,
                on_click_fn=_handle_play_slide,
                show_numbers=st.session_state.get("show_numbers", True),
                action_labels={
                    "L": t("slide_right"),
                    "R": t("slide_left"),
                    "U": t("slide_down"),
                    "D": t("slide_up"),
                },
                goal=goal,
            )
            st.markdown("</div>", unsafe_allow_html=True)
        with col_preview:
            st.markdown(
                f'<div class="play-preview-card"><div class="image-preview-title">{escape(t("play_target_preview"))}</div>',
                unsafe_allow_html=True,
            )
            if uploaded_img:
                st.image(uploaded_img, width="stretch")
            elif "sample_select" in st.session_state:
                choice = st.session_state.sample_select
                from ui.sample_images import get_full_sample_image
                try:
                    preview_img_data = get_full_sample_image(choice)
                    if preview_img_data:
                        st.image(preview_img_data, width="stretch")
                    else:
                        st.caption(t("play_preview_fail"))
                except Exception as e:
                    st.caption(t("play_preview_error", error=e))
            else:
                st.info(t("play_preview_none"))
            st.markdown("</div>", unsafe_allow_html=True)


def _render_challenge_panel(t, goal) -> None:
    with st.expander(t("play_challenge_title"), expanded=False):
        st.caption(t("play_challenge_desc"))
        if st.button(t("play_prove_optimal"), key="btn_prove_optimal"):
            with st.spinner(t("play_computing_certificate")):
                proof_result = a_star(
                    start=st.session_state.play_start_ref,
                    goal=goal,
                    heuristic="Linear Conflict",
                    timeout=30.0,
                    max_nodes=300000,
                )
            st.session_state.play_optimal_result = proof_result

        proof_result = st.session_state.get("play_optimal_result")
        if proof_result:
            if proof_result.success and proof_result.optimality_proven:
                try:
                    player_cert = validate_player_run(st.session_state.play_history, goal)
                except Exception as e:
                    st.error(t("play_cert_validation_failed", error=e))
                    player_cert = None
                assisted = st.session_state.get("play_assisted", False)
                if player_cert is None:
                    return
                cert_cols = st.columns(4)
                cert_cols[0].metric(
                    t("play_cert_player_run"),
                    t("play_cert_legal") if player_cert.is_legal else t("play_cert_invalid"),
                )
                cert_cols[1].metric(t("play_cert_recorded_moves"), player_cert.move_count)
                cert_cols[2].metric(t("play_cert_reached_goal"), t("tc_yes") if player_cert.reaches_goal else t("tc_no"))
                cert_cols[3].metric(
                    t("play_cert_assistance"),
                    t("play_cert_ai_assisted") if assisted else t("play_cert_unassisted"),
                )
                st.success(
                    t("play_cert_verified", cost=proof_result.cost)
                )
                if not player_cert.is_legal:
                    st.error(t("play_cert_failed", message=player_cert.message))
                elif not player_cert.reaches_goal:
                    st.info(
                        t("play_cert_in_progress")
                    )
                else:
                    try:
                        score = score_challenge(player_cert.move_count, len(proof_result.actions))
                    except Exception as e:
                        st.error(t("play_score_failed", error=e))
                        return
                    score_cols = st.columns(4)
                    score_cols[0].metric(t("play_score_optimal_moves"), score.optimal_moves)
                    score_cols[1].metric(t("play_score_your_moves"), score.player_moves)
                    score_cols[2].metric(t("play_score_gap"), f"{score.gap:+d}")
                    score_cols[3].metric(t("play_score_efficiency"), f"{score.efficiency_percent:.1f}%")
                    if score.is_optimal_play and not assisted:
                        st.success(t("play_score_optimal_unassisted"))
                    elif score.is_optimal_play:
                        st.info(
                            t("play_score_optimal_assisted")
                        )
                    else:
                        st.warning(
                            t(
                                "play_score_longer",
                                mode=t("play_cert_ai_assisted") if assisted else t("play_cert_unassisted"),
                                gap=score.gap,
                            )
                        )
            else:
                st.warning(t("play_no_opt_cert", message=proof_result.message))


def render_play_tab(t, solvable: bool, global_lang: str) -> None:
    goal = st.session_state.get("goal_state", GOAL_STATE)
    st.title(t("play_title"))
    st.markdown(
        f"""
        <div class="play-compact-strip">
            <div class="play-compact-kicker">{escape(t("play_hero_kicker"))}</div>
            <h2>{escape(t("play_hero_title"))}</h2>
            <p>{escape(t("play_page_purpose"))}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    _ensure_play_state(goal)
    _ensure_ai_replay_state()
    _render_play_workbench(t, goal, solvable)
    _render_start_goal_reference(t, goal, solvable)
    _render_optional_image_panel(t, goal)
    _render_challenge_panel(t, goal)
