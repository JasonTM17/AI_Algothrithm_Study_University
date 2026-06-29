"""Contracts for the four canonical bounded state-chain CSP algorithms."""

import pytest

from algorithms.csp import (
    backtracking_forward_checking,
    backtracking_search,
    constraint_propagation,
    min_conflicts,
)
from algorithms.csp_state_chain import build_state_chain_csp
from core.puzzle import GOAL_STATE, scramble


ONE_MOVE = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 0, 15)


@pytest.mark.parametrize(
    "solver, capability",
    [
        (backtracking_search, "csp_assignment_search"),
        (backtracking_forward_checking, "csp_assignment_search"),
        (constraint_propagation, "csp_propagation"),
        (min_conflicts, "csp_local_repair"),
    ],
)
def test_csp_algorithms_return_exact_one_move_chain(solver, capability):
    kwargs = {
        "start": ONE_MOVE,
        "goal": GOAL_STATE,
        "time_horizon": 1,
        "timeout": 5,
        "action_order": "LRUD",
    }
    if solver in {backtracking_search, backtracking_forward_checking}:
        kwargs["max_steps"] = 100
    if solver is min_conflicts:
        kwargs.update(max_iterations=100, seed=42)
    result = solver(**kwargs)
    assert result.success
    assert result.capability == capability
    assert result.path_verified and result.goal_reached
    assert result.path == [ONE_MOVE, GOAL_STATE]
    assert result.actions == ["R"]
    evidence = result.model_evidence
    assert evidence["horizon"] == 1
    assert evidence["variables"] == ["S[0]", "S[1]"]
    assert evidence["domain_sizes"] == [1, 1]
    assert evidence["complete_assignment"] == [list(ONE_MOVE), list(GOAL_STATE)]
    assert evidence["constraint_checks"]
    assert all(check["legal"] for check in evidence["constraint_checks"])


def test_forward_checking_does_not_try_more_assignments_than_backtracking():
    start = scramble(GOAL_STATE, depth=4, seed=8)
    plain = backtracking_search(
        start, time_horizon=4, max_steps=20_000, timeout=5
    )
    forward = backtracking_forward_checking(
        start, time_horizon=4, max_steps=20_000, timeout=5
    )
    assert plain.success and forward.success
    assert forward.model_evidence["assignments"] <= plain.model_evidence["assignments"]
    assert forward.model_evidence["values_pruned"] >= 0
    assert "partial_assignment" in forward.model_evidence
    assert "complete_assignment" in forward.model_evidence


def test_ac3_arc_consistency_has_support_for_every_remaining_value():
    start = scramble(GOAL_STATE, depth=3, seed=9)
    model = build_state_chain_csp(start, GOAL_STATE, horizon=3)
    result = constraint_propagation(start, time_horizon=3, timeout=5)
    assert result.termination_reason in {"goal", "arc_consistent"}
    assert result.model_evidence["arc_checks"] >= 1
    assert result.model_evidence["variables"] == ["S[0]", "S[1]", "S[2]", "S[3]"]
    assert len(result.model_evidence["domain_sizes"]) == 4
    assert any(step.event == "revise" for step in result.trace)
    for index in range(model.horizon):
        for left in model.domains[index]:
            assert any(model.compatible(left, right) for right in model.domains[index + 1])
        for right in model.domains[index + 1]:
            assert any(model.compatible(right, left) for left in model.domains[index])


@pytest.mark.parametrize(
    "solver, extra",
    [
        (backtracking_search, {"max_steps": 100}),
        (backtracking_forward_checking, {"max_steps": 100}),
        (constraint_propagation, {}),
        (min_conflicts, {"max_iterations": 100, "seed": 2}),
    ],
)
def test_wrong_horizon_is_bounded_failure_not_global_unsolvability(solver, extra):
    result = solver(
        ONE_MOVE,
        goal=GOAL_STATE,
        time_horizon=2,
        timeout=5,
        **extra,
    )
    assert not result.success
    assert result.termination_reason == "horizon_infeasible"
    assert "not a proof" in result.message


def test_min_conflicts_fixed_seed_is_reproducible():
    start = scramble(GOAL_STATE, depth=4, seed=3)
    kwargs = dict(
        start=start,
        goal=GOAL_STATE,
        time_horizon=4,
        max_iterations=200,
        timeout=5,
        seed=77,
    )
    first = min_conflicts(**kwargs)
    second = min_conflicts(**kwargs)
    assert first.success == second.success
    assert first.path == second.path
    assert first.actions == second.actions
    assert first.model_evidence == second.model_evidence
    if first.success:
        assert first.model_evidence["conflicts"] == 0
        assert first.model_evidence["complete_assignment"]
