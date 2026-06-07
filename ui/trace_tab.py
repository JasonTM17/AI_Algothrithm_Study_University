"""Trace inspection tab."""

import pandas as pd
import streamlit as st

from ui.components import render_search_detail_table, render_search_tree, render_trace_table


def render_step_trace_tab() -> None:
    st.title("Step-by-Step Trace")

    if "last_result" not in st.session_state or not st.session_state.last_result:
        st.info("Run an algorithm first to see the trace.")
    else:
        result = st.session_state.last_result
        st.subheader(f"Trace: {result.algorithm}")

        if result.trace:
            render_trace_table(result.trace, max_rows=200)

            st.markdown("---")
            st.subheader("Node / Frontier / Reached Detail")
            render_search_detail_table(result.trace, max_rows=50)

            st.markdown("---")
            st.subheader("Search Tree")
            render_search_tree(result.trace, max_nodes=30)

            if st.button("Export Trace as CSV"):
                import io
                rows = []
                for step in result.trace:
                    row = {"Step": step.step, "Action": step.action or ""}
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

                df = pd.DataFrame(rows)
                csv = df.to_csv(index=False).encode("utf-8")
# ── Tab 3.5: Hand-Tracing Practice ──────────────────────────────
