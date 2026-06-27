"""Registry-wide algorithm contract tests for solver evidence."""

from __future__ import annotations

import inspect

import pytest

from algorithms.adversarial import alpha_beta_pruning, expectimax, minimax
from algorithms.complex_env import (
    and_or_search,
    no_observation_search,
    online_search_lrta,
    partially_observable_search,
)
from algorithms.csp import (
    backtracking_search,
    constraint_propagation,
    csp_definition,
    global_constraints,
    min_conflicts,
    path_consistency,
    solve_csp_constraint_graphs,
)
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
from core.academic import ALGORITHM_TAXONOMY
from core.ai_vs_ai_tournament import TournamentAgentConfig, run_ai_vs_ai_tournament
from core.metrics import SearchResult
from core.puzzle import GOAL_STATE, _move_blank, scramble
from core.randomness import RANDOMIZED_SOLVERS
from core.solver_dispatch import build_solver_kwargs
from ui.styles import ALGORITHM_FN_MAP, ALGORITHM_GROUPS


CUSTOM_GOAL = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 0, 15)
OPPOSITE_PARITY_GOAL = (2, 1, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 0)
PROVEN_OPTIMAL_ON_ONE_MOVE = {"BFS", "UCS", "IDS", "A*", "IDA*"}
_SOLVERS = (
    bfs, dfs, ucs, ids, greedy_best_first, a_star, ida_star,
    simple_hill_climbing, steepest_ascent_hill_climbing, stochastic_hill_climbing,
    random_restart_hill_climbing, local_beam_search, simulated_annealing,
    and_or_search, no_observation_search, partially_observable_search, online_search_lrta,
    csp_definition, constraint_propagation, path_consistency, global_constraints,
    backtracking_search, min_conflicts, solve_csp_constraint_graphs,
    minimax, alpha_beta_pruning, expectimax,
)
SOLVER_FUNCTIONS = {fn.__name__: fn for fn in _SOLVERS}


def _displayed_solver_cases() -> list[tuple[str, str]]:
    cases = []
    for display_names in ALGORITHM_GROUPS.values():
        for display_name in display_names:
            fn_name = ALGORITHM_FN_MAP[display_name]
            if fn_name != "ai_vs_ai_tournament":
                cases.append((display_name, fn_name))
    return cases


def _call_from_dispatch(fn_name: str, start: tuple[int, ...], goal: tuple[int, ...]) -> SearchResult:
    fn = SOLVER_FUNCTIONS[fn_name]
    kwargs = build_solver_kwargs(
        fn_name,
        start=start,
        goal=goal,
        timeout=2,
        action_order="LRUD",
        max_nodes=250,
        max_depth=1,
        heuristic="Manhattan Distance",
        tie_breaker="FIFO",
    )
    extras = {
        "beam_width": 2,
        "cooling_rate": 0.8,
        "depth": 1,
        "initial_temp": 10.0,
        "max_iterations": 20,
        "max_restarts": 2,
        "min_temp": 0.01,
        "nondet_prob": 0.0,
        "num_belief_states": 1,
        "seed": 123,
        "success_prob": 0.6,
        "time_horizon": 1,
    }
    signature = inspect.signature(fn)
    for name, value in extras.items():
        if name in signature.parameters and name not in kwargs:
            kwargs[name] = value
    return fn(**kwargs)


def _assert_legal_recorded_path(result: SearchResult, start: tuple[int, ...]) -> None:
    assert len(result.path) == len(result.actions) + 1
    assert result.path[0] == start
    current = start
    for action, recorded_state in zip(result.actions, result.path[1:]):
        current = _move_blank(current, action)
        assert current is not None
        assert current == recorded_state
    assert result.path_verified
    assert result.goal_reached is (result.path[-1] == result.goal_state)


def test_display_registry_and_taxonomy_stay_in_lockstep():
    displayed = {name for names in ALGORITHM_GROUPS.values() for name in names}

    assert displayed == set(ALGORITHM_FN_MAP)
    assert displayed == set(ALGORITHM_TAXONOMY)
    assert set(ALGORITHM_FN_MAP.values()) - {"ai_vs_ai_tournament"} == set(SOLVER_FUNCTIONS)


