"""Theory-page panels that map the syllabus screenshots to app evidence."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from core.syllabus_coverage import (
    HEURISTIC_GENERATION_ROWS,
    HILL_CLIMBING_ISSUE_ROWS,
    SEARCH_FOUNDATION_ROWS,
    SYLLABUS_COVERAGE_ROWS,
    TREE_GRAPH_SEARCH_ROWS,
)
from ui.academic_panels import render_responsive_record_cards
from ui.localization import translate


def _t(key: str) -> str:
    return translate(st.session_state.get("global_lang_select"), key)


def _render_panel(
    title: str,
    caption: str,
    rows: list[dict[str, str]],
    *,
    title_key: str,
    detail_keys: list[str],
    table_label: str,
    card_limit: int | None = None,
) -> None:
    st.subheader(title)
    st.caption(caption)
    render_responsive_record_cards(
        rows,
        title_key=title_key,
        detail_keys=detail_keys,
        limit=card_limit,
    )
    with st.expander(table_label, expanded=False):
        st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)


def render_syllabus_coverage_panels() -> None:
    """Render direct syllabus-to-product academic evidence on Theory/PEAS."""
    st.markdown("---")
    st.markdown(f"### {_t('syllabus_audit_title')}")
    st.caption(_t("syllabus_audit_caption"))

    _render_panel(
        "Syllabus Coverage Matrix",
        "Every topic from the provided screenshots is mapped to an app page, output, or testable evidence.",
        SYLLABUS_COVERAGE_ROWS,
        title_key="Syllabus topic",
        detail_keys=["App surface", "Evidence", "Defense note"],
        table_label="Full syllabus coverage table",
        card_limit=12,
    )

    _render_panel(
        "Search Foundations",
        "The common search loop used to explain BFS, DFS, UCS, Greedy, A*, and IDA*.",
        SEARCH_FOUNDATION_ROWS,
        title_key="Step",
        detail_keys=["What to check", "App evidence"],
        table_label="Search foundations table",
    )

    _render_panel(
        "Tree Search vs Graph Search",
        "This separates generated parent-child evidence from duplicate-state control.",
        TREE_GRAPH_SEARCH_ROWS,
        title_key="Model",
        detail_keys=["Core idea", "Risk", "App connection"],
        table_label="Tree vs graph table",
    )

    _render_panel(
        "Heuristic Generation",
        "How the displayed heuristics are derived and why A*/IDA* may use them for optimality claims.",
        HEURISTIC_GENERATION_ROWS,
        title_key="Heuristic",
        detail_keys=["Generation idea", "Formula/example", "Guarantee"],
        table_label="Heuristic generation table",
    )

    _render_panel(
        "Hill-Climbing Issues",
        "Failure modes that justify treating local search as contrast demos for 15-puzzle.",
        HILL_CLIMBING_ISSUE_ROWS,
        title_key="Issue",
        detail_keys=["What happens", "App evidence", "Mitigation/demo"],
        table_label="Hill-climbing issue table",
    )
