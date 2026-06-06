"""UI Components for 15-Puzzle AI Streamlit app — Enhanced game-like experience."""

import streamlit as st
import pandas as pd
from core.puzzle import PuzzleState, GOAL_STATE, is_solvable
from core.utils import format_state_grid
from ui.styles import STYLES, GROUP_COLORS


def render_styles():
    """Inject custom CSS styles."""
    st.markdown(STYLES, unsafe_allow_html=True)


# ── Click-to-Slide Helpers ──────────────────────────────────────

def _is_adjacent_to_blank(state: tuple, tile_idx: int) -> bool:
    """Check if tile at tile_idx is adjacent to the blank (0)."""
    blank_idx = state.index(0)
    br, bc = blank_idx // 4, blank_idx % 4
    tr, tc = tile_idx // 4, tile_idx % 4
    return abs(br - tr) + abs(bc - tc) == 1


def _get_slide_direction(state: tuple, tile_idx: int) -> str | None:
    """Return the action that slides tile_idx into blank position."""
    blank_idx = state.index(0)
    if tile_idx == blank_idx - 1 and blank_idx % 4 != 0:
        return "R"
    if tile_idx == blank_idx + 1 and tile_idx % 4 != 0:
        return "L"
    if tile_idx == blank_idx - 4:
        return "D"
    if tile_idx == blank_idx + 4:
        return "U"
    return None


def render_clickable_board(state: tuple, key_prefix: str = "board",
                           highlight_correct: bool = True,
                           on_click_fn=None):
    """Render interactive 4x4 puzzle board with game-like 3D tile design.

    Uses HTML grid for visuals + Streamlit columns/buttons for interaction.
    Tiles have row-based gradients, 3D shadows, checkerboard blank, hover lift.

    Args:
        state: 16-element tuple
        key_prefix: unique key for Streamlit buttons
        highlight_correct: green highlight for tiles in goal position
        on_click_fn: callback function(direction) when a tile is clicked
    """
    for r in range(4):
        cols = st.columns(4, gap="small")
        for c in range(4):
            idx = r * 4 + c
            val = state[idx]
            with cols[c]:
                if val == 0:
                    st.markdown(
                        '<div class="puzzle-tile blank"></div>',
                        unsafe_allow_html=True,
                    )
                else:
                    cls_list = ["puzzle-tile", f"row-{r}"]
                    if highlight_correct and val == GOAL_STATE[idx]:
                        cls_list.append("correct")
                    cls_str = " ".join(cls_list)

                    if _is_adjacent_to_blank(state, idx) and on_click_fn:
                        direction = _get_slide_direction(state, idx)
                        st.button(
                            str(val), key=f"{key_prefix}_hit_{r}_{c}",
                            on_click=on_click_fn, args=(direction,),
                            type="primary",
                        )
                    else:
                        st.markdown(
                            f'<div class="{cls_str}">{val}</div>',
                            unsafe_allow_html=True,
                        )


def render_image_board(state: tuple, image_tiles: dict, key_prefix: str = "img",
                       highlight_correct: bool = True, on_click_fn=None):
    """Render interactive 4x4 board with pure image tiles (no number overlay).

    Each tile shows ONLY the image piece. Blank tile is empty.
    Click behavior same as number board.

    Args:
        state: 16-element tuple
        image_tiles: dict mapping tile value (1-15) to base64 data URL
        key_prefix: unique key for Streamlit buttons
        highlight_correct: green border for tiles in goal position
        on_click_fn: callback function(direction) when a tile is clicked
    """
    for r in range(4):
        cols = st.columns(4, gap="small")
        for c in range(4):
            idx = r * 4 + c
            val = state[idx]
            with cols[c]:
                if val == 0:
                    st.markdown(
                        '<div style="width:100%;aspect-ratio:1;border:1px dashed '
                        'rgba(255,255,255,0.08);border-radius:12px;background:transparent;">'
                        '</div>',
                        unsafe_allow_html=True,
                    )
                elif val in image_tiles:
                    is_correct = highlight_correct and val == GOAL_STATE[idx]
                    border_style = "2px solid #22c55e" if is_correct else "none"
                    img_html = (
                        f'<div style="width:100%;aspect-ratio:1;border-radius:12px;'
                        f'overflow:hidden;border:{border_style};cursor:pointer;">'
                        f'<img src="{image_tiles[val]}" style="width:100%;height:100%;'
                        f'object-fit:cover;" alt="tile{val}">'
                        f'</div>'
                    )
                    if _is_adjacent_to_blank(state, idx) and on_click_fn:
                        direction = _get_slide_direction(state, idx)
                        st.markdown(img_html, unsafe_allow_html=True)
                        st.button(f"Move", key=f"{key_prefix}_hit_{val}_{r}_{c}",
                                  on_click=on_click_fn, args=(direction,),
                                  type="primary")
                    else:
                        st.markdown(img_html, unsafe_allow_html=True)
                else:
                    st.button(str(val), key=f"{key_prefix}_{val}_{r}_{c}",
                              disabled=True, use_container_width=True)


