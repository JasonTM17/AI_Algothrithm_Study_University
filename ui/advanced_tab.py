"""Advanced 15-puzzle concept and tournament Streamlit tab."""

from html import escape

import streamlit as st

from algorithms.adversarial import alpha_beta_pruning, expectimax, minimax
from algorithms.complex_env import (
    BELIEF_PLANNERS,
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
from ui.action_states import render_action_state
from ui.academic_panels import render_academic_header, render_extension_warning
from ui.ai_vs_ai_tournament import render_ai_vs_ai_tournament
from ui.components import (
    render_result_metrics,
    render_path_animation,
    render_search_tree,
    render_start_goal_contract,
    render_trace_table,
)
from ui.belief_controls import render_known_positions_editor
from ui.localization import translate
from ui.run_and_or_panel import render_and_or_controls


ADVANCED_TRACE_ROWS = 80
ADVANCED_MODES = [
    "AI-vs-AI Tournament",
    "CSP Definition & Propagation",
    "Backtracking Search + Manhattan Distance heuristic",
    "Constraint Graphs & Path Consistency",
    "AND-OR Search (Nondeterministic)",
    "No Observation (Belief State)",
    "Partially Observable",
    "Online Search (LRTA*)",
    "Minimax Game",
    "Alpha-Beta Pruning Game",
    "Expectimax (Stochastic)",
]
ADVANCED_MODE_CARDS = [
    ("AI-vs-AI Tournament", "adv_card_tournament_desc", "A* optimal reference"),
    ("CSP Definition & Propagation", "adv_card_csp_desc", "AC-3 horizon evidence"),
    ("Backtracking Search + Manhattan Distance heuristic", "adv_card_backtracking_desc", "Legal heuristic-ordered path"),
    ("Constraint Graphs & Path Consistency", "adv_card_csp_desc", "CSP consistency evidence"),
    ("AND-OR Search (Nondeterministic)", "adv_card_uncertainty_desc", "Contingency plan sample"),
    ("No Observation (Belief State)", "adv_card_uncertainty_desc", "Belief evidence only"),
    ("Partially Observable", "adv_card_uncertainty_desc", "Observation trace"),
    ("Online Search (LRTA*)", "adv_card_online_desc", "Online trajectory"),
    ("Minimax Game", "adv_card_game_desc", "Artificial game tree"),
    ("Alpha-Beta Pruning Game", "adv_card_game_desc", "Pruned game tree"),
    ("Expectimax (Stochastic)", "adv_card_game_desc", "Chance outcome sample"),
]


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


def _has_search_tree(result) -> bool:
    return bool(getattr(result, "search_tree_nodes", None) and getattr(result, "search_tree_edges", None))


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
        if _has_search_tree(result):
            with st.expander(t("run_search_tree"), expanded=False):
                render_search_tree(result, max_nodes=40)
        if result.trace:
            with st.expander(t("run_trace_steps"), expanded=False):
                render_trace_table(result.trace, max_rows=ADVANCED_TRACE_ROWS)


def _render_advanced_mode_cards() -> None:
    render_action_state(
        title=t("adv_empty_title"),
        body=t("adv_empty_body"),
        kicker=t("action_state_kicker"),
    )
    for row_start in range(0, len(ADVANCED_MODE_CARDS), 3):
        cols = st.columns(min(3, len(ADVANCED_MODE_CARDS) - row_start))
        for col, (mode, desc_key, guarantee) in zip(cols, ADVANCED_MODE_CARDS[row_start:row_start + 3]):
            with col:
                st.markdown(
                    f"""
                    <div class="advanced-mode-card">
                        <h3>{escape(mode)}</h3>
                        <p>{escape(t(desc_key))}</p>
                        <div class="advanced-mode-row"><strong>{escape(t("adv_card_guarantee"))}</strong><span>{escape(guarantee)}</span></div>
                        <div class="advanced-mode-row"><strong>{escape(t("adv_card_caveat"))}</strong><span>{escape(t("adv_card_standard_caveat"))}</span></div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                if st.button(t("adv_mode_card_cta"), key=f"adv_pick_{_mode_key(mode)}", width="stretch"):
                    st.session_state["advanced_pending_mode"] = mode
                    st.rerun()


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
    pending_mode = st.session_state.pop("advanced_pending_mode", None)
    if pending_mode:
        st.session_state["complex_mode_v2"] = pending_mode
    if st.session_state.get("complex_mode_v2") in {"Backtracking", "Backtracking & Min-Conflicts"}:
        st.session_state["complex_mode_v2"] = "Backtracking Search + Manhattan Distance heuristic"
    mode = st.selectbox(
        t("adv_model_select"),
        [mode_prompt, *ADVANCED_MODES],
        key="complex_mode_v2",
    )

    if mode == mode_prompt:
        _render_advanced_mode_cards()
        return

    if mode == "AI-vs-AI Tournament":
        render_ai_vs_ai_tournament(start, goal)
        return

    base_kw = dict(start=start, goal=goal)
    csp_search_kw = dict(**base_kw, timeout=30.0)
    mode_key = _mode_key(mode)

    if mode == "CSP Definition & Propagation":
        horizon = st.number_input(t("adv_time_horizon"), 1, 5, 3, key="csp_t")
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

    elif mode == "Backtracking Search + Manhattan Distance heuristic":
        st.subheader(t("adv_bounded_transition_planning"))
        st.info(t("adv_bounded_transition_info"))
        if st.button(t("adv_run_model"), key=f"adv_run_{mode_key}", type="primary"):
            planning_variation = _next_variation("backtracking_search")
            _store_advanced_outputs(mode, [
                _result_entry(
                    t("adv_bounded_transition_planning"),
                    _run_with_variation(
                        planning_variation,
                        backtracking_search,
                        **csp_search_kw,
                        max_steps=5000,
                    ),
                ),
            ])

    elif mode == "Constraint Graphs & Path Consistency":
        horizon = st.number_input(t("adv_time_horizon"), 1, 3, 2, key="cg_t")
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
        depth = st.number_input(t("adv_max_depth"), 1, 15, 5, key="andor_depth")
        support = render_and_or_controls(t, key="andor_deflection_mode")
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
        count = st.number_input(t("adv_belief_states"), 2, 10, 5, key="no_obs_n")
        steps = st.number_input(t("adv_max_steps"), 5, 50, 20, key="no_obs_steps")
        known_positions, known_error = render_known_positions_editor(
            t,
            key="no_obs_known_matrix",
            start=start,
            default_count=0,
        )
        planner = st.selectbox(
            t("run_belief_planner"), list(BELIEF_PLANNERS), index=1,
            key="no_obs_belief_planner", help=t("run_belief_planner_help"),
        )
        st.info(t("adv_no_observation_note"))
        if st.button(
            t("adv_run_model"), key=f"adv_run_{mode_key}", type="primary",
            disabled=known_error is not None,
        ):
            variation = _next_variation("no_observation_search")
            _store_advanced_outputs(mode, [
                _result_entry(
                    "No Observation Search",
                    _with_variation(
                        no_observation_search(
                            num_belief_states=count,
                            max_steps=steps,
                            known_positions=known_positions,
                            belief_planner=planner,
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
        count = st.number_input(t("adv_belief_states"), 2, 10, 5, key="po_n")
        steps = st.number_input(t("adv_max_steps"), 5, 50, 20, key="po_steps")
        known_positions, known_error = render_known_positions_editor(
            t,
            key="po_known_matrix",
            start=start,
            default_count=2,
        )
        planner = st.selectbox(
            t("run_belief_planner"), list(BELIEF_PLANNERS), index=1,
            key="po_belief_planner", help=t("run_belief_planner_help"),
        )
        st.info(t("adv_partial_observation_note"))
        if st.button(
            t("adv_run_model"), key=f"adv_run_{mode_key}", type="primary",
            disabled=known_error is not None,
        ):
            variation = _next_variation("partially_observable_search")
            _store_advanced_outputs(mode, [
                _result_entry(
                    "Partially Observable Search",
                    _with_variation(
                        partially_observable_search(
                            num_belief_states=count,
                            max_steps=steps,
                            known_positions=known_positions,
                            belief_planner=planner,
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
        heuristic = st.selectbox(t("adv_heuristic"), list(HEURISTICS.keys()), key="lrta_h")
        steps = st.number_input(t("adv_max_steps"), 100, 100000, 10000, key="lrta_steps")
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
        st.caption(t("adv_minimax_caption"))
        depth = st.number_input(t("adv_game_tree_depth"), 1, 5, 3, key="mm_depth")
        heuristic = st.selectbox(t("adv_heuristic"), list(HEURISTICS.keys()), key="mm_h")
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
        st.caption(t("adv_alpha_beta_caption"))
        depth = st.number_input(t("adv_game_tree_depth"), 1, 5, 3, key="ab_depth")
        heuristic = st.selectbox(t("adv_heuristic"), list(HEURISTICS.keys()), key="ab_h")
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
        depth = st.number_input(t("adv_game_tree_depth"), 1, 5, 3, key="em_depth")
        heuristic = st.selectbox(t("adv_heuristic"), list(HEURISTICS.keys()), key="em_h")
        success_prob = st.slider(t("adv_success_prob"), 0.5, 1.0, 0.8, key="em_sp")
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
