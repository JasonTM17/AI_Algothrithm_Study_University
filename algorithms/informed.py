"""Group 2: Informed Search Algorithms — Greedy, A*, IDA*."""

import time
import heapq
from typing import Callable, Optional
from core.puzzle import PuzzleState, GOAL_STATE
from core.node import Node, reconstruct_path, reconstruct_actions
from core.heuristics import manhattan_distance, HEURISTICS
from core.metrics import SearchResult, TraceStep


def greedy_best_first(
    start: tuple[int, ...], goal: tuple[int, ...] = GOAL_STATE,
    heuristic: str = "Manhattan Distance",
    max_nodes: int = 50000, timeout: float = 60.0,
    action_order: str = "LRUD",
) -> SearchResult:
    """Greedy Best-First Search. Uses h(n) only, not optimal."""
    t0 = time.perf_counter()
    h_fn = HEURISTICS.get(heuristic, manhattan_distance)

    if start == goal:
        return SearchResult(success=True, algorithm="Greedy Best-First", group="Informed Search",
                            path=[start], actions=[], cost=0, depth=0,
                            runtime=time.perf_counter() - t0, message="Already at goal",
                            is_complete=True, is_optimal=False, uses_heuristic=True)

    root = Node(state=start, g=0, depth=0, h=h_fn(start))
    counter = 0
    frontier: list[tuple[float, int, Node]] = [(root.h, counter, root)]
    reached = {start: 0}
    nodes_expanded = 0
    nodes_generated = 1
    max_frontier = 1
    trace: list[TraceStep] = []

    while frontier:
        if time.perf_counter() - t0 > timeout:
            return SearchResult(success=False, algorithm="Greedy Best-First", group="Informed Search",
                                nodes_expanded=nodes_expanded, nodes_generated=nodes_generated,
                                max_frontier_size=max_frontier, reached_size=len(reached),
                                runtime=time.perf_counter() - t0, message="Timeout", trace=trace,
                                is_complete=False, is_optimal=False, uses_heuristic=True)
        if len(reached) > max_nodes:
            return SearchResult(success=False, algorithm="Greedy Best-First", group="Informed Search",
                                nodes_expanded=nodes_expanded, nodes_generated=nodes_generated,
                                max_frontier_size=max_frontier, reached_size=len(reached),
                                runtime=time.perf_counter() - t0,
                                message=f"Node limit exceeded ({max_nodes})", trace=trace,
                                is_complete=False, is_optimal=False, uses_heuristic=True)

        _, _, node = heapq.heappop(frontier)
        nodes_expanded += 1

        if node.state == goal:
            return SearchResult(success=True, algorithm="Greedy Best-First", group="Informed Search",
                                path=reconstruct_path(node), actions=reconstruct_actions(node),
                                cost=node.g, depth=node.depth,
                                nodes_expanded=nodes_expanded, nodes_generated=nodes_generated,
                                max_frontier_size=max_frontier, reached_size=len(reached),
                                runtime=time.perf_counter() - t0, message="Solution found", trace=trace,
                                is_complete=False, is_optimal=False, uses_heuristic=True)

        ps = PuzzleState(node.state)
        for ns, action, cost in ps.get_neighbors(action_order):
            if time.perf_counter() - t0 > timeout:
                return SearchResult(success=False, algorithm="Greedy Best-First", group="Informed Search",
                                    nodes_expanded=nodes_expanded, nodes_generated=nodes_generated,
                                    max_frontier_size=max_frontier, reached_size=len(reached),
                                    runtime=time.perf_counter() - t0, message="Timeout", trace=trace,
                                    is_complete=False, is_optimal=False, uses_heuristic=True)

            h = h_fn(ns)
            child = Node(state=ns, parent=node, action=action, g=node.g + cost, depth=node.depth + 1, h=h)
            nodes_generated += 1

            if ns not in reached or child.g < reached[ns]:
                reached[ns] = child.g
                counter += 1
                heapq.heappush(frontier, (h, counter, child))
                max_frontier = max(max_frontier, len(frontier))

                if len(trace) < 200:
                    trace.append(TraceStep(
                        step=nodes_expanded, state=ns, action=action,
                        g=child.g, h=h, f=child.g + h,
                        frontier_size=len(frontier), reached_size=len(reached),
                        node_state=node.state, frontier_states=[n.state for _, _, n in frontier], reached_states=list(reached.keys()),
                        reason=f"Greedy: expand h={h:.1f}",
                    ))

    return SearchResult(success=False, algorithm="Greedy Best-First", group="Informed Search",
                        nodes_expanded=nodes_expanded, nodes_generated=nodes_generated,
                        max_frontier_size=max_frontier, reached_size=len(reached),
                        runtime=time.perf_counter() - t0, message="No solution found", trace=trace,
                        is_complete=False, is_optimal=False, uses_heuristic=True)


