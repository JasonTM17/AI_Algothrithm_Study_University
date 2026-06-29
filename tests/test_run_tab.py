"""Focused tests for Run-tab state callbacks."""

import ui.run_tab as run_tab


def test_belief_demo_callback_sets_rendered_widget_state_directly(monkeypatch):
    session_state = {}
    monkeypatch.setattr(run_tab.st, "session_state", session_state)
    monkeypatch.setattr(
        run_tab,
        "apply_goal_state",
        lambda state: session_state.update(goal_state=tuple(state)),
    )
    monkeypatch.setattr(
        run_tab,
        "apply_start_state",
        lambda state: session_state.update(start_state=tuple(state)),
    )

    run_tab._apply_belief_success_demo("no_observation_search")

    assert session_state["no_observation_search_belief_size"] == 1
    assert "no_observation_search_belief_size_default" not in session_state
    assert session_state["run_forced_action_order"] == "DRUL"
    assert session_state["run_forced_action_order_for"] == "no_observation_search"


def test_belief_size_seed_preserves_callback_value(monkeypatch):
    session_state = {"no_observation_search_belief_size": 1}
    monkeypatch.setattr(run_tab.st, "session_state", session_state)

    run_tab._seed_belief_size_state("no_observation_search_belief_size")

    assert session_state["no_observation_search_belief_size"] == 1


def test_belief_size_seed_installs_default_only_when_missing(monkeypatch):
    session_state = {}
    monkeypatch.setattr(run_tab.st, "session_state", session_state)

    run_tab._seed_belief_size_state("partially_observable_search_belief_size")

    assert session_state["partially_observable_search_belief_size"] == 5


def test_forced_action_order_is_scoped_to_demo_algorithm(monkeypatch):
    session_state = {
        "run_forced_action_order": "DRUL",
        "run_forced_action_order_for": "no_observation_search",
    }
    monkeypatch.setattr(run_tab.st, "session_state", session_state)

    assert run_tab._consume_forced_action_order("bfs") is None
    assert "run_forced_action_order" not in session_state
    assert "run_forced_action_order_for" not in session_state


def test_forced_action_order_applies_to_matching_demo_algorithm(monkeypatch):
    session_state = {
        "run_forced_action_order": "DRUL",
        "run_forced_action_order_for": "partially_observable_search",
    }
    monkeypatch.setattr(run_tab.st, "session_state", session_state)

    assert run_tab._consume_forced_action_order("partially_observable_search") == "DRUL"
    assert "run_forced_action_order" not in session_state
    assert "run_forced_action_order_for" not in session_state
