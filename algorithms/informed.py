"""Group 2: Informed Search Algorithms — Greedy, A*, IDA*."""

import time
import heapq
from typing import Callable, Optional
from core.puzzle import PuzzleState, GOAL_STATE, is_solvable
from core.node import Node, reconstruct_path, reconstruct_actions
from core.heuristics import get_heuristic
from core.metrics import SearchResult, TraceStep


def _unsolvable_result(
    algorithm: str,
    t0: float,
    is_complete: bool,
    is_optimal: bool,
) -> SearchResult:
    """Return a fast, goal-relative parity rejection for impossible 15-puzzle pairs."""
    return SearchResult(
        success=False,
        algorithm=algorithm,
        group="Informed Search",
        nodes_expanded=0,
        nodes_generated=0,
        max_frontier_size=0,
        reached_size=0,
        runtime=time.perf_counter() - t0,
        message="Puzzle is not solvable relative to the selected goal.",
        trace=[],
        is_complete=is_complete,
        is_optimal=is_optimal,
        uses_heuristic=True,
    )


def greedy_best_first(
    start: tuple[int, ...], goal: tuple[int, ...] = GOAL_STATE,
    heuristic: str = "Manhattan Distance",
    max_nodes: int = 50000, timeout: float = 60.0,
    action_order: str = "LRUD",
    tie_breaker: str = "FIFO",
) -> SearchResult:
    """Greedy Best-First Search. Uses h(n) only, not optimal."""
    t0 = time.perf_counter()

    if start == goal:
        return SearchResult(success=True, algorithm="Greedy Best-First", group="Informed Search",
                            path=[start], actions=[], goal_state=goal, cost=0, depth=0,
                            runtime=time.perf_counter() - t0, message="Already at goal",
                            is_complete=False, is_optimal=False, uses_heuristic=True)
    if not is_solvable(start, goal):
        return _unsolvable_result("Greedy Best-First", t0, False, False)

    h_fn = get_heuristic(heuristic, goal)

    def make_item(cost, n, c):
        if tie_breaker == "LIFO":
            return (cost, 0, -c, n)
        elif tie_breaker == "Min-g":
            return (cost, n.g, c, n)
        elif tie_breaker == "Max-g":
            return (cost, -n.g, c, n)
        else: # FIFO
            return (cost, 0, c, n)

    root = Node(state=start, g=0, depth=0, h=h_fn(start))
    counter = 0
    frontier = [make_item(root.h, root, counter)]
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

        item = heapq.heappop(frontier)
        node = item[-1]
        nodes_expanded += 1

        if node.state == goal:
            return SearchResult(success=True, algorithm="Greedy Best-First", group="Informed Search",
                                path=reconstruct_path(node), actions=reconstruct_actions(node),
                                goal_state=goal,
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
                heapq.heappush(frontier, make_item(h, child, counter))
                max_frontier = max(max_frontier, len(frontier))

                if len(trace) < 200:
                    trace.append(TraceStep(
                        step=nodes_expanded, state=ns, action=action,
                        g=child.g, h=h, f=child.g + h, depth=child.depth, event="generate",
                        frontier_size=len(frontier), reached_size=len(reached),
                        node_state=node.state, frontier_states=[entry[-1].state for entry in sorted(frontier)], reached_states=list(reached.keys()),
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
    tie_breaker: str = "FIFO",
) -> SearchResult:
    """A* Search. Optimal if heuristic is admissible and consistent."""
    t0 = time.perf_counter()

    if start == goal:
        return SearchResult(success=True, algorithm="A*", group="Informed Search",
                            path=[start], actions=[], goal_state=goal, cost=0, depth=0,
                            runtime=time.perf_counter() - t0, message="Already at goal",
                            is_complete=True, is_optimal=True, uses_heuristic=True)
    if not is_solvable(start, goal):
        return _unsolvable_result("A*", t0, True, True)

    h_fn = get_heuristic(heuristic, goal)

    def make_item(cost, n, c):
        if tie_breaker == "LIFO":
            return (cost, 0, -c, n)
        elif tie_breaker == "Min-g":
            return (cost, n.g, c, n)
        elif tie_breaker == "Max-g":
            return (cost, -n.g, c, n)
        else: # FIFO
            return (cost, 0, c, n)

    root = Node(state=start, g=0, depth=0, h=h_fn(start))
    counter = 0
    frontier = [make_item(root.f, root, counter)]
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

        item = heapq.heappop(frontier)
        node = item[-1]

        if node.state == goal:
            return SearchResult(success=True, algorithm="A*", group="Informed Search",
                                path=reconstruct_path(node), actions=reconstruct_actions(node),
                                goal_state=goal,
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
                heapq.heappush(frontier, make_item(child.f, child, counter))
                nodes_generated += 1
                max_frontier = max(max_frontier, len(frontier))

                if len(trace) < 200:
                    trace.append(TraceStep(
                        step=nodes_expanded, state=ns, action=action,
                        g=new_g, h=h, f=new_g + h, depth=child.depth, event="generate",
                        frontier_size=len(frontier), reached_size=len(best_g),
                        node_state=node.state, frontier_states=[entry[-1].state for entry in sorted(frontier)], reached_states=list(best_g.keys()),
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

    if start == goal:
        return SearchResult(success=True, algorithm="IDA*", group="Informed Search",
                            path=[start], actions=[], goal_state=goal, cost=0, depth=0,
                            runtime=time.perf_counter() - t0, message="Already at goal",
                            is_complete=True, is_optimal=True, uses_heuristic=True)
    if not is_solvable(start, goal):
        return _unsolvable_result("IDA*", t0, True, True)

    h_fn = get_heuristic(heuristic, goal)

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
            result.goal_state = goal
            result.runtime = time.perf_counter() - t0
            result.refresh_certificate()
            return result

        if next_threshold == float("inf"):
            break

        threshold = next_threshold

    return SearchResult(success=False, algorithm="IDA*", group="Informed Search",
                        nodes_expanded=total_expanded, nodes_generated=total_generated,
                        max_frontier_size=max_frontier,
                        runtime=time.perf_counter() - t0, message="No solution found", trace=trace,
                        is_complete=True, is_optimal=True, uses_heuristic=True)


def _ida_dfs(start, goal, threshold, h_fn, action_order,
             t0, timeout, prev_expanded, prev_generated,
             prev_max_frontier, global_trace):
    """DFS with f-limit for IDA*."""
    nodes_expanded = [prev_expanded]
    nodes_generated = [prev_generated]
    max_frontier = [prev_max_frontier]
    next_threshold = [float("inf")]
    result_holder = [None]

    def recursive_search(node, path_set):
        if result_holder[0] is not None:
            return
        if time.perf_counter() - t0 > timeout:
            return

        if node.f > threshold:
            next_threshold[0] = min(next_threshold[0], node.f)
            return

        if node.state == goal:
            path = reconstruct_path(node)
            actions = reconstruct_actions(node)
            result_holder[0] = SearchResult(
                success=True, path=path, actions=actions,
                cost=node.g, depth=node.depth,
                nodes_expanded=nodes_expanded[0], nodes_generated=nodes_generated[0],
                max_frontier_size=max_frontier[0], trace=global_trace,
                message=f"Found with threshold={threshold}",
            )
            return

        nodes_expanded[0] += 1
        ps = PuzzleState(node.state)

        for ns, action, cost in ps.get_neighbors(action_order):
            if ns in path_set:
                continue
            h = h_fn(ns)
            child = Node(state=ns, parent=node, action=action, g=node.g + cost, depth=node.depth + 1, h=h)
            nodes_generated[0] += 1

            if len(global_trace) < 200:
                global_trace.append(TraceStep(
                    step=nodes_expanded[0], state=ns, action=action,
                    g=child.g, h=h, f=child.f,
                    threshold=threshold,
                    frontier_size=0, reached_size=len(path_set),
                    reason=f"IDA*: threshold={threshold}, f={child.f:.1f}",
                ))

            path_set.add(ns)
            recursive_search(child, path_set)
            path_set.discard(ns)  # Correct backtracking in recursion
            if result_holder[0] is not None:
                return

    root = Node(state=start, g=0, depth=0, h=h_fn(start))
    path_set = {start}
    recursive_search(root, path_set)

    if result_holder[0] is not None:
        return result_holder[0], next_threshold[0]

    return SearchResult(
        success=False, message=f"cutoff at threshold {threshold}",
        nodes_expanded=nodes_expanded[0], nodes_generated=nodes_generated[0],
        max_frontier_size=max_frontier[0], trace=global_trace,
    ), next_threshold[0]
