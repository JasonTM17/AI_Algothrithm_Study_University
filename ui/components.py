"""UI Components for 15-Puzzle AI Streamlit app — Enhanced game-like experience."""

from html import escape

import streamlit as st
import pandas as pd
from core.comparison import compact_action_path, shared_verified_paths, unique_verified_path_count
from core.puzzle import PuzzleState, GOAL_STATE, is_solvable
from core.utils import format_state_grid
from ui.styles import STYLES, GROUP_COLORS
from ui.localization import VIETNAMESE, resolve_language, translate


def t(key, **kwargs):
    global_lang = st.session_state.get("global_lang_select", VIETNAMESE)
    return translate(global_lang, key, **kwargs)


GROUP_LABEL_KEYS = {
    "Uninformed Search": "group_uninformed",
    "Informed Search": "group_informed",
    "Local Search": "group_local",
    "Complex Environments": "group_complex",
    "CSP": "group_csp",
    "AI-vs-AI Tournament": "group_ai_vs_ai",
}


def _current_language() -> str:
    return resolve_language(st.session_state.get("global_lang_select", VIETNAMESE))


def _localized_group_name(group: str) -> str:
    key = GROUP_LABEL_KEYS.get(group)
    return t(key) if key else group


def render_styles():
    """Inject custom CSS styles."""
    st.markdown(STYLES, unsafe_allow_html=True)


def _active_goal_state(goal: tuple | None = None) -> tuple:
    """Return the comparison goal used by the current UI render."""
    return goal or st.session_state.get("goal_state", GOAL_STATE)


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
                           on_click_fn=None, goal: tuple | None = None):
    """Render interactive 4x4 puzzle board with game-like 3D tile design.

    Uses HTML grid for visuals + Streamlit columns/buttons for interaction.
    Tiles have row-based gradients, 3D shadows, checkerboard blank, hover lift.

    Args:
        state: 16-element tuple
        key_prefix: unique key for Streamlit buttons
        highlight_correct: green highlight for tiles in goal position
        on_click_fn: callback function(direction) when a tile is clicked
    """
    goal_state = _active_goal_state(goal)
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
                        if highlight_correct and val == goal_state[idx]:
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


def _image_tile_button_style(button_key: str, image_src: str, show_numbers: bool) -> str:
    label_visibility = "flex" if show_numbers else "none"
    text_color = "#f4efe5" if show_numbers else "transparent"
    button_scope = f"div.st-key-{button_key} button"
    return f"""
    {button_scope} {{
        position: relative !important;
        width: 100% !important;
        aspect-ratio: 1 / 1 !important;
        height: auto !important;
        min-height: 44px !important;
        padding: 7px !important;
        align-items: flex-start !important;
        justify-content: flex-start !important;
        border: 3px solid rgba(239,196,119,0.98) !important;
        border-radius: 8px !important;
        background:
            linear-gradient(135deg, rgba(255,255,255,0.16), transparent 24%),
            linear-gradient(0deg, rgba(0,0,0,0.22), transparent 46%),
            url("{image_src}") center / cover no-repeat !important;
        box-shadow:
            0 14px 24px rgba(0,0,0,0.42),
            0 0 0 2px rgba(214,161,95,0.15),
            inset 0 1px 0 rgba(255,255,255,0.12) !important;
        color: {text_color} !important;
        cursor: pointer !important;
        overflow: hidden !important;
        transform: translateZ(0) !important;
        touch-action: manipulation !important;
        transition: transform 150ms ease, box-shadow 150ms ease, border-color 150ms ease, filter 150ms ease !important;
    }}
    {button_scope}:hover:not(:disabled) {{
        transform: translateY(-4px) scale(1.015) !important;
        border-color: rgba(239,196,119,0.98) !important;
        filter: saturate(1.08) brightness(1.05) !important;
    }}
    {button_scope}:active:not(:disabled) {{
        transform: translateY(1px) scale(0.99) !important;
    }}
    {button_scope} p,
    {button_scope} div,
    {button_scope} span {{
        margin: 0 !important;
        padding: 0 !important;
        border: 0 !important;
        background: transparent !important;
        box-shadow: none !important;
        color: inherit !important;
        font: inherit !important;
    }}
    {button_scope} p {{
        position: absolute !important;
        top: 7px !important;
        left: 7px !important;
        display: {label_visibility} !important;
        width: auto !important;
        padding: 2px 7px !important;
        border: 1px solid rgba(214,161,95,0.42) !important;
        border-radius: 5px !important;
        background: rgba(3,6,5,0.84) !important;
        color: #f4efe5 !important;
        font-family: var(--font-mono) !important;
        font-size: 12px !important;
        font-weight: 850 !important;
        line-height: 1.25 !important;
        text-align: center !important;
        box-shadow: 0 2px 6px rgba(4,7,6,0.45) !important;
    }}
    """


