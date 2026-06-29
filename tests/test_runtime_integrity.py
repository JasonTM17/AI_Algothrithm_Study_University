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
    assert "def render_puzzle_with_image" not in components_source
    assert "play-board-anchor" in components_source
    assert "search_tree_to_dot" in components_source
    assert 't("search_tree_caption")' in components_source
    assert "hand_trace_tree_dot" in hand_tracing_source
    assert "st.graphviz_chart" in hand_tracing_source
    assert "Compatibility for tree display" not in hand_tracing_source


def test_result_message_is_escaped_before_html_render():
    components_source = (ROOT / "ui" / "components.py").read_text(encoding="utf-8")

    assert "summary = result_message_summary(message)" in components_source
    assert "safe_message = escape(summary)" in components_source
    assert "{result.message}</div>" not in components_source


def test_result_message_summary_keeps_structured_plan_out_of_status_card():
    from ui.components import result_message_summary

    message = (
        "Conditional plan found (depth limit=20).\n"
        "OR: choose action U (h=10.0)\n"
        "  IF intended (action=U):\n"
        "    GOAL reached"
    )

    assert result_message_summary(message) == "Conditional plan found (depth limit=20)."
    assert "OR: choose action" not in result_message_summary(message)


def test_search_tree_readable_view_has_legend_and_filters():
    components_source = (ROOT / "ui" / "components.py").read_text(encoding="utf-8")

    assert "search-tree-legend" in components_source
    assert "search_tree_view_label" in components_source
    assert "search_tree_view_neighborhood" in components_source
    assert "search_tree_graphviz_evidence" in components_source


def test_streamlit_theme_uses_public_keys_only():
    config = (ROOT / ".streamlit" / "config.toml").read_text(encoding="utf-8")

    assert 'primaryColor = "#7AA66A"' in config
    assert 'secondaryBackgroundColor = "#18201A"' in config
    assert 'textColor = "#F4F1E8"' in config
    assert 'borderColor = "#4B5A4D"' in config
    assert "showWidgetBorder = true" in config
    assert "[theme.sidebar]" not in config
    assert "widgetBackgroundColor" not in config
    assert "widgetBorderColor" not in config
    assert "skeletonBackgroundColor" not in config


def test_streamlit_version_includes_sidebar_theme_fix():
    requirements = (ROOT / "requirements.txt").read_text(encoding="utf-8")

    assert "streamlit==1.58.0" in requirements


def test_advanced_mode_function_kwargs_match_app_dispatch():
    from algorithms.adversarial import alpha_beta_pruning, expectimax, minimax
    from algorithms.complex_env import (
        and_or_search,
        no_observation_search,
        partially_observable_search,
    )
    from algorithms.csp import (
        backtracking_forward_checking,
        backtracking_search,
        constraint_propagation,
        min_conflicts,
    )
    from core.puzzle import GOAL_STATE

    base_kw = dict(start=GOAL_STATE, goal=GOAL_STATE)
    csp_search_kw = dict(**base_kw, timeout=1.0)
    search_kw = dict(**base_kw, timeout=1.0, action_order="LRUD")

    calls = [
        lambda: constraint_propagation(time_horizon=1, **csp_search_kw),
        lambda: backtracking_search(time_horizon=1, **csp_search_kw, max_steps=10),
        lambda: backtracking_forward_checking(time_horizon=1, **csp_search_kw, max_steps=10),
        lambda: min_conflicts(time_horizon=1, **csp_search_kw, max_iterations=10, seed=1),
        lambda: and_or_search(max_depth=1, nondet_prob=0.2, seed=1, **search_kw),
        lambda: no_observation_search(num_belief_states=2, max_steps=1, seed=1, **search_kw),
        lambda: partially_observable_search(num_belief_states=2, max_steps=1, seed=1, **search_kw),
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
        time_horizon=1,
        max_iterations=50,
        seed=1,
    )
    assert min_conflicts_result.success
    assert min_conflicts_result.path_verified

    planning_result = backtracking_search(
        start=(1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 0, 15),
        goal=GOAL_STATE,
        timeout=1.0,
        time_horizon=1,
        max_steps=50,
    )
    assert planning_result.success and planning_result.path_verified
    assert not planning_result.is_optimal
    assert "exact-horizon CSP assignment" in planning_result.message

    custom_goal = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 0, 15)
    custom_planning_result = backtracking_search(
        start=GOAL_STATE,
        goal=custom_goal,
        timeout=1.0,
        time_horizon=1,
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

    backtracking_kwargs = build_solver_kwargs("backtracking_search", **base)
    assert backtracking_kwargs["timeout"] == 1.0
    assert backtracking_kwargs["action_order"] == "LRUD"
    assert backtracking_kwargs["time_horizon"] == 4
    assert backtracking_kwargs["max_steps"] == 50

    ac3_kwargs = build_solver_kwargs("constraint_propagation", **base)
    assert ac3_kwargs["time_horizon"] == 4
    assert ac3_kwargs["candidate_limit"] == 50

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

    conditional_plan = SearchResult(
        success=True,
        algorithm="AND-OR Search",
        capability="conditional_plan",
        message=(
            "Conditional plan found (depth limit=20).\n"
            "OR: choose action U (h=10.0)\n"
            "  IF intended (action=U): GOAL reached"
        ),
    )
    notice_level, notice_text = run_completion_notice("AND-OR Search", conditional_plan)
    assert notice_level == "info"
    assert "Conditional plan found" in notice_text
    assert "OR: choose action" not in notice_text


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


def test_run_solver_preserves_zero_runtime_and_reports_goal():
    from core.metrics import SearchResult
    from core.puzzle import GOAL_STATE
    from core.utils import run_solver

    def instant_solver(start, goal, timeout=1.0):
        return SearchResult(
            success=True,
            algorithm="Instant",
            path=[start],
            actions=[],
            runtime=0.0,
        )

    result = run_solver(instant_solver, GOAL_STATE, timeout=1.0)

    assert result.runtime == 0.0
    assert result.goal_state == GOAL_STATE
    assert result.path_verified
    assert result.goal_reached


def test_run_solver_error_results_report_requested_goal():
    from core.puzzle import GOAL_STATE
    from core.utils import run_solver

    custom_goal = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 0, 15)

    def failing_solver(start, goal, timeout=1.0):
        raise TimeoutError

    result = run_solver(failing_solver, custom_goal, goal=custom_goal, timeout=1.0)

    assert not result.success
    assert result.goal_state == custom_goal
    assert result.termination_reason == "timeout"


def test_app_image_sample_selection_updates_immediately():
    app_source = (ROOT / "app.py").read_text(encoding="utf-8")

    assert "_activate_selected_sample_image" in app_source
    assert "on_change=_activate_selected_sample_image" in app_source
    assert 'if __name__ == "__main__"' not in app_source
    assert "btn_load_sample" not in app_source