def render_puzzle_board(state: tuple, highlight_correct: bool = True, size: str = "normal"):
    """Render 4x4 puzzle board as HTML with game-like styling.

    Args:
        state: 16-element tuple representing the puzzle state
        highlight_correct: Whether to highlight tiles in goal position (green)
        size: 'normal' (70px cells) or 'small' (50px cells) or 'mini' (28px cells)
    """
    cell_size = {"normal": 70, "small": 50, "mini": 28}[size]
    font_size = {"normal": 22, "small": 16, "mini": 10}[size]

    cells = []
    for i, val in enumerate(state):
        if val == 0:
            cells.append(
                f'<div class="puzzle-cell blank" style="width:{cell_size}px;height:{cell_size}px;'
                f'font-size:{font_size}px;">_</div>'
            )
        else:
            correct = (val == GOAL_STATE[i]) if highlight_correct else False
            cls = "correct" if correct else "filled"
            cells.append(
                f'<div class="puzzle-cell {cls}" style="width:{cell_size}px;height:{cell_size}px;'
                f'font-size:{font_size}px;"><span class="tile-number">{val}</span></div>'
            )

    html = f'<div class="puzzle-grid">{"".join(cells)}</div>'
    st.markdown(html, unsafe_allow_html=True)


def render_puzzle_with_image(state: tuple, image_tiles: dict, highlight_correct: bool = True):
    """Render 4x4 puzzle board with image tiles overlaid on numbers.

    Args:
        state: 16-element tuple representing the puzzle state
        image_tiles: dict mapping tile value (1-15) to base64-encoded image data URL
        highlight_correct: Whether to highlight tiles in goal position
    """
    cells = []
    for i, val in enumerate(state):
        if val == 0:
            cells.append(
                '<div class="puzzle-cell blank" style="width:70px;height:70px;font-size:22px;">_</div>'
            )
        else:
            correct = (val == GOAL_STATE[i]) if highlight_correct else False
            cls = "correct" if correct else "filled"
            img_html = ""
            if val in image_tiles:
                img_html = f'<img class="tile-img" src="{image_tiles[val]}" alt="{val}">'
            cells.append(
                f'<div class="puzzle-cell {cls}" style="width:70px;height:70px;font-size:22px;position:relative;">'
                f'{img_html}<span class="tile-number" style="position:relative;z-index:2;">{val}</span></div>'
            )

    html = f'<div class="puzzle-grid">{"".join(cells)}</div>'
    st.markdown(html, unsafe_allow_html=True)


def render_puzzle_row(states: list[tuple], labels: list[str] = None, max_cols: int = 5):
    """Render multiple puzzle states in a row."""
    if not states:
        return

    cols = st.columns(min(len(states), max_cols))
    for i, (col, state) in enumerate(zip(cols, states)):
        with col:
            if labels and i < len(labels):
                st.caption(labels[i])
            render_puzzle_board(state)


def render_result_metrics(result):
    """Render search result as metric cards."""
    if result is None:
        return

    col1, col2, col3, col4 = st.columns(4)
    success = result.success
    icon = "OK" if success else "FAIL"

    with col1:
        st.metric("Status", f"{icon} {'Solved' if success else 'Failed'}")
    with col2:
        st.metric("Path Length", str(len(result.actions)) if success else "-")
    with col3:
        st.metric("Runtime", f"{result.runtime:.4f}s")
    with col4:
        st.metric("Nodes Expanded", str(result.nodes_expanded))

    col5, col6, col7, col8 = st.columns(4)
    with col5:
        st.metric("Cost", str(result.cost) if success else "-")
    with col6:
        st.metric("Max Frontier", str(result.max_frontier_size))
    with col7:
        st.metric("Reached Size", str(result.reached_size))
    with col8:
        st.metric("Depth", str(result.depth) if success else "-")

    if result.message:
        msg_cls = "result-success" if success else "result-failure"
        st.markdown(f'<div class="{msg_cls}">{result.message}</div>', unsafe_allow_html=True)


