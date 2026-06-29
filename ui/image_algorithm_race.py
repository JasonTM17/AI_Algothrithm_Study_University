"""Visual comparison of verified solver trajectories on the active image puzzle."""

from __future__ import annotations

from dataclasses import dataclass
from html import escape

import pandas as pd
import streamlit as st

from core.metrics import SearchResult


@dataclass(frozen=True)
class RaceResultGroups:
    """Separate comparable solutions from partial and non-linear outputs."""

    solved: tuple[SearchResult, ...]
    partial: tuple[SearchResult, ...]
    unavailable: tuple[SearchResult, ...]


CHART_LABELS = {
    "Simple Hill Climbing": "Simple HC",
    "Steepest-Ascent Hill Climbing": "Steepest HC",
    "Stochastic Hill Climbing": "Stochastic HC",
    "Random-Restart Hill Climbing": "Random-Restart HC",
}


def classify_race_results(results: list[SearchResult]) -> RaceResultGroups:
    solved: list[SearchResult] = []
    partial: list[SearchResult] = []
    unavailable: list[SearchResult] = []
    for result in results:
        if result.path_verified and result.path:
            (solved if result.goal_reached else partial).append(result)
        else:
            unavailable.append(result)
    return RaceResultGroups(tuple(solved), tuple(partial), tuple(unavailable))


def race_chart_rows(results: list[SearchResult]) -> list[dict[str, object]]:
    """Return empirical ranking rows only for legal paths ending at the goal."""
    groups = classify_race_results(results)
    return [
        {
            "Algorithm": result.algorithm,
            "Runtime (s)": round(float(result.runtime), 6),
            "Steps": len(result.actions),
        }
        for result in groups.solved
    ]


def state_at_step(result: SearchResult, step: int) -> tuple[int, ...] | None:
    if not result.path_verified or not result.path:
        return None
    return result.path[max(0, min(int(step), len(result.path) - 1))]


def _image_board_html(state: tuple[int, ...], image_tiles: dict[int, str]) -> str:
    cells: list[str] = []
    for value in state:
        if value == 0:
            cells.append('<span class="image-race-cell image-race-blank"></span>')
            continue
        if image_tiles.get(value):
            cells.append(
                f'<span class="image-race-cell image-race-tile-{value}" '
                f'aria-label="image tile {value}"></span>'
            )
        else:
            cells.append('<span class="image-race-cell image-race-missing"></span>')
    return f'<div class="image-race-board">{"".join(cells)}</div>'


def _render_result_card(
    result: SearchResult,
    step: int,
    image_tiles: dict[int, str],
    tx,
) -> None:
    state = state_at_step(result, step)
    if state is None:
        return
    shown_step = min(step, len(result.actions))
    status = tx("image_race_goal") if result.goal_reached else tx("image_race_partial")
    with st.container(border=True):
        st.markdown(f"#### {escape(result.algorithm)}")
        st.markdown(_image_board_html(state, image_tiles), unsafe_allow_html=True)
        st.caption(
            tx(
                "image_race_card_metrics",
                step=shown_step,
                total=len(result.actions),
                runtime=float(result.runtime),
                status=status,
            )
        )


def render_image_algorithm_race(
    results: list[SearchResult],
    image_tiles: dict[int, str],
    tx,
) -> None:
    """Render charts and synchronized image replay without tile-number overlays."""
    if not results or not image_tiles:
        return

    groups = classify_race_results(results)
    trajectories = [*groups.solved, *groups.partial]
    rows = race_chart_rows(results)

    st.markdown('<div class="image-algorithm-race"></div>', unsafe_allow_html=True)
    st.subheader(tx("image_race_title"))
    st.caption(tx("image_race_caption"))

    tile_styles = "".join(
        f'.image-race-tile-{value} {{ background-image: url("{escape(str(source), quote=True)}"); }}'
        for value, source in sorted(image_tiles.items())
        if source
    )
    board_styles = """
        .image-race-board {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 4px;
            width: min(100%, 280px);
            margin: 0 auto 10px;
            padding: 6px;
            border: 1px solid rgba(126, 175, 111, 0.5);
            border-radius: 7px;
            background: #0a0f0c;
        }
        .image-race-cell {
            display: block;
            aspect-ratio: 1 / 1;
            border: 1px solid rgba(214, 161, 95, 0.62);
            border-radius: 5px;
            background-position: center;
            background-size: cover;
            background-repeat: no-repeat;
        }
        .image-race-blank {
            border-color: rgba(255,255,255,0.1);
            background: repeating-linear-gradient(135deg, #080b09 0 8px, #0d110e 8px 16px);
        }
        .image-race-missing { background: #251f1b; }
    """
    st.markdown(
        f"<style>{board_styles}{tile_styles}</style>",
        unsafe_allow_html=True,
    )

    if rows:
        frame = pd.DataFrame(rows)
        algorithm_axis = tx("image_race_algorithm_axis")
        runtime_axis = tx("image_race_runtime_axis")
        steps_axis = tx("image_race_steps_axis")
        frame[algorithm_axis] = frame["Algorithm"].map(
            lambda name: CHART_LABELS.get(name, name)
        )
        frame[runtime_axis] = frame["Runtime (s)"]
        frame[steps_axis] = frame["Steps"]
        fastest = min(groups.solved, key=lambda result: result.runtime)
        shortest = min(groups.solved, key=lambda result: len(result.actions))
        summary = st.columns(3)
        with summary[0]:
            st.metric(tx("image_race_fastest"), f"{fastest.runtime:.6f}s")
            st.caption(fastest.algorithm)
        with summary[1]:
            st.metric(tx("image_race_shortest"), len(shortest.actions))
            st.caption(shortest.algorithm)
        with summary[2]:
            st.metric(tx("image_race_solved_count"), f"{len(groups.solved)}/{len(results)}")
            st.caption(tx("image_race_ranked_only"))

        chart_height = max(300, len(rows) * 30)
        st.markdown(f"**{tx('image_race_runtime_chart')}**")
        st.bar_chart(
            frame,
            x=algorithm_axis,
            y=runtime_axis,
            horizontal=True,
            height=chart_height,
        )
        st.markdown(f"**{tx('image_race_steps_chart')}**")
        st.bar_chart(
            frame,
            x=algorithm_axis,
            y=steps_axis,
            horizontal=True,
            height=chart_height,
        )
        st.caption(tx("image_race_chart_abbreviation"))
    else:
        st.warning(tx("image_race_no_solved"))

    if trajectories:
        max_step = max(len(result.actions) for result in trajectories)
        race_version = int(st.session_state.get("image_race_version", 0))
        slider_key = f"image_race_step_{race_version}"
        if max_step:
            step = st.slider(tx("image_race_step"), 0, max_step, 0, key=slider_key)
        else:
            step = 0
            st.caption(tx("image_race_zero_step"))

        for offset in range(0, len(trajectories), 3):
            batch = trajectories[offset:offset + 3]
            columns = st.columns(len(batch))
            for column, result in zip(columns, batch):
                with column:
                    _render_result_card(result, step, image_tiles, tx)

    if groups.partial:
        st.info(tx("image_race_partial_note", count=len(groups.partial)))
    if groups.unavailable:
        names = ", ".join(result.algorithm for result in groups.unavailable)
        st.caption(tx("image_race_unavailable", algorithms=names))
