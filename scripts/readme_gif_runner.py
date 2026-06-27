"""Run real algorithm demos for README GIF generation."""

from __future__ import annotations

import importlib
from dataclasses import dataclass

from core.ai_vs_ai_tournament import TournamentAgentConfig, run_ai_vs_ai_tournament
from core.heuristics import manhattan_distance
from core.metrics import SearchResult
from core.solver_dispatch import build_solver_kwargs
from scripts.readme_gif_specs import DemoSpec


@dataclass
class DemoEvidence:
    spec: DemoSpec
    result: SearchResult | None
    states: list[tuple[int, ...]]
    actions: list[str]
    facts: list[str]
    termination: str
    path_verified: bool
    goal_reached: bool
    optimality_proven: bool


MODULES = (
    "algorithms.uninformed",
    "algorithms.informed",
    "algorithms.local_search",
    "algorithms.complex_env",
    "algorithms.csp",
    "algorithms.adversarial",
)


def run_demo(spec: DemoSpec) -> DemoEvidence:
    if spec.mode == "tournament":
        return _run_tournament(spec)

    fn = _load_function(spec.function_name)
    kwargs = build_solver_kwargs(
        spec.function_name,
        start=spec.start,
        goal=spec.goal,
        timeout=10.0,
        action_order="LRUD",
        max_nodes=8000,
        max_depth=int(spec.params.get("max_depth", 10)),
        heuristic="Manhattan Distance",
        extra_params=dict(spec.params),
    )
    result: SearchResult = fn(**kwargs)
    _assert_real_evidence(spec, result)
    states = _select_states(spec, result)
    facts = _result_facts(result)
    return DemoEvidence(
        spec=spec,
        result=result,
        states=states,
        actions=list(result.actions),
        facts=facts,
        termination=result.termination_reason,
        path_verified=result.path_verified,
        goal_reached=result.goal_reached,
        optimality_proven=result.optimality_proven,
    )


def _load_function(function_name: str):
    for module_name in MODULES:
        module = importlib.import_module(module_name)
        if hasattr(module, function_name):
            return getattr(module, function_name)
    raise KeyError(f"Solver function not found: {function_name}")


def _assert_real_evidence(spec: DemoSpec, result: SearchResult) -> None:
    if not isinstance(result, SearchResult):
        raise TypeError(f"{spec.algorithm} did not return SearchResult")
    if spec.expects_goal_path and not (result.path_verified and result.goal_reached):
        raise RuntimeError(f"{spec.algorithm} demo did not prove a legal goal path")
    if not result.trace and not result.path and not result.message:
        raise RuntimeError(f"{spec.algorithm} produced no visible evidence")


def _select_states(spec: DemoSpec, result: SearchResult) -> list[tuple[int, ...]]:
    if result.path:
        return _sample_sequence(result.path, 8)
    trace_states = [step.state for step in result.trace if _is_state(step.state)]
    if trace_states:
        return _sample_sequence([spec.start, *trace_states], 8)
    return [spec.start, spec.goal, spec.start, spec.goal, spec.start, spec.goal]


def _sample_sequence(states: list[tuple[int, ...]], max_count: int) -> list[tuple[int, ...]]:
    if len(states) <= max_count:
        sample = list(states)
    else:
        step = (len(states) - 1) / (max_count - 1)
        sample = [states[round(index * step)] for index in range(max_count)]
    while len(sample) < 6:
        sample.append(sample[-1])
    return sample[:10]


def _is_state(value: object) -> bool:
    return isinstance(value, tuple) and len(value) == 16 and set(value) == set(range(16))


def _result_facts(result: SearchResult) -> list[str]:
    facts = [
        f"termination={result.termination_reason}",
        f"expanded={result.nodes_expanded}",
        f"generated={result.nodes_generated}",
    ]
    if result.path_verified:
        facts.append(f"path={len(result.actions)} legal moves")
    if result.optimality_proven:
        facts.append("optimality certificate=true")
    if result.trace:
        last = result.trace[min(len(result.trace) - 1, 4)]
        facts.append((last.reason or last.event or "trace evidence")[:58])
    return facts


def _run_tournament(spec: DemoSpec) -> DemoEvidence:
    tournament = run_ai_vs_ai_tournament(
        TournamentAgentConfig("A*", "a_star"),
        TournamentAgentConfig("Greedy", "greedy_best_first"),
        start=spec.start,
        goal=spec.goal,
        rounds=1,
        round_depth=5,
        base_seed=spec.seed,
        timeout=10.0,
        max_nodes=8000,
        max_depth=10,
    )
    round_result = tournament.rounds[0]
    facts = [
        f"{tournament.agent_a_label}: {tournament.agent_a_total} pts",
        f"{tournament.agent_b_label}: {tournament.agent_b_total} pts",
        f"winner={tournament.winner}",
        round_result.reference_status,
    ]
    states = [round_result.start_state, spec.goal] * 3
    return DemoEvidence(
        spec=spec,
        result=None,
        states=states,
        actions=[],
        facts=facts,
        termination="tournament_scored",
        path_verified=True,
        goal_reached=False,
        optimality_proven=False,
    )
