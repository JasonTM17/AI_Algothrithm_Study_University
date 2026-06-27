"""Tests for auditable solution and search-tree evidence."""

from algorithms.informed import a_star
from algorithms.csp import backtracking_search
from algorithms.local_search import (
    local_beam_search,
    random_restart_hill_climbing,
    simple_hill_climbing,
    simulated_annealing,
    steepest_ascent_hill_climbing,
    stochastic_hill_climbing,
)
from algorithms.uninformed import bfs
from core.metrics import SearchResult, TraceStep, search_tree_to_dot
from core.puzzle import GOAL_STATE, _move_blank
from ui.components import _search_tree_path_kind


START = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 0, 12, 13, 14, 11, 15)
ONE_MOVE = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 0, 15)


def assert_tree_is_legal(result):
    nodes = {node.node_id: node for node in result.search_tree_nodes}
    assert result.path_verified, result.verification_message
    assert result.search_tree_edges
    for edge in result.search_tree_edges:
        parent = nodes[edge.parent_id]
        child = nodes[edge.child_id]
        assert _move_blank(parent.state, edge.action) == child.state
        if edge.on_solution_path:
            assert parent.on_solution_path and child.on_solution_path


def test_bfs_exposes_real_parent_child_edges():
    result = bfs(START, timeout=5)
    assert_tree_is_legal(result)
    assert {event.event for event in result.trace} >= {"generate", "goal"}


def test_priority_frontier_snapshot_matches_pop_order():
    result = a_star(START, timeout=5)
    f_by_state = {event.state: event.f for event in result.trace}
    checked = False
    for event in result.trace:
        if len(event.frontier_states or []) > 1:
            values = [f_by_state[state] for state in event.frontier_states if state in f_by_state]
            if len(values) > 1:
                assert values == sorted(values)
                checked = True
                break
    assert checked


def test_a_star_exposes_real_parent_child_edges_and_dot():
    result = a_star(START, timeout=5)
    assert_tree_is_legal(result)
    dot = search_tree_to_dot(result)
    assert "digraph SearchTree" in dot
    assert "->" in dot
    assert 'color="#059669"' in dot
    assert "ranksep=0.85" in dot
    assert "fontsize=14" in dot
    assert "h=-" in dot  # Root heuristic was not captured; the renderer never invents it.
    assert result.termination_reason == "goal"
    assert result.goal_state == GOAL_STATE
    assert result.goal_reached
    assert result.optimality_proven
    assert _search_tree_path_kind(result) == "solution"


def test_local_search_exposes_generated_neighbor_edges():
    result = simple_hill_climbing(START, max_iterations=1, timeout=5)
    nodes = {node.node_id: node for node in result.search_tree_nodes}
    start_node = next(node for node in nodes.values() if node.state == START)
    generated_children = [
        edge for edge in result.search_tree_edges
        if edge.parent_id == start_node.node_id
    ]

    assert len(generated_children) > 1
    for edge in generated_children:
        child = nodes[edge.child_id]
        assert _move_blank(START, edge.action) == child.state


def test_local_search_tree_does_not_draw_reverse_arrow_to_parent():
    result = simple_hill_climbing(START, max_iterations=2, timeout=5)
    assert len(result.path) >= 2

    parent_state = result.path[0]
    child_state = result.path[1]
    nodes = {node.node_id: node for node in result.search_tree_nodes}
    reverse_edges = [
        edge for edge in result.search_tree_edges
        if nodes[edge.parent_id].state == child_state
        and nodes[edge.child_id].state == parent_state
    ]

    assert not reverse_edges


def test_all_local_search_variants_produce_legal_search_tree_edges():
    cases = [
        simple_hill_climbing(START, max_iterations=2, timeout=5),
        steepest_ascent_hill_climbing(START, max_iterations=2, timeout=5),
        stochastic_hill_climbing(START, max_iterations=2, timeout=5, seed=1),
        random_restart_hill_climbing(START, max_iterations=2, max_restarts=1, timeout=5, seed=1),
        local_beam_search(START, beam_width=2, max_iterations=2, timeout=5),
        simulated_annealing(START, max_iterations=2, timeout=5, seed=1),
    ]

    for result in cases:
        nodes = {node.node_id: node for node in result.search_tree_nodes}
        assert result.search_tree_edges, result.algorithm
        assert result.nodes_generated > result.nodes_expanded
        for edge in result.search_tree_edges:
            parent = nodes[edge.parent_id]
            child = nodes[edge.child_id]
            assert _move_blank(parent.state, edge.action) == child.state


