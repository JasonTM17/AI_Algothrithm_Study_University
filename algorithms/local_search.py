"""Group 3: Local Search Algorithms — Hill Climbing variants, Beam, Simulated Annealing."""

import time
import random
import math
from typing import Optional
from core.puzzle import PuzzleState, GOAL_STATE
from core.heuristics import get_heuristic
from core.metrics import SearchResult, TraceStep


TRACE_LIMIT = 200


def _get_h_fn(heuristic: str, goal: tuple[int, ...]):
    return get_heuristic(heuristic, goal)


def _record_local_children(
    trace: list[TraceStep],
    *,
    step: int,
    parent_state: tuple[int, ...],
    evaluated_neighbors: list[tuple[tuple[int, ...], str, int, float]],
    parent_h: float,
    parent_depth: int,
    selected_action: str | None = None,
    selected_state: tuple[int, ...] | None = None,
    hidden_child_states: set[tuple[int, ...]] | None = None,
    reason_prefix: str = "Generated local-search child",
) -> None:
    """Record every local-search neighbor as a real parent -> child tree edge."""
    hidden_child_states = hidden_child_states or set()
    visible_neighbors = [
        item for item in evaluated_neighbors
        if item[0] not in hidden_child_states
    ]
    child_states = [state for state, _, _, _ in visible_neighbors]
    for child_state, action, cost, child_h in visible_neighbors:
        if len(trace) >= TRACE_LIMIT:
            return
        selected = action == selected_action and (
            selected_state is None or child_state == selected_state
        )
        event = "select" if selected else "generate"
        comparison = "<" if child_h < parent_h else ">="
        trace.append(
            TraceStep(
                step=step,
                state=child_state,
                action=action,
                g=parent_depth + cost,
                h=child_h,
                f=child_h,
                depth=parent_depth + cost,
                current_h=parent_h,
                candidate_h=child_h,
                node_state=parent_state,
                frontier_size=len(visible_neighbors),
                frontier_states=child_states,
                event=event,
            reason=(
                f"Evaluate candidate ({reason_prefix.removesuffix(' generated neighbor')}): "
                f"action={action}, h={child_h:.1f} "
                f"{comparison} current h={parent_h:.1f}"
                + ("; selected" if selected else "")
            ),
            )
        )


def _evaluate_neighbors(neighbors, h_fn):
    return [(ns, action, cost, h_fn(ns)) for ns, action, cost in neighbors]


def _local_result(goal: tuple[int, ...], **kwargs) -> SearchResult:
    """Build a local-search result with explicit selected-goal context."""
    result = SearchResult(goal_state=goal, **kwargs)
    return result


