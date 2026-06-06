"""15-Puzzle AI â€” Streamlit application for comparing search algorithms."""

import streamlit as st
import time
import pandas as pd
from core.puzzle import PuzzleState, GOAL_STATE, is_solvable, scramble, parse_state, validate_path
from core.heuristics import HEURISTICS, HEURISTIC_DESCRIPTIONS
from core.metrics import SearchResult
from algorithms.uninformed import bfs, dfs, ucs, ids
from algorithms.informed import greedy_best_first, a_star, ida_star
from algorithms.local_search import (
    simple_hill_climbing, steepest_ascent_hill_climbing,
    stochastic_hill_climbing, random_restart_hill_climbing,
    local_beam_search, simulated_annealing,
)
from algorithms.complex_env import and_or_search, no_observation_search, partially_observable_search, online_search_lrta
from algorithms.csp import (
    csp_definition, constraint_propagation, path_consistency,
    global_constraints, backtracking_search, min_conflicts, solve_csp_constraint_graphs,
)
from algorithms.adversarial import minimax, alpha_beta_pruning, expectimax
from core.theory import THEORY
from ui.styles import ALGORITHM_GROUPS, ALGORITHM_FN_MAP, THEORY_KEY_MAP, COMPARISON_TABLE, NOTES
from ui.components import (
    render_styles, render_puzzle_board, render_result_metrics,
    render_trace_table, render_path_animation, render_comparison_table,
    render_algorithm_info, render_search_detail_table, render_search_tree,
    process_uploaded_image, render_clickable_board, render_image_board,
)
from ui.sample_images import SAMPLE_IMAGES, generate_sample_tiles

st.set_page_config(
    page_title="15-Puzzle AI",
    page_icon="🧩",
    layout="wide",
    initial_sidebar_state="expanded",
)

render_styles()


def _move(state: tuple, action: str) -> tuple | None:
    """Move blank tile for interactive play."""
    from core.puzzle import _move_blank
    return _move_blank(state, action)


def _handle_play_slide(direction: str):
    """Callback for click-to-slide in Play tab."""
    ns = _move(st.session_state.play_state, direction)
    if ns:
        st.session_state.play_state = ns
        st.session_state.play_moves += 1


# â”€â”€ Initialize session state â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
if "start_state" not in st.session_state:
    st.session_state.start_state = scramble(depth=10, seed=42)
if "benchmark_results" not in st.session_state:
    st.session_state.benchmark_results = []
if "image_tiles" not in st.session_state:
    st.session_state.image_tiles = {}

# â”€â”€ Sidebar â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
st.sidebar.title("15-Puzzle AI")
st.sidebar.markdown("---")

tab = st.sidebar.radio(
    "Navigation",
    ["Play", "Run Algorithm", "Step Trace",
     "Compare", "Theory", "Advanced"],
    key="main_tab"
)

st.sidebar.markdown("---")
st.sidebar.subheader("Start State")

state_input_method = st.sidebar.radio("Input method", ["Random (Scramble)", "Manual Input"], key="input_method")

if state_input_method == "Random (Scramble)":
    col_s1, col_s2 = st.sidebar.columns(2)
    with col_s1:
        scramble_depth = st.number_input("Scramble Depth", 1, 50, 10, key="scramble_depth")
    with col_s2:
        scramble_seed = st.number_input("Seed", 0, 99999, 42, key="scramble_seed")

    if st.sidebar.button("Generate Random", key="btn_random"):
        st.session_state.start_state = scramble(depth=scramble_depth, seed=scramble_seed)

elif state_input_method == "Manual Input":
    manual_input = st.sidebar.text_area(
        "Enter 16 numbers (0=blank, space-separated)",
        value=" ".join(str(x) for x in st.session_state.start_state),
        key="manual_input",
        height=80,
    )
    if st.sidebar.button("Parse Input", key="btn_parse"):
        try:
            st.session_state.start_state = parse_state(manual_input)
            st.sidebar.success("State parsed!")
        except ValueError as e:
            st.sidebar.error(f"Invalid input: {e}")

if st.sidebar.button("Reset to Goal", key="btn_reset"):
    st.session_state.start_state = GOAL_STATE

