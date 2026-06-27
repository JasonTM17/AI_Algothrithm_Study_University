"""Shared controls for partial and missing observation demonstrations."""

from __future__ import annotations

import streamlit as st

from algorithms.complex_env import (
    default_known_positions,
    format_known_positions_matrix,
    parse_known_positions_matrix,
)


def render_known_positions_editor(
    t,
    *,
    key: str,
    start: tuple[int, ...],
    default_count: int,
) -> tuple[dict[int, int], str | None]:
    """Render and validate the 4x4 known-tile observation matrix."""
    source_key = f"{key}_source_state"
    source_state = tuple(start)
    if key not in st.session_state or st.session_state.get(source_key) != source_state:
        defaults = default_known_positions(source_state, default_count)
        st.session_state[key] = format_known_positions_matrix(defaults)
        st.session_state[source_key] = source_state

    matrix_text = st.text_area(
        t("run_known_matrix"),
        key=key,
        height=168,
        help=t("run_known_matrix_help"),
    )
    try:
        known = parse_known_positions_matrix(matrix_text)
    except ValueError as exc:
        message = t("run_known_matrix_error", error=exc)
        st.error(message)
        return {}, message

    mismatches = [position for position, value in known.items() if source_state[position] != value]
    if mismatches:
        first = mismatches[0]
        message = t(
            "run_known_matrix_mismatch",
            row=first // 4 + 1,
            column=first % 4 + 1,
            value=source_state[first],
        )
        st.error(message)
        return known, message

    st.caption(t("run_known_matrix_summary", count=len(known)))
    st.caption(t("run_belief_model_help"))
    return known, None