@pytest.mark.parametrize("display_name, fn_name", _displayed_solver_cases())
def test_every_displayed_solver_reports_requested_goal_and_safe_certificate(
    display_name: str,
    fn_name: str,
):
    result = _call_from_dispatch(fn_name, GOAL_STATE, CUSTOM_GOAL)

    assert isinstance(result, SearchResult)
    assert result.algorithm == display_name
    assert result.group
    assert result.goal_state == CUSTOM_GOAL
    assert result.runtime >= 0

    if result.path:
        _assert_legal_recorded_path(result, GOAL_STATE)
    else:
        assert not result.path_verified
        assert not result.goal_reached

    if result.success and result.termination_reason == "goal":
        assert result.path_verified
        assert result.goal_reached
        assert result.cost == len(result.actions)
    if result.optimality_proven:
        assert result.success
        assert result.path_verified
        assert result.goal_reached
        assert result.is_optimal
    if display_name in PROVEN_OPTIMAL_ON_ONE_MOVE:
        assert result.optimality_proven
        assert result.actions == ["L"]
    elif result.algorithm not in PROVEN_OPTIMAL_ON_ONE_MOVE:
        assert not result.optimality_proven
    if fn_name in RANDOMIZED_SOLVERS:
        assert result.random_seed == 123


@pytest.mark.parametrize("depth", range(1, 6))
@pytest.mark.parametrize("display_name, fn_name", _displayed_solver_cases())
def test_algorithm_contract_sweep_on_shallow_scrambles(
    display_name: str,
    fn_name: str,
    depth: int,
):
    start = scramble(goal=GOAL_STATE, depth=depth, seed=4100 + depth)
    result = _call_from_dispatch(fn_name, start, GOAL_STATE)

    assert isinstance(result, SearchResult), display_name
    assert result.algorithm == display_name
    assert result.goal_state == GOAL_STATE
    assert result.runtime >= 0
    if result.path:
        _assert_legal_recorded_path(result, start)
    else:
        assert not result.path_verified
        assert not result.goal_reached
    if result.success and result.termination_reason == "goal":
        assert result.path_verified
        assert result.goal_reached


@pytest.mark.parametrize(
    "solver, kwargs",
    [
        (simulated_annealing, {"max_iterations": 1, "seed": 17}),
        (
            no_observation_search,
            {"num_belief_states": 1, "max_steps": 1, "seed": 17},
        ),
    ],
)
def test_legal_non_goal_trajectory_is_not_certified_as_a_solution(solver, kwargs):
    start = scramble(goal=GOAL_STATE, depth=5, seed=5521)
    result = solver(start, goal=GOAL_STATE, timeout=2, **kwargs)

    assert not result.success
    assert result.path_verified
    assert not result.goal_reached
    _assert_legal_recorded_path(result, start)


@pytest.mark.parametrize("solver, kwargs", [
    (bfs, {}),
    (dfs, {"max_depth": 2}),
    (ucs, {}),
    (ids, {"max_depth": 2}),
    (greedy_best_first, {}),
    (a_star, {}),
    (ida_star, {}),
])
def test_unsolvable_tree_search_failures_keep_requested_goal_without_claims(solver, kwargs):
    result = solver(GOAL_STATE, goal=OPPOSITE_PARITY_GOAL, timeout=1, **kwargs)

    assert not result.success
    assert result.goal_state == OPPOSITE_PARITY_GOAL
    assert not result.path
    assert not result.path_verified
    assert not result.goal_reached
    assert not result.optimality_proven


def test_ai_vs_ai_tournament_scores_only_verified_goal_paths():
    result = run_ai_vs_ai_tournament(
        TournamentAgentConfig("Reference", "a_star"),
        TournamentAgentConfig("Baseline", "greedy_best_first"),
        start=CUSTOM_GOAL,
        rounds=1,
        timeout=5,
        max_nodes=1000,
    )

    round_result = result.rounds[0]
    assert round_result.goal_state == GOAL_STATE
    for score in (round_result.agent_a, round_result.agent_b):
        assert score is not None
        assert score.path_verified
        assert score.goal_reached
        assert score.status in {"optimal", "suboptimal"}
