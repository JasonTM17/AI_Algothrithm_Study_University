"""Contracts for the role-based Group 6 Play lab."""

from __future__ import annotations

import json
from collections import defaultdict

from core.group6_decision_lab import (
    GROUP6_LAB_ALGORITHMS,
    Group6LabSettings,
    compare_minimax_alpha_beta,
    run_group6_algorithm,
)
from core.group6_variant_labs import (
    ROBUSTNESS_ALGORITHMS,
    Group6ChanceSettings,
    Group6RobustnessSettings,
    advance_chance_lab,
    advance_robustness_game,
    chance_outcome_distribution,
    create_chance_lab,
    create_robustness_game,
    run_chance_stability_sample,
)
from core.puzzle import DEFAULT_START_STATE, GOAL_STATE, _move_blank, scramble


START = scramble(GOAL_STATE, 4, seed=9)


def test_group6_registry_has_only_the_three_decision_models():
    assert GROUP6_LAB_ALGORITHMS == (
        "Minimax",
        "Alpha-Beta Pruning",
        "Expectimax",
    )


def test_minimax_and_alpha_beta_preserve_root_value_and_legal_variation():
    settings = Group6LabSettings(depth=3, timeout=10.0, action_order="LRUD")
    minimax_result = run_group6_algorithm(
        "Minimax", start=START, goal=GOAL_STATE, settings=settings
    )
    alpha_beta_result = run_group6_algorithm(
        "Alpha-Beta Pruning",
        start=START,
        goal=GOAL_STATE,
        settings=settings,
    )

    assert compare_minimax_alpha_beta(minimax_result, alpha_beta_result) is True
    assert alpha_beta_result.result.nodes_expanded <= minimax_result.result.nodes_expanded
    assert alpha_beta_result.result.termination_reason != "timeout"
    assert alpha_beta_result.prune_count == sum(
        step.event == "prune" for step in alpha_beta_result.result.trace
    )
    for lab_result in (minimax_result, alpha_beta_result):
        assert lab_result.result.path_verified
        assert [frame.role for frame in lab_result.frames] == ["MAX", "MIN", "MAX"]
        for frame in lab_result.frames:
            assert _move_blank(frame.before_state, frame.action) == frame.after_state


def test_expectimax_probability_groups_are_normalized_and_seeded_replay_is_stable():
    settings = Group6LabSettings(
        depth=3,
        timeout=10.0,
        success_probability=0.65,
        seed=123,
    )
    first = run_group6_algorithm(
        "Expectimax", start=START, goal=GOAL_STATE, settings=settings
    )
    second = run_group6_algorithm(
        "Expectimax", start=START, goal=GOAL_STATE, settings=settings
    )

    assert first.result.path == second.result.path
    assert first.frames == second.frames
    assert all(frame.role == "CHANCE" for frame in first.frames)
    assert all(frame.intended_action and frame.realized_action for frame in first.frames)

    grouped_probabilities: dict[str, float] = defaultdict(float)
    for step in first.result.trace:
        if step.event == "chance_outcome_evaluated":
            grouped_probabilities[str(step.node_id)] += float(step.probability)
    assert grouped_probabilities
    assert all(abs(total - 1.0) < 1e-9 for total in grouped_probabilities.values())


def test_group6_export_is_json_safe_and_contains_no_image_payload():
    result = run_group6_algorithm(
        "Minimax",
        start=START,
        goal=GOAL_STATE,
        settings=Group6LabSettings(depth=2, timeout=10.0),
    )
    encoded = json.dumps(result.export_summary())

    assert result.run_fingerprint
    assert result.baseline_fingerprint
    assert "image" not in encoded.lower()
    assert "base64" not in encoded.lower()
    assert result.export_summary()["space_proxy"]["generated_nodes"] >= 1


def test_group6_fingerprint_changes_with_model_settings_but_not_algorithm_pairing():
    base = Group6LabSettings(depth=2, timeout=10.0)
    minimax_result = run_group6_algorithm(
        "Minimax", start=START, goal=GOAL_STATE, settings=base
    )
    alpha_beta_result = run_group6_algorithm(
        "Alpha-Beta Pruning", start=START, goal=GOAL_STATE, settings=base
    )
    deeper = run_group6_algorithm(
        "Minimax",
        start=START,
        goal=GOAL_STATE,
        settings=Group6LabSettings(depth=3, timeout=10.0),
    )

    assert minimax_result.baseline_fingerprint == alpha_beta_result.baseline_fingerprint
    assert minimax_result.run_fingerprint != alpha_beta_result.run_fingerprint
    assert minimax_result.baseline_fingerprint != deeper.baseline_fingerprint
    assert compare_minimax_alpha_beta(deeper, alpha_beta_result) is None


