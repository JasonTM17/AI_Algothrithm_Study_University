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
    render_solution_steps,
)
from ui.sample_images import SAMPLE_IMAGES, generate_sample_tiles

VICTORY_MESSAGE_KEYS = (
    "play_victory_1",
    "play_victory_2",
    "play_victory_3",
    "play_victory_4",
    "play_victory_5",
)

PLAY_TEXT_FALLBACKS = {
    "play_ai_solver": "A* Search từng bước",
    "play_ai_desc": "A* mở rộng state có f(n)=g(n)+h(n) nhỏ nhất, với h(n) là Manhattan Distance.",
    "play_ai_solve_btn": "Chạy A* từng bước",
    "play_ai_algorithm_label": "Thuật toán",
    "play_ai_eval_label": "Hàm đánh giá",
    "play_ai_heuristic_label": "Heuristic",
    "play_ai_cost_label": "Cost model",
    "play_ai_cost_value": "Mỗi bước trượt ô trống hợp lệ có cost 1",
    "play_ai_goal_label": "Goal test",
    "play_ai_goal_value": "State hiện tại bằng goal đã chọn",
    "play_ai_optimality_label": "Tính tối ưu",
    "play_ai_optimality_value": "Đúng khi h(n) admissible/consistent và search không bị giới hạn tài nguyên",
    "play_ai_current_step_title": "Bước replay A* hiện tại",
    "play_ai_g_metric": "g(n)",
    "play_ai_h_metric": "h(n)",
    "play_ai_f_metric": "f(n)",
    "play_ai_frontier_reached_metric": "Frontier / Reached",
    "play_ai_trace_not_captured": "State replay ban đầu; trace bắt đầu sau khi mở rộng node.",
    "play_ai_step_evidence": "Action trước: **{prev}** | Action kế tiếp: **{next}** | Lý do trace: `{reason}`",
}


def _play_text(t, key: str, **kwargs) -> str:
    fallback = PLAY_TEXT_FALLBACKS.get(key, key)
    try:
        value = t(key, **kwargs)
    except Exception:
        value = fallback.format(**kwargs) if kwargs else fallback
    if not isinstance(value, str) or value == key or value.lower() == key.lower():
        value = fallback.format(**kwargs) if kwargs else fallback
    return value


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
    st.session_state.pop("play_auto_pending_first_tick", None)
    st.session_state.pop("play_auto_start_pending", None)
    st.session_state.pop("play_ai_solved_steps_pending", None)
    st.session_state.pop("play_slider_val", None)
    st.session_state.pop("play_slider_version", None)
    for key in list(st.session_state):
        if str(key).startswith("play_slider_val_"):
            st.session_state.pop(key, None)


def _store_ai_replay_result(result) -> None:
    """Persist an AI solution together with the manual history it extends."""
    st.session_state.play_solution_path = result.path
    st.session_state.play_solution_actions = result.actions
    st.session_state.play_solution_idx = 0
    st.session_state.play_solution_res = result
    st.session_state.play_solution_base_history = list(st.session_state.play_history)
    st.session_state.play_solution_base_moves = st.session_state.play_moves
    st.session_state.play_auto_run = False
    st.session_state.pop("play_auto_done_pending", None)
    st.session_state.pop("play_auto_pending_first_tick", None)
    st.session_state.play_slider_version = st.session_state.get("play_slider_version", 0) + 1


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

    previous_index = int(st.session_state.get("play_solution_idx", 0))
    st.session_state.play_solution_idx = bounded_index
    if previous_index != bounded_index:
        st.session_state.play_slider_version = st.session_state.get("play_slider_version", 0) + 1
    st.session_state.play_state = path[bounded_index]
    st.session_state.play_history = base_history + list(path[1:bounded_index + 1])
    st.session_state.play_moves = base_moves + bounded_index
    if bounded_index > 0:
        st.session_state.play_assisted = True
    if bounded_index >= len(path) - 1 and st.session_state.get("play_auto_run", False):
        st.session_state["play_auto_done_pending"] = True


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


def _ensure_play_board_mode() -> None:
    labels_to_values = {
        "Number board": "number",
        "Image puzzle": "image",
        "Bàn số": "number",
        "Puzzle ảnh": "image",
    }
    stored_mode = st.session_state.get("play_board_mode")
    if stored_mode in labels_to_values:
        st.session_state.play_board_mode = labels_to_values[stored_mode]
    elif stored_mode not in {"number", "image"}:
        st.session_state.play_board_mode = (
            "image"
            if st.session_state.get("image_active") and st.session_state.get("image_tiles")
            else "number"
        )


