"""Shared execution contract for linear 15-puzzle trajectories in the UI."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import algorithms.informed as informed
import algorithms.local_search as local_search
import algorithms.uninformed as uninformed
from core.metrics import SearchResult
from core.academic import algorithm_capability
from core.randomness import is_randomized_solver
from core.solver_dispatch import build_solver_kwargs


@dataclass(frozen=True)
class PathAlgorithmSpec:
    """UI metadata for an algorithm that can report a linear trajectory."""

    name: str
    group: str
    function_name: str
    evaluation: str
    evidence_mode: str


@dataclass(frozen=True)
class PathRunSettings:
    """Comparable resource and variation settings for one trajectory run."""

    timeout: float = 5.0
    max_nodes: int = 20_000
    max_depth: int = 30
    heuristic: str = "Manhattan Distance"
    action_order: str = "LRUD"
    tie_breaker: str = "FIFO"
    seed: int = 42


PATH_ALGORITHM_SPECS = (
    PathAlgorithmSpec("BFS", "Uninformed Search", "bfs", "FIFO frontier", "graph"),
    PathAlgorithmSpec("DFS", "Uninformed Search", "dfs", "LIFO stack", "graph"),
    PathAlgorithmSpec("UCS", "Uninformed Search", "ucs", "g(n)", "graph"),
    PathAlgorithmSpec("IDS", "Uninformed Search", "ids", "Increasing depth limit", "graph"),
    PathAlgorithmSpec(
        "Greedy Best-First", "Informed Search", "greedy_best_first", "h(n)", "informed"
    ),
    PathAlgorithmSpec("A*", "Informed Search", "a_star", "f(n)=g(n)+h(n)", "informed"),
    PathAlgorithmSpec("IDA*", "Informed Search", "ida_star", "f-threshold", "informed"),
    PathAlgorithmSpec(
        "Simple Hill Climbing", "Local Search", "simple_hill_climbing",
        "First improving h(n)", "local",
    ),
    PathAlgorithmSpec(
        "Steepest-Ascent Hill Climbing", "Local Search", "steepest_ascent_hill_climbing",
        "Best neighboring h(n)", "local",
    ),
    PathAlgorithmSpec(
        "Stochastic Hill Climbing", "Local Search", "stochastic_hill_climbing",
        "Random improving h(n)", "local",
    ),
    PathAlgorithmSpec(
        "Random-Restart Hill Climbing", "Local Search", "random_restart_hill_climbing",
        "Restart + local h(n)", "local",
    ),
    PathAlgorithmSpec(
        "Local Beam Search", "Local Search", "local_beam_search", "Best k states", "local"
    ),
    PathAlgorithmSpec(
        "Simulated Annealing", "Local Search", "simulated_annealing",
        "Temperature + acceptance probability", "local",
    ),
)

PATH_ALGORITHM_BY_NAME = {spec.name: spec for spec in PATH_ALGORITHM_SPECS}
PATH_ALGORITHM_GROUPS = {
    group: tuple(spec.name for spec in PATH_ALGORITHM_SPECS if spec.group == group)
    for group in ("Uninformed Search", "Informed Search", "Local Search")
}

_SOLVER_FUNCTIONS: dict[str, Callable[..., SearchResult]] = {
    "bfs": uninformed.bfs,
    "dfs": uninformed.dfs,
    "ucs": uninformed.ucs,
    "ids": uninformed.ids,
    "greedy_best_first": informed.greedy_best_first,
    "a_star": informed.a_star,
    "ida_star": informed.ida_star,
    "simple_hill_climbing": local_search.simple_hill_climbing,
    "steepest_ascent_hill_climbing": local_search.steepest_ascent_hill_climbing,
    "stochastic_hill_climbing": local_search.stochastic_hill_climbing,
    "random_restart_hill_climbing": local_search.random_restart_hill_climbing,
    "local_beam_search": local_search.local_beam_search,
    "simulated_annealing": local_search.simulated_annealing,
}


def run_path_algorithm(
    algorithm: str,
    *,
    start: tuple[int, ...],
    goal: tuple[int, ...],
    settings: PathRunSettings | None = None,
) -> SearchResult:
    """Run one registered algorithm with a comparable state/action contract."""
    if algorithm not in PATH_ALGORITHM_BY_NAME:
        raise ValueError(f"Unsupported path algorithm: {algorithm}")

    settings = settings or PathRunSettings()
    spec = PATH_ALGORITHM_BY_NAME[algorithm]
    extra_params = (
        {"seed": int(settings.seed)}
        if is_randomized_solver(spec.function_name)
        else None
    )
    kwargs = build_solver_kwargs(
        spec.function_name,
        start=start,
        goal=goal,
        timeout=float(settings.timeout),
        action_order=settings.action_order,
        max_nodes=int(settings.max_nodes),
        max_depth=int(settings.max_depth),
        heuristic=settings.heuristic,
        tie_breaker=settings.tie_breaker,
        extra_params=extra_params,
    )
    result = _SOLVER_FUNCTIONS[spec.function_name](**kwargs)
    result.capability = algorithm_capability(algorithm)
    result.random_seed = settings.seed if extra_params else None
    return result
