"""Two-lane Group 6 policy comparison contracts."""

from core.group6_policy_comparison import (
    Group6PolicySettings,
    advance_policy_comparison,
    create_policy_comparison,
)
from core.puzzle import GOAL_STATE, _move_blank, scramble


START = scramble(GOAL_STATE, depth=5, seed=12)


def test_policy_comparison_starts_two_lanes_from_same_board():
    comparison = create_policy_comparison(start=START, goal=GOAL_STATE)
    assert comparison.lane_a.algorithm == "Minimax"
    assert comparison.lane_b.algorithm == "Alpha-Beta Pruning"
    assert comparison.lane_a.current_state == comparison.lane_b.current_state == START
    assert comparison.lane_a.history == comparison.lane_b.history == [START]


def test_one_tick_applies_at_most_one_legal_move_per_lane():
    comparison = create_policy_comparison(
        start=START,
        goal=GOAL_STATE,
        settings=Group6PolicySettings(depth=2, per_decision_timeout=5, max_turns=4),
    )
    advance_policy_comparison(comparison)
    for lane in (comparison.lane_a, comparison.lane_b):
        assert len(lane.history) <= 2
        if lane.turns:
            turn = lane.turns[0]
            assert _move_blank(turn.before_state, turn.realized_action) == turn.after_state
            assert lane.current_state == turn.after_state
            assert turn.termination == "applied"


def test_alpha_beta_policy_does_not_expand_more_than_minimax_for_first_turn():
    comparison = create_policy_comparison(
        start=START,
        goal=GOAL_STATE,
        settings=Group6PolicySettings(depth=3, per_decision_timeout=10, max_turns=1),
    )
    advance_policy_comparison(comparison)
    assert comparison.lane_b.cumulative_expanded <= comparison.lane_a.cumulative_expanded
    assert comparison.lane_b.cumulative_pruned >= 0


def test_expectimax_seed_schedule_is_reproducible():
    settings = Group6PolicySettings(
        depth=2,
        per_decision_timeout=5,
        max_turns=3,
        base_seed=91,
    )
    first = create_policy_comparison(
        start=START,
        goal=GOAL_STATE,
        algorithm_a="Expectimax",
        algorithm_b="Expectimax",
        settings=settings,
    )
    second = create_policy_comparison(
        start=START,
        goal=GOAL_STATE,
        algorithm_a="Expectimax",
        algorithm_b="Expectimax",
        settings=settings,
    )
    for _ in range(3):
        advance_policy_comparison(first)
        advance_policy_comparison(second)
    assert first.lane_a.history == second.lane_a.history
    assert first.lane_b.history == second.lane_b.history
    assert first.export_summary()["settings"] == second.export_summary()["settings"]


def test_lane_stops_on_turn_limit_and_export_contains_no_image_payload():
    comparison = create_policy_comparison(
        start=START,
        goal=GOAL_STATE,
        settings=Group6PolicySettings(depth=1, per_decision_timeout=5, max_turns=1),
    )
    advance_policy_comparison(comparison)
    advance_policy_comparison(comparison)
    assert comparison.lane_a.status in {"goal", "cycle", "turn_limit"}
    assert comparison.lane_b.status in {"goal", "cycle", "turn_limit"}
    encoded = str(comparison.export_summary()).lower()
    assert "base64" not in encoded
    assert "image" not in encoded