def _sync_play_board_mode_from_choice(mode_options: dict[str, str]) -> None:
    """Copy the radio label into the stable internal board-mode value."""
    choice = st.session_state.get("play_board_mode_choice")
    mode = mode_options.get(choice, st.session_state.get("play_board_mode", "number"))
    if mode not in {"number", "image"}:
        mode = "number"
    st.session_state.play_board_mode = mode
    st.session_state.play_board_mode_choice_synced_to = mode


def _load_default_image_tiles() -> bool:
    """Load the selected built-in image so the image puzzle works immediately."""
    sample_name = st.session_state.get("sample_select")
    if sample_name not in SAMPLE_IMAGES:
        sample_name = next(iter(SAMPLE_IMAGES), None)
    if not sample_name:
        return False

    tiles = generate_sample_tiles(sample_name)
    if not tiles:
        return False

    st.session_state.image_tiles = tiles
    st.session_state.image_active = True
    st.session_state.play_image_sample_name = sample_name
    return True


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
    if "play_slider_version" not in st.session_state:
        st.session_state.play_slider_version = 0


def _advance_auto_replay_one_step() -> None:
    """Advance one solver frame; Streamlit fragments call this repeatedly."""
    if not st.session_state.get("play_auto_run", False):
        return
    if st.session_state.pop("play_auto_pending_first_tick", False):
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

    mode_options = {
        t("play_mode_number"): "number",
        t("play_mode_image"): "image",
    }
    stored_mode = st.session_state.get("play_board_mode", "number")
    if stored_mode not in mode_options.values():
        stored_mode = "number"
        st.session_state.play_board_mode = stored_mode
    selected_label = next(
        label for label, value in mode_options.items() if value == stored_mode
    )
    current_choice = st.session_state.get("play_board_mode_choice")
    current_choice_mode = mode_options.get(current_choice)
    synced_mode = st.session_state.get("play_board_mode_choice_synced_to")
    if current_choice_mode is None or synced_mode != stored_mode:
        st.session_state.play_board_mode_choice = selected_label
        st.session_state.play_board_mode_choice_synced_to = stored_mode

    mode_label = st.radio(
        t("play_board_mode"),
        options=list(mode_options),
        index=list(mode_options).index(selected_label),
        key="play_board_mode_choice",
        on_change=_sync_play_board_mode_from_choice,
        args=(mode_options,),
        horizontal=True,
        width="stretch",
    )
    mode = mode_options.get(mode_label, "number")
    st.session_state.play_board_mode = mode
    st.session_state.play_board_mode_choice_synced_to = mode

    if mode == "image":
        _render_image_mode_board(t, goal)
        return

    render_clickable_board(
        st.session_state.play_state,
        key_prefix="play_main",
        highlight_correct=True,
        on_click_fn=_handle_play_slide,
        goal=goal,
    )


