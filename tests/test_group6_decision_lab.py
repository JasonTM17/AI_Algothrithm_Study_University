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
from core.puzzle import GOAL_STATE, _move_blank, scramble


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
