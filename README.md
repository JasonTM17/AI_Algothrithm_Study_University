# 15-Puzzle AI Algorithm Simulator

Ứng dụng Streamlit phục vụ đồ án hoặc bài thi cuối kỳ môn Trí tuệ nhân tạo. Repo mô phỏng 15-puzzle để trình bày PEAS, không gian trạng thái, heuristic, trace tìm kiếm, bảng so sánh thuật toán, hand-tracing, CSP, môi trường phức tạp, game/chance extension và AI-vs-AI Tournament.

Điểm quan trọng nhất của repo là tính đúng học thuật. 15-puzzle chuẩn là bài toán một tác tử, xác định, quan sát đầy đủ, tĩnh, rời rạc và tuần tự. Vì vậy BFS, UCS, IDS, A*, IDA* là solver chuẩn; DFS, Greedy và local search là demo đối chiếu; CSP, AND-OR, belief-state, LRTA*, Minimax, Alpha-Beta, Expectimax và Tournament là phần mở rộng giáo dục, không phải solver tự nhiên của 15-puzzle chuẩn.

## Chạy nhanh

```bash
pip install -r requirements.txt
streamlit run app.py
```

Kiểm tra nhanh trên Windows PowerShell:

```powershell
$files = @('app.py') + (Get-ChildItem core,algorithms,ui -Filter *.py | ForEach-Object { $_.FullName })
python -m py_compile @files
python -m pytest tests/ -q
```

Môi trường phát triển đầy đủ:

```bash
pip install -r requirements-dev.txt
python -m compileall -q app.py core algorithms ui
python -m pytest tests/ -q
```

CI trên GitHub dùng Python 3.12, cài `requirements-dev.txt`, chạy compile, pytest với coverage tối thiểu 65%, rồi khởi động Streamlit và kiểm tra `/_stcore/health`.

## Luồng bảo vệ trên dashboard

| Bước | Tab | Nên trình bày |
|---|---|---|
| 1 | Play | Start/goal, ô trống `0`, move hợp lệ, solvability theo parity, challenge mode và certificate khi người chơi hoàn thành. |
| 2 | Run Algorithm | Chọn thuật toán, giải thích frontier, reached/best_g, trace, `g/h/f`, search tree và run certificate. |
| 3 | Compare | So sánh nhiều solver bằng cùng preset, seed, depth, timeout, max nodes, heuristic và action order. |
| 4 | Step Trace | Đọc từng dòng trace, frontier/reached, parent/child, export CSV khi cần chứng cứ. |
| 5 | Hand-Tracing Practice | Tập mở rộng node thủ công, kiểm tra thứ tự frontier và cây Graphviz do người học xây. |
| 6 | Theory | Bảo vệ PEAS, taxonomy, guarantee, proof card, decision guide và báo cáo chấm điểm. |
| 7 | Advanced | Chạy CSP, AND-OR, no/partial observation, LRTA*, Minimax, Alpha-Beta, Expectimax và AI-vs-AI Tournament như concept lab. |

## Mô hình 15-puzzle chuẩn

| Thành phần | Mô tả |
|---|---|
| State | Tuple 16 phần tử, là hoán vị của `0..15`; `0` là ô trống. |
| Goal mặc định | `(1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 0)`. |
| Action | `L`, `R`, `U`, `D`: trượt ô trống sang trái/phải/lên/xuống nếu hợp lệ. |
| Transition | Xác định: cùng state và action hợp lệ luôn sinh đúng một next state. |
| Cost | Mỗi move có cost `1`, nên path cost bằng số action. |
| Solvability | Hai state đi tới nhau được khi parity class bằng nhau; code dùng inversions và hàng của blank tính từ dưới lên. |
| Certificate | Path hợp lệ khi từng action áp dụng lên state trước sinh đúng state sau và state cuối bằng goal đã chọn. |

## PEAS

| PEAS | Diễn giải trong bài 15-puzzle |
|---|---|
| Performance | Tới goal, ít bước, ít node expanded/generated, ít bộ nhớ, runtime thấp. |
| Environment | Board 4x4, fully observable, deterministic, static, discrete, sequential, single-agent. |
| Actuators | Trượt ô trống theo `L/R/U/D` khi action hợp lệ. |
| Sensors | Toàn bộ board, vị trí ô trống, legal moves và heuristic estimate. |

