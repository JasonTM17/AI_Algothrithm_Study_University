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
from core.puzzle import GOAL_STATE, is_solvable
from core.randomness import activate_run_variation, apply_run_variation, make_run_variation
from ui.academic_panels import render_academic_header, render_extension_warning
from ui.ai_vs_ai_tournament import render_ai_vs_ai_tournament
from ui.components import (
    render_result_metrics,
    render_path_animation,
    render_run_variation_metadata,
    render_start_goal_contract,
    render_trace_table,
)
from ui.localization import translate


ADVANCED_TRACE_ROWS = 80


def t(key, **kwargs):
    global_lang = st.session_state.get("global_lang_select")
    return translate(global_lang, key, **kwargs)


def _mode_key(mode: str) -> str:
    return "".join(char if char.isalnum() else "_" for char in mode).strip("_").lower()


def _store_advanced_outputs(mode: str, outputs: list[dict]) -> None:
    st.session_state["advanced_result_mode"] = mode
    st.session_state["advanced_outputs"] = outputs


def _current_advanced_outputs(mode: str) -> list[dict]:
    if st.session_state.get("advanced_result_mode") != mode:
        return []
    return st.session_state.get("advanced_outputs", [])


def _next_variation(fn_name: str):
    variation = make_run_variation(
        fn_name,
        previous_seed=st.session_state.get("advanced_variation_seed"),
        previous_action_order=st.session_state.get("advanced_variation_action_order"),
        previous_tie_breaker=st.session_state.get("advanced_variation_tie_breaker"),
    )
    st.session_state["advanced_variation_seed"] = variation.seed
    st.session_state["advanced_variation_action_order"] = variation.action_order
    st.session_state["advanced_variation_tie_breaker"] = variation.tie_breaker
    return variation


def _with_variation(result, variation, *, randomizes_path: bool | None = None):
    apply_run_variation(result, variation)
    if randomizes_path is not None:
        result.variation_randomizes_path = randomizes_path
    return result


def _run_with_variation(variation, solver, **kwargs):
    with activate_run_variation(variation):
        result = solver(**kwargs)
    return _with_variation(result, variation)


def _result_entry(title: str, result, *, note: str | None = None) -> dict:
    return {"title": title, "result": result, "note": note}


def _render_advanced_outputs(outputs: list[dict]) -> None:
    if not outputs:
        return

    st.markdown("---")
    st.subheader(t("adv_result_section"))
    for entry in outputs:
        result = entry["result"]
        st.markdown(f"#### {entry['title']}")
        if entry.get("note"):
            st.info(entry["note"])
        render_result_metrics(result)
        render_run_variation_metadata(result)
        if result.message:
            with st.expander(t("adv_model_evidence"), expanded=not bool(result.path)):
                st.text(result.message)
        if result.path_verified and result.path:
            with st.expander(t("run_sol_path"), expanded=False):
                render_path_animation(
                    result.path,
                    result.actions,
                    key=f"advanced_path_{_mode_key(entry['title'])}",
                    reaches_goal=result.goal_reached,
                )
        if result.trace:
            with st.expander(t("run_trace_steps"), expanded=False):
                render_trace_table(result.trace, max_rows=ADVANCED_TRACE_ROWS)


