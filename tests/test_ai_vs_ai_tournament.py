"""Tests for AI-vs-AI 15-puzzle tournament scoring."""

import pytest

from core.ai_vs_ai_tournament import (
    AgentRoundScore,
    TournamentAgentConfig,
    TournamentRoundResult,
    TournamentResult,
    run_ai_vs_ai_tournament,
    score_search_result,
)
from core.metrics import SearchResult
from core.puzzle import GOAL_STATE
from ui.ai_vs_ai_tournament import _score_row


ONE_MOVE = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 0, 15)


def test_score_optimal_solution_gets_full_points():
    result = SearchResult(
        success=True,
        algorithm="A*",
        path=[ONE_MOVE, GOAL_STATE],
        actions=["R"],
        goal_state=GOAL_STATE,
        cost=1,
    )

    score = score_search_result(result, agent_label="AI A", algorithm="a_star", optimal_cost=1)

    assert score.points == 100
    assert score.status == "optimal"


def test_score_suboptimal_solution_gets_reduced_positive_points():
    detour = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 0, 14, 15)
    result = SearchResult(
        success=True,
        algorithm="DFS",
        path=[ONE_MOVE, detour, ONE_MOVE, GOAL_STATE],
        actions=["L", "R", "R"],
        goal_state=GOAL_STATE,
        cost=3,
    )

    score = score_search_result(result, agent_label="AI B", algorithm="dfs", optimal_cost=1)

    assert score.points == 33
    assert score.status == "suboptimal"
    assert score.excess_cost == 2
    assert score.efficiency_percent == pytest.approx(100 / 3)
    assert score.path == result.path
    assert score.actions == result.actions
    assert score.path_verified
    assert score.goal_reached


def test_score_legal_partial_path_gets_small_penalty():
    result = SearchResult(
        success=False,
        algorithm="Simple Hill Climbing",
        path=[ONE_MOVE],
        actions=[],
        goal_state=GOAL_STATE,
        message="Stuck",
    )

    score = score_search_result(result, agent_label="AI A", algorithm="simple_hill_climbing", optimal_cost=1)

    assert score.points == -10
    assert score.status == "partial_path"


def test_score_timeout_without_path_gets_failure_penalty():
    result = SearchResult(
        success=False,
        algorithm="BFS",
        goal_state=GOAL_STATE,
        message="Timeout",
    )

    score = score_search_result(result, agent_label="AI A", algorithm="bfs", optimal_cost=1)

    assert score.points == -20
    assert score.status == "timeout"


def test_tournament_score_row_keeps_optional_numeric_fields_text_stable():
    score = AgentRoundScore(
        agent_label="AI A",
        algorithm="bfs",
        points=-20,
        status="timeout",
        reason="Timeout",
        random_seed=123,
    )

    row = _score_row(score)

    values = list(row.values())
    assert values.count("-") >= 4
    assert "123" in values


def test_score_invalid_path_gets_hard_penalty():
    result = SearchResult(
        success=True,
        algorithm="Broken",
        path=[ONE_MOVE, GOAL_STATE],
        actions=["L"],
        goal_state=GOAL_STATE,
    )

    score = score_search_result(result, agent_label="AI A", algorithm="broken", optimal_cost=1)

    assert score.points == -50
    assert score.status == "invalid_path"


def test_tournament_runs_two_agents_on_same_round_with_reference_cost():
    result = run_ai_vs_ai_tournament(
        TournamentAgentConfig("AI A", "a_star"),
        TournamentAgentConfig("AI B", "greedy_best_first"),
        start=ONE_MOVE,
        goal=GOAL_STATE,
        rounds=1,
        timeout=5,
        max_nodes=1000,
    )

    assert result.rounds[0].optimal_cost == 1
    assert result.rounds[0].agent_a.optimal_cost == 1
    assert result.rounds[0].agent_b.optimal_cost == 1
    assert result.rounds[0].agent_a.path == [ONE_MOVE, GOAL_STATE]
    assert result.rounds[0].agent_a.actions == ["R"]
    assert result.winner in {"AI A", "AI B", "Draw"}


def test_tournament_tie_break_is_deterministic():
    result = TournamentResult(
        agent_a_label="AI A",
        agent_b_label="AI B",
        agent_a_total=0,
        agent_b_total=0,
    )

    from core.ai_vs_ai_tournament import _classify_tournament

    _classify_tournament(result)

    assert result.winner == "Draw"
    assert "equal" in result.tie_break_detail


def test_identical_solution_quality_draws_despite_runtime_noise():
    result = TournamentResult(
        agent_a_label="AI A",
        agent_b_label="AI B",
        agent_a_total=100,
        agent_b_total=100,
        rounds=[
            TournamentRoundResult(
                round_number=1,
                start_state=ONE_MOVE,
                goal_state=GOAL_STATE,
                optimal_cost=1,
                reference_status="A* reference proven at cost 1.",
                agent_a=AgentRoundScore(
                    "AI A", "A*", 100, "optimal", "Solved",
                    cost=1, optimal_cost=1, excess_cost=0, runtime=0.1, nodes=4,
                ),
                agent_b=AgentRoundScore(
                    "AI B", "A*", 100, "optimal", "Solved",
                    cost=1, optimal_cost=1, excess_cost=0, runtime=0.001, nodes=4,
                ),
            ),
        ],
    )

    from core.ai_vs_ai_tournament import _classify_tournament

    _classify_tournament(result)

    assert result.winner == "Draw"
    assert "runtime" in result.tie_break_detail


def test_same_deterministic_agents_draw_on_same_round():
    result = run_ai_vs_ai_tournament(
        TournamentAgentConfig("AI A", "a_star"),
        TournamentAgentConfig("AI B", "a_star"),
        start=ONE_MOVE,
        rounds=1,
        timeout=5,
        max_nodes=1000,
    )

    assert result.agent_a_total == result.agent_b_total == 100
    assert result.winner == "Draw"
