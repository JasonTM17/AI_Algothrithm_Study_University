"""Play/Compare runner contract for linear puzzle trajectories."""

from __future__ import annotations

import pytest

from core.puzzle import GOAL_STATE, _move_blank
from core.randomness import RANDOMIZED_SOLVERS
from ui.path_solver_runner import (
    PATH_ALGORITHM_BY_NAME,
    PATH_ALGORITHM_GROUPS,
    PathRunSettings,
    run_path_algorithm,
)


ONE_MOVE = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 0, 15)
MULTI_PATH = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 0, 15, 13, 14, 12, 11)
EXPECTED_GROUPS = {
    "Uninformed Search": ("BFS", "DFS", "UCS", "IDS"),
    "Informed Search": ("Greedy Best-First", "A*", "IDA*"),
    "Local Search": (
        "Simple Hill Climbing",
        "Steepest-Ascent Hill Climbing",
        "Stochastic Hill Climbing",
        "Random-Restart Hill Climbing",
        "Local Beam Search",
        "Simulated Annealing",
    ),
}


def _assert_legal_path(result, start: tuple[int, ...]) -> None:
    assert result.path[0] == start
    assert len(result.path) == len(result.actions) + 1
    current = start
    for action, recorded in zip(result.actions, result.path[1:]):
        current = _move_blank(current, action)
        assert current is not None
        assert current == recorded


def test_path_algorithm_registry_contains_only_play_linear_algorithms():
    assert PATH_ALGORITHM_GROUPS == EXPECTED_GROUPS
    assert set(PATH_ALGORITHM_BY_NAME) == {
        algorithm
        for algorithms in EXPECTED_GROUPS.values()
        for algorithm in algorithms
    }
    assert len(PATH_ALGORITHM_BY_NAME) == 13
    assert "AND-OR Search" not in PATH_ALGORITHM_BY_NAME
    assert "Minimax" not in PATH_ALGORITHM_BY_NAME
    assert "AI-vs-AI Tournament" not in PATH_ALGORITHM_BY_NAME


@pytest.mark.parametrize("algorithm", PATH_ALGORITHM_BY_NAME)
def test_path_runner_solves_one_move_contract_for_each_play_algorithm(algorithm: str):
    settings = PathRunSettings(timeout=2, max_nodes=1_000, max_depth=5, seed=99)

    result = run_path_algorithm(
        algorithm,
        start=ONE_MOVE,
        goal=GOAL_STATE,
        settings=settings,
    )

    assert result.algorithm == algorithm
    assert result.goal_state == GOAL_STATE
    assert result.path_verified
    assert result.goal_reached
    assert result.actions == ["R"]
    assert result.path[-1] == GOAL_STATE
    assert result.runtime >= 0
    _assert_legal_path(result, ONE_MOVE)

    spec = PATH_ALGORITHM_BY_NAME[algorithm]
    expected_seed = settings.seed if spec.function_name in RANDOMIZED_SOLVERS else None
    assert result.random_seed == expected_seed


def test_path_runner_rejects_non_linear_extension_algorithms():
    with pytest.raises(ValueError, match="Unsupported path algorithm"):
        run_path_algorithm("AND-OR Search", start=ONE_MOVE, goal=GOAL_STATE)


def test_path_runner_respects_action_order_for_equal_cost_paths():
    lrud = run_path_algorithm(
        "BFS",
        start=MULTI_PATH,
        goal=GOAL_STATE,
        settings=PathRunSettings(action_order="LRUD", timeout=2, max_nodes=5_000),
    )
    drul = run_path_algorithm(
        "BFS",
        start=MULTI_PATH,
        goal=GOAL_STATE,
        settings=PathRunSettings(action_order="DRUL", timeout=2, max_nodes=5_000),
    )

    assert lrud.path_verified and lrud.goal_reached
    assert drul.path_verified and drul.goal_reached
    assert lrud.actions == ["R", "D", "L", "U", "R", "D"]
    assert drul.actions == ["D", "R", "U", "L", "D", "R"]
    assert lrud.actions != drul.actions
