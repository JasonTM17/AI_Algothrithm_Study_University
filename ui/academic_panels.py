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


def _role_class(role: str) -> str:
    return "role-" + role.replace("_", "-")


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


def render_exam_path(active_step: str) -> None:
    """Render the recommended oral-defense flow for graders."""
    cards = []
    for index, (step, title, note) in enumerate(EXAM_PATH_STEPS, start=1):
        active_class = " active" if step == active_step else ""
        cards.append(
            f'<div class="exam-path-step{active_class}">'
            f'<div class="exam-path-index">Step {index}</div>'
            f'<div class="exam-path-title">{escape(title)}</div>'
            f'<div class="exam-path-note">{escape(step)}: {escape(note)}</div>'
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
            "Criterion": "Solver truth",
            "Evidence": "A*, IDA*, BFS, UCS, and IDS are separated from contrast demos.",
            "How to grade": "Check the role badge before reading runtime metrics.",
        },
        {
            "Criterion": "PEAS model",
            "Evidence": "Performance, Environment, Actuators, and Sensors are rendered as first-class data.",
            "How to grade": "Verify the environment is deterministic, fully observable, and single-agent.",
        },
        {
            "Criterion": "Proof readiness",
            "Evidence": f"{len(PROOF_CARDS)} proof cards plus answer templates for {len(EXAM_ANSWER_TEMPLATES)} groups.",
            "How to grade": "Ask for optimality, admissibility, consistency, and parity arguments.",
        },
        {
            "Criterion": "Coverage",
            "Evidence": ", ".join(f"{count} {role}" for role, count in role_counts.items()),
            "How to grade": "Confirm extension algorithms are not presented as natural solvers.",
        },
    ]
    st.subheader("Grading summary")
    render_responsive_record_cards(records, title_key="Criterion", detail_keys=["Evidence", "How to grade"])


def render_algorithm_role_card(algorithm_name: str) -> None:
    item = ALGORITHM_TAXONOMY.get(algorithm_name)
    if item is None:
        return

    role_label = ROLE_LABELS[item.role]
    st.markdown(
        f"""
        <div class="academic-card">
            <div class="academic-card-title">Academic classification</div>
            <div class="academic-card-body">
                <span class="role-badge {_role_class(item.role)}">{escape(role_label)}</span>
                <p><strong>Environment:</strong> {escape(item.environment)}</p>
                <p><strong>Guarantee:</strong> {escape(item.guarantee)}</p>
                <p><strong>Exam note:</strong> {escape(item.exam_note)}</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_peas_panel() -> None:
    st.subheader("PEAS model for the 15-puzzle agent")
    render_responsive_record_cards(
        PEAS_TABLE,
        title_key="PEAS",
        detail_keys=["Academic meaning", "15-puzzle instance", "Exam emphasis"],
    )
    with st.expander("Detailed PEAS table", expanded=False):
        st.dataframe(pd.DataFrame(PEAS_TABLE), width="stretch", hide_index=True)


def render_recommendation_rubric() -> None:
    st.subheader("Algorithm selection rubric")
    render_responsive_record_cards(
        RECOMMENDATION_RUBRIC,
        title_key="Need",
        detail_keys=["Use", "Avoid", "Reason"],
    )
    with st.expander("Detailed rubric table", expanded=False):
        st.dataframe(pd.DataFrame(RECOMMENDATION_RUBRIC), width="stretch", hide_index=True)


def render_taxonomy_table() -> None:
    st.subheader("Academic taxonomy of all algorithms")
    rows = taxonomy_rows()
    render_responsive_record_cards(
        rows,
        title_key="Algorithm",
        detail_keys=["Role", "Environment", "Guarantee", "Exam note"],
        limit=9,
    )
    st.caption("Showing the first 9 algorithms as cards. Open the full table for all 27 algorithms.")
    with st.expander("Full taxonomy table", expanded=False):
        st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)


def render_extension_warning() -> None:
    st.markdown(
        """
        <div class="academic-warning">
            <strong>Academic boundary:</strong> CSP, complex-environment, Minimax,
            Alpha-Beta, and Expectimax modes are educational extensions. They explain
            alternate AI problem formulations, but they are not natural solvers for the
            standard deterministic, fully observable 15-puzzle.
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_proof_cards() -> None:
    st.subheader("Proof cards for oral/written defense")
    records = [
        {"Proof": title, "Claim": item["claim"], "Reason": item["reason"], "Exam use": item["exam_use"]}
        for title, item in PROOF_CARDS.items()
    ]
    render_responsive_record_cards(records, title_key="Proof", detail_keys=["Claim", "Exam use"])
    with st.expander("Proof reasoning details", expanded=False):
        for title, item in PROOF_CARDS.items():
            st.markdown(f"**{title}**")
            st.markdown(f"**Claim:** {item['claim']}")
            st.markdown(f"**Reason:** {item['reason']}")
            st.markdown(f"**Exam use:** {item['exam_use']}")


def render_exam_answer_templates() -> None:
    st.subheader("Exam answer templates by algorithm group")
    rows = [
        {"Group": group, **template}
        for group, template in EXAM_ANSWER_TEMPLATES.items()
    ]
    render_responsive_record_cards(
        rows,
        title_key="Group",
        detail_keys=["goal", "frontier", "evaluation", "guarantee", "when_to_use", "when_not_to_use"],
    )
    with st.expander("Detailed answer template table", expanded=False):
        st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)