def render_trace_table(trace: list, max_rows: int = 100):
    """Render trace steps as a scrollable table."""
    if not trace:
        st.info("No trace data available.")
        return

    rows = []
    for step in trace[:max_rows]:
        row = {
            "Step": step.step,
            "Action": step.action or "-",
        }
        if step.g > 0:
            row["g(n)"] = step.g
        if step.h > 0 or step.step == 0:
            row["h(n)"] = f"{step.h:.1f}"
        if step.f > 0:
            row["f(n)"] = f"{step.f:.1f}"
        if step.frontier_size > 0:
            row["Frontier"] = step.frontier_size
        if step.reached_size > 0:
            row["Reached"] = step.reached_size
        if step.temperature is not None:
            row["T"] = f"{step.temperature:.4f}"
        if step.probability is not None:
            row["P(accept)"] = f"{step.probability:.4f}"
        if step.accepted is not None:
            row["Accepted"] = "Yes" if step.accepted else "No"
        if step.belief_size is not None:
            row["Belief"] = step.belief_size
        if step.node_type:
            row["Type"] = step.node_type
        if step.reason:
            row["Reason"] = step.reason[:60]
        rows.append(row)

    if len(trace) > max_rows:
        st.caption(f"Showing {max_rows} of {len(trace)} steps")

    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, height=300)


def _state_to_mini_grid(state: tuple) -> str:
    """Return a compact HTML mini-grid for a puzzle state."""
    cells = []
    for v in state:
        if v == 0:
            cells.append('<span class="mc b">_</span>')
        elif v == GOAL_STATE[state.index(v)]:
            cells.append(f'<span class="mc c">{v}</span>')
        else:
            cells.append(f'<span class="mc f">{v}</span>')
    return f'<div class="puzzle-grid-mini">{"".join(cells)}</div>'


def _state_to_grid_str(state: tuple) -> str:
    """Format a 4x4 puzzle state as a compact grid string for code blocks."""
    lines = []
    for r in range(4):
        row_vals = []
        for c in range(4):
            v = state[r * 4 + c]
            row_vals.append("__" if v == 0 else f"{v:2d}")
        lines.append(" ".join(row_vals))
    return "\n".join(lines)


def render_search_detail_table(trace: list, max_rows: int = 50):
    """Render detailed Node/Frontier/Reached table for each trace step."""
    if not trace:
        st.info("No trace data available.")
        return

    has_detail = any(
        hasattr(s, 'node_state') and s.node_state is not None
        for s in trace[:max_rows]
    )
    if not has_detail:
        st.info("Node/Frontier/Reached detail not available for this algorithm. "
                "Available for: BFS, DFS, UCS, IDS, Greedy, A*, IDA*.")
        return

    step_idx = st.slider(
        "Select step to inspect", 0, min(len(trace) - 1, max_rows - 1), 0,
        key="detail_step_slider"
    )

    step = trace[step_idx]

    st.markdown(f"**Step {step.step}** | Action: `{step.action or 'Start'}` | "
                f"g={step.g} h={step.h:.1f} f={step.f:.1f}")

    col1, col2, col3 = st.columns([1, 2, 2])

    with col1:
        st.markdown("**Current Node**")
        if step.node_state:
            render_puzzle_board(step.node_state, size="small")
        else:
            render_puzzle_board(step.state, size="small")

    with col2:
        st.markdown(f"**Frontier** ({step.frontier_size} states)")
        if step.frontier_states and len(step.frontier_states) > 0:
            frontier_display = step.frontier_states[:6]
            for i, fs in enumerate(frontier_display):
                st.markdown(_state_to_mini_grid(fs), unsafe_allow_html=True)
            if len(step.frontier_states) > 6:
                st.caption(f"... +{len(step.frontier_states) - 6} more")
        else:
            st.caption("Empty or not captured")

    with col3:
        st.markdown(f"**Reached** ({step.reached_size} states)")
        if step.reached_states and len(step.reached_states) > 0:
            reached_display = step.reached_states[:6]
            for i, rs in enumerate(reached_display):
                st.markdown(_state_to_mini_grid(rs), unsafe_allow_html=True)
            if len(step.reached_states) > 6:
                st.caption(f"... +{len(step.reached_states) - 6} more")
        else:
            st.caption("Not captured for this algorithm")


