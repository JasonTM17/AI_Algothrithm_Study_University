"""Search result dataclass."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class TraceStep:
    """Single step in search trace."""
    step: int
    state: tuple[int, ...]
    action: Optional[str] = None
    g: Optional[int] = None
    h: Optional[float] = None
    f: Optional[float] = None
    frontier_size: int = 0
    reached_size: int = 0
    reason: str = ""
    event: str = "generate"
    node_id: Optional[str] = None
    parent_id: Optional[str] = None
    depth: int = 0
    # For special algorithms
    depth_limit: Optional[int] = None
    threshold: Optional[float] = None
    # Local search fields
    current_h: float = 0.0
    candidate_h: Optional[float] = None
    temperature: Optional[float] = None
    probability: Optional[float] = None
    accepted: Optional[bool] = None
    # Complex env fields
    belief_size: Optional[int] = None
    observation: Optional[str] = None
    # Adversarial fields
    node_type: Optional[str] = None  # "MAX", "MIN", "CHANCE"
    alpha: Optional[float] = None
    beta: Optional[float] = None
    utility: Optional[float] = None
    intended_action: Optional[str] = None
    realized_action: Optional[str] = None
    # Search visualization fields
    node_state: Optional[tuple] = None
    frontier_states: Optional[list[tuple]] = None
    reached_states: Optional[list[tuple]] = None


@dataclass
class SearchTreeNode:
    """One auditable node in the bounded visualization graph."""
    node_id: str
    state: tuple[int, ...]
    depth: int
    g: float
    h: Optional[float]
    f: Optional[float]
    on_solution_path: bool = False


@dataclass
class SearchTreeEdge:
    """A legal parent-child transition in the visualization graph."""
    parent_id: str
    child_id: str
    action: str
    on_solution_path: bool = False


@dataclass
class SearchResult:
    """Result of a search algorithm run."""
    success: bool = False
    algorithm: str = ""
    group: str = ""
    path: list[tuple[int, ...]] = field(default_factory=list)
    actions: list[str] = field(default_factory=list)
    goal_state: Optional[tuple[int, ...]] = None
    cost: int = 0
    depth: int = 0
    nodes_expanded: int = 0
    nodes_generated: int = 0
    max_frontier_size: int = 0
    reached_size: int = 0
    runtime: float = 0.0
    random_seed: Optional[int] = None
    variation_action_order: Optional[str] = None
    variation_tie_breaker: Optional[str] = None
    variation_solver_seed: Optional[int] = None
    variation_randomizes_path: bool = True
    message: str = ""
    capability: str = ""
    model_evidence: dict[str, object] = field(default_factory=dict)
    trace: list[TraceStep] = field(default_factory=list)
    search_tree_nodes: list[SearchTreeNode] = field(default_factory=list)
    search_tree_edges: list[SearchTreeEdge] = field(default_factory=list)
    trace_truncated: bool = False
    trace_total_events: int = 0
    path_verified: bool = False
    goal_reached: bool = False
    verification_message: str = ""
    termination_reason: str = ""
    optimality_proven: bool = False
    exhaustive_failure: bool = False

    # Algorithm properties
    is_complete: bool = False
    is_optimal: bool = False
    uses_heuristic: bool = False
    uses_randomness: bool = False
    uses_adversary: bool = False
    uses_probability: bool = False
    suitable_for_puzzle: bool = True

    def __post_init__(self) -> None:
        self.trace_total_events = max(self.trace_total_events, len(self.trace))
        self.trace_truncated = self.trace_truncated or len(self.trace) >= 200
        self._verify_path_evidence()
        self._classify_run_outcome()
        if not self.search_tree_nodes:
            self._build_search_tree_evidence()

    def refresh_certificate(self) -> None:
        """Recompute derived evidence after an iterative wrapper sets guarantees."""
        self._verify_path_evidence()
        if self.termination_reason in {"goal", "model_success"}:
            self.termination_reason = ""
        self._classify_run_outcome()

    def _verify_path_evidence(self) -> None:
        self.path_verified = False
        self.goal_reached = False
        self.verification_message = ""
        if not self.path:
            return
        from core.puzzle import _move_blank

        if len(self.path) != len(self.actions) + 1:
            self.path_verified = False
            self.verification_message = "Path must contain exactly one more state than actions"
            return
        for index, action in enumerate(self.actions):
            expected = _move_blank(self.path[index], action)
            if expected is None:
                self.path_verified = False
                self.verification_message = f"Action {action} is illegal at step {index + 1}"
                return
            if expected != self.path[index + 1]:
                self.path_verified = False
                self.verification_message = (
                    f"Recorded state does not match action {action} at step {index + 1}"
                )
                return
        self.goal_reached = self.goal_state is not None and self.path[-1] == self.goal_state
        self.path_verified = True
        if self.goal_state is None:
            self.verification_message = (
                "Path is a legal state/action sequence; requested goal was not reported"
            )
        elif self.goal_reached:
            self.verification_message = (
                "Path is a legal state/action sequence ending at the requested goal"
            )
        else:
            self.verification_message = (
                "Path is legal, but its final state does not match the requested goal"
            )

    def _classify_run_outcome(self) -> None:
        message = (self.message or "").lower()
        if not self.termination_reason:
            if self.success:
                self.termination_reason = "goal" if self.goal_reached else "model_success"
            elif "timeout" in message:
                self.termination_reason = "timeout"
            elif "node limit" in message or "max steps" in message:
                self.termination_reason = "resource_limit"
            elif "depth" in message or "threshold" in message or "horizon" in message:
                self.termination_reason = "depth_limit"
            elif "no solution" in message:
                self.termination_reason = "exhausted"
            else:
                self.termination_reason = "stopped"
        self.optimality_proven = bool(
            self.success
            and self.is_optimal
            and self.path_verified
            and self.goal_reached
            and self.termination_reason == "goal"
        )
        self.exhaustive_failure = bool(
            not self.success and self.is_complete and self.termination_reason == "exhausted"
        )

    def _build_search_tree_evidence(self) -> None:
        from core.puzzle import _move_blank

        def is_puzzle_state(value: object) -> bool:
            return isinstance(value, tuple) and len(value) == 16 and set(value) == set(range(16))

        states: dict[tuple[int, ...], SearchTreeNode] = {}
        recorded_path = (
            self.path
            if self.path_verified and all(is_puzzle_state(state) for state in self.path)
            else []
        )
        solution_states = set(recorded_path) if self.success and self.goal_reached else set()
        solution_edges = {
            (recorded_path[index - 1], self.actions[index - 1], recorded_path[index])
            for index in range(1, len(recorded_path))
        } if solution_states else set()

        def add_node(
            state: tuple[int, ...], depth: int, g: float,
            h: Optional[float], f: Optional[float],
        ) -> SearchTreeNode:
            if state not in states:
                states[state] = SearchTreeNode(
                    node_id=f"n{len(states)}", state=state, depth=depth,
                    g=g, h=h, f=f, on_solution_path=state in solution_states,
                )
            return states[state]

        edges: list[SearchTreeEdge] = []
        edges_by_key: dict[tuple[str, str, str], SearchTreeEdge] = {}

        def add_edge(
            parent: SearchTreeNode,
            child: SearchTreeNode,
            action: str,
            on_solution_path: bool,
        ) -> None:
            key = (parent.node_id, child.node_id, action)
            existing = edges_by_key.get(key)
            if existing is not None:
                existing.on_solution_path = existing.on_solution_path or on_solution_path
                return
            edge = SearchTreeEdge(
                parent.node_id, child.node_id, action, on_solution_path,
            )
            edges.append(edge)
            edges_by_key[key] = edge

        # Keep node IDs chronological. The old path-first build assigned the goal
        # an early ID, then appended earlier trace events after it, which made the
        # graph look as though BFS continued generating nodes after finding Goal.
        if recorded_path:
            add_node(recorded_path[0], 0, 0, None, None)

        for event in self.trace:
            # Rejected duplicate/cycle events are useful in the trace table, but
            # they were never inserted into the search tree. Drawing them created
            # misleading reverse arrows from a child back to its parent.
            if event.event.startswith("reject"):
                continue
            parent_state, child_state = event.node_state, event.state
            if not (is_puzzle_state(parent_state) and is_puzzle_state(child_state) and event.action):
                continue
            if _move_blank(parent_state, event.action) != child_state:
                continue
            child_depth = event.depth or int(event.g or 0)
            event_g = event.g if event.g is not None else child_depth
            parent = add_node(
                parent_state, max(child_depth - 1, 0), max(event_g - 1, 0), None, None,
            )
            child = add_node(child_state, child_depth, event_g, event.h, event.f)
            add_edge(
                parent,
                child,
                event.action,
                (parent_state, event.action, child_state) in solution_edges,
            )

        # A solver may keep a bounded trace or test Goal only when popping a node.
        # Add any missing certified path states after the chronological trace, and
        # upgrade matching trace edges to solution-path edges.
        for index, state in enumerate(recorded_path):
            add_node(state, index, index, None, None)
            if index:
                parent = states[recorded_path[index - 1]]
                child = states[state]
                add_edge(
                    parent,
                    child,
                    self.actions[index - 1],
                    bool(solution_states),
                )
        self.search_tree_nodes = list(states.values())
        self.search_tree_edges = edges

    def summary_dict(self) -> dict:
        return {
            "Algorithm": self.algorithm,
            "Group": self.group,
            "Solved?": "Yes" if self.success else "No",
            "Path Length": len(self.actions) if self.path_verified else "-",
            "Cost": self.cost if self.success else "-",
            "Nodes Expanded": self.nodes_expanded,
            "Nodes Generated": self.nodes_generated,
            "Max Frontier": self.max_frontier_size,
            "Reached Size": self.reached_size,
            "Runtime (s)": f"{self.runtime:.4f}",
            "Random Seed": self.random_seed if self.random_seed is not None else "Deterministic",
            "Complete?": "Yes" if self.is_complete else "No",
            "Optimal?": "Yes" if self.is_optimal else "No",
            "Heuristic?": "Yes" if self.uses_heuristic else "No",
            "Randomness?": "Yes" if self.uses_randomness else "No",
            "Legal Path?": "Yes" if self.path_verified else "No",
            "Reached Goal?": (
                "Not reported"
                if self.goal_state is None
                else ("Yes" if self.goal_reached else "No")
            ),
            "Run Termination": self.termination_reason,
            "Optimality Proven?": "Yes" if self.optimality_proven else "No",
        }


def search_tree_to_dot(result: SearchResult, max_nodes: int = 40) -> str:
    """Serialize bounded, explicit search-tree evidence to Graphviz DOT."""
    visible = {node.node_id: node for node in result.search_tree_nodes[:max_nodes]}
    lines = [
        "digraph SearchTree {",
        "rankdir=TB;",
        'graph [bgcolor=transparent ranksep=0.85 nodesep=0.5 pad=0.25];',
        'node [shape=box style="rounded,filled" fontname="Courier" fontsize=14 margin="0.12,0.08" penwidth=1.8];',
        'edge [fontname="Arial" fontsize=12 arrowsize=0.8];',
    ]
    for node in visible.values():
        rows = [node.state[i:i + 4] for i in range(0, 16, 4)]
        grid = "\\n".join(" ".join(" _" if val == 0 else f"{val:2d}" for val in row) for row in rows)
        h_text = "-" if node.h is None else f"{node.h:g}"
        f_text = "-" if node.f is None else f"{node.f:g}"
        if result.algorithm == "BFS":
            label = f"{node.node_id} | d={node.depth}\\n{grid}"
        else:
            label = f"{node.node_id} | d={node.depth} g={node.g:g} h={h_text} f={f_text}\\n{grid}"
        fill = "#D1FAE5" if node.on_solution_path else "#E0E7FF"
        border = "#059669" if node.on_solution_path else "#4F46E5"
        lines.append(f'{node.node_id} [label="{label}" fillcolor="{fill}" color="{border}"];')
    for edge in result.search_tree_edges:
        if edge.parent_id in visible and edge.child_id in visible:
            color = "#059669" if edge.on_solution_path else "#64748B"
            width = 2.4 if edge.on_solution_path else 1.0
            lines.append(f'{edge.parent_id} -> {edge.child_id} [label="{edge.action}" color="{color}" penwidth={width}];')
    lines.append("}")
    return "\n".join(lines)
