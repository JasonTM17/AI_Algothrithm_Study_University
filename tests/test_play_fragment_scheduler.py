"""Regression tests for the shared Play fragment scheduler."""

import pytest

import ui.play_tab as play_tab


ACTIVE_FLAG_CASES = (
    ("play_auto_run", "play"),
    ("group6_lab_auto", "lab"),
    ("group6_sweep_active", "lab"),
    ("group6_policy_auto", "policy"),
    ("group6_robustness_auto", "variant"),
    ("group6_chance_auto", "variant"),
)


def _patch_tick_dependencies(monkeypatch, session_state, *, stop_source=None):
    monkeypatch.setattr(play_tab.st, "session_state", session_state)
    monkeypatch.setattr(
        play_tab,
        "group6_lab_needs_tick",
        lambda: bool(
            session_state.get("group6_lab_auto")
            or session_state.get("group6_sweep_active")
        ),
    )
    monkeypatch.setattr(
        play_tab,
        "group6_policy_needs_tick",
        lambda: bool(session_state.get("group6_policy_auto")),
    )
    monkeypatch.setattr(
        play_tab,
        "group6_variant_needs_tick",
        lambda: bool(
            session_state.get("group6_robustness_auto")
            or session_state.get("group6_chance_auto")
        ),
    )

    def stop_play():
        if stop_source == "play":
            session_state["play_auto_run"] = False

    def stop_lab():
        if stop_source == "lab":
            session_state["group6_lab_auto"] = False
            session_state["group6_sweep_active"] = False

    def stop_policy():
        if stop_source == "policy":
            session_state["group6_policy_auto"] = False

    def stop_variant():
        if stop_source == "variant":
            session_state["group6_robustness_auto"] = False
            session_state["group6_chance_auto"] = False

    monkeypatch.setattr(play_tab, "_advance_auto_replay_one_step", stop_play)
    monkeypatch.setattr(play_tab, "advance_group6_lab_tick", stop_lab)
    monkeypatch.setattr(play_tab, "advance_group6_policy_tick", stop_policy)
    monkeypatch.setattr(play_tab, "advance_group6_variant_tick", stop_variant)


@pytest.mark.parametrize(("active_flag", "stop_source"), ACTIVE_FLAG_CASES)
def test_final_tick_requests_scheduler_shutdown(monkeypatch, active_flag, stop_source):
    session_state = {active_flag: True}
    _patch_tick_dependencies(
        monkeypatch,
        session_state,
        stop_source=stop_source,
    )

    assert play_tab._advance_play_workbench_tick() is True
    assert play_tab._play_workbench_needs_tick() is False


def test_scheduler_keeps_running_while_another_workflow_is_active(monkeypatch):
    session_state = {
        "play_auto_run": True,
        "group6_policy_auto": True,
    }
    _patch_tick_dependencies(monkeypatch, session_state, stop_source="play")

    assert play_tab._advance_play_workbench_tick() is False
    assert play_tab._play_workbench_needs_tick() is True


def test_idle_workbench_does_not_request_shutdown_rerun(monkeypatch):
    session_state = {}
    _patch_tick_dependencies(monkeypatch, session_state)

    assert play_tab._advance_play_workbench_tick() is False
    assert play_tab._play_workbench_needs_tick() is False