solvable = is_solvable(st.session_state.start_state)
if solvable:
    st.sidebar.success("Solvable")
else:
    st.sidebar.error("Not solvable! Swap two tiles to make solvable.")

# Auto-load default sample image on first run only
if "image_active" not in st.session_state:
    st.session_state.image_active = True
if st.session_state.image_active and not st.session_state.get("image_tiles"):
    default_img = list(SAMPLE_IMAGES.keys())[0]
    st.session_state.image_tiles = generate_sample_tiles(default_img)

st.sidebar.markdown("---")
st.sidebar.subheader("Sample Image")
sample_choice = st.sidebar.selectbox(
    "Built-in images",
    list(SAMPLE_IMAGES.keys()),
    key="sample_select",
    index=0,
)
if st.sidebar.button("Load Sample Image", key="btn_load_sample"):
    st.session_state.image_tiles = generate_sample_tiles(sample_choice)
    st.session_state.image_active = True

if "show_numbers" not in st.session_state:
    st.session_state.show_numbers = True
st.session_state.show_numbers = st.sidebar.checkbox(
    "Hiển thị số trên ảnh (Helper)",
    value=st.session_state.show_numbers,
    key="show_numbers_checkbox"
)

st.sidebar.markdown("---")
st.sidebar.subheader("Current Start State")
render_puzzle_board(st.session_state.start_state, highlight_correct=True)

# â”€â”€ Tab 1: Play / Board â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
if tab == "Play":
    st.title("15-Puzzle | Interactive Board")

    col1, col2 = st.columns([1, 1])
    with col1:
        st.subheader("Start State")
        render_puzzle_board(st.session_state.start_state)
        h = HEURISTICS["Manhattan Distance"](st.session_state.start_state)
        st.metric("Manhattan Distance", h)
        st.metric("Is Solvable", "Yes" if solvable else "No")

    with col2:
        st.subheader("Goal State")
        render_puzzle_board(GOAL_STATE, highlight_correct=False)
        st.metric("Manhattan Distance", 0)

    st.markdown("---")

    # Image import section
    st.subheader("Custom Image")
    st.markdown("Upload an image to use as puzzle tiles. The image will be split into 15 pieces.")
    uploaded_img = st.file_uploader("Upload puzzle image", type=["png", "jpg", "jpeg", "webp"], key="puzzle_img")
    if uploaded_img:
        tiles = process_uploaded_image(uploaded_img)
        if tiles:
            st.session_state.image_tiles = tiles
            st.session_state.image_active = True
            st.success(f"Image loaded! {len(tiles)} tile pieces created.")
        else:
            st.error("Failed to process image. Make sure it's a valid image file.")
    if st.button("Remove Image", key="remove_img"):
        st.session_state.image_tiles = {}
        st.session_state.image_active = False

    st.markdown("---")
    st.subheader("Manual Play")
    st.markdown("Click any tile adjacent to the blank space to slide it.")

    if "play_state" not in st.session_state:
        st.session_state.play_state = st.session_state.start_state
        st.session_state.play_moves = 0

    if "play_start_ref" not in st.session_state:
        st.session_state.play_start_ref = st.session_state.start_state
    if st.session_state.play_start_ref != st.session_state.start_state:
        st.session_state.play_state = st.session_state.start_state
        st.session_state.play_moves = 0
        st.session_state.play_start_ref = st.session_state.start_state

    has_image = "image_tiles" in st.session_state and st.session_state.image_tiles
    if has_image:
        col_board, col_preview = st.columns([5, 3])
        with col_board:
            render_image_board(
                st.session_state.play_state,
                st.session_state.image_tiles,
                key_prefix="play",
                highlight_correct=True,
                on_click_fn=_handle_play_slide,
                show_numbers=st.session_state.get("show_numbers", True),
            )
        with col_preview:
            st.markdown('<div style="text-align: center; font-weight: bold; margin-bottom: 8px;">Target Preview (Ảnh Gốc)</div>', unsafe_allow_html=True)
            preview_img = None
            if "sample_select" in st.session_state:
                choice = st.session_state.sample_select
                if "Cyberpunk" in choice:
                    preview_img = "ui/assets/cyberpunk_city.png"
                elif "Cosmic" in choice:
                    preview_img = "ui/assets/cosmic_cat.png"
                elif "Floating" in choice:
                    preview_img = "ui/assets/magic_castle.png"
            
            if preview_img:
                import os
                if os.path.exists(preview_img):
                    st.image(preview_img, use_container_width=True)
                else:
                    st.caption("Preview not found on disk.")
            elif uploaded_img:
                st.image(uploaded_img, use_container_width=True)
            else:
                st.info("Gradient/Mandala preview is not available.")
    else:
        render_clickable_board(
            st.session_state.play_state,
            key_prefix="play",
            highlight_correct=True,
            on_click_fn=_handle_play_slide,
        )

    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        st.metric("Moves", st.session_state.play_moves)
    with col_m2:
        h_play = HEURISTICS["Manhattan Distance"](st.session_state.play_state)
        st.metric("Manhattan Dist", h_play)
    with col_m3:
        correct = sum(1 for i, v in enumerate(st.session_state.play_state) if v == GOAL_STATE[i] and v != 0)
        st.metric("Tiles Correct", f"{correct}/15")

    if st.session_state.play_state == GOAL_STATE:
        st.balloons()
        st.success(f"You solved it in {st.session_state.play_moves} moves!")
    if st.button("Reset Play Board"):
        st.session_state.play_state = st.session_state.start_state
        st.session_state.play_moves = 0


