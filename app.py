"""15-Puzzle AI Streamlit application."""

import streamlit as st

from core.puzzle import GOAL_STATE, is_solvable, scramble
from ui.advanced_tab import render_advanced_tab
from ui.components import render_puzzle_board, render_styles
from ui.sample_images import SAMPLE_IMAGES, generate_sample_tiles
from ui.localization import ENGLISH, VIETNAMESE, resolve_language, translate
from ui.play_tab import render_play_tab
from ui.run_tab import render_run_algorithm_tab
from ui.trace_tab import render_step_trace_tab
from ui.compare_tab import render_compare_tab
from ui.theory_tab import render_theory_tab
from ui.hand_tracing import render_hand_tracing_page
from ui.start_goal_controls import render_sidebar_start_goal_controls

st.set_page_config(
    page_title="15-Puzzle AI",
    page_icon="AI",
    layout="wide",
    initial_sidebar_state="collapsed",
)

render_styles()


# Initialize session state.
if "start_state" not in st.session_state:
    st.session_state.start_state = scramble(depth=10, seed=42)
if "goal_state" not in st.session_state:
    st.session_state.goal_state = GOAL_STATE
if "benchmark_results" not in st.session_state:
    st.session_state.benchmark_results = []
if "image_tiles" not in st.session_state:
    st.session_state.image_tiles = {}

# Sidebar.
st.session_state["global_lang_select"] = resolve_language(
    st.session_state.get("global_lang_select", VIETNAMESE)
)
st.sidebar.title("15-Puzzle AI")

with st.sidebar.expander(translate(st.session_state.global_lang_select, "sidebar_language_settings"), expanded=True):
    global_lang = st.selectbox(
        translate(st.session_state.global_lang_select, "language_select"),
        [VIETNAMESE, ENGLISH],
        key="global_lang_select",
    )
st.sidebar.caption(translate(global_lang, "app_sidebar_caption"))

# Translation helper function
def t(key, **kwargs):
    return translate(global_lang, key, **kwargs)

st.sidebar.markdown("---")

tab_options = {
    t("nav_play"): "Play",
    t("nav_run"): "Run Algorithm",
    t("nav_compare"): "Compare",
    t("nav_trace"): "Step Trace",
    t("nav_hand_trace"): "Hand-Tracing Practice",
    t("nav_theory"): "Theory",
    t("nav_advanced"): "Advanced"
}

selected_tab_label = st.sidebar.radio(
    t("demo_workflow"),
    list(tab_options.keys()),
    key="main_tab_label"
)
tab = tab_options[selected_tab_label]

st.sidebar.markdown("---")
render_sidebar_start_goal_controls(t)

solvable = is_solvable(st.session_state.start_state, st.session_state.goal_state)

# Keep the first Play viewport as a standard number puzzle. Image mode is an
# optional visual layer the user can enable from the sidebar or Play panel.
if "image_active" not in st.session_state:
    st.session_state.image_active = False
if st.session_state.image_active and not st.session_state.get("image_tiles"):
    default_img = list(SAMPLE_IMAGES.keys())[0]
    st.session_state.image_tiles = generate_sample_tiles(default_img)

with st.sidebar.expander(t("sidebar_image_setup"), expanded=False):
    sample_choice = st.selectbox(
        t("sb_builtin"),
        list(SAMPLE_IMAGES.keys()),
        key="sample_select",
        index=0,
    )
    if st.button(t("sb_load_img"), key="btn_load_sample"):
        st.session_state.image_tiles = generate_sample_tiles(sample_choice)
        st.session_state.image_active = True
        st.session_state.play_board_mode = "image"

    if "show_numbers" not in st.session_state:
        st.session_state.show_numbers = True
    st.session_state.show_numbers = st.checkbox(
        t("sb_show_num"),
        value=st.session_state.show_numbers,
        key="show_numbers_checkbox"
    )

with st.sidebar.expander(t("sidebar_active_contract"), expanded=False):
    st.caption(t("sidebar_active_contract_caption"))
    start_preview, goal_preview = st.columns(2)
    with start_preview:
        st.caption(t("active_start"))
        render_puzzle_board(st.session_state.start_state, highlight_correct=True, size="mini", goal=st.session_state.goal_state)
    with goal_preview:
        st.caption(t("active_goal"))
        render_puzzle_board(st.session_state.goal_state, highlight_correct=False, size="mini", goal=st.session_state.goal_state)
    if solvable:
        st.success(t("sb_solvable"))
    else:
        st.error(t("sb_unsolvable"))

# Main tab router.
if tab != "Play":
    if st.session_state.get("play_auto_run", False):
        st.session_state.play_auto_run = False

if tab == "Play":
    render_play_tab(t=t, solvable=solvable, global_lang=global_lang)
elif tab == "Run Algorithm":
    render_run_algorithm_tab(t=t)
elif tab == "Step Trace":
    render_step_trace_tab()
elif tab == "Hand-Tracing Practice":
    render_hand_tracing_page()
elif tab == "Compare":
    render_compare_tab(t=t)
elif tab == "Theory":
    render_theory_tab(t=t)
elif tab == "Advanced":
    render_advanced_tab(st.session_state.start_state, st.session_state.goal_state)
