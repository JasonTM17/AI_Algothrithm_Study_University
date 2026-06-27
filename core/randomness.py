"""Reproducible seed policy for stochastic algorithm demonstrations."""

from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
import random
import secrets
from typing import Iterator, Optional


ACTION_ORDER_VALUES = ("L", "R", "U", "D")
TIE_BREAKERS = ("FIFO", "LIFO", "Min-g", "Max-g")

RANDOMIZED_SOLVERS = frozenset({
    "stochastic_hill_climbing",
    "random_restart_hill_climbing",
    "simulated_annealing",
    "min_conflicts",
    "no_observation_search",
    "partially_observable_search",
    "expectimax",
})

TIE_BREAKER_VARIATION_SOLVERS = frozenset({
    "ucs",
    "greedy_best_first",
    "a_star",
})

NON_PATH_VARIATION_SOLVERS = frozenset({
    "and_or_search",
    "csp_definition",
    "path_consistency",
    "global_constraints",
    "solve_csp_constraint_graphs",
})

_ACTIVE_ACTION_ORDER: ContextVar[Optional[str]] = ContextVar(
    "active_run_action_order",
    default=None,
)


@dataclass(frozen=True)
class RunVariation:
    """Per-click variation applied by the UI without changing solver signatures."""

    seed: int
    action_order: str
    tie_breaker: str
    solver_seed: Optional[int]
    randomizes_path: bool


@contextmanager
def activate_run_variation(variation: RunVariation) -> Iterator[None]:
    """Expose one run's action order without changing solver signatures."""
    token = _ACTIVE_ACTION_ORDER.set(variation.action_order)
    try:
        yield
    finally:
        _ACTIVE_ACTION_ORDER.reset(token)


def active_action_order(default: str = "LRUD") -> str:
    """Return the current run action order, or the solver default."""
    return _ACTIVE_ACTION_ORDER.get() or default


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


def _fresh_seed(previous_seed: Optional[int] = None) -> int:
    candidate = secrets.randbits(63)
    if candidate == previous_seed:
        candidate = (candidate + 1) % (2**63)
    return candidate


def make_run_variation(
    fn_name: str,
    *,
    previous_seed: Optional[int] = None,
    previous_action_order: Optional[str] = None,
    previous_tie_breaker: Optional[str] = None,
) -> RunVariation:
    """Build the fresh per-click variation used by Run and Advanced tabs."""
    seed = _fresh_seed(previous_seed)
    rng = random.Random(seed)
    action_order = "".join(rng.sample(ACTION_ORDER_VALUES, len(ACTION_ORDER_VALUES)))
    randomizes_path = fn_name not in NON_PATH_VARIATION_SOLVERS

    if randomizes_path and action_order == previous_action_order:
        action_order = action_order[1:] + action_order[:1]

    tie_breaker = "FIFO"
    if fn_name in TIE_BREAKER_VARIATION_SOLVERS:
        tie_breaker = rng.choice(TIE_BREAKERS)
        if previous_tie_breaker and tie_breaker == previous_tie_breaker:
            next_index = (TIE_BREAKERS.index(tie_breaker) + 1) % len(TIE_BREAKERS)
            tie_breaker = TIE_BREAKERS[next_index]

    return RunVariation(
        seed=seed,
        action_order=action_order,
        tie_breaker=tie_breaker,
        solver_seed=seed if is_randomized_solver(fn_name) else None,
        randomizes_path=randomizes_path,
    )


def apply_run_variation(result: object, variation: RunVariation) -> None:
    """Attach the per-click UI variation metadata to a SearchResult-like object."""
    result.random_seed = variation.seed
    result.variation_action_order = variation.action_order
    result.variation_tie_breaker = variation.tie_breaker
    result.variation_solver_seed = variation.solver_seed
    result.variation_randomizes_path = variation.randomizes_path
