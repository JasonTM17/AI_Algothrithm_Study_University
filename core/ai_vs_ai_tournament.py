"""AI-vs-AI tournament scoring for 15-puzzle solver agents."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from algorithms.informed import a_star, greedy_best_first, ida_star
from algorithms.local_search import (
    local_beam_search,
    random_restart_hill_climbing,
    simple_hill_climbing,
    simulated_annealing,
    steepest_ascent_hill_climbing,
    stochastic_hill_climbing,
)
from algorithms.uninformed import bfs, dfs, ids, ucs
from core.metrics import SearchResult
from core.puzzle import GOAL_STATE, scramble
from core.randomness import is_randomized_solver
from core.solver_dispatch import build_solver_kwargs


ELIGIBLE_TOURNAMENT_SOLVERS: dict[str, str] = {
    "BFS": "bfs",
    "DFS": "dfs",
    "UCS": "ucs",
    "IDS": "ids",
    "Greedy Best-First": "greedy_best_first",
    "A*": "a_star",
    "IDA*": "ida_star",
    "Simple Hill Climbing": "simple_hill_climbing",
    "Steepest-Ascent Hill Climbing": "steepest_ascent_hill_climbing",
    "Stochastic Hill Climbing": "stochastic_hill_climbing",
    "Random-Restart Hill Climbing": "random_restart_hill_climbing",
    "Local Beam Search": "local_beam_search",
    "Simulated Annealing": "simulated_annealing",
}

_SOLVER_FUNCTIONS: dict[str, Callable[..., SearchResult]] = {
    "bfs": bfs,
    "dfs": dfs,
    "ucs": ucs,
    "ids": ids,
    "greedy_best_first": greedy_best_first,
    "a_star": a_star,
    "ida_star": ida_star,
    "simple_hill_climbing": simple_hill_climbing,
    "steepest_ascent_hill_climbing": steepest_ascent_hill_climbing,
    "stochastic_hill_climbing": stochastic_hill_climbing,
    "random_restart_hill_climbing": random_restart_hill_climbing,
    "local_beam_search": local_beam_search,
    "simulated_annealing": simulated_annealing,
}


@dataclass(frozen=True)
class TournamentAgentConfig:
    """A solver entry in an AI-vs-AI tournament."""

    label: str
    solver_name: str
    seed: int | None = None


@dataclass
class AgentRoundScore:
    """Score assigned to one agent for one puzzle round."""

    agent_label: str
    algorithm: str
    points: int
    status: str
    reason: str
    cost: int | None = None
    optimal_cost: int | None = None
    excess_cost: int | None = None
    runtime: float = 0.0
    nodes: int = 0
    random_seed: int | None = None


@dataclass
class TournamentRoundResult:
    """One shared puzzle round and both scored agent outputs."""

    round_number: int
    start_state: tuple[int, ...]
    goal_state: tuple[int, ...]
    optimal_cost: int | None
    reference_status: str
    agent_a: AgentRoundScore | None = None
    agent_b: AgentRoundScore | None = None


@dataclass
class TournamentResult:
    """Aggregate AI-vs-AI tournament result."""

    rounds: list[TournamentRoundResult] = field(default_factory=list)
    agent_a_label: str = "AI A"
    agent_b_label: str = "AI B"
    agent_a_total: int = 0
    agent_b_total: int = 0
    winner: str = "Draw"
    tie_break_detail: str = ""


def score_search_result(
    result: SearchResult | None,
    *,
    agent_label: str,
    algorithm: str,
    optimal_cost: int,
    exception_message: str | None = None,
) -> AgentRoundScore:
    """Convert a solver result into fixed tournament points."""
    if exception_message:
        return AgentRoundScore(
            agent_label=agent_label,
            algorithm=algorithm,
            points=-50,
            status="exception",
            reason=f"Solver raised an exception: {exception_message}",
            optimal_cost=optimal_cost,
        )
    if result is None:
        return AgentRoundScore(
            agent_label=agent_label,
            algorithm=algorithm,
            points=-20,
            status="no_result",
            reason="Solver did not return a result.",
            optimal_cost=optimal_cost,
        )
    runtime = float(result.runtime or 0.0)
    nodes = int(result.nodes_expanded or 0)
    if result.path and not result.path_verified:
        return AgentRoundScore(
            agent_label=agent_label,
            algorithm=result.algorithm or algorithm,
            points=-50,
            status="invalid_path",
            reason=result.verification_message or "Recorded path is not a legal action sequence.",
            cost=len(result.actions) if result.actions else None,
            optimal_cost=optimal_cost,
            runtime=runtime,
            nodes=nodes,
            random_seed=result.random_seed,
        )
    if result.path_verified and result.goal_reached:
        cost = len(result.actions)
        excess = max(0, cost - optimal_cost)
        points = 100 if excess == 0 else max(20, 100 - 10 * excess)
        status = "optimal" if excess == 0 else "suboptimal"
        reason = (
            "Legal path reaches goal with optimal cost."
            if excess == 0
            else f"Legal path reaches goal but is {excess} move(s) longer than optimal."
        )
        return AgentRoundScore(
            agent_label=agent_label,
            algorithm=result.algorithm or algorithm,
            points=points,
            status=status,
            reason=reason,
            cost=cost,
            optimal_cost=optimal_cost,
            excess_cost=excess,
            runtime=runtime,
            nodes=nodes,
            random_seed=result.random_seed,
        )
    if result.path_verified and not result.goal_reached:
        return AgentRoundScore(
            agent_label=agent_label,
            algorithm=result.algorithm or algorithm,
            points=-10,
            status="partial_path",
            reason=result.verification_message or "Legal path stopped before reaching goal.",
            cost=len(result.actions),
            optimal_cost=optimal_cost,
            runtime=runtime,
            nodes=nodes,
            random_seed=result.random_seed,
        )
    return AgentRoundScore(
        agent_label=agent_label,
        algorithm=result.algorithm or algorithm,
        points=-20,
        status=result.termination_reason or "failed",
        reason=result.message or "Solver failed to produce a path.",
        optimal_cost=optimal_cost,
        runtime=runtime,
        nodes=nodes,
        random_seed=result.random_seed,
    )


def run_ai_vs_ai_tournament(
    agent_a: TournamentAgentConfig,
    agent_b: TournamentAgentConfig,
    *,
    start: tuple[int, ...],
    goal: tuple[int, ...] = GOAL_STATE,
    rounds: int = 1,
    round_depth: int = 10,
    base_seed: int = 42,
    timeout: float = 30.0,
    max_nodes: int = 50_000,
    max_depth: int = 20,
    heuristic: str = "Manhattan Distance",
    action_order: str = "LRUD",
) -> TournamentResult:
    """Run two solver agents against the same 15-puzzle rounds."""
    result = TournamentResult(
        agent_a_label=agent_a.label,
        agent_b_label=agent_b.label,
    )
    for round_index in range(max(1, rounds)):
        round_start = (
            start
            if round_index == 0
            else scramble(goal=goal, depth=round_depth, seed=base_seed + round_index)
        )
        reference = _run_reference_solver(
            round_start,
            goal,
            timeout=max(float(timeout), 60.0),
            max_nodes=max(int(max_nodes), 300_000),
            heuristic=heuristic,
            action_order=action_order,
        )
        if not reference.optimality_proven:
            result.rounds.append(TournamentRoundResult(
                round_number=round_index + 1,
                start_state=round_start,
                goal_state=goal,
                optimal_cost=None,
                reference_status=(
                    "Reference failed: A* did not prove an optimal path for this round."
                ),
            ))
            continue
        optimal_cost = len(reference.actions)
        round_result = TournamentRoundResult(
            round_number=round_index + 1,
            start_state=round_start,
            goal_state=goal,
            optimal_cost=optimal_cost,
            reference_status=f"A* reference proven at cost {optimal_cost}.",
        )
        round_result.agent_a = _run_and_score_agent(
            agent_a,
            round_start,
            goal,
            optimal_cost,
            round_index,
            timeout=timeout,
            max_nodes=max_nodes,
            max_depth=max_depth,
            heuristic=heuristic,
            action_order=action_order,
        )
        round_result.agent_b = _run_and_score_agent(
            agent_b,
            round_start,
            goal,
            optimal_cost,
            round_index,
            timeout=timeout,
            max_nodes=max_nodes,
            max_depth=max_depth,
            heuristic=heuristic,
            action_order=action_order,
        )
        result.agent_a_total += round_result.agent_a.points
        result.agent_b_total += round_result.agent_b.points
        result.rounds.append(round_result)
    _classify_tournament(result)
    return result


def _run_reference_solver(
    start: tuple[int, ...],
    goal: tuple[int, ...],
    *,
    timeout: float,
    max_nodes: int,
    heuristic: str,
    action_order: str,
) -> SearchResult:
    return a_star(
        start=start,
        goal=goal,
        timeout=timeout,
        action_order=action_order,
        max_nodes=max_nodes,
        heuristic=heuristic,
    )


def _run_and_score_agent(
    agent: TournamentAgentConfig,
    start: tuple[int, ...],
    goal: tuple[int, ...],
    optimal_cost: int,
    round_index: int,
    *,
    timeout: float,
    max_nodes: int,
    max_depth: int,
    heuristic: str,
    action_order: str,
) -> AgentRoundScore:
    fn = _SOLVER_FUNCTIONS.get(agent.solver_name)
    if fn is None:
        return score_search_result(
            None,
            agent_label=agent.label,
            algorithm=agent.solver_name,
            optimal_cost=optimal_cost,
            exception_message=f"Unknown tournament solver: {agent.solver_name}",
        )
    seed = _round_seed(agent, round_index)
    try:
        kwargs = _build_agent_kwargs(
            agent.solver_name,
            start=start,
            goal=goal,
            timeout=timeout,
            action_order=action_order,
            max_nodes=max_nodes,
            max_depth=max_depth,
            heuristic=heuristic,
            seed=seed,
        )
        solver_result = fn(**kwargs)
        solver_result.random_seed = seed
        return score_search_result(
            solver_result,
            agent_label=agent.label,
            algorithm=agent.solver_name,
            optimal_cost=optimal_cost,
        )
    except Exception as exc:
        return score_search_result(
            None,
            agent_label=agent.label,
            algorithm=agent.solver_name,
            optimal_cost=optimal_cost,
            exception_message=str(exc),
        )


def _build_agent_kwargs(
    fn_name: str,
    *,
    start: tuple[int, ...],
    goal: tuple[int, ...],
    timeout: float,
    action_order: str,
    max_nodes: int,
    max_depth: int,
    heuristic: str,
    seed: int | None,
) -> dict:
    extra_params: dict[str, int | float] = {}
    if fn_name in {
        "simple_hill_climbing",
        "steepest_ascent_hill_climbing",
        "stochastic_hill_climbing",
        "local_beam_search",
        "simulated_annealing",
    }:
        extra_params["max_iterations"] = max_nodes
    elif fn_name == "random_restart_hill_climbing":
        extra_params["max_iterations"] = max(1, max_nodes // 20)
        extra_params["max_restarts"] = 20
    if fn_name == "local_beam_search":
        extra_params["beam_width"] = 3
    if seed is not None:
        extra_params["seed"] = seed
    return build_solver_kwargs(
        fn_name,
        start=start,
        goal=goal,
        timeout=timeout,
        action_order=action_order,
        max_nodes=max_nodes,
        max_depth=max_depth,
        heuristic=heuristic,
        extra_params=extra_params,
    )


def _round_seed(agent: TournamentAgentConfig, round_index: int) -> int | None:
    if not is_randomized_solver(agent.solver_name):
        return None
    return (agent.seed if agent.seed is not None else 42) + round_index


def _classify_tournament(result: TournamentResult) -> None:
    if result.agent_a_total > result.agent_b_total:
        result.winner = result.agent_a_label
        result.tie_break_detail = "Winner by total score."
        return
    if result.agent_b_total > result.agent_a_total:
        result.winner = result.agent_b_label
        result.tie_break_detail = "Winner by total score."
        return
    a_key = _tie_break_key(result, "agent_a")
    b_key = _tie_break_key(result, "agent_b")
    if a_key > b_key:
        result.winner = result.agent_a_label
        result.tie_break_detail = "Winner by solved rounds, excess cost, runtime, then nodes."
    elif b_key > a_key:
        result.winner = result.agent_b_label
        result.tie_break_detail = "Winner by solved rounds, excess cost, runtime, then nodes."
    else:
        result.winner = "Draw"
        result.tie_break_detail = "Scores and tie-break metrics are equal."


def _tie_break_key(result: TournamentResult, field_name: str) -> tuple[int, int, float, int]:
    scores = [
        getattr(round_result, field_name)
        for round_result in result.rounds
        if getattr(round_result, field_name) is not None
    ]
    solved = sum(1 for score in scores if score.status in {"optimal", "suboptimal"})
    excess = sum(score.excess_cost or 0 for score in scores)
    runtime = sum(score.runtime for score in scores)
    nodes = sum(score.nodes for score in scores)
    return (solved, -excess, -runtime, -nodes)
