"""Theory and PEAS tab."""

import streamlit as st

from core.algorithm_comparison import (
    comparison_rows_for_group,
    group6_robustness_comparison_rows,
)
from core.theory import THEORY
from ui.action_states import render_action_state
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
from ui.syllabus_coverage_panels import render_syllabus_coverage_panels
from ui.styles import ALGORITHM_GROUPS, THEORY_KEY_MAP


def render_theory_tab(t=None) -> None:
    tx = t or (lambda key, **kwargs: key.format(**kwargs) if kwargs else key)
    st.title(tx("theory_title"))
    render_academic_header(
        tx("theory_hero_title"),
        tx("theory_hero_desc"),
        tx("theory_hero_kicker"),
    )
    render_exam_path("Theory/PEAS", t=t)
    render_grading_summary_panel()
    render_exam_defense_panel()
    render_grading_report_export(
        st.session_state.start_state,
        st.session_state.get("benchmark_results", []),
    )
    render_peas_panel()
    render_extension_warning(t=t)
    render_recommendation_rubric()
    render_proof_cards()
    render_exam_answer_templates()
    render_syllabus_coverage_panels()

    st.markdown("---")
    st.subheader(tx("theory_detail_title"))

    group = st.selectbox(tx("run_group"), list(ALGORITHM_GROUPS.keys()), key="theory_group")
    algorithms = ALGORITHM_GROUPS[group]
    st.markdown(f"### {tx('theory_group_comparison')}")
    st.caption(tx("theory_complexity_caveat"))
    st.dataframe(
        comparison_rows_for_group(group),
        width="stretch",
        hide_index=True,
    )
    if group == "AI-vs-AI Tournament":
        st.markdown(f"### {tx('theory_group6_cross_comparison')}")
        st.caption(tx("theory_group6_cross_caption"))
        st.dataframe(
            group6_robustness_comparison_rows(),
            width="stretch",
            hide_index=True,
        )
    algo_name = st.selectbox(tx("run_algo"), algorithms, key="theory_algo")

    theory_key = THEORY_KEY_MAP.get(algo_name, algo_name)
    theory_data = THEORY.get(theory_key)

    if theory_data:
        render_algorithm_role_card(algo_name)
        render_algorithm_info(algo_name, theory_data)
    else:
        render_algorithm_role_card(algo_name)
        render_action_state(
            title=tx("theory_fallback_title", algo=algo_name),
            body=tx("theory_fallback_body"),
            bullets=[
                tx("theory_fallback_bullet_group", group=group),
                tx("theory_fallback_bullet_compare"),
            ],
            kicker=tx("action_state_kicker"),
        )

