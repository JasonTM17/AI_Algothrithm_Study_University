# 15-Puzzle AI Algorithm Simulator

Professional Streamlit dashboard for studying and defending AI algorithms on the 15-puzzle. The project is designed for a university AI final exam: it demonstrates PEAS, state-space search, heuristic guarantees, benchmark evidence, and the boundary between real solvers and educational extensions.

## Quick Start

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Lecturer App Mode

For classroom or grading use on Windows, there are two supported paths.

### One-click source launcher

Install dependencies once and launch the desktop-style app:

```bash
pip install -r requirements.txt
start-15-puzzle-ai.bat
```

`desktop_app.py` starts Streamlit on a local port and opens it in a native app window when `pywebview` is available. If the native window backend is unavailable, it falls back to the default browser while keeping the same local app behavior.

### Windows EXE build

Build a lecturer-friendly executable folder:

```powershell
powershell -ExecutionPolicy Bypass -File .\build-windows-exe.ps1
```

Then open:

```text
dist\15-Puzzle-AI\15-Puzzle-AI.exe
```

The EXE uses a parent/child launcher: the visible app process opens the native lecturer window, while a local child process serves Streamlit on `127.0.0.1`. The generated `dist/` folder is intentionally not committed because it is a large build artifact; rebuild it locally or publish it as a release asset.

On Windows PowerShell, compile all Python files with:

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

See [docs/branch-and-release-tree.md](docs/branch-and-release-tree.md) for the release tree that connects the master branch, academic UI, CSP separation, EXE app mode, and verification pipeline.

## Academic Framing

The standard 15-puzzle environment is fully observable, deterministic, static, discrete, sequential, single-agent, and unit-cost.

| Role | Algorithms | Meaning |
|---|---|---|
| Real Solver | BFS, UCS, IDS, A*, IDA* | Natural solvers for the deterministic 15-puzzle model. |
| Contrast Demo | DFS, Greedy, local search variants | Useful for showing tradeoffs, suboptimality, local optimum, or missing guarantees. |
| Illustrative Extension | CSP, AND-OR, No/Partial Observation, LRTA* | Educational reformulations for learning broader AI concepts. |
| Stochastic/Game Demo | Minimax, Alpha-Beta, Expectimax | Game/chance-node demonstrations, not natural 15-puzzle solvers. |

## PEAS Summary

| PEAS | 15-Puzzle interpretation |
|---|---|
| Performance | Reach the goal state with few moves, fewer expanded nodes, lower memory, and lower runtime. |
| Environment | 4x4 board, deterministic transitions, fully observable state, static world, discrete actions. |
| Actuators | Slide the blank tile left, right, up, or down when legal. |
| Sensors | Full board configuration, blank position, legal moves, and heuristic estimates. |

## Main Features

- Interactive board and image puzzle mode.
- Single-algorithm runner with trace, metrics, frontier/reached detail, and search tree.
- Benchmark comparison with methodology panels and academic evidence metrics.
- Theory/PEAS page with proof cards, taxonomy, decision guide, and grading report export.
- Advanced CSP, complex-environment, and game-tree demonstrations with warning labels.
- Graph coloring defaults to the current 12-ward Thu Duc map (effective 2025-07-01), with an Australia comparison, an offline SVG map, and an auditable MRV/forward-checking trace. It remains separate from the 15-puzzle solver.
- Hand-tracing practice for oral/written exam preparation.
- Teaching presets for Greedy suboptimality and Hill Climbing local optimum.
- Accessibility-oriented UI: focus states, reduced-motion support, responsive cards, and mobile sidebar safeguards.

## Project Structure

```text
app.py                         Streamlit web entrypoint and tab router
desktop_app.py                 Desktop-style launcher for lecturers
start-15-puzzle-ai.bat         Windows one-click launcher
core/                          puzzle logic, theory data, academic data, dispatch helpers
algorithms/                    uninformed, informed, local, CSP, complex, adversarial algorithms
ui/                            Streamlit tab modules, shared panels, components, styles
docs/                          project overview, design guidelines, codebase summary
tests/                         solver, runtime, dispatch, UI/academic regression tests
```

## Verification

```bash
python -m pytest tests/ -q
```

Expected coverage includes puzzle mechanics, heuristic correctness, solver regressions, runtime compile/import, dispatch safety, taxonomy completeness, grading report content, and UI/UX contracts.

## Notes For Grading

- A*, IDA*, BFS, UCS, and IDS are the main solver demonstrations.
- Greedy and local search are intentionally kept as contrast cases.
- CSP, complex-environment, Minimax, Alpha-Beta, and Expectimax are labeled as educational extensions.
- Graph coloring belongs to the map-coloring CSP demo. It is intentionally separate from 15-puzzle.
- Benchmark output is course evidence, not a production solver leaderboard.
