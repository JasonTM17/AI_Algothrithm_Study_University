"""Run-tab controls and explanation panels for AND-OR Search."""

from __future__ import annotations

from collections.abc import Callable

import streamlit as st

from core.metrics import SearchResult
from ui.styles import SOLVER_GROUPS


AND_OR_ALGORITHM = "AND-OR Search"
NO_OBSERVATION_ALGORITHM = "Searching with no observation"
PARTIALLY_OBSERVABLE_ALGORITHM = "Searching for partially observable problems"
COMPLEX_ENVIRONMENT_ALGORITHMS = [
    AND_OR_ALGORITHM,
    NO_OBSERVATION_ALGORITHM,
    PARTIALLY_OBSERVABLE_ALGORITHM,
]


def run_algorithm_groups(t: Callable[[str], str]) -> dict[str, list[str]]:
    """Return Run-tab groups, keeping Compare's standard solver groups separate."""
    groups = {name: list(algorithms) for name, algorithms in SOLVER_GROUPS.items()}
    groups[t("run_group_complex_alias")] = list(COMPLEX_ENVIRONMENT_ALGORITHMS)
    return groups


def render_and_or_controls(t: Callable[[str], str]) -> float:
    """Render AND-OR-specific parameters and return deflection support."""
    st.warning(t("run_andor_extension_warning"))
    support = st.slider(
        t("adv_deflection_support"),
        0.0,
        1.0,
        0.3,
        key="run_andor_prob",
    )
    st.caption(t("adv_andor_support_caption"))
    st.caption(t("run_andor_controls_caption"))
    return float(support)


def render_and_or_result_explanation(result: SearchResult, t: Callable[[str], str]) -> None:
    """Render the academic meaning of an AND-OR result without calling it a path."""
    if result.algorithm != AND_OR_ALGORITHM:
        return

    st.warning(t("run_andor_extension_warning"))
    st.subheader(t("run_andor_explanation_title"))
    st.markdown(
        "\n".join(
            [
                f"- **OR node:** {t('run_andor_or_node')}",
                f"- **AND node:** {t('run_andor_and_node')}",
                f"- **{t('run_andor_output_type')}:** {t('run_andor_output')}",
            ]
        )
    )

    metric_cols = st.columns(3)
    with metric_cols[0]:
        st.metric(t("mc_expanded"), str(result.nodes_expanded))
    with metric_cols[1]:
        st.metric(t("mc_generated"), str(result.nodes_generated))
    with metric_cols[2]:
        st.metric(t("run_andor_output_type"), t("run_andor_conditional_plan"))

    if result.message:
        with st.expander(t("run_andor_plan_output"), expanded=True):
            st.code(result.message, language="text")
