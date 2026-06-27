# Tóm Tắt Codebase

## Entry Point Và Tab

| File | Vai trò |
|---|---|
| `app.py` | Streamlit entrypoint, page config, sidebar, language selector, start/goal controls và tab router. |
| `ui/play_tab.py` | Board số/ảnh, AI replay A*, step slider, challenge score. |
| `ui/run_tab.py` | Chạy một thuật toán, metrics, trace, readable tree và Graphviz evidence. |
| `ui/compare_tab.py` | Benchmark nhiều solver cùng start/goal/seed/limit. |
| `ui/trace_tab.py` | Đọc trace đã lưu và export CSV. |
| `ui/hand_tracing.py` | Luyện mở rộng frontier bằng tay. |
| `ui/theory_tab.py` | PEAS, taxonomy, proof cards, caveat và Group 6 comparison. |
| `ui/advanced_tab.py` | CSP, complex environments, game/chance và AI-vs-AI Tournament. |

## Core Domain

| File | Nội dung |
|---|---|
| `core/puzzle.py` | State contract, move blank, parity solvability, scramble, parse/validate path. |
| `core/heuristics.py` | Misplaced Tiles, Manhattan Distance, Linear Conflict. |
| `core/metrics.py` | `TraceStep`, `SearchResult`, certificates, search-tree evidence. |
| `core/solver_dispatch.py` | Kwargs an toàn cho từng solver signature. |
| `core/randomness.py` | Seed, action order, stochastic solver metadata. |
| `core/ai_vs_ai_tournament.py` | A* reference, score, tie-break và per-round evidence. |
| `core/academic.py`, `core/academic_proofs.py`, `core/theory.py` | Taxonomy, PEAS, theory cards, pseudocode và exam notes. |

## Algorithms

| File | Thuật toán |
|---|---|
| `algorithms/uninformed.py` | BFS, DFS, UCS, IDS. |
| `algorithms/informed.py` | Greedy Best-First, A*, IDA*. |
| `algorithms/local_search.py` | 6 local search variants, candidate evidence, accept/reject trace. |
| `algorithms/complex_env.py` | AND-OR, No Observation, Partial Observation, LRTA*. Belief planners now report planner votes, fallback votes and fallback reason. |
| `algorithms/csp.py`, `algorithms/csp_ac3.py` | CSP teaching models and executable AC-3 state-chain. |
| `algorithms/adversarial.py` | Minimax/Alpha-Beta as worst-case robustness, Expectimax as chance model. |

## UI Support

| File | Vai trò |
|---|---|
| `ui/components.py` | Board renderer, metrics, trace tables, solution trajectory, readable tree. |
| `ui/styles.py` | Streamlit CSS. Number tiles use restrained value-stable neutral shades; correctness is shown by indicator/outline, not color swapping by row. |
| `ui/localization.py` | English/Vietnamese dictionary and translator. |
| `ui/belief_controls.py` | Known-tile matrix 4x4; `_` means unknown. |
| `ui/sample_images.py`, `ui/assets/` | Built-in image puzzle sources. |

## Media Và Documentation Pipeline

| Path | Vai trò |
|---|---|
| `scripts/generate-readme-gifs.py` | CLI tạo GIF README/gallery từ solver/model thật. |
| `scripts/readme_gif_specs.py` | Registry 6 nhóm/28 thuật toán, start/goal/seed/params cố định. |
| `scripts/readme_gif_runner.py` | Chạy solver và gom `SearchResult` evidence. |
| `scripts/readme_gif_renderer.py` | Render GIF 800x450 bằng Pillow. |
| `scripts/readme_gif_manifest.py` | Manifest semantic và asset checker. |
| `docs/assets/readme/` | 7 GIF nổi bật trong README. |
| `docs/assets/algorithm-demos/` | 28 GIF cá nhân và `manifest.json`. |
| `docs/algorithm-demo-gallery.md` | Gallery đầy đủ 28 thuật toán. |

## Tests

| Nhóm | Mục tiêu |
|---|---|
| `tests/test_solvers.py`, `tests/test_algorithm_contract_sweep.py` | Solver correctness, dispatch, legal path, custom goal. |
| `tests/test_complex_models.py` | AND-OR, belief state, known matrix, planner fallback evidence. |
| `tests/test_readme_gifs.py` | Registry 28 thuật toán, real demo evidence, GIF nonblank, README dưới 300 dòng. |
| `tests/test_streamlit_app.py` | Streamlit AppTest cho UI chính, selectors, replay. |
| `tests/test_academic.py`, `tests/test_text_quality.py`, `tests/test_localization.py` | Theory, wording, bilingual/localization and text quality. |

## Quality Gates

```bash
python -m compileall -q app.py core algorithms ui scripts
python scripts/generate-readme-gifs.py --check
python -m pytest tests -q --cov=core --cov=algorithms --cov-report=term-missing --cov-fail-under=65
```