def simple_hill_climbing(
    start: tuple[int, ...], goal: tuple[int, ...] = GOAL_STATE,
    heuristic: str = "Manhattan Distance",
    max_iterations: int = 10000,
    timeout: float = 60.0,
    action_order: str = "LRUD",
) -> SearchResult:
    """Simple Hill Climbing: pick first better neighbor."""
    t0 = time.perf_counter()
    h_fn = _get_h_fn(heuristic, goal)
    current = start
    current_h = h_fn(current)
    trace: list[TraceStep] = []
    nodes_expanded = 0
    path = [current]
    actions_taken: list[str] = []
    nodes_generated = 1

    for i in range(max_iterations):
        if time.perf_counter() - t0 > timeout:
            return _local_result(goal, success=False, algorithm="Simple Hill Climbing", group="Local Search",
                                path=path, actions=actions_taken, nodes_expanded=nodes_expanded,
                                nodes_generated=nodes_generated,
                                runtime=time.perf_counter() - t0, message="Timeout", trace=trace,
                                uses_heuristic=True, uses_randomness=False,
                                is_complete=False, is_optimal=False, suitable_for_puzzle=False)

        if current == goal:
            return _local_result(goal, success=True, algorithm="Simple Hill Climbing", group="Local Search",
                                path=path, actions=actions_taken, cost=len(actions_taken), depth=len(actions_taken),
                                nodes_expanded=nodes_expanded, nodes_generated=nodes_generated,
                                runtime=time.perf_counter() - t0, message="Goal reached", trace=trace,
                                uses_heuristic=True, uses_randomness=False,
                                is_complete=False, is_optimal=False, suitable_for_puzzle=False)

        ps = PuzzleState(current)
        neighbors = ps.get_neighbors(action_order)
        evaluated_neighbors = _evaluate_neighbors(neighbors, h_fn)
        nodes_generated += len(evaluated_neighbors)
        nodes_expanded += 1
        moved = False
        selected_ns, selected_action = None, None

        for ns, action, cost, nh in evaluated_neighbors:
            if nh < current_h:
                selected_ns, selected_action = ns, action
                _record_local_children(
                    trace,
                    step=i,
                    parent_state=current,
                    evaluated_neighbors=evaluated_neighbors,
                    parent_h=current_h,
                    parent_depth=len(actions_taken),
                    selected_action=selected_action,
                    selected_state=selected_ns,
                    hidden_child_states=set(path[:-1]),
                    reason_prefix="Simple HC generated neighbor",
                )
                current = ns
                current_h = nh
                path.append(current)
                actions_taken.append(action)
                moved = True
                break

        if not moved:
            _record_local_children(
                trace,
                step=i,
                parent_state=current,
                evaluated_neighbors=evaluated_neighbors,
                parent_h=current_h,
                parent_depth=len(actions_taken),
                hidden_child_states=set(path[:-1]),
                reason_prefix="Simple HC generated neighbor",
            )
            if len(trace) < TRACE_LIMIT:
                trace.append(TraceStep(step=i, state=current, current_h=current_h, h=current_h,
                                       reason=f"Stuck at local optimum h={current_h:.1f}"))
            return _local_result(goal, success=False, algorithm="Simple Hill Climbing", group="Local Search",
                                path=path, actions=actions_taken, depth=len(actions_taken),
                                nodes_expanded=nodes_expanded, nodes_generated=nodes_generated,
                                runtime=time.perf_counter() - t0,
                                message=f"Stuck at local optimum h={current_h:.1f}", trace=trace,
                                uses_heuristic=True, uses_randomness=False,
                                is_complete=False, is_optimal=False, suitable_for_puzzle=False)

    return _local_result(goal, success=False, algorithm="Simple Hill Climbing", group="Local Search",
                        path=path, actions=actions_taken, nodes_expanded=nodes_expanded,
                        nodes_generated=nodes_generated,
                        runtime=time.perf_counter() - t0, message="Max iterations reached", trace=trace,
                        uses_heuristic=True, uses_randomness=False,
                        is_complete=False, is_optimal=False, suitable_for_puzzle=False)


