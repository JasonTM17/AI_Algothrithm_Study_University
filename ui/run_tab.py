"""Single algorithm runner tab."""

import streamlit as st

from core.heuristics import HEURISTICS
from core.metrics import SearchResult
from core.puzzle import GOAL_STATE, is_solvable
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


def render_run_algorithm_tab() -> None:
    st.title("Run Algorithm")
    render_academic_header(
        "Run one algorithm with academic context",
        "Inspect guarantees, environment assumptions, trace data, and why the selected method is or is not a natural 15-puzzle solver.",
        "Single algorithm analysis",
    )
    render_exam_path("Run")

    col_algo, col_params = st.columns([1, 1])

    with col_algo:
        group = st.selectbox("Algorithm Group", list(SOLVER_GROUPS.keys()), key="algo_group")
        algorithms = SOLVER_GROUPS[group]
        algo_name = st.selectbox("Algorithm", algorithms, key="algo_name")
        render_algorithm_role_card(algo_name)

        # Only show heuristic for algorithms that use it
        heuristic_options = list(HEURISTICS.keys())
        uninformed_algos = ["BFS", "DFS", "UCS", "IDS"]
        if algo_name not in uninformed_algos:
            heuristic = st.selectbox("Heuristic", heuristic_options, key="heuristic_select")
        else:
            heuristic = "Manhattan Distance"  # default, won't be used

        if algo_name in ["UCS", "Greedy Best-First", "A*"]:
            tie_breaker = st.selectbox(
                "Tie-Breaking Rule",
                ["FIFO", "LIFO", "Min-g", "Max-g"],
                key="tie_breaker_select",
                help="Rule for selecting among equal-priority nodes. Use it when explaining hand-tracing results."
            )
        else:
            tie_breaker = "FIFO"

    with col_params:
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            max_nodes = st.number_input("Max Nodes", 1000, 1000000, 50000, step=5000, key="max_nodes")
            max_depth = st.number_input("Max Depth / Game Tree Depth", 1, 100, 20, key="max_depth")
        with col_p2:
            timeout = st.number_input("Timeout (seconds)", 5, 600, 60, key="timeout_val")
            action_order = st.selectbox("Action Order", ["LRUD", "UDLR", "RLDU", "DURL"], key="action_order")

        # Extra params for specific algorithms
        extra_params = {}
        if "Hill Climbing" in algo_name or "Beam" in algo_name:
            max_iter = st.number_input("Max Iterations", 100, 100000, 10000, key="max_iter")
            extra_params["max_iterations"] = max_iter
        if algo_name in ["Stochastic Hill Climbing", "Random-Restart Hill Climbing", "Simulated Annealing"]:
            seed_val = st.number_input("Random Seed", 0, 99999, 42, key="seed_val")
            extra_params["seed"] = seed_val if seed_val > 0 else None
        if algo_name == "Random-Restart Hill Climbing":
            extra_params["max_restarts"] = st.number_input("Max Restarts", 1, 100, 20, key="max_restarts")
        if algo_name == "Local Beam Search":
            extra_params["beam_width"] = st.number_input("Beam Width", 2, 20, 3, key="beam_width")
        if algo_name == "Simulated Annealing":
            extra_params["initial_temp"] = st.number_input("Initial Temp", 1.0, 1000.0, 100.0, key="init_temp")
            extra_params["cooling_rate"] = st.number_input("Cooling Rate", 0.9, 0.9999, 0.9995, key="cooling_rate", format="%0.4f")
            extra_params["min_temp"] = st.number_input("Min Temp", 0.001, 1.0, 0.01, key="min_temp", format="%0.3f")
        if algo_name == "Minimax" or algo_name == "Alpha-Beta Pruning":
            extra_params["depth"] = max_depth
        if algo_name == "Expectimax":
            extra_params["depth"] = max_depth
            extra_params["success_prob"] = st.slider("Success Probability", 0.1, 1.0, 0.8, key="success_prob")

    run_signature = (tuple(st.session_state.start_state), algo_name, heuristic, tie_breaker, action_order)
    if st.session_state.get("last_run_signature") != run_signature:
        st.session_state.pop("last_result", None)

    if st.button("Run", key="btn_run", type="primary"):
        start = st.session_state.start_state
        if not is_solvable(start):
            st.error("Current state is NOT solvable. Please generate a solvable state.")
        else:
            fn_name = ALGORITHM_FN_MAP.get(algo_name)
            if fn_name is None:
                st.error(f"Algorithm {algo_name} not found.")
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
                    st.error(f"Solver function {fn_name} not found.")
                else:
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

                    with st.spinner(f"Running {algo_name}..."):
                        try:
                            result = solver_fn(**kwargs)

                            st.session_state["last_result"] = result
                            st.session_state["last_run_signature"] = run_signature
                            st.session_state.benchmark_results.append(result)

                            if result.success:
                                st.success(f"{algo_name} found a solution!")
                            else:
                                st.warning(f"{algo_name}: {result.message}")
                        except Exception as e:
                            st.error(f"Error running {algo_name}: {e}")

    # Show last result
    if "last_result" in st.session_state and st.session_state.last_result:
        result = st.session_state.last_result
        render_result_metrics(result)
        render_algorithm_evaluation(result.algorithm)

        if result.success and result.path:
            st.subheader("Solution Path")
            render_path_animation(result.path, result.actions, key="solution_path")

        if result.trace:
            st.subheader("Trace Steps")
            render_trace_table(result.trace)
            st.subheader("Node / Frontier / Reached Detail")
            render_search_detail_table(result.trace)
            st.subheader("Search Tree")
            render_search_tree(result)