def render_image_board(state: tuple, image_tiles: dict, key_prefix: str = "img",
                       highlight_correct: bool = True, on_click_fn=None,
                       show_numbers: bool = False, action_labels: dict[str, str] | None = None,
                       goal: tuple | None = None):
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
    goal_state = _active_goal_state(goal)
    dynamic_styles = []
    st.markdown('<div class="interactive-board-container-image"></div>', unsafe_allow_html=True)
    st.markdown('<div id="play-board" class="play-board-anchor"></div>', unsafe_allow_html=True)
    with st.container():
        for r in range(4):
            cols = st.columns(4, gap="small")
            for c in range(4):
                idx = r * 4 + c
                val = state[idx]
                with cols[c]:
                    if val == 0:
                        st.markdown(
                            '<div class="play-image-cell play-image-cell-blank"></div>',
                            unsafe_allow_html=True,
                        )
                        continue

                    if val not in image_tiles:
                        st.markdown(
                            f'<div class="play-image-cell play-image-cell-missing">{escape(str(val))}</div>',
                            unsafe_allow_html=True,
                        )
                        continue

                    is_correct = highlight_correct and val == goal_state[idx]
                    is_clickable = _is_adjacent_to_blank(state, idx) and on_click_fn
                    classes = ["play-image-cell"]
                    if is_correct:
                        classes.append("is-correct")
                    if is_clickable:
                        classes.append("is-clickable")

                    if is_clickable:
                        direction = _get_slide_direction(state, idx)
                        dir_labels = action_labels or {
                            "L": "Slide right",
                            "R": "Slide left",
                            "U": "Slide down",
                            "D": "Slide up",
                        }
                        button_key = f"{key_prefix}_hit_{val}_{r}_{c}"
                        dynamic_styles.append(_image_tile_button_style(button_key, image_tiles[val], show_numbers))
                        st.button(
                            str(val) if show_numbers else dir_labels.get(direction, "Slide"),
                            key=button_key,
                            on_click=on_click_fn,
                            args=(direction,),
                            help=dir_labels.get(direction, "Slide"),
                            width="stretch",
                        )
                    else:
                        number_badge = f'<span class="play-tile-number">{val}</span>' if show_numbers else ""
                        st.markdown(
                            f'<div class="{" ".join(classes)}">'
                            f'{number_badge}<span class="play-tile-shine"></span>'
                            f'<img src="{image_tiles[val]}" alt="tile{val}" draggable="false">'
                            '</div>',
                            unsafe_allow_html=True,
                        )
    if dynamic_styles:
        st.markdown(f"<style>{''.join(dynamic_styles)}</style>", unsafe_allow_html=True)


def render_puzzle_board(
    state: tuple,
    highlight_correct: bool = True,
    size: str = "normal",
    goal: tuple | None = None,
):
    """Render 4x4 puzzle board as HTML with game-like styling.

    Args:
        state: 16-element tuple representing the puzzle state
        highlight_correct: Whether to highlight tiles in goal position (green)
        size: 'normal' (70px cells) or 'small' (50px cells) or 'mini' (28px cells)
    """
    cell_size = {"normal": 70, "small": 50, "mini": 28}[size]
    font_size = {"normal": 22, "small": 16, "mini": 10}[size]

    goal_state = _active_goal_state(goal)
    cells = []
    for i, val in enumerate(state):
        if val == 0:
            cells.append(
                f'<div class="puzzle-cell blank" style="width:{cell_size}px;height:{cell_size}px;'
                f'font-size:{font_size}px;">_</div>'
            )
        else:
            correct = (val == goal_state[i]) if highlight_correct else False
            cls = "correct" if correct else "filled"
            cells.append(
                f'<div class="puzzle-cell {cls}" style="width:{cell_size}px;height:{cell_size}px;'
                f'font-size:{font_size}px;"><span class="tile-number">{val}</span></div>'
            )

    html = f'<div class="puzzle-grid">{"".join(cells)}</div>'
    st.markdown(html, unsafe_allow_html=True)


