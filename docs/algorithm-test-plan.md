# Kế Hoạch Kiểm Thử Thuật Toán

Mục tiêu: chứng minh thuật toán, trace, UI học thuật, GIF README/gallery và các mô hình mở rộng hoạt động đúng theo ranh giới đã công bố.

## Test Oracle

| Oracle | Cách kiểm chứng |
|---|---|
| State hợp lệ | Tuple 16 phần tử là hoán vị `0..15`. |
| Legal path | `validate_solution_path`, `validate_path` và `SearchResult.path_verified`. |
| Goal reached | State cuối bằng `goal_state`. |
| Optimality | Chỉ true khi thuật toán optimal, legal path, goal reached và termination là `goal`. |
| Trace | Có action, `g/h/f`, frontier/reached, parent/child hoặc model-specific evidence. |
| Extension caveat | CSP/AND-OR/belief/LRTA*/game/chance không bị gọi là solver chuẩn của 15-puzzle. |
| Media evidence | GIF README/gallery có manifest semantic, mở được, nonblank, đúng profile và sinh từ solver/model thật. |

## Nhóm Test Chính

| File | Mục tiêu |
|---|---|
| `tests/test_puzzle.py`, `tests/test_heuristics.py` | State, solvability, heuristic admissibility corpus. |
| `tests/test_solvers.py`, `tests/test_optimality_corpus.py` | Solver correctness and optimality certificate. |
| `tests/test_algorithm_contract_sweep.py` | Registry/dispatch sweep cho nhiều scramble depth, custom goal, false-claim guard. |
| `tests/test_complex_models.py` | AND-OR, belief matrix, LRTA*, fallback votes/reasons. |
| `tests/test_search_tree_evidence.py` | Search tree edge legality and readable evidence. |
| `tests/test_readme_gifs.py` | 6 nhóm/28 GIF specs, profile/theme manifest, README atlas, gallery references. |
| `tests/test_streamlit_app.py` | Streamlit AppTest cho Play/Run/Advanced workflows. |
| `tests/test_academic.py`, `tests/test_text_quality.py`, `tests/test_localization.py` | Theory, wording, bilingual contract. |

## Media Profiles

| Profile | Size | Dùng cho |
|---|---:|---|
| `hero` | 1280x720 | A* image replay ở đầu README. |
| `group` | 960x540 | 6 GIF đại diện nhóm. |
| `algorithm` | 960x540 | 28 GIF từng thuật toán. |

Themes:

- `light`: mặc định cho README GitHub.
- `dark`: tùy chọn để đồng bộ app Streamlit.

## Required Commands

```bash
python -m compileall -q app.py core algorithms ui scripts
python scripts/generate-readme-gifs.py --check --check-readability
python -m pytest tests -q --cov=core --cov=algorithms --cov-report=term-missing --cov-fail-under=65
```

Focused checks after media/doc edits:

```bash
python -m pytest tests/test_readme_gifs.py tests/test_algorithm_contract_sweep.py tests/test_text_quality.py -q
```

## Manual Smoke

Desktop 1440x900 and mobile 390x844:

- Play number board: tile palette neutral, no color swap by row, A* Next/Auto one step at a time.
- Play image board: image pieces move with `play_state`.
- Run A*: readable tree is visible and not squeezed.
- Run Local Search: candidate evidence visible.
- Run AND-OR: control says deflection outcome support, not probability weight.
- Advanced No/Partial Observation: known matrix with `_` unknown works and trace explains belief/fallback.
- Theory Group 6: Minimax is worst-case robustness, not a real opponent.
- README/Gallery: GIFs load, are readable and have direct 28-algorithm coverage.

## Pass Criteria

- Full suite pass.
- No raw localization key in UI.
- No stale wording: AND-OR support is not probability weighting; Minimax MIN is not a real 15-puzzle opponent.
- `python scripts/generate-readme-gifs.py --check --check-readability` passes against committed assets.
- README contains 6 groups and 28 algorithms with real GIF references.
