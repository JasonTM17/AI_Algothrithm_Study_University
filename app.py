"""15-Puzzle AI Streamlit application."""

import streamlit as st

from core.puzzle import GOAL_STATE, TEACHING_PRESETS, is_solvable, parse_state, scramble
from ui.advanced_tab import render_advanced_tab
from ui.components import render_puzzle_board, render_styles
from ui.sample_images import SAMPLE_IMAGES, generate_sample_tiles
from ui.localization import LOC
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
if "benchmark_results" not in st.session_state:
    st.session_state.benchmark_results = []
if "image_tiles" not in st.session_state:
    st.session_state.image_tiles = {}

# Sidebar.
st.sidebar.title("15-Puzzle AI")
st.sidebar.caption("Bảng học thuật" if st.session_state.get("global_lang_select", "Tiếng Việt") == "Tiếng Việt" else "Academic Dashboard")
st.sidebar.markdown("---")

global_lang = st.sidebar.selectbox(
    "Ngôn ngữ / Language",
    ["Tiếng Việt", "English"],
    key="global_lang_select"
)

# Translation helper function
def t(key, **kwargs):
    text = LOC[global_lang].get(key, key)
    if kwargs:
        return text.format(**kwargs)
    return text

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
st.sidebar.subheader(t("sb_start_state"))

state_input_method = st.sidebar.radio(t("sb_input_method"), [t("sb_random"), t("sb_manual")], key="input_method")

if state_input_method == t("sb_random"):
    col_s1, col_s2 = st.sidebar.columns(2)
    with col_s1:
        scramble_depth = st.number_input(t("sb_depth"), 1, 50, 10, key="scramble_depth")
    with col_s2:
        scramble_seed = st.number_input(t("sb_seed"), 0, 99999, 42, key="scramble_seed")

    if st.sidebar.button(t("sb_generate"), key="btn_random"):
        st.session_state.start_state = scramble(depth=scramble_depth, seed=scramble_seed)

elif state_input_method == t("sb_manual"):
    manual_input = st.sidebar.text_area(
        t("sb_manual_desc"),
        value=" ".join(str(x) for x in st.session_state.start_state),
        key="manual_input",
        height=80,
    )
    if st.sidebar.button(t("sb_parse"), key="btn_parse"):
        try:
            st.session_state.start_state = parse_state(manual_input)
            st.sidebar.success(t("sb_parse_success"))
        except ValueError as e:
            st.sidebar.error(t("sb_parse_error", error=e))

teaching_preset_name = st.sidebar.selectbox(
    t("teaching_preset"),
    list(TEACHING_PRESETS.keys()),
    key="teaching_preset_select",
    help=t("teaching_preset_help"),
)
if st.sidebar.button(t("load_teaching_preset"), key="btn_load_teaching_preset"):
    preset = TEACHING_PRESETS[teaching_preset_name]
    st.session_state.start_state = preset["state"]
    st.sidebar.info(str(preset["purpose"]))

if st.sidebar.button(t("sb_reset_goal"), key="btn_reset"):
    st.session_state.start_state = GOAL_STATE

solvable = is_solvable(st.session_state.start_state)
if solvable:
    st.sidebar.success(t("sb_solvable"))
else:
    st.sidebar.error(t("sb_unsolvable"))

# Auto-load default sample image on first run only.
if "image_active" not in st.session_state:
    st.session_state.image_active = True
if st.session_state.image_active and not st.session_state.get("image_tiles"):
    default_img = list(SAMPLE_IMAGES.keys())[0]
    st.session_state.image_tiles = generate_sample_tiles(default_img)

def on_sample_image_change():
    st.session_state.image_tiles = generate_sample_tiles(st.session_state.sample_select)
    st.session_state.image_active = True

st.sidebar.markdown("---")
st.sidebar.subheader(t("sb_sample_img"))
sample_choice = st.sidebar.selectbox(
    t("sb_builtin"),
    list(SAMPLE_IMAGES.keys()),
    key="sample_select",
    index=0,
    on_change=on_sample_image_change,
)
if st.sidebar.button(t("sb_load_img"), key="btn_load_sample"):
    st.session_state.image_tiles = generate_sample_tiles(sample_choice)
    st.session_state.image_active = True

if "show_numbers" not in st.session_state:
    st.session_state.show_numbers = True
st.session_state.show_numbers = st.sidebar.checkbox(
    t("sb_show_num"),
    value=st.session_state.show_numbers,
    key="show_numbers_checkbox"
)

st.sidebar.markdown("---")
st.sidebar.subheader(t("sb_curr_start"))
with st.sidebar:
    render_puzzle_board(st.session_state.start_state, highlight_correct=True)

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
    render_advanced_tab(st.session_state.start_state)


if __name__ == "__main__":
    pass
