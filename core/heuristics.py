"""Admissible heuristic functions for the 15-puzzle."""

from collections.abc import Callable
from functools import lru_cache, partial

from core.puzzle import GOAL_STATE, GOAL_POS


def _goal_positions(goal: tuple[int, ...]) -> dict[int, tuple[int, int]]:
    return {value: divmod(index, 4) for index, value in enumerate(goal)}


def misplace_count(state: tuple[int, ...], goal: tuple[int, ...] = GOAL_STATE) -> int:
    """Count tiles not in goal position (excluding blank)."""
    return sum(1 for i, value in enumerate(state) if value != 0 and value != goal[i])


def manhattan_distance(state: tuple[int, ...], goal: tuple[int, ...] = GOAL_STATE) -> int:
    """Sum of Manhattan distances of each tile from its goal position."""
    goal_positions = GOAL_POS if goal == GOAL_STATE else _goal_positions(goal)
    total = 0
    for idx, val in enumerate(state):
        if val == 0:
            continue
        r, c = idx // 4, idx % 4
        gr, gc = goal_positions[val]
        total += abs(r - gr) + abs(c - gc)
    return total


def _maximum_matching_size(edges: set[tuple[int, int]]) -> int:
    """Maximum number of vertex-disjoint conflict pairs (15 vertices max)."""
    adjacency: dict[int, set[int]] = {}
    for left, right in edges:
        adjacency.setdefault(left, set()).add(right)
        adjacency.setdefault(right, set()).add(left)

    @lru_cache(maxsize=None)
    def match(available: frozenset[int]) -> int:
        if not available:
            return 0
        vertex = min(available)
        without_vertex = available - {vertex}
        best = match(without_vertex)
        for neighbor in adjacency.get(vertex, set()) & without_vertex:
            best = max(best, 1 + match(without_vertex - {neighbor}))
        return best

    return match(frozenset(adjacency))


def linear_conflict(state: tuple[int, ...], goal: tuple[int, ...] = GOAL_STATE) -> int:
    """Manhattan plus an admissible penalty for row/column conflicts.

    Two tiles are in linear conflict if they are in the same row/column,
    both in their goal row/column, but in the wrong order relative to
    each other. Each conflict requires at least 2 extra moves.
    """
    goal_positions = GOAL_POS if goal == GOAL_STATE else _goal_positions(goal)
    md = manhattan_distance(state, goal)
    conflicts: set[tuple[int, int]] = set()

    # Row conflicts
    for row in range(4):
        row_tiles = []
        for col in range(4):
            val = state[row * 4 + col]
            if val == 0:
                continue
            goal_r, goal_c = goal_positions[val]
            if goal_r == row and goal_c != col:
                row_tiles.append((val, goal_c))
        for left in range(len(row_tiles)):
            for right in range(left + 1, len(row_tiles)):
                if row_tiles[left][1] > row_tiles[right][1]:
                    conflicts.add(tuple(sorted((row_tiles[left][0], row_tiles[right][0]))))

    # Column conflicts
    for col in range(4):
        column_tiles = []
        for row in range(4):
            val = state[row * 4 + col]
            if val == 0:
                continue
            goal_r, goal_c = goal_positions[val]
            if goal_c == col and goal_r != row:
                column_tiles.append((val, goal_r))
        for top in range(len(column_tiles)):
            for bottom in range(top + 1, len(column_tiles)):
                if column_tiles[top][1] > column_tiles[bottom][1]:
                    conflicts.add(tuple(sorted((column_tiles[top][0], column_tiles[bottom][0]))))

    return md + 2 * _maximum_matching_size(conflicts)


HEURISTICS = {
    "Misplaced Tiles": misplace_count,
    "Manhattan Distance": manhattan_distance,
    "Linear Conflict": linear_conflict,
}


def get_heuristic(name: str, goal: tuple[int, ...] = GOAL_STATE) -> Callable[[tuple[int, ...]], int]:
    """Bind a registered heuristic to the goal used by a solver run."""
    heuristic = HEURISTICS.get(name, manhattan_distance)
    return partial(heuristic, goal=goal)

HEURISTIC_DESCRIPTIONS = {
    "Misplaced Tiles": (
        "Đếm số ô không ở vị trí đích (không tính ô trống). "
        "Admissible nhưng yếu hơn Manhattan vì không xét khoảng cách. "
        "Vì 1 ô sai vị trí cần ít nhất 1 bước, h(n) ≤ h*(n)."
    ),
    "Manhattan Distance": (
        "Tổng khoảng cách Manhattan mỗi tile từ vị trí hiện tại đến vị trí đích. "
        "Admissible và consistent. Thường tốt nhất cho 15-puzzle vì "
        "ước lượng gần hơn Misplaced Tiles."
    ),
    "Linear Conflict": (
        "Manhattan + 2 × số linear conflicts. Mạnh hơn Manhattan vì "
        "bắt thêm ràng buộc: 2 tile cùng hàng/cột mục tiêu nhưng ngược thứ tự "
        "cần ít nhất 2 bước thêm. Admissible và consistent."
    ),
}
