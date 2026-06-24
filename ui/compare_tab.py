"""Algorithm comparison tab."""

import pandas as pd
import streamlit as st

from core.academic_proofs import BENCHMARK_PRESETS
from core.heuristics import HEURISTICS
from core.metrics import SearchResult
from core.puzzle import GOAL_STATE, is_solvable, scramble
from core.randomness import resolve_run_seed
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
from ui.styles import ALGORITHM_FN_MAP, SOLVER_GROUPS, COMPARISON_TABLE, NOTES


BENCHMARK_GROUPS = (
    "Uninformed Search",
    "Informed Search",
    "Local Search",
)


def render_compare_tab(t=None) -> None:
    tx = t or (lambda key, **kwargs: key.format(**kwargs) if kwargs else key)
    goal = st.session_state.get("goal_state", GOAL_STATE)
    st.title(tx("compare_title"))
    render_academic_header(
        tx("compare_hero_title"),
        tx("compare_hero_desc"),
        tx("compare_hero_kicker"),
    )
    render_exam_path("Compare", t=t)
    render_extension_warning()

    preset_name = st.selectbox(
        tx("compare_preset"),
        list(BENCHMARK_PRESETS.keys()),
        key="compare_benchmark_preset",
    )
    preset = BENCHMARK_PRESETS[preset_name]
    render_benchmark_methodology(preset_name)
    col_preset, col_preset_note = st.columns([1, 3])
    with col_preset:
        if st.button(tx("compare_load_preset_state"), key="btn_load_benchmark_preset"):
            st.session_state.start_state = scramble(
                goal=goal,
                depth=int(preset["depth"]),
                seed=int(preset["seed"]),
            )
            st.rerun()
    with col_preset_note:
        st.caption(
            tx("compare_preset_caption")
        )

    st.markdown(tx("compare_select_algorithms_desc"))
    st.caption(
        tx("compare_standard_rankings_caption")
    )

    selected_groups = st.multiselect(
        tx("compare_groups"), list(BENCHMARK_GROUPS),
        default=["Uninformed Search", "Informed Search"],
        key="compare_groups",
    )

    selected_algos = []
    for g in selected_groups:
        algos = st.multiselect(
            tx("compare_algorithms_from", group=g),
            SOLVER_GROUPS[g],
            default=SOLVER_GROUPS[g][:2],
            key=f"compare_{g}",
        )
        selected_algos.extend(algos)

    heuristic_names = list(HEURISTICS.keys())
    heuristic_index = heuristic_names.index(preset["heuristic"]) if preset["heuristic"] in heuristic_names else 0
    heuristic = st.selectbox(
        tx("compare_heuristic"),
        heuristic_names,
        index=heuristic_index,
        key=f"compare_heuristic_{preset_name}",
    )
    max_nodes = st.number_input(
        tx("run_max_nodes"),
        1000,
        500000,
        int(preset["max_nodes"]),
        key=f"compare_max_nodes_{preset_name}",
    )
    timeout = st.number_input(
        tx("compare_timeout"),
        5,
        300,
        int(preset["timeout"]),
        key=f"compare_timeout_{preset_name}",
    )
    fresh_benchmark_seeds = st.checkbox(
        tx("compare_fresh_seeds"),
        value=True,
        key="fresh_benchmark_seeds",
        help=(
            tx("compare_fresh_seeds_help")
        ),
    )
    fixed_benchmark_seed = st.number_input(
        tx("compare_fixed_seed"),
        0,
        2**31 - 1,
        int(preset["seed"]),
        key=f"fixed_benchmark_seed_{preset_name}",
        disabled=fresh_benchmark_seeds,
    )

    benchmark_signature = (
        tuple(st.session_state.start_state),
        tuple(goal),
        preset_name,
        tuple(selected_groups),
        tuple(selected_algos),
        heuristic,
        int(max_nodes),
        int(timeout),
        fresh_benchmark_seeds,
        int(fixed_benchmark_seed),
    )
    if (
        "last_benchmark_signature" in st.session_state
        and st.session_state.last_benchmark_signature != benchmark_signature
    ):
        st.session_state.benchmark_results = []
        st.session_state["benchmark_run_seeds"] = {}

    if st.button(tx("compare_run_btn"), key="btn_benchmark", type="primary"):
        start = st.session_state.start_state
        if not is_solvable(start, goal):
            st.error(tx("run_error_unsolvable"))
        else:
            import algorithms.uninformed as u
            import algorithms.informed as inf
            import algorithms.local_search as ls

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
            }

            st.session_state.benchmark_results = []

            progress = st.progress(0, text=tx("compare_running"))
            total = len(selected_algos)
            previous_seed = st.session_state.get("last_benchmark_random_seed")
            benchmark_seeds: dict[str, int] = {}

            for i, algo in enumerate(selected_algos):
                fn_name = ALGORITHM_FN_MAP.get(algo)
                if fn_name and fn_name in solver_map:
                    try:
                        run_seed = resolve_run_seed(
                            fn_name,
                            fresh_each_run=fresh_benchmark_seeds,
                            manual_seed=int(fixed_benchmark_seed),
                            previous_seed=previous_seed,
                        )
                        kwargs = dict(start=start, goal=goal,
                                     timeout=float(timeout), action_order="LRUD")
                        if run_seed is not None:
                            kwargs["seed"] = run_seed
                            benchmark_seeds[algo] = run_seed
                            previous_seed = run_seed
                        if fn_name in ("simple_hill_climbing", "steepest_ascent_hill_climbing",
                                       "stochastic_hill_climbing", "random_restart_hill_climbing",
                                       "local_beam_search",
                                       "simulated_annealing", "greedy_best_first", "a_star",
                                       "ida_star"):
                            kwargs["heuristic"] = heuristic
                        if fn_name in ("simple_hill_climbing", "steepest_ascent_hill_climbing",
                                       "stochastic_hill_climbing", "local_beam_search",
                                       "simulated_annealing"):
                            kwargs["max_iterations"] = 10000
                        elif fn_name == "random_restart_hill_climbing":
                            kwargs["max_iterations"] = 5000
                            kwargs["max_restarts"] = 20
                        result = solver_map[fn_name](**kwargs)
                        result.random_seed = run_seed
                        st.session_state.benchmark_results.append(result)
                    except Exception as e:
                        st.session_state.benchmark_results.append(
                            SearchResult(success=False, algorithm=algo, group="",
                                        message=f"Error: {e}", runtime=0))
                else:
                    st.session_state.benchmark_results.append(
                        SearchResult(
                            success=False,
                            algorithm=algo,
                            group="",
                            message="Algorithm is not eligible for the standard benchmark.",
                        )
                    )
                progress.progress((i + 1) / total, text=tx("compare_done", curr=i + 1, total=total))

            st.session_state["last_benchmark_random_seed"] = previous_seed
            st.session_state["benchmark_run_seeds"] = benchmark_seeds
            st.session_state["last_benchmark_signature"] = benchmark_signature
            progress.empty()

    render_comparison_table(st.session_state.benchmark_results)
    render_benchmark_evidence(st.session_state.benchmark_results)
    benchmark_seeds = st.session_state.get("benchmark_run_seeds", {})
    if benchmark_seeds:
        seed_text = " · ".join(f"{name}: `{seed}`" for name, seed in benchmark_seeds.items())
        st.caption(f"Recorded stochastic seeds — {seed_text}")

    # Static comparison table
    st.markdown("---")
    st.subheader(tx("compare_prop"))
    df = pd.DataFrame(COMPARISON_TABLE)
    st.dataframe(df, width="stretch", hide_index=True)
    st.caption(NOTES)
    render_taxonomy_table()
    render_recommendation_rubric()
    render_decision_guide()
