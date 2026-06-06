# 15-Puzzle AI Algorithm Simulator

Ứng dụng Streamlit mô phỏng và so sánh **27 thuật toán AI** trên trò chơi 15-Puzzle, được thiết kế cho môn Trí tuệ nhân tạo.

## Khởi động nhanh

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## Nhóm 1: Uninformed Search (Tìm kiếm không có thông tin)

| Thuật toán | Hoàn chỉnh | Tối ưu | Độ phức tạp thời gian | Độ phức tạp bộ nhớ | Phù hợp 15-Puzzle? |
|-----------|-----------|--------|----------------------|---------------------|-------------------|
| **BFS** | ✅ Yes | ✅ Yes* | O(b^d) | O(b^d) | ⚠️ Hạn chế — tốn bộ nhớ |
| **DFS** | ❌ No† | ❌ No | O(b^m) | O(bm) | ❌ Không — có thể lặp vô hạn |
| **UCS** | ✅ Yes | ✅ Yes | O(b^(C*/ε)) | O(b^(C*/ε)) | ⚠️ Giống BFS với unit cost |
| **IDS** | ✅ Yes | ✅ Yes* | O(b^d) | O(bd) | ✅ Tốt — tiết kiệm bộ nhớ |

\* Tối ưu với unit cost. † Complete với depth limit.

- **BFS**: Duyệt theo chiều rộng, tìm đường ngắn nhất nhưng tốn rất nhiều bộ nhớ. Frontier = Queue.
- **DFS**: Duyệt theo chiều sâu, nhanh nhưng không đảm bảo tìm lời giải. Frontier = Stack.
- **UCS**: Mở rộng node có cost nhỏ nhất (g(n)). Với unit cost = BFS. Frontier = Priority Queue.
- **IDS**: Lặp DFS với depth limit tăng dần. Kết hợp ưu điểm BFS (tối ưu) và DFS (tiết kiệm bộ nhớ).

---

## Nhóm 2: Informed Search (Tìm kiếm có thông tin)

| Thuật toán | Hoàn chỉnh | Tối ưu | Heuristic | Phù hợp 15-Puzzle? |
|-----------|-----------|--------|-----------|-------------------|
| **Greedy Best-First** | ❌ No | ❌ No | h(n) | ⚠️ Nhanh nhưng không tối ưu |
| **A*** | ✅ Yes | ✅ Yes‡ | g(n) + h(n) | ✅ Lựa chọn tốt nhất |
| **IDA*** | ✅ Yes | ✅ Yes‡ | g(n) + h(n) | ✅ Tốt — tiết kiệm bộ nhớ |

‡ Tối ưu nếu heuristic admissible + consistent.

- **Greedy Best-First**: Chọn node có h(n) nhỏ nhất. Nhanh nhưng dễ bị kẹt ở local minimum.
- **A***: f(n) = g(n) + h(n). Tối ưu và hoàn chỉnh với heuristic admissible. Lựa chọn tốt nhất cho 15-Puzzle.
- **IDA***: Iterative Deepening A*. Dùng threshold tăng dần theo f-value. Tối ưu, tiết kiệm bộ nhớ.

### Heuristics hỗ trợ

| Heuristic | Admissible | Consistent | Mô tả |
|-----------|------------|-----------|-------|
| Misplaced Tiles | ✅ | ✅ | Đếm số ô không đúng vị trí |
| Manhattan Distance | ✅ | ✅ | Tổng khoảng cách Manhattan mỗi ô đến vị trí đích |
| Linear Conflict | ✅ | ✅ | Manhattan + 2 × số xung đột tuyến tính |

---

## Nh�óm 3: Local Search (Tìm kiếm cục bộ)

| Thuật toán | Hoàn chỉnh | Tối ưu | Random | Phù hợp 15-Puzzle? |
|-----------|-----------|--------|--------|-------------------|
| **Simple Hill Climbing** | ❌ | ❌ | No | ❌ Kẹt local optimum |
| **Steepest-Ascent HC** | ❌ | ❌ | No | ❌ Kẹt local optimum |
| **Stochastic HC** | ❌ | ❌ | Yes | ❌ Vẫn kẹt |
| **Random-Restart HC** | ✅‖ | ❌ | Yes | ⚠️ Có thể tìm thấy lời giải |
| **Local Beam Search** | ❌ | ❌ | Yes* | ⚠️ Tốt hơn HC đơn lẻ |
| **Simulated Annealing** | ✅‖ | ❌ | Yes | ⚠️ Có thể, không đáng tin cậy |

‖ Asymptotically complete với lịch làm ngu đủ chậm.

- **Hill Climbing**: Leo đồi — luôn chọn neighbor tốt hơn. Dễ bị kẹt ở local optimum, plateau, ridge.
- **Simulated Annealing**: Cho phép chọn neighbor tệ hơn với xác suất P(ΔE) = e^(-ΔE/T). Nhiệt độ T giảm dần theo lịch làm ngu (cooling schedule).

---

## Nhóm 4: Complex Environments (Môi trường phức tạp)

| Thuật toán | Mô hình | Phù hợp 15-Puzzle? |
|-----------|--------|-------------------|
| **AND-OR Search** | Nondeterministic | Mô phỏng — MIN cố gắng cản trở |
| **No Observation** | Belief state | Mô phỏng — không quan sát được trạng thái |
| **Partially Observable** | Belief state + observation | Mô phỏng — quan sát một phần |
| **LRTA*** | Online learning | ⚠️ Học trực tuyến — cập nhật h(n) mỗi bước |