# â”€â”€ Tab 2: Run Algorithm â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
elif tab == "Run Algorithm":
    st.title("Run Algorithm")

    col_algo, col_params = st.columns([1, 1])

    with col_algo:
        group = st.selectbox("Algorithm Group", list(ALGORITHM_GROUPS.keys()), key="algo_group")
        algorithms = ALGORITHM_GROUPS[group]
        algo_name = st.selectbox("Algorithm", algorithms, key="algo_name")

        # Only show heuristic for algorithms that use it
        heuristic_options = list(HEURISTICS.keys())
        uninformed_algos = ["BFS", "DFS", "UCS", "IDS"]
        if algo_name not in uninformed_algos:
            heuristic = st.selectbox("Heuristic", heuristic_options, key="heuristic_select")
        else:
            heuristic = "Manhattan Distance"  # default, won't be used

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
                    # Build kwargs based on algorithm
                    kwargs = dict(
                        start=start, goal=GOAL_STATE,
                        timeout=float(timeout),
                        action_order=action_order,
                    )

                    # Add algorithm-specific params
                    if fn_name in ("bfs", "ucs"):
                        kwargs["max_nodes"] = max_nodes
                    elif fn_name in ("dfs", "ids"):
                        kwargs["max_nodes"] = max_nodes
                        kwargs["max_depth"] = max_depth
                    elif fn_name in ("greedy_best_first", "a_star", "ida_star"):
                        kwargs["max_nodes"] = max_nodes
                        kwargs["heuristic"] = heuristic
                    elif fn_name in ("and_or_search",):
                        kwargs["max_depth"] = max_depth
                    elif fn_name in ("no_observation_search", "partially_observable_search"):
                        kwargs["max_steps"] = max_depth
                    elif fn_name == "online_search_lrta":
                        kwargs["max_steps"] = max_nodes
                        kwargs["heuristic"] = heuristic
                    elif fn_name == "backtracking_search":
                        kwargs["max_steps"] = max_nodes
                    elif fn_name in ("simple_hill_climbing", "steepest_ascent_hill_climbing",
                                    "stochastic_hill_climbing", "random_restart_hill_climbing",
                                    "local_beam_search", "simulated_annealing"):
                        kwargs["heuristic"] = heuristic
                    elif fn_name in ("minimax", "alpha_beta_pruning", "expectimax"):
                        kwargs["heuristic"] = heuristic

                    kwargs.update(extra_params)

                    with st.spinner(f"Running {algo_name}..."):
                        try:
                            result = solver_fn(**kwargs)

                            st.session_state["last_result"] = result
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

        if result.success and result.path:
            st.subheader("Solution Path")
            render_path_animation(result.path, result.actions, key="solution_path")

        if result.trace:
            st.subheader("Trace Steps")
            render_trace_table(result.trace)
            st.subheader("Node / Frontier / Reached Detail")
            render_search_detail_table(result.trace)
            st.subheader("Search Tree")
            render_search_tree(result.trace)


