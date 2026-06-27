"""Live Streamlit capture surface for README GIF generation."""

from __future__ import annotations

from html import escape

import streamlit as st

from core.heuristics import HEURISTICS
from scripts.readme_gif_runner import DemoEvidence, run_demo
from scripts.readme_gif_specs import get_spec
from ui.components import render_puzzle_board
from ui.sample_images import generate_sample_tiles


CAPTURE_CSS = """
<style>
header[data-testid="stHeader"], div[data-testid="stToolbar"], #MainMenu, footer,
section[data-testid="stSidebar"], div[data-testid="stDecoration"] { display: none !important; }
div[data-testid="stAppViewContainer"], .stApp {
    background: #0e1110 !important;
}
div[data-testid="stMain"], div[data-testid="stMainBlockContainer"] {
    padding: 0 !important;
    margin: 0 !important;
    max-width: none !important;
}
.block-container { padding: 0 !important; max-width: none !important; }
.capture-page {
    width: 100vw;
    min-height: 100vh;
    padding: 16px 42px;
    background:
        radial-gradient(circle at 88% 0%, rgba(127,175,111,0.16), transparent 260px),
        linear-gradient(135deg, rgba(214,161,95,0.08), transparent 40%),
        #0e1110;
    color: #f4efe5;
    font-family: "Be Vietnam Pro", "Segoe UI", sans-serif;
    overflow: hidden;
}
.capture-hero { padding: 34px 52px; }
.capture-title {
    margin: 0;
    font-size: clamp(24px, 3.2vw, 34px);
    line-height: 1.0;
    letter-spacing: 0;
}
.capture-hero .capture-title { font-size: clamp(34px, 4.2vw, 52px); }
.capture-subtitle {
    margin: 7px 0 12px;
    color: #d2c7b8;
    font-size: clamp(14px, 1.7vw, 18px);
}
.capture-hero .capture-subtitle { font-size: clamp(16px, 2vw, 22px); margin-bottom: 20px; }
.capture-layout {
    display: grid;
    grid-template-columns: minmax(330px, 0.9fr) minmax(430px, 1.15fr);
    gap: 28px;
    align-items: start;
}
.capture-hero .capture-layout { gap: 34px; }
.capture-board-card, .capture-evidence-card {
    border: 1px solid rgba(214,196,166,0.24);
    border-radius: 16px;
    background: rgba(18,21,20,0.86);
    box-shadow: 0 20px 48px rgba(0,0,0,0.32);
}
.capture-board-card { padding: 16px; }
.capture-evidence-card { padding: 18px; }
.capture-hero .capture-board-card { padding: 20px; }
.capture-hero .capture-evidence-card { padding: 22px; }
.capture-chip-row { display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 16px; }
.capture-chip {
    display: inline-flex;
    align-items: center;
    min-height: 30px;
    padding: 5px 10px;
    border-radius: 8px;
    border: 1px solid rgba(214,161,95,0.52);
    background: rgba(214,161,95,0.14);
    color: #f0c989;
    font-family: "Fira Code", Consolas, monospace;
    font-size: 13px;
    font-weight: 800;
    text-transform: uppercase;
}
.capture-chip.ok { color: #9ad08a; border-color: rgba(122,166,106,0.68); background: rgba(122,166,106,0.14); }
.capture-chip.warn { color: #f0c989; }
.capture-chip.fail { color: #e27b70; border-color: rgba(214,106,95,0.68); background: rgba(214,106,95,0.13); }
.capture-metrics {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 10px;
    margin: 14px 0;
}
.capture-metric {
    min-width: 0;
    padding: 12px;
    border: 1px solid rgba(214,196,166,0.16);
    border-radius: 10px;
    background: rgba(11,14,13,0.72);
}
.capture-metric span {
    display: block;
    color: #9f9588;
    font-family: "Fira Code", Consolas, monospace;
    font-size: 11px;
    font-weight: 800;
    text-transform: uppercase;
}
.capture-metric strong {
    display: block;
    margin-top: 6px;
    color: #f4efe5;
    font-family: "Fira Code", Consolas, monospace;
    font-size: clamp(18px, 2.4vw, 30px);
    line-height: 1.05;
    overflow-wrap: anywhere;
}
.capture-note {
    margin: 10px 0 0;
    color: #d2c7b8;
    font-size: clamp(13px, 1.5vw, 16px);
    line-height: 1.42;
}
.capture-board-card .puzzle-grid {
    width: fit-content !important;
    max-width: none !important;
    margin: 0 auto;
    gap: 7px !important;
    padding: 10px !important;
    border-radius: 14px !important;
}
.capture-board-card .puzzle-tile {
    width: 52px !important;
    height: 52px !important;
    font-size: 22px !important;
    border-radius: 9px !important;
}
.capture-board-card .puzzle-cell {
    width: 48px !important;
    height: 48px !important;
    font-size: 19px !important;
    border-radius: 8px !important;
}
.capture-hero .capture-board-card .puzzle-grid { gap: 9px !important; padding: 14px !important; }
.capture-hero .capture-board-card .puzzle-tile {
    width: 72px !important;
    height: 72px !important;
    font-size: 26px !important;
}
.capture-hero .capture-board-card .puzzle-cell {
    width: 70px !important;
    height: 70px !important;
    font-size: 22px !important;
}
.capture-image-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 8px;
    width: min(100%, 340px);
    margin: 0 auto;
}
.capture-hero .capture-image-grid { width: min(100%, 430px); }
.capture-image-tile {
    position: relative;
    aspect-ratio: 1 / 1;
    border-radius: 10px;
    overflow: hidden;
    border: 3px solid rgba(122,166,106,0.82);
    background: #101715;
}
.capture-image-tile img { width: 100%; height: 100%; object-fit: cover; display: block; }
.capture-image-tile.blank {
    border-color: rgba(214,196,166,0.18);
    background: repeating-linear-gradient(135deg, #090d0c 0 10px, #121715 10px 20px);
}
.capture-image-tile span {
    position: absolute;
    top: 7px;
    left: 7px;
    padding: 2px 7px;
    border-radius: 5px;
    background: rgba(5,8,7,0.82);
    font-family: "Fira Code", Consolas, monospace;
    font-weight: 800;
}
.capture-progress {
    height: 10px;
    border-radius: 99px;
    background: rgba(214,196,166,0.18);
    overflow: hidden;
    margin-top: 18px;
}
.capture-progress > div {
    height: 100%;
    background: #7aa66a;
}
.capture-ready {
    position: fixed;
    right: 12px;
    bottom: 8px;
    color: rgba(244,239,229,0.34);
    font-size: 10px;
}
</style>
"""


