# Kế hoạch kiểm thử thuật toán 15-Puzzle AI

Tài liệu này định nghĩa kế hoạch kiểm thử cho dashboard 15-Puzzle AI. Mục tiêu là chứng minh thuật toán, trace, UI học thuật và các mô hình mở rộng hoạt động đúng theo ranh giới đã công bố trong repo.

## Phạm vi

| Nhóm | Thuật toán | Mục tiêu kiểm thử |
|---|---|---|
| Uninformed Search | BFS, DFS, UCS, IDS | Legal path, completeness/optimality trong điều kiện bounded, frontier/reached, depth limit. |
| Informed Search | Greedy, A*, IDA* | Heuristic theo goal, admissibility corpus, optimality certificate, tie-breaking. |
| Local Search | Hill climbing variants, Local Beam, Simulated Annealing | Stuck/local optimum, randomness seed, partial trajectory không bị gắn nhãn solution sai. |
| CSP | Definition, AC-3, Path Consistency, Global Constraints, Backtracking, Min-Conflicts, Constraint Graphs | Exact-horizon certificate, ràng buộc, bounded planning, không claim solver tự nhiên. |
| Complex Environments | AND-OR, No Observation, Partial Observation, LRTA* | Belief state, observation, nondeterministic branches, online update, không claim solver tự nhiên. |
| AI-vs-AI/Game-Chance | AI-vs-AI Tournament, Minimax, Alpha-Beta, Expectimax | Tournament scoring, reference optimal, tie-break, utility và caveat game/chance. |

## Test oracle

| Oracle | Cách kiểm chứng |
|---|---|
| State hợp lệ | Mỗi state là hoán vị đúng của `0..15`; invalid input bị reject bằng `ValueError`. |
| Solvability | `is_solvable(start, goal)` dùng parity class của goal tùy chỉnh. |
| Legal path | `validate_solution_path` và `SearchResult.path_verified` xác nhận từng action bằng blank move. |
| Goal reached | `SearchResult.goal_reached` chỉ true khi state cuối bằng `goal_state` đã chọn. |
| Optimality | BFS/UCS/A*/IDA*/IDS chỉ có `optimality_proven` khi success, legal path, goal reached và termination là `goal`. |
| Heuristic | Misplaced, Manhattan, Linear Conflict tính theo goal tùy chỉnh và không vượt exact distance trong corpus nhỏ. |
| Trace evidence | Frontier/reached, parent, action, `g/h/f` và tree edge là evidence có thể audit. |
| Randomness | Run/Advanced ghi variation seed; Compare/Tournament/Hand-Tracing dùng seed rõ để tái lập. |
| Goal metadata | Mọi `SearchResult`, kể cả fail/concept model, giữ `goal_state` đã chọn. |
| Tournament reference | Mỗi scored round có A* reference optimal cost dùng chung cho hai AI. |

## Ma trận test bắt buộc

| ID | Case | Input | Kỳ vọng |
|---|---|---|---|
| ALG-01 | Goal chuẩn đã giải | `GOAL_STATE` | Solver trả path một state, cost 0, không crash UI slider. |
| ALG-02 | Một bước tới goal | `(1..14,0,15)` | BFS/A*/UCS trả cost 1, legal action đúng. |
| ALG-03 | Goal tùy chỉnh | `start=GOAL_STATE`, `goal=ONE_MOVE` | Solver dùng goal tùy chỉnh, path cuối bằng `ONE_MOVE`. |
| ALG-04 | Không giải được theo goal | Hai state khác parity | Solver complete trả fail nhanh, không sinh claim solution. |
| ALG-05 | BFS shortest path | Puzzle nông depth 2-5 | Cost bằng exact depth. |
| ALG-06 | UCS với unit cost | Cùng puzzle nông | Cost bằng BFS. |
| ALG-07 | IDS resource guard | `max_nodes` nhỏ | Dừng khi chạm node cap, không tiếp tục recursion âm thầm. |
| ALG-08 | A* heuristic | Manhattan/Linear Conflict | Path optimal trong corpus nông. |
| ALG-09 | Greedy contrast | Preset Greedy suboptimal | Không claim optimal; A* có optimal certificate. |
| ALG-10 | Hill Climbing stuck | Preset local optimum | Result có caveat, không gắn nhãn solved sai. |
| ALG-11 | Local stochastic seed | Stochastic/Annealing | Seed được ghi, kết quả tái lập khi seed cố định. |
| ALG-12 | Search tree edge | BFS/A* | Mỗi edge áp dụng action từ parent ra child. |
| ALG-13 | Tournament full score | Hai agent path optimal | Điểm 100 và tie/draw đúng khi chất lượng bằng nhau. |
| ALG-14 | Tournament reduced score | Legal path dài hơn optimal | Điểm `max(10, round(100 * optimal/actual))`. |
| ALG-15 | Tournament invalid path | Path/action mismatch | Điểm `-50`. |
| ALG-16 | Trace export | Sau khi chạy solver | CSV có dữ liệu node/parent/frontier/reached. |
| ALG-17 | AC-3 exact horizon | Start cách goal đúng `T` | Trả path hợp lệ dài `T`. |
| ALG-18 | AC-3 wipe-out | Horizon sai parity/độ dài | Domain wipe-out, không claim solution. |
| ALG-19 | Group comparison | Mỗi group trên Theory | Mỗi thuật toán có Time, Space, Steps/Output và Guarantee. |
| ALG-20 | Registry contract sweep | Mọi thuật toán hiển thị | Dispatch kwargs đúng, custom goal và certificate không lệch. |

