"""Interactive Hand-Tracing Practice Mode for 15-Puzzle Simulator."""

import streamlit as st
import pandas as pd
from core.puzzle import PuzzleState, GOAL_STATE, scramble, is_solvable
from core.node import Node, reconstruct_path
from core.heuristics import HEURISTICS, manhattan_distance
from ui.components import render_puzzle_board, _state_to_mini_grid, _state_to_grid_str
from ui.academic_panels import render_exam_path
from ui.localization import LOC


def _register_hand_trace_node(node: Node) -> str:
    """Assign a stable display id to a hand-tracing node in session state."""
    object_key = id(node)
    node_ids = st.session_state.setdefault("ht_node_ids", {})
    node_records = st.session_state.setdefault("ht_node_records", {})
    if object_key not in node_ids:
        node_id = f"n{len(node_ids)}"
        node_ids[object_key] = node_id
    node_id = node_ids[object_key]
    node_records[node_id] = {
        "state": node.state,
        "g": node.g,
        "h": node.h,
        "f": node.f,
        "depth": node.depth,
    }
    return node_id


def _record_hand_trace_edge(parent: Node, child: Node, action: str) -> None:
    """Record an auditable parent-child edge produced by a legal expansion."""
    parent_id = _register_hand_trace_node(parent)
    child_id = _register_hand_trace_node(child)
    edges = st.session_state.setdefault("ht_tree_edges", [])
    edge = {"parent": parent_id, "child": child_id, "action": action}
    if edge not in edges:
        edges.append(edge)


def hand_trace_tree_dot() -> str:
    """Serialize the practiced expansion tree to Graphviz DOT."""
    node_records = st.session_state.get("ht_node_records", {})
    expanded = set(st.session_state.get("ht_expanded_node_ids", []))
    lines = [
        "digraph HandTraceTree {",
        "rankdir=TB;",
        "graph [bgcolor=transparent];",
        'node [shape=box style="rounded,filled" fontname="Arial" fontsize=9];',
        'edge [fontname="Arial" fontsize=9 color="#64748B"];',
    ]
    for node_id, record in node_records.items():
        state = record["state"]
        rows = [state[i:i + 4] for i in range(0, 16, 4)]
        grid = "\\n".join(" ".join("_" if value == 0 else str(value) for value in row) for row in rows)
        label = (
            f"{node_id} | d={record['depth']} g={record['g']} "
            f"h={record['h']:.1f} f={record['f']:.1f}\\n{grid}"
        )
        fill = "#D1FAE5" if node_id in expanded else "#E0E7FF"
        border = "#059669" if node_id in expanded else "#4F46E5"
        lines.append(f'{node_id} [label="{label}" fillcolor="{fill}" color="{border}"];')
    for edge in st.session_state.get("ht_tree_edges", []):
        lines.append(f'{edge["parent"]} -> {edge["child"]} [label="{edge["action"]}"];')
    lines.append("}")
    return "\n".join(lines)


def render_hand_trace_tree() -> None:
    """Render the explicit tree built from user-verified expansion steps."""
    if not st.session_state.get("ht_node_records"):
        st.info(t("tc_no_trace"))
        return
    st.caption(
        "Green nodes were expanded by your choices; every edge is a generated child from a legal blank move."
    )
    st.graphviz_chart(hand_trace_tree_dot(), width="stretch")


def t(key, **kwargs):
    global_lang = st.session_state.get("global_lang_select", "Tiếng Việt")
    text = LOC[global_lang].get(key, key)
    if kwargs:
        return text.format(**kwargs)
    return text