def render_path_animation(path: list[tuple], actions: list[str], key: str = "path"):
    """Render path animation with auto-play, step slider, and speed control."""
    if not path or len(path) < 2:
        if path and len(path) == 1:
            render_puzzle_board(path[0])
            st.caption("Already at goal state!")
        return

    st.markdown("---")
    st.subheader("Solution Animation")

    # Auto-play controls
    auto_key = f"{key}_autoplay"
    speed_key = f"{key}_speed"

    col_play, col_speed, col_step = st.columns([1, 2, 3])

    with col_play:
        auto_play = st.button("Auto Play", key=f"{key}_play_btn")

    with col_speed:
        speed = st.selectbox(
            "Speed", [0.1, 0.3, 0.5, 1.0, 2.0], index=2,
            format_func=lambda x: f"{x}s per step",
            key=speed_key
        )

    current_step = st.slider(
        "Step", 0, len(path) - 1, 0, key=f"{key}_slider"
    )

    # Show current state
    render_puzzle_board(path[current_step])

    if current_step < len(actions):
        action_display = actions[current_step] if current_step > 0 else "Start"
        direction_map = {"L": "Left", "R": "Right", "U": "Up", "D": "Down"}
        display = direction_map.get(action_display, action_display)
        st.caption(f"Step {current_step}/{len(path)-1}: {display}")
    else:
        st.caption(f"Step {current_step}/{len(path)-1}: Goal!")

    # Navigation buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Prev", key=f"{key}_prev"):
            st.session_state[f"{key}_slider"] = max(0, current_step - 1)
    with col2:
        if st.button("Next", key=f"{key}_next"):
            st.session_state[f"{key}_slider"] = min(len(path) - 1, current_step + 1)
    with col3:
        if st.button("Reset", key=f"{key}_reset"):
            st.session_state[f"{key}_slider"] = 0

    # Auto-play implementation using session state
    if auto_play:
        st.session_state[auto_key] = True
        st.session_state[f"{key}_auto_step"] = 0

    if st.session_state.get(auto_key, False):
        current_auto = st.session_state.get(f"{key}_auto_step", 0)
        if current_auto < len(path) - 1:
            import time
            st.session_state[f"{key}_slider"] = current_auto
            st.session_state[f"{key}_auto_step"] = current_auto + 1
            time.sleep(speed)
            st.rerun()
        else:
            st.session_state[auto_key] = False
            st.session_state[f"{key}_auto_step"] = 0
            st.success("Animation complete!")


def render_comparison_table(results: list):
    """Render comparison table for benchmark results."""
    if not results:
        st.info("Run algorithms first to see comparison.")
        return

    rows = []
    for r in results:
        row = {
            "Group": r.group,
            "Algorithm": r.algorithm,
            "Solved": "Yes" if r.success else "No",
            "Path": len(r.actions) if r.success else "-",
            "Cost": r.cost if r.success else "-",
            "Expanded": r.nodes_expanded,
            "Max Frontier": r.max_frontier_size,
            "Time (s)": f"{r.runtime:.4f}",
            "Optimal?": "Yes" if r.is_optimal else "No",
            "Complete?": "Yes" if r.is_complete else "No",
        }
        rows.append(row)

    df = pd.DataFrame(rows)
    st.dataframe(df, use_container_width=True, hide_index=True)

    if len([r for r in results if r.success]) > 1:
        successful = [r for r in results if r.success]
        fastest = min(successful, key=lambda x: x.runtime)
        shortest = min(successful, key=lambda x: len(x.actions))

        st.markdown("### Analysis")
        st.markdown(f"- **Fastest**: {fastest.algorithm} ({fastest.runtime:.4f}s)")
        st.markdown(f"- **Shortest path**: {shortest.algorithm} ({len(shortest.actions)} steps)")
        if max(successful, key=lambda x: x.nodes_expanded).algorithm != min(successful, key=lambda x: x.nodes_expanded).algorithm:
            st.markdown(f"- **Most memory**: {max(successful, key=lambda x: x.nodes_expanded).algorithm} ({max(successful, key=lambda x: x.nodes_expanded).nodes_expanded} nodes)")


