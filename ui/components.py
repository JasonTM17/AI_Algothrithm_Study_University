"""UI Components for 15-Puzzle AI Streamlit app — Enhanced game-like experience."""

import streamlit as st
import pandas as pd
from core.comparison import compact_action_path, shared_verified_paths, unique_verified_path_count
from core.puzzle import PuzzleState, GOAL_STATE, is_solvable
from core.utils import format_state_grid
from ui.styles import STYLES, GROUP_COLORS
from ui.localization import LOC


def t(key, **kwargs):
    global_lang = st.session_state.get("global_lang_select", "Tiếng Việt")
    text = LOC[global_lang].get(key, key)
    if kwargs:
        return text.format(**kwargs)
    return text


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
    """Return the blank-move direction that slides tile_idx into blank.

    _move_blank expects blank-centric actions: 'L' = blank moves left.
    So tile left of blank → blank moves 'L' (toward the tile).
    """
    blank_idx = state.index(0)
    if tile_idx == blank_idx - 1 and blank_idx % 4 != 0:
        return "L"  # tile is left of blank → blank moves left
    if tile_idx == blank_idx + 1 and tile_idx % 4 != 0:
        return "R"  # tile is right of blank → blank moves right
    if tile_idx == blank_idx - 4:
        return "U"  # tile is above blank → blank moves up
    if tile_idx == blank_idx + 4:
        return "D"  # tile is below blank → blank moves down
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
    with st.container():
        st.markdown('<div class="interactive-board-container-number"></div>', unsafe_allow_html=True)
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
                                type="primary", width="stretch",
                            )
                        else:
                            st.markdown(
                                f'<div class="{cls_str}">{val}</div>',
                                unsafe_allow_html=True,
                            )