def test_robustness_game_alternates_max_min_and_uses_legal_moves():
    settings = Group6RobustnessSettings(
        algorithm="Minimax",
        depth=2,
        per_turn_timeout=10.0,
        max_turns=4,
    )
    game = create_robustness_game(start=START, goal=GOAL_STATE, settings=settings)

    advance_robustness_game(game)
    advance_robustness_game(game)

    assert [frame.role for frame in game.frames[:2]] == ["MAX", "MIN"]
    for frame in game.frames:
        assert _move_blank(frame.before_state, frame.realized_action) == frame.after_state
        assert frame.mode == "robustness_game_variant"
    assert "image" not in json.dumps(game.export_summary()).lower()
    assert "base64" not in json.dumps(game.export_summary()).lower()


def test_robustness_game_avoids_immediate_cycle_when_unvisited_move_exists():
    for algorithm in ROBUSTNESS_ALGORITHMS:
        game = create_robustness_game(
            start=DEFAULT_START_STATE,
            goal=GOAL_STATE,
            settings=Group6RobustnessSettings(algorithm=algorithm),
        )

        advance_robustness_game(game)
        advance_robustness_game(game)

        assert len(game.frames) == 2
        assert game.status == "running"
        assert not game.frames[-1].repeated_state
        assert game.frames[-1].intended_action == "R"
        assert game.frames[-1].realized_action != "R"
        assert len(game.history) == len(set(game.history))


def test_robustness_game_rejects_expectimax():
    settings = Group6RobustnessSettings(algorithm="Expectimax")
    try:
        create_robustness_game(start=START, goal=GOAL_STATE, settings=settings)
    except ValueError as exc:
        assert "Minimax" in str(exc)
    else:
        raise AssertionError("Expectimax must not be accepted in robustness mode")


def test_chance_outcome_distribution_is_normalized_and_legal():
    intended = next(action for action in "LRUD" if _move_blank(START, action) is not None)
    outcomes = chance_outcome_distribution(
        START,
        intended,
        success_probability=0.7,
        action_order="LRUD",
    )

    assert outcomes
    assert abs(sum(probability for _, _, probability in outcomes) - 1.0) < 1e-9
    for action, state, _ in outcomes:
        assert _move_blank(START, action) == state


def test_chance_lab_fixed_seed_is_stable_and_records_expected_value():
    settings = Group6ChanceSettings(
        depth=2,
        per_turn_timeout=10.0,
        max_turns=3,
        success_probability=0.65,
        seed=77,
    )
    first = create_chance_lab(start=START, goal=GOAL_STATE, settings=settings)
    second = create_chance_lab(start=START, goal=GOAL_STATE, settings=settings)
    for _ in range(3):
        advance_chance_lab(first)
        advance_chance_lab(second)

    assert first.history == second.history
    assert [frame.realized_action for frame in first.frames] == [
        frame.realized_action for frame in second.frames
    ]
    assert all(frame.role == "CHANCE" for frame in first.frames)
    assert all(frame.expected_utility is not None for frame in first.frames)


def test_chance_stability_stats_and_export_contract():
    settings = Group6ChanceSettings(
        depth=1,
        per_turn_timeout=10.0,
        max_turns=2,
        sample_count=3,
        seed=5,
    )
    sample = run_chance_stability_sample(start=START, goal=GOAL_STATE, settings=settings)
    assert len(sample["rows"]) == 3
    assert sample["stats"]["min_runtime"] <= sample["stats"]["mean_runtime"]
    assert sample["stats"]["goal_reached_count"] >= 0

    lab = create_chance_lab(start=START, goal=GOAL_STATE, settings=settings)
    advance_chance_lab(lab)
    encoded = json.dumps(lab.export_summary()).lower()
    assert "image" not in encoded
    assert "base64" not in encoded
