"""15-Puzzle AI Streamlit application."""

import streamlit as st

from core.puzzle import GOAL_STATE, is_solvable, scramble
from ui.advanced_tab import render_advanced_tab
from ui.components import render_styles
from ui.sample_images import SAMPLE_IMAGES, generate_sample_tiles
from ui.localization import ENGLISH, VIETNAMESE, resolve_language, translate
from ui.play_tab import render_play_tab
from ui.run_tab import render_run_algorithm_tab
from ui.compare_tab import render_compare_tab
from ui.theory_tab import render_theory_tab
from ui.hand_tracing import render_hand_tracing_page
from ui.start_goal_controls import render_sidebar_start_goal_controls
from ui.web_gif_capture import render_web_gif_capture

TAB_ROUTES = (
    ("Play", "nav_play"),
    ("Run Algorithm", "nav_run"),
    ("Compare", "nav_compare"),
    ("Hand-Tracing Practice", "nav_hand_trace"),
    ("Theory", "nav_theory"),
    ("Advanced", "nav_advanced"),
)

st.set_page_config(
    page_title="15-Puzzle AI",
    page_icon="AI",
    layout="wide",
    initial_sidebar_state="collapsed",
)

render_styles()

capture_demo = st.query_params.get("capture_demo")
if capture_demo:
    try:
        capture_frame = int(st.query_params.get("capture_frame", 0))
    except (TypeError, ValueError):
        capture_frame = 0
    capture_image = str(st.query_params.get("capture_image", "0")) == "1"
    capture_run_params = {
        "max_depth": st.query_params.get("capture_max_depth"),
        "max_nodes": st.query_params.get("capture_max_nodes"),
        "timeout": st.query_params.get("capture_timeout"),
    }
    render_web_gif_capture(
        str(capture_demo),
        capture_frame,
        image_mode=capture_image,
        start_text=st.query_params.get("capture_start"),
        goal_text=st.query_params.get("capture_goal"),
        run_params=capture_run_params,
    )
    st.stop()


# Initialize session state.
if "start_state" not in st.session_state:
    st.session_state.start_state = scramble(depth=10, seed=42)
if "goal_state" not in st.session_state:
    st.session_state.goal_state = GOAL_STATE
if "benchmark_results" not in st.session_state:
    st.session_state.benchmark_results = []
if "image_tiles" not in st.session_state:
    st.session_state.image_tiles = {}


def _activate_selected_sample_image() -> None:
    """Apply a built-in image immediately when its selector changes."""
    sample_name = st.session_state.get("sample_select")
    tiles = generate_sample_tiles(sample_name) if sample_name in SAMPLE_IMAGES else {}
    if not tiles:
        return

    st.session_state.image_tiles = tiles
    st.session_state.image_active = True
    st.session_state.play_image_sample_name = sample_name
    st.session_state.play_board_mode = "image"
    st.session_state.pop("play_board_mode_choice_synced_to", None)
    st.session_state.play_uploaded_image_signature = None
    st.session_state.image_upload_version = int(
        st.session_state.get("image_upload_version", 0)
    ) + 1
    st.session_state.show_numbers = False
    st.session_state.show_numbers_checkbox = False
    st.session_state.chk_show_numbers = False

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

def _coerce_tab_value(value: object) -> str:
    """Map old labels, translated labels, or canonical routes to a stable tab route."""
    if str(value) in {
        "Step Trace",
        "Trace t\u1eebng b\u01b0\u1edbc",
        "Trace T\u1eebng B\u01b0\u1edbc Thu\u1eadt To\u00e1n",
    }:
        return "Run Algorithm"
    routes = {route for route, _ in TAB_ROUTES}
    if value in routes:
        return str(value)
    labels_to_routes = {}
    for route, label_key in TAB_ROUTES:
        labels_to_routes[translate(VIETNAMESE, label_key)] = route
        labels_to_routes[translate(ENGLISH, label_key)] = route
    return labels_to_routes.get(str(value), "Play")


def _sync_main_tab_from_label(labels: list[str], values: list[str]) -> None:
    selected = st.session_state.get("main_tab_label")
    st.session_state.main_tab_value = values[labels.index(selected)] if selected in labels else "Play"


pending_tab = st.session_state.pop("main_tab_request", None)
legacy_tab = st.session_state.get("main_tab_label")
if pending_tab is not None:
    st.session_state.main_tab_value = _coerce_tab_value(pending_tab)
    st.session_state.pop("main_tab_label", None)
elif isinstance(legacy_tab, str):
    st.session_state.main_tab_value = _coerce_tab_value(legacy_tab)
    st.session_state.pop("main_tab_label", None)

tab_values = [route for route, _ in TAB_ROUTES]
tab_labels = [t(label_key) for _, label_key in TAB_ROUTES]
active_tab_value = _coerce_tab_value(st.session_state.get("main_tab_value", "Play"))
st.session_state.main_tab_value = active_tab_value
active_tab_index = tab_values.index(active_tab_value)
if pending_tab is not None:
    st.session_state.main_tab_label = tab_labels[active_tab_index]

selected_tab_label = st.sidebar.radio(
    t("demo_workflow"),
    tab_labels,
    index=active_tab_index,
    key="main_tab_label",
    on_change=_sync_main_tab_from_label,
    args=(tab_labels, tab_values),
)
tab = tab_values[tab_labels.index(selected_tab_label)]
st.session_state.main_tab_value = tab

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
    st.selectbox(
        t("sb_builtin"),
        list(SAMPLE_IMAGES.keys()),
        key="sample_select",
        index=0,
        on_change=_activate_selected_sample_image,
    )

    if "show_numbers" not in st.session_state:
        st.session_state.show_numbers = False
    st.session_state.show_numbers = st.checkbox(
        t("sb_show_num"),
        value=st.session_state.show_numbers,
        key="show_numbers_checkbox"
    )

# Main tab router.
if tab != "Play":
    if st.session_state.get("play_auto_run", False):
        st.session_state.play_auto_run = False

if tab == "Play":
    render_play_tab(t=t, solvable=solvable, global_lang=global_lang)
elif tab == "Run Algorithm":
    render_run_algorithm_tab(t=t)
elif tab == "Hand-Tracing Practice":
    render_hand_tracing_page()
elif tab == "Compare":
    render_compare_tab(t=t)
elif tab == "Theory":
    render_theory_tab(t=t)
elif tab == "Advanced":
    render_advanced_tab(st.session_state.start_state, st.session_state.goal_state)
