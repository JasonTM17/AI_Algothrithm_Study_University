"""Tests for the Caro/Gomoku adversarial demo."""

import pytest

from algorithms.caro import (
    CaroState,
    apply_caro_move,
    caro_alpha_beta,
    caro_minimax,
    create_initial_caro_state,
    evaluate_caro_state,
    is_draw,
    winner,
)
from algorithms.caro_rules import opponent


def board_state(size, stones, current_player="X"):
    board = ["."] * (size * size)
    for row, col, mark in stones:
        board[row * size + col] = mark
    return CaroState(size=size, board=tuple(board), current_player=current_player)


def test_caro_detects_all_five_in_row_directions():
    cases = [
        [(2, col, "X") for col in range(5)],
        [(row, 2, "X") for row in range(5)],
        [(i, i, "X") for i in range(5)],
        [(i, 4 - i, "X") for i in range(5)],
    ]

    for stones in cases:
        assert winner(board_state(7, stones)) == "X"


def test_caro_rejects_invalid_moves():
    state = create_initial_caro_state(5)
    with pytest.raises(ValueError, match="outside"):
        apply_caro_move(state, -1, 0)

    occupied = apply_caro_move(state, 2, 2)
    with pytest.raises(ValueError, match="occupied"):
        apply_caro_move(occupied, 2, 2)


def test_caro_rejects_invalid_board_marks():
    with pytest.raises(ValueError, match="only"):
        CaroState(size=5, board=tuple(["Z"] * 25), current_player="X")


def test_caro_rejects_invalid_player_symbols():
    with pytest.raises(ValueError, match="Player"):
        opponent("Z")

    state = create_initial_caro_state(5)
    with pytest.raises(ValueError, match="Player"):
        evaluate_caro_state(state, "Z")


def test_caro_draw_detection_when_board_full_without_winner():
    rows = ["XOXOX", "OXOXO", "XOOXO", "OXOXX", "XOXOO"]
    marks = [
        (row, col, mark)
        for row, line in enumerate(rows)
        for col, mark in enumerate(line)
    ]
    state = board_state(5, marks)

    assert winner(state) is None
    assert is_draw(state)


def test_caro_evaluation_rewards_win_and_blocking_move():
    winning = board_state(7, [(3, col, "X") for col in range(5)])
    open_threat = board_state(7, [(3, col, "O") for col in range(4)], current_player="X")
    blocked = apply_caro_move(open_threat, 3, 4)

    assert evaluate_caro_state(winning, "X") == 1_000_000
    assert evaluate_caro_state(blocked, "X") > evaluate_caro_state(open_threat, "X")


def test_caro_alpha_beta_matches_minimax_on_controlled_board():
    state = board_state(
        7,
        [(3, 1, "X"), (3, 2, "X"), (2, 2, "O"), (2, 3, "O")],
        current_player="X",
    )

    minimax = caro_minimax(state, depth=2, player="X")
    alpha_beta = caro_alpha_beta(state, depth=2, player="X")

    assert alpha_beta.value == minimax.value
    assert alpha_beta.move == minimax.move
    assert alpha_beta.nodes_expanded <= minimax.nodes_expanded


def test_caro_alpha_beta_reports_pruning():
    state = board_state(
        7,
        [(3, 1, "X"), (3, 2, "X"), (3, 3, "X"), (2, 2, "O"), (4, 2, "O")],
        current_player="X",
    )

    result = caro_alpha_beta(state, depth=3, player="X")

    assert result.pruned > 0