def render_image_board(state: tuple, image_tiles: dict, key_prefix: str = "img",
                       highlight_correct: bool = True, on_click_fn=None,
                       show_numbers: bool = False):
    """Render interactive 4x4 board with image tiles and optional number overlay.

    Each tile shows the image piece. Blank tile is empty.
    Click behavior same as number board.

    Args:
        state: 16-element tuple
        image_tiles: dict mapping tile value (1-15) to base64 data URL
        key_prefix: unique key for Streamlit buttons
        highlight_correct: green border for tiles in goal position
        on_click_fn: callback function(direction) when a tile is clicked
        show_numbers: overlay a small number indicator on top-left of each tile
    """
    with st.container():
        st.markdown('<div class="interactive-board-container-image"></div>', unsafe_allow_html=True)
        for r in range(4):
            cols = st.columns(4, gap="small")
            for c in range(4):
                idx = r * 4 + c
                val = state[idx]
                with cols[c]:
                    if val == 0:
                        st.markdown(
                            '<div style="width:100%;aspect-ratio:1;border:1px dashed '
                            'rgba(214,196,166,0.14);border-radius:12px;'
                            'background:radial-gradient(circle at 50% 45%, rgba(214,161,95,0.08), transparent 55%), #080b0a;'
                            'box-shadow:inset 0 8px 16px rgba(0,0,0,0.74);">'
                            '</div>',
                            unsafe_allow_html=True,
                        )
                        st.button(f" ", key=f"{key_prefix}_blank_btn_{r}_{c}",
                                  disabled=True, width="stretch")
                    elif val in image_tiles:
                        is_correct = highlight_correct and val == GOAL_STATE[idx]
                        border_color = "#697d5f" if is_correct else "#b8793e"
                        
                        number_badge = ""
                        if show_numbers:
                            number_badge = (
                                f'<span style="position:absolute;top:6px;left:6px;z-index:9;'
                                f'background:rgba(8,11,10,0.88);color:#f4efe5;padding:2px 6px;'
                                f'border-radius:4px;font-size:11px;font-weight:700;line-height:1;'
                                f'border:1px solid rgba(214,161,95,0.34);box-shadow:0 2px 6px rgba(4,7,6,0.45);'
                                f'pointer-events:none;">{val}</span>'
                            )
                        
                        img_html = (
                            f'<div style="width:100%;aspect-ratio:1;border-radius:8px;'
                            f'overflow:hidden;border:4px solid {border_color};'
                            f'box-shadow:0 8px 18px rgba(4,7,6,0.52), inset 0 1px 2px rgba(255,255,255,0.18);'
                            f'cursor:pointer;position:relative;background:#080b0a;">'
                            f'{number_badge}'
                            f'<img src="{image_tiles[val]}" style="width:100%;height:100%;'
                            f'object-fit:cover;" alt="tile{val}">'
                            f'</div>'
                        )
                        if _is_adjacent_to_blank(state, idx) and on_click_fn:
                            direction = _get_slide_direction(state, idx)
                            dir_labels = {
                                "L": "Slide right",
                                "R": "Slide left",
                                "U": "Slide down",
                                "D": "Slide up",
                            }
                            label = dir_labels.get(direction, "Slide")
                            st.markdown(img_html, unsafe_allow_html=True)
                            st.button(label, key=f"{key_prefix}_hit_{val}_{r}_{c}",
                                      on_click=on_click_fn, args=(direction,),
                                      type="primary", width="stretch")
                        else:
                            st.markdown(img_html, unsafe_allow_html=True)
                            st.button(f" ", key=f"{key_prefix}_nohit_{val}_{r}_{c}",
                                      disabled=True, width="stretch")
                    else:
                        st.button(str(val), key=f"{key_prefix}_{val}_{r}_{c}",
                                  disabled=True, width="stretch")


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
        st.metric(t("mc_status"), f"{icon} {t('mc_solved') if success else t('mc_failed')}")
    with col2:
        st.metric(t("mc_path_len"), str(len(result.actions)) if success else "-")
    with col3:
        st.metric(t("mc_runtime"), f"{result.runtime:.4f}s")
    with col4:
        st.metric(t("mc_expanded"), str(result.nodes_expanded))

    col5, col6, col7, col8 = st.columns(4)
    with col5:
        st.metric(t("mc_cost"), str(result.cost) if success else "-")
    with col6:
        st.metric(t("mc_max_f"), str(result.max_frontier_size))
    with col7:
        st.metric(t("mc_reached_size"), str(result.reached_size))
    with col8:
        st.metric(t("mc_depth"), str(result.depth) if success else "-")

    evidence_status = "verified" if result.path_verified else "not verified"
    optimality_status = "proven for this run" if result.optimality_proven else "not proven for this run"
    st.caption(
        f"Run certificate: termination={result.termination_reason} · "
        f"legal path={evidence_status} · optimality={optimality_status}. "
        f"Theoretical complete/optimal properties apply only when their assumptions and resource limits hold."
    )

    if result.message:
        msg_cls = "result-success" if success else "result-failure"
        st.markdown(f'<div class="{msg_cls}">{result.message}</div>', unsafe_allow_html=True)


def render_trace_table(trace: list, max_rows: int = 100):
    """Render trace steps as a scrollable table."""
    if not trace:
        st.info(t("tc_no_trace"))
        return

    rows = []
    for step in trace[:max_rows]:
        row = {
            t("tc_step"): step.step,
            "Event": step.event,
            t("tc_action"): step.action or "-",
        }
        if step.g > 0:
            row["g(n)"] = step.g
        if step.h > 0 or step.step == 0:
            row["h(n)"] = f"{step.h:.1f}"
        if step.f > 0:
            row["f(n)"] = f"{step.f:.1f}"
        if step.frontier_size > 0:
            row[t("tc_frontier")] = step.frontier_size
        if step.reached_size > 0:
            row[t("tc_reached")] = step.reached_size
        if step.temperature is not None:
            row[t("tc_temp")] = f"{step.temperature:.4f}"
        if step.probability is not None:
            row[t("tc_prob")] = f"{step.probability:.4f}"
        if step.accepted is not None:
            row[t("tc_accepted")] = t("tc_yes") if step.accepted else t("tc_no")
        if step.belief_size is not None:
            row[t("tc_belief")] = step.belief_size
        if step.node_type:
            row[t("tc_type")] = step.node_type
        if step.reason:
            row[t("tc_reason")] = step.reason[:60]
        rows.append(row)

    if len(trace) > max_rows:
        st.caption(t("tc_showing", curr=max_rows, total=len(trace)))

    df = pd.DataFrame(rows)
    st.dataframe(df, width="stretch", height=300)