## Phân loại thuật toán

| Vai trò | Thuật toán | Cách nói khi bảo vệ |
|---|---|---|
| Solver chuẩn | BFS, UCS, IDS, A*, IDA* | Dùng để giải 15-puzzle chuẩn; có guarantee khi không bị timeout/node cap và điều kiện lý thuyết thỏa. |
| Demo đối chiếu | DFS, Greedy Best-First, local search variants | Dùng để chỉ trade-off, thiếu optimality, local optimum, plateau hoặc phụ thuộc randomness. |
| Mở rộng minh họa | CSP, AND-OR, No Observation, Partial Observation, LRTA* | Đổi mô hình bài toán hoặc môi trường để học thêm AI; không phải solver tự nhiên nhất của 15-puzzle chuẩn. |
| Tournament/game/chance | AI-vs-AI Tournament, Minimax, Alpha-Beta, Expectimax | Tournament là lớp chấm điểm; Minimax/Alpha-Beta/Expectimax là extension game/chance. |

## Thuật toán dùng hợp lý và không hợp lý cho 15-puzzle

| Mức sử dụng | Thuật toán | Có hợp lý để giải 15-puzzle chuẩn? | Lý do chuẩn khi bảo vệ |
|---|---|---:|---|
| Rất hợp lý làm solver chuẩn | A*, IDA* | Có | Bám đúng mô hình state-space search; dùng `g+h` hoặc threshold `f`; có thể chứng minh tối ưu với heuristic admissible/consistent và đủ tài nguyên. |
| Hợp lý làm solver chuẩn cho puzzle nông | BFS, UCS, IDS | Có | Không cần heuristic; complete/optimal với unit step cost. Caveat là BFS/UCS tốn bộ nhớ, IDS expand lại node. |
| Hợp lý để minh họa trade-off, không nên chọn làm solver chính | DFS | Không nên | DFS tiết kiệm bộ nhớ nhưng không optimal và bị giới hạn bởi depth/resource cap. |
| Hợp lý để minh họa heuristic-only failure | Greedy Best-First | Không nên | Greedy chỉ nhìn `h(n)`, bỏ qua `g(n)`, nên có thể nhanh nhưng không có optimality certificate. |
| Hợp lý để dạy local optimum/plateau/randomness | Simple/Steepest/Stochastic/Random-Restart Hill Climbing, Local Beam, Simulated Annealing | Không nên | Local search không giữ frontier toàn cục, dễ kẹt hoặc phụ thuộc seed; dùng làm demo đối chiếu thay vì solver đáng tin cậy. |
| Hợp lý như mô hình hóa hoặc concept lab | CSP Definition, Constraint Propagation, Path Consistency, Global Constraints, Backtracking Search, Min-Conflicts, Constraint Graphs | Không nên gọi là solver chuẩn | CSP planning cần horizon/time-step; AC-3 chỉ chứng minh exact-horizon, Min-Conflicts dùng swap không phải legal blank move. |
| Hợp lý khi cố ý đổi environment/sensor | AND-OR, No Observation, Partial Observation, LRTA* | Không phải solver chuẩn | Chúng thay đổi transition, observability hoặc agent model; dùng để giải thích AI nâng cao. |
| Hợp lý để chấm điểm hoặc dạy game/chance | AI-vs-AI Tournament, Minimax, Alpha-Beta, Expectimax | Không phải solver chuẩn | Tournament là scoring layer; game/chance model thêm đối thủ hoặc xác suất không có trong PEAS chuẩn của 15-puzzle. |

## Heuristic trong repo

| Heuristic | Ý tưởng | Ưu điểm | Caveat |
|---|---|---|---|
| Misplaced Tiles | Đếm tile sai vị trí, bỏ qua blank. | Đơn giản, admissible, dễ giải thích. | Yếu, không biết tile cách goal bao xa. |
| Manhattan Distance | Tổng khoảng cách hàng/cột của từng tile tới goal, bỏ qua blank. | Admissible, consistent, rất hợp với 15-puzzle. | Vẫn có thể mở rộng nhiều node với puzzle sâu. |
| Linear Conflict | Manhattan cộng penalty hợp lệ cho các tile cùng goal-row/goal-column bị ngược thứ tự. | Mạnh hơn Manhattan, vẫn admissible/consistent trong repo. | Tính phức tạp hơn; lợi ích phụ thuộc state. |

