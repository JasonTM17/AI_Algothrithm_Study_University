"""Academic contracts for the three complex-environment models."""

import random

import pytest

from algorithms.belief_search import (
    BeliefState,
    conformant_belief_search,
    contingent_belief_search,
    observe_blank_and_neighbors,
    partition_by_observation,
    predict_belief,
)
from algorithms.complex_env import (
    AND_OR_EXPANSION_CAP,
    _build_belief_from_known_positions,
    and_or_search,
    default_known_positions,
    format_known_positions_matrix,
    no_observation_search,
    parse_known_positions_matrix,
    partially_observable_search,
)
from core.puzzle import GOAL_STATE, _move_blank, scramble


ONE_MOVE = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 0, 15)


def test_zero_known_tiles_produces_an_empty_observation():
    assert default_known_positions(ONE_MOVE, 0) == {}


def test_known_positions_matrix_round_trip_and_unknown_cells():
    known = parse_known_positions_matrix(
        "1 _ _ _\n_ 6 _ _\n_ _ 11 _\n_ _ _ _"
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
def test_known_positions_matrix_rejects_invalid_clues(matrix, expected_message):
    with pytest.raises(ValueError, match=expected_message):
        parse_known_positions_matrix(matrix)


def test_and_or_deterministic_support_finds_conditional_plan():
    result = and_or_search(ONE_MOVE, GOAL_STATE, max_depth=1, nondet_prob=0.0)
    assert result.success
    assert result.capability == "conditional_plan"
    assert result.termination_reason == "model_success"
    assert result.model_evidence["conditional_plan"]
    assert not result.path
    assert not result.uses_probability
    assert "not probability-weighted" in result.message


def test_and_or_trivial_goal_is_success_even_with_zero_timeout():
    result = and_or_search(GOAL_STATE, GOAL_STATE, max_depth=0, timeout=0.0)

    assert result.success
    assert result.termination_reason == "model_success"
    assert result.model_evidence["conditional_plan"]["type"] == "goal"


@pytest.mark.parametrize(
    "goal",
    (
        GOAL_STATE,
        ONE_MOVE,
        scramble(goal=GOAL_STATE, depth=5, seed=731),
    ),
)
@pytest.mark.parametrize("depth", range(0, 6))
@pytest.mark.deep_algorithm_audit
def test_and_or_intended_support_handles_multiple_start_goal_pairs(goal, depth):
    start = scramble(goal=goal, depth=depth, seed=9_000 + depth)
    result = and_or_search(
        start,
        goal=goal,
        max_depth=max(1, depth + 2),
        nondet_prob=0.0,
        timeout=5,
        action_order="LRUD",
    )

    assert result.success
    assert result.goal_state == goal
    assert result.capability == "conditional_plan"
    assert result.model_evidence["conditional_plan"]
    assert not result.path
    assert not result.goal_reached
    assert not result.optimality_proven


@pytest.mark.parametrize(
    "goal",
    (
        GOAL_STATE,
        ONE_MOVE,
        scramble(goal=GOAL_STATE, depth=5, seed=731),
    ),
)
@pytest.mark.deep_algorithm_audit
def test_and_or_deflection_support_stops_honestly_when_depth_is_insufficient(goal):
    start = scramble(goal=goal, depth=1, seed=9_101)
    result = and_or_search(
        start,
        goal=goal,
        max_depth=2,
        nondet_prob=1.0,
        timeout=2,
        action_order="LRUD",
    )

    assert not result.success
    assert result.goal_state == goal
    assert result.capability == "conditional_plan"
    assert result.termination_reason == "depth_limit"
    assert not result.goal_reached
    assert not result.optimality_proven


def test_and_or_requires_every_supported_outcome():
    result = and_or_search(ONE_MOVE, GOAL_STATE, max_depth=1, nondet_prob=1.0)
    assert not result.success
    assert result.nodes_expanded > 0
    assert "every supported outcome" in result.message
    trace_text = " ".join(step.reason for step in result.trace)
    assert "not a probability weight" in trace_text


def test_and_or_resource_limit_is_not_false_impossibility_proof():
    start = scramble(GOAL_STATE, depth=10, seed=42)
    result = and_or_search(
        start, GOAL_STATE, max_depth=20, nondet_prob=1.0, timeout=30
    )
    assert not result.success
    assert result.nodes_expanded == AND_OR_EXPANSION_CAP
    assert result.termination_reason == "resource_limit"
    assert "before proving or disproving" in result.message


@pytest.mark.parametrize("support", [-0.1, 1.1])
def test_and_or_rejects_invalid_support_switch(support):
    with pytest.raises(ValueError):
        and_or_search(ONE_MOVE, nondet_prob=support)


def test_predict_belief_uses_documented_illegal_action_noop():
    belief = BeliefState({GOAL_STATE, ONE_MOVE})
    predicted = predict_belief(belief, "R")
    assert GOAL_STATE in predicted  # R is illegal at the goal, so it is a no-op.
    assert _move_blank(ONE_MOVE, "R") in predicted


def test_belief_builder_can_represent_goal_when_clues_require_it():
    belief = _build_belief_from_known_positions(
        GOAL_STATE,
        GOAL_STATE,
        1,
        random.Random(0),
        {index: value for index, value in enumerate(GOAL_STATE)},
        include_hidden=False,
    )

    assert belief == {GOAL_STATE}


def test_observation_partitions_are_disjoint_and_cover_prediction():
    belief = BeliefState({GOAL_STATE, ONE_MOVE, scramble(GOAL_STATE, 2, seed=9)})
    predicted = predict_belief(belief, "L")
    partitions = partition_by_observation(predicted)
    values = list(partitions.values())
    assert set().union(*map(set, values)) == set(predicted)
    for index, left in enumerate(values):
        for right in values[index + 1:]:
            assert left.isdisjoint(right)
    for observation, states in partitions.items():
        assert all(observe_blank_and_neighbors(state) == observation for state in states)


def test_no_observation_singleton_returns_conformant_sequence_not_hidden_path():
    result = no_observation_search(
        ONE_MOVE,
        num_belief_states=1,
        max_steps=1,
        timeout=5,
        action_order="RULD",
        seed=123,
        known_positions={index: value for index, value in enumerate(ONE_MOVE)},
    )
    assert result.success
    assert result.actions == ["R"]
    assert result.capability == "conformant_plan"
    assert not result.path
    assert result.model_evidence["hidden_state_used_for_policy"] is False
    assert result.model_evidence["illegal_action_semantics"] == "no-op"


def test_conformant_belief_search_processes_goal_at_exact_belief_cap():
    outcome = conformant_belief_search(
        BeliefState({ONE_MOVE}),
        GOAL_STATE,
        max_depth=1,
        max_beliefs=2,
        timeout=5,
        action_order="R",
    )

    assert outcome.success
    assert outcome.termination_reason == "model_success"
    assert outcome.actions == ["R"]
    assert outcome.reached_size == 2


def test_conformant_trivial_goal_is_success_even_with_zero_timeout():
    outcome = conformant_belief_search(
        BeliefState({GOAL_STATE}),
        GOAL_STATE,
        max_depth=0,
        max_beliefs=1,
        timeout=0.0,
        action_order="LRUD",
    )

    assert outcome.success
    assert outcome.termination_reason == "model_success"
    assert outcome.actions == []


@pytest.mark.parametrize("solver", [no_observation_search, partially_observable_search])
def test_belief_search_rejects_known_positions_that_contradict_start(solver):
    result = solver(
        ONE_MOVE,
        num_belief_states=1,
        max_steps=1,
        timeout=5,
        seed=42,
        known_positions={0: 9},
    )
    assert not result.success
    assert result.termination_reason == "invalid_input"
    assert result.model_evidence["known_positions"] == {0: 9}
    assert result.model_evidence["hidden_state_used_for_policy"] is False
    assert result.model_evidence["initial_belief"]["size"] == 0
    assert "contradict" in result.message


@pytest.mark.parametrize("solver", [no_observation_search, partially_observable_search])
def test_belief_search_rejects_unsolvable_hidden_start_before_sampling(solver):
    unsolvable_start = (2, 1, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 0, 15)
    partial_clues = {index: unsolvable_start[index] for index in range(2, 16)}

    result = solver(
        unsolvable_start,
        GOAL_STATE,
        num_belief_states=1,
        max_steps=1,
        timeout=5,
        action_order="RULD",
        seed=7,
        known_positions=partial_clues,
    )

    assert not result.success
    assert result.termination_reason == "unsolvable"
    assert result.model_evidence["initial_belief"]["size"] == 0
    assert result.model_evidence["hidden_state_used_for_policy"] is False
    assert "not solvable" in result.message


def test_conformant_plan_replays_on_every_initial_belief_state():
    result = no_observation_search(
        ONE_MOVE,
        num_belief_states=1,
        max_steps=1,
        timeout=5,
        action_order="RULD",
        seed=7,
        known_positions={index: value for index, value in enumerate(ONE_MOVE)},
    )
    initial_states = result.model_evidence["initial_belief"]["sample"]
    for raw_state in initial_states:
        state = tuple(raw_state)
        for action in result.actions:
            state = _move_blank(state, action) or state
        assert state == GOAL_STATE


def test_no_observation_bounded_failure_is_not_global_impossibility():
    result = no_observation_search(
        ONE_MOVE,
        num_belief_states=3,
        max_steps=0,
        timeout=5,
        seed=11,
    )
    assert not result.success
    assert result.termination_reason == "depth_limit"
    assert "not a global impossibility proof" in result.message


def test_partial_observation_returns_policy_not_linear_path():
    result = partially_observable_search(
        ONE_MOVE,
        num_belief_states=1,
        max_steps=1,
        timeout=5,
        action_order="RULD",
        seed=42,
        known_positions={index: value for index, value in enumerate(ONE_MOVE)},
    )
    assert result.success
    assert result.capability == "contingent_policy"
    assert result.model_evidence["policy"]["type"] == "OR"
    assert "predicted_belief" in result.model_evidence["policy"]
    assert result.model_evidence["observation_partitions"]
    assert result.model_evidence["updated_beliefs"]
    assert result.model_evidence["hidden_state_used_for_policy"] is False
    assert not result.path


def test_partial_observation_start_at_goal_returns_goal_policy():
    result = partially_observable_search(
        GOAL_STATE,
        num_belief_states=1,
        max_steps=0,
        timeout=5,
        seed=99,
    )
    assert result.success
    assert result.model_evidence["policy"]["type"] == "goal"


def test_contingent_belief_search_rejects_empty_initial_belief():
    outcome = contingent_belief_search(
        BeliefState(),
        GOAL_STATE,
        max_depth=0,
        max_beliefs=10,
        timeout=5,
        action_order="LRUD",
    )

    assert not outcome.success
    assert outcome.termination_reason == "invalid_belief"
    assert outcome.evidence["initial_belief"]["size"] == 0


def test_contingent_trivial_goal_is_success_even_with_zero_timeout():
    outcome = contingent_belief_search(
        BeliefState({GOAL_STATE}),
        GOAL_STATE,
        max_depth=0,
        max_beliefs=1,
        timeout=0.0,
        action_order="LRUD",
    )

    assert outcome.success
    assert outcome.termination_reason == "model_success"
    assert outcome.evidence["policy"]["type"] == "goal"


@pytest.mark.parametrize("solver", [no_observation_search, partially_observable_search])
def test_belief_search_timeout_is_structured(solver):
    result = solver(
        ONE_MOVE,
        num_belief_states=2,
        max_steps=20,
        timeout=0.0,
        seed=7,
    )
    assert not result.success
    assert result.nodes_expanded == 0
    assert result.termination_reason == "timeout"
    assert result.goal_state == GOAL_STATE