def _get_sort_key(item, algorithm, tie_breaker):
    """Return sorting key for frontier item (node, counter)."""
    node, counter = item
    if algorithm == "BFS":
        return counter  # FIFO
    elif algorithm == "DFS":
        return -counter  # LIFO
    elif algorithm == "UCS":
        cost = node.g
        if tie_breaker == "LIFO":
            return (cost, 0, -counter)
        elif tie_breaker == "Min-g":
            return (cost, node.g, counter)
        elif tie_breaker == "Max-g":
            return (cost, -node.g, counter)
        else:  # FIFO
            return (cost, 0, counter)
    elif algorithm == "Greedy Best-First":
        cost = node.h
        if tie_breaker == "LIFO":
            return (cost, 0, -counter)
        elif tie_breaker == "Min-g":
            return (cost, node.g, counter)
        elif tie_breaker == "Max-g":
            return (cost, -node.g, counter)
        else:  # FIFO
            return (cost, 0, counter)
    elif algorithm == "A*":
        cost = node.f
        if tie_breaker == "LIFO":
            return (cost, 0, -counter)
        elif tie_breaker == "Min-g":
            return (cost, node.g, counter)
        elif tie_breaker == "Max-g":
            return (cost, -node.g, counter)
        else:  # FIFO
            return (cost, 0, counter)
    return counter


def init_tracing_challenge(algorithm, heuristic_name, tie_breaker, scramble_depth, action_order):
    """Initialize state for a new hand-tracing challenge."""
    # Generate simple start state solvable in scramble_depth steps
    start_state = scramble(depth=scramble_depth, seed=None, action_order=action_order)
    
    # Ensure it's solvable and not already solved (max 1000 attempts)
    for _ in range(1000):
        if start_state != GOAL_STATE and is_solvable(start_state):
            break
        start_state = scramble(depth=scramble_depth, seed=None, action_order=action_order)
        
    h_fn = HEURISTICS.get(heuristic_name, manhattan_distance)
    
    st.session_state.ht_active = True
    st.session_state.ht_start = start_state
    st.session_state.ht_algorithm = algorithm
    st.session_state.ht_heuristic = heuristic_name
    st.session_state.ht_tie_breaker = tie_breaker
    st.session_state.ht_action_order = action_order
    st.session_state.ht_scramble_depth = scramble_depth
    
    # Root node setup
    root_h = h_fn(start_state) if algorithm not in ["BFS", "DFS", "UCS"] else 0.0
    root_node = Node(state=start_state, g=0, depth=0, h=root_h)
    
    st.session_state.ht_step = 0
    st.session_state.ht_current = root_node
    st.session_state.ht_frontier = [(root_node, 0)]  # list of (node, counter)
    st.session_state.ht_reached = {start_state: 0}   # state -> g
    st.session_state.ht_history = []
    st.session_state.ht_counter = 0
    st.session_state.ht_solved = False
    st.session_state.ht_feedback = None
    st.session_state.ht_feedback_type = None
    st.session_state.ht_node_ids = {}
    st.session_state.ht_node_records = {}
    st.session_state.ht_tree_edges = []
    st.session_state.ht_expanded_node_ids = []
    _register_hand_trace_node(root_node)


