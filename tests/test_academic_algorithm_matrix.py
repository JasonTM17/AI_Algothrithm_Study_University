"""End-to-end academic contract matrix for every displayed algorithm/model."""

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
from core.academic import (
    ALGORITHM_TAXONOMY,
    CONTRAST_DEMO,
    ILLUSTRATIVE_EXTENSION,
    REAL_SOLVER,
    STOCHASTIC_GAME_DEMO,
)
from core.ai_vs_ai_tournament import (
    TournamentAgentConfig,
    run_ai_vs_ai_tournament,
)
from core.puzzle import GOAL_STATE


ONE_MOVE = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 0, 15)


MODEL_CASES = [
    ("BFS", lambda: bfs(ONE_MOVE, timeout=5)),
    ("DFS", lambda: dfs(ONE_MOVE, max_depth=5, timeout=5)),
    ("UCS", lambda: ucs(ONE_MOVE, timeout=5)),
    ("IDS", lambda: ids(ONE_MOVE, max_depth=5, timeout=5)),
    ("Greedy Best-First", lambda: greedy_best_first(ONE_MOVE, timeout=5)),
    ("A*", lambda: a_star(ONE_MOVE, timeout=5)),
    ("IDA*", lambda: ida_star(ONE_MOVE, timeout=5)),
    ("Simple Hill Climbing", lambda: simple_hill_climbing(ONE_MOVE, timeout=5)),
    (
        "Steepest-Ascent Hill Climbing",
        lambda: steepest_ascent_hill_climbing(ONE_MOVE, timeout=5),
    ),
    (
        "Stochastic Hill Climbing",
        lambda: stochastic_hill_climbing(ONE_MOVE, timeout=5, seed=1),
    ),
    (
        "Random-Restart Hill Climbing",
        lambda: random_restart_hill_climbing(
            ONE_MOVE, timeout=5, max_restarts=2, seed=1,
        ),
    ),
    (
        "Local Beam Search",
        lambda: local_beam_search(ONE_MOVE, timeout=5, beam_width=2),
    ),
    (
        "Simulated Annealing",
        lambda: simulated_annealing(
            ONE_MOVE, timeout=5, max_iterations=100, seed=1,
        ),
    ),
    (
        "AND-OR Search",
        lambda: and_or_search(
            ONE_MOVE, max_depth=1, nondet_prob=0.0, timeout=5,
        ),
    ),
    (
        "No Observation Search",
        lambda: no_observation_search(
            ONE_MOVE, num_belief_states=1, max_steps=1,
            action_order="RULD", timeout=5, seed=1,
        ),
    ),
    (
        "Partially Observable Search",
        lambda: partially_observable_search(
            ONE_MOVE, num_belief_states=1, max_steps=1,
            action_order="RULD", timeout=5, seed=1,
        ),
    ),
    (
        "LRTA*",
        lambda: online_search_lrta(
            ONE_MOVE, max_steps=2, action_order="RULD", timeout=5,
        ),
    ),
    ("CSP Definition", lambda: csp_definition(ONE_MOVE, time_horizon=1)),
    (
        "Constraint Propagation",
        lambda: constraint_propagation(ONE_MOVE, time_horizon=1),
    ),
    ("Path Consistency", lambda: path_consistency(ONE_MOVE)),
    ("Global Constraints", lambda: global_constraints(ONE_MOVE)),
    (
        "Backtracking Search",
        lambda: backtracking_search(ONE_MOVE, max_steps=100, timeout=5),
    ),
    (
        "Min-Conflicts",
        lambda: min_conflicts(GOAL_STATE, max_iterations=1, timeout=5, seed=1),
    ),
    (
        "Constraint Graphs",
        lambda: solve_csp_constraint_graphs(ONE_MOVE, time_horizon=1),
    ),
    ("Minimax", lambda: minimax(ONE_MOVE, depth=1, timeout=5)),
    (
        "Alpha-Beta Pruning",
        lambda: alpha_beta_pruning(ONE_MOVE, depth=1, timeout=5),
    ),
    (
        "Expectimax",
        lambda: expectimax(ONE_MOVE, depth=1, timeout=5, seed=1),
    ),
]


@pytest.mark.parametrize("expected_name, run_model", MODEL_CASES)
def test_displayed_model_matches_taxonomy_and_certificate_role(expected_name, run_model):
    result = run_model()
    taxonomy = ALGORITHM_TAXONOMY[expected_name]

    assert result.algorithm == expected_name
    if taxonomy.role == REAL_SOLVER:
        assert result.success
        assert result.path_verified
        assert result.goal_reached
        assert result.optimality_proven
    elif taxonomy.role == CONTRAST_DEMO:
        assert not result.optimality_proven
        if result.success:
            assert result.path_verified
            assert result.goal_reached
    elif taxonomy.role in {ILLUSTRATIVE_EXTENSION, STOCHASTIC_GAME_DEMO}:
        assert result.suitable_for_puzzle is False
        assert not result.optimality_proven


def test_matrix_covers_every_displayed_algorithm_including_tournament():
    covered = {name for name, _ in MODEL_CASES} | {"AI-vs-AI Tournament"}
    assert covered == set(ALGORITHM_TAXONOMY)

    tournament = run_ai_vs_ai_tournament(
        TournamentAgentConfig("AI A", "a_star"),
        TournamentAgentConfig("AI B", "greedy_best_first"),
        start=ONE_MOVE,
        rounds=1,
        timeout=5,
        max_nodes=1000,
    )
    assert tournament.rounds[0].agent_a.path_verified
    assert tournament.rounds[0].agent_b.path_verified
