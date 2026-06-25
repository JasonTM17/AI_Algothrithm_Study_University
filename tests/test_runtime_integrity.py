"""Runtime integrity tests for import and compile regressions."""

import py_compile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_all_python_sources_compile():
    sources = [ROOT / "app.py"]
    for directory in ("core", "algorithms", "ui"):
        sources.extend((ROOT / directory).glob("*.py"))
    for source in sources:
        py_compile.compile(str(source), doraise=True)


def test_theory_import_has_key_algorithms():
    from core.theory import THEORY, THEORY_BY_GROUP

    for key in ["BFS", "A*", "IDA*", "Minimax", "Expectimax"]:
        assert key in THEORY
        assert THEORY[key]["name"]

    assert "Uninformed Search" in THEORY_BY_GROUP
    assert "BFS" in THEORY_BY_GROUP["Uninformed Search"]


def test_search_tree_renderer_has_no_legacy_trace_fallback():
    components_source = (ROOT / "ui" / "components.py").read_text(encoding="utf-8")
    hand_tracing_source = (ROOT / "ui" / "hand_tracing.py").read_text(encoding="utf-8")

    assert "_render_legacy_search_trace" not in components_source
    assert "search_tree_to_dot" in components_source
    assert "Every edge is backed by a legal puzzle action" in components_source
    assert "hand_trace_tree_dot" in hand_tracing_source
    assert "st.graphviz_chart" in hand_tracing_source
    assert "Compatibility for tree display" not in hand_tracing_source


def test_advanced_mode_function_kwargs_match_app_dispatch():
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
        min_conflicts,
        path_consistency,
        solve_csp_constraint_graphs,
    )
    from core.puzzle import GOAL_STATE

    base_kw = dict(start=GOAL_STATE, goal=GOAL_STATE)
    csp_search_kw = dict(**base_kw, timeout=1.0)
    search_kw = dict(**base_kw, timeout=1.0, action_order="LRUD")

    calls = [
        lambda: csp_definition(time_horizon=1, **base_kw),
        lambda: constraint_propagation(time_horizon=1, **base_kw),
        lambda: backtracking_search(**csp_search_kw, max_steps=10),
        lambda: min_conflicts(**csp_search_kw, max_iterations=10, seed=1),
        lambda: solve_csp_constraint_graphs(time_horizon=1, **base_kw),
        lambda: path_consistency(**base_kw),
        lambda: and_or_search(max_depth=1, nondet_prob=0.2, seed=1, **search_kw),
        lambda: no_observation_search(num_belief_states=2, max_steps=1, seed=1, **search_kw),
        lambda: partially_observable_search(num_belief_states=2, max_steps=1, seed=1, **search_kw),
        lambda: online_search_lrta(heuristic="Manhattan Distance", max_steps=1, **search_kw),
        lambda: minimax(depth=1, heuristic="Manhattan Distance", **search_kw),
        lambda: alpha_beta_pruning(depth=1, heuristic="Manhattan Distance", **search_kw),
        lambda: expectimax(depth=1, heuristic="Manhattan Distance", success_prob=0.8, seed=1, **search_kw),
    ]

    for call in calls:
        result = call()
        assert result.algorithm

    min_conflicts_result = min_conflicts(
        start=(1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 0, 15),
        goal=GOAL_STATE,
        timeout=1.0,
        max_iterations=50,
        seed=1,
    )
    assert not min_conflicts_result.success
    assert "not a 15-puzzle solution" in min_conflicts_result.message

    planning_result = backtracking_search(
        start=(1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 0, 15),
        goal=GOAL_STATE,
        timeout=1.0,
        max_steps=50,
    )
    assert planning_result.success and planning_result.path_verified
    assert not planning_result.is_optimal
    assert "not MRV/forward checking" in planning_result.message

    custom_goal = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 0, 15)
    custom_planning_result = backtracking_search(
        start=GOAL_STATE,
        goal=custom_goal,
        timeout=1.0,
        max_steps=50,
    )
    assert custom_planning_result.success
    assert custom_planning_result.actions == ["L"]
    assert custom_planning_result.path[-1] == custom_goal
    assert custom_planning_result.path_verified


def test_run_algorithm_dispatch_strips_unsupported_csp_kwargs():
    from core.puzzle import GOAL_STATE
    from core.solver_dispatch import build_solver_kwargs

    base = dict(
        start=GOAL_STATE,
        goal=GOAL_STATE,
        timeout=1.0,
        action_order="LRUD",
        max_nodes=50,
        max_depth=4,
        heuristic="Manhattan Distance",
    )

    csp_definition_kwargs = build_solver_kwargs("csp_definition", **base)
    assert "timeout" not in csp_definition_kwargs
    assert "action_order" not in csp_definition_kwargs
    assert csp_definition_kwargs["time_horizon"] == 4

    csp_graph_kwargs = build_solver_kwargs("solve_csp_constraint_graphs", **base)
    assert csp_graph_kwargs["time_horizon"] == 3

    backtracking_kwargs = build_solver_kwargs("backtracking_search", **base)
    assert backtracking_kwargs["timeout"] == 1.0
    assert "action_order" not in backtracking_kwargs
    assert backtracking_kwargs["max_steps"] == 50

    a_star_kwargs = build_solver_kwargs("a_star", tie_breaker="Min-g", **base)
    assert a_star_kwargs["action_order"] == "LRUD"
    assert a_star_kwargs["heuristic"] == "Manhattan Distance"
    assert a_star_kwargs["tie_breaker"] == "Min-g"


def test_run_completion_notice_does_not_overstate_model_success():
    from core.metrics import SearchResult
    from core.puzzle import GOAL_STATE
    from ui.run_tab import run_completion_notice

    solved = SearchResult(
        success=True,
        algorithm="A*",
        path=[GOAL_STATE],
        actions=[],
        goal_state=GOAL_STATE,
    )
    model_only = SearchResult(
        success=True,
        algorithm="CSP Definition",
        message="CSP variables and constraints described.",
    )
    failed = SearchResult(success=False, algorithm="BFS", message="Node limit reached")

    assert run_completion_notice("A*", solved) == ("success", "A* found a solution!")
    model_level, model_text = run_completion_notice("CSP Definition", model_only)
    assert model_level == "info"
    assert "did not certify a standard path" in model_text
    assert run_completion_notice("BFS", failed) == ("warning", "BFS: Node limit reached")


def test_run_solver_solvability_guard_is_relative_to_goal():
    from core.metrics import SearchResult
    from core.puzzle import GOAL_STATE
    from core.utils import run_solver

    swapped_goal = (2, 1, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 0)

    def echo_solver(start, goal, timeout=1.0):
        return SearchResult(success=True, algorithm="Echo", path=[start], actions=[])

    blocked = run_solver(echo_solver, GOAL_STATE, goal=swapped_goal, timeout=1)
    allowed = run_solver(echo_solver, swapped_goal, goal=swapped_goal, timeout=1)

    assert not blocked.success
    assert "not solvable" in blocked.message
    assert allowed.success