def _state_to_mini_grid(state: tuple) -> str:
    """Return a compact HTML mini-grid for a puzzle state."""
    cells = []
    for i, v in enumerate(state):
        if v == 0:
            cells.append('<span class="mc b">_</span>')
        elif v == GOAL_STATE[i]:
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
        st.info(t("tc_no_trace"))
        return

    has_detail = any(
        hasattr(s, 'node_state') and s.node_state is not None
        for s in trace[:max_rows]
    )
    if not has_detail:
        st.info(t("det_no_detail"))
        return

    step_idx = st.slider(
        t("det_slider"), 0, min(len(trace) - 1, max_rows - 1), 0,
        key="detail_step_slider"
    )

    step = trace[step_idx]

    st.markdown(f"**{t('tc_step')} {step.step}** | {t('tc_action')}: `{step.action or 'Start'}` | "
                f"g={step.g} h={step.h:.1f} f={step.f:.1f}")

    col1, col2, col3 = st.columns([1, 2, 2])

    with col1:
        st.markdown(f"**{t('det_curr_node')}**")
        if step.node_state:
            render_puzzle_board(step.node_state, size="small")
        else:
            render_puzzle_board(step.state, size="small")

    with col2:
        st.markdown(f"**{t('tc_frontier')}** ({step.frontier_size} states)")
        if step.frontier_states and len(step.frontier_states) > 0:
            frontier_display = step.frontier_states[:6]
            for i, fs in enumerate(frontier_display):
                st.markdown(_state_to_mini_grid(fs), unsafe_allow_html=True)
            if len(step.frontier_states) > 6:
                st.caption(t("det_more", count=len(step.frontier_states) - 6))
        else:
            st.caption(t("det_empty"))

    with col3:
        st.markdown(f"**{t('tc_reached')}** ({step.reached_size} states)")
        if step.reached_states and len(step.reached_states) > 0:
            reached_display = step.reached_states[:6]
            for i, rs in enumerate(reached_display):
                st.markdown(_state_to_mini_grid(rs), unsafe_allow_html=True)
            if len(step.reached_states) > 6:
                st.caption(t("det_more", count=len(step.reached_states) - 6))
        else:
            st.caption(t("det_not_captured"))


