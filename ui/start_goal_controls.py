"""Shared controls for editing the active puzzle start and goal states."""

from __future__ import annotations

import streamlit as st

from core.puzzle import GOAL_STATE, TEACHING_PRESETS, parse_state, scramble
from ui.localization import VIETNAMESE, translate
from ui.start_goal_state import (
    apply_goal_state,
    apply_start_state,
    sync_state_input,
)


def _t(key: str, **kwargs) -> str:
    return translate(st.session_state.get("global_lang_select", VIETNAMESE), key, **kwargs)


def _notice_key(key_prefix: str) -> str:
    return f"{key_prefix}_notice"


def _finish_state_change(key_prefix: str, message: str, rerun_on_change: bool) -> None:
    if rerun_on_change:
        st.session_state[_notice_key(key_prefix)] = ("success", message)
        st.rerun()
    st.success(message)


def _render_pending_notice(key_prefix: str) -> None:
    notice = st.session_state.pop(_notice_key(key_prefix), None)
    if not notice:
        return
    level, message = notice
    getattr(st, level)(message)


def render_start_goal_editor(
    *,
    key_prefix: str = "active_contract",
    expanded: bool = True,
    rerun_on_change: bool = True,
) -> None:
    """Render a local editor for the shared start/goal contract."""
    with st.expander(_t("active_edit_title"), expanded=expanded):
        _render_pending_notice(key_prefix)
        st.caption(_t("active_edit_caption"))

        start_col, goal_col = st.columns(2)
        with start_col:
            st.markdown(f"**{_t('active_start')}**")
            depth_col, seed_col = st.columns(2)
            with depth_col:
                scramble_depth = st.number_input(
                    _t("sb_depth"),
                    1,
                    50,
                    int(st.session_state.get(f"{key_prefix}_depth", 10)),
                    key=f"{key_prefix}_depth",
                )
            with seed_col:
                scramble_seed = st.number_input(
                    _t("sb_seed"),
                    0,
                    99999,
                    int(st.session_state.get(f"{key_prefix}_seed", 42)),
                    key=f"{key_prefix}_seed",
                )
            if st.button(_t("sb_generate"), key=f"{key_prefix}_generate_start", width="stretch"):
                apply_start_state(
                    scramble(
                        goal=st.session_state.goal_state,
                        depth=int(scramble_depth),
                        seed=int(scramble_seed),
                    )
                )
                _finish_state_change(key_prefix, _t("sb_parse_success"), rerun_on_change)

            start_input_key = f"{key_prefix}_start_manual_input"
            sync_state_input(start_input_key, st.session_state.start_state)
            start_input = st.text_area(
                _t("sb_manual_desc"),
                key=start_input_key,
                height=88,
            )
            if st.button(_t("sb_parse"), key=f"{key_prefix}_apply_start", width="stretch"):
                try:
                    apply_start_state(parse_state(start_input))
                    _finish_state_change(key_prefix, _t("sb_parse_success"), rerun_on_change)
                except ValueError as exc:
                    st.error(_t("sb_parse_error", error=exc))
            if st.button(_t("sb_reset_goal"), key=f"{key_prefix}_start_from_goal", width="stretch"):
                apply_start_state(st.session_state.goal_state)
                _finish_state_change(key_prefix, _t("sb_parse_success"), rerun_on_change)

        with goal_col:
            st.markdown(f"**{_t('active_goal')}**")
            goal_input_key = f"{key_prefix}_goal_manual_input"
            sync_state_input(goal_input_key, st.session_state.goal_state)
            goal_input = st.text_area(
                _t("sb_goal_manual_desc"),
                key=goal_input_key,
                height=88,
            )
            goal_button_col, standard_button_col = st.columns(2)
            with goal_button_col:
                if st.button(_t("sb_parse_goal"), key=f"{key_prefix}_apply_goal", width="stretch"):
                    try:
                        apply_goal_state(parse_state(goal_input))
                        _finish_state_change(key_prefix, _t("sb_goal_parse_success"), rerun_on_change)
                    except ValueError as exc:
                        st.error(_t("sb_parse_error", error=exc))
            with standard_button_col:
                if st.button(_t("sb_standard_goal"), key=f"{key_prefix}_standard_goal", width="stretch"):
                    apply_goal_state(GOAL_STATE)
                    _finish_state_change(key_prefix, _t("sb_goal_parse_success"), rerun_on_change)


def render_sidebar_start_goal_controls(t) -> None:
    """Render the sidebar state controls with the same update semantics as page editors."""
    with st.sidebar.expander(t("sidebar_start_setup"), expanded=True):
        state_input_method = st.radio(t("sb_input_method"), [t("sb_random"), t("sb_manual")], key="input_method")

        if state_input_method == t("sb_random"):
            col_s1, col_s2 = st.columns(2)
            with col_s1:
                scramble_depth = st.number_input(t("sb_depth"), 1, 50, 10, key="scramble_depth")
            with col_s2:
                scramble_seed = st.number_input(t("sb_seed"), 0, 99999, 42, key="scramble_seed")

            if st.button(t("sb_generate"), key="btn_random"):
                apply_start_state(
                    scramble(
                        goal=st.session_state.goal_state,
                        depth=int(scramble_depth),
                        seed=int(scramble_seed),
                    )
                )
                st.success(t("sb_parse_success"))

        elif state_input_method == t("sb_manual"):
            sync_state_input("manual_input", st.session_state.start_state)
            manual_input = st.text_area(
                t("sb_manual_desc"),
                key="manual_input",
                height=80,
            )
            if st.button(t("sb_parse"), key="btn_parse"):
                try:
                    apply_start_state(parse_state(manual_input))
                    st.success(t("sb_parse_success"))
                except ValueError as exc:
                    st.error(t("sb_parse_error", error=exc))

    with st.sidebar.expander(t("sidebar_goal_setup"), expanded=False):
        sync_state_input("goal_manual_input", st.session_state.goal_state)
        goal_input = st.text_area(
            t("sb_goal_manual_desc"),
            key="goal_manual_input",
            height=80,
        )
        goal_col1, goal_col2 = st.columns(2)
        with goal_col1:
            if st.button(t("sb_parse_goal"), key="btn_parse_goal"):
                try:
                    apply_goal_state(parse_state(goal_input))
                    st.success(t("sb_goal_parse_success"))
                    st.rerun()
                except ValueError as exc:
                    st.error(t("sb_parse_error", error=exc))
        with goal_col2:
            if st.button(t("sb_standard_goal"), key="btn_standard_goal"):
                apply_goal_state(GOAL_STATE)
                st.rerun()
        if st.button(t("sb_reset_goal"), key="btn_reset"):
            apply_start_state(st.session_state.goal_state)

    with st.sidebar.expander(t("sidebar_teaching_presets"), expanded=False):
        teaching_preset_name = st.selectbox(
            t("teaching_preset"),
            list(TEACHING_PRESETS.keys()),
            key="teaching_preset_select",
            help=t("teaching_preset_help"),
        )
        if st.button(t("load_teaching_preset"), key="btn_load_teaching_preset"):
            preset = TEACHING_PRESETS[teaching_preset_name]
            apply_start_state(preset["state"])
            st.info(str(preset["purpose"]))
