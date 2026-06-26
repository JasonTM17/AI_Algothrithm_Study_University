"""Single algorithm runner tab."""

import streamlit as st

from core.heuristics import HEURISTICS
from core.metrics import SearchResult
from core.puzzle import GOAL_STATE, is_solvable
from core.randomness import activate_run_variation, apply_run_variation, make_run_variation
from core.solver_dispatch import build_solver_kwargs
from ui.academic_panels import render_academic_header, render_algorithm_role_card, render_exam_path
from ui.components import (
    render_algorithm_evaluation,
    render_path_animation,
    render_result_metrics,
    render_run_variation_metadata,
    render_search_detail_table,
    render_search_tree,
    render_start_goal_contract,
    render_trace_table,
)
from ui.styles import ALGORITHM_FN_MAP, SOLVER_GROUPS


RUN_MAX_NODES_MIN = 1000
RUN_MAX_NODES_DEFAULT = 20000
RUN_MAX_NODES_CAP = 50000
RUN_TRACE_ROWS = 60
RUN_DETAIL_ROWS = 30
RUN_TREE_NODES = 24


def run_completion_notice(algo_name: str, result: SearchResult, t=None) -> tuple[str, str]:
    """Return the UI notice level/text without overstating model success as a solution."""
    if result.success and result.goal_reached:
        if t:
            return "success", t("run_success", algo=algo_name)
        return "success", f"{algo_name} found a solution!"
    if result.success:
        if t:
            return "info", t("run_model_success_no_goal", algo=algo_name)
        return (
            "info",
            f"{algo_name} produced a successful model result, "
            "but it did not certify a standard path to the requested goal.",
        )
    return "warning", f"{algo_name}: {result.message}"


