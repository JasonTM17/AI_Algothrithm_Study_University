"""Tests for all solver algorithms."""

import inspect

import pytest
import algorithms.uninformed as uninformed_module
from core.puzzle import (
    GOAL_STATE,
    TEACHING_PRESETS,
    _move_blank,
    is_solvable,
    validate_path,
    validate_solution_path,
)
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
OPPOSITE_PARITY_GOAL = (2, 1, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 0)
ONE_MOVE_CUSTOM_GOAL = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 0, 15)


def assert_valid_solution(start, result):
    if result.success:
        valid, message, final_state = validate_path(start, result.actions)
        assert valid, message
        assert final_state == GOAL_STATE


def assert_valid_custom_goal_solution(start, goal, result):
    if result.success:
        assert result.path[0] == start
        valid, message = validate_solution_path(result.path, result.actions, goal=goal)
        assert valid, message
        assert result.path[-1] == goal


class TestBFS:
    def test_solves_easy(self):
        result = bfs(EASY_STATE, timeout=10)
        assert result.success is True
        assert result.algorithm == "BFS"
        assert len(result.actions) > 0
        assert_valid_solution(EASY_STATE, result)

    def test_solves_goal(self):
        result = bfs(GOAL_STATE, timeout=5)
        assert result.success is True
        assert len(result.actions) == 0
        assert_valid_solution(GOAL_STATE, result)

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

    def test_duplicate_policy_is_depth_aware(self):
        source = inspect.getsource(uninformed_module.dfs)
        assert "best_depth: dict" in source
        assert "seen_states = {start}" not in source
        assert "child.depth >= prev_depth" in source
        assert "ancestor_states" in source


class TestUCS:
    def test_solves_easy(self):
        result = ucs(EASY_STATE, timeout=10)
        assert result.success is True
        assert result.algorithm == "UCS"
        assert result.cost == len(result.actions)
        assert_valid_solution(EASY_STATE, result)


class TestIDS:
    def test_solves_easy(self):
        result = ids(EASY_STATE, max_depth=20, timeout=15)
        assert result is not None
        assert result.algorithm == "IDS"
        # IDS should solve this easy state
        assert result.success is True
        assert_valid_solution(EASY_STATE, result)

    @pytest.mark.parametrize(
        ("kwargs", "termination_reason"),
        [
            ({"timeout": -1.0}, "timeout"),
            ({"max_nodes": 0, "max_depth": 2}, "resource_limit"),
            ({"max_depth": 0}, "depth_limit"),
        ],
    )
    def test_failure_results_preserve_custom_goal(self, kwargs, termination_reason):
        result = ids(GOAL_STATE, goal=ONE_MOVE_CUSTOM_GOAL, **kwargs)

        assert not result.success
        assert result.algorithm == "IDS"
        assert result.group == "Uninformed Search"
        assert result.goal_state == ONE_MOVE_CUSTOM_GOAL
        assert result.termination_reason == termination_reason
        assert result.is_complete is False
        assert result.is_optimal is False
        assert result.optimality_proven is False


class TestPathValidation:
    @pytest.mark.parametrize(
        ("start", "goal"),
        [
            ((1, 2, 3), GOAL_STATE),
            (GOAL_STATE, (1, 2, 3)),
        ],
    )
    def test_validate_path_rejects_invalid_boundary_states(self, start, goal):
        valid, message, final_state = validate_path(start, [], goal=goal)

        assert not valid
        assert "state" in message.lower()
        assert final_state is None

    def test_validate_solution_path_rejects_invalid_recorded_state(self):
        valid, message = validate_solution_path([(1, 2, 3)], [], goal=GOAL_STATE)

        assert not valid
        assert "state" in message.lower()


class TestGreedyBestFirst:
    def test_solves_easy(self):
        result = greedy_best_first(EASY_STATE, timeout=10)
        assert result.success is True
        assert result.algorithm == "Greedy Best-First"
        assert_valid_solution(EASY_STATE, result)

    def test_uses_heuristic(self):
        result = greedy_best_first(EASY_STATE, heuristic="Manhattan Distance", timeout=10)
        assert result.uses_heuristic is True


class TestAStar:
    def test_solves_easy(self):
        result = a_star(EASY_STATE, timeout=10)
        assert result.success is True
        assert result.algorithm == "A*"
        assert_valid_solution(EASY_STATE, result)

    def test_optimal(self):
        result = a_star(EASY_STATE, timeout=10)
        assert result.is_optimal is True

    def test_solves_medium(self):
        result = a_star(MEDIUM_STATE, timeout=15)
        assert result.success is True
        assert_valid_solution(MEDIUM_STATE, result)

    def test_resource_limit_does_not_claim_completeness_or_optimality(self):
        result = a_star(EASY_STATE, max_nodes=0, timeout=10)
        assert not result.success
        assert result.termination_reason == "resource_limit"
        assert result.is_complete is False
        assert result.is_optimal is False
        assert result.optimality_proven is False


