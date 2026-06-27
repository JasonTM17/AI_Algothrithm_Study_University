# Tóm tắt codebase

## Entry point và điều hướng

| File | Vai trò |
|---|---|
| `app.py` | Streamlit entrypoint, cấu hình page, sidebar, language selector, start/goal controls và tab router. |
| `ui/play_tab.py` | Board chơi thủ công, image mode, AI replay và challenge scoring. |
| `ui/run_tab.py` | Chạy từng thuật toán, hiển thị contract start/goal, metrics, trace, readable search tree và Graphviz evidence. |
| `ui/compare_tab.py` | Benchmark nhiều thuật toán theo preset, goal tùy chỉnh, seed và giới hạn tài nguyên. |
| `ui/trace_tab.py` | Đọc trace đã lưu, bảng chi tiết và CSV export. |
| `ui/hand_tracing.py` | Bài tập mở rộng node thủ công và Graphviz tree từ các edge người học chọn. |
| `ui/theory_tab.py` | Trang Theory: PEAS, taxonomy, proof cards, decision guide, report export. |
| `ui/advanced_tab.py` | Concept lab: CSP, complex environments, game/chance và AI-vs-AI Tournament. |

## Core domain

| File | Nội dung chính |
|---|---|
| `core/puzzle.py` | `GOAL_STATE`, validate state, blank movement, parity solvability, scramble, parse state, validate path. |
| `core/heuristics.py` | Misplaced Tiles, Manhattan Distance, Linear Conflict, `get_heuristic`. |
| `core/node.py` | Node search tree cơ bản, reconstruct path/actions. |
| `core/metrics.py` | `TraceStep`, `SearchTreeNode`, `SearchTreeEdge`, `SearchResult`, DOT serialization. |
| `core/solver_dispatch.py` | Build kwargs an toàn cho từng solver từ UI. |
| `core/randomness.py` | Run variation, seed, action order và đánh dấu solver stochastic. |
| `core/gameplay.py` | Validate player run và score challenge so với optimal distance. |
| `core/comparison.py` | Compact action path và nhóm các verified path giống nhau. |
| `core/ai_vs_ai_tournament.py` | Tournament configs, per-round scoring, A* reference, tie-break. |
| `core/academic.py` | Taxonomy, PEAS table và recommendation rubric. |
| `core/academic_proofs.py` | Proof cards, exam templates, benchmark presets và decision guide. |
| `core/algorithm_comparison.py` | Bảng so sánh time, space, step/output, guarantee theo từng group. |
| `core/academic_report.py` | Sinh báo cáo chấm điểm học thuật. |

## Algorithms

| File | Thuật toán |
|---|---|
| `algorithms/uninformed.py` | BFS, DFS, UCS, IDS. |
| `algorithms/informed.py` | Greedy Best-First, A*, IDA*. |
| `algorithms/local_search.py` | Simple/Steepest/Stochastic/Random-Restart Hill Climbing, Local Beam, Simulated Annealing. |
| `algorithms/csp.py` | CSP Definition, Constraint Propagation, Path Consistency, Global Constraints, Backtracking Search, Min-Conflicts, Constraint Graphs. |
| `algorithms/csp_ac3.py` | AC-3 executable trên state-chain `S[0]..S[T]`. |
| `algorithms/complex_env.py` | AND-OR, No Observation, Partially Observable Search, LRTA*. |
| `algorithms/adversarial.py` | Minimax, Alpha-Beta Pruning, Expectimax. |

## UI support

| File | Vai trò |
|---|---|
| `ui/components.py` | Board renderer, metrics, trace table, readable search tree, Graphviz evidence, algorithm evaluation cards. |
| `ui/styles.py` | CSS cho dashboard Streamlit. |
| `ui/localization.py` | Từ điển English/Tiếng Việt và hàm translate. |
| `ui/sample_images.py` | Built-in image tiles cho board. |
| `ui/start_goal_controls.py` | Editor start/goal trong sidebar và các tab. |
| `ui/belief_controls.py` | Known-tile matrix 4x4 cho No/Partial Observation; `_` nghĩa là unknown. |
| `ui/academic_panels.py` | Các panel PEAS, rubric, taxonomy, proof, report. |
| `ui/syllabus_coverage_panels.py` | Mapping đề cương sang vị trí trong app. |
| `ui/ai_vs_ai_tournament.py` | UI cấu hình và kết quả Tournament. |
| `ui/tournament_replay.py` | Replay hai trajectory trên cùng timeline. |
| `ui/assets/` | Ảnh mẫu cho puzzle ảnh. |
| `docs/assets/` | GIF/diagram dùng trong README và tài liệu. |

## Tests

| Nhóm test | Mục tiêu |
|---|---|
| `tests/test_puzzle.py`, `tests/test_heuristics.py` | Cơ chế puzzle, solvability, heuristic. |
| `tests/test_solvers.py`, `tests/test_optimality_corpus.py` | Solver correctness, custom goal, optimality corpus. |
| `tests/test_search_tree_evidence.py`, `tests/test_algorithm_contract_sweep.py` | Certificate, trace, search tree và registry contract. |
| `tests/test_csp_ac3.py`, `tests/test_complex_models.py` | AC-3, belief-state, observation và LRTA*. |
| `tests/test_ai_vs_ai_tournament.py`, `tests/test_gameplay.py` | Tournament scoring và challenge scoring. |
| `tests/test_streamlit_app.py` | Streamlit AppTest cho các tab và workflow chính. |
| `tests/test_academic.py`, `tests/test_academic_algorithm_matrix.py` | Taxonomy, PEAS, proof cards, syllabus coverage. |
| `tests/test_localization.py`, `tests/test_text_quality.py` | Localization và chống lỗi mã hóa/mojibake. |
| `tests/test_runtime_integrity.py`, `tests/test_randomness.py` | Compile/import, dispatch kwargs, seed và action order. |

## Tài liệu liên quan

- [Tổng quan dự án và PDR](./project-overview-pdr.md)
- [Kiến trúc hệ thống](./system-architecture.md)
- [Chuẩn code và quy ước phát triển](./code-standards.md)
- [Kế hoạch kiểm thử thuật toán](./algorithm-test-plan.md)
- [Tham chiếu học thuật](./algorithm-groups-academic-reference.md)
