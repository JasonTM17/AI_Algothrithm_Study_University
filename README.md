# 15-Puzzle AI Algorithm Simulator

Professional Streamlit dashboard for studying and defending AI algorithms on the 15-puzzle. The project is designed for a university AI final exam: it demonstrates PEAS, state-space search, heuristic guarantees, benchmark evidence, and the boundary between real solvers and educational extensions.

## Quick Start

```bash
pip install -r requirements.txt
streamlit run app.py
```

This repository ships one product: the browser-based Streamlit web app. On Windows PowerShell, verify all Python files with:

```powershell
$files = @('app.py') + (Get-ChildItem core,algorithms,ui -Filter *.py | ForEach-Object { $_.FullName })
python -m py_compile @files
python -m pytest tests/ -q
```

## Academic Dashboard Flow

Use the app in this order when presenting to an instructor:

| Step | Tab | Purpose |
|---|---|---|
| 1 | Play | Inspect the start state, goal state, solvability, and puzzle mechanics. |
| 2 | Run Algorithm | Explain one solver with frontier, reached set, heuristic, and guarantee. |
| 3 | Compare | Benchmark selected algorithms with seed, depth, timeout, node cap, and caveats. |
| 4 | Theory/PEAS | Defend the agent model, proof cards, taxonomy, and PEAS. |
| 5 | Hand-Tracing | Practice manual expansion order, tie-breaking, and trace verification. |

See [docs/branch-and-release-tree.md](docs/branch-and-release-tree.md) for the web release tree connecting the academic UI, solver evidence, concept-lab boundary, and verification pipeline.

For a detailed Vietnamese academic reference on the algorithm groups, guarantees, heuristics, failure modes, and exam-defense talking points, see [docs/algorithm-groups-academic-reference.md](docs/algorithm-groups-academic-reference.md).

For the algorithm verification matrix, edge cases, UI/browser checks, and exam-defense acceptance criteria, see [docs/algorithm-test-plan.md](docs/algorithm-test-plan.md).

## Academic Framing

The standard 15-puzzle environment is fully observable, deterministic, static, discrete, sequential, single-agent, and unit-cost.

| Role | Algorithms | Meaning |
|---|---|---|
| Real Solver | BFS, UCS, IDS, A*, IDA* | Natural solvers for the deterministic 15-puzzle model. |
| Contrast Demo | DFS, Greedy, local search variants | Useful for showing tradeoffs, suboptimality, local optimum, or missing guarantees. |
| Illustrative Extension | CSP, AND-OR, No/Partial Observation, LRTA* | Educational reformulations for learning broader AI concepts. |
| AI-vs-AI Tournament | AI-vs-AI scoring, Minimax, Alpha-Beta, Expectimax | Tournament compares two solver agents on the same 15-puzzle with A* reference scoring; game/chance modes remain educational extensions. |

## PEAS Summary

| PEAS | 15-Puzzle interpretation |
|---|---|
| Performance | Reach the goal state with few moves, fewer expanded nodes, lower memory, and lower runtime. |
| Environment | 4x4 board, deterministic transitions, fully observable state, static world, discrete actions. |
| Actuators | Slide the blank tile left, right, up, or down when legal. |
| Sensors | Full board configuration, blank position, legal moves, and heuristic estimates. |

## Main Features

- Interactive board, image puzzle, Undo, and optimality challenge mode with separate player-run legality, AI-assistance disclosure, and A* optimality certificates.
- Single-algorithm runner with trace, metrics, frontier/reached detail, and a parent-linked search graph; even failed or stuck runs expose a certified legal partial trajectory without labeling it as a solution.
- Benchmark comparison with methodology panels, recorded seeds, compact action paths, and explicit shared-path explanations for unit-cost optimal solvers.
- Theory/PEAS page with proof cards, taxonomy, decision guide, and grading report export.
- Theory/PEAS includes a within-group comparison table for step rule, time complexity, space complexity, output steps, and guarantees.
- Vietnamese full-reference documentation for algorithm groups, PEAS boundaries, heuristic guarantees, CSP modeling, complex environments, and AI-vs-AI scoring.
- Formal algorithm test plan covering solver oracles, trace evidence, custom goals, stochastic seeds, CSP/game demos, AI-vs-AI scoring, and UI/browser validation.
- Advanced CSP, complex-environment, game/chance, and AI-vs-AI tournament demonstrations live in a separate Concept Lab and are excluded from standard solver rankings.
- Group 5 includes executable AC-3 propagation over a bounded state chain `S[0]..S[T]`; it returns an exact-horizon legal path or a domain-wipe-out certificate.
- AI-vs-AI Tournament scores two selected solvers on identical 15-puzzle rounds: optimal paths get 100 points, legal longer paths are normalized by `optimal_cost / actual_cost`, partial/failed paths lose points, and invalid paths receive the strongest penalty.
- Tournament rounds include a synchronized step replay so both certified trajectories can be followed on one timeline before comparing the final score.
- Hand-tracing practice for oral/written exam preparation, including an explicit Graphviz expansion tree built from the learner's verified choices.
- Teaching presets for Greedy suboptimality and Hill Climbing local optimum.
- Run and Advanced demos record a fresh variation seed on each click, randomizing action order and tie-breaks where supported while preserving legal-path and optimality certificates. Compare, Tournament, and Hand-Tracing keep explicit seeds/orderings for reproducible grading.
- Accessibility-oriented UI: focus states, reduced-motion support, responsive cards, and mobile sidebar safeguards.

## Project Structure

```text
app.py                         Streamlit web entrypoint and tab router
core/                          puzzle logic, theory data, academic data, dispatch helpers
algorithms/                    uninformed, informed, local, CSP, complex, adversarial algorithms
ui/                            Streamlit tab modules, shared panels, components, styles
docs/                          project overview, design guidelines, codebase summary
tests/                         solver, runtime, dispatch, UI/academic regression tests
```

## Verification

```bash
pip install -r requirements-dev.txt
python -m compileall -q app.py core algorithms ui
python -m pytest tests/ -q
```

Expected coverage includes exact heuristic checks, bounded admissibility/consistency checks, legal path and tree-edge evidence, solver regressions, Streamlit AppTest flows, dispatch safety, AI-vs-AI tournament scoring, and academic taxonomy.

## Notes For Grading

- A*, IDA*, BFS, UCS, and IDS are the main solver demonstrations.
- Greedy and local search are intentionally kept as contrast cases.
- CSP, complex-environment, Minimax, Alpha-Beta, and Expectimax are labeled as educational extensions.
- Standard 15-puzzle is not adversarial. AI-vs-AI Tournament is a scoring layer over solver outputs, not a MIN-player environment.
- Benchmark output is course evidence, not a production solver leaderboard.