class TestIDAStar:
    def test_solves_easy(self):
        result = ida_star(EASY_STATE, timeout=10)
        assert result.success is True
        assert result.algorithm == "IDA*"
        assert_valid_solution(EASY_STATE, result)

    def test_optimal(self):
        result = ida_star(EASY_STATE, timeout=10)
        assert result.is_optimal is True

    def test_reached_size_tracks_best_g_not_recursion_stack(self):
        result = ida_star(EASY_STATE, timeout=10)
        reached_sizes = [step.reached_size for step in result.trace if step.reached_size]

        assert reached_sizes
        assert max(reached_sizes) >= 2
        assert result.reached_size >= max(reached_sizes)

    def test_resource_limit_does_not_claim_completeness_or_optimality(self):
        result = ida_star(EASY_STATE, max_nodes=0, timeout=10)
        assert not result.success
        assert result.termination_reason == "resource_limit"
        assert result.is_complete is False
        assert result.is_optimal is False
        assert result.optimality_proven is False


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

    def test_random_restart_exposes_random_trial_path_before_hill_climb(self):
        result = random_restart_hill_climbing(
            EASY_STATE,
            max_iterations=1,
            max_restarts=2,
            timeout=10,
            seed=42,
        )
        assert any("random-walk probe" in step.reason for step in result.trace)

    def test_beam_search_returns_result(self):
        result = local_beam_search(EASY_STATE, beam_width=3, timeout=10)
        assert result.algorithm == "Local Beam Search"

    def test_custom_goal_is_used_by_local_heuristic(self):
        custom_goal = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 0, 15)
        result = simple_hill_climbing(GOAL_STATE, goal=custom_goal, timeout=5)
        assert result.success
        assert result.goal_state == custom_goal
        assert result.goal_reached
        assert result.path_verified
        assert result.cost == 1
        valid, message, final_state = validate_path(GOAL_STATE, result.actions)
        assert not valid  # validate_path intentionally targets the standard goal.
        assert final_state == custom_goal


@pytest.mark.parametrize("solver, kwargs", [
    (simple_hill_climbing, {}),
    (steepest_ascent_hill_climbing, {}),
    (stochastic_hill_climbing, {"seed": 1}),
    (random_restart_hill_climbing, {"seed": 1}),
    (local_beam_search, {"beam_width": 2}),
    (simulated_annealing, {"seed": 1}),
])
def test_local_search_results_report_the_selected_custom_goal(solver, kwargs):
    result = solver(
        OPPOSITE_PARITY_GOAL,
        goal=OPPOSITE_PARITY_GOAL,
        max_iterations=5,
        timeout=2,
        **kwargs,
    )

    assert result.success
    assert result.goal_state == OPPOSITE_PARITY_GOAL
    assert result.goal_reached
    assert result.path_verified


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
        assert "MIN branch models worst-case legal continuations" in result.message
        assert "not a real opponent" in result.message
        assert "tries to obstruct" not in result.message


class TestAlphaBeta:
    def test_returns_result(self):
        result = alpha_beta_pruning(EASY_STATE, depth=2, timeout=10)
        assert result.algorithm == "Alpha-Beta Pruning"
        assert result.uses_adversary is True

    def test_prunes_nodes(self):
        result_mm = minimax(EASY_STATE, depth=2, timeout=10)
        result_ab = alpha_beta_pruning(EASY_STATE, depth=2, timeout=10)
        assert result_ab.nodes_expanded <= result_mm.nodes_expanded

    def test_message_preserves_minimax_value_under_worst_case_tree(self):
        result = alpha_beta_pruning(EASY_STATE, depth=2, timeout=10)
        assert "same fully searched worst-case tree" in result.message
        assert "not a real opponent" in result.message