## Kiểm thử UI/UX thuật toán

| Tab | Kỳ vọng |
|---|---|
| Play | Start/Goal preview rõ, nhập goal tùy chỉnh, solvability cập nhật, challenge score không crash với history sai. |
| Run Algorithm | Contract rõ, mỗi run có variation metadata, result metric không che trace, search tree hợp lệ. |
| Compare | Benchmark reset khi thay input/goal/seed; seed stochastic được ghi; bảng không tràn ngang trên mobile. |
| Step Trace | Empty state có hướng dẫn; detail slider không crash khi trace có 0 hoặc 1 dòng; CSV export tồn tại. |
| Hand-Tracing | Frontier order đúng theo thuật toán, Graphviz tree dùng explicit parent/child edge. |
| Theory | Taxonomy không thiếu thuật toán; mỗi group có bảng complexity; caveat extension rõ. |
| Advanced | Không còn demo đã bị loại; CSP/complex/game/tournament có label concept/extension/scoring. |

## Lệnh kiểm thử

Kiểm tra runtime Python:

```bash
python -m compileall -q app.py core algorithms ui
python -m pytest tests -q
```

Kiểm tra theo CI:

```bash
python -m pytest tests -q --cov=core --cov=algorithms --cov-report=term-missing --cov-fail-under=65
```

Kiểm tra Streamlit smoke:

```bash
streamlit run app.py --server.port 8510 --server.headless true
```

Sau đó mở hoặc poll:

```text
http://127.0.0.1:8510/_stcore/health
```

## Kịch bản kiểm thử thủ công

Desktop:

- Play: đổi start/goal, chơi vài move, chạy AI assistance, kiểm challenge certificate.
- Run Algorithm: chạy BFS và A*, kiểm trace tuple, search tree, path animation.
- Compare: chạy A* vs Greedy trên preset nông, kiểm seed và goal tùy chỉnh.
- Advanced: chạy AI-vs-AI Tournament với A* vs Greedy, replay hai board trên cùng step.
- Advanced: chạy Constraint Propagation với horizon đúng và horizon sai.
- Step Trace: kiểm empty state và CSV export.
- Theory: kiểm PEAS, taxonomy, proof cards và grading report.

Mobile 390x844:

- Sidebar không che nội dung sau khi đóng.
- Board và image tiles giữ kích thước bấm được.
- Bảng trace/dataframe không tạo overflow vô nghĩa.
- Button text không tràn khỏi container.

## Tiêu chí pass

- Không có exception Streamlit trong các tab chính.
- Full test suite pass.
- Mọi solver success có `path_verified=True` và state cuối bằng goal đã chọn.
- Mọi result giữ `goal_state` đã chọn, kể cả fail, timeout, model-success hoặc concept-only.
- Không có claim sai như "Greedy tối ưu" hoặc "Minimax là solver tự nhiên của 15-puzzle".
- Tournament không chấm khi reference A* không chứng minh được optimal path.
- Hai AI cùng solver, board và tham số phải draw; runtime noise không tự tạo winner.
- IDS/IDA* phải dừng ngay khi chạm `max_nodes`, kể cả bên trong recursive pass.
- Trace và search tree có evidence: node label, action, `g/h/f`, parent, frontier/reached và legal edge.
- Các demo mở rộng được label là concept/extension/tournament scoring layer, không bị trộn vào solver chuẩn.