def render_advanced_tab(start: tuple[int, ...], goal: tuple[int, ...] = GOAL_STATE) -> None:
    """Render academic extensions and AI-vs-AI scoring for 15-puzzle."""
    st.title(t("adv_title"))
    render_academic_header(
        t("adv_hero_title"),
        t("adv_hero_desc"),
        t("adv_hero_kicker"),
    )
    render_extension_warning(t=t)
    render_start_goal_contract(start, goal, is_solvable(start, goal))

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

    if mode == "AI-vs-AI Tournament":
        render_ai_vs_ai_tournament(start, goal)
        return

    base_kw = dict(start=start, goal=goal)
    csp_search_kw = dict(**base_kw, timeout=30.0)
    mode_key = _mode_key(mode)

    if mode == "CSP Definition & Propagation":
        horizon = st.number_input("Time Horizon", 1, 5, 3, key="csp_t")
        if st.button(t("adv_run_model"), key=f"adv_run_{mode_key}", type="primary"):
            variation = _next_variation("constraint_propagation")
            _store_advanced_outputs(mode, [
                _result_entry(
                    "CSP Definition",
                    _with_variation(
                        csp_definition(time_horizon=horizon, **base_kw),
                        variation,
                        randomizes_path=False,
                    ),
                ),
                _result_entry(
                    "Constraint Propagation",
                    _run_with_variation(
                        variation,
                        constraint_propagation,
                        time_horizon=horizon,
                        **base_kw,
                    ),
                ),
            ])

    elif mode == "Backtracking & Min-Conflicts":
        st.subheader("Bounded Transition-CSP Planning")
        st.info(
            "Illustrative depth-first planning with heuristic value ordering; "
            "not an MRV/forward-checking CSP solver."
        )
        if st.button(t("adv_run_model"), key=f"adv_run_{mode_key}", type="primary"):
            planning_variation = _next_variation("backtracking_search")
            contrast_variation = _next_variation("min_conflicts")
            _store_advanced_outputs(mode, [
                _result_entry(
                    "Bounded Transition-CSP Planning",
                    _run_with_variation(
                        planning_variation,
                        backtracking_search,
                        **csp_search_kw,
                        max_steps=5000,
                    ),
                ),
                _result_entry(
                    "Min-Conflicts Tile-Placement Contrast",
                    _with_variation(
                        min_conflicts(
                            **csp_search_kw,
                            max_iterations=10000,
                            seed=contrast_variation.solver_seed,
                        ),
                        contrast_variation,
                    ),
                    note="This contrast may swap arbitrary positions, so it cannot certify a legal 15-puzzle path.",
                ),
            ])

    elif mode == "Constraint Graphs & Path Consistency":
        horizon = st.number_input("Time Horizon", 1, 3, 2, key="cg_t")
        if st.button(t("adv_run_model"), key=f"adv_run_{mode_key}", type="primary"):
            variation = _next_variation("solve_csp_constraint_graphs")
            _store_advanced_outputs(mode, [
                _result_entry(
                    "Constraint Graphs",
                    _with_variation(solve_csp_constraint_graphs(time_horizon=horizon, **base_kw), variation),
                ),
                _result_entry(
                    "Path Consistency",
                    _with_variation(path_consistency(**base_kw), variation),
                ),
            ])

    elif mode == "AND-OR Search (Nondeterministic)":
        depth = st.number_input("Max Depth", 1, 15, 5, key="andor_depth")
        support = st.slider("Deflection outcome support", 0.0, 1.0, 0.3, key="andor_prob")
        st.caption(
            "At 0, only the intended outcome exists. Above 0, modeled deflections are possible; "
            "AND-OR does not weight branches by probability."
        )
        if st.button(t("adv_run_model"), key=f"adv_run_{mode_key}", type="primary"):
            variation = _next_variation("and_or_search")
            _store_advanced_outputs(mode, [
                _result_entry(
                    "AND-OR Search",
                    _with_variation(
                        and_or_search(
                            max_depth=depth,
                            nondet_prob=support,
                            timeout=30.0,
                            action_order=variation.action_order,
                            **base_kw,
                        ),
                        variation,
                    ),
                ),
            ])

    elif mode == "No Observation (Belief State)":
        count = st.number_input("Belief States", 2, 10, 5, key="no_obs_n")
        steps = st.number_input("Max Steps", 5, 50, 20, key="no_obs_steps")
        st.info(t("adv_no_observation_note"))
        if st.button(t("adv_run_model"), key=f"adv_run_{mode_key}", type="primary"):
            variation = _next_variation("no_observation_search")
            _store_advanced_outputs(mode, [
                _result_entry(
                    "No Observation Search",
                    _with_variation(
                        no_observation_search(
                            num_belief_states=count,
                            max_steps=steps,
                            seed=variation.solver_seed,
                            timeout=30.0,
                            action_order=variation.action_order,
                            **base_kw,
                        ),
                        variation,
                    ),
                    note=t("adv_strict_certificate"),
                ),
            ])

    elif mode == "Partially Observable":
        count = st.number_input("Belief States", 2, 10, 5, key="po_n")
        steps = st.number_input("Max Steps", 5, 50, 20, key="po_steps")
        st.info(t("adv_partial_observation_note"))
        if st.button(t("adv_run_model"), key=f"adv_run_{mode_key}", type="primary"):
            variation = _next_variation("partially_observable_search")
            _store_advanced_outputs(mode, [
                _result_entry(
                    "Partially Observable Search",
                    _with_variation(
                        partially_observable_search(
                            num_belief_states=count,
                            max_steps=steps,
                            seed=variation.solver_seed,
                            timeout=30.0,
                            action_order=variation.action_order,
                            **base_kw,
                        ),
                        variation,
                    ),
                    note=t("adv_strict_certificate"),
                ),
            ])

    elif mode == "Online Search (LRTA*)":
        heuristic = st.selectbox("Heuristic", list(HEURISTICS.keys()), key="lrta_h")
        steps = st.number_input("Max Steps", 100, 100000, 10000, key="lrta_steps")
        if st.button(t("adv_run_model"), key=f"adv_run_{mode_key}", type="primary"):
            variation = _next_variation("online_search_lrta")
            _store_advanced_outputs(mode, [
                _result_entry(
                    "LRTA*",
                    _with_variation(
                        online_search_lrta(
                            heuristic=heuristic,
                            max_steps=steps,
                            timeout=30.0,
                            action_order=variation.action_order,
                            **base_kw,
                        ),
                        variation,
                    ),
                ),
            ])

    elif mode == "Minimax Game":
        st.caption("15-puzzle has no natural opponent; this is an artificial MAX/MIN extension.")
        depth = st.number_input("Game Tree Depth", 1, 5, 3, key="mm_depth")
        heuristic = st.selectbox("Heuristic", list(HEURISTICS.keys()), key="mm_h")
        if st.button(t("adv_run_model"), key=f"adv_run_{mode_key}", type="primary"):
            variation = _next_variation("minimax")
            _store_advanced_outputs(mode, [
                _result_entry(
                    "Minimax",
                    _with_variation(
                        minimax(
                            depth=depth,
                            heuristic=heuristic,
                            timeout=30.0,
                            action_order=variation.action_order,
                            **base_kw,
                        ),
                        variation,
                    ),
                ),
            ])

    elif mode == "Alpha-Beta Pruning Game":
        st.caption("Alpha-Beta is shown as an artificial MAX/MIN extension over 15-puzzle states.")
        depth = st.number_input("Game Tree Depth", 1, 5, 3, key="ab_depth")
        heuristic = st.selectbox("Heuristic", list(HEURISTICS.keys()), key="ab_h")
        if st.button(t("adv_run_model"), key=f"adv_run_{mode_key}", type="primary"):
            variation = _next_variation("alpha_beta_pruning")
            _store_advanced_outputs(mode, [
                _result_entry(
                    "Alpha-Beta Pruning",
                    _with_variation(
                        alpha_beta_pruning(
                            depth=depth,
                            heuristic=heuristic,
                            timeout=30.0,
                            action_order=variation.action_order,
                            **base_kw,
                        ),
                        variation,
                    ),
                ),
            ])

    elif mode == "Expectimax (Stochastic)":
        depth = st.number_input("Game Tree Depth", 1, 5, 3, key="em_depth")
        heuristic = st.selectbox("Heuristic", list(HEURISTICS.keys()), key="em_h")
        success_prob = st.slider("Success Probability", 0.5, 1.0, 0.8, key="em_sp")
        if st.button(t("adv_run_model"), key=f"adv_run_{mode_key}", type="primary"):
            variation = _next_variation("expectimax")
            _store_advanced_outputs(mode, [
                _result_entry(
                    "Expectimax",
                    _with_variation(
                        expectimax(
                            depth=depth,
                            heuristic=heuristic,
                            success_prob=success_prob,
                            seed=variation.solver_seed,
                            timeout=30.0,
                            action_order=variation.action_order,
                            **base_kw,
                        ),
                        variation,
                    ),
                ),
            ])

    _render_advanced_outputs(_current_advanced_outputs(mode))
