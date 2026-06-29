from core.metrics import SearchResult
from core.puzzle import GOAL_STATE
from ui.image_algorithm_race import classify_race_results, race_chart_rows, state_at_step


ONE_MOVE = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 0, 15)


def _solved(name: str, runtime: float) -> SearchResult:
    return SearchResult(
        success=True,
        algorithm=name,
        group="Informed Search",
        path=[ONE_MOVE, GOAL_STATE],
        actions=["R"],
        goal_state=GOAL_STATE,
        runtime=runtime,
        message="Solution found",
    )


def test_race_rankings_only_include_verified_goal_paths():
    solved = _solved("A*", 0.01)
    partial = SearchResult(
        success=False,
        algorithm="Simulated Annealing",
        group="Local Search",
        path=[ONE_MOVE],
        actions=[],
        goal_state=GOAL_STATE,
        runtime=0.02,
        message="Max iterations reached",
    )
    unavailable = SearchResult(
        success=False,
        algorithm="AND-OR Search",
        group="Complex Environments",
        termination_reason="not_applicable",
        message="Conditional plan is not a linear path benchmark.",
    )

    groups = classify_race_results([solved, partial, unavailable])
    rows = race_chart_rows([solved, partial, unavailable])

    assert groups.solved == (solved,)
    assert groups.partial == (partial,)
    assert groups.unavailable == (unavailable,)
    assert rows == [{"Algorithm": "A*", "Runtime (s)": 0.01, "Steps": 1}]


def test_shared_step_caps_shorter_trajectory_at_final_state():
    solved = _solved("BFS", 0.02)

    assert state_at_step(solved, 0) == ONE_MOVE
    assert state_at_step(solved, 99) == GOAL_STATE
