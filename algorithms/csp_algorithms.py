"""Executable CSP algorithms over the shared bounded state-chain model."""

from __future__ import annotations

from collections import deque
import random
import time

from algorithms.csp_state_chain import (
    CSPModelLimit,
    State,
    StateChainCSP,
    build_state_chain_csp,
)
from core.metrics import SearchResult, TraceStep
from core.puzzle import GOAL_STATE


def _capability_for(algorithm: str) -> str:
    if algorithm == "AC-3":
        return "csp_propagation"
    if algorithm == "Min-Conflicts":
        return "csp_local_repair"
    return "csp_assignment_search"


def _variables(horizon: int) -> list[str]:
    return [f"S[{index}]" for index in range(horizon + 1)]


def _state_payload(state: State | None) -> list[int] | None:
    return list(state) if state is not None else None


def _assignment_payload(assignment: list[State | None] | tuple[State | None, ...]) -> list[list[int] | None]:
    return [_state_payload(state) for state in assignment]


def _constraint_checks(
    model: StateChainCSP,
    assignment: list[State | None] | tuple[State | None, ...],
) -> list[dict[str, object]]:
    checks: list[dict[str, object]] = []
    for index, (left, right) in enumerate(zip(assignment, assignment[1:])):
        action = None
        legal = False
        if left is not None and right is not None:
            action = model.action_between(left, right)
            legal = action is not None
        checks.append({
            "from": f"S[{index}]",
            "to": f"S[{index + 1}]",
            "action": action,
            "legal": legal,
        })
    return checks


def _assignment_evidence(
    model: StateChainCSP,
    domains: list[set[State]],
    *,
    partial_assignment: list[State | None] | tuple[State | None, ...] | None = None,
    complete_assignment: list[State] | tuple[State, ...] | None = None,
    **extra: object,
) -> dict[str, object]:
    partial = list(partial_assignment or [])
    complete = list(complete_assignment or [])
    check_source: list[State | None] = complete if complete else partial
    return {
        "horizon": model.horizon,
        "variables": _variables(model.horizon),
        "domain_sizes": [len(domain) for domain in domains],
        "partial_assignment": _assignment_payload(partial),
        "complete_assignment": [list(state) for state in complete],
        "constraint_checks": _constraint_checks(model, check_source),
        **extra,
    }


def _model_failure(
    algorithm: str,
    goal: State,
    started: float,
    message: str,
    reason: str,
) -> SearchResult:
    return SearchResult(
        success=False,
        algorithm=algorithm,
        group="CSP",
        capability=_capability_for(algorithm),
        goal_state=goal,
        runtime=time.perf_counter() - started,
        message=message,
        termination_reason=reason,
        suitable_for_puzzle=False,
    )


def _build_model(
    algorithm: str,
    start: State,
    goal: State,
    *,
    time_horizon: int,
    action_order: str,
    candidate_limit: int,
    timeout: float,
    started: float,
) -> tuple[StateChainCSP | None, SearchResult | None]:
    try:
        model = build_state_chain_csp(
            start,
            goal,
            horizon=time_horizon,
            action_order=action_order,
            candidate_limit=candidate_limit,
            timeout=timeout,
        )
    except (CSPModelLimit, ValueError) as exc:
        reason = "resource_limit" if isinstance(exc, CSPModelLimit) else "invalid_input"
        return None, _model_failure(
            algorithm,
            goal,
            started,
            str(exc),
            reason,
        )
    if any(not domain for domain in model.domains):
        return None, _model_failure(
            algorithm,
            goal,
            started,
            (
                f"Domain wipe-out: no exact-horizon assignment exists for T={time_horizon}. "
                "This bounded failure is not a proof that the puzzle is globally unsolvable."
            ),
            "horizon_infeasible",
        )
    return model, None


def _candidate_values(
    model: StateChainCSP,
    domain: set[State],
) -> list[State]:
    return sorted(domain)


def _extract_chain_assignment(
    model: StateChainCSP,
    domains: list[set[State]],
) -> tuple[list[State], list[str]]:
    """Extract one exact legal assignment after sound domain propagation."""
    if not domains or any(not domain for domain in domains):
        return [], []
    path = [model.start]

    def extend(index: int) -> bool:
        if index == model.horizon:
            return path[-1] == model.goal
        current = path[-1]
        for candidate in _candidate_values(model, domains[index + 1]):
            if not model.compatible(current, candidate):
                continue
            path.append(candidate)
            if extend(index + 1):
                return True
            path.pop()
        return False

    if not extend(0):
        return [], []
    return model.verify_assignment(path)


