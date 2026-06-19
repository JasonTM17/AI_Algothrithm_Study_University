"""Advanced CSP, complex-environment, and game-mode Streamlit tab."""

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
    graph_coloring_demo,
    min_conflicts,
    path_consistency,
    solve_csp_constraint_graphs,
)
from core.heuristics import HEURISTICS
from core.puzzle import GOAL_STATE
from ui.academic_panels import render_academic_header, render_extension_warning
from ui.components import render_result_metrics, render_trace_table
from ui.map_coloring import render_coloring_map


def render_advanced_tab(start: tuple[int, ...]) -> None:
    """Render academic extensions for CSP, complex environments, and games."""
    st.title("CSP / Complex Environments / Game Mode")
    render_academic_header(
        "Extended AI environment demonstrations",
        "These modes show how the 15-puzzle can be reframed for CSP planning, uncertainty, online learning, and game-tree reasoning.",
        "Advanced academic models",
    )
    render_extension_warning()

    mode = st.radio("Mode", [
        "Graph Coloring (Map CSP)",
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

    base_kw = dict(start=start, goal=GOAL_STATE)
    csp_search_kw = dict(**base_kw, timeout=30.0)
    search_kw = dict(**base_kw, timeout=30.0, action_order="LRUD")

    if mode == "Graph Coloring (Map CSP)":
        st.subheader("Graph Coloring CSP — Bài toán tô màu bản đồ")
        st.info(
            "Mỗi phường/bang là một biến; miền là tập màu; hai vùng giáp ranh không được "
            "trùng màu. Đây là CSP bản đồ độc lập, không phải thuật toán giải 15-puzzle."
        )
        map_options = {
            "Thủ Đức 2025 — 12 phường hiện hành": "thu-duc-2025",
            "Australia — ví dụ kinh điển": "australia",
        }
        selected_map_label = st.selectbox(
            "Bản đồ / Map dataset",
            list(map_options),
            key="graph_coloring_map",
            help="Thủ Đức dùng địa giới 12 phường có hiệu lực từ 01/07/2025.",
        )
        selected_colors = st.multiselect(
            "Màu được phép / Available colors",
            ["Red", "Green", "Blue", "Yellow"],
            default=["Red", "Green", "Blue"],
            key="graph_coloring_colors",
        )
        result = graph_coloring_demo(
            colors=tuple(selected_colors),
            map_id=map_options[selected_map_label],
        )
        render_result_metrics(result)
        metric_a, metric_b, metric_c = st.columns(3)
        metric_a.metric("Color attempts", result.attempts)
        metric_b.metric("Backtracks", result.backtracks)
        metric_c.metric("Adjacency edges", sum(map(len, result.adjacency.values())) // 2)
        if not selected_colors:
            st.error("Hãy chọn ít nhất một màu. Thuật toán không tự thay thế lựa chọn của bạn.")
        elif result.success:
            st.success("Đã kiểm chứng: mọi phường/bang đều có màu và mọi cặp giáp ranh đều khác màu.")
        else:
            st.warning("Không tồn tại nghiệm với tập màu đã chọn. Hãy thêm màu hoặc xem các bước backtrack.")

        if len(result.assignment_history) > 1:
            palette_key = "_".join(selected_colors).lower()
            step_index = st.slider(
                "Bước chạy / Search step",
                0,
                len(result.assignment_history) - 1,
                len(result.assignment_history) - 1,
                key=f"graph_coloring_step_{result.map_id}_{palette_key}",
            )
        else:
            step_index = 0
            st.caption("Chưa có bước gán màu để hiển thị.")
        render_coloring_map(
            result,
            result.assignment_history[step_index],
            f"Step {step_index}/{len(result.assignment_history) - 1}: {result.history_labels[step_index]}",
        )

        rows = [
            {
                "Region": region,
                "Color": result.assignment.get(region, "—"),
                "Degree": len(neighbors),
                "Adjacent regions": ", ".join(sorted(neighbors)) or "—",
            }
            for region, neighbors in result.adjacency.items()
        ]
        with st.expander("Bảng giáp ranh và nghiệm chi tiết", expanded=True):
            st.dataframe(rows, width="stretch", hide_index=True)
        with st.expander("Dấu vết MRV / forward checking"):
            if result.trace:
                render_trace_table(result.trace)
            st.markdown(result.message)
        if result.map_id == "thu-duc-2025":
            metadata = result.source_metadata
            st.caption(
                "Hiệu lực 01/07/2025 · Nguồn pháp lý: "
                f"[{metadata['legal_source']}]({metadata['legal_source_url']}) · "
                f"Hình học: [{metadata['geometry_source']}]({metadata['geometry_source_url']}) "
                f"@ `{metadata['geometry_source_commit'][:12]}` ({metadata['geometry_license']}). "
                f"{metadata['disclaimer']}"
            )

    elif mode == "CSP Definition & Propagation":
        t = st.number_input("Time Horizon", 1, 5, 3, key="csp_t")
        st.subheader("CSP Definition")
        result = csp_definition(time_horizon=t, **base_kw)
        st.markdown(result.message)
        st.subheader("Constraint Propagation")
        result2 = constraint_propagation(time_horizon=t, **base_kw)
        st.markdown(result2.message)

    elif mode == "Backtracking & Min-Conflicts":
        st.subheader("Backtracking Search")
        result = backtracking_search(**csp_search_kw, max_steps=5000)
        render_result_metrics(result)
        if result.trace:
            render_trace_table(result.trace)
        st.markdown("---")
        st.subheader("Min-Conflicts")
        seed = st.number_input("Seed", 0, 99999, 42, key="mc_seed")
        result2 = min_conflicts(**csp_search_kw, max_iterations=10000, seed=seed)
        render_result_metrics(result2)

    elif mode == "Constraint Graphs & Path Consistency":
        st.subheader("Constraint Graphs")
        t = st.number_input("Time Horizon", 1, 3, 2, key="cg_t")
        result = solve_csp_constraint_graphs(time_horizon=t, **base_kw)
        st.markdown(result.message)
        st.markdown("---")
        st.subheader("Path Consistency")
        result2 = path_consistency(**base_kw)
        st.markdown(result2.message)

    elif mode == "AND-OR Search (Nondeterministic)":
        d = st.number_input("Max Depth", 1, 15, 5, key="andor_depth")
        p = st.slider("Nondeterministic Probability", 0.1, 0.5, 0.3, key="andor_prob")
        seed = st.number_input("Seed", 0, 99999, 42, key="andor_seed")
        result = and_or_search(max_depth=d, nondet_prob=p, seed=seed, **search_kw)
        st.markdown(result.message)

    elif mode == "No Observation (Belief State)":
        n = st.number_input("Belief States", 2, 10, 5, key="no_obs_n")
        steps = st.number_input("Max Steps", 5, 50, 20, key="no_obs_steps")
        seed = st.number_input("Seed", 0, 99999, 42, key="no_obs_seed")
        result = no_observation_search(num_belief_states=n, max_steps=steps, seed=seed, **search_kw)
        render_result_metrics(result)
        if result.trace:
            render_trace_table(result.trace)

    elif mode == "Partially Observable":
        n = st.number_input("Belief States", 2, 10, 5, key="po_n")
        steps = st.number_input("Max Steps", 5, 50, 20, key="po_steps")
        seed = st.number_input("Seed", 0, 99999, 42, key="po_seed")
        result = partially_observable_search(num_belief_states=n, max_steps=steps, seed=seed, **search_kw)
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
        d = st.number_input("Game Tree Depth", 1, 5, 3, key="mm_depth")
        heuristic = st.selectbox("Heuristic", list(HEURISTICS.keys()), key="mm_h")
        result = minimax(depth=d, heuristic=heuristic, **search_kw)
        render_result_metrics(result)
        st.markdown(result.message)

    elif mode == "Alpha-Beta Pruning Game":
        d = st.number_input("Game Tree Depth", 1, 5, 3, key="ab_depth")
        heuristic = st.selectbox("Heuristic", list(HEURISTICS.keys()), key="ab_h")
        result = alpha_beta_pruning(depth=d, heuristic=heuristic, **search_kw)
        render_result_metrics(result)
        st.markdown(result.message)

    elif mode == "Expectimax (Stochastic)":
        d = st.number_input("Game Tree Depth", 1, 5, 3, key="em_depth")
        heuristic = st.selectbox("Heuristic", list(HEURISTICS.keys()), key="em_h")
        sp = st.slider("Success Probability", 0.5, 1.0, 0.8, key="em_sp")
        seed = st.number_input("Seed", 0, 99999, 42, key="em_seed")
        result = expectimax(depth=d, heuristic=heuristic, success_prob=sp, seed=seed, **search_kw)
        render_result_metrics(result)
        st.markdown(result.message)
