"""Tests for academic challenge scoring."""

import pytest

from core.gameplay import score_challenge, validate_player_run


GOAL = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 0)
ONE_MOVE_AWAY = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 0, 15)


def test_optimal_player_run_scores_full_efficiency():
    score = score_challenge(player_moves=12, optimal_moves=12)
    assert score.gap == 0
    assert score.is_optimal_play
    assert score.efficiency_percent == 100.0


def test_longer_run_reports_gap_and_efficiency():
    score = score_challenge(player_moves=15, optimal_moves=12)
    assert score.gap == 3
    assert not score.is_optimal_play
    assert score.efficiency_percent == 80.0


def test_invalid_move_counts_are_rejected():
    with pytest.raises(ValueError):
        score_challenge(-1, 0)


def test_incomplete_run_is_certified_but_not_scored_as_solution():
    cert = validate_player_run([ONE_MOVE_AWAY])

    assert cert.is_legal
    assert not cert.reaches_goal
    assert cert.actions == ()
    assert "not reached" in cert.message


def test_completed_player_run_reaches_goal_with_actions():
    cert = validate_player_run([ONE_MOVE_AWAY, GOAL])

    assert cert.is_legal
    assert cert.reaches_goal
    assert cert.actions == ("R",)
    assert cert.move_count == 1


def test_illegal_player_history_is_rejected():
    illegal_state = (2, 1, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 0)
    cert = validate_player_run([GOAL, illegal_state])

    assert not cert.is_legal
    assert not cert.reaches_goal
    assert "Illegal transition" in cert.message


def test_malformed_player_history_is_rejected_without_exception():
    duplicate_tile_state = (1, 1, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 0)
    cert = validate_player_run([GOAL, duplicate_tile_state])

    assert not cert.is_legal
    assert not cert.reaches_goal
    assert cert.final_state == duplicate_tile_state
    assert "Invalid board state at player step 1" in cert.message


def test_malformed_challenge_goal_is_rejected_without_exception():
    malformed_goal = (1, 2, 3)
    cert = validate_player_run([GOAL], goal=malformed_goal)

    assert not cert.is_legal
    assert not cert.reaches_goal
    assert cert.actions == ()
    assert "Invalid goal state" in cert.message


def test_completed_score_cannot_beat_proven_optimum():
    with pytest.raises(ValueError):
        score_challenge(player_moves=0, optimal_moves=1)
