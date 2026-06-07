"""Algorithm comparison tab."""

import pandas as pd
import streamlit as st

from core.academic_proofs import BENCHMARK_PRESETS
from core.heuristics import HEURISTICS
from core.metrics import SearchResult
from core.puzzle import GOAL_STATE, is_solvable, scramble
from ui.academic_panels import (
    render_academic_header,
    render_benchmark_evidence,
    render_benchmark_methodology,
    render_decision_guide,
    render_exam_path,
    render_extension_warning,
    render_recommendation_rubric,
    render_taxonomy_table,
)
from ui.components import render_comparison_table
from ui.styles import ALGORITHM_FN_MAP, ALGORITHM_GROUPS, COMPARISON_TABLE, NOTES


def render_compare_tab() -> None:
    st.title("Compare Algorithms")
    render_academic_header(
        "Compare solver behavior and academic guarantees",
        "Benchmark results show runtime behavior; the taxonomy table separates standard 15-puzzle solvers from contrast cases and illustrative AI extensions.",
        "Algorithm comparison",
    )
    render_exam_path("Compare")
    render_extension_warning()

    preset_name = st.selectbox(
        "Benchmark preset",
        list(BENCHMARK_PRESETS.keys()),
        key="compare_benchmark_preset",
    )
    preset = BENCHMARK_PRESETS[preset_name]
    render_benchmark_methodology(preset_name)
    col_preset, col_preset_note = st.columns([1, 3])
    with col_preset:
        if st.button("Load preset state", key="btn_load_benchmark_preset"):
            st.session_state.start_state = scramble(
                depth=int(preset["depth"]),
                seed=int(preset["seed"]),
            )
            st.rerun()
    with col_preset_note:
        st.caption(
            "Preset loads a deterministic solvable state. You can still adjust algorithms, "
            "heuristic, node cap, and timeout before running."
        )

    st.markdown("Select algorithms to benchmark against the current start state.")

    selected_groups = st.multiselect(
        "Algorithm Groups", list(ALGORITHM_GROUPS.keys()),
        default=["Uninformed Search", "Informed Search"],
        key="compare_groups",
    )

    selected_algos = []
    for g in selected_groups:
        algos = st.multiselect(
            f"Algorithms from {g}",
            ALGORITHM_GROUPS[g],
            default=ALGORITHM_GROUPS[g][:2],
            key=f"compare_{g}",
        )
        selected_algos.extend(algos)

    heuristic_names = list(HEURISTICS.keys())
    heuristic_index = heuristic_names.index(preset["heuristic"]) if preset["heuristic"] in heuristic_names else 0
    heuristic = st.selectbox(
        "Heuristic for comparison",
        heuristic_names,
        index=heuristic_index,
        key=f"compare_heuristic_{preset_name}",
    )
    max_nodes = st.number_input(
        "Max Nodes",
        1000,
        500000,
        int(preset["max_nodes"]),
        key=f"compare_max_nodes_{preset_name}",
    )
    timeout = st.number_input(
        "Timeout (s)",
        5,
        300,
        int(preset["timeout"]),
        key=f"compare_timeout_{preset_name}",
    )

    if st.button("Run Benchmark", key="btn_benchmark", type="primary"):
        start = st.session_state.start_state
        if not is_solvable(start):
            st.error("Current state is NOT solvable.")
        else:
            import algorithms.uninformed as u
            import algorithms.informed as inf
            import algorithms.local_search as ls
            import algorithms.complex_env as ce
            import algorithms.csp as csp_mod
            import algorithms.adversarial as adv

            solver_map = {
                "bfs": lambda **kw: u.bfs(**kw, max_nodes=max_nodes),
                "dfs": lambda **kw: u.dfs(**kw, max_depth=30, max_nodes=max_nodes),
                "ucs": lambda **kw: u.ucs(**kw, max_nodes=max_nodes),
                "ids": lambda **kw: u.ids(**kw, max_depth=30, max_nodes=max_nodes),
                "greedy_best_first": lambda **kw: inf.greedy_best_first(**kw, max_nodes=max_nodes),
                "a_star": lambda **kw: inf.a_star(**kw, max_nodes=max_nodes),
                "ida_star": lambda **kw: inf.ida_star(**kw, max_nodes=max_nodes),
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
                "minimax": adv.minimax,
                "alpha_beta_pruning": adv.alpha_beta_pruning,
                "expectimax": adv.expectimax,
            }

            st.session_state.benchmark_results = []

            progress = st.progress(0, text="Running benchmark...")
            total = len(selected_algos)

            for i, algo in enumerate(selected_algos):
                fn_name = ALGORITHM_FN_MAP.get(algo)
                if fn_name and fn_name in solver_map:
                    try:
                        kwargs = dict(start=start, goal=GOAL_STATE,
                                     timeout=float(timeout), action_order="LRUD")
                        # Only pass heuristic to algorithms that use it
                        if fn_name not in ("bfs", "dfs", "ucs", "ids", "and_or_search",
                                          "no_observation_search", "partially_observable_search",
                                          "csp_definition", "constraint_propagation",
                                          "path_consistency", "global_constraints",
                                          "backtracking_search", "min_conflicts",
                                          "solve_csp_constraint_graphs",
                                          "minimax", "alpha_beta_pruning", "expectimax"):
                            pass  # heuristic handled per-algorithm below
                        if fn_name in ("simple_hill_climbing", "steepest_ascent_hill_climbing",
                                       "stochastic_hill_climbing", "local_beam_search",
                                       "simulated_annealing", "greedy_best_first", "a_star",
                                       "ida_star", "online_search_lrta",
                                       "minimax", "alpha_beta_pruning", "expectimax"):
                            kwargs["heuristic"] = heuristic
                        if fn_name in ("simple_hill_climbing", "steepest_ascent_hill_climbing",
                                       "stochastic_hill_climbing", "local_beam_search",
                                       "simulated_annealing"):
                            kwargs["max_iterations"] = 10000
                        elif fn_name == "random_restart_hill_climbing":
                            kwargs["max_iterations"] = 5000
                            kwargs["max_restarts"] = 20
                        elif fn_name in ("minimax", "alpha_beta_pruning", "expectimax"):
                            kwargs["depth"] = 3
                        result = solver_map[fn_name](**kwargs)
                        st.session_state.benchmark_results.append(result)
                    except Exception as e:
                        st.session_state.benchmark_results.append(
                            SearchResult(success=False, algorithm=algo, group="",
                                        message=f"Error: {e}", runtime=0))
                progress.progress((i + 1) / total, text=f"Done: {i+1}/{total}")

            progress.empty()

    render_comparison_table(st.session_state.benchmark_results)
    render_benchmark_evidence(st.session_state.benchmark_results)

    # Static comparison table
    st.markdown("---")
    st.subheader("Algorithm Properties Comparison")
    df = pd.DataFrame(COMPARISON_TABLE)
    st.dataframe(df, width="stretch", hide_index=True)
    st.caption(NOTES)
    render_taxonomy_table()
    render_recommendation_rubric()
    render_decision_guide()