# â”€â”€ Tab 3: Step Trace â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
elif tab == "Step Trace":
    st.title("Step-by-Step Trace")

    if "last_result" not in st.session_state or not st.session_state.last_result:
        st.info("Run an algorithm first to see the trace.")
    else:
        result = st.session_state.last_result
        st.subheader(f"Trace: {result.algorithm}")

        if result.trace:
            render_trace_table(result.trace, max_rows=200)

            st.markdown("---")
            st.subheader("Node / Frontier / Reached Detail")
            render_search_detail_table(result.trace, max_rows=50)

            st.markdown("---")
            st.subheader("Search Tree")
            render_search_tree(result.trace, max_nodes=30)

            if st.button("Export Trace as CSV"):
                import io
                rows = []
                for step in result.trace:
                    row = {"Step": step.step, "Action": step.action or ""}
                    if step.g > 0:
                        row["g(n)"] = step.g
                    if step.h > 0:
                        row["h(n)"] = f"{step.h:.1f}"
                    if step.f > 0:
                        row["f(n)"] = f"{step.f:.1f}"
                    if step.frontier_size > 0:
                        row["Frontier"] = step.frontier_size
                    if step.reached_size > 0:
                        row["Reached"] = step.reached_size
                    if step.reason:
                        row["Reason"] = step.reason
                    rows.append(row)

                df = pd.DataFrame(rows)
                csv = df.to_csv(index=False).encode("utf-8")
                st.download_button("Download CSV", csv, f"trace_{result.algorithm}.csv", "text/csv")
        else:
            st.info("No trace data available for this algorithm.")


# â”€â”€ Tab 4: Compare Algorithms â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
elif tab == "Compare":
    st.title("Compare Algorithms")

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

    heuristic = st.selectbox("Heuristic for comparison", list(HEURISTICS.keys()), key="compare_heuristic")
    max_nodes = st.number_input("Max Nodes", 1000, 500000, 30000, key="compare_max_nodes")
    timeout = st.number_input("Timeout (s)", 5, 300, 30, key="compare_timeout")

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

    # Static comparison table
    st.markdown("---")
    st.subheader("Algorithm Properties Comparison")
    df = pd.DataFrame(COMPARISON_TABLE)
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.caption(NOTES)


# â”€â”€ Tab 5: Theory Notes â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
elif tab == "Theory":
    st.title("Theory Notes")

    group = st.selectbox("Algorithm Group", list(ALGORITHM_GROUPS.keys()), key="theory_group")
    algorithms = ALGORITHM_GROUPS[group]
    algo_name = st.selectbox("Algorithm", algorithms, key="theory_algo")

    theory_key = THEORY_KEY_MAP.get(algo_name, algo_name)
    theory_data = THEORY.get(theory_key)

    if theory_data:
        render_algorithm_info(algo_name, theory_data)
    else:
        st.info(f"Detailed theory for {algo_name} coming soon.")
        st.markdown(f"**{algo_name}** belongs to group: **{group}**")


