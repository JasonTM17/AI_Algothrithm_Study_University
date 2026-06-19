"""15-Puzzle state representation and operations."""

import random
from typing import Optional

GOAL_STATE: tuple[int, ...] = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 0)

GOAL_POS: dict[int, tuple[int, int]] = {}
for _i, _v in enumerate(GOAL_STATE):
    GOAL_POS[_v] = (_i // 4, _i % 4)

ACTIONS = ("L", "R", "U", "D")


def validate_state(state: tuple[int, ...]) -> None:
    """Raise ``ValueError`` unless state is a permutation of tiles 0..15."""
    if len(state) != 16:
        raise ValueError("State must have exactly 16 elements")
    if set(state) != set(range(16)):
        raise ValueError("State must contain each tile from 0 to 15 exactly once")

TEACHING_PRESETS: dict[str, dict[str, object]] = {
    "Greedy suboptimal: A*=15, Greedy=17": {
        "state": (6, 1, 4, 8, 0, 2, 7, 3, 5, 10, 11, 12, 9, 13, 14, 15),
        "purpose": "Shows that Greedy Best-First can find a longer path than A*.",
    },
    "Hill Climbing stuck: local optimum h=4": {
        "state": (1, 2, 3, 4, 5, 6, 7, 8, 0, 13, 10, 11, 14, 9, 15, 12),
        "purpose": "Shows Simple Hill Climbing stopping at a local optimum.",
    },
}


def _blank_rc(state: tuple[int, ...]) -> tuple[int, int]:
    idx = state.index(0)
    return idx // 4, idx % 4


def _move_blank(state: tuple[int, ...], action: str) -> Optional[tuple[int, ...]]:
    blank = state.index(0)
    r, c = blank // 4, blank % 4
    if action == "L" and c > 0:
        nb = blank - 1
    elif action == "R" and c < 3:
        nb = blank + 1
    elif action == "U" and r > 0:
        nb = blank - 4
    elif action == "D" and r < 3:
        nb = blank + 4
    else:
        return None
    lst = list(state)
    lst[blank], lst[nb] = lst[nb], lst[blank]
    return tuple(lst)


class PuzzleState:
    """Represents a 15-puzzle state with core operations."""

    def __init__(self, state: tuple[int, ...]):
        validate_state(state)
        self.state = state
        self.blank = state.index(0)

    def __eq__(self, other):
        return isinstance(other, PuzzleState) and self.state == other.state

    def __hash__(self):
        return hash(self.state)

    def __repr__(self):
        return f"PuzzleState({self.state})"

    def is_goal(self) -> bool:
        return self.state == GOAL_STATE

    def get_neighbors(self, action_order: str = "LRUD") -> list[tuple[tuple[int, ...], str, int]]:
        """Return list of (new_state, action, cost=1) for valid moves."""
        result = []
        for a in action_order:
            ns = _move_blank(self.state, a)
            if ns is not None:
                result.append((ns, a, 1))
        return result

    def pretty_str(self) -> str:
        lines = []
        for r in range(4):
            row = self.state[r * 4:(r + 1) * 4]
            lines.append("  ".join(f"{v:2d}" if v != 0 else " _" for v in row))
        return "\n".join(lines)


def is_solvable(state: tuple[int, ...]) -> bool:
    """Check if a 15-puzzle state is solvable.

    For 4x4 puzzle with goal blank in bottom-right:
    solvable iff (inversions + blank_row_from_bottom) is odd.
    """
    validate_state(state)
    tiles = [t for t in state if t != 0]
    inversions = 0
    for i in range(len(tiles)):
        for j in range(i + 1, len(tiles)):
            if tiles[i] > tiles[j]:
                inversions += 1
    blank_row = state.index(0) // 4
    blank_row_from_bottom = 4 - blank_row
    return (inversions + blank_row_from_bottom) % 2 == 1


def scramble(goal: tuple[int, ...] = GOAL_STATE, depth: int = 10,
             seed: Optional[int] = None, action_order: str = "LRUD") -> tuple[int, ...]:
    """Generate a solvable puzzle by scrambling from goal state."""
    validate_state(goal)
    if depth < 0:
        raise ValueError("Scramble depth must be non-negative")
    rng = random.Random(seed)
    state = goal
    last_action = None
    opposites = {"L": "R", "R": "L", "U": "D", "D": "U"}
    for _ in range(depth):
        actions = list(action_order)
        rng.shuffle(actions)
        for a in actions:
            if last_action and a == opposites.get(last_action):
                continue
            ns = _move_blank(state, a)
            if ns is not None:
                state = ns
                last_action = a
                break
    return state


def parse_state(text: str) -> tuple[int, ...]:
    """Parse a 4x4 grid string into state tuple.

    Accepts space/comma/newline separated values, 0 = blank.
    Example: '1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 0'
    """
    nums = [int(x) for x in text.replace("\n", " ").replace(",", " ").split() if x.strip()]
    result = tuple(nums)
    validate_state(result)
    return result


def validate_solution_path(
    path: list[tuple[int, ...]], actions: list[str], goal: tuple[int, ...] = GOAL_STATE,
) -> tuple[bool, str]:
    """Validate every recorded edge, action count, and final state."""
    if not path:
        return False, "Solution path is empty"
    if len(path) != len(actions) + 1:
        return False, "A solution path must contain exactly one more state than actions"
    for index, action in enumerate(actions):
        expected = _move_blank(path[index], action)
        if expected is None:
            return False, f"Action {action} is illegal at step {index + 1}"
        if expected != path[index + 1]:
            return False, f"Recorded state does not match action {action} at step {index + 1}"
    if path[-1] != goal:
        return False, "Final state does not match the requested goal"
    return True, "Solution path is a legal sequence and reaches the goal"


def validate_path(start: tuple[int, ...], actions: list[str]) -> tuple[bool, str, Optional[tuple[int, ...]]]:
    """Validate that action sequence leads from start to goal.

    Returns (valid, message, final_state).
    """
    state = start
    for i, a in enumerate(actions):
        ns = _move_blank(state, a)
        if ns is None:
            inv = {"L": "Right", "R": "Left", "U": "Down", "D": "Up"}
            return False, f"Invalid action {a} at step {i} (cannot move {inv.get(a, a)})", None
        state = ns
    if state == GOAL_STATE:
        return True, "Path valid and reaches goal", state
    return False, "Path valid but does not reach goal", state