def render_path_animation(path: list[tuple], actions: list[str], key: str = "path"):
    """Render path animation with auto-play, step slider, and speed control."""
    if not path or len(path) < 2:
        if path and len(path) == 1:
            render_puzzle_board(path[0])
            st.caption(t("anim_already_goal"))
        return

    st.markdown("---")
    st.subheader(t("anim_title"))

    # Auto-play controls
    auto_key = f"{key}_autoplay"
    speed_key = f"{key}_speed"

    col_play, col_speed, col_step = st.columns([1, 2, 3])

    with col_play:
        if st.session_state.get(auto_key, False):
            if st.button(t("play_stop_run"), key=f"{key}_stop_btn", type="secondary"):
                st.session_state[auto_key] = False
                st.rerun()
        else:
            if st.button(t("play_auto_run"), key=f"{key}_play_btn", type="primary"):
                st.session_state[auto_key] = True
                st.session_state[f"{key}_auto_step"] = st.session_state.get(f"{key}_slider", 0)
                st.rerun()

    with col_speed:
        speed_options = {
            t("anim_per_step", sec=value): value
            for value in (0.1, 0.3, 0.5, 1.0, 2.0)
        }
        speed_label = st.selectbox(
            t("anim_speed"), list(speed_options), index=2, key=speed_key,
        )
        speed = speed_options[speed_label]

    current_step = st.slider(
        t("play_curr_step"), 0, len(path) - 1, 0, key=f"{key}_slider"
    )

    # Show current state
    render_puzzle_board(path[current_step])

    direction_map = {
        "L": t("dir_L").split(" ")[0],
        "R": t("dir_R").split(" ")[0],
        "U": t("dir_U").split(" ")[0],
        "D": t("dir_D").split(" ")[0],
    }
    if current_step == 0:
        action_display = "Start"
    else:
        action_display = actions[current_step - 1]
    display = direction_map.get(action_display, action_display)
    goal_suffix = f" · {t('anim_goal')}" if current_step == len(path) - 1 else ""
    st.caption(f"Step {current_step}/{len(path)-1}: {display}{goal_suffix}")

    # Navigation buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button(t("anim_prev"), key=f"{key}_prev"):
            st.session_state[f"{key}_slider"] = max(0, current_step - 1)
    with col2:
        if st.button(t("anim_next"), key=f"{key}_next"):
            st.session_state[f"{key}_slider"] = min(len(path) - 1, current_step + 1)
    with col3:
        if st.button(t("anim_reset"), key=f"{key}_reset"):
            st.session_state[f"{key}_slider"] = 0
            st.session_state[auto_key] = False
            st.session_state[f"{key}_auto_step"] = 0

    if st.session_state.get(auto_key, False):
        current_auto = st.session_state.get(f"{key}_auto_step", 0)
        if current_auto < len(path) - 1:
            import time
            st.session_state[f"{key}_slider"] = current_auto + 1
            st.session_state[f"{key}_auto_step"] = current_auto + 1
            time.sleep(speed)
            st.rerun()
        else:
            st.session_state[auto_key] = False
            st.session_state[f"{key}_auto_step"] = 0
            st.success(t("anim_complete"))


def render_comparison_table(results: list):
    """Render comparison table for benchmark results."""
    global_lang = st.session_state.get("global_lang_select", "Tiếng Việt")
    if not results:
        st.info(t("compare_no_data"))
        return

    rows = []
    for r in results:
        group_trans = r.group
        if global_lang == "Tiếng Việt":
            if r.group == "Uninformed Search": group_trans = "Tìm kiếm mù"
            elif r.group == "Informed Search": group_trans = "Tìm kiếm có thông tin"
            elif r.group == "Local Search": group_trans = "Tìm kiếm cục bộ"
            elif r.group == "Complex Environments": group_trans = "Môi trường phức tạp"
            elif r.group == "CSP": group_trans = "Thỏa mãn ràng buộc"
            elif r.group == "Adversarial/Stochastic": group_trans = "Đối kháng/Ngẫu nhiên"
            
        row = {
            t("compare_group_col"): group_trans,
            t("run_algo"): r.algorithm,
            t("mc_status"): t("mc_solved") if r.success else t("mc_failed"),
            t("mc_path_len"): len(r.actions) if r.success else "-",
            "Action Path": compact_action_path(r.actions) if r.success else "-",
            t("mc_cost"): r.cost if r.success else "-",
            t("mc_expanded"): r.nodes_expanded,
            t("mc_max_f"): r.max_frontier_size,
            t("mc_runtime"): f"{r.runtime:.4f}",
            "Seed / Mode": r.random_seed if r.random_seed is not None else "Deterministic",
            f"{t('compare_optimal_col')} (theory)": t("tc_yes") if r.is_optimal else t("tc_no"),
            f"{t('compare_complete_col')} (theory)": t("tc_yes") if r.is_complete else t("tc_no"),
            "Run optimality proven": t("tc_yes") if r.optimality_proven else t("tc_no"),
            "Termination": r.termination_reason,
        }
        rows.append(row)

    df = pd.DataFrame(rows)
    st.dataframe(df, width="stretch", hide_index=True)

    if len([r for r in results if r.success]) > 1:
        successful = [r for r in results if r.success]
        fastest = min(successful, key=lambda x: x.runtime)
        shortest = min(successful, key=lambda x: len(x.actions))
        max_mem = max(successful, key=lambda x: x.nodes_expanded)

        st.markdown(f"### {t('compare_analysis')}")
        st.markdown(f"- {t('compare_fastest', algo=fastest.algorithm, time=fastest.runtime)}")
        st.markdown(f"- {t('compare_shortest', algo=shortest.algorithm, steps=len(shortest.actions))}")
        if max_mem.algorithm != min(successful, key=lambda x: x.nodes_expanded).algorithm:
            st.markdown(f"- {t('compare_most_memory', algo=max_mem.algorithm, nodes=max_mem.nodes_expanded)}")

        verified_count = len([r for r in successful if r.path_verified])
        unique_count = unique_verified_path_count(successful)
        st.caption(
            f"Verified path evidence: {unique_count} unique trajectory/trajectories "
            f"across {verified_count} certified successful run(s)."
        )
        for algorithms in shared_verified_paths(successful):
            st.info(
                "Shared verified solution path: " + ", ".join(algorithms) + ". "
                "This can be academically correct: with unit-cost moves and the same action order, "
                "multiple optimal algorithms may select the same optimal solution while expanding "
                "different frontiers and using different memory."
            )


