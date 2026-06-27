"""Academic contracts for extension environment models."""

import pytest

from algorithms.complex_env import (
    and_or_search,
    default_known_positions,
    format_known_positions_matrix,
    no_observation_search,
    online_search_lrta,
    parse_known_positions_matrix,
    partially_observable_search,
)
from core.puzzle import GOAL_STATE


ONE_MOVE = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 0, 15)


def test_zero_known_tiles_produces_an_empty_observation():
    assert default_known_positions(ONE_MOVE, 0) == {}


def test_known_positions_matrix_parses_visible_tiles_and_ignores_unknown_cells():
    known = parse_known_positions_matrix(
        "1 _ _ _\n"
        "_ 6 _ _\n"
        "_ _ 11 _\n"
        "_ _ _ _"
    )

    assert known == {0: 1, 5: 6, 10: 11}
    assert parse_known_positions_matrix(format_known_positions_matrix(known)) == known


@pytest.mark.parametrize(
    "matrix, expected_message",
    [
        ("1 _ _ _\n_ 1 _ _\n_ _ _ _\n_ _ _ _", "unique"),
        ("1 _ _\n_ _ _ _\n_ _ _ _\n_ _ _ _", "four values"),
        ("1 _ _ _\n_ _ _ _\n_ _ _ _", "four rows"),
        ("16 _ _ _\n_ _ _ _\n_ _ _ _\n_ _ _ _", "0..15"),
    ],
)
def test_known_positions_matrix_rejects_invalid_academic_clues(matrix, expected_message):
    with pytest.raises(ValueError, match=expected_message):
        parse_known_positions_matrix(matrix)


def test_and_or_deterministic_support_finds_one_step_conditional_plan():
    result = and_or_search(ONE_MOVE, GOAL_STATE, max_depth=1, nondet_prob=0.0)
    assert result.success
    assert result.nodes_expanded > 0
    assert result.nodes_generated > 1
    assert not result.uses_probability
    assert "intended outcome only" in result.message
    assert "not probability-weighted" in result.message


def test_and_or_requires_all_supported_outcomes_to_succeed():
    result = and_or_search(ONE_MOVE, GOAL_STATE, max_depth=1, nondet_prob=0.3)
    assert not result.success
    assert result.nodes_expanded > 0
    assert "include all legal deflections" in result.message
    assert "every supported outcome" in result.message


def test_and_or_trace_treats_nondet_prob_as_support_switch():
    result = and_or_search(ONE_MOVE, GOAL_STATE, max_depth=1, nondet_prob=1.0)

    trace_text = " ".join(step.reason for step in result.trace)
    assert "binary support switch" in trace_text
    assert "not a probability weight" in trace_text


@pytest.mark.parametrize("probability", [-0.1, 1.1])
def test_and_or_rejects_invalid_support_probability(probability):
    with pytest.raises(ValueError):
        and_or_search(ONE_MOVE, nondet_prob=probability)


def test_no_observation_binds_heuristic_to_custom_goal():
    custom_goal = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 0, 15)
    result = no_observation_search(
        GOAL_STATE,
        goal=custom_goal,
        num_belief_states=1,
        max_steps=1,
        timeout=5,
        action_order="LRUD",
    )

    assert result.success
    assert result.actions == ["L"]
    assert result.path[-1] == custom_goal
    assert result.goal_state == custom_goal
    assert result.random_seed is None
    assert result.uses_randomness
    assert result.path_verified


def test_no_observation_records_seed_for_reproducible_belief_generation():
    first = no_observation_search(
        ONE_MOVE,
        num_belief_states=1,
        max_steps=1,
        timeout=5,
        seed=123,
    )
    second = no_observation_search(
        ONE_MOVE,
        num_belief_states=1,
        max_steps=1,
        timeout=5,
        seed=123,
    )

    assert first.random_seed == second.random_seed == 123
    assert first.actions == second.actions
    assert first.path == second.path
    assert first.goal_state == GOAL_STATE
    assert first.path_verified


def test_no_observation_trace_tracks_hidden_state_after_a_legal_blind_action():
    result = no_observation_search(
        ONE_MOVE,
        num_belief_states=1,
        max_steps=1,
        timeout=5,
        seed=123,
    )

    assert result.path == [ONE_MOVE, GOAL_STATE]
    assert result.trace[-1].state == result.path[-1]
    assert "decision itself uses belief" in result.trace[-1].reason