def render_puzzle_with_image(
    state: tuple,
    image_tiles: dict,
    highlight_correct: bool = True,
    goal: tuple | None = None,
):
    """Render 4x4 puzzle board with image tiles overlaid on numbers.

    Args:
        state: 16-element tuple representing the puzzle state
        image_tiles: dict mapping tile value (1-15) to base64-encoded image data URL
        highlight_correct: Whether to highlight tiles in goal position
    """
    goal_state = _active_goal_state(goal)
    cells = []
    for i, val in enumerate(state):
        if val == 0:
            cells.append(
                '<div class="puzzle-cell blank" style="width:70px;height:70px;font-size:22px;">_</div>'
            )
        else:
            correct = (val == goal_state[i]) if highlight_correct else False
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


def render_puzzle_row(
    states: list[tuple],
    labels: list[str] = None,
    max_cols: int = 5,
    goal: tuple | None = None,
):
    """Render multiple puzzle states in a row."""
    if not states:
        return

    cols = st.columns(min(len(states), max_cols))
    for i, (col, state) in enumerate(zip(cols, states)):
        with col:
            if labels and i < len(labels):
                st.caption(labels[i])
            render_puzzle_board(state, goal=goal)


def render_start_goal_contract(start: tuple, goal: tuple, solvable: bool) -> None:
    """Show the active start/goal pair shared by the current algorithm surface."""
    st.markdown(f"### {t('active_contract_title')}")
    st.caption(t("active_contract_caption"))
    col_start, col_goal, col_status = st.columns([1, 1, 1])
    with col_start:
        st.caption(t("active_start"))
        render_puzzle_board(start, size="small", goal=goal)
    with col_goal:
        st.caption(t("active_goal"))
        render_puzzle_board(goal, highlight_correct=False, size="small", goal=goal)
    with col_status:
        st.metric(
            t("active_solvability"),
            t("active_solvable") if solvable else t("active_unsolvable"),
        )
        st.caption(t("active_solvability_caption"))


def render_run_variation_metadata(result) -> None:
    """Show the randomized run controls that produced this result."""
    seed = getattr(result, "random_seed", None)
    action_order = getattr(result, "variation_action_order", None)
    tie_breaker = getattr(result, "variation_tie_breaker", None)
    solver_seed = getattr(result, "variation_solver_seed", None)
    randomizes_path = getattr(result, "variation_randomizes_path", True)

    if seed is None and action_order is None and tie_breaker is None:
        return

    st.caption(
        t(
            "run_variation_caption",
            seed=seed if seed is not None else "-",
            action_order=action_order or "-",
            tie_breaker=tie_breaker or "-",
        )
    )
    if solver_seed is not None:
        st.caption(t("run_variation_solver_seed", seed=solver_seed))
    if not randomizes_path:
        st.info(t("run_variation_no_path"))


def render_result_metrics(result):
    """Render search result as metric cards."""
    if result is None:
        return

    col1, col2, col3, col4 = st.columns(4)
    success = result.success
    icon = "OK" if success else "FAIL"
    status_text = (
        t("mc_solved")
        if success and result.goal_reached
        else (t("mc_model_success") if success else t("mc_failed"))
    )

    with col1:
        st.metric(t("mc_status"), f"{icon} {status_text}")
    with col2:
        st.metric(t("mc_recorded_steps"), str(len(result.actions)) if result.path_verified else "-")
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

    cert_cols = st.columns(4)
    with cert_cols[0]:
        st.metric(t("mc_legal_path"), t("tc_yes") if result.path_verified else t("tc_no"))
    with cert_cols[1]:
        st.metric(t("mc_reached_goal"), t("tc_yes") if result.goal_reached else t("tc_no"))
    with cert_cols[2]:
        st.metric(t("mc_optimality_proven"), t("tc_yes") if result.optimality_proven else t("tc_no"))
    with cert_cols[3]:
        st.metric(t("mc_termination"), result.termination_reason or "-")

    model_evidence = next(
        (
            step
            for step in reversed(result.trace)
            if step.belief_size is not None or step.observation
        ),
        None,
    )
    if model_evidence is not None:
        evidence_cols = st.columns(2)
        with evidence_cols[0]:
            st.metric(
                t("mc_belief_size"),
                str(model_evidence.belief_size)
                if model_evidence.belief_size is not None
                else "-",
            )
        with evidence_cols[1]:
            st.metric(t("tc_observation"), model_evidence.observation or "-")

    evidence_status = t("run_cert_verified") if result.path_verified else t("run_cert_not_verified")
    optimality_status = (
        t("run_cert_optimality_proven")
        if result.optimality_proven
        else t("run_cert_optimality_not_proven")
    )
    st.caption(
        t(
            "run_certificate_caption",
            termination=result.termination_reason or "-",
            legal_path=evidence_status,
            optimality=optimality_status,
        )
    )

    if result.message:
        msg_cls = "result-success" if success else "result-failure"
        st.markdown(f'<div class="{msg_cls}">{result.message}</div>', unsafe_allow_html=True)


