"""Streamlit UI for AI-vs-AI 15-puzzle tournament scoring."""

from __future__ import annotations

import streamlit as st

from core.ai_vs_ai_tournament import (
    ELIGIBLE_TOURNAMENT_SOLVERS,
    AgentRoundScore,
    TournamentAgentConfig,
    TournamentResult,
    run_ai_vs_ai_tournament,
)
from core.heuristics import HEURISTICS
from core.puzzle import GOAL_STATE
from ui.components import render_puzzle_board
from ui.localization import translate


def t(key, **kwargs):
    global_lang = st.session_state.get("global_lang_select", "Tiếng Việt")
    return translate(global_lang, key, **kwargs)


def render_ai_vs_ai_tournament(
    start: tuple[int, ...],
    goal: tuple[int, ...] = GOAL_STATE,
) -> None:
    """Render a scored two-agent tournament over the same 15-puzzle states."""
    st.subheader(t("tournament_title"))
    st.info(
        t("tournament_desc")
    )
    solver_labels = list(ELIGIBLE_TOURNAMENT_SOLVERS)
    col_a, col_b = st.columns(2)
    with col_a:
        agent_a_algo = st.selectbox(
            t("tournament_agent_a_algorithm"),
            solver_labels,
            index=solver_labels.index("A*"),
            key="tournament_agent_a",
        )
        agent_a_seed = st.number_input(t("tournament_agent_a_seed"), 0, 2**31 - 1, 42, key="tournament_agent_a_seed")
    with col_b:
        agent_b_algo = st.selectbox(
            t("tournament_agent_b_algorithm"),
            solver_labels,
            index=solver_labels.index("Greedy Best-First"),
            key="tournament_agent_b",
        )
        agent_b_seed = st.number_input(t("tournament_agent_b_seed"), 0, 2**31 - 1, 99, key="tournament_agent_b_seed")

    col_params_1, col_params_2, col_params_3 = st.columns(3)
    with col_params_1:
        rounds = st.number_input(t("tournament_rounds"), 1, 10, 1, key="tournament_rounds")
        round_depth = st.number_input(t("tournament_round_depth"), 1, 50, 10, key="tournament_depth")
    with col_params_2:
        max_nodes = st.number_input(t("tournament_max_nodes"), 1000, 500000, 50000, step=5000, key="tournament_nodes")
        max_depth = st.number_input(t("tournament_max_depth"), 1, 100, 20, key="tournament_max_depth")
    with col_params_3:
        timeout = st.number_input(t("tournament_timeout"), 5, 300, 30, key="tournament_timeout")
        base_seed = st.number_input(t("tournament_base_seed"), 0, 99999, 42, key="tournament_base_seed")

    heuristic = st.selectbox(
        t("tournament_reference_heuristic"),
        list(HEURISTICS),
        index=list(HEURISTICS).index("Manhattan Distance"),
        key="tournament_heuristic",
    )
    action_order = st.selectbox(t("run_action_order"), ["LRUD", "UDLR", "RLDU", "DURL"], key="tournament_action_order")

    if st.button(t("tournament_run"), key="btn_run_tournament", type="primary"):
        st.session_state.tournament_result = run_ai_vs_ai_tournament(
            TournamentAgentConfig(
                label=f"AI A ({agent_a_algo})",
                solver_name=ELIGIBLE_TOURNAMENT_SOLVERS[agent_a_algo],
                seed=int(agent_a_seed),
            ),
            TournamentAgentConfig(
                label=f"AI B ({agent_b_algo})",
                solver_name=ELIGIBLE_TOURNAMENT_SOLVERS[agent_b_algo],
                seed=int(agent_b_seed),
            ),
            start=start,
            goal=goal,
            rounds=int(rounds),
            round_depth=int(round_depth),
            base_seed=int(base_seed),
            timeout=float(timeout),
            max_nodes=int(max_nodes),
            max_depth=int(max_depth),
            heuristic=heuristic,
            action_order=action_order,
        )

    result: TournamentResult | None = st.session_state.get("tournament_result")
    if result is None:
        st.info(t("tournament_empty_state"))
        return
    _render_tournament_summary(result)
    _render_rounds(result)


def _render_tournament_summary(result: TournamentResult) -> None:
    metric_a, metric_b, metric_c = st.columns(3)
    metric_a.metric(result.agent_a_label, result.agent_a_total)
    metric_b.metric(result.agent_b_label, result.agent_b_total)
    metric_c.metric(t("tournament_winner"), result.winner)
    st.caption(result.tie_break_detail)


def _render_rounds(result: TournamentResult) -> None:
    for round_result in result.rounds:
        with st.expander(t("tournament_round_label", number=round_result.round_number), expanded=round_result.round_number == 1):
            st.caption(round_result.reference_status)
            render_puzzle_board(round_result.start_state, highlight_correct=True)
            if round_result.agent_a is None or round_result.agent_b is None:
                st.warning(t("tournament_round_skipped"))
                continue
            st.dataframe(
                [_score_row(round_result.agent_a), _score_row(round_result.agent_b)],
                width="stretch",
                hide_index=True,
            )


def _score_row(score: AgentRoundScore) -> dict[str, object]:
    return {
        t("tournament_agent_col"): score.agent_label,
        t("run_algo"): score.algorithm,
        t("tournament_points_col"): score.points,
        t("mc_status"): score.status,
        t("mc_cost"): "-" if score.cost is None else score.cost,
        t("tournament_optimal_cost_col"): "-" if score.optimal_cost is None else score.optimal_cost,
        t("tournament_excess_col"): "-" if score.excess_cost is None else score.excess_cost,
        t("mc_runtime"): f"{score.runtime:.4f}s",
        t("tournament_nodes_col"): score.nodes,
        t("run_seed"): "Deterministic" if score.random_seed is None else score.random_seed,
        t("tc_reason"): score.reason,
    }