def a_star(
    start: tuple[int, ...], goal: tuple[int, ...] = GOAL_STATE,
    heuristic: str = "Manhattan Distance",
    max_nodes: int = 100000, timeout: float = 120.0,
    action_order: str = "LRUD",
) -> SearchResult:
    """A* Search. Optimal if heuristic is admissible and consistent."""
    t0 = time.perf_counter()
    h_fn = HEURISTICS.get(heuristic, manhattan_distance)

    if start == goal:
        return SearchResult(success=True, algorithm="A*", group="Informed Search",
                            path=[start], actions=[], cost=0, depth=0,
                            runtime=time.perf_counter() - t0, message="Already at goal",
                            is_complete=True, is_optimal=True, uses_heuristic=True)

    root = Node(state=start, g=0, depth=0, h=h_fn(start))
    counter = 0
    frontier: list[tuple[float, int, Node]] = [(root.f, counter, root)]
    best_g = {start: 0}
    nodes_expanded = 0
    nodes_generated = 1
    max_frontier = 1
    trace: list[TraceStep] = []

    while frontier:
        if time.perf_counter() - t0 > timeout:
            return SearchResult(success=False, algorithm="A*", group="Informed Search",
                                nodes_expanded=nodes_expanded, nodes_generated=nodes_generated,
                                max_frontier_size=max_frontier, reached_size=len(best_g),
                                runtime=time.perf_counter() - t0, message="Timeout", trace=trace,
                                is_complete=True, is_optimal=True, uses_heuristic=True)
        if len(best_g) > max_nodes:
            return SearchResult(success=False, algorithm="A*", group="Informed Search",
                                nodes_expanded=nodes_expanded, nodes_generated=nodes_generated,
                                max_frontier_size=max_frontier, reached_size=len(best_g),
                                runtime=time.perf_counter() - t0,
                                message=f"Node limit exceeded ({max_nodes})", trace=trace,
                                is_complete=True, is_optimal=True, uses_heuristic=True)

        _, _, node = heapq.heappop(frontier)

        if node.state == goal:
            return SearchResult(success=True, algorithm="A*", group="Informed Search",
                                path=reconstruct_path(node), actions=reconstruct_actions(node),
                                cost=node.g, depth=node.depth,
                                nodes_expanded=nodes_expanded, nodes_generated=nodes_generated,
                                max_frontier_size=max_frontier, reached_size=len(best_g),
                                runtime=time.perf_counter() - t0, message="Solution found", trace=trace,
                                is_complete=True, is_optimal=True, uses_heuristic=True)

        if node.g > best_g.get(node.state, float("inf")):
            continue

        nodes_expanded += 1
        ps = PuzzleState(node.state)

        for ns, action, cost in ps.get_neighbors(action_order):
            if time.perf_counter() - t0 > timeout:
                return SearchResult(success=False, algorithm="A*", group="Informed Search",
                                    nodes_expanded=nodes_expanded, nodes_generated=nodes_generated,
                                    max_frontier_size=max_frontier, reached_size=len(best_g),
                                    runtime=time.perf_counter() - t0, message="Timeout", trace=trace,
                                    is_complete=True, is_optimal=True, uses_heuristic=True)

            new_g = node.g + cost
            if new_g < best_g.get(ns, float("inf")):
                best_g[ns] = new_g
                h = h_fn(ns)
                child = Node(state=ns, parent=node, action=action, g=new_g, depth=node.depth + 1, h=h)
                counter += 1
                heapq.heappush(frontier, (child.f, counter, child))
                nodes_generated += 1
                max_frontier = max(max_frontier, len(frontier))

                if len(trace) < 200:
                    trace.append(TraceStep(
                        step=nodes_expanded, state=ns, action=action,
                        g=new_g, h=h, f=new_g + h,
                        frontier_size=len(frontier), reached_size=len(best_g),
                        node_state=node.state, frontier_states=[n.state for _, _, n in frontier], reached_states=list(best_g.keys()),
                        reason=f"A*: g={new_g}, h={h:.1f}, f={new_g+h:.1f}",
                    ))

    return SearchResult(success=False, algorithm="A*", group="Informed Search",
                        nodes_expanded=nodes_expanded, nodes_generated=nodes_generated,
                        max_frontier_size=max_frontier, reached_size=len(best_g),
                        runtime=time.perf_counter() - t0, message="No solution found", trace=trace,
                        is_complete=True, is_optimal=True, uses_heuristic=True)


