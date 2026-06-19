"""Academic contracts for extension environment models."""

import pytest

from algorithms.complex_env import and_or_search
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
