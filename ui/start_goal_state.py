"""State helpers for the shared start/goal puzzle contract."""

from __future__ import annotations

import streamlit as st

from core.puzzle import validate_state


STATE_DEPENDENT_KEYS = (
    "last_result",
    "last_run_signature",
    "last_run_variation_seed",
    "last_run_variation_action_order",
    "last_run_variation_tie_breaker",
    "run_forced_action_order",
    "run_forced_action_order_for",
    "run_belief_demo_applied",
    "last_benchmark_signature",
    "benchmark_run_seeds",
    "last_benchmark_random_seed",
    "tournament_result",
    "advanced_outputs",
    "advanced_result_mode",
    "play_state",
    "play_moves",
    "play_history",
    "play_start_ref",
    "play_goal_ref",
    "play_assisted",
    "play_solution_path",
    "play_solution_actions",
    "play_solution_idx",
    "play_solution_res",
    "play_solution_base_history",
    "play_solution_base_moves",
    "play_auto_run",
    "play_auto_done_pending",
    "play_slider_val",
    "play_slider_version",
    "play_comparison_baseline",
    "play_comparison_base_history",
    "play_comparison_base_moves",
    "play_comparison_base_assisted",
    "play_comparison_goal",
    "play_comparison_results",
    "play_comparison_last_algorithm",
    "play_victory_signature",
    "play_victory_message_key",
    "play_victory_balloons_pending",
)


def state_text(state: tuple[int, ...]) -> str:
    rows = [
        " ".join(str(tile) for tile in state[row_start:row_start + 4])
        for row_start in range(0, 16, 4)
    ]
    return "\n".join(rows)


def normalize_state(state: tuple[int, ...]) -> tuple[int, ...]:
    normalized = tuple(state)
    validate_state(normalized)
    return normalized


def sync_state_input(input_key: str, state: tuple[int, ...]) -> None:
    """Keep text inputs in sync with external state changes without erasing drafts."""
    ref_key = f"{input_key}_state_ref"
    normalized = tuple(state)
    if st.session_state.get(ref_key) != normalized:
        st.session_state[input_key] = state_text(normalized)
        st.session_state[ref_key] = normalized


def clear_start_goal_dependents() -> None:
    """Clear cached outputs that were computed for an older start/goal pair."""
    for key in STATE_DEPENDENT_KEYS:
        st.session_state.pop(key, None)
    for key in list(st.session_state):
        if str(key).startswith("play_slider_val_"):
            st.session_state.pop(key, None)
    st.session_state.benchmark_results = []


def apply_start_state(state: tuple[int, ...]) -> None:
    st.session_state.start_state = normalize_state(state)
    clear_start_goal_dependents()


def apply_goal_state(state: tuple[int, ...]) -> None:
    st.session_state.goal_state = normalize_state(state)
    clear_start_goal_dependents()
