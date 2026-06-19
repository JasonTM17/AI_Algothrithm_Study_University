"""Tests for academic challenge scoring."""

import pytest

from core.gameplay import score_challenge


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
