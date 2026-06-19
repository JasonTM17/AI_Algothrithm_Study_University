"""Group 6: Adversarial / Stochastic Search — Minimax, Alpha-Beta, Expectimax.

Note: 15-puzzle is NOT a two-player game. These algorithms are modeled
as extended versions for academic illustration, treating the puzzle
as a MAX vs MIN game where MIN tries to increase heuristic distance.
"""

import time
import random
import math
from typing import Optional
from core.puzzle import PuzzleState, GOAL_STATE, _move_blank
from core.heuristics import get_heuristic, manhattan_distance
from core.metrics import SearchResult, TraceStep


def _utility(state: tuple[int, ...], goal: tuple[int, ...], solved_bonus: float = 1000.0) -> float:
    """Utility function: +solved_bonus for goal, -Manhattan otherwise."""
    if state == goal:
        return solved_bonus
    return -manhattan_distance(state, goal)


def minimax(
    start: tuple[int, ...], goal: tuple[int, ...] = GOAL_STATE,
    depth: int = 3, heuristic: str = "Manhattan Distance",
    timeout: float = 60.0, action_order: str = "LRUD",
) -> SearchResult:
    """Minimax search treating 15-puzzle as MAX vs MIN game.

    MAX: puzzle solver, wants to minimize heuristic (maximize utility).
    MIN: adversary, wants to maximize heuristic (minimize utility).
    """
    t0 = time.perf_counter()
    h_fn = get_heuristic(heuristic, goal)
    trace: list[TraceStep] = []
    nodes_expanded = [0]

    def minimax_search(state: tuple, depth_left: int, is_max: bool, path: list) -> tuple[float, list, list]:
        nodes_expanded[0] += 1
        if state == goal:
            return 1000.0, [("MAX" if is_max else "MIN", state, 1000.0, h_fn(state))], []

        if depth_left <= 0:
            util = -h_fn(state)
            return util, [("MAX" if is_max else "MIN", state, util, h_fn(state))], []

        ps = PuzzleState(state)
        neighbors = ps.get_neighbors(action_order)

        if not neighbors:
            util = -h_fn(state)
            return util, [("MAX" if is_max else "MIN", state, util, h_fn(state))], []

        if is_max:
            best_val = float("-inf")
            best_action = None
            best_tree = []
            for ns, action, cost in neighbors:
                val, tree, _ = minimax_search(ns, depth_left - 1, False, path + [action])
                if val > best_val:
                    best_val = val
                    best_action = action
                    best_tree = tree

            tree_entry = ("MAX", state, best_val, h_fn(state))
            full_tree = [tree_entry] + best_tree
            return best_val, full_tree, [best_action] if best_action else []

        else:  # MIN
            best_val = float("inf")
            best_action = None
            best_tree = []
            for ns, action, cost in neighbors:
                val, tree, _ = minimax_search(ns, depth_left - 1, True, path + [action])
                if val < best_val:
                    best_val = val
                    best_action = action
                    best_tree = tree

            tree_entry = ("MIN", state, best_val, h_fn(state))
            full_tree = [tree_entry] + best_tree
            return best_val, full_tree, [best_action] if best_action else []

    utility, game_tree, actions = minimax_search(start, depth, True, [])

    # Build trace from game tree
    for i, (node_type, state, util, h) in enumerate(game_tree[:200]):
        trace.append(TraceStep(
            step=i, state=state, node_type=node_type,
            utility=util, h=h,
            reason=f"{node_type}: utility={util:.1f}, h={h:.1f}",
        ))

    # Format game tree as text
    tree_lines = _format_game_tree(start, game_tree[:50], depth)

    solved = start == goal
    msg = f"Minimax (depth={depth})\nBest utility: {utility:.1f}\n"
    msg += f"This is a GAME model: MAX tries to solve, MIN tries to obstruct.\n"
    msg += f"Standard 15-puzzle has NO adversary — this is for illustration only.\n\n"
    msg += f"Game Tree (truncated):\n{tree_lines}"

    return SearchResult(
        success=solved, algorithm="Minimax", group="Adversarial/Stochastic",
        path=[start], actions=actions, cost=len(actions), depth=len(actions),
        nodes_expanded=nodes_expanded[0], nodes_generated=nodes_expanded[0],
        runtime=time.perf_counter() - t0, message=msg, trace=trace,
        uses_adversary=True, is_complete=False, is_optimal=False, suitable_for_puzzle=False,
    )


