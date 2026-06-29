"""Parameter dispatch helpers for algorithm calls from the Streamlit UI."""

from __future__ import annotations

from typing import Any


CSP_FUNCTIONS = {
    "backtracking_search",
    "backtracking_forward_checking",
    "constraint_propagation",
    "min_conflicts",
}


def build_solver_kwargs(
    fn_name: str,
    *,
    start: tuple[int, ...],
    goal: tuple[int, ...],
    timeout: float,
    action_order: str,
    max_nodes: int,
    max_depth: int,
    heuristic: str,
    tie_breaker: str = "FIFO",
    extra_params: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build keyword arguments that match each solver function signature."""
    if fn_name in CSP_FUNCTIONS:
        kwargs: dict[str, Any] = {
            "start": start,
            "goal": goal,
            "timeout": timeout,
            "action_order": action_order,
            "time_horizon": max(1, min(max_depth, 12)),
            "candidate_limit": max_nodes,
        }
    else:
        kwargs = {
            "start": start,
            "goal": goal,
            "timeout": timeout,
            "action_order": action_order,
        }

    if fn_name in ("bfs", "ucs"):
        kwargs["max_nodes"] = max_nodes
        if fn_name == "ucs":
            kwargs["tie_breaker"] = tie_breaker
    elif fn_name in ("dfs", "ids"):
        kwargs["max_nodes"] = max_nodes
        kwargs["max_depth"] = max_depth
    elif fn_name in ("greedy_best_first", "a_star", "ida_star"):
        kwargs["max_nodes"] = max_nodes
        kwargs["heuristic"] = heuristic
        if fn_name in ("greedy_best_first", "a_star"):
            kwargs["tie_breaker"] = tie_breaker
    elif fn_name == "and_or_search":
        kwargs["max_depth"] = max_depth
    elif fn_name in ("no_observation_search", "partially_observable_search"):
        kwargs["max_steps"] = max_depth
    elif fn_name in ("backtracking_search", "backtracking_forward_checking"):
        kwargs["max_steps"] = max_nodes
    elif fn_name == "min_conflicts":
        kwargs["max_iterations"] = max_nodes
    elif fn_name in (
        "simple_hill_climbing",
        "steepest_ascent_hill_climbing",
        "stochastic_hill_climbing",
        "random_restart_hill_climbing",
        "local_beam_search",
        "simulated_annealing",
    ):
        kwargs["heuristic"] = heuristic
        kwargs["max_iterations"] = max_nodes
    elif fn_name in (
        "minimax",
        "alpha_beta_pruning",
        "expectimax",
    ):
        kwargs["heuristic"] = heuristic

    if extra_params:
        solver_params = dict(extra_params)
        for runner_key in ("max_depth", "max_nodes", "timeout"):
            solver_params.pop(runner_key, None)
        kwargs.update(solver_params)

    return kwargs