class TestExpectimax:
    def test_returns_result(self):
        result = expectimax(EASY_STATE, depth=2, timeout=10, seed=42)
        assert result.algorithm == "Expectimax"
        assert result.uses_probability is True
        assert result.uses_randomness is True
        assert result.uses_adversary is False
        assert result.random_seed == 42

    def test_has_probability_trace(self):
        result = expectimax(EASY_STATE, depth=2, timeout=10, seed=42)
        if result.trace:
            probs = [s.probability for s in result.trace if s.probability is not None]
            assert len(probs) > 0
        assert "EXPECTED outcome with CHANCE nodes" in result.message
        assert "WORST-CASE legal continuations" in result.message

    def test_seed_replays_the_same_sampled_outcome_path(self):
        first = expectimax(EASY_STATE, depth=2, success_prob=0.5, timeout=10, seed=123)
        second = expectimax(EASY_STATE, depth=2, success_prob=0.5, timeout=10, seed=123)

        assert first.actions == second.actions
        assert first.path == second.path
        assert first.random_seed == second.random_seed == 123
        assert "seeded probability-sampled outcome path" in first.message

    def test_different_seeds_can_sample_different_outcome_paths(self):
        sampled_paths = {
            tuple(expectimax(EASY_STATE, depth=2, success_prob=0.5, timeout=10, seed=seed).actions)
            for seed in range(20)
        }

        assert len(sampled_paths) > 1

    def test_rejects_invalid_probability(self):
        with pytest.raises(ValueError):
            expectimax(EASY_STATE, success_prob=1.1)

    def test_depth_one_evaluates_chance_outcomes_and_counts_generated_nodes(self):
        result = expectimax(EASY_STATE, depth=1, success_prob=0.75, timeout=10, seed=42)
        assert any(step.node_type == "CHANCE" for step in result.trace)
        assert result.nodes_generated > result.nodes_expanded


@pytest.mark.parametrize("solver", [minimax, alpha_beta_pruning, expectimax])
def test_game_models_honor_timeout_and_label_partial_evaluation(solver):
    result = solver(EASY_STATE, depth=5, timeout=0.0)
    assert "Timeout" in result.message
    assert result.termination_reason == "timeout"
    assert result.runtime < 1.0


@pytest.mark.parametrize("solver", [minimax, alpha_beta_pruning, expectimax])
def test_game_models_return_legal_selected_variation_path(solver):
    result = solver(EASY_STATE, depth=2, timeout=10)
    current = EASY_STATE
    reconstructed = [current]
    for action in result.actions:
        next_state = _move_blank(current, action)
        assert next_state is not None
        reconstructed.append(next_state)
        current = next_state

    assert len(result.path) == len(result.actions) + 1
    assert result.path == reconstructed
    assert result.goal_state == GOAL_STATE
    assert result.goal_reached is (current == GOAL_STATE)
    assert result.success is (current == GOAL_STATE)
    if result.success:
        assert result.path_verified


class TestSolvableGuard:
    """Ensure all solvers handle unsolvable states gracefully."""

    UNSOLVABLE = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15, 14, 0)

    def test_unsolvable_detected(self):
        assert is_solvable(self.UNSOLVABLE) is False

    def test_bfs_on_goal(self):
        result = bfs(GOAL_STATE, timeout=2)
        assert result is not None
        assert result.success is True
        assert_valid_solution(GOAL_STATE, result)

    def test_a_star_on_goal(self):
        result = a_star(GOAL_STATE, timeout=2)
        assert result.success is True
        assert_valid_solution(GOAL_STATE, result)


TREE_SEARCH_SOLVERS = [
    (bfs, {}),
    (dfs, {"max_depth": 4}),
    (ucs, {}),
    (ids, {"max_depth": 4}),
    (greedy_best_first, {}),
    (a_star, {}),
    (ida_star, {}),
]


@pytest.mark.parametrize("solver, kwargs", TREE_SEARCH_SOLVERS)
def test_tree_search_rejects_pairs_unsolvable_relative_to_selected_goal(solver, kwargs):
    result = solver(GOAL_STATE, goal=OPPOSITE_PARITY_GOAL, timeout=2, **kwargs)

    assert result.success is False
    assert result.nodes_expanded == 0
    assert "selected goal" in result.message


@pytest.mark.parametrize("solver, kwargs", TREE_SEARCH_SOLVERS)
def test_tree_search_accepts_custom_goal_even_when_not_standard_solvable(solver, kwargs):
    result = solver(OPPOSITE_PARITY_GOAL, goal=OPPOSITE_PARITY_GOAL, timeout=2, **kwargs)

    assert result.success is True
    assert result.actions == []
    assert result.path == [OPPOSITE_PARITY_GOAL]
    assert_valid_custom_goal_solution(OPPOSITE_PARITY_GOAL, OPPOSITE_PARITY_GOAL, result)


