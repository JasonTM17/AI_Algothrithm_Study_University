"""Algorithm comparison tab."""

import pandas as pd
import streamlit as st

from core.academic_proofs import BENCHMARK_PRESETS
from core.heuristics import HEURISTICS
from core.metrics import SearchResult
from core.puzzle import GOAL_STATE, is_solvable, scramble
from core.randomness import resolve_run_seed
from ui.action_states import render_action_state
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
from ui.components import render_comparison_table, render_start_goal_contract
from ui.components import render_puzzle_board
from ui.image_algorithm_race import render_image_algorithm_race
from ui.path_solver_runner import (
    PATH_ALGORITHM_BY_NAME,
    PATH_ALGORITHM_SPECS,
    PathRunSettings,
    run_path_algorithm,
)
from ui.start_goal_controls import apply_goal_state, apply_start_state
from ui.styles import ALGORITHM_FN_MAP, ALGORITHM_GROUPS, COMPARISON_TABLE, NOTES


BENCHMARK_GROUPS = tuple(ALGORITHM_GROUPS)
COMPARE_MAX_NODES_MIN = 1000
COMPARE_MAX_NODES_CAP = 20000
COMPARE_TIMEOUT_MIN = 5
COMPARE_TIMEOUT_CAP = 120
PATH_BENCHMARK_ALGORITHMS = tuple(spec.name for spec in PATH_ALGORITHM_SPECS)


def _preset_state_pair(preset: dict) -> tuple[tuple[int, ...], tuple[int, ...]]:
    preset_goal = tuple(preset.get("goal_state", GOAL_STATE))
    preset_start = tuple(
        preset.get("start_state")
        or scramble(
            goal=preset_goal,
            depth=int(preset["depth"]),
            seed=int(preset["seed"]),
        )
    )
    return preset_start, preset_goal


def _sync_default_selection_for_preset(preset_name: str, preset: dict) -> None:
    """Reset benchmark selections only when the user picks a different preset."""
    if (
        st.session_state.get("compare_selection_preset") == preset_name
        and "compare_groups" in st.session_state
    ):
        return

    recommended_groups = list(preset.get("recommended_groups", BENCHMARK_GROUPS))
    recommended_algorithms = tuple(preset.get("recommended_algorithms", ()))
    st.session_state["compare_groups"] = recommended_groups
    for group in BENCHMARK_GROUPS:
        st.session_state[f"compare_{group}"] = [
            algorithm
            for algorithm in recommended_algorithms
            if algorithm in ALGORITHM_GROUPS[group]
        ]
    st.session_state["compare_selection_preset"] = preset_name


def _select_all_path_benchmark_algorithms() -> None:
    """Select every algorithm that can produce a comparable linear trajectory."""
    selected_groups: list[str] = []
    for group, algorithms in ALGORITHM_GROUPS.items():
        selected = [name for name in algorithms if name in PATH_BENCHMARK_ALGORITHMS]
        st.session_state[f"compare_{group}"] = selected
        if selected:
            selected_groups.append(group)
    st.session_state["compare_groups"] = selected_groups


