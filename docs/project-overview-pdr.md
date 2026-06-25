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
- AI-vs-AI/game-chance demos: AI-vs-AI Tournament, Minimax, Alpha-Beta, Expectimax.

This distinction is required so the app stays academically truthful while still covering broad AI topics.
AI-vs-AI Tournament is handled as a scoring layer over two 15-puzzle solver agents. Each round uses an A* reference optimal certificate; optimal legal paths receive 100 points, longer legal paths are scored by relative path efficiency, failed paths lose points, and invalid paths receive the strongest penalty. Certified trajectories are replayed side by side on a shared step timeline.

## Academic Documentation

- `docs/algorithm-groups-academic-reference.md` is the Vietnamese full reference for defending algorithm groups.
- `docs/algorithm-test-plan.md` is the Vietnamese verification plan for solver oracles, trace evidence, custom goals, stochastic seeds, UI/browser checks, and exam-defense acceptance criteria.
- It covers PEAS, completeness, optimality, memory/runtime tradeoffs, heuristic guarantees, local-search failure modes, CSP formulation, complex environments, tournament scoring, and game/chance boundaries.
- It is intentionally aligned with `core/academic.py`, `core/academic_proofs.py`, `core/heuristics.py`, and the `algorithms/` modules, so exam claims stay tied to implemented behavior.

## Success Criteria

- The app runs without Streamlit runtime errors.
- Theory/PEAS compares algorithms inside each group by time complexity, space complexity, step/output behavior, and guarantees.
- Group 5 AC-3 reports an exact-horizon legal path or domain wipe-out without claiming global shortest-path optimality.
- The browser app is the only supported product surface.
- Every reported puzzle solution has a legal edge-by-edge path certificate.
- Search visualization contains explicit parent/child edges rather than inferred indentation.
- Hand-Tracing records the learner's chosen expansions as explicit parent/child graph edges.
- Advanced game/chance demos return only a legal selected variation or sample outcome path, and label it separately from full-tree evidence or optimal puzzle certificates.
- AI-vs-AI Tournament shows reference optimal cost, per-agent path efficiency and score reason, synchronized replay, winner/draw, and deterministic tie-break detail.
- Challenge Mode first certifies the recorded player history as a legal trajectory, then compares completed solutions against an A* optimality certificate.
- Compare and Theory views clearly identify guarantees, environment assumptions, and solver role.
- PEAS is presented as a structured model, not only prose.
- Theory/PEAS includes an Exam Defense guide and downloadable grading report.
- The repository includes a detailed Vietnamese academic reference for all algorithm groups and their correct exam framing.
- The five-step exam path is visible across the main grading workflow.
- Mobile UI supports readable academic cards and a clickable sidebar.
- Tests cover puzzle validity, exact/admissible heuristics, solver regressions, tournament scoring, tree edges, Streamlit integration, runtime compile, and academic taxonomy.
