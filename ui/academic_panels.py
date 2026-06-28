"""Reusable academic presentation panels for Streamlit pages."""

from __future__ import annotations

from html import escape

import pandas as pd
import streamlit as st

from core.academic import (
    ALGORITHM_TAXONOMY,
    PEAS_TABLE,
    RECOMMENDATION_RUBRIC,
    ROLE_LABELS,
    taxonomy_rows,
)
from core.academic_report import build_grading_report
from core.academic_proofs import (
    BENCHMARK_PRESETS,
    DECISION_GUIDE,
    EXAM_ANSWER_TEMPLATES,
    PROOF_CARDS,
)
from ui.localization import translate


def _role_class(role: str) -> str:
    return "role-" + role.replace("_", "-")


def _t(key: str, **kwargs) -> str:
    return translate(st.session_state.get("global_lang_select"), key, **kwargs)


def render_responsive_record_cards(
    records: list[dict[str, object]],
    *,
    title_key: str,
    detail_keys: list[str],
    limit: int | None = None,
) -> None:
    """Render dataframe-style records as mobile-readable cards."""
    visible = records[:limit] if limit else records
    cards = []
    for record in visible:
        title = escape(str(record.get(title_key, "")))
        rows = []
        for key in detail_keys:
            value = record.get(key)
            if value in (None, ""):
                continue
            rows.append(
                '<div class="academic-record-row">'
                f'<span class="academic-record-label">{escape(key)}</span>'
                f"<span>{escape(str(value))}</span>"
                "</div>"
            )
        cards.append(
            '<div class="academic-record-card">'
            f"<h4>{title}</h4>"
            f"{''.join(rows)}"
            "</div>"
        )
    st.markdown(f"<div class=\"academic-card-grid\">{''.join(cards)}</div>", unsafe_allow_html=True)