def ida_star(
    start: tuple[int, ...], goal: tuple[int, ...] = GOAL_STATE,
    heuristic: str = "Manhattan Distance",
    max_nodes: int = 100000, timeout: float = 120.0,
    action_order: str = "LRUD",
) -> SearchResult:
    """Iterative Deepening A*. Memory-efficient, optimal with admissible heuristic."""
    t0 = time.perf_counter()
    h_fn = HEURISTICS.get(heuristic, manhattan_distance)

    if start == goal:
        return SearchResult(success=True, algorithm="IDA*", group="Informed Search",
                            path=[start], actions=[], cost=0, depth=0,
                            runtime=time.perf_counter() - t0, message="Already at goal",
                            is_complete=True, is_optimal=True, uses_heuristic=True)

    threshold = h_fn(start)
    total_expanded = 0
    total_generated = 0
    max_frontier = 0
    trace: list[TraceStep] = []

    while True:
        if time.perf_counter() - t0 > timeout:
            return SearchResult(success=False, algorithm="IDA*", group="Informed Search",
                                nodes_expanded=total_expanded, nodes_generated=total_generated,
                                max_frontier_size=max_frontier,
                                runtime=time.perf_counter() - t0, message="Timeout", trace=trace,
                                is_complete=True, is_optimal=True, uses_heuristic=True)
        if total_expanded > max_nodes:
            return SearchResult(success=False, algorithm="IDA*", group="Informed Search",
                                nodes_expanded=total_expanded, nodes_generated=total_generated,
                                max_frontier_size=max_frontier,
                                runtime=time.perf_counter() - t0,
                                message=f"Node limit exceeded ({max_nodes})", trace=trace,
                                is_complete=True, is_optimal=True, uses_heuristic=True)

        result, next_threshold = _ida_dfs(
            start, goal, threshold, h_fn, action_order,
            t0, timeout, total_expanded, total_generated, max_frontier, trace,
        )

        total_expanded = result.nodes_expanded
        total_generated = result.nodes_generated
        max_frontier = max(max_frontier, result.max_frontier_size)
        trace = result.trace

        if result.success:
            result.algorithm = "IDA*"
            result.group = "Informed Search"
            result.is_complete = True
            result.is_optimal = True
            result.uses_heuristic = True
            result.runtime = time.perf_counter() - t0
            return result

        if next_threshold == float("inf"):
            break

        threshold = next_threshold

    return SearchResult(success=False, algorithm="IDA*", group="Informed Search",
                        nodes_expanded=total_expanded, nodes_generated=total_generated,
                        max_frontier_size=max_frontier,
                        runtime=time.perf_counter() - t0, message="No solution found", trace=trace,
                        is_complete=True, is_optimal=True, uses_heuristic=True)


def _ida_dfs(
    start: tuple, goal: tuple, threshold: float,
    h_fn: Callable, action_order: str,
    t0: float, timeout: float,
    prev_expanded: int, prev_generated: int,
    prev_max_frontier: int, global_trace: list,
) -> tuple[SearchResult, float]:
    """DFS with f-limit for IDA*."""
    root = Node(state=start, g=0, depth=0, h=h_fn(start))
    stack = [root]
    next_threshold = float("inf")
    nodes_expanded = prev_expanded
    nodes_generated = prev_generated
    max_frontier = prev_max_frontier
    path_set = {start}
    path_list = [root]

    while stack:
        if time.perf_counter() - t0 > timeout:
            return SearchResult(
                success=False, message="Timeout",
                nodes_expanded=nodes_expanded, nodes_generated=nodes_generated,
                max_frontier_size=max_frontier, trace=global_trace,
            ), next_threshold

        node = stack.pop()

        if node.f > threshold:
            next_threshold = min(next_threshold, node.f)
            continue

        if node.state == goal:
            path = reconstruct_path(node)
            actions = reconstruct_actions(node)
            return SearchResult(
                success=True, path=path, actions=actions,
                cost=node.g, depth=node.depth,
                nodes_expanded=nodes_expanded, nodes_generated=nodes_generated,
                max_frontier_size=max_frontier, trace=global_trace,
                message=f"Found with threshold={threshold}",
            ), next_threshold

        nodes_expanded += 1
        ps = PuzzleState(node.state)

        for ns, action, cost in reversed(ps.get_neighbors(action_order)):
            h = h_fn(ns)
            child = Node(state=ns, parent=node, action=action, g=node.g + cost, depth=node.depth + 1, h=h)
            nodes_generated += 1

            if ns not in path_set:
                path_set.add(ns)
                path_list.append(child)
                stack.append(child)
                max_frontier = max(max_frontier, len(stack))

                if len(global_trace) < 200:
                    global_trace.append(TraceStep(
                        step=nodes_expanded, state=ns, action=action,
                        g=child.g, h=h, f=child.f,
                        threshold=threshold,
                        frontier_size=len(stack), reached_size=len(path_set),
                        reason=f"IDA*: threshold={threshold}, f={child.f:.1f}",
                    ))
            elif child.f <= threshold:
                stack.append(child)
                nodes_generated += 1

        path_set.discard(node.state)

    return SearchResult(
        success=False, message=f"cutoff at threshold {threshold}",
        nodes_expanded=nodes_expanded, nodes_generated=nodes_generated,
        max_frontier_size=max_frontier, trace=global_trace,
    ), next_threshold