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

    # Algorithm properties
    is_complete: bool = False
    is_optimal: bool = False
    uses_heuristic: bool = False
    uses_randomness: bool = False
    uses_adversary: bool = False
    uses_probability: bool = False
    suitable_for_puzzle: bool = True

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
        }