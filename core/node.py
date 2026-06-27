"""Node for search algorithms."""

from typing import Optional


class Node:
    """Search node with state, parent, action, path cost, depth, and heuristic."""

    __slots__ = ("state", "parent", "action", "g", "depth", "h", "f")

    def __init__(
        self,
        state: tuple[int, ...],
        parent: Optional["Node"] = None,
        action: Optional[str] = None,
        g: int = 0,
        depth: int = 0,
        h: float = 0.0,
    ):
        self.state = state
        self.parent = parent
        self.action = action
        self.g = g
        self.depth = depth
        self.h = h
        self.f = g + h

    def __lt__(self, other: "Node") -> bool:
        if self.f != other.f:
            return self.f < other.f
        return self.g < other.g

    def __repr__(self) -> str:
        return f"Node(g={self.g}, h={self.h:.1f}, f={self.f:.1f}, depth={self.depth})"


def reconstruct_path(node: Node) -> list[tuple[int, ...]]:
    """Trace path from root to node."""
    path = []
    cur = node
    while cur is not None:
        path.append(cur.state)
        cur = cur.parent
    path.reverse()
    return path


def reconstruct_actions(node: Node) -> list[str]:
    """Trace actions from root to node."""
    actions = []
    cur = node
    while cur is not None and cur.action is not None:
        actions.append(cur.action)
        cur = cur.parent
    actions.reverse()
    return actions