def render_academic_header(title: str, subtitle: str, kicker: str = "AI final exam dashboard") -> None:
    st.markdown(
        f"""
        <div class="academic-hero">
            <div class="academic-kicker">{escape(kicker)}</div>
            <h2>{escape(title)}</h2>
            <p>{escape(subtitle)}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


EXAM_PATH_STEPS = [
    ("Play", "Set state", "Load a preset or inspect solvability."),
    ("Run", "Trace one solver", "Explain frontier, reached, and guarantees."),
    ("Compare", "Measure tradeoffs", "Use seed, depth, heuristic, and caveat."),
    ("Theory/PEAS", "Defend model", "Show PEAS, proofs, taxonomy, and limits."),
    ("Hand-Tracing", "Verify by hand", "Practice expansion order and tie-breaking."),
]

EXAM_PATH_TRANSLATION_KEYS = {
    "Play": ("exam_step_play_title", "exam_step_play_note"),
    "Run": ("exam_step_run_title", "exam_step_run_note"),
    "Compare": ("exam_step_compare_title", "exam_step_compare_note"),
    "Theory/PEAS": ("exam_step_theory_title", "exam_step_theory_note"),
    "Hand-Tracing": ("exam_step_hand_title", "exam_step_hand_note"),
}

EXAM_PATH_STEP_LABEL_KEYS = {
    "Play": "exam_tab_play",
    "Run": "exam_tab_run",
    "Compare": "exam_tab_compare",
    "Theory/PEAS": "exam_tab_theory",
    "Hand-Tracing": "exam_tab_hand",
}


def _translate(t, key: str, fallback: str) -> str:
    return t(key) if t else fallback


def render_exam_path(active_step: str, t=None) -> None:
    """Render the recommended oral-defense flow for graders."""
    cards = []
    for index, (step, title_fallback, note_fallback) in enumerate(EXAM_PATH_STEPS, start=1):
        active_class = " active" if step == active_step else ""
        title_key, note_key = EXAM_PATH_TRANSLATION_KEYS[step]
        title = _translate(t, title_key, title_fallback)
        note = _translate(t, note_key, note_fallback)
        step_label = _translate(t, "exam_step_label", "Step")
        step_display = _translate(t, EXAM_PATH_STEP_LABEL_KEYS.get(step, ""), step)
        cards.append(
            f'<div class="exam-path-step{active_class}">'
            f'<div class="exam-path-index">{escape(step_label)} {index}</div>'
            f'<div class="exam-path-title">{escape(title)}</div>'
            f'<div class="exam-path-note">{escape(step_display)}: {escape(note)}</div>'
            "</div>"
        )
    st.markdown(f"<div class=\"exam-path\">{''.join(cards)}</div>", unsafe_allow_html=True)


def render_grading_summary_panel() -> None:
    """Render a compact overview of the academic grading contract."""
    role_counts = {label: 0 for label in ROLE_LABELS.values()}
    for item in ALGORITHM_TAXONOMY.values():
        role_counts[ROLE_LABELS[item.role]] += 1

    records = [
        {
            _t("academic_criterion"): _t("academic_solver_truth"),
            _t("academic_evidence"): _t("academic_solver_truth_evidence"),
            _t("academic_how_to_grade"): _t("academic_solver_truth_grade"),
        },
        {
            _t("academic_criterion"): _t("academic_peas_model"),
            _t("academic_evidence"): _t("academic_peas_evidence"),
            _t("academic_how_to_grade"): _t("academic_peas_grade"),
        },
        {
            _t("academic_criterion"): _t("academic_proof_readiness"),
            _t("academic_evidence"): _t(
                "academic_proof_evidence",
                proof_count=len(PROOF_CARDS),
                template_count=len(EXAM_ANSWER_TEMPLATES),
            ),
            _t("academic_how_to_grade"): _t("academic_proof_grade"),
        },
        {
            _t("academic_criterion"): _t("academic_coverage"),
            _t("academic_evidence"): ", ".join(f"{count} {role}" for role, count in role_counts.items()),
            _t("academic_how_to_grade"): _t("academic_coverage_grade"),
        },
    ]
    st.subheader(_t("academic_grading_summary_title"))
    render_responsive_record_cards(
        records,
        title_key=_t("academic_criterion"),
        detail_keys=[_t("academic_evidence"), _t("academic_how_to_grade")],
    )


def render_algorithm_role_card(algorithm_name: str) -> None:
    item = ALGORITHM_TAXONOMY.get(algorithm_name)
    if item is None:
        return

    role_label = ROLE_LABELS[item.role]
    st.markdown(
        f"""
        <div class="academic-card">
                <div class="academic-card-title">{escape(_t("academic_classification"))}</div>
                <div class="academic-card-body">
                    <span class="role-badge {_role_class(item.role)}">{escape(role_label)}</span>
                    <p><strong>{escape(_t("academic_environment"))}:</strong> {escape(item.environment)}</p>
                    <p><strong>{escape(_t("academic_guarantee"))}:</strong> {escape(item.guarantee)}</p>
                    <p><strong>{escape(_t("academic_exam_note"))}:</strong> {escape(item.exam_note)}</p>
                </div>
            </div>
        """,
        unsafe_allow_html=True,
    )


def render_peas_panel() -> None:
    st.subheader(_t("academic_peas_title"))
    render_responsive_record_cards(
        PEAS_TABLE,
        title_key="PEAS",
        detail_keys=["Academic meaning", "15-puzzle instance", "Exam emphasis"],
    )
    with st.expander(_t("academic_peas_table"), expanded=False):
        st.dataframe(pd.DataFrame(PEAS_TABLE), width="stretch", hide_index=True)


def render_recommendation_rubric() -> None:
    st.subheader(_t("academic_rubric_title"))
    render_responsive_record_cards(
        RECOMMENDATION_RUBRIC,
        title_key="Need",
        detail_keys=["Use", "Avoid", "Reason"],
    )
    with st.expander(_t("academic_rubric_table"), expanded=False):
        st.dataframe(pd.DataFrame(RECOMMENDATION_RUBRIC), width="stretch", hide_index=True)


def render_taxonomy_table() -> None:
    st.subheader(_t("academic_taxonomy_title"))
    rows = taxonomy_rows()
    render_responsive_record_cards(
        rows,
        title_key="Algorithm",
        detail_keys=["Role", "Environment", "Guarantee", "Exam note"],
        limit=9,
    )
    st.caption(_t("academic_taxonomy_caption"))
    with st.expander(_t("academic_taxonomy_table"), expanded=False):
        st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)


def render_extension_warning(t=None) -> None:
    warning = _translate(
        t,
        "academic_extension_warning",
        (
            "Academic boundary: CSP, complex-environment, Minimax, Alpha-Beta, "
            "and Expectimax modes are educational extensions. They explain alternate "
            "AI problem formulations, but they are not natural solvers for the standard "
            "deterministic, fully observable 15-puzzle."
        ),
    )
    st.markdown(
        f"""
        <div class="academic-warning">
            {escape(warning)}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_proof_cards() -> None:
    st.subheader(_t("academic_proof_cards_title"))
    records = [
        {
            "Proof": title,
            _t("academic_claim"): item["claim"],
            _t("academic_reason"): item["reason"],
            _t("academic_exam_use"): item["exam_use"],
        }
        for title, item in PROOF_CARDS.items()
    ]
    render_responsive_record_cards(records, title_key="Proof", detail_keys=[_t("academic_claim"), _t("academic_exam_use")])
    with st.expander(_t("academic_proof_details"), expanded=False):
        for title, item in PROOF_CARDS.items():
            st.markdown(f"**{title}**")
            st.markdown(f"**{_t('academic_claim')}:** {item['claim']}")
            st.markdown(f"**{_t('academic_reason')}:** {item['reason']}")
            st.markdown(f"**{_t('academic_exam_use')}:** {item['exam_use']}")


def render_exam_answer_templates() -> None:
    st.subheader(_t("academic_answer_templates_title"))
    rows = [
        {"Group": group, **template}
        for group, template in EXAM_ANSWER_TEMPLATES.items()
    ]
    render_responsive_record_cards(
        rows,
        title_key="Group",
        detail_keys=["goal", "frontier", "evaluation", "guarantee", "when_to_use", "when_not_to_use"],
    )
    with st.expander(_t("academic_answer_template_table"), expanded=False):
        st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)


