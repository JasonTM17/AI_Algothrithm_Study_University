"""Executable AC-3 propagation for a bounded 15-puzzle state-chain CSP."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass

from core.puzzle import PuzzleState


State = tuple[int, ...]


@dataclass
class AC3StateChainResult:
    """Propagation evidence for variables S[0]..S[T]."""

    domains: list[set[State]]
    consistent: bool
    revisions: int
    values_removed: int
    arc_checks: int
    candidate_states: int
    path: list[State]
    actions: list[str]


def _bounded_state_universe(
    origin: State,
    max_depth: int,
    action_order: str,
) -> set[State]:
    reached = {origin}
    frontier = deque([(origin, 0)])
    while frontier:
        state, depth = frontier.popleft()
        if depth >= max_depth:
            continue
        for neighbor, _, _ in PuzzleState(state).get_neighbors(action_order):
            if neighbor not in reached:
                reached.add(neighbor)
                frontier.append((neighbor, depth + 1))
    return reached


def _extract_chain_path(
    domains: list[set[State]],
    action_order: str,
) -> tuple[list[State], list[str]]:
    path = [next(iter(domains[0]))]
    actions: list[str] = []

    def extend(time_index: int) -> bool:
        if time_index == len(domains) - 1:
            return True
        current = path[-1]
        for candidate, action, _ in PuzzleState(current).get_neighbors(action_order):
            if candidate not in domains[time_index + 1]:
                continue
            path.append(candidate)
            actions.append(action)
            if extend(time_index + 1):
                return True
            path.pop()
            actions.pop()
        return False

    if extend(0):
        return path, actions
    return [], []


def run_state_chain_ac3(
    start: State,
    goal: State,
    *,
    time_horizon: int,
    action_order: str = "LRUD",
) -> AC3StateChainResult:
    """Enforce arc consistency on S[t] --legal move--> S[t+1]."""
    if time_horizon < 0:
        raise ValueError("time_horizon must be non-negative")
    if time_horizon == 0:
        consistent = start == goal
        domains = [{start}] if consistent else [set()]
        return AC3StateChainResult(
            domains=domains,
            consistent=consistent,
            revisions=0,
            values_removed=0,
            arc_checks=0,
            candidate_states=1 if consistent else 2,
            path=[start] if consistent else [],
            actions=[],
        )

    universe = (
        _bounded_state_universe(start, time_horizon, action_order)
        | _bounded_state_universe(goal, time_horizon, action_order)
    )
    domains = [{start}]
    domains.extend(set(universe) for _ in range(time_horizon - 1))
    domains.append({goal})

    neighbor_cache = {
        state: {
            neighbor
            for neighbor, _, _ in PuzzleState(state).get_neighbors(action_order)
        }
        for state in universe
    }
    queue = deque()
    for index in range(time_horizon):
        queue.append((index, index + 1))
        queue.append((index + 1, index))

    revisions = 0
    values_removed = 0
    arc_checks = 0

    while queue:
        left, right = queue.popleft()
        arc_checks += 1
        unsupported = {
            left_value
            for left_value in domains[left]
            if not any(
                right_value in neighbor_cache.get(left_value, set())
                for right_value in domains[right]
            )
        }
        if not unsupported:
            continue
        domains[left].difference_update(unsupported)
        revisions += 1
        values_removed += len(unsupported)
        if not domains[left]:
            return AC3StateChainResult(
                domains=domains,
                consistent=False,
                revisions=revisions,
                values_removed=values_removed,
                arc_checks=arc_checks,
                candidate_states=len(universe),
                path=[],
                actions=[],
            )
        for neighbor_index in (left - 1, left + 1):
            if 0 <= neighbor_index <= time_horizon and neighbor_index != right:
                queue.append((neighbor_index, left))

    path, actions = _extract_chain_path(domains, action_order)
    return AC3StateChainResult(
        domains=domains,
        consistent=bool(path),
        revisions=revisions,
        values_removed=values_removed,
        arc_checks=arc_checks,
        candidate_states=len(universe),
        path=path,
        actions=actions,
    )
