"""Deterministic map-coloring CSPs used by the advanced teaching demo."""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

from core.metrics import SearchResult, TraceStep
from core.puzzle import GOAL_STATE


AUSTRALIA_GRAPH: dict[str, set[str]] = {
    "WA": {"NT", "SA"},
    "NT": {"WA", "SA", "Q"},
    "SA": {"WA", "NT", "Q", "NSW", "V"},
    "Q": {"NT", "SA", "NSW"},
    "NSW": {"Q", "SA", "V"},
    "V": {"SA", "NSW"},
    "T": set(),
}

THU_DUC_2025_WARDS = frozenset({
    "Hiệp Bình", "Tam Bình", "Thủ Đức", "Linh Xuân", "Long Bình",
    "Tăng Nhơn Phú", "Phước Long", "Long Phước", "Long Trường",
    "An Khánh", "Bình Trưng", "Cát Lái",
})


@dataclass(frozen=True)
class MapDefinition:
    """Static geometry and adjacency data for one coloring problem."""

    map_id: str
    title: str
    adjacency: dict[str, frozenset[str]]
    geojson: dict | None = None
    metadata: dict = field(default_factory=dict)


@dataclass
class MapColoringResult(SearchResult):
    """Search result plus structured state needed by the map renderer."""

    map_id: str = ""
    map_title: str = ""
    assignment: dict[str, str] = field(default_factory=dict)
    adjacency: dict[str, frozenset[str]] = field(default_factory=dict)
    assignment_history: list[dict[str, str]] = field(default_factory=list)
    history_labels: list[str] = field(default_factory=list)
    validation_errors: list[str] = field(default_factory=list)
    attempts: int = 0
    backtracks: int = 0
    geojson: dict | None = None
    source_metadata: dict = field(default_factory=dict)


@lru_cache(maxsize=1)
def _load_thu_duc_definition() -> MapDefinition:
    asset = Path(__file__).with_name("assets") / "thu-duc-wards-2025.geojson"
    data = json.loads(asset.read_text(encoding="utf-8"))
    raw_adjacency = data["metadata"]["adjacency"]
    adjacency = {
        region: frozenset(neighbors)
        for region, neighbors in raw_adjacency.items()
    }
    if set(adjacency) != THU_DUC_2025_WARDS:
        raise ValueError("Thu Duc asset does not contain the audited 12-ward set")
    for region, neighbors in adjacency.items():
        if region in neighbors or not neighbors <= THU_DUC_2025_WARDS:
            raise ValueError(f"Invalid adjacency entry for {region}")
        if any(region not in adjacency[neighbor] for neighbor in neighbors):
            raise ValueError(f"Asymmetric adjacency entry for {region}")
    return MapDefinition(
        map_id="thu-duc-2025",
        title=data["metadata"]["title"],
        adjacency=adjacency,
        geojson=data,
        metadata={key: value for key, value in data["metadata"].items() if key != "adjacency"},
    )


def load_map_definition(map_id: str = "thu-duc-2025") -> MapDefinition:
    """Return an audited built-in map by stable identifier."""
    if map_id == "thu-duc-2025":
        return _load_thu_duc_definition()
    if map_id == "australia":
        return MapDefinition(
            map_id="australia",
            title="Australia states and territories",
            adjacency={region: frozenset(neighbors) for region, neighbors in AUSTRALIA_GRAPH.items()},
            metadata={"disclaimer": "Schematic classroom graph; Tasmania has no land adjacency."},
        )
    raise ValueError(f"Unknown map_id: {map_id}")


def _validate_coloring(
    assignment: dict[str, str], adjacency: dict[str, frozenset[str]]
) -> list[str]:
    errors: list[str] = []
    for region, neighbors in adjacency.items():
        if region not in assignment:
            errors.append(f"{region} is unassigned")
        for neighbor in neighbors:
            if region < neighbor and assignment.get(region) == assignment.get(neighbor):
                errors.append(f"{region} and {neighbor} share {assignment.get(region)}")
    return errors