def _render_image_mode_board(t, goal) -> None:
    """Keep uploaded imagery in the primary play surface instead of a hidden panel."""
    board_slot = st.empty()
    status_messages: list[tuple[str, str]] = []

    if not st.session_state.get("image_tiles"):
        if _load_default_image_tiles():
            status_messages.append(
                ("caption", t("play_default_image_loaded", name=st.session_state.play_image_sample_name))
            )

    with st.expander(t("play_upload_label"), expanded=not bool(st.session_state.get("image_tiles"))):
        uploaded_img = st.file_uploader(
            t("play_upload_label"),
            type=["png", "jpg", "jpeg", "webp"],
            key="puzzle_img",
            label_visibility="collapsed",
        )
        if uploaded_img:
            image_signature = (uploaded_img.name, uploaded_img.size)
            if st.session_state.get("play_uploaded_image_signature") != image_signature:
                tiles = process_uploaded_image(uploaded_img)
                if tiles:
                    st.session_state.image_tiles = tiles
                    st.session_state.image_active = True
                    st.session_state.play_uploaded_image_signature = image_signature
                    status_messages.append(("success", t("play_img_loaded", count=len(tiles))))
                else:
                    status_messages.append(("error", t("play_img_failed")))

    image_available = bool(st.session_state.get("image_tiles"))
    if image_available:
        image_action_col, image_status_col, image_target_col = st.columns([1, 1, 1])
        with image_action_col:
            if st.button(t("play_remove_img"), key="remove_img", width="stretch"):
                st.session_state.image_tiles = {}
                st.session_state.image_active = False
                st.session_state.play_board_mode = "number"
                st.session_state.play_board_mode_choice_synced_to = "number"
                st.session_state.pop("play_uploaded_image_signature", None)
                st.rerun()
        with image_status_col:
            st.session_state.show_numbers = st.checkbox(
                t("play_show_numbers"),
                value=st.session_state.get("show_numbers", False),
                key="chk_show_numbers",
            )
        with image_target_col:
            with st.popover(t("play_view_goal_image")):
                st.caption(t("play_complete_image_to_arrange"))
                st.markdown('<div style="pointer-events: none; width: 300px;">', unsafe_allow_html=True)
                render_image_board(
                    goal,
                    st.session_state.image_tiles,
                    key_prefix="play_target_image_preview",
                    highlight_correct=False,
                    on_click_fn=None,
                    show_numbers=False,
                )
                st.markdown("</div>", unsafe_allow_html=True)

    with board_slot.container():
        for message_type, message in status_messages:
            if message_type == "success":
                st.success(message)
            elif message_type == "error":
                st.error(message)
            else:
                st.caption(message)

        if not image_available:
            st.info(t("play_image_missing"))
            return

        render_image_board(
            st.session_state.play_state,
            st.session_state.image_tiles,
            key_prefix="play_main_image",
            highlight_correct=True,
            on_click_fn=_handle_play_slide,
            show_numbers=st.session_state.get("show_numbers", False),
            action_labels={
                "L": t("slide_right"),
                "R": t("slide_left"),
                "U": t("slide_down"),
                "D": t("slide_up"),
            },
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
    with st.expander(t("play_ai_evidence_title"), expanded=True):
        st.caption(t("play_ai_evidence_desc"))
        render_search_detail_table(res.trace, max_rows=24, key="play_ai_detail_step_slider")
        if st.session_state.get("play_auto_run"):
            st.info(t("play_ai_evidence_pause_hint"))
        render_search_tree(
            res,
            max_nodes=12,
            compact=True,
            board_mode=st.session_state.get("play_board_mode", "number"),
            image_tiles=st.session_state.get("image_tiles"),
        )


def _render_full_width_solver_evidence(t) -> None:
    """Keep trajectory and search evidence out of the narrow solver column."""
    path = st.session_state.get("play_solution_path")
    res = st.session_state.get("play_solution_res")
    if not path or not res:
        return

    render_solution_steps(
        path,
        res.actions,
        board_mode=st.session_state.get("play_board_mode", "number"),
        image_tiles=st.session_state.get("image_tiles"),
        current_step=int(st.session_state.get("play_solution_idx", 0)),
    )
    _render_solver_evidence(t, res)


def _trace_step_for_state(trace: list, state: tuple[int, ...]):
    """Find the captured A* trace row that generated the displayed replay state."""
    for step in trace:
        if step.state == state:
            return step
    return None


def _render_ai_academic_contract(t) -> None:
    rows = [
        (_play_text(t, "play_ai_algorithm_label"), "A* Search"),
        (_play_text(t, "play_ai_eval_label"), "f(n)=g(n)+h(n)"),
        (_play_text(t, "play_ai_heuristic_label"), "Manhattan Distance"),
        (_play_text(t, "play_ai_cost_label"), _play_text(t, "play_ai_cost_value")),
        (_play_text(t, "play_ai_goal_label"), _play_text(t, "play_ai_goal_value")),
        (_play_text(t, "play_ai_optimality_label"), _play_text(t, "play_ai_optimality_value")),
    ]
    markup = "".join(
        '<div class="ai-contract-row">'
        f'<span>{escape(label)}</span>'
        f'<strong>{escape(value)}</strong>'
        "</div>"
        for label, value in rows
    )
    st.markdown(
        f'<div class="ai-contract-grid">{markup}</div>',
        unsafe_allow_html=True,
    )


def _render_ai_step_evidence(t, res, idx: int, replay_state: tuple[int, ...], goal) -> None:
    current_h = HEURISTICS["Manhattan Distance"](replay_state, goal=goal)
    current_g = idx
    current_f = current_g + current_h
    trace_step = _trace_step_for_state(res.trace, replay_state)
    frontier_size = trace_step.frontier_size if trace_step else res.max_frontier_size
    reached_size = trace_step.reached_size if trace_step else res.reached_size
    previous_action = (
        _direction_label(t, res.actions[idx - 1])
        if 0 < idx <= len(res.actions)
        else t("dir_start_short")
    )
    next_action = (
        _direction_label(t, res.actions[idx])
        if idx < len(res.actions)
        else t("anim_goal")
    )
    trace_reason = trace_step.reason if trace_step else _play_text(t, "play_ai_trace_not_captured")

    st.markdown(f"#### {_play_text(t, 'play_ai_current_step_title')}")
    evidence_items = [
        (_play_text(t, "play_ai_g_metric"), str(current_g)),
        (_play_text(t, "play_ai_h_metric"), f"{current_h:.1f}"),
        (_play_text(t, "play_ai_f_metric"), f"{current_f:.1f}"),
        (_play_text(t, "play_ai_frontier_reached_metric"), f"{frontier_size} / {reached_size}"),
    ]
    evidence_markup = "".join(
        '<div class="play-ai-evidence-card">'
        f'<span>{escape(label)}</span>'
        f'<strong>{escape(value)}</strong>'
        "</div>"
        for label, value in evidence_items
    )
    st.markdown(
        f'<div class="play-ai-evidence-grid">{evidence_markup}</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        _play_text(
            t,
            "play_ai_step_evidence",
            prev=previous_action,
            next=next_action,
            reason=trace_reason,
        )
    )


