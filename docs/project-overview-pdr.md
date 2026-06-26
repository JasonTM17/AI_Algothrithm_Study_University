# Tổng quan dự án và PDR

## Mục đích

15-Puzzle AI Algorithm Simulator là ứng dụng Streamlit dùng cho bài thi cuối kỳ môn Trí tuệ nhân tạo. Dự án lấy 15-puzzle làm bài toán trung tâm để trình bày search, heuristic, PEAS, trace, chứng chỉ lời giải, so sánh thuật toán và các mô hình mở rộng.

Sản phẩm được thiết kế cho lớp học: người chấm có thể chạy thuật toán, xem chứng cứ từng bước, đọc taxonomy học thuật và kiểm tra các claim về completeness, optimality, heuristic, resource limit và environment model.

## Đối tượng sử dụng

| Đối tượng | Nhu cầu |
|---|---|
| Giảng viên | Chấm nhanh tính đúng học thuật, xem bằng chứng chạy được và báo cáo bảo vệ. |
| Sinh viên | Thực hành trace, so sánh thuật toán, thử start/goal tùy chỉnh, học ranh giới giữa solver và extension. |
| Người bảo trì | Có tài liệu cấu trúc, chuẩn code, test plan và roadmap để tiếp tục phát triển. |

## Phạm vi sản phẩm

| Trong phạm vi | Ngoài phạm vi |
|---|---|
| Web app Streamlit trong `app.py`. | Desktop app hoặc EXE wrapper. |
| Board 4x4, state là hoán vị `0..15`. | Board kích thước khác. |
| Solver chuẩn: BFS, UCS, IDS, A*, IDA*. | Claim rằng mọi demo đều là solver đáng tin cậy. |
| Demo đối chiếu: DFS, Greedy, local search. | Dùng local search để chứng minh tối ưu. |
| Concept lab: CSP, AND-OR, belief-state, LRTA*, game/chance, Tournament. | Gộp extension vào leaderboard solver chuẩn. |
| Kiểm thử bằng compile, pytest, Streamlit health. | Backend API, database, auth hoặc secret management. |

## Định vị học thuật

15-puzzle chuẩn trong repo là môi trường một tác tử, xác định, quan sát đầy đủ, tĩnh, rời rạc và tuần tự. Điều này dẫn tới phân loại:

| Vai trò | Thuật toán |
|---|---|
| Solver chuẩn | BFS, UCS, IDS, A*, IDA* |
| Demo đối chiếu | DFS, Greedy Best-First, Simple/Steepest/Stochastic/Random-Restart Hill Climbing, Local Beam, Simulated Annealing |
| Mở rộng minh họa | CSP Definition, Constraint Propagation, Path Consistency, Global Constraints, Backtracking Search, Min-Conflicts, Constraint Graphs, AND-OR, No Observation, Partial Observation, LRTA* |
| Tournament/game/chance | AI-vs-AI Tournament, Minimax, Alpha-Beta Pruning, Expectimax |

AI-vs-AI Tournament chỉ là lớp chấm điểm hai solver agent trên cùng puzzle. Mỗi round dùng A* làm reference optimal certificate; đường tối ưu hợp lệ được 100 điểm, đường hợp lệ dài hơn bị giảm theo `optimal_cost / actual_cost`, fail/timeout bị trừ điểm và invalid path bị phạt mạnh nhất.

## Yêu cầu chức năng

| ID | Yêu cầu | Bằng chứng trong repo |
|---|---|---|
| F-01 | Người dùng chọn hoặc nhập start/goal tùy chỉnh. | `ui/start_goal_controls.py`, `ui/start_goal_state.py`, sidebar trong `app.py`. |
| F-02 | App kiểm tra solvability theo goal đã chọn. | `core/puzzle.py:is_solvable`. |
| F-03 | Chạy solver chuẩn và trả `SearchResult`. | `algorithms/uninformed.py`, `algorithms/informed.py`, `core/metrics.py`. |
| F-04 | Trace và search tree có parent/child edge hợp lệ. | `TraceStep`, `SearchTreeNode`, `SearchTreeEdge`, `search_tree_to_dot`. |
| F-05 | Compare chạy nhiều thuật toán với preset và seed rõ ràng. | `ui/compare_tab.py`, `core/comparison.py`. |
| F-06 | Theory hiển thị PEAS, taxonomy, proof card, rubric và báo cáo chấm. | `ui/theory_tab.py`, `ui/academic_panels.py`, `core/academic.py`, `core/academic_proofs.py`. |
| F-07 | Advanced tách CSP, complex environment, game/chance và Tournament khỏi solver chuẩn. | `ui/advanced_tab.py`, `algorithms/csp.py`, `algorithms/complex_env.py`, `algorithms/adversarial.py`. |
| F-08 | Tournament dùng A* reference và replay hai trajectory. | `core/ai_vs_ai_tournament.py`, `ui/ai_vs_ai_tournament.py`, `ui/tournament_replay.py`. |
| F-09 | Play có puzzle board, image mode và challenge score. | `ui/play_tab.py`, `ui/sample_images.py`, `core/gameplay.py`. |
| F-10 | UI có localization tiếng Việt/English. | `ui/localization.py`, `tests/test_localization.py`. |

## Yêu cầu phi chức năng

| Nhóm | Yêu cầu |
|---|---|
| Đúng học thuật | Không gọi extension là solver chuẩn; không claim tối ưu khi thiếu certificate. |
| Hiệu năng demo | Có timeout, max nodes, trace cap và cảnh báo resource limit. |
| Tái lập | Benchmark, Tournament và Hand-Tracing dùng seed/action order rõ ràng; Run có variation metadata. |
| Khả dụng lớp học | Chạy bằng `streamlit run app.py`, không cần database hoặc secret. |
| Dễ chấm | Có test plan, docs học thuật, báo cáo grading và CI. |
| Mobile | Sidebar, board, bảng trace và cards phải đọc được trên viewport nhỏ. |

## Tiêu chí thành công

- App chạy không lỗi Streamlit ở các tab Play, Run Algorithm, Compare, Step Trace, Hand-Tracing, Theory và Advanced.
- Mọi path solution thành công phải có `path_verified=True` và state cuối bằng `goal_state`.
- `optimality_proven=True` chỉ xuất hiện khi thuật toán optimal, path hợp lệ, tới goal và termination là `goal`.
- CSP AC-3 trả exact-horizon path hoặc domain wipe-out cho horizon đã chọn, không claim shortest path toàn cục.
- Tournament không chấm điểm khi A* reference không chứng minh được optimal path.
- Tài liệu và UI nêu rõ ranh giới solver chuẩn, demo đối chiếu, extension và tournament/game.
- Full test suite pass theo workflow `.github/workflows/quality.yml`.
