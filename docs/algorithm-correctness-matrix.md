# Algorithm Correctness Matrix

Tài liệu này tách rõ solver chuẩn, demo đối chiếu và extension. Mục tiêu là tránh claim sai khi thuyết trình hoặc khi đọc GIF trong README.

## Matrix

| Nhóm | Thuật toán | Output chính | Có thể claim solution chuẩn? | Optimality claim | Evidence bắt buộc |
|---|---|---|---:|---|---|
| Uninformed | BFS | Linear path | Có | Có với unit cost | `path_verified`, `goal_reached`, FIFO trace |
| Uninformed | DFS | Linear path hoặc stopped | Không | Không | legal path nếu có, depth/stack trace |
| Uninformed | UCS | Linear path | Có | Có với non-negative cost | `g(n)`, priority queue, goal certificate |
| Uninformed | IDS | Linear path | Có | Có với unit cost khi đủ limit | depth limit, cutoff/exhausted reason |
| Informed | Greedy Best-First | Linear path hoặc stopped | Demo đối chiếu | Không | h-only priority, final goal flag |
| Informed | A* | Linear path | Có | Có khi heuristic admissible/consistent | `g/h/f`, frontier/reached, optimality flag |
| Informed | IDA* | Linear path | Có | Có khi đủ threshold | f-threshold, reached metric, legal path |
| Local | Hill Climbing variants | Local trajectory | Không | Không | candidate xét/chọn/từ chối, h change |
| Local | Local Beam Search | Beam trajectory | Không | Không | beam width, candidate h, stop reason |
| Local | Simulated Annealing | Stochastic trajectory | Không | Không | temperature, probability, accepted flag |
| Complex | AND-OR Search | Conditional plan | Không | Không | OR/AND branches, deflection support |
| Complex | No/Partial Observation | Belief-driven actions | Không | Không | belief size, known tiles, fallback votes |
| Complex | LRTA* | Online trace | Không | Không | H update, observed successor, step cap |
| CSP | CSP family | Model/assignment/horizon path | Không mặc định | Horizon-bound only | variables, domains, constraints |
| AI-vs-AI | Tournament | Score report | Không | Reference-bound | A* reference, legal path, excess cost |
| AI-vs-AI | Minimax/Alpha-Beta | Depth-limited robust action | Không | Depth-limited utility | MAX/MIN, utility, prune evidence |
| AI-vs-AI | Expectimax | Expected-value action | Không | Probability-model bound | CHANCE node, probability, expected utility |

## Contract

- `path_verified=True` chỉ nói các action hợp lệ.
- `goal_reached=True` mới nói state cuối bằng goal.
- `optimality_proven=True` chỉ bật khi solver optimal, path hợp lệ, tới goal và termination là `goal`.
- Extension algorithms phải có caveat trong UI/docs/GIF manifest.
- AND-OR là conditional plan, không phải linear path giả.
- Minimax dùng MIN như worst-case robustness branch, không phải đối thủ thật của 15-puzzle.