A* và IDA* chỉ có optimality certificate khi heuristic admissible, path verified, goal reached, thuật toán kết thúc bằng `goal`, và run không dừng do resource limit.

## Nhóm thuật toán chính

### Uninformed Search

| Thuật toán | Cách chạy | Guarantee trong 15-puzzle |
|---|---|---|
| BFS | FIFO queue, mở node theo depth. | Complete và optimal với unit cost; tốn bộ nhớ `O(b^d)`. |
| DFS | Stack/depth-first với `max_depth`; code có reached set. | Không optimal; không complete khi depth limit thấp hoặc bị giới hạn tài nguyên. |
| UCS | Priority queue theo `g(n)`, có tie-breaker. | Complete, optimal với cost dương; với unit cost gần BFS. |
| IDS | Lặp depth-limited search từ depth 0 tới `max_depth`. | Complete và optimal với unit cost; ít bộ nhớ hơn BFS nhưng expand lại node. |

### Informed Search

| Thuật toán | Hàm đánh giá | Guarantee trong 15-puzzle |
|---|---|---|
| Greedy Best-First | Ưu tiên `h(n)` nhỏ nhất, bỏ qua `g(n)`. | Không optimal; dùng để so với A*. |
| A* | Ưu tiên `f(n)=g(n)+h(n)`. | Solver tham chiếu chính; complete/optimal với heuristic admissible consistent và đủ tài nguyên. |
| IDA* | DFS lặp theo threshold `f`. | Optimal với admissible heuristic; bộ nhớ thấp hơn A* nhưng re-expand nhiều. |

### Local Search

Local search không giữ frontier đầy đủ. Nhóm này tối ưu heuristic cục bộ của current state hoặc beam, nên phù hợp làm demo failure hơn làm solver chuẩn.

| Thuật toán | Điểm chính | Caveat |
|---|---|---|
| Simple Hill Climbing | Chọn neighbor đầu tiên có `h` tốt hơn. | Kẹt local optimum/plateau. |
| Steepest-Ascent Hill Climbing | Xét tất cả neighbor rồi chọn neighbor tốt nhất. | Vẫn kẹt nếu không có bước cải thiện. |
| Stochastic Hill Climbing | Random trong các neighbor tốt hơn. | Phụ thuộc seed, vẫn không complete/optimal. |
| Random-Restart Hill Climbing | Restart bằng random walk rồi leo đồi lại. | Tăng xác suất thành công, không chứng minh tối ưu. |
| Local Beam Search | Giữ `k` state tốt nhất. | Beam hẹp có thể loại mất nhánh đúng. |
| Simulated Annealing | Có thể nhận move xấu theo `exp(-delta/T)`. | Schedule/seed ảnh hưởng mạnh, không có finite optimality guarantee. |

### CSP và môi trường phức tạp

| Thành phần | Mô hình | Output |
|---|---|---|
| CSP Definition | Biến `X[t][p]`, action `A[t]`, ràng buộc initial/goal/AllDifferent/transition/legal move. | Mô tả `X, D, C`, chưa phải solver. |
| Constraint Propagation | AC-3 trên state-chain `S[0]..S[T]`. | Exact-horizon path hoặc domain wipe-out cho horizon đã chọn. |
| Backtracking Search | Bounded transition planning với heuristic value ordering. | Có thể tìm path nhỏ; fail không phải proof unsolvable. |
| Min-Conflicts | Local repair trên tile-placement conflicts. | Swap tile không phải legal blank move, nên không là solver hợp lệ. |
| AND-OR Search | Môi trường nondeterministic. | Conditional plan. |
| No/Partial Observation | Belief-state và observation filtering. | Minh họa sensor yếu; không phải solver chuẩn. |
| LRTA* | Online learning, cập nhật `H(state)` từng bước. | Có thể đi dài/lặp; không bằng A* offline về optimality. |

### AI-vs-AI, game tree và chance

15-puzzle không có đối thủ tự nhiên. Nhóm này tồn tại để bảo vệ kiến thức game/chance và cách chấm điểm hai solver.