def render_algorithm_info(algo_name: str, theory: dict):
    """Render algorithm theory information."""
    global_lang = st.session_state.get("global_lang_select", "Tiếng Việt")
    if not theory:
        st.info(t("theory_coming_soon", algo=algo_name))
        return

    group = theory.get("group", "")
    group_style = GROUP_COLORS.get(group, {})

    st.markdown(f"### {theory.get('name', algo_name)}")

    group_display = group
    if global_lang == "Tiếng Việt":
        if group == "Uninformed Search": group_display = "Tìm kiếm mù"
        elif group == "Informed Search": group_display = "Tìm kiếm có thông tin"
        elif group == "Local Search": group_display = "Tìm kiếm cục bộ"
        elif group == "Complex Environments": group_display = "Môi trường phức tạp"
        elif group == "CSP": group_display = "Thỏa mãn ràng buộc"
        elif group == "Adversarial/Stochastic": group_display = "Đối kháng/Ngẫu nhiên"

    badge_cls = group_style.get("badge", "")
    if badge_cls:
        st.markdown(f'<span class="group-badge {badge_cls}">{group_display}</span>', unsafe_allow_html=True)

    props = []
    suitable_key = "suitable_en" if global_lang == "English" and "suitable_en" in theory else "suitable"
    suitable_val = theory.get(suitable_key)
    if suitable_val:
        if "RẤT" in suitable_val or "rất" in suitable_val.lower() or "highly" in suitable_val.lower():
            props.append(("Phù hợp" if global_lang == "Tiếng Việt" else "Suitable", "#06d6a0"))
        elif "KHÔNG" in suitable_val or "không" in suitable_val.lower() or "not" in suitable_val.lower():
            props.append(("Không phù hợp" if global_lang == "Tiếng Việt" else "Not suitable", "#ef476f"))
        else:
            props.append(("Hạn chế" if global_lang == "Tiếng Việt" else "Limited", "#ffd166"))

    for label, color in props:
        st.markdown(f'<span style="background:{color};color:#fff;padding:2px 10px;border-radius:12px;font-size:12px;font-weight:600;">{label}</span>', unsafe_allow_html=True)

    sections = [
        ("Mục tiêu" if global_lang == "Tiếng Việt" else "Goal", "goal"),
        ("Ý tưởng" if global_lang == "Tiếng Việt" else "Idea", "idea"),
        ("Cấu trúc dữ liệu" if global_lang == "Tiếng Việt" else "Data Structure", "data_structure"),
        ("Công thức" if global_lang == "Tiếng Việt" else "Formula", "formula"),
        ("Áp dụng 15-Puzzle" if global_lang == "Tiếng Việt" else "15-Puzzle Application", "application"),
        ("Phù hợp 15-Puzzle?" if global_lang == "Tiếng Việt" else "Suitable for 15-Puzzle?", "suitable"),
        ("Ưu điểm" if global_lang == "Tiếng Việt" else "Pros", "pros"),
        ("Nhược điểm" if global_lang == "Tiếng Việt" else "Cons", "cons"),
        ("Độ phức tạp" if global_lang == "Tiếng Việt" else "Complexity", "complexity"),
        ("Ví dụ chạy tệ" if global_lang == "Tiếng Việt" else "Worst-case Example", "bad_example"),
        ("So sánh" if global_lang == "Tiếng Việt" else "Comparison", "comparison"),
        ("Điểm cần nhớ khi thi" if global_lang == "Tiếng Việt" else "Exam Tips", "exam_tips"),
    ]

    for title, key in sections:
        content_key = f"{key}_en" if global_lang == "English" and f"{key}_en" in theory else key
        content = theory.get(content_key)
        if content:
            if isinstance(content, list):
                content = "\n".join(f"- {item}" for item in content)
            st.markdown(f"**{title}**\n\n{content}")

    pseudocode_key = "pseudocode_en" if global_lang == "English" and "pseudocode_en" in theory else "pseudocode"
    pseudocode = theory.get(pseudocode_key)
    if pseudocode:
        st.markdown("**Pseudocode**")
        st.code(pseudocode, language="python")


