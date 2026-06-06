"""Group 1: Uninformed Search Algorithms — BFS, DFS, UCS, IDS."""

import time
from collections import deque
import heapq
from typing import Optional
from core.puzzle import PuzzleState, GOAL_STATE, _move_blank
from core.node import Node, reconstruct_path, reconstruct_actions
from core.heuristics import manhattan_distance
from core.metrics import SearchResult, TraceStep

ACTIONS_LIST = ("L", "R", "U", "D")


def _make_result(
    success: bool, algorithm: str, node: Optional[Node],
    start: tuple, goal: tuple,
    nodes_expanded: int, nodes_generated: int,
    max_frontier: int, reached_size: int,
    t0: float, trace: list, message: str = "",
    is_complete: bool = False, is_optimal: bool = False,
) -> SearchResult:
    """Build SearchResult from search outcome."""
    elapsed = time.perf_counter() - t0
    if success:
        if node is not None:
            path = reconstruct_path(node)
            actions = reconstruct_actions(node)
            return SearchResult(
                success=True, algorithm=algorithm, group="Uninformed Search",
                path=path, actions=actions, cost=node.g, depth=node.depth,
                nodes_expanded=nodes_expanded, nodes_generated=nodes_generated,
                max_frontier_size=max_frontier, reached_size=reached_size,
                runtime=elapsed, message=message, trace=trace,
                is_complete=is_complete, is_optimal=is_optimal,
            )
        else:
            return SearchResult(
                success=True, algorithm=algorithm, group="Uninformed Search",
                path=[start], actions=[], cost=0, depth=0,
                nodes_expanded=nodes_expanded, nodes_generated=nodes_generated,
                max_frontier_size=max_frontier, reached_size=reached_size,
                runtime=elapsed, message=message, trace=trace,
                is_complete=is_complete, is_optimal=is_optimal,
            )
    return SearchResult(
        success=False, algorithm=algorithm, group="Uninformed Search",
        nodes_expanded=nodes_expanded, nodes_generated=nodes_generated,
        max_frontier_size=max_frontier, reached_size=reached_size,
        runtime=elapsed, message=message, trace=trace,
        is_complete=is_complete, is_optimal=is_optimal,
    )


def bfs(
    start: tuple[int, ...], goal: tuple[int, ...] = GOAL_STATE,
    max_nodes: int = 50000, timeout: float = 60.0,
    action_order: str = "LRUD",
) -> SearchResult:
    """Breadth-First Search. Optimal for unit-cost, complete, high memory."""
    t0 = time.perf_counter()
    if start == goal:
        return _make_result(True, "BFS", None, start, goal, 0, 0, 0, 0, t0, [], "Already at goal", True, True)

    root = Node(state=start, g=0, depth=0)
    frontier: deque[Node] = deque([root])
    reached = {start: 0}
    nodes_expanded = 0
    nodes_generated = 1
    max_frontier = 1
    trace: list[TraceStep] = []

    while frontier:
        if time.perf_counter() - t0 > timeout:
            return _make_result(False, "BFS", None, start, goal, nodes_expanded, nodes_generated, max_frontier, len(reached), t0, trace, "Timeout", True, True)
        if len(reached) > max_nodes:
            return _make_result(False, "BFS", None, start, goal, nodes_expanded, nodes_generated, max_frontier, len(reached), t0, trace, f"Node limit exceeded ({max_nodes})", True, True)

        node = frontier.popleft()
        nodes_expanded += 1
        ps = PuzzleState(node.state)

        for ns, action, cost in ps.get_neighbors(action_order):
            if time.perf_counter() - t0 > timeout:
                return _make_result(False, "BFS", None, start, goal, nodes_expanded, nodes_generated, max_frontier, len(reached), t0, trace, "Timeout", True, True)

            child = Node(state=ns, parent=node, action=action, g=node.g + cost, depth=node.depth + 1)
            nodes_generated += 1

            if ns == goal:
                trace.append(TraceStep(step=nodes_expanded, state=ns, action=action, g=child.g, h=0, f=child.g, frontier_size=len(frontier), reached_size=len(reached), node_state=ns, frontier_states=[n.state for n in frontier], reached_states=list(reached.keys()), reason="Goal found"))
                return _make_result(True, "BFS", child, start, goal, nodes_expanded, nodes_generated, max_frontier, len(reached), t0, trace, "Solution found", True, True)

            if ns not in reached or child.g < reached[ns]:
                reached[ns] = child.g
                frontier.append(child)
                max_frontier = max(max_frontier, len(frontier))

            if len(trace) < 200:
                trace.append(TraceStep(
                    step=nodes_expanded, state=ns, action=action,
                    g=child.g, h=manhattan_distance(ns),
                    f=child.g + manhattan_distance(ns),
                    frontier_size=len(frontier), reached_size=len(reached),
                    node_state=node.state, frontier_states=[n.state for n in frontier], reached_states=list(reached.keys()),
                    reason=f"Expand node, action={action}",
                ))

    return _make_result(False, "BFS", None, start, goal, nodes_expanded, nodes_generated, max_frontier, len(reached), t0, trace, "No solution found", True, True)