def _render_preset_start_goal_preview(t, preset: dict) -> None:
    preset_start, preset_goal = _preset_state_pair(preset)
    recommended = ", ".join(preset.get("recommended_algorithms", ())) or "-"

    preview_cols = st.columns([1, 1, 2])
    with preview_cols[0]:
        st.caption(t("compare_preset_start"))
        render_puzzle_board(preset_start, size="mini", goal=preset_goal)
    with preview_cols[1]:
        st.caption(t("compare_preset_goal"))
        render_puzzle_board(
            preset_goal,
            highlight_correct=False,
            size="mini",
            goal=preset_goal,
        )
    with preview_cols[2]:
        st.caption(
            t(
                "compare_preset_goal_desc",
                purpose=preset.get("comparison_goal", "-"),
            )
        )
        st.caption(t("compare_preset_algorithms", algorithms=recommended))
        st.caption(
            t(
                "compare_preset_expected",
                expected=preset.get("expected_outcome", "-"),
            )
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
    render_extension_warning(t=t)
    render_start_goal_contract(
        st.session_state.start_state,
        goal,
        is_solvable(st.session_state.start_state, goal),
    )

    preset_name = st.selectbox(
        tx("compare_preset"),
        list(BENCHMARK_PRESETS.keys()),
        key="compare_benchmark_preset",
    )
    preset = BENCHMARK_PRESETS[preset_name]
    _sync_default_selection_for_preset(preset_name, preset)
    preset_action_order = str(preset.get("action_order", "LRUD"))
    render_benchmark_methodology(preset_name)
    col_preset, col_preset_note = st.columns([1, 3])
    with col_preset:
        if st.button(tx("compare_load_preset_state"), key="btn_load_benchmark_preset"):
            preset_start, preset_goal = _preset_state_pair(preset)
            apply_goal_state(preset_goal)
            apply_start_state(preset_start)
            st.rerun()
    with col_preset_note:
        st.caption(
            tx("compare_preset_caption")
        )
    _render_preset_start_goal_preview(tx, preset)

    st.markdown(tx("compare_select_algorithms_desc"))
    st.caption(
        tx("compare_standard_rankings_caption")
    )
    st.button(
        tx("compare_select_all_path_algorithms"),
        key="compare_select_all_path_algorithms",
        on_click=_select_all_path_benchmark_algorithms,
        width="stretch",
    )

    selected_groups = st.multiselect(
        tx("compare_groups"), list(BENCHMARK_GROUPS),
        key="compare_groups",
    )

    selected_algos = []
    for g in selected_groups:
        algos = st.multiselect(
            tx("compare_algorithms_from", group=g),
            ALGORITHM_GROUPS[g],
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
        COMPARE_MAX_NODES_MIN,
        COMPARE_MAX_NODES_CAP,
        int(preset["max_nodes"]),
        key=f"compare_max_nodes_{preset_name}",
    )
    timeout = st.number_input(
        tx("compare_timeout"),
        COMPARE_TIMEOUT_MIN,
        COMPARE_TIMEOUT_CAP,
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
        if not selected_algos:
            st.warning(tx("compare_no_algorithms_selected"))
        elif not is_solvable(start, goal):
            st.error(tx("run_error_unsolvable"))
        else:
            st.session_state.benchmark_results = []
            st.session_state["image_race_version"] = int(
                st.session_state.get("image_race_version", 0)
            ) + 1

            progress = st.progress(0, text=tx("compare_running"))
            total = len(selected_algos)
            previous_seed = st.session_state.get("last_benchmark_random_seed")
            benchmark_seeds: dict[str, int] = {}

            for i, algo in enumerate(selected_algos):
                fn_name = ALGORITHM_FN_MAP.get(algo)
                if fn_name and algo in PATH_ALGORITHM_BY_NAME:
                    try:
                        run_seed = resolve_run_seed(
                            fn_name,
                            fresh_each_run=fresh_benchmark_seeds,
                            manual_seed=int(fixed_benchmark_seed),
                            previous_seed=previous_seed,
                        )
                        if run_seed is not None:
                            benchmark_seeds[algo] = run_seed
                            previous_seed = run_seed
                        result = run_path_algorithm(
                            algo,
                            start=start,
                            goal=goal,
                            settings=PathRunSettings(
                                timeout=float(timeout),
                                max_nodes=int(max_nodes),
                                max_depth=30,
                                heuristic=heuristic,
                                action_order=preset_action_order,
                                tie_breaker="FIFO",
                                seed=int(run_seed if run_seed is not None else fixed_benchmark_seed),
                            ),
                        )
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
                            goal_state=goal,
                            termination_reason="not_applicable",
                        )
                    )
                progress.progress((i + 1) / total, text=tx("compare_done", curr=i + 1, total=total))

            st.session_state["last_benchmark_random_seed"] = previous_seed
            st.session_state["benchmark_run_seeds"] = benchmark_seeds
            st.session_state["last_benchmark_signature"] = benchmark_signature
            progress.empty()

    if st.session_state.benchmark_results:
        render_comparison_table(st.session_state.benchmark_results)
        render_image_algorithm_race(
            st.session_state.benchmark_results,
            st.session_state.get("image_tiles", {}),
            tx,
        )
        render_benchmark_evidence(st.session_state.benchmark_results)
    else:
        render_action_state(
            title=tx("compare_empty_title"),
            body=tx("compare_empty_body"),
            bullets=[tx("compare_empty_bullet_setup"), tx("compare_empty_bullet_scope")],
            kicker=tx("action_state_kicker"),
        )
    benchmark_seeds = st.session_state.get("benchmark_run_seeds", {})
    if benchmark_seeds:
        seed_text = " | ".join(f"{name}: `{seed}`" for name, seed in benchmark_seeds.items())
        st.caption(tx("compare_recorded_seeds", seeds=seed_text))

    # Static comparison table
    st.markdown("---")
    st.subheader(tx("compare_prop"))
    df = pd.DataFrame(COMPARISON_TABLE)
    st.dataframe(df, width="stretch", hide_index=True)
    st.caption(NOTES)
    render_taxonomy_table()
    render_recommendation_rubric()
    render_decision_guide()
