"""Readable, zoomable evidence viewer for Group 6 decision traces."""

from __future__ import annotations

from html import escape

import streamlit as st

from core.group6_decision_lab import Group6LabResult


TREE_MODES = ("Principal variation", "Evaluated nodes", "Pruned branches")


def _principal_cards(result: Group6LabResult, current_index: int) -> str:
    cards = [
        (
            "MAX",
            "Root",
            result.root_value,
            0,
            current_index == 0,
        )
    ]
    cards.extend(
        (
            frame.role,
            f"{frame.intended_action} -> {frame.realized_action}",
            frame.utility,
            frame.index,
            current_index == frame.index,
        )
        for frame in result.frames
    )
    parts = []
    for index, (role, action, utility, ply, active) in enumerate(cards):
        role_class = "chance" if role == "CHANCE" else role.lower()
        active_class = " active" if active else ""
        value = "-" if utility is None else f"{utility:.2f}"
        parts.append(
            f'<div class="node {role_class}{active_class}">'
            f'<b>{escape(role)}</b><span>Ply {ply}</span>'
            f'<strong>{escape(action)}</strong><small>value {value}</small></div>'
        )
        if index < len(cards) - 1:
            parts.append('<div class="edge">-></div>')
    return "".join(parts)


def _event_cards(result: Group6LabResult, mode: str) -> str:
    if mode == "Pruned branches":
        events = [step for step in result.result.trace if step.event == "prune"]
    else:
        events = [
            step
            for step in result.result.trace
            if step.event
            in {
                "evaluate_action",
                "chance_outcome_evaluated",
                "generate",
                "prune",
            }
        ]
    if not events:
        return '<div class="empty">No captured events for this filter.</div>'

    parts = []
    for step in events[:48]:
        role = step.node_type or "NODE"
        role_class = "chance" if role == "CHANCE" else role.lower()
        utility = "-" if step.utility is None else f"{step.utility:.2f}"
        action = step.action or "-"
        details = []
        if step.alpha is not None or step.beta is not None:
            details.append(f"alpha={step.alpha} beta={step.beta}")
        if step.probability is not None:
            details.append(f"P={step.probability:.2f}")
        detail_text = " | ".join(details) or step.event
        parts.append(
            f'<div class="node evidence {role_class}">'
            f'<b>{escape(role)}</b><span>{escape(step.event)}</span>'
            f'<strong>{escape(action)}</strong><small>value {utility}</small>'
            f'<em>{escape(detail_text)}</em></div>'
        )
    return "".join(parts)


def render_group6_tree_viewer(
    result: Group6LabResult,
    *,
    current_index: int,
    mode: str,
    height: int = 430,
) -> None:
    """Render exact captured evidence with local zoom, pan and fullscreen controls."""
    cards = (
        _principal_cards(result, current_index)
        if mode == "Principal variation"
        else _event_cards(result, mode)
    )
    html = f"""
    <div class="shell">
      <div class="toolbar">
        <div>
          <b>{escape(mode)}</b>
          <span class="legend max">MAX</span>
          <span class="legend min">Worst-case</span>
          <span class="legend chance">CHANCE</span>
          <span class="legend prune">Pruned</span>
        </div>
        <div class="tools">
          <button onclick="zoomBy(-0.15)" title="Zoom out">-</button>
          <button onclick="resetView()" title="Reset zoom">1:1</button>
          <button onclick="zoomBy(0.15)" title="Zoom in">+</button>
          <button onclick="fullView()" title="Fullscreen">&#x26F6;</button>
        </div>
      </div>
      <div id="viewport" class="viewport">
        <div id="canvas" class="canvas">{cards}</div>
      </div>
    </div>
    <style>
      * {{ box-sizing: border-box; }}
      body {{ margin: 0; font-family: Inter, system-ui, sans-serif; color: #f4efe5; }}
      .shell {{ height: {height - 8}px; border: 1px solid #425046; background: #0c120f;
        border-radius: 7px; overflow: hidden; }}
      .toolbar {{ height: 54px; padding: 9px 12px; display: flex; align-items: center;
        justify-content: space-between; gap: 12px; border-bottom: 1px solid #344239;
        background: #111914; }}
      .legend {{ display: inline-block; margin-left: 8px; padding: 3px 7px;
        border-radius: 4px; font-size: 11px; border: 1px solid; }}
      .legend.max {{ color: #9ed7bd; border-color: #4b8f6d; }}
      .legend.min {{ color: #f3c983; border-color: #9a6d31; }}
      .legend.chance {{ color: #9cc7ef; border-color: #477aa8; }}
      .legend.prune {{ color: #e6a2a2; border-color: #9d4f4f; }}
      .tools {{ display: flex; gap: 6px; }}
      button {{ min-width: 36px; height: 34px; border: 1px solid #46584c; border-radius: 5px;
        background: #17221b; color: #f4efe5; font-weight: 700; cursor: pointer; }}
      button:hover {{ background: #223128; }}
      .viewport {{ height: calc(100% - 54px); overflow: auto; cursor: grab; }}
      .viewport.dragging {{ cursor: grabbing; user-select: none; }}
      .canvas {{ transform-origin: 0 0; min-width: max-content; padding: 34px;
        display: flex; align-items: center; gap: 12px; flex-wrap: nowrap; }}
      .node {{ width: 154px; min-height: 118px; padding: 12px; display: flex;
        flex-direction: column; gap: 6px; border: 2px solid #4b8f6d; border-radius: 7px;
        background: #142219; box-shadow: 0 8px 20px rgba(0,0,0,.28); }}
      .node.min {{ border-color: #9a6d31; background: #251d12; }}
      .node.chance {{ border-color: #477aa8; background: #121f2b; }}
      .node.active {{ outline: 3px solid #f1d39a; outline-offset: 4px; }}
      .node span, .node small, .node em {{ color: #aebbb3; font-size: 12px; }}
      .node strong {{ font-size: 16px; }}
      .node.evidence {{ width: 174px; min-height: 132px; }}
      .node.evidence:has(span:nth-child(2)) {{ border-style: solid; }}
      .edge {{ color: #83b89a; font-size: 24px; font-weight: 800; }}
      .empty {{ padding: 36px; color: #aebbb3; }}
    </style>
    <script>
      let scale = 1;
      const viewport = document.getElementById("viewport");
      const canvas = document.getElementById("canvas");
      function applyScale() {{ canvas.style.transform = `scale(${{scale}})`; }}
      function zoomBy(delta) {{ scale = Math.min(2.2, Math.max(0.55, scale + delta)); applyScale(); }}
      function resetView() {{ scale = 1; viewport.scrollLeft = 0; viewport.scrollTop = 0; applyScale(); }}
      function fullView() {{
        const shell = document.querySelector(".shell");
        if (!document.fullscreenElement) shell.requestFullscreen();
        else document.exitFullscreen();
      }}
      let dragging = false, startX = 0, startY = 0, left = 0, top = 0;
      viewport.addEventListener("mousedown", (event) => {{
        dragging = true; viewport.classList.add("dragging");
        startX = event.pageX; startY = event.pageY;
        left = viewport.scrollLeft; top = viewport.scrollTop;
      }});
      window.addEventListener("mouseup", () => {{
        dragging = false; viewport.classList.remove("dragging");
      }});
      viewport.addEventListener("mousemove", (event) => {{
        if (!dragging) return;
        viewport.scrollLeft = left - (event.pageX - startX);
        viewport.scrollTop = top - (event.pageY - startY);
      }});
    </script>
    """
    st.iframe(html, height=height, width="stretch", tab_index=0)