def dfs(
    start: tuple[int, ...], goal: tuple[int, ...] = GOAL_STATE,
    max_depth: int = 50, max_nodes: int = 50000,
    timeout: float = 60.0, action_order: str = "LRUD",
) -> SearchResult:
    """Depth-First Search with depth limit. Not optimal."""
    t0 = time.perf_counter()
    if start == goal:
        return _make_result(True, "DFS", None, start, goal, 0, 0, 0, 0, t0, [], "Already at goal", True, False)

    root = Node(state=start, g=0, depth=0)
    frontier: list[Node] = [root]
    reached = {start}
    nodes_expanded = 0
    nodes_generated = 1
    max_frontier = 1
    trace: list[TraceStep] = []

    while frontier:
        if time.perf_counter() - t0 > timeout:
            return _make_result(False, "DFS", None, start, goal, nodes_expanded, nodes_generated, max_frontier, len(reached), t0, trace, "Timeout", True, False)
        if nodes_expanded > max_nodes:
            return _make_result(False, "DFS", None, start, goal, nodes_expanded, nodes_generated, max_frontier, len(reached), t0, trace, f"Node limit exceeded ({max_nodes})", True, False)

        node = frontier.pop()
        nodes_expanded += 1

        if node.depth >= max_depth:
            continue

        ps = PuzzleState(node.state)
        for ns, action, cost in reversed(ps.get_neighbors(action_order)):
            if time.perf_counter() - t0 > timeout:
                return _make_result(False, "DFS", None, start, goal, nodes_expanded, nodes_generated, max_frontier, len(reached), t0, trace, "Timeout", True, False)

            child = Node(state=ns, parent=node, action=action, g=node.g + cost, depth=node.depth + 1)
            nodes_generated += 1

            if ns == goal:
                return _make_result(True, "DFS", child, start, goal, nodes_expanded, nodes_generated, max_frontier, len(reached), t0, trace, "Solution found", True, False)

            if ns not in reached:
                reached.add(ns)
                frontier.append(child)
                max_frontier = max(max_frontier, len(frontier))

                if len(trace) < 200:
                    trace.append(TraceStep(
                        step=nodes_expanded, state=ns, action=action,
                        g=child.g, h=0, f=child.g,
                        frontier_size=len(frontier), reached_size=len(reached),
                        node_state=node.state, frontier_states=[n.state for n in frontier], reached_states=list(reached),
                        reason=f"Depth-first expand, action={action}",
                    ))

    return _make_result(False, "DFS", None, start, goal, nodes_expanded, nodes_generated, max_frontier, len(reached), t0, trace, "No solution found within depth limit", True, False)


