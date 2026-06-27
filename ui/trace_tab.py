"""Trace inspection tab."""

import pandas as pd
import streamlit as st

from core.puzzle import GOAL_STATE, is_solvable
from ui.action_states import render_action_state
from ui.localization import VIETNAMESE, translate
from ui.components import (
    _format_trace_state,
    _format_trace_state_list,
    _trace_state_catalog,
    render_search_detail_table,
    render_search_tree,
    render_start_goal_contract,
    render_trace_table,
)


def t(key, **kwargs):
    global_lang = st.session_state.get("global_lang_select", VIETNAMESE)
    return translate(global_lang, key, **kwargs)


def trace_rows(trace) -> list[dict[str, object]]:
    """Convert trace events to CSV-friendly rows."""
    labels, details = _trace_state_catalog(trace)
    rows = []
    for step in trace:
        row = {
            "Step": step.step,
            "Event": step.event,
            "Node": _format_trace_state(step.state, labels, details, include_parent=True),
            "Parent": _format_trace_state(getattr(step, "node_state", None), labels, details),
            "Action": step.action or "",
        }
        if step.g is not None and step.g > 0:
            row["g(n)"] = step.g
        if step.h is not None and step.h > 0:
            row["h(n)"] = f"{step.h:.1f}"
        if step.f is not None and step.f > 0:
            row["f(n)"] = f"{step.f:.1f}"
        if step.frontier_states:
            row["Frontier"] = _format_trace_state_list(step.frontier_states, labels, details)
        elif step.frontier_size > 0:
            row["Frontier"] = step.frontier_size
        if step.reached_states:
            row["Reached"] = _format_trace_state_list(step.reached_states, labels, details)
        elif step.reached_size > 0:
            row["Reached"] = step.reached_size
        if step.reason:
            row["Reason"] = step.reason
        rows.append(row)
    return rows


def render_step_trace_tab() -> None:
    st.title(t("trace_title"))
    goal = st.session_state.get("goal_state", GOAL_STATE)

    if "last_result" not in st.session_state or not st.session_state.last_result:
        render_start_goal_contract(
            st.session_state.start_state,
            goal,
            is_solvable(st.session_state.start_state, goal),
            show_editor=False,
        )
        render_action_state(
            title=t("trace_empty_title"),
            body=t("trace_empty_body"),
            bullets=[t("trace_empty_bullet_start"), t("trace_empty_bullet_run")],
            kicker=t("action_state_kicker"),
            action_label=t("trace_empty_cta"),
            action_key="trace_empty_go_run",
            target_tab_label=t("nav_run"),
        )
        return

    result = st.session_state.last_result
    st.subheader(t("trace_result_title", algorithm=result.algorithm))

    if not result.trace:
        render_action_state(
            title=t("trace_no_events_title"),
            body=t("trace_no_events_body"),
            bullets=[t("trace_empty_bullet_run")],
            kicker=t("action_state_kicker"),
            action_label=t("trace_empty_cta"),
            action_key="trace_no_events_go_run",
            target_tab_label=t("nav_run"),
        )
        return

    st.caption(t("trace_notation_help"))
    render_trace_table(result.trace, max_rows=200)

    st.markdown("---")
    st.subheader(t("trace_detail_title"))
    render_search_detail_table(result.trace, max_rows=50, key="trace_detail_step_slider")

    st.markdown("---")
    st.subheader(t("trace_tree_title"))
    render_search_tree(result, max_nodes=40)

    df = pd.DataFrame(trace_rows(result.trace))
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        t("trace_download_csv"),
        data=csv,
        file_name=f"{result.algorithm.lower().replace(' ', '-')}-trace.csv",
        mime="text/csv",
        key="download_trace_csv",
    )