def _backtracking_result(
    algorithm: str,
    start: State,
    goal: State,
    *,
    time_horizon: int,
    max_steps: int,
    timeout: float,
    action_order: str,
    candidate_limit: int,
    forward_checking: bool,
) -> SearchResult:
    started = time.perf_counter()
    model, failure = _build_model(
        algorithm,
        start,
        goal,
        time_horizon=time_horizon,
        action_order=action_order,
        candidate_limit=candidate_limit,
        timeout=timeout,
        started=started,
    )
    if failure is not None or model is None:
        return failure

    domains = [set(domain) for domain in model.domains]
    assignment: list[State | None] = [None] * (time_horizon + 1)
    assignment[0] = tuple(start)
    assignment[-1] = tuple(goal)
    checks = 0
    assignments_tried = 0
    backtracks = 0
    values_pruned = 0
    trace: list[TraceStep] = []
    stop_reason: str | None = None

    def stopped() -> bool:
        nonlocal stop_reason
        if time.perf_counter() - started >= timeout:
            stop_reason = "timeout"
            return True
        if assignments_tried >= max_steps:
            stop_reason = "resource_limit"
            return True
        return False

    def search(index: int, active_domains: list[set[State]]) -> bool:
        nonlocal checks, assignments_tried, backtracks, values_pruned
        if stopped():
            return False
        if index >= time_horizon:
            complete = [state for state in assignment if state is not None]
            return len(complete) == time_horizon + 1 and bool(
                model.verify_assignment(complete)[0]
            )

        previous = assignment[index - 1]
        if previous is None:
            return False
        for candidate in _candidate_values(model, active_domains[index]):
            if stopped():
                return False
            assignments_tried += 1
            checks += 1
            compatible = model.compatible(previous, candidate)
            if len(trace) < 200:
                trace.append(
                    TraceStep(
                        step=assignments_tried,
                        state=candidate,
                        node_state=previous,
                        depth=index,
                        event="assign" if compatible else "reject_constraint",
                        belief_size=len(active_domains[index]),
                        reason=(
                            f"Try S[{index}]; legal predecessor={compatible}; "
                            f"domain={len(active_domains[index])}"
                        ),
                    )
                )
            if not compatible:
                continue

            assignment[index] = candidate
            next_domains = active_domains
            if forward_checking and index + 1 <= time_horizon:
                next_domains = [set(domain) for domain in active_domains]
                old_size = len(next_domains[index + 1])
                next_domains[index + 1] = {
                    value
                    for value in next_domains[index + 1]
                    if model.compatible(candidate, value)
                }
                removed = old_size - len(next_domains[index + 1])
                values_pruned += removed
                if len(trace) < 200:
                    trace.append(
                        TraceStep(
                            step=assignments_tried,
                            state=candidate,
                            depth=index,
                            event="forward_check",
                            belief_size=len(next_domains[index + 1]),
                            reason=(
                                f"Forward check D(S[{index + 1}]): "
                                f"{old_size}->{len(next_domains[index + 1])}; "
                                f"removed={removed}"
                            ),
                        )
                    )
                if not next_domains[index + 1]:
                    assignment[index] = None
                    backtracks += 1
                    continue

            if search(index + 1, next_domains):
                return True
            assignment[index] = None
            backtracks += 1
            if len(trace) < 200:
                trace.append(
                    TraceStep(
                        step=assignments_tried,
                        state=candidate,
                        depth=index,
                        event="backtrack",
                        reason=f"Backtrack from S[{index}]",
                    )
                )
        return False

    solved = search(1, domains)
    complete = [state for state in assignment if state is not None]
    path, actions = model.verify_assignment(complete) if solved else ([], [])
    if path:
        message = (
            f"{algorithm} found an exact-horizon CSP assignment for T={time_horizon}. "
            f"checks={checks}, backtracks={backtracks}, values_pruned={values_pruned}."
        )
        termination = "goal"
    else:
        message = (
            f"{algorithm} stopped without an exact-horizon assignment for T={time_horizon}. "
            f"checks={checks}, backtracks={backtracks}, values_pruned={values_pruned}. "
            "This is not a global unsolvability proof."
        )
        termination = stop_reason or "horizon_exhausted"
    return SearchResult(
        success=bool(path),
        algorithm=algorithm,
        group="CSP",
        capability=_capability_for(algorithm),
        model_evidence=_assignment_evidence(
            model,
            domains,
            partial_assignment=assignment,
            complete_assignment=path,
            assignments=assignments_tried,
            checks=checks,
            backtracks=backtracks,
            values_pruned=values_pruned,
        ),
        path=path,
        actions=actions,
        goal_state=goal,
        cost=len(actions),
        depth=len(actions),
        nodes_expanded=assignments_tried,
        nodes_generated=checks,
        reached_size=sum(len(domain) for domain in domains),
        runtime=time.perf_counter() - started,
        message=message,
        trace=trace,
        termination_reason=termination,
        is_complete=False,
        is_optimal=False,
        suitable_for_puzzle=False,
    )