def render_run_algorithm_tab(t=None) -> None:
    tx = t or (lambda key, **kwargs: key.format(**kwargs) if kwargs else key)
    goal = st.session_state.get("goal_state", GOAL_STATE)
    st.title(tx("run_title"))
    render_academic_header(
        tx("run_hero_title"),
        tx("run_hero_desc"),
        tx("run_hero_kicker"),
    )
    render_exam_path("Run", t=t)
    render_start_goal_contract(
        st.session_state.start_state,
        goal,
        is_solvable(st.session_state.start_state, goal),
    )

    col_algo, col_params = st.columns([1, 1])

    with col_algo:
        group = st.selectbox(tx("run_group"), list(SOLVER_GROUPS.keys()), key="algo_group")
        algorithms = SOLVER_GROUPS[group]
        algo_name = st.selectbox(tx("run_algo"), algorithms, key="algo_name")
        selected_fn_name = ALGORITHM_FN_MAP.get(algo_name, "")
        render_algorithm_role_card(algo_name)

        # Only show heuristic for algorithms that use it
        heuristic_options = list(HEURISTICS.keys())
        uninformed_algos = ["BFS", "DFS", "UCS", "IDS"]
        if algo_name not in uninformed_algos:
            heuristic = st.selectbox(tx("run_heuristic"), heuristic_options, key="heuristic_select")
        else:
            heuristic = "Manhattan Distance"  # default, won't be used

        tie_breaker = "FIFO"

    with col_params:
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            max_nodes = st.number_input(
                tx("run_max_nodes"),
                RUN_MAX_NODES_MIN,
                RUN_MAX_NODES_CAP,
                RUN_MAX_NODES_DEFAULT,
                step=1000,
                key="max_nodes",
                help=tx("run_max_nodes_help", limit=RUN_MAX_NODES_CAP),
            )
            max_depth = st.number_input(tx("run_max_depth"), 1, 100, 20, key="max_depth")
        with col_p2:
            timeout = st.number_input(tx("run_timeout"), 5, 600, 60, key="timeout_val")
            st.caption(tx("run_variation_no_path") if not selected_fn_name else tx("run_fresh_seed_help"))
        st.caption(
            tx(
                "run_layout_guard",
                nodes=RUN_MAX_NODES_CAP,
                trace=RUN_TRACE_ROWS,
                tree=RUN_TREE_NODES,
            )
        )

        # Extra params for specific algorithms
        extra_params = {}
        if "Hill Climbing" in algo_name or "Beam" in algo_name:
            max_iter = st.number_input(tx("run_max_iter"), 100, 100000, 10000, key="max_iter")
            extra_params["max_iterations"] = max_iter
        if algo_name == "Random-Restart Hill Climbing":
            extra_params["max_restarts"] = st.number_input(tx("run_max_restarts"), 1, 100, 20, key="max_restarts")
        if algo_name == "Local Beam Search":
            extra_params["beam_width"] = st.number_input(tx("run_beam_width"), 2, 20, 3, key="beam_width")
        if algo_name == "Simulated Annealing":
            extra_params["initial_temp"] = st.number_input(tx("run_init_temp"), 1.0, 1000.0, 100.0, key="init_temp")
            extra_params["cooling_rate"] = st.number_input(tx("run_cooling_rate"), 0.9, 0.9999, 0.9995, key="cooling_rate", format="%0.4f")
            extra_params["min_temp"] = st.number_input(tx("run_min_temp"), 0.001, 1.0, 0.01, key="min_temp", format="%0.3f")
        if algo_name == "Minimax" or algo_name == "Alpha-Beta Pruning":
            extra_params["depth"] = max_depth
        if algo_name == "Expectimax":
            extra_params["depth"] = max_depth
            extra_params["success_prob"] = st.slider(tx("run_success_prob"), 0.1, 1.0, 0.8, key="success_prob")

    run_signature = (
        tuple(st.session_state.start_state), tuple(goal), selected_fn_name, algo_name, heuristic,
        int(max_nodes), int(max_depth), float(timeout), tuple(sorted(extra_params.items())),
    )
    if st.session_state.get("last_run_signature") != run_signature:
        st.session_state.pop("last_result", None)

    if st.button(tx("run_btn"), key="btn_run", type="primary"):
        start = st.session_state.start_state
        if not is_solvable(start, goal):
            st.error(tx("run_error_unsolvable"))
        else:
            fn_name = selected_fn_name
            if not fn_name:
                st.error(tx("run_error_not_found", algo=algo_name))
            else:
                import algorithms.uninformed as u
                import algorithms.informed as inf
                import algorithms.local_search as ls
                import algorithms.complex_env as ce
                import algorithms.csp as csp_mod
                import algorithms.adversarial as adv

                solver_map = {
                    "bfs": u.bfs, "dfs": u.dfs, "ucs": u.ucs, "ids": u.ids,
                    "greedy_best_first": inf.greedy_best_first,
                    "a_star": inf.a_star, "ida_star": inf.ida_star,
                    "simple_hill_climbing": ls.simple_hill_climbing,
                    "steepest_ascent_hill_climbing": ls.steepest_ascent_hill_climbing,
                    "stochastic_hill_climbing": ls.stochastic_hill_climbing,
                    "random_restart_hill_climbing": ls.random_restart_hill_climbing,
                    "local_beam_search": ls.local_beam_search,
                    "simulated_annealing": ls.simulated_annealing,
                    "and_or_search": ce.and_or_search,
                    "no_observation_search": ce.no_observation_search,
                    "partially_observable_search": ce.partially_observable_search,
                    "online_search_lrta": ce.online_search_lrta,
                    "csp_definition": csp_mod.csp_definition,
                    "constraint_propagation": csp_mod.constraint_propagation,
                    "path_consistency": csp_mod.path_consistency,
                    "global_constraints": csp_mod.global_constraints,
                    "backtracking_search": csp_mod.backtracking_search,
                    "min_conflicts": csp_mod.min_conflicts,
                    "solve_csp_constraint_graphs": csp_mod.solve_csp_constraint_graphs,
                    "minimax": adv.minimax,
                    "alpha_beta_pruning": adv.alpha_beta_pruning,
                    "expectimax": adv.expectimax,
                }

                solver_fn = solver_map.get(fn_name)
                if solver_fn is None:
                    st.error(tx("run_error_func_not_found", func=fn_name))
                else:
                    variation = make_run_variation(
                        fn_name,
                        previous_seed=st.session_state.get("last_run_variation_seed"),
                        previous_action_order=st.session_state.get("last_run_variation_action_order"),
                        previous_tie_breaker=st.session_state.get("last_run_variation_tie_breaker"),
                    )
                    run_extra_params = dict(extra_params)
                    if variation.solver_seed is not None:
                        run_extra_params["seed"] = variation.solver_seed
                    kwargs = build_solver_kwargs(
                        fn_name,
                        start=start,
                        goal=goal,
                        timeout=float(timeout),
                        action_order=variation.action_order,
                        max_nodes=int(max_nodes),
                        max_depth=int(max_depth),
                        heuristic=heuristic,
                        tie_breaker=variation.tie_breaker,
                        extra_params=run_extra_params,
                    )

                    with st.spinner(tx("run_spinner_running", algo=algo_name)):
                        try:
                            with activate_run_variation(variation):
                                result = solver_fn(**kwargs)
                            apply_run_variation(result, variation)
                            st.session_state["last_run_variation_seed"] = variation.seed
                            st.session_state["last_run_variation_action_order"] = variation.action_order
                            st.session_state["last_run_variation_tie_breaker"] = variation.tie_breaker

                            st.session_state["last_result"] = result
                            st.session_state["last_run_signature"] = run_signature
                            st.session_state.benchmark_results.append(result)

                            notice_level, notice_text = run_completion_notice(algo_name, result, t=tx)
                            getattr(st, notice_level)(notice_text)
                        except Exception as e:
                            st.error(tx("run_error_exception", algo=algo_name, error=e))

    # Show last result
    if "last_result" in st.session_state and st.session_state.last_result:
        result = st.session_state.last_result
        render_result_metrics(result)
        render_run_variation_metadata(result)

        with st.expander(tx("run_eval_section"), expanded=False):
            render_algorithm_evaluation(result.algorithm)

        if result.path_verified and result.path:
            solution_title = (
                tx("run_sol_path")
                if result.success and result.goal_reached
                else tx("run_recorded_trajectory")
            )
            with st.expander(solution_title, expanded=True):
                if not (result.success and result.goal_reached):
                    st.warning(tx("run_recorded_warning"))
                render_path_animation(
                    result.path,
                    result.actions,
                    key="solution_path",
                    reaches_goal=result.goal_reached,
                )

        if result.trace:
            st.caption(
                tx(
                    "run_evidence_guard",
                    trace=RUN_TRACE_ROWS,
                    detail=RUN_DETAIL_ROWS,
                    tree=RUN_TREE_NODES,
                )
            )
            st.subheader(tx("run_live_evidence_title"))
            st.caption(tx("run_live_evidence_desc"))
            render_search_detail_table(
                result.trace,
                max_rows=RUN_DETAIL_ROWS,
                key="run_detail_step_slider",
            )

            st.markdown("---")
            render_search_tree(result, max_nodes=RUN_TREE_NODES)

            with st.expander(tx("run_trace_steps"), expanded=True):
                st.caption(tx("trace_notation_help"))
                render_trace_table(result.trace, max_rows=RUN_TRACE_ROWS)
            with st.expander(tx("run_detail"), expanded=False):
                render_search_detail_table(
                    result.trace,
                    max_rows=RUN_DETAIL_ROWS,
                    key="run_expanded_detail_step_slider",
                )