def ucs(
    start: tuple[int, ...], goal: tuple[int, ...] = GOAL_STATE,
    max_nodes: int = 50000, timeout: float = 60.0,
    action_order: str = "LRUD",
) -> SearchResult:
    """Uniform Cost Search. Optimal, same as BFS for unit cost."""
    t0 = time.perf_counter()
    if start == goal:
        return _make_result(True, "UCS", None, start, goal, 0, 0, 0, 0, t0, [], "Already at goal", True, True)

    root = Node(state=start, g=0, depth=0)
    counter = 0
    frontier: list[tuple[int, int, Node]] = [(0, counter, root)]
    best_g = {start: 0}
    nodes_expanded = 0
    nodes_generated = 1
    max_frontier = 1
    trace: list[TraceStep] = []

    while frontier:
        if time.perf_counter() - t0 > timeout:
            return _make_result(False, "UCS", None, start, goal, nodes_expanded, nodes_generated, max_frontier, len(best_g), t0, trace, "Timeout", True, True)
        if len(best_g) > max_nodes:
            return _make_result(False, "UCS", None, start, goal, nodes_expanded, nodes_generated, max_frontier, len(best_g), t0, trace, f"Node limit exceeded ({max_nodes})", True, True)

        _, _, node = heapq.heappop(frontier)

        if node.state == goal:
            return _make_result(True, "UCS", node, start, goal, nodes_expanded, nodes_generated, max_frontier, len(best_g), t0, trace, "Solution found", True, True)

        if node.g > best_g.get(node.state, float("inf")):
            continue

        nodes_expanded += 1
        ps = PuzzleState(node.state)

        for ns, action, cost in ps.get_neighbors(action_order):
            if time.perf_counter() - t0 > timeout:
                return _make_result(False, "UCS", None, start, goal, nodes_expanded, nodes_generated, max_frontier, len(best_g), t0, trace, "Timeout", True, True)

            new_g = node.g + cost
            if new_g < best_g.get(ns, float("inf")):
                best_g[ns] = new_g
                child = Node(state=ns, parent=node, action=action, g=new_g, depth=node.depth + 1)
                counter += 1
                heapq.heappush(frontier, (new_g, counter, child))
                nodes_generated += 1
                max_frontier = max(max_frontier, len(frontier))

                if len(trace) < 200:
                    trace.append(TraceStep(
                        step=nodes_expanded, state=ns, action=action,
                        g=new_g, h=0, f=new_g,
                        frontier_size=len(frontier), reached_size=len(best_g),
                        node_state=node.state, frontier_states=[n.state for _, _, n in frontier], reached_states=list(best_g.keys()),
                        reason=f"Expand node, g={new_g}",
                    ))

    return _make_result(False, "UCS", None, start, goal, nodes_expanded, nodes_generated, max_frontier, len(best_g), t0, trace, "No solution found", True, True)


def ids(
    start: tuple[int, ...], goal: tuple[int, ...] = GOAL_STATE,
    max_depth: int = 50, max_nodes: int = 50000,
    timeout: float = 60.0, action_order: str = "LRUD",
) -> SearchResult:
    """Iterative Deepening Search. Optimal for unit cost, low memory."""
    t0 = time.perf_counter()
    if start == goal:
        return _make_result(True, "IDS", None, start, goal, 0, 0, 0, 0, t0, [], "Already at goal", True, True)

    total_expanded = 0
    total_generated = 0
    total_max_frontier = 0
    trace: list[TraceStep] = []

    for depth_limit in range(max_depth + 1):
        if time.perf_counter() - t0 > timeout:
            return SearchResult(
                success=False, algorithm="IDS", group="Uninformed Search",
                nodes_expanded=total_expanded, nodes_generated=total_generated,
                max_frontier_size=total_max_frontier, runtime=time.perf_counter() - t0,
                message="Timeout", trace=trace, is_complete=True, is_optimal=True,
            )
        if total_expanded > max_nodes:
            return SearchResult(
                success=False, algorithm="IDS", group="Uninformed Search",
                nodes_expanded=total_expanded, nodes_generated=total_generated,
                max_frontier_size=total_max_frontier, runtime=time.perf_counter() - t0,
                message=f"Node limit exceeded ({max_nodes})", trace=trace, is_complete=True, is_optimal=True,
            )

        result = _dls(start, goal, depth_limit, action_order, t0, timeout, total_expanded, total_generated, total_max_frontier, trace)

        total_expanded = result.nodes_expanded
        total_generated = result.nodes_generated
        total_max_frontier = max(total_max_frontier, result.max_frontier_size)
        trace = result.trace

        if result.success:
            result.algorithm = "IDS"
            result.group = "Uninformed Search"
            result.is_complete = True
            result.is_optimal = True
            result.runtime = time.perf_counter() - t0
            return result

        if result.message and "depth" not in result.message.lower():
            break

    return SearchResult(
        success=False, algorithm="IDS", group="Uninformed Search",
        nodes_expanded=total_expanded, nodes_generated=total_generated,
        max_frontier_size=total_max_frontier, runtime=time.perf_counter() - t0,
        message=f"No solution found within depth {max_depth}", trace=trace,
        is_complete=True, is_optimal=True,
    )