def steepest_ascent_hill_climbing(
    start: tuple[int, ...], goal: tuple[int, ...] = GOAL_STATE,
    heuristic: str = "Manhattan Distance",
    max_iterations: int = 10000, timeout: float = 60.0,
    action_order: str = "LRUD",
) -> SearchResult:
    """Steepest-Ascent Hill Climbing: pick the best neighbor."""
    t0 = time.perf_counter()
    h_fn = _get_h_fn(heuristic, goal)
    current = start
    current_h = h_fn(current)
    trace: list[TraceStep] = []
    nodes_expanded = 0
    path = [current]
    actions_taken: list[str] = []
    nodes_generated = 1

    for i in range(max_iterations):
        if time.perf_counter() - t0 > timeout:
            return _local_result(goal, success=False, algorithm="Steepest-Ascent Hill Climbing", group="Local Search",
                                path=path, actions=actions_taken, nodes_expanded=nodes_expanded,
                                nodes_generated=nodes_generated,
                                runtime=time.perf_counter() - t0, message="Timeout", trace=trace,
                                uses_heuristic=True, is_complete=False, is_optimal=False, suitable_for_puzzle=False)

        if current == goal:
            return _local_result(goal, success=True, algorithm="Steepest-Ascent Hill Climbing", group="Local Search",
                                path=path, actions=actions_taken, cost=len(actions_taken), depth=len(actions_taken),
                                nodes_expanded=nodes_expanded, nodes_generated=nodes_generated,
                                runtime=time.perf_counter() - t0, message="Goal reached", trace=trace,
                                uses_heuristic=True, is_complete=False, is_optimal=False, suitable_for_puzzle=False)

        ps = PuzzleState(current)
        neighbors = ps.get_neighbors(action_order)
        evaluated_neighbors = _evaluate_neighbors(neighbors, h_fn)
        nodes_generated += len(evaluated_neighbors)
        nodes_expanded += 1
        best_ns, best_action, best_h = None, None, float("inf")

        for ns, action, cost, nh in evaluated_neighbors:
            if nh < best_h:
                best_ns, best_action, best_h = ns, action, nh
            if len(trace) < 200:
                status = "eligible improvement" if nh < current_h else "rejected: not better"
                trace.append(TraceStep(
                    step=i, state=ns, node_state=current, action=action,
                    current_h=current_h, candidate_h=nh, h=nh,
                    reason=(
                        f"Evaluate candidate {action}: h(candidate)={nh:.1f}, "
                        f"h(current)={current_h:.1f}; {status}."
                    ),
                ))

        if best_ns is not None and best_h < current_h:
            _record_local_children(
                trace,
                step=i,
                parent_state=current,
                evaluated_neighbors=evaluated_neighbors,
                parent_h=current_h,
                parent_depth=len(actions_taken),
                selected_action=best_action,
                selected_state=best_ns,
                hidden_child_states=set(path[:-1]),
                reason_prefix="Steepest HC generated neighbor",
            )
            current = best_ns
            current_h = best_h
            path.append(current)
            actions_taken.append(best_action)
        else:
            _record_local_children(
                trace,
                step=i,
                parent_state=current,
                evaluated_neighbors=evaluated_neighbors,
                parent_h=current_h,
                parent_depth=len(actions_taken),
                hidden_child_states=set(path[:-1]),
                reason_prefix="Steepest HC generated neighbor",
            )
            if len(trace) < TRACE_LIMIT:
                trace.append(TraceStep(step=i, state=current, current_h=current_h, h=current_h,
                                       reason=f"Stuck: no neighbor better than h={current_h:.1f}"))
            return _local_result(goal, success=False, algorithm="Steepest-Ascent Hill Climbing", group="Local Search",
                                path=path, actions=actions_taken, depth=len(actions_taken),
                                nodes_expanded=nodes_expanded, nodes_generated=nodes_generated,
                                runtime=time.perf_counter() - t0,
                                message=f"Stuck at local optimum h={current_h:.1f}", trace=trace,
                                uses_heuristic=True, is_complete=False, is_optimal=False, suitable_for_puzzle=False)

    return _local_result(goal, success=False, algorithm="Steepest-Ascent Hill Climbing", group="Local Search",
                        path=path, actions=actions_taken, nodes_expanded=nodes_expanded,
                        nodes_generated=nodes_generated,
                        runtime=time.perf_counter() - t0, message="Max iterations reached", trace=trace,
                        uses_heuristic=True, is_complete=False, is_optimal=False, suitable_for_puzzle=False)


