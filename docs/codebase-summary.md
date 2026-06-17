# Codebase Summary

## Entry Point

- `app.py` is the Streamlit entrypoint and main tab router.
- `desktop_app.py` starts the Streamlit server and opens a lecturer-friendly app window.
- `ui/advanced_tab.py` renders CSP, complex-environment, and game-tree demos.
- `ui/academic_panels.py` renders PEAS, taxonomy, rubric, exam path, grading summary, and academic warning panels.

## Core Data

- `core/puzzle.py` contains puzzle state utilities, solvability, scramble, path validation, and teaching presets.
- `core/heuristics.py` contains Misplaced Tiles, Manhattan Distance, and Linear Conflict.
- `core/metrics.py` defines `SearchResult` and `TraceStep`.
- `core/academic.py` defines academic taxonomy, PEAS data, and recommendation rubric.
- `core/solver_dispatch.py` builds safe kwargs for UI solver calls.

## Algorithms

- `algorithms/uninformed.py`: BFS, DFS, UCS, IDS.
- `algorithms/informed.py`: Greedy Best-First, A*, IDA*.
- `algorithms/local_search.py`: hill climbing variants, beam search, simulated annealing.
- `algorithms/complex_env.py`: AND-OR, belief-state, partial-observation, LRTA* demos.
- `algorithms/csp.py`: CSP definition, propagation, consistency, backtracking, min-conflicts, graph coloring, graphs.
- `algorithms/adversarial.py`: Minimax, Alpha-Beta, Expectimax demos.

## Tests

- `tests/test_puzzle.py`: puzzle mechanics and solvability.
- `tests/test_heuristics.py`: heuristic correctness.
- `tests/test_solvers.py`: solver behavior, path validation, teaching preset regressions.
- `tests/test_runtime_integrity.py`: compile/import and dispatch regressions.
- `tests/test_academic.py`: taxonomy, PEAS, rubric, exam path, report, and UI contract completeness.
