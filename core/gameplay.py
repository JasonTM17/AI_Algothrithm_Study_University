"""Pure scoring rules for the interactive 15-puzzle challenge."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ChallengeScore:
    player_moves: int
    optimal_moves: int
    gap: int
    efficiency_percent: float
    is_optimal_play: bool


def score_challenge(player_moves: int, optimal_moves: int) -> ChallengeScore:
    """Compare a legal player run with a proven optimal path length."""
    if player_moves < 0 or optimal_moves < 0:
        raise ValueError("Move counts must be non-negative")
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