def backtracking(
    start: State,
    goal: State = GOAL_STATE,
    *,
    time_horizon: int = 3,
    max_steps: int = 20_000,
    timeout: float = 5.0,
    action_order: str = "LRUD",
    candidate_limit: int = 20_000,
) -> SearchResult:
    """Chronological backtracking on the bounded state-chain CSP."""
    return _backtracking_result(
        "Backtracking",
        start,
        goal,
        time_horizon=time_horizon,
        max_steps=max_steps,
        timeout=timeout,
        action_order=action_order,
        candidate_limit=candidate_limit,
        forward_checking=False,
    )


def backtracking_forward_checking(
    start: State,
    goal: State = GOAL_STATE,
    *,
    time_horizon: int = 3,
    max_steps: int = 20_000,
    timeout: float = 5.0,
    action_order: str = "LRUD",
    candidate_limit: int = 20_000,
) -> SearchResult:
    """Backtracking with one-step domain filtering after each assignment."""
    return _backtracking_result(
        "Backtracking + Forward Checking",
        start,
        goal,
        time_horizon=time_horizon,
        max_steps=max_steps,
        timeout=timeout,
        action_order=action_order,
        candidate_limit=candidate_limit,
        forward_checking=True,
    )


def ac3(
    start: State,
    goal: State = GOAL_STATE,
    *,
    time_horizon: int = 3,
    timeout: float = 5.0,
    action_order: str = "LRUD",
    candidate_limit: int = 20_000,
) -> SearchResult:
    """Enforce arc consistency without pretending propagation is search."""
    started = time.perf_counter()
    model, failure = _build_model(
        "AC-3",
        start,
        goal,
        time_horizon=time_horizon,
        action_order=action_order,
        candidate_limit=candidate_limit,
        timeout=timeout,
        started=started,
    )
    if failure is not None or model is None:
        return failure

    domains = [set(domain) for domain in model.domains]
    queue = deque(
        (left, right)
        for index in range(time_horizon)
        for left, right in ((index, index + 1), (index + 1, index))
    )
    arc_checks = 0
    revisions = 0
    removed_total = 0
    trace: list[TraceStep] = []

    while queue:
        if time.perf_counter() - started >= timeout:
            return _model_failure(
                "AC-3", goal, started, "AC-3 timed out during propagation.", "timeout"
            )
        left, right = queue.popleft()
        arc_checks += 1
        before = len(domains[left])
        unsupported = {
            value
            for value in domains[left]
            if not any(model.compatible(value, support) for support in domains[right])
        }
        if unsupported:
            domains[left].difference_update(unsupported)
            revisions += 1
            removed_total += len(unsupported)
        representative = next(iter(domains[left]), tuple(start))
        if len(trace) < 200:
            trace.append(
                TraceStep(
                    step=arc_checks,
                    state=representative,
                    event="revise",
                    belief_size=len(domains[left]),
                    reason=(
                        f"REVISE(S[{left}], S[{right}]): "
                        f"{before}->{len(domains[left])}; removed={len(unsupported)}"
                    ),
                )
            )
        if not domains[left]:
            return SearchResult(
                success=False,
                algorithm="AC-3",
                group="CSP",
                capability="csp_propagation",
                model_evidence=_assignment_evidence(
                    model,
                    domains,
                    partial_assignment=[next(iter(domain), None) for domain in domains],
                    arc_checks=arc_checks,
                    revisions=revisions,
                    values_removed=removed_total,
                ),
                goal_state=goal,
                nodes_expanded=arc_checks,
                nodes_generated=model.candidate_states,
                reached_size=sum(len(domain) for domain in domains),
                runtime=time.perf_counter() - started,
                message=(
                    f"AC-3 detected a domain wipe-out at S[{left}] for "
                    f"T={time_horizon}."
                ),
                trace=trace,
                termination_reason="inconsistent",
                suitable_for_puzzle=False,
            )
        if unsupported:
            for neighbor in (left - 1, left + 1):
                if 0 <= neighbor <= time_horizon and neighbor != right:
                    queue.append((neighbor, left))

    path, actions = _extract_chain_assignment(model, domains)
    solved = bool(path)
    termination = "goal" if solved else "arc_consistent"
    message = (
        f"AC-3 State-Chain CSP completed: revisions={revisions}, values_removed={removed_total}, "
        f"arc_checks={arc_checks}. "
        + (
            "Arc-consistent domains contain an extracted verified goal path."
            if solved
            else "Domains are arc-consistent but not a unique solved assignment."
        )
    )
    return SearchResult(
        success=solved,
        algorithm="AC-3",
        group="CSP",
        capability="csp_propagation",
        model_evidence=_assignment_evidence(
            model,
            domains,
            partial_assignment=path or [next(iter(domain), None) for domain in domains],
            complete_assignment=path,
            arc_checks=arc_checks,
            revisions=revisions,
            values_removed=removed_total,
        ),
        path=path,
        actions=actions,
        goal_state=goal,
        cost=len(actions),
        depth=len(actions),
        nodes_expanded=arc_checks,
        nodes_generated=model.candidate_states,
        reached_size=sum(len(domain) for domain in domains),
        runtime=time.perf_counter() - started,
        message=message,
        trace=trace,
        termination_reason=termination,
        suitable_for_puzzle=False,
    )