def render_benchmark_methodology(preset_name: str | None = None) -> None:
    st.subheader(_t("academic_benchmark_methodology"))
    if preset_name and preset_name in BENCHMARK_PRESETS:
        preset = BENCHMARK_PRESETS[preset_name]
        recommended = ", ".join(preset.get("recommended_algorithms", ())) or "-"
        st.markdown(
            f"""
            <div class="academic-card">
                <div class="academic-card-title">{escape(preset_name)}</div>
                <div class="academic-card-body">
                    depth={preset['depth']} | seed={preset['seed']} | max_nodes={preset['max_nodes']} | timeout={preset['timeout']}s | heuristic={escape(str(preset['heuristic']))}<br>
                    recommended={escape(recommended)}<br>
                    purpose={escape(str(preset.get('comparison_goal', '-')))}<br>
                    expected={escape(str(preset.get('expected_outcome', '-')))}<br>
                    <em>{escape(str(preset['caveat']))}</em>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.caption(_t("academic_benchmark_caption"))


def render_decision_guide() -> None:
    st.subheader(_t("academic_decision_guide"))
    render_responsive_record_cards(
        DECISION_GUIDE,
        title_key="Question",
        detail_keys=["Use", "Why"],
    )
    with st.expander(_t("academic_decision_guide_table"), expanded=False):
        st.dataframe(pd.DataFrame(DECISION_GUIDE), width="stretch", hide_index=True)


def render_benchmark_evidence(results: list) -> None:
    if not results:
        return

    baseline = next(
        (r for r in results if r.algorithm in {"A*", "A* Search"} and r.success and r.cost is not None),
        None,
    )
    rows = []
    for result in results:
        if not getattr(result, "success", False):
            continue
        cost = getattr(result, "cost", None)
        expanded = getattr(result, "nodes_expanded", 0)
        runtime = getattr(result, "runtime", 0.0)
        row = {
            "Algorithm": result.algorithm,
            "Cost": cost,
            "Expanded": expanded,
            "Runtime (s)": round(runtime, 4),
        }
        if baseline and cost is not None and baseline.cost is not None and baseline.nodes_expanded is not None and baseline.runtime is not None:
            row["Optimality gap"] = cost - baseline.cost
            row["Expanded ratio vs A*"] = round(expanded / max(baseline.nodes_expanded, 1), 3)
            row["Runtime ratio vs A*"] = round(runtime / max(baseline.runtime, 1e-9), 3)
        rows.append(row)

    if rows:
        st.subheader(_t("academic_evidence_metrics"))
        render_responsive_record_cards(
            rows,
            title_key="Algorithm",
            detail_keys=[
                "Cost",
                "Expanded",
                "Runtime (s)",
                "Optimality gap",
                "Expanded ratio vs A*",
                "Runtime ratio vs A*",
            ],
        )
        with st.expander(_t("academic_evidence_metrics_table"), expanded=False):
            st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)


def render_exam_defense_panel() -> None:
    st.subheader(_t("academic_exam_defense_guide"))
    records = [
        {
            _t("academic_section"): "Demo flow",
            _t("academic_what_to_show"): "Start in Play, run A*, then use Run Algorithm to compare its certificate with Greedy or Hill Climbing.",
            _t("academic_why_it_matters"): "Shows the difference between optimal solvers and contrast demos.",
        },
        {
            _t("academic_section"): "Proof map",
            _t("academic_what_to_show"): "Use PEAS, proof cards, and the selected algorithm role before opening detailed theory.",
            _t("academic_why_it_matters"): "Lets instructors verify guarantees quickly.",
        },
        {
            _t("academic_section"): "Boundary statement",
            _t("academic_what_to_show"): "Point out CSP, complex, and game modes as extensions.",
            _t("academic_why_it_matters"): "Prevents the common mistake of calling every AI topic a natural 15-puzzle solver.",
        },
        {
            _t("academic_section"): "Evidence",
            _t("academic_what_to_show"): "Use benchmark methodology, seed, depth, heuristic, and caveat.",
            _t("academic_why_it_matters"): "Frames results as course evidence rather than production benchmarking.",
        },
    ]
    render_responsive_record_cards(
        records,
        title_key=_t("academic_section"),
        detail_keys=[_t("academic_what_to_show"), _t("academic_why_it_matters")],
    )


def render_grading_report_export(start_state: tuple[int, ...], benchmark_results: list | None = None) -> None:
    report = build_grading_report(start_state, benchmark_results)
    st.download_button(
        _t("academic_download_report"),
        data=report,
        file_name="15-puzzle-ai-grading-report.md",
        mime="text/markdown",
        key="download_grading_report",
    )
    with st.expander(_t("academic_preview_report"), expanded=False):
        st.code(report, language="markdown")
