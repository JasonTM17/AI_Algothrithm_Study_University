"""Reproducible seed policy for stochastic algorithm demonstrations."""

from __future__ import annotations

import secrets
from typing import Optional


RANDOMIZED_SOLVERS = frozenset({
    "stochastic_hill_climbing",
    "random_restart_hill_climbing",
    "simulated_annealing",
    "min_conflicts",
    "and_or_search",
    "no_observation_search",
    "partially_observable_search",
    "expectimax",
})


def is_randomized_solver(fn_name: str) -> bool:
    """Return whether a solver consumes random choices in this implementation."""
    return fn_name in RANDOMIZED_SOLVERS


def resolve_run_seed(
    fn_name: str,
    *,
    fresh_each_run: bool,
    manual_seed: int,
    previous_seed: Optional[int] = None,
) -> Optional[int]:
    """Choose a fresh or fixed seed only for algorithms that are actually stochastic."""
    if not is_randomized_solver(fn_name):
        return None
    if not fresh_each_run:
        return int(manual_seed)

    candidate = secrets.randbits(63)
    if candidate == previous_seed:
        candidate = (candidate + 1) % (2**63)
    return candidate
