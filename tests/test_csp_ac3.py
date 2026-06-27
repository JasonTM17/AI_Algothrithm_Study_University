"""Academic correctness tests for bounded 15-puzzle AC-3 propagation."""

from algorithms.csp import (
    constraint_propagation,
    global_constraints,
    path_consistency,
    solve_csp_constraint_graphs,
)
from algorithms.csp_ac3 import run_state_chain_ac3
from core.puzzle import GOAL_STATE


ONE_MOVE = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 0, 15)


def test_ac3_finds_and_certifies_exact_one_move_chain():
    evidence = run_state_chain_ac3(
        ONE_MOVE,
        GOAL_STATE,
        time_horizon=1,
        action_order="LRUD",
    )
    result = constraint_propagation(
        ONE_MOVE,
        GOAL_STATE,
        time_horizon=1,
    )

    assert evidence.consistent
    assert evidence.actions == ["R"]
    assert result.success
    assert result.actions == ["R"]
    assert result.path_verified
    assert result.goal_reached
    assert "AC-3 State-Chain CSP" in result.message


def test_ac3_detects_exact_horizon_parity_domain_wipeout():
    evidence = run_state_chain_ac3(
        ONE_MOVE,
        GOAL_STATE,
        time_horizon=2,
    )
    result = constraint_propagation(
        ONE_MOVE,
        GOAL_STATE,
        time_horizon=2,
    )

    assert not evidence.consistent
    assert any(not domain for domain in evidence.domains)
    assert evidence.values_removed > 0
    assert not result.success
    assert result.termination_reason == "depth_limit"
    assert "Domain wipe-out" in result.message


def test_ac3_supports_custom_goal_and_longer_exact_chain():
    evidence = run_state_chain_ac3(
        GOAL_STATE,
        ONE_MOVE,
        time_horizon=3,
        action_order="LRUD",
    )
    result = constraint_propagation(
        GOAL_STATE,
        ONE_MOVE,
        time_horizon=3,
    )

    assert evidence.consistent
    assert len(evidence.actions) == 3
    assert result.goal_state == ONE_MOVE
    assert result.path_verified
    assert result.goal_reached


def test_csp_explanations_use_precise_variable_and_constraint_semantics():
    path_text = path_consistency(ONE_MOVE).message
    global_text = global_constraints(ONE_MOVE).message
    graph_text = solve_csp_constraint_graphs(ONE_MOVE, time_horizon=1).message

    assert "state-chain variables S[t]" in path_text
    assert "intermediate state S[1]" in path_text
    assert "120 undirected pairwise inequalities" in global_text
    assert "240 directed arcs" in global_text
    assert "high-arity transition constraint" in graph_text
    assert "connects A[t], X[t][0..15], and X[t+1][0..15]" in graph_text
