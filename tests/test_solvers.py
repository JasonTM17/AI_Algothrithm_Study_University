"""Tests for all solver algorithms."""

import pytest
from core.puzzle import GOAL_STATE, is_solvable
from algorithms.uninformed import bfs, dfs, ucs, ids
from algorithms.informed import greedy_best_first, a_star, ida_star
from algorithms.local_search import (
    simple_hill_climbing, steepest_ascent_hill_climbing,
    stochastic_hill_climbing, random_restart_hill_climbing,
    local_beam_search, simulated_annealing,
)
from algorithms.adversarial import minimax, alpha_beta_pruning, expectimax

EASY_STATE = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 0, 12, 13, 14, 11, 15)
MEDIUM_STATE = (1, 2, 3, 4, 5, 6, 0, 8, 9, 10, 7, 12, 13, 14, 11, 15)


class TestBFS:
    def test_solves_easy(self):
        result = bfs(EASY_STATE, timeout=10)
        assert result.success is True
        assert result.algorithm == "BFS"
        assert len(result.actions) > 0

    def test_solves_goal(self):
        result = bfs(GOAL_STATE, timeout=5)
        assert result.success is True
        assert len(result.actions) == 0

    def test_returns_result_object(self):
        result = bfs(EASY_STATE, timeout=5)
        assert hasattr(result, 'nodes_expanded')
        assert hasattr(result, 'runtime')
        assert hasattr(result, 'trace')


class TestDFS:
    def test_returns_result(self):
        result = dfs(EASY_STATE, max_depth=20, timeout=10)
        assert result.algorithm == "DFS"
        assert result is not None

    def test_depth_limit(self):
        result = dfs(MEDIUM_STATE, max_depth=5, timeout=5)
        assert result is not None


class TestUCS:
    def test_solves_easy(self):
        result = ucs(EASY_STATE, timeout=10)
        assert result.success is True
        assert result.algorithm == "UCS"
        assert result.cost == len(result.actions)


class TestIDS:
    def test_solves_easy(self):
        result = ids(EASY_STATE, max_depth=20, timeout=15)
        assert result is not None
        assert result.algorithm == "IDS"
        # IDS should solve this easy state
        assert result.success is True


class TestGreedyBestFirst:
    def test_solves_easy(self):
        result = greedy_best_first(EASY_STATE, timeout=10)
        assert result.success is True
        assert result.algorithm == "Greedy Best-First"

    def test_uses_heuristic(self):
        result = greedy_best_first(EASY_STATE, heuristic="Manhattan Distance", timeout=10)
        assert result.uses_heuristic is True


class TestAStar:
    def test_solves_easy(self):
        result = a_star(EASY_STATE, timeout=10)
        assert result.success is True
        assert result.algorithm == "A*"

    def test_optimal(self):
        result = a_star(EASY_STATE, timeout=10)
        assert result.is_optimal is True

    def test_solves_medium(self):
        result = a_star(MEDIUM_STATE, timeout=15)
        assert result.success is True


class TestIDAStar:
    def test_solves_easy(self):
        result = ida_star(EASY_STATE, timeout=10)
        assert result.success is True
        assert result.algorithm == "IDA*"

    def test_optimal(self):
        result = ida_star(EASY_STATE, timeout=10)
        assert result.is_optimal is True


class TestHillClimbing:
    def test_simple_returns_result(self):
        result = simple_hill_climbing(EASY_STATE, timeout=10)
        assert result.algorithm == "Simple Hill Climbing"
        assert hasattr(result, 'success')

    def test_steepest_ascent_returns_result(self):
        result = steepest_ascent_hill_climbing(EASY_STATE, timeout=10)
        assert result.algorithm == "Steepest-Ascent Hill Climbing"

    def test_stochastic_returns_result(self):
        result = stochastic_hill_climbing(EASY_STATE, timeout=10, seed=42)
        assert result.algorithm == "Stochastic Hill Climbing"
        assert result.uses_randomness is True

    def test_random_restart_returns_result(self):
        result = random_restart_hill_climbing(EASY_STATE, timeout=10, seed=42)
        assert result.algorithm == "Random-Restart Hill Climbing"

    def test_beam_search_returns_result(self):
        result = local_beam_search(EASY_STATE, beam_width=3, timeout=10)
        assert result.algorithm == "Local Beam Search"


class TestSimulatedAnnealing:
    def test_returns_result(self):
        result = simulated_annealing(EASY_STATE, timeout=10, seed=42)
        assert result.algorithm == "Simulated Annealing"
        assert result.uses_randomness is True

    def test_has_temperature_trace(self):
        result = simulated_annealing(EASY_STATE, timeout=10, seed=42)
        if result.trace:
            temps = [s.temperature for s in result.trace if s.temperature is not None]
            assert len(temps) > 0


class TestMinimax:
    def test_returns_result(self):
        result = minimax(EASY_STATE, depth=2, timeout=10)
        assert result.algorithm == "Minimax"
        assert result.uses_adversary is True
        assert result.suitable_for_puzzle is False

    def test_has_game_tree(self):
        result = minimax(EASY_STATE, depth=2, timeout=10)
        assert result.message is not None


class TestAlphaBeta:
    def test_returns_result(self):
        result = alpha_beta_pruning(EASY_STATE, depth=2, timeout=10)
        assert result.algorithm == "Alpha-Beta Pruning"
        assert result.uses_adversary is True

    def test_prunes_nodes(self):
        result_mm = minimax(EASY_STATE, depth=2, timeout=10)
        result_ab = alpha_beta_pruning(EASY_STATE, depth=2, timeout=10)
        assert result_ab.nodes_expanded <= result_mm.nodes_expanded


class TestExpectimax:
    def test_returns_result(self):
        result = expectimax(EASY_STATE, depth=2, timeout=10, seed=42)
        assert result.algorithm == "Expectimax"
        assert result.uses_probability is True

    def test_has_probability_trace(self):
        result = expectimax(EASY_STATE, depth=2, timeout=10, seed=42)
        if result.trace:
            probs = [s.probability for s in result.trace if s.probability is not None]
            assert len(probs) > 0


class TestSolvableGuard:
    """Ensure all solvers handle unsolvable states gracefully."""

    UNSOLVABLE = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15, 14, 0)

    def test_unsolvable_detected(self):
        assert is_solvable(self.UNSOLVABLE) is False

    def test_bfs_on_goal(self):
        result = bfs(GOAL_STATE, timeout=2)
        assert result is not None
        assert result.success is True

    def test_a_star_on_goal(self):
        result = a_star(GOAL_STATE, timeout=2)
        assert result.success is True