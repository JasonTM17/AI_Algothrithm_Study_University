"""Shared action-oriented empty states for Streamlit pages."""

from __future__ import annotations

from html import escape
from typing import Iterable

import streamlit as st


def render_action_state(
    *,
    title: str,
    body: str,
    bullets: Iterable[str] = (),
    kicker: str = "Next step",
    action_label: str | None = None,
    action_key: str | None = None,
    target_tab_label: str | None = None,
) -> None:
    """Render an empty state that explains context and offers a next action."""
    bullet_items = "".join(f"<li>{escape(item)}</li>" for item in bullets if item)
    bullet_block = f"<ul>{bullet_items}</ul>" if bullet_items else ""
    st.markdown(
        f"""
        <div class="action-state">
            <div class="action-state-kicker">{escape(kicker)}</div>
            <h3>{escape(title)}</h3>
            <p>{escape(body)}</p>
            {bullet_block}
        </div>
        """,
        unsafe_allow_html=True,
    )
    if action_label and action_key and target_tab_label:
        if st.button(action_label, key=action_key, width="stretch"):
            st.session_state["main_tab_label"] = target_tab_label
            st.rerun()
