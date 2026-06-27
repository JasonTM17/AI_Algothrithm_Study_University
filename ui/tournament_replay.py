"""Synchronized step replay for two certified tournament trajectories."""

from __future__ import annotations

import time

import streamlit as st

from core.ai_vs_ai_tournament import AgentRoundScore, TournamentRoundResult
from core.metrics import SearchResult
from ui.components import render_puzzle_board, render_search_tree
from ui.localization import translate


def _t(key: str, **kwargs) -> str:
    return translate(st.session_state.get("global_lang_select"), key, **kwargs)


def _set_replay_step(slider_key: str, step: int, max_step: int) -> None:
    st.session_state[slider_key] = max(0, min(step, max_step))


def _reset_replay(slider_key: str, auto_key: str, auto_step_key: str) -> None:
    st.session_state[slider_key] = 0
    st.session_state[auto_key] = False
    st.session_state[auto_step_key] = 0


def _trajectory(score: AgentRoundScore, start: tuple[int, ...]) -> list[tuple[int, ...]]:
    return score.path if score.path else [start]


def _score_search_tree_result(score: AgentRoundScore, goal: tuple[int, ...]) -> SearchResult | None:
    if not score.path_verified or not score.path:
        return None
    return SearchResult(
        success=score.goal_reached,
        algorithm=score.algorithm,
        group="AI-vs-AI Tournament",
        path=list(score.path),
        actions=list(score.actions),
        goal_state=goal,
        cost=len(score.actions),
        depth=len(score.actions),
    )


def _render_agent_step(
    score: AgentRoundScore,
    *,
    start: tuple[int, ...],
    goal: tuple[int, ...],
    replay_step: int,
) -> None:
    path = _trajectory(score, start)
    last_step = len(path) - 1
    shown_step = min(replay_step, last_step)
    action = "Start" if shown_step == 0 else score.actions[shown_step - 1]

    st.markdown(f"#### {score.agent_label}")
    st.caption(
        f"{score.algorithm} · {score.status} · "
        f"{score.points:+d} {_t('tournament_points_suffix')}"
    )
    render_puzzle_board(path[shown_step], size="small", goal=goal)
    st.caption(
        _t(
            "tournament_replay_agent_step",
            step=shown_step,
            total=last_step,
            action=action,
        )
    )
    if replay_step > last_step:
        st.caption(_t("tournament_replay_finished"))
    if shown_step == last_step:
        if score.goal_reached:
            st.success(_t("tournament_replay_goal"))
        elif score.path_verified:
            st.warning(_t("tournament_replay_partial"))
        else:
            st.error(_t("tournament_replay_no_path"))
    tree_result = _score_search_tree_result(score, goal)
    if tree_result and tree_result.search_tree_edges:
        with st.expander(_t("run_search_tree"), expanded=False):
            render_search_tree(tree_result, max_nodes=30)


def render_tournament_replay(round_result: TournamentRoundResult) -> None:
    """Replay both agents on one shared timeline after certificate scoring."""
    if round_result.agent_a is None or round_result.agent_b is None:
        return

    scores = (round_result.agent_a, round_result.agent_b)
    max_step = max(
        len(_trajectory(score, round_result.start_state)) - 1
        for score in scores
    )
    prefix = f"tournament_replay_round_{round_result.round_number}"
    slider_key = f"{prefix}_slider"
    auto_key = f"{prefix}_autoplay"
    auto_step_key = f"{prefix}_auto_step"
    speed_key = f"{prefix}_speed"

    current_step = int(st.session_state.get(slider_key, 0))
    current_step = max(0, min(current_step, max_step))
    st.session_state[slider_key] = current_step

    st.markdown(f"#### {_t('tournament_replay_title')}")
    st.caption(_t("tournament_replay_caption"))

    play_col = st.columns([1])[0]
    with play_col:
        if st.session_state.get(auto_key, False):
            if st.button(_t("play_stop_run"), key=f"{prefix}_stop"):
                st.session_state[auto_key] = False
                st.rerun()
        elif st.button(
            _t("play_auto_run"),
            key=f"{prefix}_play",
            type="primary",
            disabled=max_step == 0,
        ):
            st.session_state[auto_key] = True
            st.session_state[auto_step_key] = current_step
            st.rerun()

    if st.session_state.get(auto_key, False):
        st.session_state[slider_key] = max_step
        st.session_state[auto_key] = False
        st.session_state[auto_step_key] = 0
        st.success(_t("anim_complete"))

    current_step = st.slider(
        _t("tournament_replay_step"),
        0,
        max_step,
        current_step,
        key=slider_key,
        disabled=max_step == 0,
    )

    agent_a_col, agent_b_col = st.columns(2)
    with agent_a_col:
        _render_agent_step(
            round_result.agent_a,
            start=round_result.start_state,
            goal=round_result.goal_state,
            replay_step=current_step,
        )
    with agent_b_col:
        _render_agent_step(
            round_result.agent_b,
            start=round_result.start_state,
            goal=round_result.goal_state,
            replay_step=current_step,
        )

    prev_col, next_col, reset_col = st.columns(3)
    prev_col.button(
        _t("anim_prev"),
        key=f"{prefix}_prev",
        on_click=_set_replay_step,
        args=(slider_key, current_step - 1, max_step),
        disabled=current_step <= 0,
    )
    next_col.button(
        _t("anim_next"),
        key=f"{prefix}_next",
        on_click=_set_replay_step,
        args=(slider_key, current_step + 1, max_step),
        disabled=current_step >= max_step,
    )
    reset_col.button(
        _t("anim_reset"),
        key=f"{prefix}_reset",
        on_click=_reset_replay,
        args=(slider_key, auto_key, auto_step_key),
    )
