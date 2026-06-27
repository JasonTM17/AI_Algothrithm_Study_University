"""Utility helpers for 15-Puzzle AI project."""

import time
from typing import Callable

from core.metrics import SearchResult
from core.puzzle import GOAL_STATE, is_solvable


def run_solver(
    solver_fn: Callable,
    start: tuple[int, ...],
    goal: tuple[int, ...] = GOAL_STATE,
    timeout: float = 60.0,
    **kwargs,
) -> SearchResult:
    """Run a solver function with timeout and return SearchResult."""
    try:
        solvable = is_solvable(start, goal)
    except (TypeError, ValueError) as exc:
        return SearchResult(
            success=False,
            goal_state=goal,
            message=f"Invalid puzzle state: {exc}",
        )
    if not solvable:
        return SearchResult(
            success=False,
            goal_state=goal,
            message="Puzzle is not solvable.",
        )
    t0 = time.perf_counter()
    try:
        result = solver_fn(start, goal, timeout=timeout, **kwargs)
    except TimeoutError:
        result = SearchResult(
            success=False,
            goal_state=goal,
            message=f"Timeout after {timeout}s",
            runtime=time.perf_counter() - t0,
        )
    except MemoryError:
        result = SearchResult(
            success=False,
            goal_state=goal,
            message="Memory limit exceeded",
            runtime=time.perf_counter() - t0,
        )
    except Exception as e:
        result = SearchResult(
            success=False,
            goal_state=goal,
            message=f"Error: {e}",
            runtime=time.perf_counter() - t0,
        )
    if result.goal_state is None:
        result.goal_state = goal
        result.refresh_certificate()
    return result


def format_state_grid(state: tuple[int, ...]) -> str:
    """Format state as 4x4 grid string."""
    lines = []
    for r in range(4):
        row = state[r * 4:(r + 1) * 4]
        lines.append("| " + " | ".join(f"{v:2d}" if v != 0 else " _" for v in row) + " |")
    return "\n".join(lines)


def state_to_flat_str(state: tuple[int, ...]) -> str:
    """Flat string representation for display."""
    return " ".join(str(v) for v in state)
