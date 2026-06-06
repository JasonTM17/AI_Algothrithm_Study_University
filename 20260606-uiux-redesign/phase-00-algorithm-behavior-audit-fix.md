---
phase: 0
title: Algorithm Behavior Audit & Fix
status: completed
priority: P0
effort: 2h
dependencies: []
---

# Phase 0: Algorithm Behavior Audit & Fix

## Overview

Audit tất cả 27 thuật toán để đảm bảo mỗi thuật toán thể hiện đúng đặc trưng riêng.
Các thuật toán cùng nhóm (uninformed) PHẢI cho ra kết quả KHÁC NHAU.
UI phải làm nổi bật sự khác biệt này.

## Vấn đề hiện tại

Hiện tại BFS, UCS, IDS đều tìm optimal path (unit cost = 1) → **cùng độ dài đường đi**.
Điều này ĐÚNG về mặt lý thuyết nhưng gây cảm giác "thuật toán nào cũng giống nhau".
Cần làm nổi bật sự khác biệt qua các metrics khác: nodes_expanded, max_frontier, runtime, path quality.

## Requirements

### Uninformed Search (BFS, DFS, UCS, IDS)

| Thuật toán | Expected Behavior | Verify |
|-----------|-------------------|--------|
| **BFS** | Shortest path, HUGE frontier (10K+ nodes), high memory | Path length = optimal, max_frontier lớn nhất |
| **DFS** | First path found (NOT shortest), low memory, may be very long | Path length > optimal, max_frontier nhỏ |
| **UCS** | Same as BFS for unit cost (ghi chú rõ điều này) | Path = BFS, nên note "giống BFS với unit cost" |
| **IDS** | Shortest path, more total expansions than BFS, low memory per iter | Path = optimal, total nodes > BFS |

**Fix cần làm:**
- DFS: Đảm bảo KHÔNG tìm shortest path (hiện tại dùng stack + reversed neighbors → đã đúng)
- Verify output: BFS path length < DFS path length (với scramble depth đủ lớn, >15)

### Informed Search (Greedy, A*, IDA*)

| Thuật toán | Expected Behavior | Verify |
|-----------|-------------------|--------|
| **Greedy** | Fast, ít nodes expanded, but path KHÔNG optimal | Path dài hơn A*, nodes ít hơn A* |
| **A*** | Optimal path, expands ít hơn BFS, nhiều hơn Greedy | Path = optimal, heuristic admissible |
| **IDA*** | Same optimal path as A*, more expansions, low memory | Path = A*, total expansions > A* |

**Fix cần làm:**
- Verify Greedy path > A* path (test với scramble depth 10-15)
- Nếu Greedy vô tình tìm optimal → làm rõ trong UI rằng "Greedy không guarantee optimal, may mắn lần này"

### Local Search

| Thuật toán | Expected Behavior | Verify |
|-----------|-------------------|--------|
| **Simple Hill Climbing** | Kẹt local optimum, KHÔNG solve được | Success = False, message = "Stuck at local optimum h=..." |
| **Steepest-Ascent HC** | Kẹt local optimum | Success = False |
| **Stochastic HC** | Có thể tìm thấy nhưng unreliable | Success sometimes, sometimes not |
| **Random-Restart HC** | Có xác suất tìm thấy với đủ restarts | May succeed with many restarts |
| **Local Beam Search** | Tốt hơn HC đơn lẻ, vẫn có thể kẹt | k beams explored |
| **Simulated Annealing** | Có cơ hội thoát local optimum, trace hiển thị temperature + accept probability | Trace có T và P(accept) |

**Fix cần làm:**
- Đảm bảo Hill Climbing variants THỰC SỰ kẹt local optimum (không fake)
- Simulated Annealing trace phải hiển thị rõ các bước accept worse move

### Adversarial/Stochastic

| Thuật toán | Expected Behavior | Verify |
|-----------|-------------------|--------|
| **Minimax** | Tìm best move với game tree depth | Message mô tả MAX/MIN reasoning |
| **Alpha-Beta** | Cùng kết quả Minimax, less nodes | Nodes < Minimax, same best action |
| **Expectimax** | Expected value calculation | Message mô tả probability-weighted avg |

### CSP

Tất cả CSP algorithms hiện tại là mô phỏng học thuật (15-puzzle không phải CSP tự nhiên). Cần hiển thị rõ message giải thích tại sao CSP không phù hợp.

## Implementation Steps

1. **Audit run**: Chạy từng nhóm thuật toán với cùng 1 start state (scramble depth=15, seed=42)
   - Ghi lại: path length, nodes expanded, max frontier, runtime, success
   - So sánh BFS vs DFS vs UCS vs IDS → xác nhận khác biệt
   - So sánh Greedy vs A* vs IDA* → xác nhận Greedy path > A* path

2. **Fix nếu cần**:
   - Nếu DFS trả về optimal path → kiểm tra action_order có ảnh hưởng không
   - Nếu Greedy luôn trả về optimal → kiểm tra heuristic có quá informative không
   - Nếu Hill Climbing luôn fail → tốt, đúng behavior
   - Nếu Simulated Annealing không có trace T/P(accept) → thêm vào trace

3. **Enhance trace output**:
   - Mỗi trace step nên có thêm context về behavior: "BFS expanding level by level", "DFS going deep", "Greedy picking lowest h(n)"
   - Compare tab: thêm cột "Path Quality" (optimal/suboptimal/long) và "Memory Usage" (high/medium/low)

4. **Update theory display**:
   - Tab Theory Notes: làm nổi bật "Tại sao thuật toán này khác thuật toán kia"
   - Thêm phần "So sánh với thuật toán tương tự" vào mỗi theory entry

5. **Write verification tests** (nếu cần):
   ```python
   def test_bfs_vs_dfs_different_paths():
       """BFS and DFS should produce different paths for same input."""
       start = scramble(depth=15, seed=42)
       bfs_result = bfs(start)
       dfs_result = dfs(start, max_depth=30)
       assert bfs_result.success
       assert dfs_result.success
       assert len(bfs_result.actions) <= len(dfs_result.actions)  # BFS optimal
   
   def test_greedy_not_optimal():
       """Greedy path should NOT be shorter than A* path."""
       start = scramble(depth=15, seed=42)
       greedy_result = greedy_best_first(start)
       astar_result = a_star(start)
       assert len(greedy_result.actions) >= len(astar_result.actions)
   
   def test_hill_climbing_gets_stuck():
       """Simple Hill Climbing should fail on a non-trivial puzzle."""
       start = scramble(depth=20, seed=42)
       result = simple_hill_climbing(start, max_iterations=50000)
       # Should get stuck (local optimum), NOT solve
       assert not result.success or len(result.actions) > 0
   ```

## Success Criteria

- [ ] BFS path length ≤ DFS path length (BFS optimal, DFS not)
- [ ] Greedy path length ≥ A* path length (Greedy không tối ưu)
- [ ] BFS max_frontier >> DFS max_frontier (BFS tốn memory hơn)
- [ ] Hill Climbing variants trả về "Stuck at local optimum" (không solve được)
- [ ] Simulated Annealing trace hiển thị T (temperature) và P(accept)
- [ ] Compare tab hiển thị rõ sự khác biệt giữa các thuật toán
- [ ] Tất cả tests pass (cũ + mới)
