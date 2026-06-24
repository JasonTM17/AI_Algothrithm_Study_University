"""Core Caro/Gomoku board rules."""

from __future__ import annotations

from dataclasses import dataclass, field


EMPTY = "."
PLAYERS = ("X", "O")
DIRECTIONS = ((0, 1), (1, 0), (1, 1), (1, -1))


@dataclass(frozen=True)
class CaroState:
    size: int = 15
    board: tuple[str, ...] = field(default_factory=tuple)
    current_player: str = "X"

    def __post_init__(self) -> None:
        board = self.board or (EMPTY,) * (self.size * self.size)
        if len(board) != self.size * self.size:
            raise ValueError("Board length must equal size * size")
        if self.current_player not in PLAYERS:
            raise ValueError("Current player must be X or O")
        object.__setattr__(self, "board", tuple(board))


def create_initial_caro_state(size: int = 15) -> CaroState:
    """Create an empty Caro board."""
    if size < 5:
        raise ValueError("Caro board size must be at least 5")
    return CaroState(size=size)


def opponent(player: str) -> str:
    return "O" if player == "X" else "X"


def apply_caro_move(state: CaroState, row: int, col: int) -> CaroState:
    """Return a new state after placing the current player's mark."""
    if not (0 <= row < state.size and 0 <= col < state.size):
        raise ValueError("Move is outside the board")
    index = row * state.size + col
    if state.board[index] != EMPTY:
        raise ValueError("Move targets an occupied cell")
    board = list(state.board)
    board[index] = state.current_player
    return CaroState(state.size, tuple(board), opponent(state.current_player))


def winner(state: CaroState) -> str | None:
    for index, mark in enumerate(state.board):
        if mark == EMPTY:
            continue
        row, col = divmod(index, state.size)
        for dr, dc in DIRECTIONS:
            if count_run(state, row, col, dr, dc, mark) >= 5:
                return mark
    return None


def is_draw(state: CaroState) -> bool:
    return winner(state) is None and EMPTY not in state.board


def legal_caro_moves(state: CaroState, radius: int = 2) -> list[tuple[int, int]]:
    """Generate empty cells near existing stones to keep game-tree branching bounded."""
    occupied = [
        divmod(index, state.size)
        for index, mark in enumerate(state.board)
        if mark != EMPTY
    ]
    if not occupied:
        center = state.size // 2
        return [(center, center)]

    moves: set[tuple[int, int]] = set()
    for row, col in occupied:
        for r in range(max(0, row - radius), min(state.size, row + radius + 1)):
            for c in range(max(0, col - radius), min(state.size, col + radius + 1)):
                if state.board[r * state.size + c] == EMPTY:
                    moves.add((r, c))
    return sorted(moves, key=lambda move: (center_distance(state, move), move[0], move[1]))


def count_run(state: CaroState, row: int, col: int, dr: int, dc: int, mark: str) -> int:
    count = 0
    while 0 <= row < state.size and 0 <= col < state.size and state.board[row * state.size + col] == mark:
        count += 1
        row += dr
        col += dc
    return count


def center_distance(state: CaroState, move: tuple[int, int]) -> int:
    center = state.size // 2
    return abs(move[0] - center) + abs(move[1] - center)
