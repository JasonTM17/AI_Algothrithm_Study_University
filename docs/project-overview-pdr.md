# 15-Puzzle AI Final Exam - Project Overview

## Purpose

This project is a browser-based Streamlit learning and demonstration app for an Artificial Intelligence final exam. It uses the 15-puzzle to teach state-space search, heuristics, PEAS, local-search failure modes, CSP modeling, complex environments, and game-model extensions.

## Audience

Primary audience: instructors grading an AI course project.

Secondary audience: students practicing algorithm tracing and comparing solver behavior.

## Academic Positioning

The standard 15-puzzle environment is deterministic, fully observable, static, discrete, sequential, and single-agent. The app distinguishes:

- Real solvers: BFS, UCS, IDS, A*, IDA*.
- Contrast demos: DFS, Greedy Best-First, local search variants.
- Illustrative extensions: CSP, AND-OR, no/partial observation, LRTA*.
- Stochastic/game demos: Minimax, Alpha-Beta, Expectimax.

This distinction is required so the app stays academically truthful while still covering broad AI topics.
Graph coloring is handled as its own map-coloring CSP demo because it is a natural CSP example, not a 15-puzzle solver. The default dataset covers the 12 wards on the former Thu Duc City territory effective 2025-07-01; Australia remains available for comparison.

## Success Criteria

- The app runs without Streamlit runtime errors.
- The browser app is the only supported product surface.
- Every reported puzzle solution has a legal edge-by-edge path certificate.
- Search visualization contains explicit parent/child edges rather than inferred indentation.
- Hand-Tracing records the learner's chosen expansions as explicit parent/child graph edges.
- Advanced game/chance demos return only a legal selected variation or sample outcome path, and label it separately from full-tree evidence or optimal puzzle certificates.
- Challenge Mode first certifies the recorded player history as a legal trajectory, then compares completed solutions against an A* optimality certificate.
- Compare and Theory views clearly identify guarantees, environment assumptions, and solver role.
- PEAS is presented as a structured model, not only prose.
- Theory/PEAS includes an Exam Defense guide and downloadable grading report.
- The five-step exam path is visible across the main grading workflow.
- Mobile UI supports readable academic cards and a clickable sidebar.
- Tests cover puzzle validity, exact/admissible heuristics, solver regressions, tree edges, Streamlit integration, runtime compile, and academic taxonomy.