def stochastic_hill_climbing(
    start: tuple[int, ...], goal: tuple[int, ...] = GOAL_STATE,
    heuristic: str = "Manhattan Distance",
    max_iterations: int = 10000, timeout: float = 60.0,
    seed: Optional[int] = None, action_order: str = "LRUD",
) -> SearchResult:
    """Stochastic Hill Climbing: randomly pick among better neighbors."""
    t0 = time.perf_counter()
    rng = random.Random(seed)
    h_fn = _get_h_fn(heuristic, goal)
    current = start
    current_h = h_fn(current)
    trace: list[TraceStep] = []
    nodes_expanded = 0
    path = [current]
    actions_taken: list[str] = []
    nodes_generated = 1

    for i in range(max_iterations):
        if time.perf_counter() - t0 > timeout:
            return _local_result(goal, success=False, algorithm="Stochastic Hill Climbing", group="Local Search",
                                path=path, actions=actions_taken, nodes_expanded=nodes_expanded,
                                nodes_generated=nodes_generated, random_seed=seed,
                                runtime=time.perf_counter() - t0, message="Timeout", trace=trace,
                                uses_heuristic=True, uses_randomness=True,
                                is_complete=False, is_optimal=False, suitable_for_puzzle=False)

        if current == goal:
            return _local_result(goal, success=True, algorithm="Stochastic Hill Climbing", group="Local Search",
                                path=path, actions=actions_taken, cost=len(actions_taken), depth=len(actions_taken),
                                random_seed=seed,
                                nodes_expanded=nodes_expanded, nodes_generated=nodes_generated,
                                runtime=time.perf_counter() - t0, message="Goal reached", trace=trace,
                                uses_heuristic=True, uses_randomness=True,
                                is_complete=False, is_optimal=False, suitable_for_puzzle=False)

        ps = PuzzleState(current)
        neighbors = ps.get_neighbors(action_order)
        evaluated_neighbors = _evaluate_neighbors(neighbors, h_fn)
        nodes_generated += len(evaluated_neighbors)
        nodes_expanded += 1
        better = []
        for ns, a, _, nh in evaluated_neighbors:
            if nh < current_h:
                better.append((ns, a, nh))
            if len(trace) < 200:
                status = "eligible for random selection" if nh < current_h else "rejected: not better"
                trace.append(TraceStep(
                    step=i, state=ns, node_state=current, action=a,
                    current_h=current_h, candidate_h=nh, h=nh,
                    reason=(
                        f"Evaluate candidate {a}: h(candidate)={nh:.1f}, "
                        f"h(current)={current_h:.1f}; {status}."
                    ),
                ))

        if better:
            ns, action, nh = rng.choice(better)
            _record_local_children(
                trace,
                step=i,
                parent_state=current,
                evaluated_neighbors=evaluated_neighbors,
                parent_h=current_h,
                parent_depth=len(actions_taken),
                selected_action=action,
                selected_state=ns,
                hidden_child_states=set(path[:-1]),
                reason_prefix="Stochastic HC generated neighbor",
            )
            current = ns
            current_h = nh
            path.append(current)
            actions_taken.append(action)
        else:
            _record_local_children(
                trace,
                step=i,
                parent_state=current,
                evaluated_neighbors=evaluated_neighbors,
                parent_h=current_h,
                parent_depth=len(actions_taken),
                hidden_child_states=set(path[:-1]),
                reason_prefix="Stochastic HC generated neighbor",
            )
            if len(trace) < TRACE_LIMIT:
                trace.append(TraceStep(step=i, state=current, current_h=current_h,
                                       reason=f"Stuck: no better neighbor, h={current_h:.1f}"))
            return _local_result(goal, success=False, algorithm="Stochastic Hill Climbing", group="Local Search",
                                path=path, actions=actions_taken, depth=len(actions_taken),
                                random_seed=seed,
                                nodes_expanded=nodes_expanded, nodes_generated=nodes_generated,
                                runtime=time.perf_counter() - t0,
                                message=f"Stuck at local optimum h={current_h:.1f}", trace=trace,
                                uses_heuristic=True, uses_randomness=True,
                                is_complete=False, is_optimal=False, suitable_for_puzzle=False)

    return _local_result(goal, success=False, algorithm="Stochastic Hill Climbing", group="Local Search",
                        path=path, actions=actions_taken, nodes_expanded=nodes_expanded,
                        nodes_generated=nodes_generated, random_seed=seed,
                        runtime=time.perf_counter() - t0, message="Max iterations reached", trace=trace,
                        uses_heuristic=True, uses_randomness=True,
                        is_complete=False, is_optimal=False, suitable_for_puzzle=False)