| Thành phần | Ý tưởng | Caveat |
|---|---|---|
| AI-vs-AI Tournament | Hai solver chạy cùng start/goal; A* làm reference optimal cost. | Là scoring layer, không biến PEAS chuẩn thành adversarial. |
| Minimax | MAX muốn giảm heuristic/tới goal, MIN làm xấu utility. | Mô hình nhân tạo, không là optimal certificate cho puzzle chuẩn. |
| Alpha-Beta Pruning | Minimax có `alpha`, `beta` để cắt nhánh. | Chỉ đúng trong game-tree model. |
| Expectimax | MAX chọn action, CHANCE lấy expected utility theo probability. | Cần mô hình xác suất; path là sample/variation. |

Tournament scoring:

| Kết quả agent | Điểm |
|---|---:|
| Path hợp lệ, tới goal, cost bằng optimal cost | `+100` |
| Path hợp lệ, tới goal, cost dài hơn optimal | `max(10, round(100 * optimal_cost / actual_cost))` |
| Path hợp lệ nhưng chưa tới goal | `-10` |
| Timeout/resource limit/no path | `-20` |
| Exception/path invalid/action sai/state mismatch | `-50` |

## Cách đọc kết quả một run

| Trường | Ý nghĩa |
|---|---|
| `success` | Thuật toán báo thành công theo mô hình của nó; với extension, success có thể là model-success. |
| `path_verified` | Mỗi action trong path là legal blank move. |
| `goal_reached` | State cuối bằng goal đã chọn. |
| `optimality_proven` | Chỉ true khi success, path legal, goal reached, algorithm optimal và termination là `goal`. |
| `nodes_expanded` | Số node/state được mở rộng; không luôn so sánh 1-1 giữa các họ thuật toán. |
| `nodes_generated` | Số candidate sinh ra. |
| `max_frontier_size` | Đỉnh bộ nhớ frontier. |
| `trace` | Evidence gồm action, parent, frontier/reached, `g/h/f`, reason; trace bị giới hạn để UI vẫn nhanh. |

## Cấu trúc repo

```text
app.py                         Streamlit entrypoint và tab router
core/                          puzzle logic, heuristic, metrics, taxonomy, tournament scoring
algorithms/                    uninformed, informed, local, CSP, complex, adversarial algorithms
ui/                            Streamlit tabs, components, styles, localization, image tiles
docs/                          PDR, kiến trúc, chuẩn code, test plan, roadmap, tài liệu học thuật
tests/                         solver, heuristic, runtime, tournament, UI, academic regression tests
.github/workflows/quality.yml  compile, pytest coverage, Streamlit health smoke test
```

## Tài liệu chuyên sâu

- [Tổng quan dự án và PDR](docs/project-overview-pdr.md)
- [Tóm tắt codebase](docs/codebase-summary.md)
- [Kiến trúc hệ thống](docs/system-architecture.md)
- [Chuẩn code và quy ước phát triển](docs/code-standards.md)
- [Hướng dẫn triển khai](docs/deployment-guide.md)
- [Design guidelines](docs/design-guidelines.md)
- [Roadmap dự án](docs/project-roadmap.md)
- [Kế hoạch kiểm thử thuật toán](docs/algorithm-test-plan.md)
- [Tham chiếu học thuật về các nhóm thuật toán](docs/algorithm-groups-academic-reference.md)
- [Cây nhánh và release](docs/branch-and-release-tree.md)

## Ghi chú bảo vệ nhanh

- Nói PEAS trước khi nói thuật toán.
- A* là solver tham chiếu tốt nhất khi dùng Manhattan/Linear Conflict và không bị giới hạn tài nguyên.
- UCS và BFS đều optimal vì mỗi move cost 1; UCS tổng quát hơn khi cost khác nhau.
- Greedy có heuristic nhưng không optimal vì bỏ qua `g(n)`.
- Hill climbing/local search tốt để minh họa local optimum, không nên gọi là solver đáng tin cậy.
- CSP, game, chance, no-observation và partial-observation là extension học thuật, phải tách khỏi 15-puzzle chuẩn.
- Mọi benchmark phải ghi seed, depth, heuristic, action order, timeout và max nodes.
- Path hợp lệ, path tới goal và path tối ưu là ba claim khác nhau; dùng certificate của app để chứng minh.
