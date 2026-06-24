"""Caro/Gomoku adversarial search demo for Minimax and Alpha-Beta."""

from __future__ import annotations

from dataclasses import dataclass
from math import inf
from time import perf_counter

from algorithms.caro_rules import (
    DIRECTIONS,
    EMPTY,
    CaroState,
    apply_caro_move,
    create_initial_caro_state,
    is_draw,
    legal_caro_moves,
    opponent,
    winner,
)


@dataclass(frozen=True)
class CaroSearchResult:
    algorithm: str
    move: tuple[int, int] | None
    value: int
    nodes_expanded: int
    nodes_generated: int
    pruned: int = 0
    runtime: float = 0.0
    principal_variation: tuple[tuple[int, int], ...] = ()


def evaluate_caro_state(state: CaroState, player: str) -> int:
    """Score a board from player perspective using five-cell line threats."""
    win = winner(state)
    if win == player:
        return 1_000_000
    if win == opponent(player):
        return -1_000_000
    return _line_score(state, player) - _line_score(state, opponent(player))


def caro_minimax(state: CaroState, depth: int, player: str) -> CaroSearchResult:
    started = perf_counter()
    nodes_expanded = 0
    nodes_generated = 0

    def search(current: CaroState, depth_left: int) -> tuple[int, tuple[tuple[int, int], ...]]:
        nonlocal nodes_expanded, nodes_generated
        nodes_expanded += 1
        if depth_left == 0 or winner(current) or is_draw(current):
            return evaluate_caro_state(current, player), ()
        moves = _ordered_moves(current, player)
        nodes_generated += len(moves)
        if current.current_player == player:
            best_value, best_line = -inf, ()
            for move in moves:
                value, line = search(apply_caro_move(current, *move), depth_left - 1)
                if value > best_value:
                    best_value, best_line = value, (move,) + line
            return int(best_value), best_line
        best_value, best_line = inf, ()
        for move in moves:
            value, line = search(apply_caro_move(current, *move), depth_left - 1)
            if value < best_value:
                best_value, best_line = value, (move,) + line
        return int(best_value), best_line

    value, line = search(state, max(0, depth))
    return CaroSearchResult(
        "Minimax", line[0] if line else None, value, nodes_expanded, nodes_generated,
        runtime=perf_counter() - started, principal_variation=line,
    )


def caro_alpha_beta(state: CaroState, depth: int, player: str) -> CaroSearchResult:
    started = perf_counter()
    nodes_expanded = 0
    nodes_generated = 0
    pruned = 0

    def search(
        current: CaroState, depth_left: int, alpha: float, beta: float,
    ) -> tuple[int, tuple[tuple[int, int], ...]]:
        nonlocal nodes_expanded, nodes_generated, pruned
        nodes_expanded += 1
        if depth_left == 0 or winner(current) or is_draw(current):
            return evaluate_caro_state(current, player), ()
        moves = _ordered_moves(current, player)
        nodes_generated += len(moves)
        if current.current_player == player:
            best_value, best_line = -inf, ()
            for move in moves:
                value, line = search(apply_caro_move(current, *move), depth_left - 1, alpha, beta)
                if value > best_value:
                    best_value, best_line = value, (move,) + line
                alpha = max(alpha, best_value)
                if alpha >= beta:
                    pruned += 1
                    break
            return int(best_value), best_line
        best_value, best_line = inf, ()
        for move in moves:
            value, line = search(apply_caro_move(current, *move), depth_left - 1, alpha, beta)
            if value < best_value:
                best_value, best_line = value, (move,) + line
            beta = min(beta, best_value)
            if alpha >= beta:
                pruned += 1
                break
        return int(best_value), best_line

    value, line = search(state, max(0, depth), -inf, inf)
    return CaroSearchResult(
        "Alpha-Beta", line[0] if line else None, value, nodes_expanded,
        nodes_generated, pruned, perf_counter() - started, line,
    )


def _ordered_moves(state: CaroState, player: str) -> list[tuple[int, int]]:
    moves = legal_caro_moves(state)
    reverse = state.current_player == player
    return sorted(
        moves,
        key=lambda move: evaluate_caro_state(apply_caro_move(state, *move), player),
        reverse=reverse,
    )


def _line_score(state: CaroState, player: str) -> int:
    weights = {1: 2, 2: 20, 3: 200, 4: 20_000, 5: 1_000_000}
    total = 0
    size = state.size
    for row in range(size):
        for col in range(size):
            for dr, dc in DIRECTIONS:
                cells = [(row + dr * i, col + dc * i) for i in range(5)]
                if not all(0 <= r < size and 0 <= c < size for r, c in cells):
                    continue
                marks = [state.board[r * size + c] for r, c in cells]
                if opponent(player) in marks:
                    continue
                count = marks.count(player)
                if count:
                    total += weights[count] * _open_end_multiplier(state, row, col, dr, dc)
    return total


def _open_end_multiplier(state: CaroState, row: int, col: int, dr: int, dc: int) -> int:
    size = state.size
    before = (row - dr, col - dc)
    after = (row + dr * 5, col + dc * 5)
    open_ends = 0
    for r, c in (before, after):
        if 0 <= r < size and 0 <= c < size and state.board[r * size + c] == EMPTY:
            open_ends += 1
    return 1 + open_ends
