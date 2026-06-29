# Tóm Tắt Codebase

## Entry Point Và Tab

| File | Vai trò |
|---|---|
| `app.py` | Streamlit entrypoint, page config, sidebar, language selector, start/goal controls và tab router. |
| `ui/play_tab.py` | Board số/ảnh và router hai mode: Solver Replay hoặc Group 6 Decision Lab. |
| `ui/group6_decision_lab.py`, `ui/group6_tree_viewer.py` | Replay role MAX/MIN/CHANCE trên board ảnh không số, profiler depth, stability, export và tree zoom/pan. |
| `ui/run_tab.py` | Chạy một thuật toán, metrics, trace, trajectory, readable tree và Graphviz evidence. |
| `ui/compare_tab.py` | Benchmark nhiều solver cùng start/goal/seed/limit; chọn nhanh toàn bộ thuật toán có quỹ đạo so sánh được. |
| `ui/image_algorithm_race.py` | Biểu đồ runtime/bước và replay đồng bộ nhiều quỹ đạo bằng cùng puzzle ảnh, không phủ số. |
| `ui/path_solver_runner.py` | Runner dùng chung cho 13 thuật toán tạo path tuyến tính trong Play và Compare; cố định seed/limit/action order khi cần so sánh. |
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
| `core/group6_decision_lab.py` | Settings, fingerprint, role frames, space proxy và runner Minimax/Alpha-Beta/Expectimax cho Play. |
| `core/academic.py`, `core/academic_proofs.py`, `core/theory.py` | Taxonomy, PEAS, theory cards, pseudocode và exam notes. |

## Algorithms

| File | Thuật toán |
|---|---|
| `algorithms/uninformed.py` | BFS, DFS, UCS, IDS. |
| `algorithms/informed.py` | Greedy Best-First, A*, IDA*. |
| `algorithms/local_search.py` | 6 local search variants, candidate evidence, accept/reject trace. |
| `algorithms/complex_env.py`, `algorithms/belief_search.py` | AND-OR conditional plan, No Observation conformant belief-state search and Partial Observation contingent policy. |
| `algorithms/csp.py`, `algorithms/csp_algorithms.py`, `algorithms/csp_state_chain.py` | Four CSP algorithms over bounded state chains: Backtracking, Forward Checking, AC-3 and Min-Conflicts. |
| `algorithms/adversarial.py` | Minimax/Alpha-Beta as worst-case robustness, Expectimax as chance model. |

## UI Support

| File | Vai trò |
|---|---|
| `ui/components.py` | Board renderer, metrics, trace tables, solution trajectory, readable tree. |
| `ui/styles.py` | Streamlit CSS. Number tiles use restrained value-stable neutral shades; correctness is shown by indicator/outline, not row color. |
| `ui/localization.py` | English/Vietnamese dictionary and translator. |
| `ui/belief_controls.py` | Known-tile matrix 4x4; `_` means unknown. |
| `ui/sample_images.py`, `ui/assets/` | Built-in image puzzle sources. |

## Media Và Documentation Pipeline

| Path | Vai trò |
|---|---|
| `scripts/generate-readme-gifs.py` | CLI tạo GIF README/gallery từ live Streamlit browser capture. Supports `--profile hero|group|algorithm|all`, `--contact-sheet`, `--check-readability`; `--theme` chỉ là metadata tương thích. |
| `scripts/readme_gif_catalog.py` | Academic metadata: role, learning goal, mechanism, evidence, guarantee, caveat. |
| `scripts/readme_gif_specs.py` | Registry 6 nhóm/24 thuật toán, start/goal/seed/params cố định. |
| `scripts/readme_gif_runner.py` | Chạy solver và gom `SearchResult` evidence trước khi capture. |
| `ui/web_gif_capture.py`, `scripts/readme_gif_styles.py` | Hidden Streamlit route `?capture_demo=...` render frame thật trong browser; profiles 1280x720 hero và 960x540 group/algorithm. |
| `scripts/readme_gif_manifest.py` | Manifest semantic và asset checker. |
| `scripts/render_readme_docs.py` | Render README atlas và gallery từ catalog + manifest để tránh docs lệch. |
| `docs/assets/readme/` | 7 GIF nổi bật trong README. |
| `docs/assets/algorithm-demos/` | 24 GIF cá nhân và `manifest.json`. |
| `docs/algorithm-demo-gallery.md` | Gallery đầy đủ 24 thuật toán. |

## Tests

| Nhóm | Mục tiêu |
|---|---|
| `tests/test_solvers.py`, `tests/test_algorithm_contract_sweep.py`, `tests/test_path_solver_runner.py`, `tests/test_group6_decision_lab.py` | Solver correctness, structured Group 6 trace, root-value invariant, probability normalization và registry Play. |
| `tests/test_complex_models.py` | AND-OR, belief state, known matrix, conformant search and contingent policy evidence. |
| `tests/test_readme_gifs.py` | Registry 24 thuật toán, real demo evidence, live-web capture source, GIF nonblank/profile, README atlas references. |
| `tests/test_streamlit_app.py` | Streamlit AppTest cho UI chính, selectors, replay, đổi ảnh tức thời và image race. |
| `tests/test_image_algorithm_race.py` | Phân loại solved/partial/unavailable, chart contract và shared-step state. |
| `tests/test_academic.py`, `tests/test_text_quality.py`, `tests/test_localization.py` | Theory, wording, bilingual/localization and text quality. |

## Quality Gates

```bash
python -m compileall -q app.py core algorithms ui scripts
python scripts/generate-readme-gifs.py --check --check-readability
python -m pytest tests -q --cov=core --cov=algorithms --cov-report=term-missing --cov-fail-under=65
```
