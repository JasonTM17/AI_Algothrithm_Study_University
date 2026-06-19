"""Tests for core puzzle module."""

import pytest
from core.puzzle import (
    PuzzleState, GOAL_STATE, is_solvable, scramble,
    parse_state, validate_path, validate_solution_path, _move_blank, _blank_rc,
)


class TestGoalState:
    def test_goal_state_is_tuple(self):
        assert isinstance(GOAL_STATE, tuple)
        assert len(GOAL_STATE) == 16

    def test_goal_state_values(self):
        expected = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 0)
        assert GOAL_STATE == expected


class TestPuzzleState:
    @pytest.mark.parametrize("state", [tuple(range(15)), (0,) * 16, tuple(range(1, 17))])
    def test_rejects_malformed_permutations(self, state):
        with pytest.raises(ValueError):
            PuzzleState(state)

    def test_get_neighbors_goal(self):
        ps = PuzzleState(GOAL_STATE)
        neighbors = ps.get_neighbors()
        assert len(neighbors) == 2  # blank at (3,3): can go L or U

    def test_get_neighbors_corner(self):
        state = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15)
        ps = PuzzleState(state)
        neighbors = ps.get_neighbors()
        assert len(neighbors) == 2  # top-left: R or D

    def test_get_neighbors_center(self):
        state = (1, 2, 3, 4, 5, 6, 0, 8, 9, 10, 11, 12, 13, 14, 15, 7)
        ps = PuzzleState(state)
        neighbors = ps.get_neighbors()
        assert len(neighbors) == 4  # center area: all directions

    def test_move_action_changes_state(self):
        ps = PuzzleState(GOAL_STATE)
        neighbors = ps.get_neighbors()
        for new_state, action, cost in neighbors:
            assert new_state != GOAL_STATE
            assert cost == 1
            assert action in ("L", "R", "U", "D")


class TestMoveBlank:
    def test_left_valid(self):
        state = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 0, 12, 13, 14, 15, 11)
        result = _move_blank(state, "L")
        assert result is not None
        assert result[9] == 0  # blank moved left

    def test_left_invalid(self):
        # blank at index 0 (row 0, col 0) - can't go left
        state = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15)
        result = _move_blank(state, "L")
        assert result is None

    def test_up_invalid_top_row(self):
        # blank at index 1 (row 0) - can't go up
        state = (1, 0, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 2)
        result = _move_blank(state, "U")
        assert result is None

    def test_right_valid(self):
        state = (1, 0, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 2)
        result = _move_blank(state, "R")
        assert result is not None


class TestBlankRC:
    def test_goal_blank_position(self):
        r, c = _blank_rc(GOAL_STATE)
        assert r == 3 and c == 3

    def test_top_left_blank(self):
        state = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15)
        r, c = _blank_rc(state)
        assert r == 0 and c == 0


class TestIsSolvable:
    def test_goal_is_solvable(self):
        assert is_solvable(GOAL_STATE) is True

    def test_one_move_away(self):
        state = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 0, 13, 14, 15, 12)
        assert is_solvable(state) is True

    def test_unsolvable_state(self):
        state = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 15, 14, 0)
        assert is_solvable(state) is False

    def test_swap_two_tiles(self):
        state = (2, 1, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 0)
        assert is_solvable(state) is False

    def test_solvability_is_relative_to_requested_goal(self):
        swapped_goal = (2, 1, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 0)

        assert is_solvable(GOAL_STATE)
        assert not is_solvable(swapped_goal)
        assert is_solvable(swapped_goal, goal=swapped_goal)
        assert not is_solvable(GOAL_STATE, goal=swapped_goal)


class TestScramble:
    def test_rejects_negative_depth(self):
        with pytest.raises(ValueError):
            scramble(depth=-1)

    def test_scramble_preserves_solvability(self):
        for seed_val in range(10):
            state = scramble(depth=20, seed=seed_val)
            assert is_solvable(state) is True

    def test_scramble_changes_state(self):
        state = scramble(depth=10, seed=123)
        assert state != GOAL_STATE

    def test_scramble_deterministic_with_seed(self):
        s1 = scramble(depth=10, seed=999)
        s2 = scramble(depth=10, seed=999)
        assert s1 == s2


class TestParseState:
    def test_parse_valid(self):
        text = "1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 0"
        result = parse_state(text)
        assert result == GOAL_STATE

    def test_parse_comma_separated(self):
        text = "1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,0"
        result = parse_state(text)
        assert result == GOAL_STATE

    def test_parse_invalid_length_raises(self):
        with pytest.raises(ValueError):
            parse_state("1 2 3")

    def test_parse_invalid_values_raises(self):
        with pytest.raises(ValueError):
            parse_state("1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 99")


class TestValidatePath:
    def test_valid_path_to_goal(self):
        # Scramble goal by one move, then validate the path back
        ps = PuzzleState(GOAL_STATE)
        neighbors = ps.get_neighbors()
        # Move blank away from goal
        away_state = neighbors[0][0]
        away_action = neighbors[0][1]
        # The reverse action should bring it back to goal
        reverse_map = {"L": "R", "R": "L", "U": "D", "D": "U"}
        reverse_action = reverse_map[away_action]
        success, msg, path = validate_path(away_state, [reverse_action])
        assert success is True
        assert path == GOAL_STATE

    def test_valid_path_does_not_reach_goal(self):
        # Moving from goal state away doesn't reach goal
        ps = PuzzleState(GOAL_STATE)
        neighbors = ps.get_neighbors()
        action = neighbors[0][1]
        success, msg, path = validate_path(GOAL_STATE, [action])
        assert success is False  # doesn't reach goal

    def test_invalid_action(self):
        state = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15)
        success, msg, path = validate_path(state, ["L"])
        assert success is False


class TestSolutionPathValidation:
    def test_accepts_real_transition_sequence(self):
        start = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 0, 15)
        valid, message = validate_solution_path([start, GOAL_STATE], ["R"])
        assert valid, message

    def test_rejects_state_not_produced_by_action(self):
        start = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 0, 15)
        valid, message = validate_solution_path([start, GOAL_STATE], ["L"])
        assert not valid
        assert "does not match" in message

    def test_rejects_mismatched_lengths(self):
        valid, message = validate_solution_path([GOAL_STATE], ["R"])
        assert not valid
        assert "one more state" in message