- **AND-OR**: Xây dựng cây AND-OR cho môi trường nondeterministic. AND-node: tất cả kết quả phải handle. OR-node: chọn hành động tốt nhất.
- **No Observation**: Tìm hành động trong môi trường không quan sát được. Duy trì belief state (tập các trạng thái có thể).
- **LRTA***: Online search — bắt đầu mà không có mô hình môi trường. Cập nhật heuristic sau mỗi bước: h(s) ← max(h(s), cost(s,a) + h(s')).

---

## Nhóm 5: CSP (Constraint Satisfaction Problems)

| Thuật toán | Mô tả | Phù hợp 15-Puzzle? |
|-----------|-------|-------------------|
| **CSP Definition** | Định nghĩa 15-Puzzle như CSP với 16 biến | ❌ Không phù hợp tự nhiên |
| **Constraint Propagation** | AC-3 cho miền giá trị | ❌ Giảm miền giá trị |
| **Path Consistency** | Kiểm tra consistency theo cặp | ❌ Phức tạp hơn AC-3 |
| **Global Constraints** | Alldifferent constraint | ❌ Nhưng có thể áp dụng |
| **Backtracking Search** | MRV + LCV heuristic | ❌ Không hiệu quả |
| **Min-Conflicts** | Chọn giá trị xung đột ít nhất | ❌ Tốt cho N-Queens hơn |
| **Constraint Graphs** | Phân tích đồ thị ràng buộc | ❌ Đồ thị 15-Puzzle khít |

15-Puzzle không phải CSP tự nhiên — CSP phù hợp hơn cho bài toán như N-Queens, Sudoku. Các thuật toán CSP được mô phỏng cho mục đích học thuật.

---

## Nhóm 6: Adversarial/Stochastic Search (Tìm kiếm đối kháng/ngẫu nhiên)

| Thuật toán | Đối thủ | Xác suất | Phù hợp 15-Puzzle? |
|-----------|--------|---------|-------------------|
| **Minimax** | MAX vs MIN | No | ❌ 15-Puzzle không phải 2-player |
| **Alpha-Beta Pruning** | MAX vs MIN | No | ❌ Cùng kết quả Minimax, ít node hơn |
| **Expectimax** | MAX vs CHANCE | Yes | ❌ Mô phỏng stochastic |

- **Minimax**: MAX (solver) chọn hành động maximize utility, MIN (adversary) chọn minimize. 15-Puzzle không có đối thủ — đây là mô phỏng học thuật.
- **Alpha-Beta Pruning**: Cùng kết quả Minimax nhưng cắt tỉa nhánh không ảnh hưởng kết quả. Pruned branches != kết quả sai.
- **Expectimax**: Thay vì MIN, có CHANCE node tính kỳ vọng weighted. Mô phỏng môi trường stochastic (hành động có xác suất thành công).

---

## Cấu trúc dự án

```
Exercise_AI_FinalExam/
├── app.py                         # Streamlit app chính (6 tabs)
├── requirements.txt               # streamlit, pandas
├── core/
│   ├── puzzle.py                   # PuzzleState, GOAL_STATE, solvability, scramble
│   ├── heuristics.py              # Misplaced Tiles, Manhattan, Linear Conflict
│   ├── node.py                    # Node class cho graph search
│   ├── metrics.py                 # SearchResult, TraceStep dataclasses
│   ├── utils.py                   # run_solver, format helpers
│   └── theory.py                  # Lý thuyết tiếng Việt cho 27 thuật toán
├── algorithms/
│   ├── uninformed.py              # BFS, DFS, UCS, IDS
│   ├── informed.py                # Greedy Best-First, A*, IDA*
│   ├── local_search.py            # 6 biến thể Hill Climbing + Beam + SA
│   ├── complex_env.py             # AND-OR, No Obs, Partial Obs, LRTA*
│   ├── csp.py                     # 7 thuật toán CSP
│   └── adversarial.py            # Minimax, Alpha-Beta, Expectimax
├── ui/
│   ├── components.py              # render_puzzle_board, metrics, trace, tree, detail tables
│   └── styles.py                  # CSS, GROUP_COLORS, maps, COMPARISON_TABLE
└── tests/
    ├── test_puzzle.py             # 17 tests cho core.puzzle
    ├── test_heuristics.py          # 12 tests cho heuristics
    └── test_solvers.py             # 38 tests cho tất cả solver algorithms
```

## Chạy tests

```bash
python -m pytest tests/ -v
```

## Tính năng chính

- **6 tab chức năng**: Play/Board, Run Algorithm, Step Trace, Compare, Theory Notes, CSP/Complex/Game
- **Bảng Node/Frontier/Reached**: Xem chi tiết từng bước tìm kiếm (BFS, DFS, UCS, IDS, Greedy, A*)
- **Search Tree Visualization**: Xem cây tìm kiếm mở rộng từng bước với giá trị g/h/f
- **Interactive Play**: Chơi tay bằng nút mũi tên, random scramble, manual input
- **Benchmark**: So sánh nhiều thuật toán cùng lúc với bảng phân tích
- **Lý thuyết tiếng Việt**: Mục tiêu, ý tưởng, CT, ưu/nhược điểm, mẹo thi cho từng thuật toán
- **Solvable check**: Kiểm tra trạng thái có giải được không (inversions + blank_row parity)
- **Safety limits**: Timeout, max_nodes để tránh BFS/DFS bị treo