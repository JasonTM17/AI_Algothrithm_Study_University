"""Advanced 15-puzzle concept and tournament Streamlit tab."""

import streamlit as st

from algorithms.adversarial import alpha_beta_pruning, expectimax, minimax
from algorithms.complex_env import (
    and_or_search,
    no_observation_search,
    online_search_lrta,
    partially_observable_search,
)
from algorithms.csp import (
    backtracking_search,
    constraint_propagation,
    csp_definition,
    min_conflicts,
    path_consistency,
    solve_csp_constraint_graphs,
)
from core.heuristics import HEURISTICS
from core.puzzle import GOAL_STATE
from ui.academic_panels import render_academic_header, render_extension_warning
from ui.ai_vs_ai_tournament import render_ai_vs_ai_tournament
from ui.components import render_result_metrics, render_trace_table
from ui.localization import translate


def t(key, **kwargs):
    global_lang = st.session_state.get("global_lang_select", "Tiếng Việt")
    return translate(global_lang, key, **kwargs)


def render_advanced_tab(start: tuple[int, ...], goal: tuple[int, ...] = GOAL_STATE) -> None:
    """Render academic extensions and AI-vs-AI scoring for 15-puzzle."""
    st.title(t("adv_title"))
    render_academic_header(
        t("adv_hero_title"),
        t("adv_hero_desc"),
        t("adv_hero_kicker"),
    )
    render_extension_warning(t=t)

    mode_prompt = t("adv_mode_prompt")
    mode = st.selectbox(
        t("adv_model_select"),
        [
            mode_prompt,
            "AI-vs-AI Tournament",
            "CSP Definition & Propagation",
            "Backtracking & Min-Conflicts",
            "Constraint Graphs & Path Consistency",
            "AND-OR Search (Nondeterministic)",
            "No Observation (Belief State)",
            "Partially Observable",
            "Online Search (LRTA*)",
            "Minimax Game",
            "Alpha-Beta Pruning Game",
            "Expectimax (Stochastic)",
        ],
        key="complex_mode_v2",
    )

    if mode == mode_prompt:
        st.info(t("adv_select_mode_help"))
        return

    base_kw = dict(start=start, goal=goal)
    csp_search_kw = dict(**base_kw, timeout=30.0)
    search_kw = dict(**base_kw, timeout=30.0, action_order="LRUD")

    if mode == "AI-vs-AI Tournament":
        render_ai_vs_ai_tournament(start, goal)

    elif mode == "CSP Definition & Propagation":
        horizon = st.number_input("Time Horizon", 1, 5, 3, key="csp_t")
        st.subheader("CSP Definition")
        result = csp_definition(time_horizon=horizon, **base_kw)
        st.markdown(result.message)
        st.subheader("Constraint Propagation")
        propagated = constraint_propagation(time_horizon=horizon, **base_kw)
        st.markdown(propagated.message)

    elif mode == "Backtracking & Min-Conflicts":
        st.subheader("Bounded Transition-CSP Planning")
        st.info(
            "Illustrative depth-first planning with heuristic value ordering; "
            "not an MRV/forward-checking CSP solver."
        )
        result = backtracking_search(**csp_search_kw, max_steps=5000)
        render_result_metrics(result)
        if result.trace:
            render_trace_table(result.trace)
        st.markdown("---")
        st.subheader("Min-Conflicts Tile-Placement Contrast")
        st.warning("This contrast may swap arbitrary positions, so it cannot certify a legal 15-puzzle path.")
        seed = st.number_input("Seed", 0, 99999, 42, key="mc_seed")
        contrast = min_conflicts(**csp_search_kw, max_iterations=10000, seed=seed)
        render_result_metrics(contrast)

    elif mode == "Constraint Graphs & Path Consistency":
        st.subheader("Constraint Graphs")
        horizon = st.number_input("Time Horizon", 1, 3, 2, key="cg_t")
        result = solve_csp_constraint_graphs(time_horizon=horizon, **base_kw)
        st.markdown(result.message)
        st.markdown("---")
        st.subheader("Path Consistency")
        consistent = path_consistency(**base_kw)
        st.markdown(consistent.message)

    elif mode == "AND-OR Search (Nondeterministic)":
        depth = st.number_input("Max Depth", 1, 15, 5, key="andor_depth")
        support = st.slider("Deflection outcome support", 0.0, 1.0, 0.3, key="andor_prob")
        st.caption(
            "At 0, only the intended outcome exists. Above 0, modeled deflections are possible; "
            "AND-OR does not weight branches by probability."
        )
        result = and_or_search(max_depth=depth, nondet_prob=support, **search_kw)
        st.markdown(result.message)

    elif mode == "No Observation (Belief State)":
        count = st.number_input("Belief States", 2, 10, 5, key="no_obs_n")
        steps = st.number_input("Max Steps", 5, 50, 20, key="no_obs_steps")
        seed = st.number_input("Seed", 0, 99999, 42, key="no_obs_seed")
        result = no_observation_search(num_belief_states=count, max_steps=steps, seed=seed, **search_kw)
        render_result_metrics(result)
        if result.trace:
            render_trace_table(result.trace)

    elif mode == "Partially Observable":
        count = st.number_input("Belief States", 2, 10, 5, key="po_n")
        steps = st.number_input("Max Steps", 5, 50, 20, key="po_steps")
        seed = st.number_input("Seed", 0, 99999, 42, key="po_seed")
        result = partially_observable_search(num_belief_states=count, max_steps=steps, seed=seed, **search_kw)
        render_result_metrics(result)
        if result.trace:
            render_trace_table(result.trace)

    elif mode == "Online Search (LRTA*)":
        heuristic = st.selectbox("Heuristic", list(HEURISTICS.keys()), key="lrta_h")
        steps = st.number_input("Max Steps", 100, 100000, 10000, key="lrta_steps")
        result = online_search_lrta(heuristic=heuristic, max_steps=steps, **search_kw)
        render_result_metrics(result)
        if result.trace:
            render_trace_table(result.trace)

    elif mode == "Minimax Game":
        st.caption("15-puzzle has no natural opponent; this is an artificial MAX/MIN extension.")
        depth = st.number_input("Game Tree Depth", 1, 5, 3, key="mm_depth")
        heuristic = st.selectbox("Heuristic", list(HEURISTICS.keys()), key="mm_h")
        result = minimax(depth=depth, heuristic=heuristic, **search_kw)
        render_result_metrics(result)
        st.markdown(result.message)

    elif mode == "Alpha-Beta Pruning Game":
        st.caption("Alpha-Beta is shown as an artificial MAX/MIN extension over 15-puzzle states.")
        depth = st.number_input("Game Tree Depth", 1, 5, 3, key="ab_depth")
        heuristic = st.selectbox("Heuristic", list(HEURISTICS.keys()), key="ab_h")
        result = alpha_beta_pruning(depth=depth, heuristic=heuristic, **search_kw)
        render_result_metrics(result)
        st.markdown(result.message)

    elif mode == "Expectimax (Stochastic)":
        depth = st.number_input("Game Tree Depth", 1, 5, 3, key="em_depth")
        heuristic = st.selectbox("Heuristic", list(HEURISTICS.keys()), key="em_h")
        success_prob = st.slider("Success Probability", 0.5, 1.0, 0.8, key="em_sp")
        seed = st.number_input("Seed", 0, 99999, 42, key="em_seed")
        result = expectimax(depth=depth, heuristic=heuristic, success_prob=success_prob, seed=seed, **search_kw)
        render_result_metrics(result)
        st.markdown(result.message)