def render_trace_table(trace: list, max_rows: int = 100):
    """Render trace steps as a scrollable table."""
    if not trace:
        st.info(t("tc_no_trace"))
        return

    labels, details = _trace_state_catalog(trace[:max_rows])
    rows = []
    for step in trace[:max_rows]:
        row = {
            t("tc_step"): step.step,
            "Event": step.event,
            t("tc_node"): _format_trace_state(
                step.state, labels, details, include_parent=True,
            ),
            t("tc_parent"): _format_trace_state(
                getattr(step, "node_state", None), labels, details,
            ),
            t("tc_action"): step.action or "-",
        }
        if step.g is not None and step.g > 0:
            row["g(n)"] = step.g
        if step.h is not None and (step.h > 0 or step.step == 0):
            row["h(n)"] = f"{step.h:.1f}"
        if step.f is not None and step.f > 0:
            row["f(n)"] = f"{step.f:.1f}"
        if step.frontier_states:
            row[t("tc_frontier")] = _format_trace_state_list(
                step.frontier_states, labels, details,
            )
        elif step.frontier_size is not None and step.frontier_size > 0:
            row[t("tc_frontier")] = step.frontier_size
        if step.reached_states:
            row[t("tc_reached")] = _format_trace_state_list(
                step.reached_states, labels, details,
            )
        elif step.reached_size is not None and step.reached_size > 0:
            row[t("tc_reached")] = step.reached_size
        if step.frontier_size is not None and step.frontier_size > 0:
            row[t("tc_frontier_size")] = step.frontier_size
        if step.reached_size is not None and step.reached_size > 0:
            row[t("tc_reached_size")] = step.reached_size
        if step.temperature is not None:
            row[t("tc_temp")] = f"{step.temperature:.4f}"
        if step.probability is not None:
            row[t("tc_prob")] = f"{step.probability:.4f}"
        if step.accepted is not None:
            row[t("tc_accepted")] = t("tc_yes") if step.accepted else t("tc_no")
        if step.belief_size is not None:
            row[t("tc_belief")] = step.belief_size
        if step.observation:
            row[t("tc_observation")] = step.observation
        if step.node_type:
            row[t("tc_type")] = step.node_type
        if step.reason:
            row[t("tc_reason")] = step.reason[:60]
        rows.append(row)

    if len(trace) > max_rows:
        st.caption(t("tc_showing", curr=max_rows, total=len(trace)))

    df = pd.DataFrame(rows)
    st.dataframe(df, width="stretch", height=300)


