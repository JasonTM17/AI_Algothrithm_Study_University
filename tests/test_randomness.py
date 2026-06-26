"""Tests for reproducible-vs-fresh run variation policy."""

from core.metrics import SearchResult
from core.randomness import (
    activate_run_variation,
    active_action_order,
    apply_run_variation,
    is_randomized_solver,
    make_run_variation,
    resolve_run_seed,
)


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


def test_run_variation_gives_deterministic_solvers_a_recorded_seed(monkeypatch):
    monkeypatch.setattr("core.randomness.secrets.randbits", lambda _: 12345)

    variation = make_run_variation("a_star", previous_seed=7)
    result = SearchResult(algorithm="A*")
    apply_run_variation(result, variation)

    assert result.random_seed == 12345
    assert sorted(result.variation_action_order) == ["D", "L", "R", "U"]
    assert result.variation_tie_breaker in {"FIFO", "LIFO", "Min-g", "Max-g"}
    assert result.variation_solver_seed is None
    assert result.variation_randomizes_path


def test_run_variation_avoids_immediate_seed_and_order_repeat(monkeypatch):
    monkeypatch.setattr("core.randomness.secrets.randbits", lambda _: 99)

    previous = make_run_variation("bfs")
    current = make_run_variation(
        "bfs",
        previous_seed=previous.seed,
        previous_action_order=previous.action_order,
    )

    assert current.seed != previous.seed
    assert current.action_order != previous.action_order
    assert sorted(current.action_order) == ["D", "L", "R", "U"]


def test_non_path_models_record_variation_without_claiming_path_randomness(monkeypatch):
    monkeypatch.setattr("core.randomness.secrets.randbits", lambda _: 77)

    variation = make_run_variation("csp_definition")
    and_or_variation = make_run_variation("and_or_search")

    assert variation.seed == 77
    assert sorted(variation.action_order) == ["D", "L", "R", "U"]
    assert not variation.randomizes_path
    assert and_or_variation.seed == 77
    assert sorted(and_or_variation.action_order) == ["D", "L", "R", "U"]
    assert not and_or_variation.randomizes_path


def test_ac3_constraint_propagation_can_randomize_a_legal_path(monkeypatch):
    monkeypatch.setattr("core.randomness.secrets.randbits", lambda _: 78)

    variation = make_run_variation("constraint_propagation")

    assert variation.seed == 78
    assert sorted(variation.action_order) == ["D", "L", "R", "U"]
    assert variation.randomizes_path
    assert variation.solver_seed is None


def test_run_variation_action_order_is_scoped_and_restored(monkeypatch):
    monkeypatch.setattr("core.randomness.secrets.randbits", lambda _: 123)
    variation = make_run_variation("backtracking_search")

    assert active_action_order() == "LRUD"
    with activate_run_variation(variation):
        assert active_action_order() == variation.action_order
    assert active_action_order() == "LRUD"
