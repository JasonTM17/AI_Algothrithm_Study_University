"""Group 6: game-tree robustness / stochastic search.

Note: 15-puzzle is NOT a two-player game. Minimax and Alpha-Beta are
shown as worst-case robustness analysis over legal puzzle continuations:
MAX picks the most promising move, while MIN asks what happens if every
subsequent legal move is the worst for the heuristic. In a true
two-player game MIN would have its own action set; here both sides share
blank-tile moves because the puzzle has no natural adversary.
"""

import time
import random
from typing import Optional
from core.puzzle import PuzzleState, GOAL_STATE, _move_blank
from core.heuristics import get_heuristic, manhattan_distance
from core.metrics import SearchResult, TraceStep


def _utility(state: tuple[int, ...], goal: tuple[int, ...], solved_bonus: float = 1000.0) -> float:
    """Utility function: +solved_bonus for goal, -Manhattan otherwise."""
    if state == goal:
        return solved_bonus
    return -manhattan_distance(state, goal)


def _path_from_actions(start: tuple[int, ...], actions: list[str]) -> list[tuple[int, ...]]:
    path = [start]
    current = start
    for action in actions:
        next_state = _move_blank(current, action)
        if next_state is None:
            break
        path.append(next_state)
        current = next_state
    return path


def _append_root_summary(
    trace: list[TraceStep],
    *,
    state: tuple[int, ...],
    utility: float,
    depth: int,
    node_type: str = "MAX",
) -> None:
    """Record the backed-up root value as structured evidence."""
    trace.append(
        TraceStep(
            step=0,
            state=state,
            node_type=node_type,
            utility=utility,
            depth=0,
            depth_limit=depth,
            event="root_summary",
            node_id="pv-0",
            reason=f"Root {node_type} value={utility:.1f} at depth={depth}",
        )
    )


def _append_worst_case_variation(
    trace: list[TraceStep],
    *,
    path: list[tuple[int, ...]],
    actions: list[str],
    game_tree: list,
    depth: int,
) -> None:
    """Record the selected MAX/MIN variation without inventing a solution tree."""
    if not path:
        return
    for index, action in enumerate(actions):
        before = path[index]
        after = path[index + 1]
        role = "MAX" if index % 2 == 0 else "MIN"
        event = "select_action" if role == "MAX" else "worst_case"
        utility = None
        if index < len(game_tree):
            entry = game_tree[index]
            if isinstance(entry, tuple) and len(entry) >= 3:
                utility = float(entry[2])
        trace.append(
            TraceStep(
                step=index + 1,
                state=after,
                node_state=before,
                action=action,
                intended_action=action,
                realized_action=action,
                node_type=role,
                utility=utility,
                depth=index + 1,
                depth_limit=depth,
                event=event,
                node_id=f"pv-{index + 1}",
                parent_id=f"pv-{index}",
                reason=(
                    f"{role} selected legal action {action}"
                    if role == "MAX"
                    else f"MIN selected worst-case legal continuation {action}"
                ),
            )
        )