def random_restart_hill_climbing(
    start: tuple[int, ...], goal: tuple[int, ...] = GOAL_STATE,
    heuristic: str = "Manhattan Distance",
    max_iterations: int = 5000, max_restarts: int = 20,
    timeout: float = 60.0, seed: Optional[int] = None,
    action_order: str = "LRUD",
) -> SearchResult:
    """Random-Restart Hill Climbing using legal random walks from the input."""
    t0 = time.perf_counter()
    rng = random.Random(seed)
    h_fn = _get_h_fn(heuristic, goal)

    best_path = [start]
    best_actions: list[str] = []
    best_h = h_fn(start)
    total_expanded = 0
    total_generated = 1
    trace: list[TraceStep] = []

    for restart in range(max_restarts):
        if time.perf_counter() - t0 > timeout:
            break

        current = start
        path = [start]
        actions_taken: list[str] = []
        if restart > 0:
            previous_action = None
            opposites = {"L": "R", "R": "L", "U": "D", "D": "U"}
            for _ in range(rng.randint(10, 25)):
                candidates = PuzzleState(current).get_neighbors(action_order)
                filtered = [item for item in candidates if item[1] != opposites.get(previous_action)]
                ns, action, _ = rng.choice(filtered or candidates)
                current = ns
                path.append(current)
                actions_taken.append(action)
                previous_action = action
                probe_h = h_fn(current)
                if len(trace) < 200:
                    trace.append(TraceStep(
                        step=restart,
                        state=current,
                        action=action,
                        h=probe_h,
                        current_h=probe_h,
                        reason=(
                            f"Restart {restart}: random-walk probe action={action}, "
                            "then hill climbing evaluates this trial state."
                        ),
                    ))
        current_h = h_fn(current)

        for i in range(max_iterations):
            if time.perf_counter() - t0 > timeout:
                break

            if current == goal:
                msg = f"Goal reached after legal random-walk restart {restart}"
                return _local_result(goal, success=True, algorithm="Random-Restart Hill Climbing", group="Local Search",
                                    path=path, actions=actions_taken, cost=len(actions_taken), depth=len(actions_taken),
                                    random_seed=seed,
                                    nodes_expanded=total_expanded, nodes_generated=total_generated,
                                    runtime=time.perf_counter() - t0, message=msg, trace=trace,
                                    uses_heuristic=True, uses_randomness=True,
                                    is_complete=False, is_optimal=False, suitable_for_puzzle=False)

            ps = PuzzleState(current)
            neighbors = ps.get_neighbors(action_order)
            evaluated_neighbors = _evaluate_neighbors(neighbors, h_fn)
            total_generated += len(evaluated_neighbors)
            total_expanded += 1
            better = [(ns, a, nh) for ns, a, _, nh in evaluated_neighbors if nh < current_h]

            if better:
                best_nn = min(better, key=lambda x: x[2])
                ns, action, nh = best_nn
                _record_local_children(
                    trace,
                    step=total_expanded,
                    parent_state=current,
                    evaluated_neighbors=evaluated_neighbors,
                    parent_h=current_h,
                    parent_depth=len(actions_taken),
                    selected_action=action,
                    selected_state=ns,
                    hidden_child_states=set(path[:-1]),
                    reason_prefix=f"Restart {restart} generated neighbor",
                )
                current, current_h = ns, nh
                path.append(current)
                actions_taken.append(action)
            else:
                _record_local_children(
                    trace,
                    step=total_expanded,
                    parent_state=current,
                    evaluated_neighbors=evaluated_neighbors,
                    parent_h=current_h,
                    parent_depth=len(actions_taken),
                    hidden_child_states=set(path[:-1]),
                    reason_prefix=f"Restart {restart} generated neighbor",
                )
                if current_h < best_h:
                    best_path, best_actions, best_h = path, actions_taken, current_h
                if len(trace) < TRACE_LIMIT:
                    trace.append(TraceStep(step=restart, state=current, current_h=current_h,
                                           reason=f"Restart {restart}: stuck h={current_h:.1f}"))
                break

        else:
            if current_h < best_h:
                best_path, best_actions, best_h = path, actions_taken, current_h

    return _local_result(goal, success=False, algorithm="Random-Restart Hill Climbing", group="Local Search",
                        path=best_path, actions=best_actions, depth=len(best_actions),
                        random_seed=seed,
                        nodes_expanded=total_expanded, nodes_generated=total_generated,
                        runtime=time.perf_counter() - t0,
                        message=f"Best h={best_h:.1f} after {max_restarts} restarts",
                        trace=trace, uses_heuristic=True, uses_randomness=True,
                        is_complete=False, is_optimal=False, suitable_for_puzzle=False)