def test_no_observation_reconstructs_belief_from_known_tiles_and_group_planner():
    known = default_known_positions(ONE_MOVE, 2)
    result = no_observation_search(
        ONE_MOVE,
        num_belief_states=4,
        max_steps=1,
        timeout=5,
        seed=123,
        known_positions=known,
        belief_planner="BFS",
    )

    reasons = " ".join(step.reason for step in result.trace)
    assert result.trace[0].belief_size >= 1
    assert "known positions=2" in reasons
    assert "planner=BFS" in reasons
    assert "Blind action" in reasons
    assert result.random_seed == 123


def test_belief_planner_trace_reports_successful_planner_votes():
    result = no_observation_search(
        ONE_MOVE,
        num_belief_states=1,
        max_steps=1,
        timeout=5,
        seed=123,
        belief_planner="BFS",
    )

    reasons = " ".join(step.reason for step in result.trace)
    assert "planner_votes=" in reasons
    assert "fallback_votes={'L': 0, 'R': 0, 'U': 0, 'D': 0}" in reasons
    assert "fallback_reason=none" in reasons


def test_belief_planner_trace_reports_exception_fallback(monkeypatch):
    def broken_bfs(*args, **kwargs):
        raise RuntimeError("test planner failure")

    monkeypatch.setattr("algorithms.uninformed.bfs", broken_bfs)
    result = no_observation_search(
        ONE_MOVE,
        num_belief_states=1,
        max_steps=1,
        timeout=5,
        seed=123,
        belief_planner="BFS",
    )

    reasons = " ".join(step.reason for step in result.trace)
    assert "planner_votes={'L': 0, 'R': 0, 'U': 0, 'D': 0}" in reasons
    assert "fallback_votes=" in reasons
    assert "fallback_reason=planner=BFS raised RuntimeError" in reasons


def test_partially_observable_search_returns_certified_actual_trajectory():
    result = partially_observable_search(
        ONE_MOVE,
        num_belief_states=1,
        max_steps=1,
        timeout=5,
        action_order="RULD",
        seed=42,
    )

    assert result.success
    assert result.actions == ["R"]
    assert result.path == [ONE_MOVE, GOAL_STATE]
    assert result.goal_state == GOAL_STATE
    assert result.random_seed == 42
    assert result.uses_randomness
    assert result.path_verified
    assert result.goal_reached


def test_partial_observation_uses_known_tiles_and_collapses_to_reconstructed_state():
    result = partially_observable_search(
        ONE_MOVE,
        num_belief_states=4,
        max_steps=2,
        timeout=5,
        action_order="RULD",
        seed=42,
        known_positions=default_known_positions(ONE_MOVE, 2),
        belief_planner="A* Search",
    )

    reasons = " ".join(step.reason for step in result.trace)
    assert "known positions=2" in reasons
    assert "planner=A* Search" in reasons
    assert result.path_verified


def test_partially_observable_search_certifies_start_at_goal():
    result = partially_observable_search(
        GOAL_STATE,
        num_belief_states=1,
        max_steps=0,
        timeout=5,
        seed=99,
    )

    assert result.success
    assert result.actions == []
    assert result.path == [GOAL_STATE]
    assert result.goal_state == GOAL_STATE
    assert result.random_seed == 99
    assert result.path_verified
    assert result.goal_reached


@pytest.mark.parametrize("solver", [no_observation_search, partially_observable_search])
def test_belief_generators_scramble_from_custom_goal_parity(solver):
    swapped_goal = (2, 1, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 0)
    result = solver(
        swapped_goal,
        goal=swapped_goal,
        num_belief_states=2,
        max_steps=0,
        timeout=1,
        seed=7,
    )

    assert result.runtime < 1
    assert result.nodes_expanded == 0


@pytest.mark.parametrize("solver", [no_observation_search, partially_observable_search])
def test_belief_search_timeout_reports_actual_completed_steps(solver):
    result = solver(
        ONE_MOVE,
        num_belief_states=2,
        max_steps=20,
        timeout=0.0,
        seed=7,
    )

    assert result.nodes_expanded == 0
    assert result.nodes_generated == 0
    assert result.termination_reason == "timeout"
    assert "Timeout after 0" in result.message


def test_lrta_success_reports_requested_goal_certificate():
    result = online_search_lrta(
        ONE_MOVE,
        goal=GOAL_STATE,
        max_steps=5,
        timeout=5,
        action_order="RULD",
    )

    assert result.success
    assert result.goal_state == GOAL_STATE
    assert result.path_verified
    assert result.goal_reached
