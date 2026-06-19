"""Tests for path-level comparison evidence."""

import pytest

from core.comparison import compact_action_path, shared_verified_paths, unique_verified_path_count
from core.metrics import SearchResult
from core.puzzle import GOAL_STATE, _move_blank


START = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 0, 15)


def _result(name: str, actions: list[str]) -> SearchResult:
    path = [START]
    state = START
    for action in actions:
        state = _move_blank(state, action)
        assert state is not None
        path.append(state)
    return SearchResult(
        success=True,
        algorithm=name,
        path=path,
        actions=actions,
        goal_state=path[-1],
    )


def test_compact_action_path_is_readable_and_bounded():
    assert compact_action_path([]) == "Start = Goal"
    assert compact_action_path(["L", "U"]) == "L → U"
    assert compact_action_path(["L", "U", "R"], max_actions=2) == "L → U … (+1)"
    with pytest.raises(ValueError):
        compact_action_path(["L"], max_actions=0)


def test_shared_paths_group_only_exact_verified_trajectories():
    bfs = _result("BFS", ["R"])
    ucs = _result("UCS", ["R"])
    detour = _result("DFS", ["U", "D", "R"])

    assert shared_verified_paths([bfs, ucs, detour]) == [("BFS", "UCS")]
    assert unique_verified_path_count([bfs, ucs, detour]) == 2


def test_unverified_paths_are_excluded_from_equivalence_claims():
    valid = _result("A*", ["R"])
    invalid = SearchResult(
        success=True,
        algorithm="Broken",
        path=[START, GOAL_STATE],
        actions=["L"],
        goal_state=GOAL_STATE,
    )

    assert not invalid.path_verified
    assert shared_verified_paths([valid, invalid]) == []
    assert unique_verified_path_count([valid, invalid]) == 1