def _state_label(index: int) -> str:
    """Return spreadsheet-like labels: A..Z, A1..Z1, A2..."""
    letter = chr(ord("A") + (index % 26))
    suffix = "" if index < 26 else str(index // 26)
    return f"{letter}{suffix}"


def _is_puzzle_state(value: object) -> bool:
    return isinstance(value, tuple) and len(value) == 16 and set(value) == set(range(16))


def _trace_state_catalog(trace: list) -> tuple[dict[tuple, str], dict[tuple, dict[str, object]]]:
    """Build stable labels and first-known metrics for states appearing in a trace."""
    labels: dict[tuple, str] = {}
    details: dict[tuple, dict[str, object]] = {}

    def ensure_label(state: tuple | None) -> None:
        if _is_puzzle_state(state) and state not in labels:
            labels[state] = _state_label(len(labels))

    for step in trace:
        ensure_label(getattr(step, "node_state", None))
        ensure_label(getattr(step, "state", None))
        for state in getattr(step, "frontier_states", None) or []:
            ensure_label(state)
        for state in getattr(step, "reached_states", None) or []:
            ensure_label(state)

        state = getattr(step, "state", None)
        if _is_puzzle_state(state):
            details.setdefault(
                state,
                {
                    "action": step.action,
                    "g": step.g,
                    "h": step.h,
                    "f": step.f,
                    "parent": getattr(step, "node_state", None),
                    "event": step.event,
                },
            )

        parent = getattr(step, "node_state", None)
        if _is_puzzle_state(parent):
            details.setdefault(
                parent,
                {
                    "action": None,
                    "g": max(int(step.g or 0) - 1, 0),
                    "h": None,
                    "f": None,
                    "parent": None,
                    "event": "expand",
                },
            )
    return labels, details


def _metric_text(name: str, value: object) -> str | None:
    if value is None:
        return None
    if isinstance(value, float):
        return f"{name}={value:g}"
    return f"{name}={value}"


def _format_trace_state(
    state: tuple | None,
    labels: dict[tuple, str],
    details: dict[tuple, dict[str, object]],
    *,
    include_parent: bool = False,
) -> str:
    if not _is_puzzle_state(state):
        return "-"
    info = details.get(state, {})
    parts = [labels.get(state, "?")]
    action = info.get("action")
    if action:
        parts.append(str(action))
    for metric in ("g", "h", "f"):
        metric_part = _metric_text(metric, info.get(metric))
        if metric_part:
            parts.append(metric_part)
    if include_parent and _is_puzzle_state(info.get("parent")):
        parts.append(f"cha={labels.get(info['parent'], '?')}")
    return f"({', '.join(parts)})"


def _format_trace_state_list(
    states: list[tuple] | None,
    labels: dict[tuple, str],
    details: dict[tuple, dict[str, object]],
    limit: int = 6,
) -> str:
    if not states:
        return "-"
    shown = [
        _format_trace_state(state, labels, details)
        for state in states[:limit]
    ]
    if len(states) > limit:
        shown.append(f"... +{len(states) - limit}")
    return " ".join(shown)


def _state_to_mini_grid(state: tuple, goal: tuple | None = None) -> str:
    """Return a compact HTML mini-grid for a puzzle state."""
    goal_state = _active_goal_state(goal)
    cells = []
    for i, v in enumerate(state):
        if v == 0:
            cells.append('<span class="mc b">_</span>')
        elif v == goal_state[i]:
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

    max_step_index = min(len(trace) - 1, max_rows - 1)
    if max_step_index == 0:
        step_idx = 0
        st.caption(t("det_single_step"))
    else:
        step_idx = st.slider(
            t("det_slider"), 0, max_step_index, 0,
            key="detail_step_slider"
        )

    step = trace[step_idx]
    labels, details = _trace_state_catalog(trace[:max_rows])

    st.markdown(f"**{t('tc_step')} {step.step}** | {t('tc_action')}: `{step.action or 'Start'}` | "
                f"g={step.g} h={step.h:.1f} f={step.f:.1f}")

    col1, col2, col3 = st.columns([1, 2, 2])

    with col1:
        st.markdown(f"**{t('det_curr_node')}**")
        if step.node_state:
            render_puzzle_board(step.node_state, size="small")
        elif step.state:
            render_puzzle_board(step.state, size="small")
        else:
            st.caption(t("no_state"))

    with col2:
        st.markdown(f"**{t('tc_frontier')}** ({step.frontier_size} states)")
        if step.frontier_states and len(step.frontier_states) > 0:
            frontier_display = step.frontier_states[:6]
            for i, fs in enumerate(frontier_display):
                st.caption(_format_trace_state(fs, labels, details, include_parent=True))
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
                st.caption(_format_trace_state(rs, labels, details, include_parent=True))
                st.markdown(_state_to_mini_grid(rs), unsafe_allow_html=True)
            if len(step.reached_states) > 6:
                st.caption(t("det_more", count=len(step.reached_states) - 6))
        else:
            st.caption(t("det_not_captured"))


def _set_slider_step(slider_key: str, step: int, max_step: int) -> None:
    """Move a Streamlit slider by updating its key before the widget rerenders."""
    st.session_state[slider_key] = max(0, min(step, max_step))


def _reset_animation_slider(slider_key: str, auto_key: str, auto_step_key: str) -> None:
    """Reset animation controls without mutating a slider after instantiation."""
    st.session_state[slider_key] = 0
    st.session_state[auto_key] = False
    st.session_state[auto_step_key] = 0


def render_path_animation(
    path: list[tuple], actions: list[str], key: str = "path", *, reaches_goal: bool = True,
):
    """Render a recorded trajectory without inventing a goal claim for partial runs."""
    if not path or len(path) < 2:
        if path and len(path) == 1:
            render_puzzle_board(path[0])
            st.caption(t("anim_already_goal"))
        return

    st.markdown("---")
    st.subheader(t("anim_title"))

    # Auto-play controls
    auto_key = f"{key}_autoplay"
    auto_step_key = f"{key}_auto_step"
    slider_key = f"{key}_slider"
    speed_key = f"{key}_speed"
    max_step = len(path) - 1

    current_step = int(st.session_state.get(slider_key, 0))
    if current_step < 0 or current_step > max_step:
        current_step = max(0, min(current_step, max_step))
        st.session_state[slider_key] = current_step

    col_play, col_speed, col_step = st.columns([1, 2, 3])

    with col_play:
        if st.session_state.get(auto_key, False):
            if st.button(t("play_stop_run"), key=f"{key}_stop_btn", type="secondary"):
                st.session_state[auto_key] = False
                st.rerun()
        else:
            if st.button(t("play_auto_run"), key=f"{key}_play_btn", type="primary"):
                st.session_state[auto_key] = True
                st.session_state[auto_step_key] = st.session_state.get(slider_key, 0)
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

    if st.session_state.get(auto_key, False):
        current_auto = int(st.session_state.get(auto_step_key, current_step))
        if current_auto < max_step:
            import time
            next_step = current_auto + 1
            st.session_state[slider_key] = next_step
            st.session_state[auto_step_key] = next_step
            time.sleep(speed)
            st.rerun()
        else:
            st.session_state[auto_key] = False
            st.session_state[auto_step_key] = 0
            st.success(t("anim_complete"))

    current_step = st.slider(
        t("play_curr_step"), 0, max_step, current_step, key=slider_key
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
        action_display = t("dir_start_short")
    else:
        action_display = actions[current_step - 1]
    display = direction_map.get(action_display, action_display)
    goal_suffix = (
        f" · {t('anim_goal')}"
        if reaches_goal and current_step == len(path) - 1
        else ""
    )
    st.caption(
        t(
            "anim_step_caption",
            current=current_step,
            total=len(path) - 1,
            action=display,
            goal_suffix=goal_suffix,
        )
    )

    # Navigation buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        st.button(
            t("anim_prev"),
            key=f"{key}_prev",
            on_click=_set_slider_step,
            args=(slider_key, current_step - 1, max_step),
        )
    with col2:
        st.button(
            t("anim_next"),
            key=f"{key}_next",
            on_click=_set_slider_step,
            args=(slider_key, current_step + 1, max_step),
        )
    with col3:
        st.button(
            t("anim_reset"),
            key=f"{key}_reset",
            on_click=_reset_animation_slider,
            args=(slider_key, auto_key, auto_step_key),
        )


def render_comparison_table(results: list):
    """Render comparison table for benchmark results."""
    if not results:
        st.info(t("compare_no_data"))
        return

    rows = []
    for r in results:
        row = {
            t("compare_group_col"): _localized_group_name(r.group),
            t("run_algo"): r.algorithm,
            t("mc_status"): t("mc_solved") if r.success else t("mc_failed"),
            t("mc_recorded_steps"): len(r.actions) if r.path_verified else "-",
            t("compare_action_trajectory"): compact_action_path(r.actions) if r.path_verified else "-",
            t("mc_cost"): r.cost if r.success else "-",
            t("mc_expanded"): r.nodes_expanded,
            t("mc_max_f"): r.max_frontier_size,
            t("mc_runtime"): f"{r.runtime:.4f}",
            t("compare_seed_mode"): r.random_seed if r.random_seed is not None else t("compare_deterministic"),
            f"{t('compare_optimal_col')} ({t('compare_theory_suffix')})": t("tc_yes") if r.is_optimal else t("tc_no"),
            f"{t('compare_complete_col')} ({t('compare_theory_suffix')})": t("tc_yes") if r.is_complete else t("tc_no"),
            t("compare_run_optimality_proven"): t("tc_yes") if r.optimality_proven else t("tc_no"),
            t("compare_termination"): r.termination_reason,
        }
        rows.append(row)

    df = pd.DataFrame(rows)
    st.dataframe(df, width="stretch", hide_index=True)

    if len([r for r in results if r.success]) > 1:
        successful = [r for r in results if r.success]
        fastest = min(successful, key=lambda x: x.runtime if x.runtime is not None else float('inf'))
        shortest = min(successful, key=lambda x: len(x.actions) if x.actions is not None else float('inf'))
        max_mem = max(successful, key=lambda x: x.nodes_expanded if x.nodes_expanded is not None else 0)

        st.markdown(f"### {t('compare_analysis')}")
        st.markdown(f"- {t('compare_fastest', algo=fastest.algorithm, time=fastest.runtime)}")
        st.markdown(f"- {t('compare_shortest', algo=shortest.algorithm, steps=len(shortest.actions))}")
        if max_mem.algorithm != min(successful, key=lambda x: x.nodes_expanded if x.nodes_expanded is not None else float('inf')).algorithm:
            st.markdown(f"- {t('compare_most_memory', algo=max_mem.algorithm, nodes=max_mem.nodes_expanded)}")

        verified_count = len([r for r in successful if r.path_verified])
        unique_count = unique_verified_path_count(successful)
        st.caption(
            t("compare_verified_path_evidence", unique=unique_count, verified=verified_count)
        )
        for algorithms in shared_verified_paths(successful):
            st.info(
                t("compare_shared_path_explanation", algorithms=", ".join(algorithms))
            )


def render_algorithm_info(algo_name: str, theory: dict):
    """Render algorithm theory information."""
    global_lang = _current_language()
    if not theory:
        st.info(t("theory_coming_soon", algo=algo_name))
        return

    group = theory.get("group", "")
    group_style = GROUP_COLORS.get(group, {})

    st.markdown(f"### {theory.get('name', algo_name)}")

    group_display = _localized_group_name(group)

    badge_cls = group_style.get("badge", "")
    if badge_cls:
        st.markdown(f'<span class="group-badge {badge_cls}">{group_display}</span>', unsafe_allow_html=True)

    props = []
    suitable_key = "suitable_en" if global_lang == "English" and "suitable_en" in theory else "suitable"
    suitable_val = theory.get(suitable_key)
    if suitable_val:
        if "RẤT" in suitable_val or "rất" in suitable_val.lower() or "highly" in suitable_val.lower():
            props.append((t("alg_suitable"), "#06d6a0"))
        elif "KHÔNG" in suitable_val or "không" in suitable_val.lower() or "not" in suitable_val.lower():
            props.append((t("alg_not_suitable"), "#ef476f"))
        else:
            props.append((t("alg_limited"), "#ffd166"))

    for label, color in props:
        st.markdown(f'<span style="background:{color};color:#fff;padding:2px 10px;border-radius:12px;font-size:12px;font-weight:600;">{label}</span>', unsafe_allow_html=True)

    sections = [
        (t("alg_goal"), "goal"),
        (t("alg_idea"), "idea"),
        (t("alg_data_structure"), "data_structure"),
        (t("alg_formula"), "formula"),
        (t("alg_application"), "application"),
        (t("alg_suitable_question"), "suitable"),
        (t("alg_pros"), "pros"),
        (t("alg_cons"), "cons"),
        (t("alg_complexity"), "complexity"),
        (t("alg_worst_case"), "bad_example"),
        (t("alg_comparison"), "comparison"),
        (t("alg_exam_tips"), "exam_tips"),
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
        st.markdown(f"**{t('pseudocode_label')}**")
        st.code(pseudocode, language="python")


def render_search_tree(result, max_nodes: int = 40):
    """Render only verified parent-child transitions as a directed graph."""
    from core.metrics import search_tree_to_dot

    if not result.search_tree_nodes or not result.search_tree_edges:
        st.info(t("tc_no_trace"))
        return

    st.markdown(f"### {t('run_search_tree')}")
    st.caption(t("search_tree_caption"))
    st.graphviz_chart(search_tree_to_dot(result, max_nodes), width="stretch")
    if len(result.search_tree_nodes) > max_nodes:
        st.caption(
            t("search_tree_showing", shown=max_nodes, total=len(result.search_tree_nodes))
        )
    if result.trace_truncated:
        st.warning(t("trace_capture_limit_warning"))


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

    # Find the algorithm row in COMPARISON_TABLE — exact match first
    row_data = None
    for row in COMPARISON_TABLE:
        if row["Algorithm"].lower() == algo_name.lower():
            row_data = row
            break
    if not row_data:
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