def render_algorithm_info(algo_name: str, theory: dict):
    """Render algorithm theory information."""
    if not theory:
        st.info(f"No theory information available for {algo_name}.")
        return

    group = theory.get("group", "")
    group_style = GROUP_COLORS.get(group, {})

    st.markdown(f"### {theory.get('name', algo_name)}")

    badge_cls = group_style.get("badge", "")
    if badge_cls:
        st.markdown(f'<span class="group-badge {badge_cls}">{group}</span>', unsafe_allow_html=True)

    props = []
    if theory.get("suitable"):
        suitable = theory["suitable"]
        if "RẤT" in suitable or "rất" in suitable.lower():
            props.append(("Phu hop", "#06d6a0"))
        elif "KHÔNG" in suitable or "không" in suitable.lower():
            props.append(("Khong phu hop", "#ef476f"))
        else:
            props.append(("Han che", "#ffd166"))

    for label, color in props:
        st.markdown(f'<span style="background:{color};color:#fff;padding:2px 10px;border-radius:12px;font-size:12px;font-weight:600;">{label}</span>', unsafe_allow_html=True)

    sections = [
        ("Muc tieu", "goal"),
        ("Y tuong", "idea"),
        ("Cau truc du lieu", "data_structure"),
        ("Cong thuc", "formula"),
        ("Ap dung 15-Puzzle", "application"),
        ("Phu hop 15-Puzzle?", "suitable"),
        ("Uu diem", "pros"),
        ("Nhuoc diem", "cons"),
        ("Do phuc tap", "complexity"),
        ("Vi du chay te", "bad_example"),
        ("So sanh", "comparison"),
        ("Diem can nho khi thi", "exam_tips"),
    ]

    for title, key in sections:
        content = theory.get(key)
        if content:
            if isinstance(content, list):
                content = "\n".join(f"- {item}" for item in content)
            st.markdown(f"**{title}**\n\n{content}")

    pseudocode = theory.get("pseudocode")
    if pseudocode:
        st.markdown("**Pseudocode**")
        st.code(pseudocode, language="python")


def render_search_tree(trace: list, max_nodes: int = 30):
    """Render search tree as indented text with matrix states."""
    if not trace:
        st.info("No trace data to visualize.")
        return

    st.markdown("### Search Tree Visualization")
    st.caption("Each node shows the 4×4 puzzle grid, g/h/f values, and action taken.")

    has_detail = any(
        hasattr(s, 'node_state') and s.node_state is not None
        for s in trace[:max_nodes]
    )

    lines = []
    disp_count = min(len(trace), max_nodes)

    for i in range(disp_count):
        step = trace[i]
        indent = "│  " * min(i, 6) + ("├─" if i < disp_count - 1 else "└─")
        action_str = step.action or "Start"
        state = step.node_state if (has_detail and step.node_state) else step.state
        grid = " ".join(f"{v:2d}" if v != 0 else "__" for v in state)
        parts = [f"Step {step.step}", action_str, f"[{grid}]"]
        if step.h > 0 or step.step == 0:
            parts.append(f"h={step.h:.1f}")
        if step.f > 0:
            parts.append(f"f={step.f:.1f}")
        parts.append(f"g={step.g}")
        if step.frontier_size > 0:
            parts.append(f"F={step.frontier_size}")
        if step.reached_size > 0:
            parts.append(f"R={step.reached_size}")
        lines.append(f"{indent} {' | '.join(parts)}")

    st.code("\n".join(lines), language="")
    if len(trace) > max_nodes:
        st.caption(f"Showing first {max_nodes} of {len(trace)} nodes")


def process_uploaded_image(image_file, grid_size: int = 4):
    """Process an uploaded image into tile pieces.

    Args:
        image_file: Uploaded image file from st.file_uploader
        grid_size: Grid dimension (default 4 for 15-puzzle)

    Returns:
        dict mapping tile values (1-15) to base64 data URLs, or empty dict if failed
    """
    try:
        from PIL import Image
        import io
        import base64

        img = Image.open(image_file)
        img = img.convert("RGBA")

        # Make square
        w, h = img.size
        size = min(w, h)
        left = (w - size) // 2
        top = (h - size) // 2
        img = img.crop((left, top, left + size, top + size))

        # Resize to grid_size * tile_size
        tile_size = 70  # Match CSS puzzle cell size
        img = img.resize((grid_size * tile_size, grid_size * tile_size), Image.Resampling.LANCZOS)

        tiles = {}
        for val in range(1, grid_size * grid_size):
            row = (val - 1) // grid_size
            col = (val - 1) % grid_size
            tile = img.crop((col * tile_size, row * tile_size, (col + 1) * tile_size, (row + 1) * tile_size))

            buffer = io.BytesIO()
            tile.save(buffer, format="PNG")
            b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
            tiles[val] = f"data:image/png;base64,{b64}"

        return tiles
    except Exception as e:
        import logging
        logging.warning(f"process_uploaded_image failed: {e}")
        return {}