def graph_coloring_demo(
    colors: tuple[str, ...] = ("Red", "Green", "Blue"),
    map_id: str = "thu-duc-2025",
) -> MapColoringResult:
    """Color a real map graph using MRV, degree tie-break and forward checking."""
    started = time.perf_counter()
    definition = load_map_definition(map_id)
    palette = tuple(dict.fromkeys(color.strip() for color in colors if color.strip()))
    assignment: dict[str, str] = {}
    trace: list[TraceStep] = []
    history: list[dict[str, str]] = [dict(assignment)]
    history_labels = ["Initial unassigned map"]
    attempts = 0
    backtracks = 0
    valid_assignments = 0
    max_depth = 0

    def legal_colors(region: str) -> tuple[str, ...]:
        used = {assignment[n] for n in definition.adjacency[region] if n in assignment}
        return tuple(color for color in palette if color not in used)

    def choose_region() -> str:
        candidates = [region for region in definition.adjacency if region not in assignment]
        return min(
            candidates,
            key=lambda region: (
                len(legal_colors(region)),
                -len(definition.adjacency[region]),
                region,
            ),
        )

    def record(label: str) -> None:
        history.append(dict(assignment))
        history_labels.append(label)

    def backtrack() -> bool:
        nonlocal attempts, backtracks, valid_assignments, max_depth
        if len(assignment) == len(definition.adjacency):
            return True
        max_depth = max(max_depth, len(assignment))
        region = choose_region()
        for color in palette:
            attempts += 1
            if color not in legal_colors(region):
                trace.append(TraceStep(
                    step=attempts,
                    state=GOAL_STATE,
                    reason=f"Reject {region}={color}: conflicts with an assigned neighbor.",
                ))
                continue
            assignment[region] = color
            valid_assignments += 1
            label = f"Assign {region} = {color}"
            record(label)
            trace.append(TraceStep(
                step=attempts,
                state=GOAL_STATE,
                depth_limit=len(assignment),
                frontier_size=sum(1 for item in definition.adjacency if item not in assignment),
                reached_size=len(assignment),
                reason=label,
            ))
            dead_end = any(
                not legal_colors(item)
                for item in definition.adjacency
                if item not in assignment
            )
            if not dead_end and backtrack():
                return True
            backtracks += 1
            del assignment[region]
            record(f"Backtrack {region}; restore previous partial assignment")
        return False

    solved = bool(palette) and backtrack()
    errors = _validate_coloring(assignment, definition.adjacency) if solved else []
    solved = solved and not errors
    adjacency_lines = [
        f"- {region}: {', '.join(sorted(neighbors)) or 'no adjacent regions'}"
        for region, neighbors in definition.adjacency.items()
    ]
    assignment_lines = [
        f"- {region}: {assignment.get(region, 'unassigned')}"
        for region in definition.adjacency
    ]
    status = "valid solution" if solved else "no valid solution with the selected colors"
    message = (
        f"Graph Coloring CSP — {definition.title}\n\n"
        "This map CSP is separate from the 15-puzzle and is not a natural 15-puzzle solver.\n\n"
        f"Variables: {len(definition.adjacency)} regions\n"
        f"Domain: {{{', '.join(palette) or 'empty'}}}\n"
        "Constraint: every adjacent pair must use different colors.\n"
        "Search: MRV + degree tie-break + forward checking.\n"
        f"Result: {status}.\n\nAdjacency graph:\n"
        + "\n".join(adjacency_lines)
        + "\n\nSolution:\n"
        + "\n".join(assignment_lines)
    )
    return MapColoringResult(
        success=solved,
        algorithm="Graph Coloring — MRV + Forward Checking",
        group="CSP",
        nodes_expanded=attempts,
        nodes_generated=valid_assignments,
        max_frontier_size=max_depth,
        reached_size=len(assignment),
        runtime=time.perf_counter() - started,
        termination_reason="valid_coloring" if solved else ("empty_palette" if not palette else "exhausted"),
        message=message,
        trace=trace[:240],
        suitable_for_puzzle=False,
        is_complete=True,
        is_optimal=False,
        map_id=map_id,
        map_title=definition.title,
        assignment=dict(assignment),
        adjacency=definition.adjacency,
        assignment_history=history,
        history_labels=history_labels,
        validation_errors=errors,
        attempts=attempts,
        backtracks=backtracks,
        geojson=definition.geojson,
        source_metadata=definition.metadata,
    )