def local_beam_search(
    start: tuple[int, ...], goal: tuple[int, ...] = GOAL_STATE,
    heuristic: str = "Manhattan Distance",
    beam_width: int = 3, max_iterations: int = 10000,
    timeout: float = 60.0, action_order: str = "LRUD",
) -> SearchResult:
    """Local Beam Search: keep k best states, expand all neighbors."""
    t0 = time.perf_counter()
    h_fn = _get_h_fn(heuristic, goal)
    beam = [(h_fn(start), start)]
    best_path = {start: ([start], [])}
    nodes_expanded = 0
    nodes_generated = 1
    max_frontier = 1
    trace: list[TraceStep] = []

    def best_trajectory() -> tuple[list[tuple[int, ...]], list[str]]:
        if not beam:
            return [start], []
        _, best_state = min(beam, key=lambda item: item[0])
        path, actions = best_path.get(best_state, ([start], []))
        return list(path), list(actions)

    for i in range(max_iterations):
        if time.perf_counter() - t0 > timeout:
            path, actions = best_trajectory()
            return _local_result(goal, success=False, algorithm="Local Beam Search", group="Local Search",
                                path=path, actions=actions, depth=len(actions),
                                nodes_expanded=nodes_expanded, nodes_generated=nodes_generated,
                                max_frontier_size=max_frontier, runtime=time.perf_counter() - t0,
                                message="Timeout", trace=trace,
                                uses_heuristic=True, is_complete=False, is_optimal=False, suitable_for_puzzle=False)

        all_neighbors = []
        next_frontier_states = []
        for _, state in beam:
            if state == goal:
                path, actions = best_path[state]
                return _local_result(goal, success=True, algorithm="Local Beam Search", group="Local Search",
                                    path=path, actions=actions, cost=len(actions), depth=len(actions),
                                    nodes_expanded=nodes_expanded, nodes_generated=nodes_generated,
                                    max_frontier_size=max_frontier,
                                    runtime=time.perf_counter() - t0, message="Goal reached", trace=trace,
                                    uses_heuristic=True, is_complete=False, is_optimal=False, suitable_for_puzzle=False)

            ps = PuzzleState(state)
            neighbors = ps.get_neighbors(action_order)
            evaluated_neighbors = _evaluate_neighbors(neighbors, h_fn)
            nodes_generated += len(evaluated_neighbors)
            next_frontier_states.extend(ns for ns, _, _, _ in evaluated_neighbors)
            nodes_expanded += 1
            for ns, action, cost, nh in evaluated_neighbors:
                all_neighbors.append((nh, ns, action, state))
            _record_local_children(
                trace,
                step=i,
                parent_state=state,
                evaluated_neighbors=evaluated_neighbors,
                parent_h=h_fn(state),
                parent_depth=len(best_path.get(state, ([state], []))[1]),
                hidden_child_states=set(best_path.get(state, ([state], []))[0][:-1]),
                reason_prefix="Beam generated neighbor",
            )

        all_neighbors.sort(key=lambda x: x[0])
        new_beam = []
        new_best_path = {}
        seen = set()
        for nh, ns, action, parent in all_neighbors:
            if ns not in seen:
                seen.add(ns)
                pp, pa = best_path.get(parent, ([parent], []))
                new_best_path[ns] = (pp + [ns], pa + [action])
                new_beam.append((nh, ns))
                if len(new_beam) >= beam_width:
                    break

        if not new_beam:
            if len(trace) < TRACE_LIMIT:
                trace.append(TraceStep(step=i, state=beam[0][1], current_h=beam[0][0],
                                       reason=f"Beam stuck, best h={beam[0][0]:.1f}"))
            break

        beam = new_beam
        best_path = new_best_path
        max_frontier = max(max_frontier, len(beam), len(next_frontier_states))

        if len(trace) < TRACE_LIMIT:
            trace.append(TraceStep(step=i, state=beam[0][1], current_h=beam[0][0],
                                   frontier_size=len(beam),
                                   frontier_states=[state for _, state in beam],
                                   reason=f"Beam iteration, best h={beam[0][0]:.1f}, width={len(beam)}"))

    path, actions = best_trajectory()
    best_h = h_fn(path[-1])
    return _local_result(goal, success=False, algorithm="Local Beam Search", group="Local Search",
                        path=path, actions=actions, depth=len(actions),
                        nodes_expanded=nodes_expanded, nodes_generated=nodes_generated,
                        max_frontier_size=max_frontier,
                        runtime=time.perf_counter() - t0,
                        message=f"Best h={best_h:.1f}", trace=trace,
                        uses_heuristic=True, is_complete=False, is_optimal=False, suitable_for_puzzle=False)