def test_backtracking_search_exposes_generated_child_edges_without_reverse_parent_arrow():
    result = backtracking_search(START, max_steps=50, timeout=5)
    nodes = {node.node_id: node for node in result.search_tree_nodes}

    assert result.search_tree_edges
    assert result.nodes_generated > result.nodes_expanded
    for edge in result.search_tree_edges:
        parent = nodes[edge.parent_id]
        child = nodes[edge.child_id]
        assert _move_blank(parent.state, edge.action) == child.state

    if len(result.path) >= 2:
        parent_state = result.path[0]
        child_state = result.path[1]
        reverse_edges = [
            edge for edge in result.search_tree_edges
            if nodes[edge.parent_id].state == child_state
            and nodes[edge.child_id].state == parent_state
        ]
        assert not reverse_edges


def test_solution_highlight_requires_exact_recorded_action_edge():
    left_detour = _move_blank(ONE_MOVE, "L")
    result = SearchResult(
        success=True,
        algorithm="Loop Highlight Probe",
        path=[ONE_MOVE, left_detour, ONE_MOVE, GOAL_STATE],
        actions=["L", "R", "R"],
        goal_state=GOAL_STATE,
        trace=[
            TraceStep(
                step=1,
                node_state=GOAL_STATE,
                state=ONE_MOVE,
                action="L",
                reason="Legal reverse edge between solution states, not a solution step.",
            ),
        ],
    )

    nodes = {node.node_id: node for node in result.search_tree_nodes}
    reverse_edges = [
        edge for edge in result.search_tree_edges
        if nodes[edge.parent_id].state == GOAL_STATE and nodes[edge.child_id].state == ONE_MOVE
    ]

    assert result.path_verified
    assert result.goal_reached
    assert reverse_edges
    assert all(not edge.on_solution_path for edge in reverse_edges)


def test_resource_limit_does_not_claim_exhaustive_failure():
    result = bfs(START, max_nodes=1, timeout=5)
    assert not result.success
    assert result.termination_reason == "resource_limit"
    assert not result.exhaustive_failure
    assert not result.optimality_proven


def test_failed_run_can_certify_a_legal_partial_trajectory():
    child = _move_blank(START, "D")
    result = SearchResult(
        success=False,
        algorithm="Partial Trajectory Probe",
        path=[START, child],
        actions=["D"],
        goal_state=GOAL_STATE,
        message="Stopped before goal",
    )

    assert result.path_verified
    assert not result.goal_reached
    assert not result.optimality_proven
    assert result.summary_dict()["Path Length"] == 1
    assert len(result.search_tree_edges) == 1
    assert not result.search_tree_edges[0].on_solution_path
    assert all(not node.on_solution_path for node in result.search_tree_nodes)
    assert _search_tree_path_kind(result) == "trajectory"


def test_path_certificate_is_legal_path_not_goal_claim():
    child = _move_blank(START, "D")
    result = SearchResult(
        success=True,
        algorithm="Certificate Probe",
        path=[START, child],
        actions=["D"],
    )

    assert child != START
    assert result.path_verified
    assert not result.goal_reached
    assert "legal state/action sequence" in result.verification_message
    assert "reaches the goal" not in result.verification_message
    assert result.summary_dict()["Legal Path?"] == "Yes"
    assert result.summary_dict()["Reached Goal?"] == "Not reported"
    assert "Path Verified?" not in result.summary_dict()
    assert _search_tree_path_kind(result) == "trajectory"


def test_model_only_success_does_not_report_goal_termination():
    result = SearchResult(
        success=True,
        algorithm="CSP Definition",
        message="CSP variables and constraints described.",
    )

    assert result.termination_reason == "model_success"
    assert not result.goal_reached
    assert not result.optimality_proven


def test_optimality_certificate_requires_a_reported_goal():
    child = _move_blank(START, "D")
    result = SearchResult(
        success=True,
        algorithm="Missing Goal Probe",
        path=[START, child],
        actions=["D"],
        is_optimal=True,
    )

    assert result.path_verified
    assert not result.goal_reached
    assert not result.optimality_proven
    assert "goal was not reported" in result.verification_message


def test_optimality_certificate_requires_reported_goal_match():
    child = _move_blank(START, "D")
    result = SearchResult(
        success=True,
        algorithm="Bad Proof Probe",
        path=[START, child],
        actions=["D"],
        goal_state=START,
        is_optimal=True,
    )

    assert result.path_verified
    assert not result.goal_reached
    assert not result.optimality_proven
    assert "does not match the requested goal" in result.verification_message
    assert result.summary_dict()["Reached Goal?"] == "No"


def test_explicit_termination_reason_is_preserved():
    result = SearchResult(
        success=True,
        algorithm="Contextual Success",
        termination_reason="valid_coloring",
    )

    assert result.termination_reason == "valid_coloring"
    assert not result.optimality_proven
