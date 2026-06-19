"""Tests for heuristics module."""

import pytest
from core.puzzle import GOAL_STATE
from core.heuristics import (
    misplace_count, manhattan_distance, linear_conflict, get_heuristic, HEURISTICS,
)
from core.puzzle import PuzzleState


class TestMisplaceCount:
    def test_goal_state_zero(self):
        assert misplace_count(GOAL_STATE) == 0

    def test_one_tile_misplaced(self):
        state = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 0, 13, 14, 15, 12)
        # Tile 12 is misplaced (at position 11 instead of position 11)
        # Actually tile 12 should be at pos 11 but is at pos 15,
        # and 0 is at pos 11 (blank, not counted)
        # So misplace_count counts tiles not in goal position (excluding 0)
        assert misplace_count(state) >= 1

    def test_reversed_state(self):
        # Reversed: tile 15 at position 0 (goal position for 1), etc.
        # Only tile 0 is in correct position (at index 15)
        state = (15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0)
        # 0 is at position 15 which is its goal position, so not counted
        # All other 15 tiles are misplaced? Actually misplace_count
        # doesn't count 0, but counts whether each tile is in its goal position
        result = misplace_count(state)
        assert result == 14  # 0 is correct; tiles 1-15: check which match
        # Actually let's just verify it's > 0 and reasonable
        assert result > 10


class TestManhattanDistance:
    def test_goal_state_zero(self):
        assert manhattan_distance(GOAL_STATE) == 0

    def test_one_step_away(self):
        state = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 0, 13, 14, 15, 12)
        assert manhattan_distance(state) >= 1

    def test_never_negative(self):
        state = (15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0)
        assert manhattan_distance(state) >= 0


class TestLinearConflict:
    def test_goal_state_zero(self):
        assert linear_conflict(GOAL_STATE) == 0

    def test_greater_or_equal_manhattan(self):
        state = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 0, 13, 14, 15, 12)
        lc = linear_conflict(state)
        md = manhattan_distance(state)
        assert lc >= md

    def test_never_negative(self):
        state = (15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0)
        assert linear_conflict(state) >= 0

    def test_detects_reversed_tiles_in_goal_row(self):
        state = (2, 1, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 0)
        assert manhattan_distance(state) == 2
        assert linear_conflict(state) == 4

    def test_overlapping_conflicts_do_not_double_charge_a_tile(self):
        state = (3, 2, 1, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 0)
        assert manhattan_distance(state) == 4
        assert linear_conflict(state) == 6

    def test_two_disjoint_conflicts_are_both_counted(self):
        state = (2, 1, 4, 3, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 0)
        assert manhattan_distance(state) == 4
        assert linear_conflict(state) == 8

    def test_admissible_and_consistent_on_shallow_reachable_states(self):
        exact_distance = {GOAL_STATE: 0}
        queue = [GOAL_STATE]
        for state in queue:
            depth = exact_distance[state]
            if depth == 5:
                continue
            for neighbor, _, _ in PuzzleState(state).get_neighbors():
                if neighbor not in exact_distance:
                    exact_distance[neighbor] = depth + 1
                    queue.append(neighbor)

        for state, distance in exact_distance.items():
            value = linear_conflict(state)
            assert value <= distance
            for neighbor, _, _ in PuzzleState(state).get_neighbors():
                assert value <= 1 + linear_conflict(neighbor)

    def test_custom_goal_is_bound_to_solver_heuristic(self):
        custom_goal = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 0, 15)
        heuristic = get_heuristic("Linear Conflict", custom_goal)
        assert heuristic(custom_goal) == 0
        assert heuristic(GOAL_STATE) == 1


class TestHeuristicsDict:
    def test_all_heuristics_registered(self):
        assert "Misplaced Tiles" in HEURISTICS
        assert "Manhattan Distance" in HEURISTICS
        assert "Linear Conflict" in HEURISTICS

    def test_heuristics_are_callable(self):
        for name, fn in HEURISTICS.items():
            result = fn(GOAL_STATE)
            assert isinstance(result, (int, float))
            assert result == 0  # goal state should have h=0
