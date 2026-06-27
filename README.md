# 15-Puzzle AI Algorithm Simulator

[![Web quality](https://github.com/JasonTM17/AI_Algothrithm_Study_University/actions/workflows/quality.yml/badge.svg)](https://github.com/JasonTM17/AI_Algothrithm_Study_University/actions/workflows/quality.yml)
![Python 3.12](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-app-FF4B4B?logo=streamlit&logoColor=white)
![28 algorithms](https://img.shields.io/badge/AI-28%20algorithms-7FAF6F)

**Tác giả:** JasonTM17

Ứng dụng Streamlit để học và bảo vệ đồ án Trí tuệ nhân tạo qua 15-puzzle. Repo không chỉ in ra đáp án; nó trình bày `state`, `action`, `frontier`, `reached`, heuristic, trace, certificate, GIF chạy thật và ranh giới học thuật của từng nhóm thuật toán.

<p align="center"><img src="docs/assets/readme/a-star-image-replay.gif" alt="A* image puzzle replay" width="960"></p>

GIF hero ở trên được chụp từ live Streamlit browser capture bằng `agent-browser screenshot`: A* Search, Manhattan Distance, `f(n)=g(n)+h(n)`, legal blank moves và image tiles đi theo cùng trajectory. Không dùng mockup renderer.

## Mục Lục

- [Chạy Nhanh](#chạy-nhanh)
- [Bản Đồ 6 Nhóm](#bản-đồ-6-nhóm)
- [Cách Đọc Từng Nhóm](#cách-đọc-từng-nhóm)
- [So Sánh Thuật Toán Trong Nhóm](#so-sánh-thuật-toán-trong-nhóm)
- [Atlas 28 Thuật Toán Có GIF Chạy Thật](#atlas-28-thuật-toán-có-gif-chạy-thật)
- [Cách Đọc Evidence](#cách-đọc-evidence)
- [Tài Liệu](#tài-liệu)

## Chạy Nhanh

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

Kiểm tra phát triển:

```bash
pip install -r requirements-dev.txt
python -m compileall -q app.py core algorithms ui scripts
python scripts/generate-readme-gifs.py --check --check-readability
python -m pytest tests -q --cov=core --cov=algorithms --cov-report=term-missing --cov-fail-under=65
```

## Bản Đồ 6 Nhóm

`ALGORITHM_GROUPS` là contract chính: 6 nhóm, 28 thuật toán. Mỗi GIF dưới đây là live Streamlit browser capture, không phải mockup.

### Uninformed Search

<p><img src="docs/assets/readme/uninformed-search.gif" alt="Uninformed Search" width="620"></p>

- **Vai trò:** Duyet state-space without heuristic; evidence focuses on frontier/reached and legal path.
- **Câu hỏi học thuật:** If every move costs 1 and no domain estimate is used, how does queue discipline change behavior?
- **Thuật toán:** BFS, DFS, UCS, IDS

### Informed Search

<p><img src="docs/assets/readme/informed-search.gif" alt="Informed Search" width="620"></p>

- **Vai trò:** Add h(n), then combine with g(n) for optimal informed search.
- **Câu hỏi học thuật:** When is a heuristic only fast, and when does it justify an optimality certificate?
- **Thuật toán:** Greedy Best-First, A*, IDA*

### Local Search

<p><img src="docs/assets/readme/local-search.gif" alt="Local Search" width="620"></p>

- **Vai trò:** Show candidate-level choices without treating the run as guaranteed path search.
- **Câu hỏi học thuật:** Which neighbor was considered, chosen, rejected or accepted probabilistically?
- **Thuật toán:** Simple Hill Climbing, Steepest-Ascent Hill Climbing, Stochastic Hill Climbing, Random-Restart Hill Climbing, Local Beam Search, Simulated Annealing

### Complex Environments

<p><img src="docs/assets/readme/complex-environments.gif" alt="Complex Environments" width="620"></p>

- **Vai trò:** Model conditional, belief-state and online variants that extend the basic 15-puzzle PEAS.
- **Câu hỏi học thuật:** What does the agent know, and is the output a path, a policy or an online trace?
- **Thuật toán:** AND-OR Search, Searching with no observation, Searching for partially observable problems, LRTA*

### CSP

<p><img src="docs/assets/readme/csp.gif" alt="CSP" width="620"></p>

- **Vai trò:** Reframe puzzle planning as variables, domains and constraints.
- **Câu hỏi học thuật:** Which variable/domain/constraint evidence is being shown instead of a shortest path claim?
- **Thuật toán:** CSP Definition, Constraint Propagation, Path Consistency, Global Constraints, Backtracking Search, Min-Conflicts, Constraint Graphs

### AI-vs-AI Tournament

<p><img src="docs/assets/readme/ai-vs-ai-tournament.gif" alt="AI-vs-AI Tournament" width="620"></p>

- **Vai trò:** Compare agents, robustness and chance models without pretending the puzzle has a natural opponent.
- **Câu hỏi học thuật:** Is this a scored benchmark, a worst-case branch or an expected-value model?
- **Thuật toán:** AI-vs-AI Tournament, Minimax, Alpha-Beta Pruning, Expectimax

## Cách Đọc Từng Nhóm

| Nhóm | Cách đọc đúng | Sai lầm cần tránh |
|---|---|---|
| Uninformed Search | So sánh FIFO, LIFO, cost queue và iterative deepening khi không có h(n). | Gọi DFS là optimal hoặc quên memory của BFS. |
| Informed Search | Đọc h(n), g(n), f(n), admissible/consistent và certificate. | Gọi Greedy là optimal chỉ vì một run tình cờ ngắn. |
| Local Search | Xem candidate được xét/chọn/từ chối và lý do dừng. | Nhầm legal trajectory thành solution path. |
| Complex Environments | Đọc belief, conditional plan, online update theo đúng mô hình mở rộng. | Ép AND-OR/belief thành đường đi tuyến tính giả. |
| CSP | Đọc variables, domains, constraints, propagation và horizon. | Gọi CSP model definition là shortest-path solver. |
| AI-vs-AI Tournament | Đọc scoring, robustness, pruning và expected value. | Gọi MIN là đối thủ thật của 15-puzzle. |

## So Sánh Thuật Toán Trong Nhóm

### Uninformed Search

| Thuật toán | Frontier/decision rule | Evidence cần nhìn | Guarantee đúng | Caveat |
|---|---|---|---|---|
| BFS | FIFO queue, mở theo tầng. | frontier/reached, path cost, depth. | Complete, optimal với unit step cost. | Memory tăng rất nhanh. |
| DFS | LIFO stack, đi sâu trước. | depth, expanded, legal trajectory. | Không có shortest-path guarantee. | Có thể đi nhánh sâu và bỏ lỡ đường ngắn. |
| UCS | Priority queue theo `g(n)`. | cumulative cost, frontier/reached. | Complete, optimal với non-negative cost. | Với 15-puzzle unit cost gần giống BFS nhưng nêu rõ cost model. |
| IDS | DFS giới hạn độ sâu, tăng limit. | cutoff/exhausted theo từng limit. | Complete, optimal với unit step cost khi limit đủ. | Lặp lại work qua nhiều iteration. |

### Informed Search

| Thuật toán | Evaluation rule | Evidence cần nhìn | Guarantee đúng | Caveat |
|---|---|---|---|---|
| Greedy Best-First | Ưu tiên `h(n)` nhỏ nhất. | selected h, frontier, goal flag. | Không optimality certificate. | Nhanh nhưng có thể bị heuristic đánh lừa. |
| A* | Ưu tiên `f(n)=g(n)+h(n)`. | g/h/f, expanded/generated/frontier. | Optimal nếu h admissible/consistent và không bị limit. | Certificate chỉ đúng cho goal/heuristic đã chọn. |
| IDA* | DFS bounded bởi threshold `f`. | threshold, best_g/reached, path. | Optimal với admissible heuristic và threshold đủ. | Tiết kiệm memory nhưng revisit nhiều state. |

### Local Search

| Thuật toán | Candidate rule | Evidence cần nhìn | Output đúng | Caveat |
|---|---|---|---|---|
| Simple Hill Climbing | Chọn candidate cải thiện đầu tiên. | candidate được xét, selected action. | Legal local trajectory nếu có action. | Dễ kẹt local optimum. |
| Steepest-Ascent HC | Xét toàn bộ neighbor rồi chọn tốt nhất. | evaluated candidates, best candidate. | Local improvement trace. | Tốn xét neighbor nhưng vẫn local. |
| Stochastic HC | Random trong nhóm candidate cải thiện. | seed, candidate pool, chosen action. | Reproducible khi seed cố định. | Kết quả phụ thuộc seed. |
| Random-Restart HC | Nhiều lần start lại rồi hill climb. | restart index, best h. | So sánh nhiều basin cục bộ. | Không biến thành shortest-path solver. |
| Local Beam Search | Giữ `k` state tốt nhất mỗi vòng. | beam states, selected successors. | Population-based local evidence. | Beam nhỏ có thể mất nhánh tốt. |
| Simulated Annealing | Có thể accept bước xấu theo temperature. | temperature, delta h, accept/reject. | Legal trajectory, đôi khi thoát local optimum. | Không claim solved nếu chưa tới goal. |

### Complex Environments

| Thuật toán | Mô hình output | Evidence cần nhìn | Guarantee đúng | Caveat |
|---|---|---|---|---|
| AND-OR Search | Conditional plan/policy. | AND node, OR action, deflection support. | Plan hợp lệ trong depth/support đã chọn. | Không phải linear path giả; support switch không phải probability weight. |
| Searching with no observation | Belief-state reasoning. | belief size, planner votes, fallback reason. | Agent quyết định từ belief set. | Hidden actual state chỉ để debug. |
| Partially observable search | Known-tile matrix + belief update. | known tiles, observation, belief prune. | Trace reconstruction giáo dục. | Không biến thành solver chuẩn khi chỉ biết vài ô. |
| LRTA* | Online one-step learning. | H update, local successors, chosen action. | Online demo có legal moves. | Cap là max online steps, không phải node frontier chuẩn. |

### CSP

| Thuật toán | CSP concept | Evidence cần nhìn | Output đúng | Caveat |
|---|---|---|---|---|
| CSP Definition | Variables/domains/constraints. | variable count, domain endpoints. | Model definition. | Chưa phải solved trajectory. |
| Constraint Propagation | AC-3 style exact-horizon pruning. | arc checks, candidate states, domain wipe-out/goal. | Sound pruning for represented constraints. | Horizon parity quan trọng; `T=2` có thể wipe-out đúng logic. |
| Path Consistency | Triple support explanation. | consistency events, remaining supports. | Educational consistency evidence. | Illustration, không phải shortest-path solver. |
| Global Constraints | AllDifferent/structural rules. | global check summary. | Rules out invalid assignments. | Không thay thế graph search certificate. |
| Backtracking Search | DFS over bounded transition model. | assignment/backtrack reason, final path if found. | Can solve small exact horizon. | Dùng Manhattan ordering, không claim full MRV/forward checking. |
| Min-Conflicts | Local repair of CSP assignment. | conflict count, selected variable. | CSP repair concept. | Tile swaps không nhất thiết là legal blank moves. |
| Constraint Graphs | Network/factor view. | nodes, edges, high-arity relation. | Structural explanation. | Readability/evidence, not path optimality. |

### AI-vs-AI Tournament

| Thuật toán | Decision model | Evidence cần nhìn | Output đúng | Caveat |
|---|---|---|---|---|
| AI-vs-AI Tournament | Scored benchmark against A* reference. | score, optimal cost, verified trajectory. | Fair score if reference certificate exists. | Không phải một đối thủ tự nhiên trong 15-puzzle. |
| Minimax | MAX vs worst-case MIN branch. | utility, depth, selected root action. | Depth-limited worst-case decision. | MIN không phải người chơi thật; cả hai dùng legal blank moves. |
| Alpha-Beta Pruning | Minimax with branch-and-bound pruning. | alpha, beta, cutoff events. | Same root value as full Minimax under same searched tree. | Pruning tiết kiệm node, không đổi PEAS thành game thật. |
| Expectimax | Expected value with CHANCE nodes. | probability model, expected utility. | Depth-limited expected-value policy. | Probability model là giáo dục và phải nêu rõ. |

## Atlas 28 Thuật Toán Có GIF Chạy Thật

Mỗi mục dưới đây có GIF riêng. GIF được tạo từ `scripts/generate-readme-gifs.py`, mở app thật, chụp frame thật từ route `?capture_demo=...`, dùng start/goal/seed/resource limit cố định và được khóa bằng manifest semantic. Trường `web_run_status` ghi trung thực: solved, partial/model, not solved hoặc tournament.

## Uninformed Search: từng thuật toán

### 1. BFS

<p><img src="docs/assets/algorithm-demos/bfs.gif" alt="BFS real GIF" width="560"></p>

| Trục đọc | Nội dung |
|---|---|
| Nhóm | Uninformed Search |
| Vai trò | Standard solver |
| Learning goal | Understand level-order expansion and why unit-cost BFS can certify shortest paths. |
| Cơ chế | FIFO frontier over puzzle states. |
| Evidence trong GIF | frontier size, reached set, legal path and path cost. |
| Guarantee | Complete and optimal for unit step cost if resources suffice. |
| Caveat | Memory grows quickly; good for shallow teaching cases, not deep 15-puzzle production search. |
| Web capture source | `live_streamlit_browser_capture` via `agent-browser screenshot` |
| web_run_status | `solved_optimal` - reached goal with an optimality certificate |
| Demo input | seed `42`, termination `goal`, default demo parameters |
| Certificate flags | `path_verified=True`, `goal_reached=True`, `optimality_proven=True` |
| Result message | Solution found |

Khi thuyết trình:

1. Nói rõ state/action/cost model trước khi giải thích hình.
2. Chỉ vào evidence chính trên GIF: frontier, reached, candidate, belief, domain, utility hoặc score.
3. Kết thúc bằng guarantee và caveat để không claim quá mức.

### 2. DFS

<p><img src="docs/assets/algorithm-demos/dfs.gif" alt="DFS real GIF" width="560"></p>

| Trục đọc | Nội dung |
|---|---|
| Nhóm | Uninformed Search |
| Vai trò | Contrast demo |
| Learning goal | See how depth-first commitment differs from optimal state-space search. |
| Cơ chế | LIFO stack with depth-aware duplicate handling. |
| Evidence trong GIF | expanded nodes, depth limit and legal trajectory when present. |
| Guarantee | No shortest-path guarantee in this app setting. |
| Caveat | Can chase a deep branch and miss a shorter path. |
| Web capture source | `live_streamlit_browser_capture` via `agent-browser screenshot` |
| web_run_status | `solved_not_optimal` - reached goal without an optimality certificate |
| Demo input | seed `42`, termination `goal`, `max_depth=12` |
| Certificate flags | `path_verified=True`, `goal_reached=True`, `optimality_proven=False` |
| Result message | Solution found |

Khi thuyết trình:

1. Nói rõ state/action/cost model trước khi giải thích hình.
2. Chỉ vào evidence chính trên GIF: frontier, reached, candidate, belief, domain, utility hoặc score.
3. Kết thúc bằng guarantee và caveat để không claim quá mức.

### 3. UCS

<p><img src="docs/assets/algorithm-demos/ucs.gif" alt="UCS real GIF" width="560"></p>

| Trục đọc | Nội dung |
|---|---|
| Nhóm | Uninformed Search |
| Vai trò | Standard solver |
| Learning goal | Connect path cost g(n) to optimal search. |
| Cơ chế | Priority queue ordered by cumulative path cost. |
| Evidence trong GIF | g(n), frontier, reached and cost certificate. |
| Guarantee | Complete and optimal for non-negative costs. |
| Caveat | On unit-cost 15-puzzle it behaves like BFS but keeps the general cost model explicit. |
| Web capture source | `live_streamlit_browser_capture` via `agent-browser screenshot` |
| web_run_status | `solved_optimal` - reached goal with an optimality certificate |
| Demo input | seed `42`, termination `goal`, default demo parameters |
| Certificate flags | `path_verified=True`, `goal_reached=True`, `optimality_proven=True` |
| Result message | Solution found |

Khi thuyết trình:

1. Nói rõ state/action/cost model trước khi giải thích hình.
2. Chỉ vào evidence chính trên GIF: frontier, reached, candidate, belief, domain, utility hoặc score.
3. Kết thúc bằng guarantee và caveat để không claim quá mức.

### 4. IDS

<p><img src="docs/assets/algorithm-demos/ids.gif" alt="IDS real GIF" width="560"></p>

| Trục đọc | Nội dung |
|---|---|
| Nhóm | Uninformed Search |
| Vai trò | Standard solver |
| Learning goal | Trade BFS optimality for DFS-like memory by increasing the depth limit. |
| Cơ chế | Repeated depth-limited DFS with cutoff tracking. |
| Evidence trong GIF | depth limit, cutoff/exhausted reason and legal path. |
| Guarantee | Complete and optimal for unit step cost if the limit reaches the solution depth. |
| Caveat | Repeats work across iterations; the trace should be read by limit, not as one queue. |
| Web capture source | `live_streamlit_browser_capture` via `agent-browser screenshot` |
| web_run_status | `solved_optimal` - reached goal with an optimality certificate |
| Demo input | seed `42`, termination `goal`, `max_depth=12` |
| Certificate flags | `path_verified=True`, `goal_reached=True`, `optimality_proven=True` |
| Result message | Found at depth 5, limit=5 |

Khi thuyết trình:

1. Nói rõ state/action/cost model trước khi giải thích hình.
2. Chỉ vào evidence chính trên GIF: frontier, reached, candidate, belief, domain, utility hoặc score.
3. Kết thúc bằng guarantee và caveat để không claim quá mức.

## Informed Search: từng thuật toán

### 5. Greedy Best-First

<p><img src="docs/assets/algorithm-demos/greedy-best-first.gif" alt="Greedy Best-First real GIF" width="560"></p>

| Trục đọc | Nội dung |
|---|---|
| Nhóm | Informed Search |
| Vai trò | Contrast demo |
| Learning goal | Show why h(n) alone is fast but not a certificate. |
| Cơ chế | Priority queue ordered only by heuristic h(n). |
| Evidence trong GIF | selected h(n), frontier and whether the final path reaches goal. |
| Guarantee | No optimality guarantee. |
| Caveat | May find a longer path or get misled by a locally attractive state. |
| Web capture source | `live_streamlit_browser_capture` via `agent-browser screenshot` |
| web_run_status | `solved_not_optimal` - reached goal without an optimality certificate |
| Demo input | seed `42`, termination `goal`, default demo parameters |
| Certificate flags | `path_verified=True`, `goal_reached=True`, `optimality_proven=False` |
| Result message | Solution found |

Khi thuyết trình:

1. Nói rõ state/action/cost model trước khi giải thích hình.
2. Chỉ vào evidence chính trên GIF: frontier, reached, candidate, belief, domain, utility hoặc score.
3. Kết thúc bằng guarantee và caveat để không claim quá mức.

### 6. A*

<p><img src="docs/assets/algorithm-demos/astar.gif" alt="A* real GIF" width="560"></p>

| Trục đọc | Nội dung |
|---|---|
| Nhóm | Informed Search |
| Vai trò | Standard solver |
| Learning goal | Read f(n)=g(n)+h(n) and the Manhattan optimality condition. |
| Cơ chế | Priority queue ordered by g(n)+h(n). |
| Evidence trong GIF | g/h/f, expanded/generated/frontier, legal path and optimality flag. |
| Guarantee | Optimal with admissible and consistent heuristic when resources do not stop the run. |
| Caveat | The certificate is valid only for the selected goal and heuristic contract. |
| Web capture source | `live_streamlit_browser_capture` via `agent-browser screenshot` |
| web_run_status | `solved_optimal` - reached goal with an optimality certificate |
| Demo input | seed `42`, termination `goal`, default demo parameters |
| Certificate flags | `path_verified=True`, `goal_reached=True`, `optimality_proven=True` |
| Result message | Solution found |

Khi thuyết trình:

1. Nói rõ state/action/cost model trước khi giải thích hình.
2. Chỉ vào evidence chính trên GIF: frontier, reached, candidate, belief, domain, utility hoặc score.
3. Kết thúc bằng guarantee và caveat để không claim quá mức.

### 7. IDA*

<p><img src="docs/assets/algorithm-demos/idastar.gif" alt="IDA* real GIF" width="560"></p>

| Trục đọc | Nội dung |
|---|---|
| Nhóm | Informed Search |
| Vai trò | Standard solver |
| Learning goal | Combine A* evaluation with memory-bounded iterative thresholds. |
| Cơ chế | Depth-first search bounded by increasing f-threshold. |
| Evidence trong GIF | threshold, reached metric, legal path and optimality flag. |
| Guarantee | Optimal with admissible heuristic and sufficient threshold iterations. |
| Caveat | May revisit many states; trace is threshold-based, not a single frontier queue. |
| Web capture source | `live_streamlit_browser_capture` via `agent-browser screenshot` |
| web_run_status | `solved_optimal` - reached goal with an optimality certificate |
| Demo input | seed `42`, termination `goal`, default demo parameters |
| Certificate flags | `path_verified=True`, `goal_reached=True`, `optimality_proven=True` |
| Result message | Found with threshold=4 |

Khi thuyết trình:

1. Nói rõ state/action/cost model trước khi giải thích hình.
2. Chỉ vào evidence chính trên GIF: frontier, reached, candidate, belief, domain, utility hoặc score.
3. Kết thúc bằng guarantee và caveat để không claim quá mức.

## Local Search: từng thuật toán

### 8. Simple Hill Climbing

<p><img src="docs/assets/algorithm-demos/simple-hill-climbing.gif" alt="Simple Hill Climbing real GIF" width="560"></p>

| Trục đọc | Nội dung |
|---|---|
| Nhóm | Local Search |
| Vai trò | Contrast demo |
| Learning goal | Watch the first improving candidate win or the search stop. |
| Cơ chế | Scan neighbors and move to the first lower h(n). |
| Evidence trong GIF | candidate h, selected action and stop reason. |
| Guarantee | No completeness or optimality guarantee. |
| Caveat | Local optimum can stop the run far from the goal. |
| Web capture source | `live_streamlit_browser_capture` via `agent-browser screenshot` |
| web_run_status | `not_solved_in_demo` - web demo completed without a solution claim |
| Demo input | seed `42`, termination `stopped`, `max_iterations=40` |
| Certificate flags | `path_verified=True`, `goal_reached=False`, `optimality_proven=False` |
| Result message | Stuck at local optimum h=4.0 |

Khi thuyết trình:

1. Nói rõ state/action/cost model trước khi giải thích hình.
2. Chỉ vào evidence chính trên GIF: frontier, reached, candidate, belief, domain, utility hoặc score.
3. Kết thúc bằng guarantee và caveat để không claim quá mức.

### 9. Steepest-Ascent Hill Climbing

<p><img src="docs/assets/algorithm-demos/steepest-ascent-hill-climbing.gif" alt="Steepest-Ascent Hill Climbing real GIF" width="560"></p>

| Trục đọc | Nội dung |
|---|---|
| Nhóm | Local Search |
| Vai trò | Contrast demo |
| Learning goal | Compare all local neighbors before moving. |
| Cơ chế | Choose the neighbor with best h(n) decrease. |
| Evidence trong GIF | evaluated candidates, best candidate and reject/accept reason. |
| Guarantee | No completeness or optimality guarantee. |
| Caveat | Still local; evaluating every neighbor does not solve plateaus. |
| Web capture source | `live_streamlit_browser_capture` via `agent-browser screenshot` |
| web_run_status | `not_solved_in_demo` - web demo completed without a solution claim |
| Demo input | seed `42`, termination `stopped`, `max_iterations=40` |
| Certificate flags | `path_verified=True`, `goal_reached=False`, `optimality_proven=False` |
| Result message | Stuck at local optimum h=4.0 |

Khi thuyết trình:

1. Nói rõ state/action/cost model trước khi giải thích hình.
2. Chỉ vào evidence chính trên GIF: frontier, reached, candidate, belief, domain, utility hoặc score.
3. Kết thúc bằng guarantee và caveat để không claim quá mức.

### 10. Stochastic Hill Climbing

<p><img src="docs/assets/algorithm-demos/stochastic-hill-climbing.gif" alt="Stochastic Hill Climbing real GIF" width="560"></p>

| Trục đọc | Nội dung |
|---|---|
| Nhóm | Local Search |
| Vai trò | Contrast demo |
| Learning goal | See randomness among improving candidates. |
| Cơ chế | Sample one improving move using a fixed seed. |
| Evidence trong GIF | candidate pool, chosen action, seed and legal trajectory. |
| Guarantee | No deterministic optimality guarantee. |
| Caveat | Different seeds can produce different partial trajectories. |
| Web capture source | `live_streamlit_browser_capture` via `agent-browser screenshot` |
| web_run_status | `not_solved_in_demo` - web demo completed without a solution claim |
| Demo input | seed `42`, termination `stopped`, `max_iterations=40`, `seed=7` |
| Certificate flags | `path_verified=True`, `goal_reached=False`, `optimality_proven=False` |
| Result message | Stuck at local optimum h=4.0 |

Khi thuyết trình:

1. Nói rõ state/action/cost model trước khi giải thích hình.
2. Chỉ vào evidence chính trên GIF: frontier, reached, candidate, belief, domain, utility hoặc score.
3. Kết thúc bằng guarantee và caveat để không claim quá mức.

### 11. Random-Restart Hill Climbing

<p><img src="docs/assets/algorithm-demos/random-restart-hill-climbing.gif" alt="Random-Restart Hill Climbing real GIF" width="560"></p>

| Trục đọc | Nội dung |
|---|---|
| Nhóm | Local Search |
| Vai trò | Contrast demo |
| Learning goal | Use restarts to escape one bad local basin. |
| Cơ chế | Run multiple hill climbs from deterministic restart states. |
| Evidence trong GIF | restart index, best h(n) and selected trajectory. |
| Guarantee | Still not a complete 15-puzzle solver here. |
| Caveat | More restarts improve chances but do not prove optimality. |
| Web capture source | `live_streamlit_browser_capture` via `agent-browser screenshot` |
| web_run_status | `not_solved_in_demo` - web demo completed without a solution claim |
| Demo input | seed `42`, termination `stopped`, `max_iterations=40`, `seed=7`, `max_restarts=3` |
| Certificate flags | `path_verified=True`, `goal_reached=False`, `optimality_proven=False` |
| Result message | Best h=4.0 after 3 restarts |

Khi thuyết trình:

1. Nói rõ state/action/cost model trước khi giải thích hình.
2. Chỉ vào evidence chính trên GIF: frontier, reached, candidate, belief, domain, utility hoặc score.
3. Kết thúc bằng guarantee và caveat để không claim quá mức.

### 12. Local Beam Search

<p><img src="docs/assets/algorithm-demos/local-beam-search.gif" alt="Local Beam Search real GIF" width="560"></p>

| Trục đọc | Nội dung |
|---|---|
| Nhóm | Local Search |
| Vai trò | Contrast demo |
| Learning goal | Track several local candidates at once. |
| Cơ chế | Keep k best states per iteration. |
| Evidence trong GIF | beam width, candidate scores and selected beam states. |
| Guarantee | No optimality guarantee. |
| Caveat | The beam can collapse to similar states and miss the global route. |
| Web capture source | `live_streamlit_browser_capture` via `agent-browser screenshot` |
| web_run_status | `solved_not_optimal` - reached goal without an optimality certificate |
| Demo input | seed `42`, termination `goal`, `max_iterations=40`, `beam_width=3` |
| Certificate flags | `path_verified=True`, `goal_reached=True`, `optimality_proven=False` |
| Result message | Goal reached |

Khi thuyết trình:

1. Nói rõ state/action/cost model trước khi giải thích hình.
2. Chỉ vào evidence chính trên GIF: frontier, reached, candidate, belief, domain, utility hoặc score.
3. Kết thúc bằng guarantee và caveat để không claim quá mức.

### 13. Simulated Annealing

<p><img src="docs/assets/algorithm-demos/simulated-annealing.gif" alt="Simulated Annealing real GIF" width="560"></p>

| Trục đọc | Nội dung |
|---|---|
| Nhóm | Local Search |
| Vai trò | Contrast demo |
| Learning goal | Understand probabilistic acceptance of worse moves. |
| Cơ chế | Temperature-controlled accept/reject over neighbors. |
| Evidence trong GIF | temperature, probability, accepted flag and legal trajectory. |
| Guarantee | No certificate of reaching or optimizing the goal. |
| Caveat | A legal trajectory is not automatically a solution. |
| Web capture source | `live_streamlit_browser_capture` via `agent-browser screenshot` |
| web_run_status | `not_solved_in_demo` - web demo completed without a solution claim |
| Demo input | seed `42`, termination `stopped`, `max_iterations=40`, `seed=7` |
| Certificate flags | `path_verified=True`, `goal_reached=False`, `optimality_proven=False` |
| Result message | Best h=5.0, temp=98.0684 |

Khi thuyết trình:

1. Nói rõ state/action/cost model trước khi giải thích hình.
2. Chỉ vào evidence chính trên GIF: frontier, reached, candidate, belief, domain, utility hoặc score.
3. Kết thúc bằng guarantee và caveat để không claim quá mức.

## Complex Environments: từng thuật toán

### 14. AND-OR Search

<p><img src="docs/assets/algorithm-demos/and-or-search.gif" alt="AND-OR Search real GIF" width="560"></p>

| Trục đọc | Nội dung |
|---|---|
| Nhóm | Complex Environments |
| Vai trò | Extension |
| Learning goal | Read a conditional plan under possible outcome deflections. |
| Cơ chế | OR chooses action; AND requires subplans for supported outcomes. |
| Evidence trong GIF | conditional branches, depth limit and deflection support mode. |
| Guarantee | Returns a policy-like conditional plan, not a linear shortest path. |
| Caveat | The support switch is not probability weighting. |
| Web capture source | `live_streamlit_browser_capture` via `agent-browser screenshot` |
| web_run_status | `ran_model_not_goal_path` - ran successfully as model evidence, not a solved path |
| Demo input | seed `42`, termination `model_success`, `max_depth=2`, `nondet_prob=0.0` |
| Certificate flags | `path_verified=True`, `goal_reached=False`, `optimality_proven=False` |
| Result message | Conditional plan found (depth limit=2). AND-OR requires every supported outcome to succeed. Deflection support=intended outcome only; nondet_prob>0 adds all legal deflections, not probability-weighted branches. OR: choose action R (h=1.0) |

Khi thuyết trình:

1. Nói rõ state/action/cost model trước khi giải thích hình.
2. Chỉ vào evidence chính trên GIF: frontier, reached, candidate, belief, domain, utility hoặc score.
3. Kết thúc bằng guarantee và caveat để không claim quá mức.

### 15. Searching with no observation

<p><img src="docs/assets/algorithm-demos/searching-with-no-observation.gif" alt="Searching with no observation real GIF" width="560"></p>

| Trục đọc | Nội dung |
|---|---|
| Nhóm | Complex Environments |
| Vai trò | Extension |
| Learning goal | Separate hidden actual state from belief-state decision making. |
| Cơ chế | Maintain a belief set when observations reveal no tile positions. |
| Evidence trong GIF | belief size, planner votes, fallback votes and action trace. |
| Guarantee | Demonstrates belief reasoning; not a standard full-observation solver. |
| Caveat | Hidden state is shown only as debug evidence. |
| Web capture source | `live_streamlit_browser_capture` via `agent-browser screenshot` |
| web_run_status | `not_solved_in_demo` - web demo completed without a solution claim |
| Demo input | seed `42`, termination `stopped`, `max_steps=3`, `num_belief_states=4`, `known_positions={'14': 15}`, `seed=42` |
| Certificate flags | `path_verified=True`, `goal_reached=False`, `optimality_proven=False` |
| Result message | Belief size=4 after 3 steps. No observation keeps a belief set; planner=A* Search cannot safely collapse it. |

Khi thuyết trình:

1. Nói rõ state/action/cost model trước khi giải thích hình.
2. Chỉ vào evidence chính trên GIF: frontier, reached, candidate, belief, domain, utility hoặc score.
3. Kết thúc bằng guarantee và caveat để không claim quá mức.

### 16. Searching for partially observable problems

<p><img src="docs/assets/algorithm-demos/searching-for-partially-observable-problems.gif" alt="Searching for partially observable problems real GIF" width="560"></p>

| Trục đọc | Nội dung |
|---|---|
| Nhóm | Complex Environments |
| Vai trò | Extension |
| Learning goal | Use known tile positions to reduce the belief set. |
| Cơ chế | Filter belief candidates using a known-tile matrix. |
| Evidence trong GIF | known positions, belief size, planner votes and fallback reason. |
| Guarantee | Can propose legal actions under partial knowledge. |
| Caveat | With too few known tiles, the belief set can still be ambiguous. |
| Web capture source | `live_streamlit_browser_capture` via `agent-browser screenshot` |
| web_run_status | `solved_not_optimal` - reached goal without an optimality certificate |
| Demo input | seed `42`, termination `goal`, `max_steps=3`, `num_belief_states=4`, `known_positions={'14': 15}`, `seed=42` |
| Certificate flags | `path_verified=True`, `goal_reached=True`, `optimality_proven=False` |
| Result message | Actual state reached goal |

Khi thuyết trình:

1. Nói rõ state/action/cost model trước khi giải thích hình.
2. Chỉ vào evidence chính trên GIF: frontier, reached, candidate, belief, domain, utility hoặc score.
3. Kết thúc bằng guarantee và caveat để không claim quá mức.

### 17. LRTA*

<p><img src="docs/assets/algorithm-demos/lrtastar.gif" alt="LRTA* real GIF" width="560"></p>

| Trục đọc | Nội dung |
|---|---|
| Nhóm | Complex Environments |
| Vai trò | Extension |
| Learning goal | Study online heuristic learning one action at a time. |
| Cơ chế | Update H(s) after observing local successors. |
| Evidence trong GIF | online step, H update, chosen action and cap reason. |
| Guarantee | Online learning demo, not an offline optimal certificate. |
| Caveat | The node cap is a max online-step cap in the UI. |
| Web capture source | `live_streamlit_browser_capture` via `agent-browser screenshot` |
| web_run_status | `solved_not_optimal` - reached goal without an optimality certificate |
| Demo input | seed `42`, termination `goal`, `max_steps=8` |
| Certificate flags | `path_verified=True`, `goal_reached=True`, `optimality_proven=False` |
| Result message | Goal reached online |

Khi thuyết trình:

1. Nói rõ state/action/cost model trước khi giải thích hình.
2. Chỉ vào evidence chính trên GIF: frontier, reached, candidate, belief, domain, utility hoặc score.
3. Kết thúc bằng guarantee và caveat để không claim quá mức.

## CSP: từng thuật toán

### 18. CSP Definition

<p><img src="docs/assets/algorithm-demos/csp-definition.gif" alt="CSP Definition real GIF" width="560"></p>

| Trục đọc | Nội dung |
|---|---|
| Nhóm | CSP |
| Vai trò | Extension |
| Learning goal | Name variables, domains and constraints. |
| Cơ chế | Build a state-chain CSP model. |
| Evidence trong GIF | variables/domains/constraints count. |
| Guarantee | Model definition only. |
| Caveat | A model is not yet a solved trajectory. |
| Web capture source | `live_streamlit_browser_capture` via `agent-browser screenshot` |
| web_run_status | `ran_model_not_goal_path` - ran successfully as model evidence, not a solved path |
| Demo input | seed `42`, termination `model_success`, `time_horizon=1` |
| Certificate flags | `path_verified=False`, `goal_reached=False`, `optimality_proven=False` |
| Result message | CSP Definition for 15-Puzzle (T=1)  Variables:   X[t][p]: tile at position p at time t, t=0..1, p=0..15   A[t]: action at time t, t=0..0  Total variables: 33  Domains:   X[0][p] = {15} (fixed by initial state)   X[1][p] = {0} (fixed by goal |

Khi thuyết trình:

1. Nói rõ state/action/cost model trước khi giải thích hình.
2. Chỉ vào evidence chính trên GIF: frontier, reached, candidate, belief, domain, utility hoặc score.
3. Kết thúc bằng guarantee và caveat để không claim quá mức.

### 19. Constraint Propagation

<p><img src="docs/assets/algorithm-demos/constraint-propagation.gif" alt="Constraint Propagation real GIF" width="560"></p>

| Trục đọc | Nội dung |
|---|---|
| Nhóm | CSP |
| Vai trò | Extension |
| Learning goal | See domains shrink before search. |
| Cơ chế | Apply AC-3 style propagation. |
| Evidence trong GIF | domain reductions and wipe-out status. |
| Guarantee | Sound pruning for represented constraints. |
| Caveat | Propagation alone may not decide the puzzle. |
| Web capture source | `live_streamlit_browser_capture` via `agent-browser screenshot` |
| web_run_status | `solved_not_optimal` - reached goal without an optimality certificate |
| Demo input | seed `42`, termination `goal`, `time_horizon=1` |
| Certificate flags | `path_verified=True`, `goal_reached=True`, `optimality_proven=False` |
| Result message | AC-3 State-Chain CSP for 15-Puzzle (T=1)  Variables: S[0]..S[T], where each value is a complete legal puzzle state. Binary constraint: consecutive values must differ by exactly one legal blank move. Endpoints: S[0]=start and S[T]=goal. This |

Khi thuyết trình:

1. Nói rõ state/action/cost model trước khi giải thích hình.
2. Chỉ vào evidence chính trên GIF: frontier, reached, candidate, belief, domain, utility hoặc score.
3. Kết thúc bằng guarantee và caveat để không claim quá mức.

### 20. Path Consistency

<p><img src="docs/assets/algorithm-demos/path-consistency.gif" alt="Path Consistency real GIF" width="560"></p>

| Trục đọc | Nội dung |
|---|---|
| Nhóm | CSP |
| Vai trò | Extension |
| Learning goal | Inspect consistency across triples of variables. |
| Cơ chế | Check pair/triple compatibility in the model. |
| Evidence trong GIF | consistency events and remaining domains. |
| Guarantee | Educational consistency evidence. |
| Caveat | Not a shortest-path solver. |
| Web capture source | `live_streamlit_browser_capture` via `agent-browser screenshot` |
| web_run_status | `ran_model_not_goal_path` - ran successfully as model evidence, not a solved path |
| Demo input | seed `42`, termination `model_success`, default demo parameters |
| Certificate flags | `path_verified=False`, `goal_reached=False`, `optimality_proven=False` |
| Result message | Path Consistency (Illustration for 15-Puzzle CSP)  Path consistency extends arc consistency to triples of variables. For variables Xi, Xj, Xk, every allowed (Xi, Xj) pair must have a supporting value of Xk that satisfies both connecting con |

Khi thuyết trình:

1. Nói rõ state/action/cost model trước khi giải thích hình.
2. Chỉ vào evidence chính trên GIF: frontier, reached, candidate, belief, domain, utility hoặc score.
3. Kết thúc bằng guarantee và caveat để không claim quá mức.

### 21. Global Constraints

<p><img src="docs/assets/algorithm-demos/global-constraints.gif" alt="Global Constraints real GIF" width="560"></p>

| Trục đọc | Nội dung |
|---|---|
| Nhóm | CSP |
| Vai trò | Extension |
| Learning goal | Use all-different and structural constraints. |
| Cơ chế | Apply global constraint checks over the state chain. |
| Evidence trong GIF | constraint status and domain evidence. |
| Guarantee | Rules out impossible assignments. |
| Caveat | Does not replace graph-search optimality. |
| Web capture source | `live_streamlit_browser_capture` via `agent-browser screenshot` |
| web_run_status | `ran_model_not_goal_path` - ran successfully as model evidence, not a solved path |
| Demo input | seed `42`, termination `model_success`, default demo parameters |
| Certificate flags | `path_verified=False`, `goal_reached=False`, `optimality_proven=False` |
| Result message | Global Constraints in 15-Puzzle CSP  AllDifferent(X[t][0], X[t][1], ..., X[t][15]):   At each time step t, all 16 positions must contain distinct tiles (0-15).  This is a GLOBAL constraint because it involves all 16 variables at once. A bin |

Khi thuyết trình:

1. Nói rõ state/action/cost model trước khi giải thích hình.
2. Chỉ vào evidence chính trên GIF: frontier, reached, candidate, belief, domain, utility hoặc score.
3. Kết thúc bằng guarantee và caveat để không claim quá mức.

### 22. Backtracking Search

<p><img src="docs/assets/algorithm-demos/backtracking-search.gif" alt="Backtracking Search real GIF" width="560"></p>

| Trục đọc | Nội dung |
|---|---|
| Nhóm | CSP |
| Vai trò | Extension |
| Learning goal | Search assignments in the CSP model. |
| Cơ chế | Depth-first assignment with constraint checks. |
| Evidence trong GIF | assigned variables, backtrack reason and final path if found. |
| Guarantee | Can solve small exact-horizon demos. |
| Caveat | Horizon-bound; not a global shortest-path claim. |
| Web capture source | `live_streamlit_browser_capture` via `agent-browser screenshot` |
| web_run_status | `solved_not_optimal` - reached goal without an optimality certificate |
| Demo input | seed `42`, termination `goal`, `max_steps=600` |
| Certificate flags | `path_verified=True`, `goal_reached=True`, `optimality_proven=False` |
| Result message | Bounded transition-planning demo found a path with T=1. This run orders child nodes by Manhattan Distance heuristic, not MRV/forward checking. |

Khi thuyết trình:

1. Nói rõ state/action/cost model trước khi giải thích hình.
2. Chỉ vào evidence chính trên GIF: frontier, reached, candidate, belief, domain, utility hoặc score.
3. Kết thúc bằng guarantee và caveat để không claim quá mức.

### 23. Min-Conflicts

<p><img src="docs/assets/algorithm-demos/min-conflicts.gif" alt="Min-Conflicts real GIF" width="560"></p>

| Trục đọc | Nội dung |
|---|---|
| Nhóm | CSP |
| Vai trò | Extension |
| Learning goal | Repair an assignment by reducing conflicts. |
| Cơ chế | Randomized local repair over CSP variables. |
| Evidence trong GIF | conflict count, selected variable and seed. |
| Guarantee | Useful concept for CSP repair. |
| Caveat | Better suited to N-Queens style CSPs than canonical 15-puzzle. |
| Web capture source | `live_streamlit_browser_capture` via `agent-browser screenshot` |
| web_run_status | `ran_model_not_goal_path` - ran successfully as model evidence, not a solved path |
| Demo input | seed `42`, termination `model_success`, `max_iterations=80` |
| Certificate flags | `path_verified=False`, `goal_reached=False`, `optimality_proven=False` |
| Result message | Goal reached after 1 iterations via tile swaps. This is a CSP repair trace, NOT a sequence of legal 15-puzzle moves. |

Khi thuyết trình:

1. Nói rõ state/action/cost model trước khi giải thích hình.
2. Chỉ vào evidence chính trên GIF: frontier, reached, candidate, belief, domain, utility hoặc score.
3. Kết thúc bằng guarantee và caveat để không claim quá mức.

### 24. Constraint Graphs

<p><img src="docs/assets/algorithm-demos/constraint-graphs.gif" alt="Constraint Graphs real GIF" width="560"></p>

| Trục đọc | Nội dung |
|---|---|
| Nhóm | CSP |
| Vai trò | Extension |
| Learning goal | Visualize variables as a constraint network. |
| Cơ chế | Build graph nodes/edges from CSP relations. |
| Evidence trong GIF | constraint graph summary and consistency evidence. |
| Guarantee | Explains structure, not a solver certificate. |
| Caveat | Graph readability matters more than path optimality here. |
| Web capture source | `live_streamlit_browser_capture` via `agent-browser screenshot` |
| web_run_status | `ran_model_not_goal_path` - ran successfully as model evidence, not a solved path |
| Demo input | seed `42`, termination `model_success`, `time_horizon=1` |
| Certificate flags | `path_verified=False`, `goal_reached=False`, `optimality_proven=False` |
| Result message | Constraint Graph for 15-Puzzle CSP (T=1)  Nodes: Variables (X[t][p] and A[t]) Edges: Constraints between variables  For T=1:   Position variables: X[0][0..15], X[1][0..15], ... X[1][0..15]   Action variables: A[0], A[1], ... A[1-1]  Constra |

Khi thuyết trình:

1. Nói rõ state/action/cost model trước khi giải thích hình.
2. Chỉ vào evidence chính trên GIF: frontier, reached, candidate, belief, domain, utility hoặc score.
3. Kết thúc bằng guarantee và caveat để không claim quá mức.

## AI-vs-AI Tournament: từng thuật toán

### 25. AI-vs-AI Tournament

<p><img src="docs/assets/algorithm-demos/ai-vs-ai-tournament.gif" alt="AI-vs-AI Tournament real GIF" width="560"></p>

| Trục đọc | Nội dung |
|---|---|
| Nhóm | AI-vs-AI Tournament |
| Vai trò | Scoring layer |
| Learning goal | Score two agents against the same A* reference. |
| Cơ chế | Run two solvers and classify verified trajectories. |
| Evidence trong GIF | points, optimal cost, excess cost and invalid-path penalties. |
| Guarantee | Fair benchmark when the reference certificate exists. |
| Caveat | Tournament is not a natural adversarial PEAS model. |
| Web capture source | `live_streamlit_browser_capture` via `agent-browser screenshot` |
| web_run_status | `ran_tournament_model` - scored tournament model, not one solution path |
| Demo input | seed `42`, termination `tournament_scored`, default demo parameters |
| Certificate flags | `path_verified=True`, `goal_reached=True`, `optimality_proven=False` |
| Result message | Tournament scoring run |

Khi thuyết trình:

1. Nói rõ state/action/cost model trước khi giải thích hình.
2. Chỉ vào evidence chính trên GIF: frontier, reached, candidate, belief, domain, utility hoặc score.
3. Kết thúc bằng guarantee và caveat để không claim quá mức.

### 26. Minimax

<p><img src="docs/assets/algorithm-demos/minimax.gif" alt="Minimax real GIF" width="560"></p>

| Trục đọc | Nội dung |
|---|---|
| Nhóm | AI-vs-AI Tournament |
| Vai trò | Robustness demo |
| Learning goal | Interpret MIN as worst-case robustness, not a real puzzle opponent. |
| Cơ chế | Alternate MAX promising moves with MIN worst-case legal continuations. |
| Evidence trong GIF | MAX/MIN nodes, utility and selected root action. |
| Guarantee | Depth-limited worst-case decision rule. |
| Caveat | Both sides share legal blank moves because 15-puzzle has no natural adversary. |
| Web capture source | `live_streamlit_browser_capture` via `agent-browser screenshot` |
| web_run_status | `solved_not_optimal` - reached goal without an optimality certificate |
| Demo input | seed `42`, termination `goal`, `depth=2` |
| Certificate flags | `path_verified=True`, `goal_reached=True`, `optimality_proven=False` |
| Result message | Minimax (depth=2) Completed depth 2 Best utility: 1000.0 MAX selects the most promising legal move. MIN branch models worst-case legal continuations, not a real opponent. Standard 15-puzzle has no natural adversary; this is robustness analy |

Khi thuyết trình:

1. Nói rõ state/action/cost model trước khi giải thích hình.
2. Chỉ vào evidence chính trên GIF: frontier, reached, candidate, belief, domain, utility hoặc score.
3. Kết thúc bằng guarantee và caveat để không claim quá mức.

### 27. Alpha-Beta Pruning

<p><img src="docs/assets/algorithm-demos/alpha-beta-pruning.gif" alt="Alpha-Beta Pruning real GIF" width="560"></p>

| Trục đọc | Nội dung |
|---|---|
| Nhóm | AI-vs-AI Tournament |
| Vai trò | Robustness demo |
| Learning goal | Learn branch-and-bound pruning over the same worst-case tree. |
| Cơ chế | Prune branches that cannot change the minimax root value. |
| Evidence trong GIF | alpha, beta, pruned branches and root utility. |
| Guarantee | Same root value as full Minimax for the searched tree. |
| Caveat | Pruning saves nodes; it does not turn the puzzle into a real two-player game. |
| Web capture source | `live_streamlit_browser_capture` via `agent-browser screenshot` |
| web_run_status | `solved_not_optimal` - reached goal without an optimality certificate |
| Demo input | seed `42`, termination `goal`, `depth=2` |
| Certificate flags | `path_verified=True`, `goal_reached=True`, `optimality_proven=False` |
| Result message | Alpha-Beta Pruning (depth=2) Completed depth 2 Best utility: 1000.0 Nodes expanded: 8 Cutoff events: 1 MIN branch models worst-case legal continuations, not a real opponent. With identical ordering, no timeout, and a completed depth, Alpha- |

Khi thuyết trình:

1. Nói rõ state/action/cost model trước khi giải thích hình.
2. Chỉ vào evidence chính trên GIF: frontier, reached, candidate, belief, domain, utility hoặc score.
3. Kết thúc bằng guarantee và caveat để không claim quá mức.

### 28. Expectimax

<p><img src="docs/assets/algorithm-demos/expectimax.gif" alt="Expectimax real GIF" width="560"></p>

| Trục đọc | Nội dung |
|---|---|
| Nhóm | AI-vs-AI Tournament |
| Vai trò | Chance demo |
| Learning goal | Compare expected value against worst-case reasoning. |
| Cơ chế | Replace MIN with CHANCE outcomes and success probability. |
| Evidence trong GIF | CHANCE nodes, probabilities and expected utility. |
| Guarantee | Depth-limited expected-value policy under the chosen probability model. |
| Caveat | Probability model is educational and must be stated before interpreting the result. |
| Web capture source | `live_streamlit_browser_capture` via `agent-browser screenshot` |
| web_run_status | `solved_not_optimal` - reached goal without an optimality certificate |
| Demo input | seed `42`, termination `goal`, `depth=2`, `success_prob=0.75`, `seed=11` |
| Certificate flags | `path_verified=True`, `goal_reached=True`, `optimality_proven=False` |
| Result message | Expectimax (depth=2, success_prob=0.75) Completed depth 2 Expected utility from start: 749.5 Nodes expanded: 4  Comparison with Minimax:   Minimax: evaluates WORST-CASE legal continuations   Expectimax: computes EXPECTED outcome with CHANCE |

Khi thuyết trình:

1. Nói rõ state/action/cost model trước khi giải thích hình.
2. Chỉ vào evidence chính trên GIF: frontier, reached, candidate, belief, domain, utility hoặc score.
3. Kết thúc bằng guarantee và caveat để không claim quá mức.

## Cách Đọc Evidence

| Trường | Nghĩa |
|---|---|
| `path_verified` | Chuỗi action là legal blank moves. |
| `goal_reached` | State cuối bằng goal đã chọn. |
| `optimality_proven` | Chỉ true khi thuật toán optimal, path hợp lệ, tới goal và termination là `goal`. |
| `frontier` | Node đang chờ xét. |
| `reached` | State/record đã biết trong reached, best_g hoặc best_depth. |
| `g(n)` | Path cost từ start tới node. |
| `h(n)` | Heuristic estimate tới goal. |
| `f(n)` | Priority của A*: `g(n)+h(n)`. |
| `trace` | Bằng chứng từng bước: generate, expand, select, prune, accept/reject. |
| `web_run_status` | Trạng thái thật của browser capture: solved, partial/model, not solved hoặc tournament. |
| `source` | Phải là `live_streamlit_browser_capture`; nếu khác thì asset không được xem là GIF web thật. |

Ba tầng chứng minh phải đọc riêng:

```text
Path legal       !=  Goal reached
Goal reached     !=  Optimal
Algorithm success !=  Solver chuẩn của 15-puzzle
```

## Tài Liệu

- [Algorithm demo gallery](docs/algorithm-demo-gallery.md)
- [Algorithm correctness matrix](docs/algorithm-correctness-matrix.md)
- [UI/UX evidence surfaces](docs/ui-ux-evidence-surfaces.md)
- [Known limitations](docs/known-limitations.md)
- [Deep bug audit](docs/deep-bug-audit.md)
- [Project overview/PDR](docs/project-overview-pdr.md)
- [Codebase summary](docs/codebase-summary.md)
- [System architecture](docs/system-architecture.md)
- [Algorithm test plan](docs/algorithm-test-plan.md)
- [Academic reference for groups](docs/algorithm-groups-academic-reference.md)
- [Project roadmap](docs/project-roadmap.md)
