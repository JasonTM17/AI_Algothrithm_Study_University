"""Theory and PEAS tab."""

import streamlit as st

from core.theory import THEORY
from ui.academic_panels import (
    render_academic_header,
    render_algorithm_role_card,
    render_exam_defense_panel,
    render_exam_answer_templates,
    render_extension_warning,
    render_exam_path,
    render_grading_summary_panel,
    render_grading_report_export,
    render_peas_panel,
    render_proof_cards,
    render_recommendation_rubric,
)
from ui.components import render_algorithm_info
from ui.styles import ALGORITHM_GROUPS, THEORY_KEY_MAP


def render_theory_tab() -> None:
    st.title("Theory Notes & PEAS Analysis")
    render_academic_header(
        "Theory notes, PEAS, and exam framing",
        "Use this page to explain the agent model, algorithm guarantees, data structures, complexity, and why some methods are only academic extensions.",
        "Academic reference",
    )
    render_exam_path("Theory/PEAS")
    render_grading_summary_panel()
    render_exam_defense_panel()
    render_grading_report_export(
        st.session_state.start_state,
        st.session_state.get("benchmark_results", []),
    )
    render_peas_panel()
    render_extension_warning()
    render_recommendation_rubric()
    render_proof_cards()
    render_exam_answer_templates()

    st.markdown("---")
    st.subheader("Chi tiết lý thuyết thuật toán")

    group = st.selectbox("Algorithm Group", list(ALGORITHM_GROUPS.keys()), key="theory_group")
    algorithms = ALGORITHM_GROUPS[group]
    algo_name = st.selectbox("Algorithm", algorithms, key="theory_algo")

    theory_key = THEORY_KEY_MAP.get(algo_name, algo_name)
    theory_data = THEORY.get(theory_key)

    if theory_data:
        render_algorithm_role_card(algo_name)
        render_algorithm_info(algo_name, theory_data)
    else:
        st.info(f"Detailed theory for {algo_name} coming soon.")
        st.markdown(f"**{algo_name}** belongs to group: **{group}**")

