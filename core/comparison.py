"""Pure evidence helpers for comparing algorithm solution paths."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable

from core.metrics import SearchResult


def compact_action_path(actions: list[str], max_actions: int = 16) -> str:
    """Render an auditable but table-friendly action sequence."""
    if max_actions < 1:
        raise ValueError("max_actions must be positive")
    if not actions:
        return "Start = Goal"
    visible = " → ".join(actions[:max_actions])
    remaining = len(actions) - max_actions
    return f"{visible} … (+{remaining})" if remaining > 0 else visible


def shared_verified_paths(results: Iterable[SearchResult]) -> list[tuple[str, ...]]:
    """Return algorithm groups that produced the exact same verified state path."""
    by_path: dict[tuple[tuple[int, ...], ...], list[str]] = defaultdict(list)
    for result in results:
        if result.success and result.path_verified and result.path:
            by_path[tuple(result.path)].append(result.algorithm)
    return [tuple(names) for names in by_path.values() if len(names) > 1]


def unique_verified_path_count(results: Iterable[SearchResult]) -> int:
    """Count distinct legal state paths among successful comparison runs."""
    return len({
        tuple(result.path)
        for result in results
        if result.success and result.path_verified and result.path
    })
