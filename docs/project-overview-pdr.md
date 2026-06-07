# 15-Puzzle AI Final Exam - Project Overview

## Purpose

This project is a Streamlit learning and demonstration app for an Artificial Intelligence final exam. It uses the 15-puzzle to teach state-space search, heuristics, PEAS, local search failure modes, CSP modeling, complex environments, and game-tree extensions.

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

## Success Criteria

- The app runs without Streamlit runtime errors.
- Algorithm paths are validated when solvers succeed.
- Compare and Theory views clearly identify guarantees, environment assumptions, and solver role.
- PEAS is presented as a structured model, not only prose.
- Theory/PEAS includes an Exam Defense guide and downloadable grading report.
- The five-step exam path is visible across the main grading workflow.
- Mobile UI supports readable academic cards and a clickable sidebar.
- Tests cover puzzle validity, heuristics, solver regressions, runtime import/compile, and academic taxonomy.
