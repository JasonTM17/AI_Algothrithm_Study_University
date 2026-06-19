"""Tests for reproducible-vs-fresh stochastic run policy."""

from core.randomness import is_randomized_solver, resolve_run_seed


def test_only_stochastic_implementations_receive_random_seeds():
    assert is_randomized_solver("stochastic_hill_climbing")
    assert is_randomized_solver("expectimax")
    assert is_randomized_solver("no_observation_search")
    assert is_randomized_solver("partially_observable_search")
    assert not is_randomized_solver("and_or_search")
    assert not is_randomized_solver("a_star")
    assert not is_randomized_solver("bfs")


def test_deterministic_solver_never_receives_seed():
    assert resolve_run_seed(
        "a_star",
        fresh_each_run=True,
        manual_seed=42,
        previous_seed=7,
    ) is None

    assert resolve_run_seed(
        "and_or_search",
        fresh_each_run=True,
        manual_seed=42,
        previous_seed=7,
    ) is None


def test_fixed_seed_mode_is_reproducible():
    assert resolve_run_seed(
        "simulated_annealing",
        fresh_each_run=False,
        manual_seed=1234,
    ) == 1234


def test_fresh_seed_never_repeats_previous_seed(monkeypatch):
    monkeypatch.setattr("core.randomness.secrets.randbits", lambda _: 99)

    assert resolve_run_seed(
        "expectimax",
        fresh_each_run=True,
        manual_seed=42,
        previous_seed=99,
    ) == 100