def render_hand_tracing_page():
    st.title(t("ht_title"))
    render_exam_path("Hand-Tracing")
    st.markdown(t("ht_desc"))

    # ── Configuration Panel ──
    with st.expander(t("ht_setup"), expanded=not st.session_state.get("ht_active", False)):
        col1, col2 = st.columns(2)
        with col1:
            algorithm = st.selectbox(
                t("run_algo"),
                ["BFS", "DFS", "UCS", "Greedy Best-First", "A*"],
                key="ht_algo_select"
            )
            
            # Show heuristic only for informed search
            if algorithm in ["Greedy Best-First", "A*"]:
                heuristic_name = st.selectbox(
                    t("run_heuristic"),
                    list(HEURISTICS.keys()),
                    key="ht_heuristic_select"
                )
            else:
                heuristic_name = "Manhattan Distance"
                
        with col2:
            # Show tie breaker only for priority queue algorithms
            if algorithm in ["UCS", "Greedy Best-First", "A*"]:
                tie_breaker = st.selectbox(
                    t("ht_tie_breaker"),
                    ["FIFO", "LIFO", "Min-g", "Max-g"],
                    key="ht_tie_select"
                )
            else:
                tie_breaker = "FIFO"
                
            scramble_depth = st.slider(
                t("ht_scramble"),
                1, 4, 2,
                help=t("ht_scramble_help")
            )
            
        action_order = st.selectbox(
            t("ht_order"),
            ["LRUD", "UDLR", "RLDU", "DURL"],
            key="ht_order_select",
            help=t("ht_order_help")
        )

        if st.button(t("ht_btn_generate"), key="btn_ht_generate", type="primary"):
            init_tracing_challenge(algorithm, heuristic_name, tie_breaker, scramble_depth, action_order)
            st.rerun()

    if not st.session_state.get("ht_active", False):
        idle_message = (
            "Select an algorithm and press 'Generate New Challenge' to start."
            if st.session_state.get("global_lang_select") == "English"
            else "Hãy chọn thuật toán và nhấn 'Tạo Thử Thách Mới' để bắt đầu luyện tập."
        )
        st.info(idle_message)
        return

    # Tracing challenge is active.
    algo = st.session_state.ht_algorithm
    tb = st.session_state.ht_tie_breaker
    h_name = st.session_state.ht_heuristic
    frontier = st.session_state.ht_frontier
    reached = st.session_state.ht_reached
    step_num = st.session_state.ht_step
    solved = st.session_state.ht_solved

    st.markdown("---")
    col_info, col_btn = st.columns([3, 1])
    with col_info:
        st.subheader(f"{t('run_algo')}: **{algo}** | Tie-breaker: `{tb}`")
        if algo in ["Greedy Best-First", "A*"]:
            st.caption(f"{t('run_heuristic')}: *{h_name}* | {t('run_action_order')}: `{st.session_state.ht_action_order}`")
        else:
            st.caption(f"{t('run_action_order')}: `{st.session_state.ht_action_order}`")
    with col_btn:
        if st.button(t("ht_btn_cancel"), key="btn_ht_cancel"):
            st.session_state.ht_active = False
            st.rerun()

    # Calculate the mathematically correct next node to expand
    if not frontier:
        st.error("Frontier is empty — search space exhausted.")
        st.session_state.ht_active = False
        st.rerun()
    correct_item = min(frontier, key=lambda item: _get_sort_key(item, algo, tb))
    correct_node, _ = correct_item

    # Render Board States side-by-side
    st.markdown(f"### {t('ht_cur_state')}")
    col_start, col_curr, col_goal = st.columns(3)
    with col_start:
        st.markdown(f"**{t('ht_state_start')}**")
        render_puzzle_board(st.session_state.ht_start, size="small")
    with col_curr:
        st.markdown(f"**{t('ht_state_curr')}**")
        render_puzzle_board(st.session_state.ht_current.state, size="small")
        st.caption(t("ht_curr_step", step=step_num))
    with col_goal:
        st.markdown(f"**{t('ht_state_goal')}**")
        render_puzzle_board(GOAL_STATE, highlight_correct=False, size="small")

    # Show feedback from last choice
    if st.session_state.ht_feedback:
        if st.session_state.ht_feedback_type == "success":
            st.success(st.session_state.ht_feedback)
        else:
            st.error(st.session_state.ht_feedback)

    # ── Solved State ──
    if solved:
        st.balloons()
        st.success(t("ht_success_msg"))
        
        # Display final table
        st.subheader(t("ht_table_title"))
        df_hist = pd.DataFrame(st.session_state.ht_history)
        st.dataframe(df_hist, width="stretch", hide_index=True)
        
        # Display final search tree
        st.subheader(t("ht_tree_title"))
        render_hand_trace_tree()
        
        if st.button(t("ht_btn_new"), key="btn_new_after_solve", type="primary"):
            st.session_state.ht_active = False
            st.rerun()
        return

    # ── Frontier Interaction ──
    st.markdown("---")
    st.subheader(t("ht_decision"))
    st.markdown(t("ht_decision_desc"))

    # Show frontier options as cards in rows of 4
    selected_idx = -1
    row_size = 4

    for i, (node, counter) in enumerate(frontier):
        row_start = (i // row_size) * row_size
        if i % row_size == 0:
            row_cols = st.columns(min(len(frontier) - i, row_size))
        col_idx = i % row_size
        with row_cols[col_idx]:
            st.markdown(f"**{t('ht_choice', num=i+1)}**")
            render_puzzle_board(node.state, size="mini")
            
            # Print node metrics
            metrics_str = f"g={node.g}"
            if algo in ["Greedy Best-First", "A*"]:
                metrics_str += f" | h={node.h:.1f}"
            if algo == "A*":
                metrics_str += f" | f={node.f:.1f}"
                
            st.caption(metrics_str)
            
            dir_labels = {
                "L": t("dir_L").split(" ")[0],
                "R": t("dir_R").split(" ")[0],
                "U": t("dir_U").split(" ")[0],
                "D": t("dir_D").split(" ")[0]
            }
            act_label = dir_labels.get(node.action, node.action or t("dir_Start"))
            st.caption(t("ht_expanded_to", act=act_label))
            
            if st.button(t("ht_choice_btn", num=i+1), key=f"btn_choose_{i}", width="stretch"):
                selected_idx = i

    # ── Handle Selection Logic ──
    if selected_idx >= 0:
        chosen_node, chosen_counter = frontier[selected_idx]
        
        # Verify if choice is correct
        if chosen_node.state == correct_node.state:
            # CORRECT CHOICE!
            st.session_state.ht_feedback_type = "success"
            st.session_state.ht_feedback = t("ht_expand_success", num=selected_idx+1)
            chosen_id = _register_hand_trace_node(chosen_node)
            if chosen_id not in st.session_state.ht_expanded_node_ids:
                st.session_state.ht_expanded_node_ids.append(chosen_id)
            
            # Check if this node is Goal
            if chosen_node.state == GOAL_STATE:
                # Add to history
                hist_item = {
                    t("tc_step"): step_num + 1,
                    t("tc_action"): chosen_node.action or t("dir_Start"),
                    "depth": chosen_node.depth,
                    "g": chosen_node.g,
                    "h": chosen_node.h,
                    "f": chosen_node.f,
                    "Frontier size": len(frontier) - 1,
                    "Reached size": len(reached)
                }
                st.session_state.ht_history.append(hist_item)
                st.session_state.ht_solved = True
                st.session_state.ht_frontier = []
                st.rerun()
                
            # Perform expansion
            st.session_state.ht_step += 1
            st.session_state.ht_current = chosen_node
            
            # Remove chosen node from frontier
            new_frontier = [item for item in frontier if item[0].state != chosen_node.state]
            
            # Expand chosen node
            ps = PuzzleState(chosen_node.state)
            action_order = st.session_state.ht_action_order
            neighbors = ps.get_neighbors(action_order)
            
            h_fn = HEURISTICS.get(h_name, manhattan_distance)
            
            added_neighbors = []
            
            for ns, action, cost in neighbors:
                new_g = chosen_node.g + cost
                
                # Check duplicate
                if algo == "DFS":
                    path_states = reconstruct_path(chosen_node)
                    if ns in path_states:
                        continue
                else:
                    if ns in reached and new_g >= reached[ns]:
                        continue
                
                # Node is valid, create child
                h_val = h_fn(ns) if algo in ["Greedy Best-First", "A*"] else 0.0
                child = Node(state=ns, parent=chosen_node, action=action, g=new_g, depth=chosen_node.depth + 1, h=h_val)
                _record_hand_trace_edge(chosen_node, child, action)
                
                st.session_state.ht_counter += 1
                new_frontier.append((child, st.session_state.ht_counter))
                reached[ns] = new_g
                added_neighbors.append(f"{action} (g={new_g})")
            
            # Save step history
            frontier_desc = ", ".join([f"{item[0].action or t('dir_Start')}(f={item[0].f})" for item in new_frontier])
            reached_desc = f"{len(reached)} states"
            
            hist_item = {
                t("tc_step"): step_num + 1,
                t("tc_action"): chosen_node.action or t("dir_Start"),
                "depth": chosen_node.depth,
                "g": chosen_node.g,
                "h": chosen_node.h,
                "f": chosen_node.f,
                t("tc_frontier"): f"[{frontier_desc}]",
                t("tc_reached"): reached_desc
            }
            st.session_state.ht_history.append(hist_item)
            
            st.session_state.ht_frontier = new_frontier
            st.session_state.ht_reached = reached
            st.rerun()
            
        else:
            # INCORRECT CHOICE!
            st.session_state.ht_feedback_type = "error"
            
            # Explain why
            metrics_chosen = f"f={chosen_node.f}" if algo == "A*" else (f"h={chosen_node.h}" if algo == "Greedy Best-First" else f"g={chosen_node.g}")
            metrics_correct = f"f={correct_node.f}" if algo == "A*" else (f"h={correct_node.h}" if algo == "Greedy Best-First" else f"g={correct_node.g}")
            
            explain_msg = t("ht_expand_error", 
                            chosen=chosen_node.action or t("dir_Start"), 
                            chosen_val=metrics_chosen, 
                            algo=algo, 
                            tb=tb, 
                            correct=correct_node.action or t("dir_Start"), 
                            correct_val=metrics_correct)
            st.session_state.ht_feedback = explain_msg
            st.rerun()

    # ── Progress Panel (Frontier & Reached List) ──
    st.markdown("---")
    col_f, col_r = st.columns(2)
    
    with col_f:
        st.markdown(t("ht_frontier_title", count=len(frontier)))
        frontier_rows = []
        for i, (node, counter) in enumerate(frontier):
            row = {
                "STT": i + 1,
                t("tc_action"): node.action or t("dir_Start"),
                "g(n)": node.g,
            }
            if algo in ["Greedy Best-First", "A*"]:
                row["h(n)"] = f"{node.h:.1f}"
                row["f(n)"] = f"{node.f:.1f}"
            frontier_rows.append(row)
            
        if frontier_rows:
            st.dataframe(pd.DataFrame(frontier_rows), width="stretch", hide_index=True)
        else:
            st.caption("Trống" if st.session_state.get("global_lang_select") == "Tiếng Việt" else "Empty")
            
    with col_r:
        st.markdown(t("ht_reached_title", count=len(reached)))
        reached_rows = []
        for i, (state_val, g_val) in enumerate(reached.items()):
            reached_rows.append({
                "STT": i + 1,
                "Trạng thái" if st.session_state.get("global_lang_select") == "Tiếng Việt" else "State": f"State {str(state_val[:4])}...",
                "Cost g": g_val
            })
        if reached_rows:
            st.dataframe(pd.DataFrame(reached_rows), width="stretch", hide_index=True, height=180)
        else:
            st.caption("Trống" if st.session_state.get("global_lang_select") == "Tiếng Việt" else "Empty")

    # ── History Tracing Table ──
    if st.session_state.ht_history:
        st.markdown("---")
        st.subheader(t("ht_history_title"))
        df_history = pd.DataFrame(st.session_state.ht_history)
        # Drop columns not suitable for intermediate viewing
        cols_to_show = [c for c in df_history.columns if c not in ["depth", "g", "h", "f"]]
        st.dataframe(df_history[cols_to_show], width="stretch", hide_index=True)
        with st.expander(t("ht_tree_title"), expanded=False):
            render_hand_trace_tree()