@pytest.mark.parametrize("solver, kwargs", TREE_SEARCH_SOLVERS)
def test_tree_search_solves_one_move_custom_goal(solver, kwargs):
    result = solver(GOAL_STATE, goal=ONE_MOVE_CUSTOM_GOAL, timeout=5, **kwargs)

    assert result.success is True
    assert result.actions == ["L"]
    assert_valid_custom_goal_solution(GOAL_STATE, ONE_MOVE_CUSTOM_GOAL, result)


def test_a_star_matches_bfs_and_ids_on_shallow_puzzle():
    bfs_result = bfs(EASY_STATE, timeout=10)
    ids_result = ids(EASY_STATE, max_depth=20, timeout=10)
    a_star_result = a_star(EASY_STATE, timeout=10)

    assert bfs_result.success
    assert ids_result.success
    assert a_star_result.success
    assert len(a_star_result.actions) == len(bfs_result.actions) == len(ids_result.actions)
    assert_valid_solution(EASY_STATE, a_star_result)


@pytest.mark.parametrize("solver, kwargs", [
    (ids, {"max_depth": 20}),
    (ida_star, {}),
])
def test_iterative_deepening_respects_node_budget_inside_recursive_pass(solver, kwargs):
    result = solver(
        MEDIUM_STATE,
        max_nodes=1,
        timeout=5,
        **kwargs,
    )

    assert not result.success
    assert result.nodes_expanded <= 1
    assert result.termination_reason == "resource_limit"
    assert "Node limit exceeded" in result.message


def test_contrast_solvers_keep_theoretical_completeness_labels_on_trivial_goal():
    dfs_result = dfs(GOAL_STATE, timeout=2)
    greedy_result = greedy_best_first(GOAL_STATE, timeout=2)

    assert dfs_result.success
    assert greedy_result.success
    assert dfs_result.is_complete is False
    assert greedy_result.is_complete is False


def test_greedy_suboptimal_teaching_preset():
    state = TEACHING_PRESETS["Greedy suboptimal: A*=15, Greedy=17"]["state"]

    a_star_result = a_star(state, max_nodes=300000, timeout=10)
    greedy_result = greedy_best_first(state, max_nodes=300000, timeout=10)

    assert a_star_result.success
    assert greedy_result.success
    assert len(a_star_result.actions) == 15
    assert len(greedy_result.actions) == 17
    assert len(greedy_result.actions) > len(a_star_result.actions)
    assert_valid_solution(state, a_star_result)
    assert_valid_solution(state, greedy_result)


def test_hill_climbing_stuck_teaching_preset():
    state = TEACHING_PRESETS["Hill Climbing stuck: local optimum h=4"]["state"]

    result = simple_hill_climbing(state, max_iterations=1000, timeout=5)

    assert result.success is False
    assert len(result.actions) == 4
    assert result.path_verified
    assert result.goal_state == GOAL_STATE
    assert not result.goal_reached
    assert "does not match the requested goal" in result.verification_message
    assert "Stuck at local optimum h=4.0" in result.message


def test_random_restart_never_returns_a_path_from_an_unrelated_state():
    result = random_restart_hill_climbing(
        EASY_STATE, max_iterations=20, max_restarts=4, timeout=5, seed=7,
    )
    if result.path:
        assert result.path[0] == EASY_STATE
        assert len(result.path) == len(result.actions) + 1
    if result.success:
        assert result.path_verified


def test_simulated_annealing_keeps_the_original_path_prefix():
    result = simulated_annealing(
        EASY_STATE, max_iterations=1200, timeout=5, seed=11,
    )
    assert result.path[0] == EASY_STATE
    assert len(result.path) == len(result.actions) + 1


@pytest.mark.parametrize(
    "solver, kwargs",
    [
        (simple_hill_climbing, {"max_iterations": 2}),
        (steepest_ascent_hill_climbing, {"max_iterations": 2}),
        (stochastic_hill_climbing, {"max_iterations": 2, "seed": 7}),
        (simulated_annealing, {"max_iterations": 2, "seed": 7}),
    ],
)
def test_local_search_trace_exposes_each_evaluated_candidate(solver, kwargs):
    result = solver(EASY_STATE, timeout=5, **kwargs)
    reasons = " ".join(step.reason for step in result.trace)

    assert "Evaluate candidate" in reasons
    assert "selected" in reasons or "accepted" in reasons or "rejected" in reasons


def test_local_beam_failure_keeps_best_legal_partial_trajectory():
    state = TEACHING_PRESETS["Hill Climbing stuck: local optimum h=4"]["state"]
    result = local_beam_search(
        state,
        beam_width=1,
        max_iterations=5,
        timeout=5,
    )

    assert not result.success
    assert result.path
    assert result.path[0] == state
    assert result.path_verified
    assert len(result.path) == len(result.actions) + 1