def _render_ai_solver_panel(t, goal) -> None:
    """Render A* controls that replay directly on the main puzzle board."""
    _ensure_ai_replay_state()

    st.markdown(
        f"""
        <div class="ai-solver-card">
            <div class="ai-solver-header">
                <div class="ai-solver-title-container">
                    <span class="ai-solver-badge">A* Search</span>
                    <h3>{escape(_play_text(t, "play_ai_solver"))}</h3>
                </div>
            </div>
            <p class="ai-solver-desc">{escape(_play_text(t, "play_ai_desc"))}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    _render_ai_academic_contract(t)

    if st.session_state.pop("play_auto_done_pending", False):
        st.success(t("play_auto_done"))
    solved_steps_pending = st.session_state.pop("play_ai_solved_steps_pending", None)
    if solved_steps_pending is not None:
        st.success(t("play_ai_solved_msg", steps=solved_steps_pending))

    solve_col, clear_col = st.columns([1, 1])
    with solve_col:
        if st.button(_play_text(t, "play_ai_solve_btn"), key="btn_ai_solve", type="primary", width="stretch"):
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
                    st.session_state.play_ai_solved_steps_pending = len(result.actions)
                    st.rerun()
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
            st.session_state.play_auto_pending_first_tick = True
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

    slider_key = f"play_slider_val_{st.session_state.get('play_slider_version', 0)}"
    slider_val = st.slider(t("play_curr_step"), 0, len(res.actions), idx, key=slider_key)
    if slider_val != idx:
        _apply_ai_replay_step(slider_val)
        st.rerun()

    _render_ai_step_evidence(t, res, idx, replay_state, goal)

    if 0 < idx <= len(res.actions):
        act_label = _direction_label(t, res.actions[idx - 1])
        st.markdown(t("play_action_performed", step=idx, total=len(res.actions), act=act_label))

def _render_play_workbench_content(t, goal, solvable: bool) -> None:
    _advance_auto_replay_one_step()
    board_col, solver_col = st.columns([1.08, 0.92], gap="large")
    with board_col:
        _render_play_board_panel(t, goal, solvable)
    with solver_col:
        _render_ai_solver_panel(t, goal)
    _render_full_width_solver_evidence(t)
    _render_play_status_controls(t, goal, solvable)
    _render_start_goal_reference(t, goal, solvable)
    _render_challenge_panel(t, goal)


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
                if not player_cert.is_legal:
                    st.error(t("play_cert_failed", message=player_cert.message))
                else:
                    st.success(t("play_cert_verified", cost=proof_result.cost))
                    if not player_cert.reaches_goal:
                        st.info(t("play_cert_in_progress"))
                        return
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
    _ensure_play_board_mode()
    _ensure_ai_replay_state()
    _render_play_workbench(t, goal, solvable)