def minimax(
    start: tuple[int, ...], goal: tuple[int, ...] = GOAL_STATE,
    depth: int = 3, heuristic: str = "Manhattan Distance",
    timeout: float = 60.0, action_order: str = "LRUD",
) -> SearchResult:
    """Minimax search as worst-case robustness analysis.

    MAX: solver selecting the most promising legal move.
    MIN: worst-case branch selecting legal continuations that maximize
    heuristic damage. This is not a real opponent in the 15-puzzle.
    """
    t0 = time.perf_counter()
    h_fn = get_heuristic(heuristic, goal)
    trace: list[TraceStep] = []
    nodes_expanded = [0]
    nodes_generated = [1]
    timed_out = [False]

    def minimax_search(state: tuple, depth_left: int, is_max: bool, path: list) -> tuple[float, list, list]:
        if time.perf_counter() - t0 > timeout:
            timed_out[0] = True
            util = -h_fn(state)
            return util, [("MAX" if is_max else "MIN", state, util, h_fn(state))], []
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
            best_child_actions = []
            for ns, action, cost in neighbors:
                nodes_generated[0] += 1
                val, tree, child_actions = minimax_search(ns, depth_left - 1, False, path + [action])
                if val > best_val:
                    best_val = val
                    best_action = action
                    best_tree = tree
                    best_child_actions = child_actions

            tree_entry = ("MAX", state, best_val, h_fn(state))
            full_tree = [tree_entry] + best_tree
            return best_val, full_tree, ([best_action] + best_child_actions) if best_action else []

        else:  # MIN
            best_val = float("inf")
            best_action = None
            best_tree = []
            best_child_actions = []
            for ns, action, cost in neighbors:
                nodes_generated[0] += 1
                val, tree, child_actions = minimax_search(ns, depth_left - 1, True, path + [action])
                if val < best_val:
                    best_val = val
                    best_action = action
                    best_tree = tree
                    best_child_actions = child_actions

            tree_entry = ("MIN", state, best_val, h_fn(state))
            full_tree = [tree_entry] + best_tree
            return best_val, full_tree, ([best_action] + best_child_actions) if best_action else []

    utility, game_tree, actions = minimax_search(start, depth, True, [])

    # Build trace from game tree
    for i, (node_type, state, util, h) in enumerate(game_tree[:200]):
        trace.append(TraceStep(
            step=i, state=state, node_type=node_type,
            utility=util, h=h,
            reason=f"{node_type}: utility={util:.1f}, h={h:.1f}",
        ))

    # Format game tree as text
    tree_lines = _format_principal_variation(game_tree[:50], depth)

    status = "Timeout: partial depth-limited evaluation" if timed_out[0] else f"Completed depth {depth}"
    msg = f"Minimax (depth={depth})\n{status}\nBest utility: {utility:.1f}\n"
    msg += "MAX selects the most promising legal move.\n"
    msg += "MIN branch models worst-case legal continuations, not a real opponent.\n"
    msg += "Standard 15-puzzle has no natural adversary; this is robustness analysis.\n"
    msg += "Returned actions are the selected variation, not an optimality certificate for the standard puzzle.\n\n"
    msg += f"Principal variation (not the full evaluated tree):\n{tree_lines}"

    selected_path = _path_from_actions(start, actions)
    _append_root_summary(
        trace, state=start, utility=utility, depth=depth, node_type="MAX"
    )
    _append_worst_case_variation(
        trace,
        path=selected_path,
        actions=actions,
        game_tree=game_tree,
        depth=depth,
    )
    solved = bool(selected_path and selected_path[-1] == goal and not timed_out[0])
    return SearchResult(
        success=solved, algorithm="Minimax", group="AI-vs-AI Tournament",
        path=selected_path, actions=actions, goal_state=goal,
        cost=len(actions), depth=len(actions),
        nodes_expanded=nodes_expanded[0], nodes_generated=nodes_generated[0],
        runtime=time.perf_counter() - t0, message=msg, trace=trace,
        termination_reason=(
            "goal" if solved else "timeout" if timed_out[0] else "depth_limit"
        ),
        uses_adversary=True, is_complete=False, is_optimal=False, suitable_for_puzzle=False,
    )