# â”€â”€ Tab 6: CSP / Complex / Game Mode â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
elif tab == "Advanced":
    st.title("CSP / Complex Environments / Game Mode")

    mode = st.radio("Mode", [
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
    ], key="complex_mode")

    start = st.session_state.start_state

    common_kw = dict(start=start, goal=GOAL_STATE, timeout=30.0, action_order="LRUD")

    if mode == "CSP Definition & Propagation":
        t = st.number_input("Time Horizon", 1, 5, 3, key="csp_t")
        st.subheader("CSP Definition")
        result = csp_definition(time_horizon=t, **common_kw)
        st.markdown(result.message)
        st.subheader("Constraint Propagation")
        result2 = constraint_propagation(time_horizon=t, **common_kw)
        st.markdown(result2.message)

    elif mode == "Backtracking & Min-Conflicts":
        st.subheader("Backtracking Search")
        result = backtracking_search(**common_kw, max_steps=5000, timeout=30.0)
        render_result_metrics(result)
        if result.trace:
            render_trace_table(result.trace)
        st.markdown("---")
        st.subheader("Min-Conflicts")
        seed = st.number_input("Seed", 0, 99999, 42, key="mc_seed")
        result2 = min_conflicts(**common_kw, max_iterations=10000, seed=seed)
        render_result_metrics(result2)

    elif mode == "Constraint Graphs & Path Consistency":
        st.subheader("Constraint Graphs")
        t = st.number_input("Time Horizon", 1, 3, 2, key="cg_t")
        result = solve_csp_constraint_graphs(time_horizon=t, **common_kw)
        st.markdown(result.message)
        st.markdown("---")
        st.subheader("Path Consistency")
        result2 = path_consistency(**common_kw)
        st.markdown(result2.message)

    elif mode == "AND-OR Search (Nondeterministic)":
        d = st.number_input("Max Depth", 1, 15, 5, key="andor_depth")
        p = st.slider("Nondeterministic Probability", 0.1, 0.5, 0.3, key="andor_prob")
        seed = st.number_input("Seed", 0, 99999, 42, key="andor_seed")
        result = and_or_search(max_depth=d, nondet_prob=p, seed=seed, **common_kw)
        st.markdown(result.message)

    elif mode == "No Observation (Belief State)":
        n = st.number_input("Belief States", 2, 10, 5, key="no_obs_n")
        steps = st.number_input("Max Steps", 5, 50, 20, key="no_obs_steps")
        seed = st.number_input("Seed", 0, 99999, 42, key="no_obs_seed")
        result = no_observation_search(num_belief_states=n, max_steps=steps, seed=seed, **common_kw)
        render_result_metrics(result)
        if result.trace:
            render_trace_table(result.trace)

    elif mode == "Partially Observable":
        n = st.number_input("Belief States", 2, 10, 5, key="po_n")
        steps = st.number_input("Max Steps", 5, 50, 20, key="po_steps")
        seed = st.number_input("Seed", 0, 99999, 42, key="po_seed")
        result = partially_observable_search(num_belief_states=n, max_steps=steps, seed=seed, **common_kw)
        render_result_metrics(result)
        if result.trace:
            render_trace_table(result.trace)

    elif mode == "Online Search (LRTA*)":
        heuristic = st.selectbox("Heuristic", list(HEURISTICS.keys()), key="lrta_h")
        steps = st.number_input("Max Steps", 100, 100000, 10000, key="lrta_steps")
        result = online_search_lrta(heuristic=heuristic, max_steps=steps, **common_kw)
        render_result_metrics(result)
        if result.trace:
            render_trace_table(result.trace)

    elif mode == "Minimax Game":
        d = st.number_input("Game Tree Depth", 1, 5, 3, key="mm_depth")
        heuristic = st.selectbox("Heuristic", list(HEURISTICS.keys()), key="mm_h")
        result = minimax(depth=d, heuristic=heuristic, **common_kw)
        render_result_metrics(result)
        st.markdown(result.message)

    elif mode == "Alpha-Beta Pruning Game":
        d = st.number_input("Game Tree Depth", 1, 5, 3, key="ab_depth")
        heuristic = st.selectbox("Heuristic", list(HEURISTICS.keys()), key="ab_h")
        result = alpha_beta_pruning(depth=d, heuristic=heuristic, **common_kw)
        render_result_metrics(result)
        st.markdown(result.message)

    elif mode == "Expectimax (Stochastic)":
        d = st.number_input("Game Tree Depth", 1, 5, 3, key="em_depth")
        heuristic = st.selectbox("Heuristic", list(HEURISTICS.keys()), key="em_h")
        sp = st.slider("Success Probability", 0.5, 1.0, 0.8, key="em_sp")
        seed = st.number_input("Seed", 0, 99999, 42, key="em_seed")
        result = expectimax(depth=d, heuristic=heuristic, success_prob=sp, seed=seed, **common_kw)
        render_result_metrics(result)
        st.markdown(result.message)


if __name__ == "__main__":
    pass