def render_benchmark_methodology(preset_name: str | None = None) -> None:
    st.subheader("Benchmark methodology")
    if preset_name and preset_name in BENCHMARK_PRESETS:
        preset = BENCHMARK_PRESETS[preset_name]
        st.markdown(
            f"""
            <div class="academic-card">
                <div class="academic-card-title">{escape(preset_name)}</div>
                <div class="academic-card-body">
                    depth={preset['depth']} | seed={preset['seed']} | max_nodes={preset['max_nodes']} | timeout={preset['timeout']}s | heuristic={escape(preset['heuristic'])}<br>
                    <em>{escape(preset['caveat'])}</em>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    st.caption("Benchmark output is course evidence, not a production solver leaderboard.")


def render_decision_guide() -> None:
    st.subheader("Algorithm decision guide")
    render_responsive_record_cards(
        DECISION_GUIDE,
        title_key="Question",
        detail_keys=["Use", "Why"],
    )
    with st.expander("Detailed decision guide table", expanded=False):
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
        if baseline and cost is not None and baseline.cost is not None:
            row["Optimality gap"] = cost - baseline.cost
            row["Expanded ratio vs A*"] = round(expanded / max(baseline.nodes_expanded, 1), 3)
            row["Runtime ratio vs A*"] = round(runtime / max(baseline.runtime, 1e-9), 3)
        rows.append(row)

    if rows:
        st.subheader("Academic evidence metrics")
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
        with st.expander("Detailed evidence metrics table", expanded=False):
            st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)


def render_exam_defense_panel() -> None:
    st.subheader("Exam defense guide")
    records = [
        {
            "Section": "Demo flow",
            "What to show": "Start in Play, load a teaching preset, run A*, then compare against Greedy or Hill Climbing.",
            "Why it matters": "Shows the difference between optimal solvers and contrast demos.",
        },
        {
            "Section": "Proof map",
            "What to show": "Use PEAS, proof cards, and the selected algorithm role before opening detailed theory.",
            "Why it matters": "Lets instructors verify guarantees quickly.",
        },
        {
            "Section": "Boundary statement",
            "What to show": "Point out CSP, complex, and game modes as extensions.",
            "Why it matters": "Prevents the common mistake of calling every AI topic a natural 15-puzzle solver.",
        },
        {
            "Section": "Evidence",
            "What to show": "Use benchmark methodology, seed, depth, heuristic, and caveat.",
            "Why it matters": "Frames results as course evidence rather than production benchmarking.",
        },
    ]
    render_responsive_record_cards(records, title_key="Section", detail_keys=["What to show", "Why it matters"])


def render_grading_report_export(start_state: tuple[int, ...], benchmark_results: list | None = None) -> None:
    report = build_grading_report(start_state, benchmark_results)
    st.download_button(
        "Download grading report (Markdown)",
        data=report,
        file_name="15-puzzle-ai-grading-report.md",
        mime="text/markdown",
        key="download_grading_report",
    )
    with st.expander("Preview grading report", expanded=False):
        st.markdown(report)
