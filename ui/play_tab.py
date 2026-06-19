"""Play tab for the Streamlit app."""

import time

import streamlit as st

from algorithms.informed import a_star
from core.heuristics import HEURISTICS
from core.puzzle import GOAL_STATE, is_solvable, _move_blank
from ui.academic_panels import render_academic_header, render_exam_path
from ui.components import (
    process_uploaded_image,
    render_clickable_board,
    render_image_board,
    render_puzzle_board,
)


def _handle_play_slide(direction: str) -> None:
    ns = _move_blank(st.session_state.play_state, direction)
    if ns:
        st.session_state.play_state = ns
        st.session_state.play_moves += 1


def render_play_tab(t, solvable: bool, global_lang: str) -> None:
    st.title("15-Puzzle | Interactive Board")
    render_academic_header(
        "15-Puzzle AI Solver Lab",
        "A final-exam dashboard for demonstrating PEAS, state-space search, heuristics, and the boundary between real solvers and educational extensions.",
    )
    render_exam_path("Play")

    col1, col2 = st.columns([1, 1])
    with col1:
        st.subheader("Start State")
        render_puzzle_board(st.session_state.start_state)
        h = HEURISTICS["Manhattan Distance"](st.session_state.start_state)
        st.metric("Manhattan Distance", h)
        st.metric("Is Solvable", "Yes" if solvable else "No")

    with col2:
        st.subheader("Goal State")
        render_puzzle_board(GOAL_STATE, highlight_correct=False)
        st.metric("Manhattan Distance", 0)

    st.markdown("---")

    # Image import section
    st.subheader("Custom Image")
    st.markdown("Upload an image to use as puzzle tiles. The image will be split into 15 pieces.")
    uploaded_img = st.file_uploader("Upload puzzle image", type=["png", "jpg", "jpeg", "webp"], key="puzzle_img")
    if uploaded_img:
        tiles = process_uploaded_image(uploaded_img)
        if tiles:
            st.session_state.image_tiles = tiles
            st.session_state.image_active = True
            st.success(f"Image loaded! {len(tiles)} tile pieces created.")
        else:
            st.error("Failed to process image. Make sure it's a valid image file.")
    if st.button("Remove Image", key="remove_img"):
        st.session_state.image_tiles = {}
        st.session_state.image_active = False

    st.markdown("---")
    st.subheader("Manual Play")
    st.markdown("Click any tile adjacent to the blank space to slide it.")

    if "play_state" not in st.session_state:
        st.session_state.play_state = st.session_state.start_state
        st.session_state.play_moves = 0

    if "play_start_ref" not in st.session_state:
        st.session_state.play_start_ref = st.session_state.start_state
    if st.session_state.play_start_ref != st.session_state.start_state:
        st.session_state.play_state = st.session_state.start_state
        st.session_state.play_moves = 0
        st.session_state.play_start_ref = st.session_state.start_state

    has_image = "image_tiles" in st.session_state and st.session_state.image_tiles
    if has_image:
        col_board, col_preview = st.columns([5, 3])
        with col_board:
            render_image_board(
                st.session_state.play_state,
                st.session_state.image_tiles,
                key_prefix="play",
                highlight_correct=True,
                on_click_fn=_handle_play_slide,
                show_numbers=st.session_state.get("show_numbers", True),
            )
        with col_preview:
            st.markdown('<div class="image-preview-title">Target Preview (Ảnh Gốc)</div>', unsafe_allow_html=True)
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
                        st.caption("Preview could not be generated.")
                except Exception as e:
                    st.caption(f"Error loading preview: {e}")
            else:
                st.info("No preview available.")
    else:
        render_clickable_board(
            st.session_state.play_state,
            key_prefix="play",
            highlight_correct=True,
            on_click_fn=_handle_play_slide,
        )

    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        st.metric("Moves", st.session_state.play_moves)
    with col_m2:
        h_play = HEURISTICS["Manhattan Distance"](st.session_state.play_state)
        st.metric("Manhattan Dist", h_play)
    with col_m3:
        correct = sum(1 for i, v in enumerate(st.session_state.play_state) if v == GOAL_STATE[i] and v != 0)
        st.metric("Tiles Correct", f"{correct}/15")

    if st.session_state.play_state == GOAL_STATE:
        st.balloons()
        st.success(f"You solved it in {st.session_state.play_moves} moves!")

    col_reset1, col_reset2 = st.columns(2)
    with col_reset1:
        if st.button("Reset Play Board"):
            st.session_state.play_state = st.session_state.start_state
            st.session_state.play_moves = 0
            st.session_state.play_solution_path = None
            st.session_state.play_solution_actions = None
            st.session_state.play_solution_idx = 0
            st.session_state.play_auto_run = False
            st.rerun()

    # ── AI Auto-Solver ──────────────────────────────────────
    st.markdown("---")
    
    # Premium AI Solver Card
    ai_title = t("play_ai_solver")
    ai_desc = t("play_ai_desc")
    st.markdown(f"""
    <div class="ai-solver-card">
        <div class="ai-solver-header">
            <div class="ai-solver-title-container">
                <span class="ai-solver-badge">OPTIMIZATION</span>
                <h3>{ai_title}</h3>
            </div>
        </div>
        <p class="ai-solver-desc">{ai_desc}</p>
    </div>
    """, unsafe_allow_html=True)

    if "play_solution_path" not in st.session_state:
        st.session_state.play_solution_path = None
    if "play_solution_actions" not in st.session_state:
        st.session_state.play_solution_actions = None
    if "play_solution_idx" not in st.session_state:
        st.session_state.play_solution_idx = 0
    if "play_auto_run" not in st.session_state:
        st.session_state.play_auto_run = False

    col_solve1, col_solve2 = st.columns(2)
    with col_solve1:
        if st.button(t("play_ai_solve_btn_full"), key="btn_ai_solve"):
            if st.session_state.play_state == GOAL_STATE:
                st.info(t("play_ai_already_goal"))
            elif not is_solvable(st.session_state.play_state):
                st.error(t("play_ai_unsolvable"))
            else:
                with st.spinner(t("play_ai_running")):
                    res = a_star(
                        start=st.session_state.play_state,
                        goal=GOAL_STATE,
                        heuristic="Manhattan Distance",
                        timeout=30.0,
                    )
                    if res.success:
                        st.session_state.play_solution_path = res.path
                        st.session_state.play_solution_actions = res.actions
                        st.session_state.play_solution_idx = 0
                        st.session_state.play_solution_res = res
                        st.success(t("play_ai_solved_msg", steps=len(res.actions)))
                    else:
                        st.error(t("play_ai_error", error=res.message))
    with col_solve2:
        if st.session_state.play_solution_path:
            if st.button(t("play_ai_clear_btn"), key="btn_ai_clear"):
                st.session_state.play_solution_path = None
                st.session_state.play_solution_actions = None
                st.session_state.play_solution_idx = 0
                st.session_state.play_auto_run = False
                st.rerun()

    if st.session_state.play_solution_path:
        res = st.session_state.play_solution_res
        st.info(t("play_ai_solved_info", steps=len(res.actions), time=res.runtime, expanded=res.nodes_expanded, max_f=res.max_frontier_size))
        
        idx = st.session_state.play_solution_idx
        
        col_ctrl1, col_ctrl2, col_ctrl3 = st.columns(3)
        
        with col_ctrl1:
            if st.button(t("play_prev_step"), key="btn_play_prev", disabled=(idx == 0)):
                st.session_state.play_solution_idx -= 1
                st.session_state.play_state = st.session_state.play_solution_path[st.session_state.play_solution_idx]
                st.session_state.play_moves = st.session_state.play_solution_idx
                st.rerun()
                
        with col_ctrl2:
            if st.button(t("play_next_step"), key="btn_play_next", disabled=(idx >= len(st.session_state.play_solution_path) - 1)):
                st.session_state.play_solution_idx += 1
                st.session_state.play_state = st.session_state.play_solution_path[st.session_state.play_solution_idx]
                st.session_state.play_moves = st.session_state.play_solution_idx
                st.rerun()
                
        with col_ctrl3:
            if st.session_state.get("play_auto_run", False):
                if st.button(t("play_stop_run"), key="btn_play_stop"):
                    st.session_state.play_auto_run = False
                    st.rerun()
            else:
                if st.button(t("play_auto_run"), key="btn_play_auto", disabled=(idx >= len(st.session_state.play_solution_path) - 1)):
                    st.session_state.play_auto_run = True
                    st.rerun()
                    
        slider_val = st.slider(t("play_curr_step"), 0, len(res.actions), idx, key="play_slider_val")
        if slider_val != idx:
            st.session_state.play_solution_idx = slider_val
            st.session_state.play_state = st.session_state.play_solution_path[slider_val]
            st.session_state.play_moves = slider_val
            st.rerun()
                
        if idx > 0 and idx <= len(res.actions):
            act = res.actions[idx - 1]
            dir_labels = {
                "L": t("dir_L").split(" ")[0],
                "R": t("dir_R").split(" ")[0],
                "U": t("dir_U").split(" ")[0],
                "D": t("dir_D").split(" ")[0]
            }
            act_label = dir_labels.get(act, act)
            st.markdown(t("play_action_performed", step=idx, total=len(res.actions), act=act_label))
            
        if st.session_state.get("play_auto_run", False):
            if idx < len(st.session_state.play_solution_path) - 1:
                time.sleep(0.4)
                st.session_state.play_solution_idx += 1
                st.session_state.play_state = st.session_state.play_solution_path[st.session_state.play_solution_idx]
                st.session_state.play_moves = st.session_state.play_solution_idx
                st.rerun()
            else:
                st.session_state.play_auto_run = False
                st.success(t("play_auto_done"))
                st.rerun()
