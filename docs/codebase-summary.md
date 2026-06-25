# Codebase Summary

## Entry Point

- `app.py` is the Streamlit entrypoint and main tab router.
- `ui/advanced_tab.py` renders CSP, complex-environment, game-tree, and AI-vs-AI tournament demos.
- `ui/ai_vs_ai_tournament.py` renders the tournament setup, per-round scoring table, reference status, and winner summary.
- `ui/tournament_replay.py` replays both certified tournament trajectories step by step on one shared timeline.
- `ui/academic_panels.py` renders PEAS, taxonomy, rubric, exam path, grading summary, and academic warning panels.
- `ui/hand_tracing.py` renders interactive expansion-order practice and a Graphviz tree from the learner's verified parent/child choices.

## Core Data

- `core/puzzle.py` contains puzzle state utilities, solvability, scramble, path validation, and teaching presets.
- `core/heuristics.py` contains Misplaced Tiles, Manhattan Distance, and Linear Conflict.
- `core/metrics.py` defines run certificates, trace events, and explicit search-graph nodes/edges.
- `core/gameplay.py` scores legal player runs against a proven optimal distance.
- `core/ai_vs_ai_tournament.py` scores two solver agents on identical 15-puzzle rounds against an A* reference optimal certificate.
- `core/algorithm_comparison.py` defines within-group time, space, step/output, and guarantee comparison rows for the Theory UI.
- `core/academic.py` defines academic taxonomy, PEAS data, and recommendation rubric.
- `core/academic_proofs.py` defines proof cards, exam answer templates, benchmark presets, and decision guide data.
- `core/solver_dispatch.py` builds safe kwargs for UI solver calls.

## Algorithms

- `algorithms/uninformed.py`: BFS, DFS, UCS, IDS.
- `algorithms/informed.py`: Greedy Best-First, A*, IDA*.
- `algorithms/local_search.py`: hill climbing variants, beam search, simulated annealing.
- `algorithms/complex_env.py`: AND-OR, belief-state, partial-observation, LRTA* demos.
- `algorithms/csp.py`: CSP definition, propagation, consistency, backtracking, min-conflicts, and constraint-graph demos.
- `algorithms/csp_ac3.py`: executable AC-3 for the bounded full-state chain `S[0]..S[T]`, including exact-horizon path extraction and domain-wipe-out evidence.
- `algorithms/adversarial.py`: Minimax, Alpha-Beta, Expectimax demos; returned actions form a legal selected variation/sample path with explicit caveats that these are not standard 15-puzzle optimality certificates.

## Academic Documentation

- `docs/algorithm-groups-academic-reference.md`: Vietnamese full reference for PEAS, algorithm groups, guarantees, heuristic proofs, failure modes, CSP/complex-environment boundaries, tournament scoring, and game/chance framing.
- `docs/algorithm-test-plan.md`: Vietnamese verification matrix for solver correctness, custom goals, trace evidence, stochastic seeds, AI-vs-AI scoring, UI/browser checks, and exam-defense acceptance criteria.
- `docs/project-overview-pdr.md`: project purpose, audience, academic positioning, and success criteria.
- `docs/system-architecture.md`: Streamlit architecture, solver/evidence flow, extension boundaries, and documentation/reporting flow.

## Tests

- `tests/test_puzzle.py`: puzzle mechanics and solvability.
- `tests/test_heuristics.py`: heuristic correctness.
- `tests/test_solvers.py`: solver behavior, path validation, teaching preset regressions, and legal selected-path checks for game/chance demos.
- `tests/test_ai_vs_ai_tournament.py`: scoring rules, reference reuse, deterministic seeds, integration, and tie-break behavior for AI-vs-AI Tournament.
- `tests/test_academic_algorithm_matrix.py`: executable taxonomy/certificate matrix covering every displayed algorithm and model.
- `tests/test_csp_ac3.py`: AC-3 exact-horizon success, parity wipe-out, custom-goal path, and certificate regressions.
- `tests/test_runtime_integrity.py`: compile/import and dispatch regressions.
- `tests/test_academic.py`: taxonomy, PEAS, rubric, exam path, report, and UI contract completeness.
- `tests/test_search_tree_evidence.py`: legal parent/child edges and run certificates.
- `tests/test_streamlit_app.py`: browser-app flow through Streamlit AppTest, including Hand-Tracing graph-edge evidence.
