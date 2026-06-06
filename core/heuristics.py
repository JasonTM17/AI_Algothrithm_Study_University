"""Heuristic functions for 15-Puzzle."""

from core.puzzle import GOAL_STATE, GOAL_POS


def misplace_count(state: tuple[int, ...]) -> int:
    """Count tiles not in goal position (excluding blank)."""
    return sum(1 for i, v in enumerate(state) if v != 0 and v != GOAL_STATE[i])


def manhattan_distance(state: tuple[int, ...]) -> int:
    """Sum of Manhattan distances of each tile from its goal position."""
    total = 0
    for idx, val in enumerate(state):
        if val == 0:
            continue
        r, c = idx // 4, idx % 4
        gr, gc = GOAL_POS[val]
        total += abs(r - gr) + abs(c - gc)
    return total


def linear_conflict(state: tuple[int, ...]) -> int:
    """Manhattan distance + 2 * number of linear conflicts.

    Two tiles are in linear conflict if they are in the same row/column,
    both in their goal row/column, but in the wrong order relative to
    each other. Each conflict requires at least 2 extra moves.
    """
    md = manhattan_distance(state)
    conflicts = 0

    # Row conflicts
    for row in range(4):
        tiles_in_row = []
        for col in range(4):
            val = state[row * 4 + col]
            if val == 0:
                continue
            goal_r, goal_c = GOAL_POS[val]
            if goal_r == row:
                tiles_in_row.append((col, goal_c))
        # Count conflicts: pairs where both are in goal row but reversed
        for i in range(len(tiles_in_row)):
            for j in range(i + 1, len(tiles_in_row)):
                if tiles_in_row[i][0] > tiles_in_row[j][0] and tiles_in_row[i][1] < tiles_in_row[j][1]:
                    conflicts += 1

    # Column conflicts
    for col in range(4):
        tiles_in_col = []
        for row in range(4):
            val = state[row * 4 + col]
            if val == 0:
                continue
            goal_r, goal_c = GOAL_POS[val]
            if goal_c == col:
                tiles_in_col.append((row, goal_r))
        for i in range(len(tiles_in_col)):
            for j in range(i + 1, len(tiles_in_col)):
                if tiles_in_col[i][0] > tiles_in_col[j][0] and tiles_in_col[i][1] < tiles_in_col[j][1]:
                    conflicts += 1

    return md + 2 * conflicts


HEURISTICS = {
    "Misplaced Tiles": misplace_count,
    "Manhattan Distance": manhattan_distance,
    "Linear Conflict": linear_conflict,
}

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