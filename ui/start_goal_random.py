"""Random start-state helpers shared by puzzle setup UIs."""

from __future__ import annotations

from dataclasses import dataclass
import random
import secrets

from core.puzzle import GOAL_STATE, scramble
from core.randomness import ACTION_ORDER_VALUES


MAX_UI_SCRAMBLE_SEED = 99_999


@dataclass(frozen=True)
class ScrambleGeneration:
    """A generated start board plus the values needed to reproduce it."""

    state: tuple[int, ...]
    seed: int
    action_order: str


def fresh_scramble_seed(previous_seed: int | None = None) -> int:
    """Return a UI-sized random seed, avoiding the immediate previous value."""
    candidate = secrets.randbelow(MAX_UI_SCRAMBLE_SEED + 1)
    if previous_seed is not None and candidate == int(previous_seed):
        candidate = (candidate + 1) % (MAX_UI_SCRAMBLE_SEED + 1)
    return candidate


def scramble_action_order(seed: int) -> str:
    """Derive a reproducible legal-action order from the displayed seed."""
    rng = random.Random(int(seed))
    return "".join(rng.sample(ACTION_ORDER_VALUES, len(ACTION_ORDER_VALUES)))


def generate_scrambled_start(
    *,
    goal: tuple[int, ...] = GOAL_STATE,
    depth: int = 10,
    seed: int | None = None,
    previous_seed: int | None = None,
) -> ScrambleGeneration:
    """Generate a solvable start state with reproducible seed/order evidence."""
    resolved_seed = fresh_scramble_seed(previous_seed) if seed is None else int(seed)
    action_order = scramble_action_order(resolved_seed)
    state = scramble(goal=goal, depth=int(depth), seed=resolved_seed, action_order=action_order)
    return ScrambleGeneration(state=state, seed=resolved_seed, action_order=action_order)