def _format_game_tree(start: tuple, tree: list, max_depth: int) -> str:
    """Format game tree as text."""
    lines = []
    for i, (node_type, state, util, h) in enumerate(tree[:30]):
        indent = "  " * min(i, max_depth)
        state_short = f"[{state[0]:2d},{state[1]:2d},{state[2]:2d},{state[3]:2d}...]"
        lines.append(f"{indent}{node_type}: h={h:.0f}, util={util:.1f}, state≈{state_short}")
    if len(tree) > 30:
        lines.append(f"  ... ({len(tree) - 30} more nodes)")
    return "\n".join(lines)


def alpha_beta_pruning(
    start: tuple[int, ...], goal: tuple[int, ...] = GOAL_STATE,
    depth: int = 3, heuristic: str = "Manhattan Distance",
    timeout: float = 60.0, action_order: str = "LRUD",
) -> SearchResult:
    """Alpha-Beta Pruning: same as Minimax but prunes branches that can't affect outcome."""
    t0 = time.perf_counter()
    h_fn = get_heuristic(heuristic, goal)
    trace: list[TraceStep] = []
    nodes_expanded = [0]
    pruned = [0]

    def ab_search(state: tuple, depth_left: int, alpha: float, beta: float, is_max: bool) -> tuple[float, list, list]:
        nodes_expanded[0] += 1

        if state == goal:
            return 1000.0, [("MAX" if is_max else "MIN", state, 1000.0, 0)], []

        if depth_left <= 0:
            util = -h_fn(state)
            return util, [("MAX" if is_max else "MIN", state, util, h_fn(state))], []

        ps = PuzzleState(state)
        neighbors = ps.get_neighbors(action_order)

        if not neighbors:
            util = -h_fn(state)
            return util, [("MAX" if is_max else "MIN", state, util, h_fn(state))], []

        if is_max:
            best_val = float("-inf")
            best_tree = []
            best_actions = []
            for ns, action, cost in neighbors:
                val, tree, acts = ab_search(ns, depth_left - 1, alpha, beta, False)
                if val > best_val:
                    best_val = val
                    best_tree = tree
                    best_actions = [action]
                alpha = max(alpha, val)
                if beta <= alpha:
                    pruned[0] += 1
                    if len(trace) < 200:
                        trace.append(TraceStep(
                            step=nodes_expanded[0], state=ns, action=action,
                            node_type="MAX", alpha=alpha, beta=beta,
                            reason=f"PRUNE: β({beta:.1f})≤α({alpha:.1f})"))
                    break  # Beta cutoff
            tree_entry = ("MAX", state, best_val, h_fn(state))
            return best_val, [tree_entry] + best_tree, best_actions
        else:
            best_val = float("inf")
            best_tree = []
            best_actions = []
            for ns, action, cost in neighbors:
                val, tree, acts = ab_search(ns, depth_left - 1, alpha, beta, True)
                if val < best_val:
                    best_val = val
                    best_tree = tree
                    best_actions = [action]
                beta = min(beta, val)
                if beta <= alpha:
                    pruned[0] += 1
                    if len(trace) < 200:
                        trace.append(TraceStep(
                            step=nodes_expanded[0], state=ns, action=action,
                            node_type="MIN", alpha=alpha, beta=beta,
                            reason=f"PRUNE: β({beta:.1f})≤α({alpha:.1f})"))
                    break  # Alpha cutoff
            tree_entry = ("MIN", state, best_val, h_fn(state))
            return best_val, [tree_entry] + best_tree, best_actions

    utility, game_tree, actions = ab_search(start, depth, float("-inf"), float("inf"), True)

    # Add non-pruning trace entries
    for i, (node_type, state, util, h) in enumerate(game_tree[:100]):
        trace.append(TraceStep(
            step=i, state=state, node_type=node_type,
            utility=util, h=h,
            reason=f"{node_type}: utility={util:.1f}, h={h:.1f}"))

    tree_text = _format_game_tree(start, game_tree[:50], depth)

    msg = f"Alpha-Beta Pruning (depth={depth})\n"
    msg += f"Best utility: {utility:.1f}\n"
    msg += f"Nodes expanded: {nodes_expanded[0]}\n"
    msg += f"Branches pruned: {pruned[0]}\n"
    msg += f"Alpha-Beta gives SAME result as Minimax but visits fewer nodes.\n\n"
    msg += f"Game Tree (truncated):\n{tree_text}"

    solved = start == goal
    return SearchResult(
        success=solved, algorithm="Alpha-Beta Pruning", group="Adversarial/Stochastic",
        path=[start], actions=actions, cost=len(actions), depth=len(actions),
        nodes_expanded=nodes_expanded[0], nodes_generated=nodes_expanded[0],
        runtime=time.perf_counter() - t0, message=msg, trace=trace,
        uses_adversary=True, is_complete=False, is_optimal=False, suitable_for_puzzle=False,
    )


