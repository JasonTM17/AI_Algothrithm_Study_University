"""Shared bounded state-chain model for the CSP teaching algorithms."""

from __future__ import annotations

from dataclasses import dataclass
import time

from core.puzzle import PuzzleState


State = tuple[int, ...]


class CSPModelLimit(RuntimeError):
    """Raised when the bounded CSP universe exceeds its safety contract."""


@dataclass(frozen=True)
class StateChainCSP:
    """Variables S[0]..S[T] with legal-move constraints between neighbors."""

    start: State
    goal: State
    horizon: int
    action_order: str
    domains: tuple[frozenset[State], ...]
    neighbors: dict[State, tuple[tuple[State, str], ...]]
    candidate_states: int

    def compatible(self, left: State, right: State) -> bool:
        return any(candidate == right for candidate, _ in self.neighbors.get(left, ()))

    def action_between(self, left: State, right: State) -> str | None:
        for candidate, action in self.neighbors.get(left, ()):
            if candidate == right:
                return action
        return None

    def verify_assignment(
        self,
        assignment: list[State] | tuple[State, ...],
    ) -> tuple[list[State], list[str]]:
        if len(assignment) != self.horizon + 1:
            return [], []
        if assignment[0] != self.start or assignment[-1] != self.goal:
            return [], []
        actions: list[str] = []
        for left, right in zip(assignment, assignment[1:]):
            action = self.action_between(left, right)
            if action is None:
                return [], []
            actions.append(action)
        return list(assignment), actions


def _next_layer(
    states: set[State],
    action_order: str,
) -> set[State]:
    return {
        neighbor
        for state in states
        for neighbor, _, _ in PuzzleState(state).get_neighbors(action_order)
    }


def build_state_chain_csp(
    start: State,
    goal: State,
    *,
    horizon: int,
    action_order: str = "LRUD",
    candidate_limit: int = 20_000,
    timeout: float = 5.0,
) -> StateChainCSP:
    """Build exact-step domains from forward and backward reachability layers."""
    if horizon < 0:
        raise ValueError("horizon must be non-negative")
    if candidate_limit < 1:
        raise ValueError("candidate_limit must be positive")
    if timeout <= 0:
        raise ValueError("timeout must be positive")

    started = time.perf_counter()
    forward: list[set[State]] = [{tuple(start)}]
    backward_reversed: list[set[State]] = [{tuple(goal)}]
    universe = {tuple(start), tuple(goal)}

    for _ in range(horizon):
        if time.perf_counter() - started >= timeout:
            raise CSPModelLimit("Timed out while building the bounded CSP domains")
        forward.append(_next_layer(forward[-1], action_order))
        backward_reversed.append(_next_layer(backward_reversed[-1], action_order))
        universe.update(forward[-1])
        universe.update(backward_reversed[-1])
        if len(universe) > candidate_limit:
            raise CSPModelLimit(
                f"Candidate state limit exceeded ({candidate_limit})"
            )

    backward = list(reversed(backward_reversed))
    domains = [
        frozenset(forward[index] & backward[index])
        for index in range(horizon + 1)
    ]
    if domains:
        domains[0] = frozenset({tuple(start)}) if tuple(start) in domains[0] else frozenset()
        domains[-1] = frozenset({tuple(goal)}) if tuple(goal) in domains[-1] else frozenset()

    relevant_states = set().union(*domains) if domains else set()
    neighbors = {
        state: tuple(
            (neighbor, action)
            for neighbor, action, _ in PuzzleState(state).get_neighbors(action_order)
            if neighbor in relevant_states
        )
        for state in relevant_states
    }
    return StateChainCSP(
        start=tuple(start),
        goal=tuple(goal),
        horizon=horizon,
        action_order=action_order,
        domains=tuple(domains),
        neighbors=neighbors,
        candidate_states=len(universe),
    )

