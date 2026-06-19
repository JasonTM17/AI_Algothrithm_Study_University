"""Pure scoring rules for the interactive 15-puzzle challenge."""

from dataclasses import dataclass
from typing import Optional

from core.puzzle import GOAL_STATE, _move_blank


@dataclass(frozen=True)
class ChallengeScore:
    player_moves: int
    optimal_moves: int
    gap: int
    efficiency_percent: float
    is_optimal_play: bool


@dataclass(frozen=True)
class PlayerRunCertificate:
    """Evidence that a manual play history is a legal puzzle trajectory."""

    is_legal: bool
    reaches_goal: bool
    actions: tuple[str, ...]
    final_state: Optional[tuple[int, ...]]
    message: str

    @property
    def move_count(self) -> int:
        return len(self.actions)


def _action_between(
    current: tuple[int, ...],
    next_state: tuple[int, ...],
) -> Optional[str]:
    """Return the legal blank-slide action that transforms current into next_state."""
    for action in ("L", "R", "U", "D"):
        if _move_blank(current, action) == next_state:
            return action
    return None


def validate_player_run(
    history: list[tuple[int, ...]] | tuple[tuple[int, ...], ...],
    goal: tuple[int, ...] = GOAL_STATE,
) -> PlayerRunCertificate:
    """Validate a player's recorded board history before comparing it to optimal play."""
    if not history:
        return PlayerRunCertificate(
            is_legal=False,
            reaches_goal=False,
            actions=(),
            final_state=None,
            message="Player history is empty.",
        )

    actions: list[str] = []
    for index, (current, next_state) in enumerate(zip(history, history[1:]), start=1):
        action = _action_between(current, next_state)
        if action is None:
            return PlayerRunCertificate(
                is_legal=False,
                reaches_goal=False,
                actions=tuple(actions),
                final_state=next_state,
                message=f"Illegal transition at player step {index}.",
            )
        actions.append(action)

    final_state = history[-1]
    reaches_goal = final_state == goal
    return PlayerRunCertificate(
        is_legal=True,
        reaches_goal=reaches_goal,
        actions=tuple(actions),
        final_state=final_state,
        message=(
            "Player run is legal and reaches the goal."
            if reaches_goal
            else "Player run is legal but has not reached the goal yet."
        ),
    )


def score_challenge(player_moves: int, optimal_moves: int) -> ChallengeScore:
    """Compare a completed legal player solution with a proven optimal path length."""
    if player_moves < 0 or optimal_moves < 0:
        raise ValueError("Move counts must be non-negative")
    if player_moves < optimal_moves:
        raise ValueError("A completed legal solution cannot be shorter than the proven optimum")
    gap = player_moves - optimal_moves
    if player_moves == 0:
        efficiency = 100.0 if optimal_moves == 0 else 0.0
    else:
        efficiency = min(100.0, 100.0 * optimal_moves / player_moves)
    return ChallengeScore(
        player_moves=player_moves,
        optimal_moves=optimal_moves,
        gap=gap,
        efficiency_percent=efficiency,
        is_optimal_play=gap == 0,
    )