def expectimax(
    start: tuple[int, ...], goal: tuple[int, ...] = GOAL_STATE,
    depth: int = 3, heuristic: str = "Manhattan Distance",
    success_prob: float = 0.8, timeout: float = 60.0,
    action_order: str = "LRUD", seed: Optional[int] = None,
) -> SearchResult:
    """Expectimax: MAX chooses action, CHANCE node computes expected value.

    Models stochastic 15-puzzle where action has success_prob chance of
    executing correctly, with remaining probability split among other valid moves.
    """
    t0 = time.perf_counter()
    h_fn = get_heuristic(heuristic, goal)
    rng = random.Random(seed)
    trace: list[TraceStep] = []
    nodes_expanded = [0]

    def get_outcomes(state: tuple, action: str) -> list[tuple[tuple, str, float]]:
        """Return (new_state, actual_action, probability) for stochastic action."""
        results = []
        intended = _move_blank(state, action)
        if intended is None:
            return []

        intended_prob = success_prob
        remaining = 1.0 - intended_prob
        other_actions = [a for a in action_order if a != action and _move_blank(state, a) is not None]

        if other_actions:
            other_prob = remaining / len(other_actions)
            results.append((intended, action, intended_prob))
            for alt in other_actions:
                ns = _move_blank(state, alt)
                if ns is not None:
                    results.append((ns, alt, other_prob))
        else:
            results.append((intended, action, 1.0))

        return results

    def expectimax_search(state: tuple, depth_left: int, node_type: str = "MAX", action_taken: Optional[str] = None) -> tuple[float, list]:
        """Returns (expected_utility, tree_nodes)."""
        nodes_expanded[0] += 1

        if state == goal:
            util = 1000.0
            h = 0
            node = (node_type, state, util, h, 1.0)
            return util, [node]

        if depth_left <= 0:
            util = -h_fn(state)
            h = h_fn(state)
            node = (node_type, state, util, h, 1.0)
            return util, [node]

        ps = PuzzleState(state)

        if node_type == "MAX":
            best_val = float("-inf")
            best_tree = []
            best_action = None
            neighbors = ps.get_neighbors(action_order)

            for ns, action, cost in neighbors:
                # Call CHANCE node to compute expected utility of this action
                val, tree = expectimax_search(state, depth_left, "CHANCE", action_taken=action)
                if val > best_val:
                    best_val = val
                    best_action = action
                    best_tree = tree

                if len(trace) < 200:
                    trace.append(TraceStep(
                        step=nodes_expanded[0], state=ns, action=action,
                        node_type="MAX", utility=val, h=h_fn(ns),
                        probability=success_prob,
                        reason=f"MAX: action={action}, ev={val:.1f}"))

            h = h_fn(state)
            node = ("MAX", state, best_val, h, 1.0)
            return best_val, [node] + best_tree

        elif node_type == "CHANCE":
            # CHANCE node: computes expected value over outcomes of action_taken at state
            outcomes = get_outcomes(state, action_taken)
            if not outcomes:
                util = -h_fn(state)
                node = ("CHANCE", state, util, h_fn(state), 1.0)
                return util, [node]

            expected_value = 0.0
            children_trees = []
            for out_state, out_action, prob in outcomes:
                # Call MAX recursively on the outcome state
                val, tree = expectimax_search(out_state, depth_left - 1, "MAX")
                expected_value += prob * val
                children_trees.extend(tree)

                if len(trace) < 200:
                    trace.append(TraceStep(
                        step=nodes_expanded[0], state=out_state, action=out_action,
                        node_type="CHANCE", utility=val, h=h_fn(out_state),
                        probability=prob,
                        reason=f"CHANCE: P({out_action})={prob:.2f}, ev={val:.1f}"))

            h = h_fn(state)
            node = ("CHANCE", state, expected_value, h, 1.0)
            return expected_value, [node] + children_trees

        return 0, []

    utility, game_tree = expectimax_search(start, depth, "MAX")

    tree_text = ""
    for i, node_data in enumerate(game_tree[:30]):
        if len(node_data) == 5:
            ntype, state, util, h, prob = node_data
            prob_str = f", P={prob:.2f}" if prob and ntype == "CHANCE" else ""
            tree_text += f"{'  ' * min(i, depth)}{ntype}: h={h:.0f}, ev={util:.1f}{prob_str}\n"

    msg = f"Expectimax (depth={depth}, success_prob={success_prob})\n"
    msg += f"Expected utility from start: {utility:.1f}\n"
    msg += f"Nodes expanded: {nodes_expanded[0]}\n\n"
    msg += f"Comparison with Minimax:\n"
    msg += f"  Minimax: assumes WORST outcome (adversarial)\n"
    msg += f"  Expectimax: computes EXPECTED outcome (probabilistic)\n"
    msg += f"  Result differs when success_prob < 1.0\n\n"
    msg += f"Game Tree (truncated):\n{tree_text}"

    # Determine actions based on the path taken in game tree
    # Since MAX starts at the root, the next node is CHANCE, and then the outcomes are MAX.
    # The action is stored in the trace or we can reconstruct it from the tree.
    actions = []
    # Reconstruct chosen actions path from the game_tree
    current_idx = 0
    # Walk the game tree to extract MAX actions
    while current_idx < len(game_tree):
        node = game_tree[current_idx]
        if node[0] == "MAX":
            # Find the best action taken at this state
            # In our search, we can check trace steps or transition
            state_val = node[1]
            ps = PuzzleState(state_val)
            # Find next MAX node in the tree and find the transition
            next_max_node = None
            for idx in range(current_idx + 1, len(game_tree)):
                if game_tree[idx][0] == "MAX":
                    next_max_node = game_tree[idx]
                    break
            if next_max_node:
                next_state = next_max_node[1]
                # Check how to transition from state_val to next_state
                for ns, action, cost in ps.get_neighbors(action_order):
                    # Check if next_state is in the outcomes of this action
                    outcomes = get_outcomes(state_val, action)
                    if any(o[0] == next_state for o in outcomes):
                        actions.append(action)
                        break
                current_idx = idx
            else:
                break
        else:
            current_idx += 1

    solved = start == goal
    return SearchResult(
        success=solved, algorithm="Expectimax", group="Adversarial/Stochastic",
        path=[start], actions=actions, cost=len(actions), depth=len(actions),
        nodes_expanded=nodes_expanded[0], nodes_generated=nodes_expanded[0],
        runtime=time.perf_counter() - t0, message=msg, trace=trace,
        uses_adversary=True, uses_probability=True,
        is_complete=False, is_optimal=False, suitable_for_puzzle=False,
    )
