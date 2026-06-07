"""Markdown grading report generation for the final-exam UI."""

from __future__ import annotations

from collections.abc import Iterable

from core.academic import PEAS_TABLE, ROLE_LABELS, taxonomy_rows
from core.academic_proofs import BENCHMARK_PRESETS, PROOF_CARDS


def _format_state(state: tuple[int, ...] | None) -> str:
    if not state:
        return "Not provided"
    rows = []
    for row in range(4):
        values = state[row * 4:(row + 1) * 4]
        rows.append(" ".join("__" if value == 0 else f"{value:2d}" for value in values))
    return "\n".join(rows)


def _benchmark_rows(results: Iterable[object] | None) -> list[str]:
    if not results:
        return ["No benchmark run included in this report."]

    rows = ["| Algorithm | Success | Cost | Expanded | Runtime |", "|---|---:|---:|---:|---:|"]
    for result in results:
        algorithm = getattr(result, "algorithm", "Unknown")
        success = "yes" if getattr(result, "success", False) else "no"
        cost = getattr(result, "cost", "-")
        expanded = getattr(result, "nodes_expanded", "-")
        runtime = getattr(result, "runtime", 0.0)
        rows.append(f"| {algorithm} | {success} | {cost} | {expanded} | {runtime:.4f}s |")
    return rows


def build_grading_report(
    start_state: tuple[int, ...] | None = None,
    benchmark_results: Iterable[object] | None = None,
) -> str:
    """Build a deterministic Markdown report for instructor grading."""
    role_counts = {label: 0 for label in ROLE_LABELS.values()}
    for row in taxonomy_rows():
        role_counts[row["Role"]] += 1

    lines = [
        "# 15-Puzzle AI Final Exam Grading Report",
        "",
        "## Current Start State",
        "```text",
        _format_state(start_state),
        "```",
        "",
        "## PEAS Model",
        "| PEAS | 15-puzzle instance | Exam emphasis |",
        "|---|---|---|",
    ]
    for row in PEAS_TABLE:
        lines.append(f"| {row['PEAS']} | {row['15-puzzle instance']} | {row['Exam emphasis']} |")

    lines.extend([
        "",
        "## Algorithm Taxonomy",
        "| Role | Count |",
        "|---|---:|",
    ])
    for role, count in role_counts.items():
        lines.append(f"| {role} | {count} |")

    lines.extend([
        "",
        "## Proof Cards",
        "| Claim | Exam use |",
        "|---|---|",
    ])
    for name, card in PROOF_CARDS.items():
        lines.append(f"| {name}: {card['claim']} | {card['exam_use']} |")

    lines.extend([
        "",
        "## Benchmark Methodology",
        "| Preset | Depth | Seed | Heuristic | Caveat |",
        "|---|---:|---:|---|---|",
    ])
    for name, preset in BENCHMARK_PRESETS.items():
        lines.append(
            f"| {name} | {preset['depth']} | {preset['seed']} | "
            f"{preset['heuristic']} | {preset['caveat']} |"
        )

    lines.extend([
        "",
        "## Benchmark Results",
        *_benchmark_rows(benchmark_results),
        "",
        "## Known Limitations",
        "- CSP, complex-environment, Minimax, Alpha-Beta, and Expectimax modes are educational extensions.",
        "- Benchmark output is course evidence, not a production solver leaderboard.",
        "- Solver signatures and algorithm behavior are intentionally unchanged by the UI/UX hardening pass.",
        "",
        "## Verification Commands",
        "```bash",
        "python -m py_compile app.py core/*.py algorithms/*.py ui/*.py",
        "python -m pytest tests/ -q",
        "```",
    ])
    return "\n".join(lines)