def simulated_annealing(
    start: tuple[int, ...], goal: tuple[int, ...] = GOAL_STATE,
    heuristic: str = "Manhattan Distance",
    max_iterations: int = 50000,
    initial_temp: float = 100.0,
    cooling_rate: float = 0.9995,
    min_temp: float = 0.01,
    seed: Optional[int] = None,
    timeout: float = 60.0,
    action_order: str = "LRUD",
) -> SearchResult:
    """Simulated Annealing: accept worse moves with decreasing probability."""
    t0 = time.perf_counter()
    rng = random.Random(seed)
    h_fn = _get_h_fn(heuristic, goal)

    current = start
    current_h = h_fn(current)
    best = start
    best_h = current_h
    best_path = [start]
    best_actions: list[str] = []

    path = [start]
    actions_taken: list[str] = []
    temp = initial_temp
    nodes_expanded = 0
    nodes_generated = 1
    trace: list[TraceStep] = []

    for i in range(max_iterations):
        if time.perf_counter() - t0 > timeout:
            break

        temp = initial_temp * (cooling_rate ** i)
        if temp < min_temp:
            temp = min_temp

        if current == goal:
            return _local_result(goal, success=True, algorithm="Simulated Annealing", group="Local Search",
                                path=path, actions=actions_taken, cost=len(actions_taken), depth=len(actions_taken),
                                random_seed=seed,
                                nodes_expanded=nodes_expanded, nodes_generated=nodes_generated,
                                runtime=time.perf_counter() - t0, message="Goal reached", trace=trace,
                                uses_heuristic=True, uses_randomness=True,
                                is_complete=False, is_optimal=False, suitable_for_puzzle=False)

        ps = PuzzleState(current)
        neighbors = ps.get_neighbors(action_order)
        if not neighbors:
            break
        evaluated_neighbors = _evaluate_neighbors(neighbors, h_fn)
        nodes_generated += len(evaluated_neighbors)
        nodes_expanded += 1

        parent_state = current
        parent_depth = len(actions_taken)
        ns, action, cost, nh = rng.choice(evaluated_neighbors)
        delta = nh - current_h

        accepted = False
        probability = 0.0
        old_h = current_h

        if delta < 0:
            accepted = True
        else:
            probability = min(1.0, math.exp(-delta / max(temp, 0.001)))
            accepted = rng.random() < probability

        if accepted:
            current = ns
            current_h = nh
            path.append(current)
            actions_taken.append(action)
            if current_h < best_h:
                best = current
                best_h = current_h
                best_path = list(path)
                best_actions = list(actions_taken)

        _record_local_children(
            trace,
            step=i,
            parent_state=parent_state,
            evaluated_neighbors=evaluated_neighbors,
            parent_h=old_h,
            parent_depth=parent_depth,
            selected_action=action,
            selected_state=ns,
            hidden_child_states=set(path[:-1]),
            reason_prefix="Simulated Annealing generated neighbor",
        )
        if len(trace) < TRACE_LIMIT:
            trace.append(TraceStep(step=i, state=ns, action=action,
                                   current_h=old_h, candidate_h=nh,
                                   temperature=round(temp, 4), probability=round(probability, 4) if delta >= 0 else 1.0,
                                   accepted=accepted, reason=f"T={temp:.2f}, δ={delta:.1f}, {'accept' if accepted else 'reject'}"))

    if best == goal:
        return _local_result(goal, success=True, algorithm="Simulated Annealing", group="Local Search",
                            path=best_path, actions=best_actions, cost=len(best_actions), depth=len(best_actions),
                            random_seed=seed,
                            nodes_expanded=nodes_expanded, nodes_generated=nodes_generated,
                            runtime=time.perf_counter() - t0, message="Goal reached", trace=trace,
                            uses_heuristic=True, uses_randomness=True,
                            is_complete=False, is_optimal=False, suitable_for_puzzle=False)

    return _local_result(goal, success=False, algorithm="Simulated Annealing", group="Local Search",
                        path=best_path, actions=best_actions, depth=len(best_actions),
                        random_seed=seed,
                        nodes_expanded=nodes_expanded, nodes_generated=nodes_generated,
                        runtime=time.perf_counter() - t0,
                        message=f"Best h={best_h:.1f}, temp={temp:.4f}", trace=trace,
                        uses_heuristic=True, uses_randomness=True,
                        is_complete=False, is_optimal=False, suitable_for_puzzle=False)
