"""Trace inspection tab."""

import pandas as pd
import streamlit as st

from ui.components import render_search_detail_table, render_search_tree, render_trace_table


def trace_rows(trace) -> list[dict[str, object]]:
    """Convert trace events to CSV-friendly rows."""
    rows = []
    for step in trace:
        row = {"Step": step.step, "Event": step.event, "Action": step.action or ""}
        if step.g > 0:
            row["g(n)"] = step.g
        if step.h > 0:
            row["h(n)"] = f"{step.h:.1f}"
        if step.f > 0:
            row["f(n)"] = f"{step.f:.1f}"
        if step.frontier_size > 0:
            row["Frontier"] = step.frontier_size
        if step.reached_size > 0:
            row["Reached"] = step.reached_size
        if step.reason:
            row["Reason"] = step.reason
        rows.append(row)
    return rows


def render_step_trace_tab() -> None:
    st.title("Step-by-Step Trace")

    if "last_result" not in st.session_state or not st.session_state.last_result:
        st.info("Run an algorithm first to see the trace.")
        return

    result = st.session_state.last_result
    st.subheader(f"Trace: {result.algorithm}")

    if not result.trace:
        st.info("This result has no recorded trace events.")
        return

    render_trace_table(result.trace, max_rows=200)

    st.markdown("---")
    st.subheader("Node / Frontier / Reached Detail")
    render_search_detail_table(result.trace, max_rows=50)

    st.markdown("---")
    st.subheader("Search Tree")
    render_search_tree(result, max_nodes=40)

    df = pd.DataFrame(trace_rows(result.trace))
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "Download Trace CSV",
        data=csv,
        file_name=f"{result.algorithm.lower().replace(' ', '-')}-trace.csv",
        mime="text/csv",
        key="download_trace_csv",
    )