def render_web_gif_capture(slug: str, frame: int, *, image_mode: bool = False) -> None:
    """Render one browser-capturable frame from a real algorithm run."""
    st.markdown(CAPTURE_CSS, unsafe_allow_html=True)
    try:
        spec = get_spec(slug)
        evidence = run_demo(spec)
    except Exception as exc:  # Keep capture route honest instead of crashing.
        st.markdown(_error_page(slug, exc), unsafe_allow_html=True)
        return

    frame_index = max(0, min(int(frame), len(evidence.states) - 1))
    state = evidence.states[frame_index]
    step_number = evidence.state_indices[frame_index] if frame_index < len(evidence.state_indices) else frame_index
    total_steps = max(1, len(evidence.actions))
    h_value = HEURISTICS["Manhattan Distance"](state, goal=spec.goal)
    g_value = min(step_number, total_steps)
    status_label, status_class, status_note = _status(evidence)
    previous_action, next_action = _actions(evidence, step_number)
    result = evidence.result
    metrics = [
        ("Step", f"{step_number}/{total_steps}"),
        ("g / h / f", f"{g_value} / {h_value} / {g_value + h_value}"),
        ("Expanded", str(getattr(result, "nodes_expanded", "-") if result else "-")),
        ("Frontier", str(getattr(result, "max_frontier_size", "-") if result else "-")),
    ]
    metric_markup = "".join(
        f'<div class="capture-metric"><span>{escape(label)}</span><strong>{escape(value)}</strong></div>'
        for label, value in metrics
    )
    facts = " | ".join(evidence.facts[:3])
    profile_class = " capture-hero" if image_mode else ""
    board_markup = _image_board(state) if image_mode else render_puzzle_board(state, size="normal", goal=spec.goal, as_html=True)
    progress = int(100 * (frame_index + 1) / max(1, len(evidence.states)))
    st.markdown(
        f"""
        <main class="capture-page{profile_class}">
            <h1 class="capture-title">{escape(spec.algorithm)}</h1>
            <p class="capture-subtitle">Source: live Streamlit browser capture. No mockup renderer. {escape(spec.mechanism)}</p>
            <section class="capture-layout">
                <div class="capture-board-card">
                    {board_markup}
                    <div class="capture-progress"><div style="width:{progress}%"></div></div>
                </div>
                <div class="capture-evidence-card">
                    <div class="capture-chip-row">
                        <span class="capture-chip">{escape(spec.group)}</span>
                        <span class="capture-chip {status_class}">{escape(status_label)}</span>
                        <span class="capture-chip">Frame {frame_index + 1}/{len(evidence.states)}</span>
                    </div>
                    <div class="capture-metrics">{metric_markup}</div>
                    <p class="capture-note"><strong>Previous:</strong> {escape(previous_action)} &nbsp; <strong>Next:</strong> {escape(next_action)}</p>
                    <p class="capture-note"><strong>Truth:</strong> {escape(status_note)}</p>
                    <p class="capture-note"><strong>Evidence:</strong> {escape(facts)}</p>
                    <p class="capture-note"><strong>Caveat:</strong> {escape(spec.academic_caveat)}</p>
                </div>
            </section>
            <div class="capture-ready">capture-ready-{escape(spec.slug)}-{frame_index}</div>
        </main>
        """,
        unsafe_allow_html=True,
    )


