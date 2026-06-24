"""Single algorithm runner tab."""

import streamlit as st

from core.heuristics import HEURISTICS
from core.metrics import SearchResult
from core.puzzle import GOAL_STATE, is_solvable
from core.randomness import is_randomized_solver, resolve_run_seed
from core.solver_dispatch import build_solver_kwargs
from ui.academic_panels import render_academic_header, render_algorithm_role_card, render_exam_path
from ui.components import (
    render_algorithm_evaluation,
    render_path_animation,
    render_result_metrics,
    render_search_detail_table,
    render_search_tree,
    render_trace_table,
)
from ui.styles import ALGORITHM_FN_MAP, SOLVER_GROUPS


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
    st.title(tx("run_title"))
    render_academic_header(
        tx("run_hero_title"),
        tx("run_hero_desc"),
        tx("run_hero_kicker"),
    )
    render_exam_path("Run", t=t)

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

        if algo_name in ["UCS", "Greedy Best-First", "A*"]:
            tie_breaker = st.selectbox(
                tx("run_tie_breaker"),
                ["FIFO", "LIFO", "Min-g", "Max-g"],
                key="tie_breaker_select",
                help=tx("run_tie_breaker_help")
            )
        else:
            tie_breaker = "FIFO"

    with col_params:
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            max_nodes = st.number_input(tx("run_max_nodes"), 1000, 1000000, 50000, step=5000, key="max_nodes")
            max_depth = st.number_input(tx("run_max_depth"), 1, 100, 20, key="max_depth")
        with col_p2:
            timeout = st.number_input(tx("run_timeout"), 5, 600, 60, key="timeout_val")
            action_order = st.selectbox(tx("run_action_order"), ["LRUD", "UDLR", "RLDU", "DURL"], key="action_order")

        # Extra params for specific algorithms
        extra_params = {}
        fresh_seed_each_run = False
        manual_seed = 42
        if "Hill Climbing" in algo_name or "Beam" in algo_name:
            max_iter = st.number_input(tx("run_max_iter"), 100, 100000, 10000, key="max_iter")
            extra_params["max_iterations"] = max_iter
        if is_randomized_solver(selected_fn_name):
            fresh_seed_each_run = st.checkbox(
                tx("run_fresh_seed"),
                value=True,
                key="fresh_seed_each_run",
                help=(
                    tx("run_fresh_seed_help")
                ),
            )
            manual_seed = st.number_input(
                tx("run_fixed_seed"),
                0,
                2**31 - 1,
                42,
                key="seed_val",
                disabled=fresh_seed_each_run,
            )
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
        tuple(st.session_state.start_state), selected_fn_name, algo_name, heuristic,
        tie_breaker, action_order, int(max_nodes), int(max_depth), float(timeout),
        tuple(sorted(extra_params.items())), fresh_seed_each_run, int(manual_seed),
    )
    if st.session_state.get("last_run_signature") != run_signature:
        st.session_state.pop("last_result", None)

    if st.button(tx("run_btn"), key="btn_run", type="primary"):
        start = st.session_state.start_state
        if not is_solvable(start):
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
                    run_seed = resolve_run_seed(
                        fn_name,
                        fresh_each_run=fresh_seed_each_run,
                        manual_seed=int(manual_seed),
                        previous_seed=st.session_state.get("last_random_seed"),
                    )
                    if run_seed is not None:
                        extra_params["seed"] = run_seed
                    kwargs = build_solver_kwargs(
                        fn_name,
                        start=start,
                        goal=GOAL_STATE,
                        timeout=float(timeout),
                        action_order=action_order,
                        max_nodes=int(max_nodes),
                        max_depth=int(max_depth),
                        heuristic=heuristic,
                        tie_breaker=tie_breaker,
                        extra_params=extra_params,
                    )

                    with st.spinner(tx("run_spinner_running", algo=algo_name)):
                        try:
                            result = solver_fn(**kwargs)
                            result.random_seed = run_seed
                            if run_seed is not None:
                                st.session_state["last_random_seed"] = run_seed

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
        if result.random_seed is None:
            st.caption(tx("run_deterministic_caption"))
        else:
            st.caption(tx("run_random_seed_caption", seed=result.random_seed))
        render_algorithm_evaluation(result.algorithm)

        if result.path_verified and result.path:
            if result.success and result.goal_reached:
                st.subheader(tx("run_sol_path"))
            else:
                st.subheader(tx("run_recorded_trajectory"))
                st.warning(tx("run_recorded_warning"))
            render_path_animation(
                result.path,
                result.actions,
                key="solution_path",
                reaches_goal=result.goal_reached,
            )

        if result.trace:
            st.subheader(tx("run_trace_steps"))
            render_trace_table(result.trace)
            st.subheader(tx("run_detail"))
            render_search_detail_table(result.trace)
            st.subheader(tx("run_search_tree"))
            render_search_tree(result)
