"""Trace inspection tab."""

import pandas as pd
import streamlit as st

from ui.localization import translate
from ui.components import (
    _format_trace_state,
    _format_trace_state_list,
    _trace_state_catalog,
    render_search_detail_table,
    render_search_tree,
    render_trace_table,
)


def t(key, **kwargs):
    global_lang = st.session_state.get("global_lang_select", "Tiếng Việt")
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

    if "last_result" not in st.session_state or not st.session_state.last_result:
        st.info(t("trace_info"))
        return

    result = st.session_state.last_result
    st.subheader(t("trace_result_title", algorithm=result.algorithm))

    if not result.trace:
        st.info(t("trace_empty_result"))
        return

    st.caption(t("trace_notation_help"))
    render_trace_table(result.trace, max_rows=200)

    st.markdown("---")
    st.subheader(t("trace_detail_title"))
    render_search_detail_table(result.trace, max_rows=50)

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
