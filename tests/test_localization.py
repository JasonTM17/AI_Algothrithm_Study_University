"""Regression tests for localized Streamlit UI text."""

from __future__ import annotations

import ast
from pathlib import Path

from ui.localization import LOC, VIETNAMESE, resolve_language, translate


MOJIBAKE_MARKERS = (
    "\u00c3",
    "\u00c2",
    "\u00c4",
    "\u00c6",
    "\u00e1\u00ba",
    "\u00e1\u00bb",
    "\u0090",
)

STREAMLIT_TEXT_METHODS = {
    "title",
    "subheader",
    "header",
    "caption",
    "markdown",
    "info",
    "warning",
    "error",
    "success",
    "button",
    "selectbox",
    "number_input",
    "slider",
    "radio",
    "checkbox",
    "text_area",
    "metric",
    "expander",
    "download_button",
}

ALLOWED_LITERAL_TEXT = {
    ("app.py", "title", "15-Puzzle AI"),
}


def test_localization_keys_match_between_languages():
    assert set(LOC["English"]) == set(LOC[VIETNAMESE])
    assert translate(VIETNAMESE, "nav_run") == "Chạy thuật toán"
    assert translate(VIETNAMESE, "sidebar_start_setup") == "Thiết lập Start"
    assert translate(VIETNAMESE, "academic_grading_summary_title") == "Tóm tắt tiêu chí chấm"
    assert translate(VIETNAMESE, "search_tree_caption").startswith("Mỗi cạnh đều được kiểm chứng")
    assert resolve_language("\u0054\u0069\u00e1\u00ba\u00bf\u006e\u0067\u0020\u0056\u0069\u00e1\u00bb\u2021\u0074") == VIETNAMESE


def test_ui_source_has_no_legacy_mojibake_markers():
    for path in [Path("app.py"), *Path("ui").glob("*.py")]:
        source = path.read_text(encoding="utf-8-sig")
        assert not any(marker in source for marker in MOJIBAKE_MARKERS), path


def test_streamlit_user_facing_literals_are_localized():
    hits: list[tuple[str, str, str]] = []
    for path in [Path("app.py"), *Path("ui").glob("*.py")]:
        source = path.read_text(encoding="utf-8-sig")
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            if not isinstance(node.func, ast.Attribute):
                continue
            method = node.func.attr
            if method not in STREAMLIT_TEXT_METHODS:
                continue
            for arg in node.args[:2]:
                if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                    text = arg.value.strip()
                    if text and text != "---" and not text.startswith("<") and len(text) > 2:
                        hit = (path.as_posix(), method, text.replace("\n", " "))
                        if hit not in ALLOWED_LITERAL_TEXT:
                            hits.append(hit)
            for keyword in node.keywords:
                if keyword.arg not in {"label", "help"}:
                    continue
                if isinstance(keyword.value, ast.Constant) and isinstance(keyword.value.value, str):
                    hit = (path.as_posix(), f"{method}.{keyword.arg}", keyword.value.value)
                    if hit not in ALLOWED_LITERAL_TEXT:
                        hits.append(hit)

    assert hits == []
