"""Academic contracts for extension environment models."""

import pytest

from algorithms.complex_env import and_or_search, no_observation_search, partially_observable_search
from core.puzzle import GOAL_STATE


ONE_MOVE = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 0, 15)


def test_and_or_deterministic_support_finds_one_step_conditional_plan():
    result = and_or_search(ONE_MOVE, GOAL_STATE, max_depth=1, nondet_prob=0.0)
    assert result.success
    assert result.nodes_expanded > 0
    assert result.nodes_generated > 1
    assert not result.uses_probability


def test_and_or_requires_all_supported_outcomes_to_succeed():
    result = and_or_search(ONE_MOVE, GOAL_STATE, max_depth=1, nondet_prob=0.3)
    assert not result.success
    assert result.nodes_expanded > 0


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