def render_search_tree(result, max_nodes: int = 40):
    """Render only verified parent-child transitions as a directed graph."""
    from core.metrics import search_tree_to_dot

    if not result.search_tree_nodes or not result.search_tree_edges:
        st.info(t("tc_no_trace"))
        return

    st.markdown(f"### {t('run_search_tree')}")
    st.caption(
        "Every edge is backed by a legal puzzle action. Green nodes and edges "
        "show the verified legal result path; the remaining nodes are explored evidence."
    )
    st.graphviz_chart(search_tree_to_dot(result, max_nodes), width="stretch")
    if len(result.search_tree_nodes) > max_nodes:
        st.caption(
            f"Showing {max_nodes}/{len(result.search_tree_nodes)} recorded nodes. "
            "The visualization is bounded to keep the web page responsive."
        )
    if result.trace_truncated:
        st.warning("Trace display reached its capture limit; run metrics still cover the solver run.")


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

def render_algorithm_evaluation(algo_name: str):
    """Render a dedicated academic evaluation table for the selected algorithm."""
    from ui.styles import THEORY_KEY_MAP, COMPARISON_TABLE
    from core.theory import THEORY
    import pandas as pd

    global_lang = st.session_state.get("global_lang_select", "Tiếng Việt")
    is_eng = (global_lang == "English")

    theory_key = THEORY_KEY_MAP.get(algo_name, algo_name)
    theory_data = THEORY.get(theory_key)

    # Find the algorithm row in COMPARISON_TABLE
    row_data = None
    for row in COMPARISON_TABLE:
        if row["Algorithm"].lower() in algo_name.lower() or algo_name.lower() in row["Algorithm"].lower():
            row_data = row
            break
    # Fallback search
    if not row_data and theory_data:
        for row in COMPARISON_TABLE:
            if row["Group"].lower() in theory_data.get("group", "").lower():
                row_data = row
                break

    st.markdown("---")
    st.markdown(f"### {t('eval_title')}")
    
    if row_data and theory_data:
        # Get complexities
        comp_key = "complexity_en" if is_eng and "complexity_en" in theory_data else "complexity"
        comp_str = theory_data.get(comp_key, "N/A")
        time_comp = "N/A"
        space_comp = "N/A"
        if "," in comp_str:
            parts = comp_str.split(",")
            for p in parts:
                if "thời gian" in p.lower() or "time" in p.lower() or "trước" in p.lower():
                    time_comp = p.replace("Thời gian:", "").replace("time:", "").replace("Time:", "").strip()
                elif "bộ nhớ" in p.lower() or "space" in p.lower() or "memory" in p.lower():
                    space_comp = p.replace("Bộ nhớ:", "").replace("space:", "").replace("Space:", "").strip()
        else:
            time_comp = comp_str

        def translate_comp_val(val, lang):
            if lang == "Tiếng Việt":
                trans = {
                    "Yes": "Có",
                    "No": "Không",
                    "Yes*": "Có*",
                    "Limited (memory)": "Hạn chế (bộ nhớ)",
                    "Same as BFS": "Giống BFS",
                    "Good (low memory)": "Tốt (ít bộ nhớ)",
                    "Fast, suboptimal": "Nhanh, không tối ưu",
                    "Best choice": "Lựa chọn tốt nhất",
                    "Memory efficient": "Tiết kiệm bộ nhớ",
                    "Gets stuck": "Bị kẹt",
                    "Asymptotic": "Tiệm cận",
                    "May find solution": "Có thể tìm lời giải",
                    "Better than HC": "Tốt hơn HC",
                    "Unreliable": "Không đáng tin",
                    "Nondeterministic": "Không xác định",
                    "Academic": "Học thuật",
                    "Online learning": "Học trực tuyến",
                    "Online demo": "Minh họa online",
                    "Extended env": "Môi trường mở rộng",
                    "Planning demo": "Minh họa planning",
                    "Game demo": "Minh họa game tree",
                    "Pruning demo": "Minh họa cắt tỉa",
                    "Stochastic demo": "Minh họa ngẫu nhiên",
                    "Illustrative": "Minh họa",
                    "Not standard": "Không chuẩn",
                    "N-Queens better": "N-Queens tốt hơn",
                    "2-player game": "Trò chơi 2 người",
                    "2-player (faster)": "Trò chơi 2 người (nhanh hơn)",
                    "Stochastic env": "Môi trường ngẫu nhiên",
                    "-": "-"
                }
                return trans.get(val, val)
            return val

        # Create properties table
        properties = {
            t("eval_prop"): [
                t("eval_complete"),
                t("eval_optimal"),
                t("eval_time"),
                t("eval_space"),
                t("eval_suit")
            ],
            t("eval_val"): [
                translate_comp_val(row_data.get("Complete", "N/A"), global_lang),
                translate_comp_val(row_data.get("Optimal", "N/A"), global_lang),
                time_comp,
                space_comp,
                translate_comp_val(row_data.get("Suitable", "N/A"), global_lang)
            ]
        }
        df = pd.DataFrame(properties)
        st.table(df)
        
        # Render Pros & Cons
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**{t('eval_pros')}**")
            pros_key = "pros_en" if is_eng and "pros_en" in theory_data else "pros"
            for pro in theory_data.get(pros_key, ["N/A"]):
                st.markdown(f"- {pro}")
        with col2:
            st.markdown(f"**{t('eval_cons')}**")
            cons_key = "cons_en" if is_eng and "cons_en" in theory_data else "cons"
            for con in theory_data.get(cons_key, ["N/A"]):
                st.markdown(f"- {con}")
                
        # Render Exam Tips
        tips_key = "exam_tips_en" if is_eng and "exam_tips_en" in theory_data else "exam_tips"
        if theory_data.get(tips_key):
            st.info(f"{t('eval_tips')}: {theory_data.get(tips_key)}")
    else:
        st.info(t("eval_not_found"))
