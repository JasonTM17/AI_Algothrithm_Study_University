"""Text-quality regressions for user-facing academic content."""

from __future__ import annotations

from pathlib import Path
import re

from core.theory import THEORY


MOJIBAKE_MARKERS = (
    "\u00c3",
    "\u00c2",
    "\u00c4",
    "\u00c6",
    "\u00e1\u00ba",
    "\u00e1\u00bb",
    "\u00e2\u20ac",
    "\u00e2\u201d",
    "\u00e2\u201e",
)

TEXT_ROOTS = ("core", "ui", "tests", "docs")


def _text_files() -> list[Path]:
    paths: list[Path] = []
    for root in TEXT_ROOTS:
        paths.extend(Path(root).rglob("*.py"))
        paths.extend(Path(root).rglob("*.md"))
    return [
        path for path in paths
        if "__pycache__" not in path.parts
    ]


def test_user_facing_text_sources_have_no_mojibake_markers():
    offenders: list[tuple[str, str]] = []
    for path in _text_files():
        source = path.read_text(encoding="utf-8-sig")
        for marker in MOJIBAKE_MARKERS:
            if marker in source:
                offenders.append((path.as_posix(), marker))

    assert offenders == []


def test_ai_vs_ai_tournament_theory_text_is_clean_and_keeps_terms():
    item = THEORY["AI-vs-AI Tournament"]
    text_fields = [
        item["goal"],
        item["idea"],
        item["application"],
        item["suitable"],
        item["complexity"],
        item["bad_example"],
        item["comparison"],
        item["exam_tips"],
        *item["pros"],
        *item["cons"],
    ]
    joined = "\n".join(text_fields)

    assert "Chấm điểm hai AI" in item["goal"]
    assert "Môi trường puzzle vẫn single-agent" in item["idea"]
    for term in ("A*", "single-agent", "solver", "optimal cost", "AI-vs-AI"):
        assert term in joined
    assert "benchmark" in joined.lower()
    for marker in MOJIBAKE_MARKERS:
        assert marker not in joined


def test_docs_track_current_ui_evidence_surfaces():
    readme = Path("README.md").read_text(encoding="utf-8")
    codebase_summary = Path("docs/codebase-summary.md").read_text(encoding="utf-8")
    architecture = Path("docs/system-architecture.md").read_text(encoding="utf-8")

    assert "Atlas 28 Thuật Toán Có GIF Chạy Thật" in readme
    assert "--theme light" in readme
    assert "--theme dark" in readme
    assert "ui/belief_controls.py" in codebase_summary
    assert "docs/assets/" in codebase_summary
    assert "readable tree" in architecture
    assert "Graphviz evidence" in architecture
    assert "profile" in architecture


def test_readme_relative_markdown_links_exist():
    readme = Path("README.md").read_text(encoding="utf-8")
    missing = []
    for target in re.findall(r"\]\(([^)#][^)]+)\)", readme):
        if target.startswith(("http://", "https://")):
            continue
        path = Path(target)
        if not path.exists():
            missing.append(target)
    assert missing == []
