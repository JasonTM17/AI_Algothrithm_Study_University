"""15-Puzzle AI Streamlit application."""

import streamlit as st

from core.puzzle import GOAL_STATE, TEACHING_PRESETS, is_solvable, parse_state, scramble
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

st.set_page_config(
    page_title="15-Puzzle AI",
    page_icon="AI",
    layout="wide",
    initial_sidebar_state="auto",
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
    t("nav_trace"): "Step Trace",
    t("nav_hand_trace"): "Hand-Tracing Practice",
    t("nav_compare"): "Compare",
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
with st.sidebar.expander(t("sidebar_start_setup"), expanded=True):
    state_input_method = st.radio(t("sb_input_method"), [t("sb_random"), t("sb_manual")], key="input_method")

    if state_input_method == t("sb_random"):
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            scramble_depth = st.number_input(t("sb_depth"), 1, 50, 10, key="scramble_depth")
        with col_s2:
            scramble_seed = st.number_input(t("sb_seed"), 0, 99999, 42, key="scramble_seed")

        if st.button(t("sb_generate"), key="btn_random"):
            st.session_state.start_state = scramble(
                goal=st.session_state.goal_state,
                depth=scramble_depth,
                seed=scramble_seed,
            )

    elif state_input_method == t("sb_manual"):
        manual_input = st.text_area(
            t("sb_manual_desc"),
            value=" ".join(str(x) for x in st.session_state.start_state),
            key="manual_input",
            height=80,
        )
        if st.button(t("sb_parse"), key="btn_parse"):
            try:
                st.session_state.start_state = parse_state(manual_input)
                st.success(t("sb_parse_success"))
            except ValueError as e:
                st.error(t("sb_parse_error", error=e))

with st.sidebar.expander(t("sidebar_goal_setup"), expanded=False):
    goal_input = st.text_area(
        t("sb_goal_manual_desc"),
        value=" ".join(str(x) for x in st.session_state.goal_state),
        key="goal_manual_input",
        height=80,
    )
    goal_col1, goal_col2 = st.columns(2)
    with goal_col1:
        if st.button(t("sb_parse_goal"), key="btn_parse_goal"):
            try:
                st.session_state.goal_state = parse_state(goal_input)
                st.success(t("sb_goal_parse_success"))
                st.session_state.pop("last_result", None)
                st.session_state.benchmark_results = []
                st.rerun()
            except ValueError as e:
                st.error(t("sb_parse_error", error=e))
    with goal_col2:
        if st.button(t("sb_standard_goal"), key="btn_standard_goal"):
            st.session_state.goal_state = GOAL_STATE
            st.session_state.pop("last_result", None)
            st.session_state.benchmark_results = []
            st.rerun()
    if st.button(t("sb_reset_goal"), key="btn_reset"):
        st.session_state.start_state = st.session_state.goal_state

with st.sidebar.expander(t("sidebar_teaching_presets"), expanded=False):
    teaching_preset_name = st.selectbox(
        t("teaching_preset"),
        list(TEACHING_PRESETS.keys()),
        key="teaching_preset_select",
        help=t("teaching_preset_help"),
    )
    if st.button(t("load_teaching_preset"), key="btn_load_teaching_preset"):
        preset = TEACHING_PRESETS[teaching_preset_name]
        st.session_state.start_state = preset["state"]
        st.info(str(preset["purpose"]))

solvable = is_solvable(st.session_state.start_state, st.session_state.goal_state)

# Auto-load default sample image on first run only.
if "image_active" not in st.session_state:
    st.session_state.image_active = True
if st.session_state.image_active and not st.session_state.get("image_tiles"):
    default_img = list(SAMPLE_IMAGES.keys())[0]
    st.session_state.image_tiles = generate_sample_tiles(default_img)

def on_sample_image_change():
    st.session_state.image_tiles = generate_sample_tiles(st.session_state.sample_select)
    st.session_state.image_active = True

with st.sidebar.expander(t("sidebar_image_setup"), expanded=False):
    sample_choice = st.selectbox(
        t("sb_builtin"),
        list(SAMPLE_IMAGES.keys()),
        key="sample_select",
        index=0,
        on_change=on_sample_image_change,
    )
    if st.button(t("sb_load_img"), key="btn_load_sample"):
        st.session_state.image_tiles = generate_sample_tiles(sample_choice)
        st.session_state.image_active = True

    if "show_numbers" not in st.session_state:
        st.session_state.show_numbers = True
    st.session_state.show_numbers = st.checkbox(
        t("sb_show_num"),
        value=st.session_state.show_numbers,
        key="show_numbers_checkbox"
    )

with st.sidebar.expander(t("sidebar_active_contract"), expanded=True):
    render_puzzle_board(st.session_state.start_state, highlight_correct=True)
    st.caption(t("sb_curr_goal"))
    render_puzzle_board(st.session_state.goal_state, highlight_correct=False)
    if solvable:
        st.success(t("sb_solvable"))
    else:
        st.error(t("sb_unsolvable"))

# Main tab router.
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


if __name__ == "__main__":
    pass