def min_conflicts_state_chain(
    start: State,
    goal: State = GOAL_STATE,
    *,
    time_horizon: int = 3,
    max_iterations: int = 10_000,
    timeout: float = 5.0,
    action_order: str = "LRUD",
    candidate_limit: int = 20_000,
    seed: int | None = None,
) -> SearchResult:
    """Repair a complete state-chain assignment by minimizing edge conflicts."""
    started = time.perf_counter()
    model, failure = _build_model(
        "Min-Conflicts",
        start,
        goal,
        time_horizon=time_horizon,
        action_order=action_order,
        candidate_limit=candidate_limit,
        timeout=timeout,
        started=started,
    )
    if failure is not None or model is None:
        return failure

    rng = random.Random(seed)
    assignment = [
        next(iter(domain)) if len(domain) == 1 else rng.choice(sorted(domain))
        for domain in model.domains
    ]
    trace: list[TraceStep] = []

    def edge_conflict(left: State, right: State) -> int:
        return 0 if model.compatible(left, right) else 1

    def variable_conflicts(index: int, value: State) -> int:
        total = edge_conflict(assignment[index - 1], value) if index > 0 else 0
        if index < time_horizon:
            total += edge_conflict(value, assignment[index + 1])
        return total

    def conflicted_variables() -> list[int]:
        return [
            index
            for index in range(1, time_horizon)
            if variable_conflicts(index, assignment[index]) > 0
        ]

    for iteration in range(max_iterations + 1):
        path, actions = model.verify_assignment(assignment)
        if path:
            return SearchResult(
                success=True,
                algorithm="Min-Conflicts",
                group="CSP",
                capability="csp_local_repair",
                model_evidence=_assignment_evidence(
                    model,
                    [set(domain) for domain in model.domains],
                    partial_assignment=assignment,
                    complete_assignment=path,
                    iterations=iteration,
                    conflicts=0,
                ),
                path=path,
                actions=actions,
                goal_state=goal,
                cost=len(actions),
                depth=len(actions),
                random_seed=seed,
                nodes_expanded=iteration,
                nodes_generated=sum(len(domain) for domain in model.domains),
                runtime=time.perf_counter() - started,
                message=f"Min-Conflicts found a zero-conflict chain at iteration {iteration}.",
                trace=trace,
                termination_reason="goal",
                suitable_for_puzzle=False,
            )
        if iteration >= max_iterations or time.perf_counter() - started >= timeout:
            break
        conflicted = conflicted_variables()
        if not conflicted:
            break
        index = rng.choice(conflicted)
        scored = [
            (variable_conflicts(index, value), value)
            for value in model.domains[index]
        ]
        best_score = min(score for score, _ in scored)
        best_values = [value for score, value in scored if score == best_score]
        before = variable_conflicts(index, assignment[index])
        assignment[index] = rng.choice(sorted(best_values))
        if len(trace) < 200:
            trace.append(
                TraceStep(
                    step=iteration + 1,
                    state=assignment[index],
                    depth=index,
                    event="repair",
                    belief_size=len(model.domains[index]),
                    reason=(
                        f"Repair S[{index}]: conflicts {before}->{best_score}; "
                        f"candidate_values={len(model.domains[index])}"
                    ),
                )
            )

    final_conflicts = sum(
        edge_conflict(left, right)
        for left, right in zip(assignment, assignment[1:])
    )
    return SearchResult(
        success=False,
        algorithm="Min-Conflicts",
        group="CSP",
        capability="csp_local_repair",
        model_evidence=_assignment_evidence(
            model,
            [set(domain) for domain in model.domains],
            partial_assignment=assignment,
            iterations=min(max_iterations, len(trace)),
            conflicts=final_conflicts,
        ),
        goal_state=goal,
        random_seed=seed,
        nodes_expanded=min(max_iterations, len(trace)),
        nodes_generated=sum(len(domain) for domain in model.domains),
        runtime=time.perf_counter() - started,
        message=(
            f"Min-Conflicts stopped with {final_conflicts} violated transition "
            "constraint(s). No puzzle path is reported."
        ),
        trace=trace,
        termination_reason=(
            "timeout"
            if time.perf_counter() - started >= timeout
            else "iteration_limit"
        ),
        suitable_for_puzzle=False,
    )
