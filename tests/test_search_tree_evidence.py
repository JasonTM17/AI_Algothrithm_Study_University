"""Tests for auditable solution and search-tree evidence."""

from algorithms.informed import a_star
from algorithms.uninformed import bfs
from core.metrics import search_tree_to_dot
from core.puzzle import _move_blank


START = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 0, 12, 13, 14, 11, 15)


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
    assert "h=-" in dot  # Root heuristic was not captured; the renderer never invents it.
    assert result.termination_reason == "goal"
    assert result.optimality_proven


def test_resource_limit_does_not_claim_exhaustive_failure():
    result = bfs(START, max_nodes=1, timeout=5)
    assert not result.success
    assert result.termination_reason == "resource_limit"
    assert not result.exhaustive_failure
    assert not result.optimality_proven