def _status(evidence: DemoEvidence) -> tuple[str, str, str]:
    result = evidence.result
    if result is None:
        return "WEB RUN: TOURNAMENT", "warn", "Tournament scoring is real, but it is not a single solution path."
    if result.success and result.goal_reached:
        if result.optimality_proven:
            return "WEB RUN: SOLVED + OPTIMAL", "ok", "This run reached the selected goal and has an optimality certificate."
        return "WEB RUN: SOLVED", "ok", "This run reached the selected goal, but no optimality certificate is claimed."
    if result.success:
        return "WEB RUN: PARTIAL / MODEL", "warn", "The algorithm produced valid model evidence, not a solved 15-puzzle path."
    return "WEB RUN: NOT SOLVED", "fail", "The web run completed without a solution claim; the GIF shows that failure honestly."


def _actions(evidence: DemoEvidence, step: int) -> tuple[str, str]:
    if not evidence.actions:
        return "Initialize", "No linear action"
    previous = "Initialize" if step == 0 else evidence.actions[min(step - 1, len(evidence.actions) - 1)]
    next_action = "Goal" if step >= len(evidence.actions) else evidence.actions[step]
    return previous, next_action


def _image_board(state: tuple[int, ...]) -> str:
    tiles = generate_sample_tiles("Cyberpunk City")
    cells: list[str] = []
    for value in state:
        if value == 0:
            cells.append('<div class="capture-image-tile blank"></div>')
        else:
            src = tiles.get(value, "")
            cells.append(
                '<div class="capture-image-tile">'
                f'<span>{value}</span><img src="{escape(src)}" alt="tile {value}">'
                '</div>'
            )
    return f'<div class="capture-image-grid">{"".join(cells)}</div>'


def _error_page(slug: str, exc: Exception) -> str:
    return f"""
    <main class="capture-page">
        <h1 class="capture-title">Capture failed: {escape(slug)}</h1>
        <p class="capture-subtitle">Source: live Streamlit browser capture. The web route did not hide this error.</p>
        <section class="capture-evidence-card">
            <div class="capture-chip-row"><span class="capture-chip fail">WEB RUN ERROR</span></div>
            <p class="capture-note">{escape(type(exc).__name__)}: {escape(str(exc))}</p>
        </section>
        <div class="capture-ready">capture-ready-error</div>
    </main>
    """