def _format_principal_variation(tree: list, max_depth: int) -> str:
    """Format the selected root-to-leaf variation, not a full game tree."""
    lines = []
    for i, entry in enumerate(tree[:30]):
        if not isinstance(entry, tuple) or len(entry) < 4:
            continue
        node_type, state, util, h = entry[0], entry[1], entry[2], entry[3]
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
    """Alpha-Beta Pruning over the same worst-case tree as Minimax."""
    t0 = time.perf_counter()
    h_fn = get_heuristic(heuristic, goal)
    trace: list[TraceStep] = []
    nodes_expanded = [0]
    nodes_generated = [1]
    pruned = [0]
    timed_out = [False]

    def ab_search(state: tuple, depth_left: int, alpha: float, beta: float, is_max: bool) -> tuple[float, list, list]:
        if time.perf_counter() - t0 > timeout:
            timed_out[0] = True
            util = -h_fn(state)
            return util, [("MAX" if is_max else "MIN", state, util, h_fn(state), [])], []
        nodes_expanded[0] += 1

        if state == goal:
            return 1000.0, [("MAX" if is_max else "MIN", state, 1000.0, h_fn(state), [])], []

        if depth_left <= 0:
            util = -h_fn(state)
            return util, [("MAX" if is_max else "MIN", state, util, h_fn(state), [])], []

        ps = PuzzleState(state)
        neighbors = ps.get_neighbors(action_order)

        if not neighbors:
            util = -h_fn(state)
            return util, [("MAX" if is_max else "MIN", state, util, h_fn(state), [])], []

        if is_max:
            best_val = float("-inf")
            best_tree = []
            best_actions = []
            children = []
            for ns, action, cost in neighbors:
                nodes_generated[0] += 1
                val, tree, acts = ab_search(ns, depth_left - 1, alpha, beta, False)
                children.append(tree)
                if val > best_val:
                    best_val = val
                    best_tree = tree
                    best_actions = [action] + acts
                alpha = max(alpha, val)
                if beta <= alpha:
                    pruned[0] += 1
                    if len(trace) < 200:
                        trace.append(TraceStep(
                            step=nodes_expanded[0], state=ns, action=action,
                            node_type="MAX", alpha=alpha, beta=beta,
                            event="prune",
                            reason=f"PRUNE: β({beta:.1f})≤α({alpha:.1f})"))
                    break
            tree_entry = ("MAX", state, best_val, h_fn(state), children)
            return best_val, [tree_entry] + best_tree, best_actions
        else:
            best_val = float("inf")
            best_tree = []
            best_actions = []
            children = []
            for ns, action, cost in neighbors:
                nodes_generated[0] += 1
                val, tree, acts = ab_search(ns, depth_left - 1, alpha, beta, True)
                children.append(tree)
                if val < best_val:
                    best_val = val
                    best_tree = tree
                    best_actions = [action] + acts
                beta = min(beta, val)
                if beta <= alpha:
                    pruned[0] += 1
                    if len(trace) < 200:
                        trace.append(TraceStep(
                            step=nodes_expanded[0], state=ns, action=action,
                            node_type="MIN", alpha=alpha, beta=beta,
                            event="prune",
                            reason=f"PRUNE: β({beta:.1f})≤α({alpha:.1f})"))
                    break
            tree_entry = ("MIN", state, best_val, h_fn(state), children)
            return best_val, [tree_entry] + best_tree, best_actions

    utility, game_tree, actions = ab_search(start, depth, float("-inf"), float("inf"), True)

    # Flatten the full tree (with all explored siblings) into trace entries
    def _flatten_tree(tree: list, step_counter: list[int]) -> None:
        for entry in tree:
            if not isinstance(entry, tuple) or len(entry) < 4:
                continue
            node_type, st, util, h = entry[0], entry[1], entry[2], entry[3]
            children = entry[4] if len(entry) > 4 else []
            step_counter[0] += 1
            if len(trace) < 200:
                trace.append(TraceStep(
                    step=step_counter[0], state=st, node_type=node_type,
                    utility=util, h=h,
                    reason=f"{node_type}: utility={util:.1f}, h={h:.1f}"))
            _flatten_tree(children, step_counter)

    _flatten_tree(game_tree, [0])

    tree_text = _format_principal_variation(game_tree[:50], depth)

    status = "Timeout: partial depth-limited evaluation" if timed_out[0] else f"Completed depth {depth}"
    msg = f"Alpha-Beta Pruning (depth={depth})\n{status}\n"
    msg += f"Best utility: {utility:.1f}\n"
    msg += f"Nodes expanded: {nodes_expanded[0]}\n"
    msg += f"Cutoff events: {pruned[0]}\n"
    msg += "MIN branch models worst-case legal continuations, not a real opponent.\n"
    msg += "With identical ordering, no timeout, and a completed depth, Alpha-Beta preserves the same root value as Minimax under the same fully searched worst-case tree.\n\n"
    msg += "Returned actions are the selected variation, not an optimality certificate for the standard puzzle.\n\n"
    msg += f"Principal variation (not the full evaluated tree):\n{tree_text}"

    selected_path = _path_from_actions(start, actions)
    _append_root_summary(
        trace, state=start, utility=utility, depth=depth, node_type="MAX"
    )
    _append_worst_case_variation(
        trace,
        path=selected_path,
        actions=actions,
        game_tree=game_tree,
        depth=depth,
    )
    solved = bool(selected_path and selected_path[-1] == goal and not timed_out[0])
    return SearchResult(
        success=solved, algorithm="Alpha-Beta Pruning", group="AI-vs-AI Tournament",
        path=selected_path, actions=actions, goal_state=goal,
        cost=len(actions), depth=len(actions),
        nodes_expanded=nodes_expanded[0], nodes_generated=nodes_generated[0],
        runtime=time.perf_counter() - t0, message=msg, trace=trace,
        termination_reason=(
            "goal" if solved else "timeout" if timed_out[0] else "depth_limit"
        ),
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
    if not 0.0 <= success_prob <= 1.0:
        raise ValueError("success_prob must be between 0 and 1")
    h_fn = get_heuristic(heuristic, goal)
    rng = random.Random(seed)
    trace: list[TraceStep] = []
    nodes_expanded = [0]
    nodes_generated = [1]
    timed_out = [False]
    chance_calls = [0]

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

    def expectimax_search(
        state: tuple, depth_left: int, node_type: str = "MAX",
        action_taken: Optional[str] = None,
    ) -> tuple[float, list, list[str], list[tuple[str, str, float, float]]]:
        """Return expected utility, displayed subtree, and one legal sample path.

        The sample path is not a deterministic guarantee in a stochastic model; it
        samples one outcome according to its probability at each chance node so
        the UI can display a seeded, auditable trajectory without pretending it
        is the full stochastic policy.
        """
        if time.perf_counter() - t0 > timeout:
            timed_out[0] = True
            util = -h_fn(state)
            return util, [(node_type, state, util, h_fn(state), 1.0)], [], []
        if state == goal:
            util = 1000.0
            h = 0
            node = (node_type, state, util, h, 1.0)
            return util, [node], [], []

        if depth_left <= 0 and node_type != "CHANCE":
            util = -h_fn(state)
            h = h_fn(state)
            node = (node_type, state, util, h, 1.0)
            return util, [node], [], []

        ps = PuzzleState(state)
        nodes_expanded[0] += 1

        if node_type == "MAX":
            best_val = float("-inf")
            best_tree = []
            best_actions: list[str] = []
            best_details: list[tuple[str, str, float, float]] = []
            neighbors = ps.get_neighbors(action_order)

            for ns, action, cost in neighbors:
                nodes_generated[0] += 1
                # Call CHANCE node to compute expected utility of this action
                val, tree, child_actions, child_details = expectimax_search(
                    state, depth_left - 1, "CHANCE", action_taken=action
                )
                if val > best_val:
                    best_val = val
                    best_tree = tree
                    best_actions = child_actions
                    best_details = child_details

                if len(trace) < 200:
                    trace.append(TraceStep(
                        step=nodes_expanded[0], state=ns, action=action,
                        node_state=state,
                        node_type="MAX", utility=val, h=h_fn(ns),
                        probability=success_prob,
                        intended_action=action,
                        event="evaluate_action",
                        reason=f"MAX: action={action}, ev={val:.1f}"))

            h = h_fn(state)
            node = ("MAX", state, best_val, h, 1.0)
            return best_val, [node] + best_tree, best_actions, best_details

        elif node_type == "CHANCE":
            # CHANCE node: computes expected value over outcomes of action_taken at state
            chance_calls[0] += 1
            chance_node_id = f"chance-{chance_calls[0]}"
            outcomes = get_outcomes(state, action_taken)
            if not outcomes:
                util = -h_fn(state)
                node = ("CHANCE", state, util, h_fn(state), 1.0)
                return util, [node], [], []

            expected_value = 0.0
            children_trees = []
            capture_outcomes = len(trace) + len(outcomes) <= 200
            sample_candidates: list[
                tuple[
                    float,
                    str,
                    float,
                    list[str],
                    list[tuple[str, str, float, float]],
                ]
            ] = []
            for out_state, out_action, prob in outcomes:
                nodes_generated[0] += 1
                # Call MAX recursively on the outcome state
                val, tree, child_actions, child_details = expectimax_search(
                    out_state, depth_left - 1, "MAX"
                )
                expected_value += prob * val
                children_trees.extend(tree)
                sample_candidates.append(
                    (prob, out_action, val, child_actions, child_details)
                )

                if capture_outcomes:
                    trace.append(TraceStep(
                        step=nodes_expanded[0], state=out_state, action=out_action,
                        node_state=state,
                        node_type="CHANCE", utility=val, h=h_fn(out_state),
                        probability=prob,
                        intended_action=action_taken,
                        realized_action=out_action,
                        event="chance_outcome_evaluated",
                        node_id=chance_node_id,
                        reason=f"CHANCE: P({out_action})={prob:.2f}, ev={val:.1f}"))

            draw = rng.random()
            cumulative = 0.0
            sample_actions: list[str] = []
            sample_details: list[tuple[str, str, float, float]] = []
            for prob, out_action, outcome_value, child_actions, child_details in sample_candidates:
                cumulative += prob
                if draw < cumulative:
                    sample_actions = [out_action] + child_actions
                    sample_details = [
                        (str(action_taken), out_action, prob, outcome_value)
                    ] + child_details
                    break
            if not sample_actions and sample_candidates:
                prob, out_action, outcome_value, child_actions, child_details = sample_candidates[-1]
                sample_actions = [out_action] + child_actions
                sample_details = [
                    (str(action_taken), out_action, prob, outcome_value)
                ] + child_details

            h = h_fn(state)
            node = ("CHANCE", state, expected_value, h, 1.0)
            return expected_value, [node] + children_trees, sample_actions, sample_details

        return 0, [], [], []

    utility, game_tree, actions, sampled_details = expectimax_search(
        start, depth, "MAX"
    )

    tree_text = ""
    for i, node_data in enumerate(game_tree[:30]):
        if len(node_data) == 5:
            ntype, state, util, h, prob = node_data
            prob_str = f", P={prob:.2f}" if prob and ntype == "CHANCE" else ""
            tree_text += f"{'  ' * min(i, depth)}{ntype}: h={h:.0f}, ev={util:.1f}{prob_str}\n"

    status = "Timeout: partial depth-limited evaluation" if timed_out[0] else f"Completed depth {depth}"
    msg = f"Expectimax (depth={depth}, success_prob={success_prob})\n{status}\n"
    msg += f"Expected utility from start: {utility:.1f}\n"
    msg += f"Nodes expanded: {nodes_expanded[0]}\n\n"
    msg += f"Comparison with Minimax:\n"
    msg += f"  Minimax: evaluates WORST-CASE legal continuations\n"
    msg += f"  Expectimax: computes EXPECTED outcome with CHANCE nodes\n"
    msg += f"  Result differs when success_prob < 1.0\n\n"
    msg += "Returned actions are one seeded probability-sampled outcome path, not the full stochastic policy.\n\n"
    msg += f"Selected policy subtree (truncated, not the full evaluated tree):\n{tree_text}"

    selected_path = _path_from_actions(start, actions)
    _append_root_summary(
        trace, state=start, utility=utility, depth=depth, node_type="MAX"
    )
    for index, action in enumerate(actions):
        before = selected_path[index]
        after = selected_path[index + 1]
        intended, realized, probability, outcome_value = (
            sampled_details[index]
            if index < len(sampled_details)
            else (action, action, 1.0, float(-h_fn(after)))
        )
        trace.append(
            TraceStep(
                step=index + 1,
                state=after,
                node_state=before,
                action=realized,
                intended_action=intended,
                realized_action=realized,
                node_type="CHANCE",
                utility=outcome_value,
                h=h_fn(after),
                probability=probability,
                depth=index + 1,
                depth_limit=depth,
                event="chance_outcome",
                node_id=f"pv-{index + 1}",
                parent_id=f"pv-{index}",
                reason=(
                    f"MAX intended {intended}; CHANCE realized {realized} "
                    f"with P={probability:.2f}"
                ),
            )
        )
    solved = bool(selected_path and selected_path[-1] == goal and not timed_out[0])
    return SearchResult(
        success=solved, algorithm="Expectimax", group="AI-vs-AI Tournament",
        path=selected_path, actions=actions, goal_state=goal,
        cost=len(actions), depth=len(actions), random_seed=seed,
        nodes_expanded=nodes_expanded[0], nodes_generated=nodes_generated[0],
        runtime=time.perf_counter() - t0, message=msg, trace=trace,
        termination_reason=(
            "goal" if solved else "timeout" if timed_out[0] else "depth_limit"
        ),
        uses_adversary=False, uses_probability=True, uses_randomness=True,
        is_complete=False, is_optimal=False, suitable_for_puzzle=False,
    )
