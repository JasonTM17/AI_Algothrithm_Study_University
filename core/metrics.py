"""Search result dataclass."""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class TraceStep:
    """Single step in search trace."""
    step: int
    state: tuple[int, ...]
    action: Optional[str] = None
    g: int = 0
    h: float = 0.0
    f: float = 0.0
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
    cost: int = 0
    depth: int = 0
    nodes_expanded: int = 0
    nodes_generated: int = 0
    max_frontier_size: int = 0
    reached_size: int = 0
    runtime: float = 0.0
    message: str = ""
    trace: list[TraceStep] = field(default_factory=list)
    search_tree_nodes: list[SearchTreeNode] = field(default_factory=list)
    search_tree_edges: list[SearchTreeEdge] = field(default_factory=list)
    trace_truncated: bool = False
    trace_total_events: int = 0
    path_verified: bool = False
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

    def _verify_path_evidence(self) -> None:
        if not self.success or not self.path:
            return
        from core.puzzle import validate_solution_path
        self.path_verified, self.verification_message = validate_solution_path(
            self.path, self.actions, self.path[-1]
        )

    def _classify_run_outcome(self) -> None:
        message = self.message.lower()
        if self.success:
            self.termination_reason = "goal"
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
        self.optimality_proven = bool(self.success and self.is_optimal and self.path_verified)
        self.exhaustive_failure = bool(
            not self.success and self.is_complete and self.termination_reason == "exhausted"
        )

    def _build_search_tree_evidence(self) -> None:
        from core.puzzle import _move_blank

        def is_puzzle_state(value: object) -> bool:
            return isinstance(value, tuple) and len(value) == 16 and set(value) == set(range(16))

        states: dict[tuple[int, ...], SearchTreeNode] = {}
        solution_states = set(self.path) if self.path and all(is_puzzle_state(s) for s in self.path) else set()

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
        edge_keys: set[tuple[str, str, str]] = set()
        if solution_states:
            for index, state in enumerate(self.path):
                add_node(state, index, index, None, None)
                if index:
                    parent = states[self.path[index - 1]]
                    child = states[state]
                    action = self.actions[index - 1]
                    edges.append(SearchTreeEdge(parent.node_id, child.node_id, action, True))
                    edge_keys.add((parent.node_id, child.node_id, action))

        for event in self.trace:
            parent_state, child_state = event.node_state, event.state
            if not (is_puzzle_state(parent_state) and is_puzzle_state(child_state) and event.action):
                continue
            if _move_blank(parent_state, event.action) != child_state:
                continue
            parent = add_node(
                parent_state, max(int(event.g) - 1, 0), max(event.g - 1, 0), None, None,
            )
            child = add_node(child_state, event.depth or int(event.g), event.g, event.h, event.f)
            child.depth, child.g, child.h, child.f = (
                event.depth or int(event.g), event.g, event.h, event.f,
            )
            key = (parent.node_id, child.node_id, event.action)
            if key not in edge_keys:
                edges.append(SearchTreeEdge(
                    parent.node_id, child.node_id, event.action,
                    parent_state in solution_states and child_state in solution_states,
                ))
                edge_keys.add(key)
        self.search_tree_nodes = list(states.values())
        self.search_tree_edges = edges

    def summary_dict(self) -> dict:
        return {
            "Algorithm": self.algorithm,
            "Group": self.group,
            "Solved?": "Yes" if self.success else "No",
            "Path Length": len(self.actions) if self.success else "-",
            "Cost": self.cost if self.success else "-",
            "Nodes Expanded": self.nodes_expanded,
            "Nodes Generated": self.nodes_generated,
            "Max Frontier": self.max_frontier_size,
            "Reached Size": self.reached_size,
            "Runtime (s)": f"{self.runtime:.4f}",
            "Complete?": "Yes" if self.is_complete else "No",
            "Optimal?": "Yes" if self.is_optimal else "No",
            "Heuristic?": "Yes" if self.uses_heuristic else "No",
            "Randomness?": "Yes" if self.uses_randomness else "No",
            "Path Verified?": "Yes" if self.path_verified else "No",
            "Run Termination": self.termination_reason,
            "Optimality Proven?": "Yes" if self.optimality_proven else "No",
        }


def search_tree_to_dot(result: SearchResult, max_nodes: int = 40) -> str:
    """Serialize bounded, explicit search-tree evidence to Graphviz DOT."""
    visible = {node.node_id: node for node in result.search_tree_nodes[:max_nodes]}
    lines = [
        "digraph SearchTree {", "rankdir=TB;", "graph [bgcolor=transparent];",
        'node [shape=box style="rounded,filled" fontname="Arial" fontsize=9];',
        'edge [fontname="Arial" fontsize=9];',
    ]
    for node in visible.values():
        rows = [node.state[i:i + 4] for i in range(0, 16, 4)]
        grid = "\\n".join(" ".join("_" if value == 0 else str(value) for value in row) for row in rows)
        h_text = "-" if node.h is None else f"{node.h:g}"
        f_text = "-" if node.f is None else f"{node.f:g}"
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
