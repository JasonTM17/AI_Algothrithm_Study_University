"""Certified shallow corpus for optimal solver cross-checks."""

import pytest

from algorithms.informed import a_star, ida_star
from algorithms.uninformed import bfs, ids, ucs
from core.puzzle import GOAL_STATE, PuzzleState


def _one_state_at_each_exact_depth(max_depth: int) -> dict[int, tuple[int, ...]]:
    distance = {GOAL_STATE: 0}
    representative = {0: GOAL_STATE}
    queue = [GOAL_STATE]
    for state in queue:
        depth = distance[state]
        if depth == max_depth:
            continue
        for neighbor, _, _ in PuzzleState(state).get_neighbors():
            if neighbor in distance:
                continue
            next_depth = depth + 1
            distance[neighbor] = next_depth
            representative.setdefault(next_depth, neighbor)
            queue.append(neighbor)
    return representative


CORPUS = _one_state_at_each_exact_depth(6)


@pytest.mark.parametrize("depth", range(7))
def test_optimal_solvers_match_certified_exact_distance(depth):
    state = CORPUS[depth]
    results = [
        bfs(state, timeout=5),
        ucs(state, timeout=5),
        ids(state, max_depth=depth + 2, timeout=5),
        a_star(state, heuristic="Linear Conflict", timeout=5),
        ida_star(state, heuristic="Linear Conflict", timeout=5),
    ]
    for result in results:
        assert result.success, (result.algorithm, result.message)
        assert result.cost == depth, result.algorithm
        assert len(result.actions) == depth
        assert result.path_verified, (result.algorithm, result.verification_message)
        assert result.optimality_proven, result.algorithm