def _dls(
    start: tuple, goal: tuple, depth_limit: int, action_order: str,
    t0_global: float, timeout: float,
    prev_expanded: int, prev_generated: int, prev_max_frontier: int,
    global_trace: list,
) -> SearchResult:
    """Depth-Limited Search (helper for IDS)."""
    root = Node(state=start, g=0, depth=0)
    stack = [root]
    visited_in_path = set()
    nodes_expanded = prev_expanded
    nodes_generated = prev_generated
    max_frontier = prev_max_frontier
    found_cutoff = False

    while stack:
        if time.perf_counter() - t0_global > timeout:
            return SearchResult(
                success=False, message="Timeout",
                nodes_expanded=nodes_expanded, nodes_generated=nodes_generated,
                max_frontier_size=max_frontier, trace=global_trace,
            )

        node = stack.pop()

        if node.state == goal:
            path = reconstruct_path(node)
            actions = reconstruct_actions(node)
            if len(global_trace) < 200:
                global_trace.append(TraceStep(
                    step=nodes_expanded, state=node.state, action=node.action,
                    g=node.g, h=0, f=node.g, depth_limit=depth_limit,
                    frontier_size=len(stack), reached_size=0,
                    node_state=node.state, frontier_states=[n.state for n in stack], reached_states=[],
                    reason=f"Goal found at depth {node.depth}",
                ))
            return SearchResult(
                success=True, path=path, actions=actions,
                cost=node.g, depth=node.depth,
                nodes_expanded=nodes_expanded, nodes_generated=nodes_generated,
                max_frontier_size=max_frontier, trace=global_trace,
                message=f"Found at depth {node.depth}, limit={depth_limit}",
            )

        if node.depth >= depth_limit:
            found_cutoff = True
            continue

        if node.state in visited_in_path:
            continue
        visited_in_path.add(node.state)
        nodes_expanded += 1

        ps = PuzzleState(node.state)
        neighbors = list(reversed(ps.get_neighbors(action_order)))
        for ns, action, cost in neighbors:
            child = Node(state=ns, parent=node, action=action, g=node.g + cost, depth=node.depth + 1)
            stack.append(child)
            nodes_generated += 1
            max_frontier = max(max_frontier, len(stack))

        visited_in_path.discard(node.state)

        if len(global_trace) < 200:
            global_trace.append(TraceStep(
                step=nodes_expanded, state=node.state, action=node.action,
                g=node.g, h=0, f=node.g, depth_limit=depth_limit,
                frontier_size=len(stack), reached_size=0,
                node_state=node.state, frontier_states=[n.state for n in stack], reached_states=[],
                reason=f"IDS depth_limit={depth_limit}",
            ))

    if found_cutoff:
        return SearchResult(
            success=False, message=f"cutoff at depth {depth_limit}",
            nodes_expanded=nodes_expanded, nodes_generated=nodes_generated,
            max_frontier_size=max_frontier, trace=global_trace,
        )
    return SearchResult(
        success=False, message="No solution at this depth",
        nodes_expanded=nodes_expanded, nodes_generated=nodes_generated,
        max_frontier_size=max_frontier, trace=global_trace,
    )