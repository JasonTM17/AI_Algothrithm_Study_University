# Algorithm Demo Gallery

Trang này nhúng đủ 28 GIF chạy thật. Mỗi GIF lấy frame từ live Streamlit browser capture bằng `agent-browser screenshot` và có manifest semantic tại `docs/assets/algorithm-demos/manifest.json`.

## Uninformed Search

**Mục tiêu:** Duyet state-space without heuristic; evidence focuses on frontier/reached and legal path.

### BFS

<p><img src="assets/algorithm-demos/bfs.gif" alt="BFS" width="720"></p>

- **Learning goal:** Understand level-order expansion and why unit-cost BFS can certify shortest paths.
- **Mechanism:** FIFO frontier over puzzle states.
- **Trace evidence:** frontier size, reached set, legal path and path cost.
- **Guarantee:** Complete and optimal for unit step cost if resources suffice.
- **Caveat:** Memory grows quickly; good for shallow teaching cases, not deep 15-puzzle production search.
- **Phù hợp với 15-puzzle chuẩn:** Solver chuẩn cho ca nông: complete và optimal với unit step cost, nhưng frontier/reached tăng rất nhanh nên không hợp cho 15-puzzle sâu.
- **Source:** `live_streamlit_browser_capture` via `agent-browser screenshot`.
- **web_run_status:** `solved_optimal` - reached goal with an optimality certificate.
- **Result message:** Solution found
- **Manifest:** termination `goal`, profile `algorithm`, frames `6`, verified `2026-06-27`.

### DFS

<p><img src="assets/algorithm-demos/dfs.gif" alt="DFS" width="720"></p>

- **Learning goal:** See how depth-first commitment differs from optimal state-space search.
- **Mechanism:** LIFO stack with depth-aware duplicate handling.
- **Trace evidence:** expanded nodes, depth limit and legal trajectory when present.
- **Guarantee:** No shortest-path guarantee in this app setting.
- **Caveat:** Can chase a deep branch and miss a shorter path.
- **Phù hợp với 15-puzzle chuẩn:** Không dùng làm solver chuẩn: có thể tìm được một path hợp lệ nhưng không bảo đảm ngắn nhất và dễ đi sâu vào nhánh kém.
- **Source:** `live_streamlit_browser_capture` via `agent-browser screenshot`.
- **web_run_status:** `solved_not_optimal` - reached goal without an optimality certificate.
- **Result message:** Solution found
- **Manifest:** termination `goal`, profile `algorithm`, frames `8`, verified `2026-06-27`.

### UCS

<p><img src="assets/algorithm-demos/ucs.gif" alt="UCS" width="720"></p>

- **Learning goal:** Connect path cost g(n) to optimal search.
- **Mechanism:** Priority queue ordered by cumulative path cost.
- **Trace evidence:** g(n), frontier, reached and cost certificate.
- **Guarantee:** Complete and optimal for non-negative costs.
- **Caveat:** On unit-cost 15-puzzle it behaves like BFS but keeps the general cost model explicit.
- **Phù hợp với 15-puzzle chuẩn:** Solver chuẩn khi chi phí bước không âm. Với 15-puzzle unit cost, UCS gần tương đương BFS nhưng giữ rõ mô hình path cost g(n).
- **Source:** `live_streamlit_browser_capture` via `agent-browser screenshot`.
- **web_run_status:** `solved_optimal` - reached goal with an optimality certificate.
- **Result message:** Solution found
- **Manifest:** termination `goal`, profile `algorithm`, frames `6`, verified `2026-06-27`.

### IDS

<p><img src="assets/algorithm-demos/ids.gif" alt="IDS" width="720"></p>

- **Learning goal:** Trade BFS optimality for DFS-like memory by increasing the depth limit.
- **Mechanism:** Repeated depth-limited DFS with cutoff tracking.
- **Trace evidence:** depth limit, cutoff/exhausted reason and legal path.
- **Guarantee:** Complete and optimal for unit step cost if the limit reaches the solution depth.
- **Caveat:** Repeats work across iterations; the trace should be read by limit, not as one queue.
- **Phù hợp với 15-puzzle chuẩn:** Solver chuẩn cho unit-cost khi depth limit đủ lớn: tiết kiệm bộ nhớ hơn BFS nhưng lặp lại nhiều lần qua các giới hạn độ sâu.
- **Source:** `live_streamlit_browser_capture` via `agent-browser screenshot`.
- **web_run_status:** `solved_optimal` - reached goal with an optimality certificate.
- **Result message:** Found at depth 5, limit=5
- **Manifest:** termination `goal`, profile `algorithm`, frames `6`, verified `2026-06-27`.

## Informed Search

**Mục tiêu:** Add h(n), then combine with g(n) for optimal informed search.

### Greedy Best-First

<p><img src="assets/algorithm-demos/greedy-best-first.gif" alt="Greedy Best-First" width="720"></p>

- **Learning goal:** Show why h(n) alone is fast but not a certificate.
- **Mechanism:** Priority queue ordered only by heuristic h(n).
- **Trace evidence:** selected h(n), frontier and whether the final path reaches goal.
- **Guarantee:** No optimality guarantee.
- **Caveat:** May find a longer path or get misled by a locally attractive state.
- **Phù hợp với 15-puzzle chuẩn:** Không dùng để chứng minh tối ưu: h(n) giúp chạy nhanh hơn nhưng bỏ qua g(n), nên path có thể dài hơn A*.
- **Source:** `live_streamlit_browser_capture` via `agent-browser screenshot`.
- **web_run_status:** `solved_not_optimal` - reached goal without an optimality certificate.
- **Result message:** Solution found
- **Manifest:** termination `goal`, profile `algorithm`, frames `6`, verified `2026-06-27`.

### A*

<p><img src="assets/algorithm-demos/astar.gif" alt="A*" width="720"></p>

- **Learning goal:** Read f(n)=g(n)+h(n) and the Manhattan optimality condition.
- **Mechanism:** Priority queue ordered by g(n)+h(n).
- **Trace evidence:** g/h/f, expanded/generated/frontier, legal path and optimality flag.
- **Guarantee:** Optimal with admissible and consistent heuristic when resources do not stop the run.
- **Caveat:** The certificate is valid only for the selected goal and heuristic contract.
- **Phù hợp với 15-puzzle chuẩn:** Solver chuẩn chính của app: với Manhattan Distance admissible/consistent và unit step cost, có thể bật optimality_proven khi tới goal.
- **Source:** `live_streamlit_browser_capture` via `agent-browser screenshot`.
- **web_run_status:** `solved_optimal` - reached goal with an optimality certificate.
- **Result message:** Solution found
- **Manifest:** termination `goal`, profile `algorithm`, frames `11`, verified `2026-06-27`.

### IDA*

<p><img src="assets/algorithm-demos/idastar.gif" alt="IDA*" width="720"></p>

- **Learning goal:** Combine A* evaluation with memory-bounded iterative thresholds.
- **Mechanism:** Depth-first search bounded by increasing f-threshold.
- **Trace evidence:** threshold, reached metric, legal path and optimality flag.
- **Guarantee:** Optimal with admissible heuristic and sufficient threshold iterations.
- **Caveat:** May revisit many states; trace is threshold-based, not a single frontier queue.
- **Phù hợp với 15-puzzle chuẩn:** Solver chuẩn memory-bounded: hợp với 15-puzzle sâu hơn A* về bộ nhớ, đổi lại có thể revisit nhiều state theo threshold.
- **Source:** `live_streamlit_browser_capture` via `agent-browser screenshot`.
- **web_run_status:** `solved_optimal` - reached goal with an optimality certificate.
- **Result message:** Found with threshold=4
- **Manifest:** termination `goal`, profile `algorithm`, frames `6`, verified `2026-06-27`.

## Local Search

**Mục tiêu:** Show candidate-level choices without treating the run as guaranteed path search.

### Simple Hill Climbing

<p><img src="assets/algorithm-demos/simple-hill-climbing.gif" alt="Simple Hill Climbing" width="720"></p>

- **Learning goal:** Watch the first improving candidate win or the search stop.
- **Mechanism:** Scan neighbors and move to the first lower h(n).
- **Trace evidence:** candidate h, selected action and stop reason.
- **Guarantee:** No completeness or optimality guarantee.
- **Caveat:** Local optimum can stop the run far from the goal.
- **Phù hợp với 15-puzzle chuẩn:** Không ổn làm solver chuẩn: chỉ đi theo cải thiện cục bộ và có thể dừng ở local optimum dù goal chưa đạt. GIF ghi trung thực rằng demo không tạo solution claim.
- **Source:** `live_streamlit_browser_capture` via `agent-browser screenshot`.
- **web_run_status:** `not_solved_in_demo` - web demo completed without a solution claim.
- **Result message:** Stuck at local optimum h=4.0
- **Manifest:** termination `stopped`, profile `algorithm`, frames `6`, verified `2026-06-27`.

### Steepest-Ascent Hill Climbing

<p><img src="assets/algorithm-demos/steepest-ascent-hill-climbing.gif" alt="Steepest-Ascent Hill Climbing" width="720"></p>

- **Learning goal:** Compare all local neighbors before moving.
- **Mechanism:** Choose the neighbor with best h(n) decrease.
- **Trace evidence:** evaluated candidates, best candidate and reject/accept reason.
- **Guarantee:** No completeness or optimality guarantee.
- **Caveat:** Still local; evaluating every neighbor does not solve plateaus.
- **Phù hợp với 15-puzzle chuẩn:** Không ổn làm solver chuẩn: xét hết neighbor cục bộ tốt hơn Simple HC nhưng vẫn kẹt plateau/local optimum. GIF ghi trung thực rằng demo không tạo solution claim.
- **Source:** `live_streamlit_browser_capture` via `agent-browser screenshot`.
- **web_run_status:** `not_solved_in_demo` - web demo completed without a solution claim.
- **Result message:** Stuck at local optimum h=4.0
- **Manifest:** termination `stopped`, profile `algorithm`, frames `6`, verified `2026-06-27`.

### Stochastic Hill Climbing

<p><img src="assets/algorithm-demos/stochastic-hill-climbing.gif" alt="Stochastic Hill Climbing" width="720"></p>

- **Learning goal:** See randomness among improving candidates.
- **Mechanism:** Sample one improving move using a fixed seed.
- **Trace evidence:** candidate pool, chosen action, seed and legal trajectory.
- **Guarantee:** No deterministic optimality guarantee.
- **Caveat:** Different seeds can produce different partial trajectories.
- **Phù hợp với 15-puzzle chuẩn:** Không ổn làm solver chuẩn: seed khác có thể cho trajectory khác, không có completeness hay optimality certificate. GIF ghi trung thực rằng demo không tạo solution claim.
- **Source:** `live_streamlit_browser_capture` via `agent-browser screenshot`.
- **web_run_status:** `not_solved_in_demo` - web demo completed without a solution claim.
- **Result message:** Stuck at local optimum h=4.0
- **Manifest:** termination `stopped`, profile `algorithm`, frames `6`, verified `2026-06-27`.

### Random-Restart Hill Climbing

<p><img src="assets/algorithm-demos/random-restart-hill-climbing.gif" alt="Random-Restart Hill Climbing" width="720"></p>

- **Learning goal:** Use restarts to escape one bad local basin.
- **Mechanism:** Run multiple hill climbs from deterministic restart states.
- **Trace evidence:** restart index, best h(n) and selected trajectory.
- **Guarantee:** Still not a complete 15-puzzle solver here.
- **Caveat:** More restarts improve chances but do not prove optimality.
- **Phù hợp với 15-puzzle chuẩn:** Không ổn làm solver chuẩn: restart tăng cơ hội thoát basin xấu nhưng vẫn không chứng minh được shortest path. GIF ghi trung thực rằng demo không tạo solution claim.
- **Source:** `live_streamlit_browser_capture` via `agent-browser screenshot`.
- **web_run_status:** `not_solved_in_demo` - web demo completed without a solution claim.
- **Result message:** Best h=4.0 after 3 restarts
- **Manifest:** termination `stopped`, profile `algorithm`, frames `6`, verified `2026-06-27`.

### Local Beam Search

<p><img src="assets/algorithm-demos/local-beam-search.gif" alt="Local Beam Search" width="720"></p>

- **Learning goal:** Track several local candidates at once.
- **Mechanism:** Keep k best states per iteration.
- **Trace evidence:** beam width, candidate scores and selected beam states.
- **Guarantee:** No optimality guarantee.
- **Caveat:** The beam can collapse to similar states and miss the global route.
- **Phù hợp với 15-puzzle chuẩn:** Không ổn làm solver chuẩn: giữ nhiều candidate giúp minh họa tìm kiếm cục bộ, nhưng beam nhỏ có thể bỏ mất route tốt.
- **Source:** `live_streamlit_browser_capture` via `agent-browser screenshot`.
- **web_run_status:** `solved_not_optimal` - reached goal without an optimality certificate.
- **Result message:** Goal reached
- **Manifest:** termination `goal`, profile `algorithm`, frames `8`, verified `2026-06-27`.

### Simulated Annealing

<p><img src="assets/algorithm-demos/simulated-annealing.gif" alt="Simulated Annealing" width="720"></p>

- **Learning goal:** Understand probabilistic acceptance of worse moves.
- **Mechanism:** Temperature-controlled accept/reject over neighbors.
- **Trace evidence:** temperature, probability, accepted flag and legal trajectory.
- **Guarantee:** No certificate of reaching or optimizing the goal.
- **Caveat:** A legal trajectory is not automatically a solution.
- **Phù hợp với 15-puzzle chuẩn:** Không ổn làm solver chuẩn: có thể nhận bước xấu để thoát local optimum, nhưng legal trajectory không đồng nghĩa solved hoặc optimal. GIF ghi trung thực rằng demo không tạo solution claim.
- **Source:** `live_streamlit_browser_capture` via `agent-browser screenshot`.
- **web_run_status:** `not_solved_in_demo` - web demo completed without a solution claim.
- **Result message:** Best h=5.0, temp=98.0684
- **Manifest:** termination `stopped`, profile `algorithm`, frames `8`, verified `2026-06-27`.

## Complex Environments

**Mục tiêu:** Model conditional, belief-state and online variants that extend the basic 15-puzzle PEAS.

### AND-OR Search

<p><img src="assets/algorithm-demos/and-or-search.gif" alt="AND-OR Search" width="720"></p>

- **Learning goal:** Read a conditional plan under possible outcome deflections.
- **Mechanism:** OR chooses action; AND requires subplans for supported outcomes.
- **Trace evidence:** conditional branches, depth limit and deflection support mode.
- **Guarantee:** Returns a policy-like conditional plan, not a linear shortest path.
- **Caveat:** The support switch is not probability weighting.
- **Phù hợp với 15-puzzle chuẩn:** Không phải solver tuyến tính của 15-puzzle deterministic: dùng để minh họa conditional plan khi môi trường có outcome lệch. GIF là model evidence, không phải path tới goal.
- **Source:** `live_streamlit_browser_capture` via `agent-browser screenshot`.
- **web_run_status:** `ran_model_not_goal_path` - ran successfully as model evidence, not a solved path.
- **Result message:** Conditional plan found (depth limit=2). AND-OR requires every supported outcome to succeed. Deflection support=intended outcome only; nondet_prob>0 adds all legal deflections, not probability-weighted branches. OR: choose action R (h=1.0)
- **Manifest:** termination `model_success`, profile `algorithm`, frames `6`, verified `2026-06-27`.

### Searching with no observation

<p><img src="assets/algorithm-demos/searching-with-no-observation.gif" alt="Searching with no observation" width="720"></p>

- **Learning goal:** Separate hidden actual state from belief-state decision making.
- **Mechanism:** Maintain a belief set when observations reveal no tile positions.
- **Trace evidence:** belief size, planner votes, fallback votes and action trace.
- **Guarantee:** Demonstrates belief reasoning; not a standard full-observation solver.
- **Caveat:** Hidden state is shown only as debug evidence.
- **Phù hợp với 15-puzzle chuẩn:** Không phải solver chuẩn full-observation: dùng belief set khi agent không thấy trạng thái thật; hidden state chỉ để debug. GIF ghi trung thực rằng demo không tạo solution claim.
- **Source:** `live_streamlit_browser_capture` via `agent-browser screenshot`.
- **web_run_status:** `not_solved_in_demo` - web demo completed without a solution claim.
- **Result message:** Belief size=4 after 3 steps. No observation keeps a belief set; planner=A* Search cannot safely collapse it.
- **Manifest:** termination `stopped`, profile `algorithm`, frames `6`, verified `2026-06-27`.

### Searching for partially observable problems

<p><img src="assets/algorithm-demos/searching-for-partially-observable-problems.gif" alt="Searching for partially observable problems" width="720"></p>

- **Learning goal:** Use known tile positions to reduce the belief set.
- **Mechanism:** Filter belief candidates using a known-tile matrix.
- **Trace evidence:** known positions, belief size, planner votes and fallback reason.
- **Guarantee:** Can propose legal actions under partial knowledge.
- **Caveat:** With too few known tiles, the belief set can still be ambiguous.
- **Phù hợp với 15-puzzle chuẩn:** Không phải solver chuẩn khi chỉ biết vài ô: dùng known-tile matrix để thu hẹp belief, vẫn có thể mơ hồ.
- **Source:** `live_streamlit_browser_capture` via `agent-browser screenshot`.
- **web_run_status:** `solved_not_optimal` - reached goal without an optimality certificate.
- **Result message:** Actual state reached goal
- **Manifest:** termination `goal`, profile `algorithm`, frames `6`, verified `2026-06-27`.

### LRTA*

<p><img src="assets/algorithm-demos/lrtastar.gif" alt="LRTA*" width="720"></p>

- **Learning goal:** Study online heuristic learning one action at a time.
- **Mechanism:** Update H(s) after observing local successors.
- **Trace evidence:** online step, H update, chosen action and cap reason.
- **Guarantee:** Online learning demo, not an offline optimal certificate.
- **Caveat:** The node cap is a max online-step cap in the UI.
- **Phù hợp với 15-puzzle chuẩn:** Không phải offline optimal solver: minh họa agent online cập nhật H(s) từng bước, cap là số bước hành động tối đa.
- **Source:** `live_streamlit_browser_capture` via `agent-browser screenshot`.
- **web_run_status:** `solved_not_optimal` - reached goal without an optimality certificate.
- **Result message:** Goal reached online
- **Manifest:** termination `goal`, profile `algorithm`, frames `6`, verified `2026-06-27`.

## CSP

**Mục tiêu:** Reframe puzzle planning as variables, domains and constraints.

### CSP Definition

<p><img src="assets/algorithm-demos/csp-definition.gif" alt="CSP Definition" width="720"></p>

- **Learning goal:** Name variables, domains and constraints.
- **Mechanism:** Build a state-chain CSP model.
- **Trace evidence:** variables/domains/constraints count.
- **Guarantee:** Model definition only.
- **Caveat:** A model is not yet a solved trajectory.
- **Phù hợp với 15-puzzle chuẩn:** Không giải puzzle trực tiếp: chỉ dựng mô hình biến/domain/constraint để người học hiểu cách mã hóa bài toán. GIF là model evidence, không phải path tới goal.
- **Source:** `live_streamlit_browser_capture` via `agent-browser screenshot`.
- **web_run_status:** `ran_model_not_goal_path` - ran successfully as model evidence, not a solved path.
- **Result message:** CSP Definition for 15-Puzzle (T=1)  Variables:   X[t][p]: tile at position p at time t, t=0..1, p=0..15   A[t]: action at time t, t=0..0  Total variables: 33  Domains:   X[0][p] = {15} (fixed by initial state)   X[1][p] = {0} (fixed by goal
- **Manifest:** termination `model_success`, profile `algorithm`, frames `6`, verified `2026-06-27`.

### Constraint Propagation

<p><img src="assets/algorithm-demos/constraint-propagation.gif" alt="Constraint Propagation" width="720"></p>

- **Learning goal:** See domains shrink before search.
- **Mechanism:** Apply AC-3 style propagation.
- **Trace evidence:** domain reductions and wipe-out status.
- **Guarantee:** Sound pruning for represented constraints.
- **Caveat:** Propagation alone may not decide the puzzle.
- **Phù hợp với 15-puzzle chuẩn:** Không thay thế graph search: propagation lọc domain trong horizon đã chọn, chỉ solved khi horizon khớp path demo.
- **Source:** `live_streamlit_browser_capture` via `agent-browser screenshot`.
- **web_run_status:** `solved_not_optimal` - reached goal without an optimality certificate.
- **Result message:** AC-3 State-Chain CSP for 15-Puzzle (T=1)  Variables: S[0]..S[T], where each value is a complete legal puzzle state. Binary constraint: consecutive values must differ by exactly one legal blank move. Endpoints: S[0]=start and S[T]=goal. This
- **Manifest:** termination `goal`, profile `algorithm`, frames `6`, verified `2026-06-27`.

### Path Consistency

<p><img src="assets/algorithm-demos/path-consistency.gif" alt="Path Consistency" width="720"></p>

- **Learning goal:** Inspect consistency across triples of variables.
- **Mechanism:** Check pair/triple compatibility in the model.
- **Trace evidence:** consistency events and remaining domains.
- **Guarantee:** Educational consistency evidence.
- **Caveat:** Not a shortest-path solver.
- **Phù hợp với 15-puzzle chuẩn:** Không giải 15-puzzle chuẩn: minh họa consistency trên ràng buộc, không sinh shortest path. GIF là model evidence, không phải path tới goal.
- **Source:** `live_streamlit_browser_capture` via `agent-browser screenshot`.
- **web_run_status:** `ran_model_not_goal_path` - ran successfully as model evidence, not a solved path.
- **Result message:** Path Consistency (Illustration for 15-Puzzle CSP)  Path consistency extends arc consistency to triples of variables. For variables Xi, Xj, Xk, every allowed (Xi, Xj) pair must have a supporting value of Xk that satisfies both connecting con
- **Manifest:** termination `model_success`, profile `algorithm`, frames `6`, verified `2026-06-27`.

### Global Constraints

<p><img src="assets/algorithm-demos/global-constraints.gif" alt="Global Constraints" width="720"></p>

- **Learning goal:** Use all-different and structural constraints.
- **Mechanism:** Apply global constraint checks over the state chain.
- **Trace evidence:** constraint status and domain evidence.
- **Guarantee:** Rules out impossible assignments.
- **Caveat:** Does not replace graph-search optimality.
- **Phù hợp với 15-puzzle chuẩn:** Không giải trực tiếp: kiểm tra ràng buộc toàn cục như AllDifferent, dùng để giải thích model CSP. GIF là model evidence, không phải path tới goal.
- **Source:** `live_streamlit_browser_capture` via `agent-browser screenshot`.
- **web_run_status:** `ran_model_not_goal_path` - ran successfully as model evidence, not a solved path.
- **Result message:** Global Constraints in 15-Puzzle CSP  AllDifferent(X[t][0], X[t][1], ..., X[t][15]):   At each time step t, all 16 positions must contain distinct tiles (0-15).  This is a GLOBAL constraint because it involves all 16 variables at once. A bin
- **Manifest:** termination `model_success`, profile `algorithm`, frames `6`, verified `2026-06-27`.

### Backtracking Search

<p><img src="assets/algorithm-demos/backtracking-search.gif" alt="Backtracking Search" width="720"></p>

- **Learning goal:** Search assignments in the CSP model.
- **Mechanism:** Depth-first assignment with constraint checks.
- **Trace evidence:** assigned variables, backtrack reason and final path if found.
- **Guarantee:** Can solve small exact-horizon demos.
- **Caveat:** Horizon-bound; not a global shortest-path claim.
- **Phù hợp với 15-puzzle chuẩn:** Chỉ hợp demo horizon nhỏ: có thể tìm path trong mô hình bounded transition, không claim tối ưu toàn cục.
- **Source:** `live_streamlit_browser_capture` via `agent-browser screenshot`.
- **web_run_status:** `solved_not_optimal` - reached goal without an optimality certificate.
- **Result message:** Bounded transition-planning demo found a path with T=1. This run orders child nodes by Manhattan Distance heuristic, not MRV/forward checking.
- **Manifest:** termination `goal`, profile `algorithm`, frames `6`, verified `2026-06-27`.

### Min-Conflicts

<p><img src="assets/algorithm-demos/min-conflicts.gif" alt="Min-Conflicts" width="720"></p>

- **Learning goal:** Repair an assignment by reducing conflicts.
- **Mechanism:** Randomized local repair over CSP variables.
- **Trace evidence:** conflict count, selected variable and seed.
- **Guarantee:** Useful concept for CSP repair.
- **Caveat:** Better suited to N-Queens style CSPs than canonical 15-puzzle.
- **Phù hợp với 15-puzzle chuẩn:** Không phù hợp 15-puzzle chuẩn: repair bằng tile swaps không nhất thiết là legal blank moves, nên không phải lời giải trượt ô. GIF là model evidence, không phải path tới goal.
- **Source:** `live_streamlit_browser_capture` via `agent-browser screenshot`.
- **web_run_status:** `ran_model_not_goal_path` - ran successfully as model evidence, not a solved path.
- **Result message:** Goal reached after 1 iterations via tile swaps. This is a CSP repair trace, NOT a sequence of legal 15-puzzle moves.
- **Manifest:** termination `model_success`, profile `algorithm`, frames `6`, verified `2026-06-27`.

### Constraint Graphs

<p><img src="assets/algorithm-demos/constraint-graphs.gif" alt="Constraint Graphs" width="720"></p>

- **Learning goal:** Visualize variables as a constraint network.
- **Mechanism:** Build graph nodes/edges from CSP relations.
- **Trace evidence:** constraint graph summary and consistency evidence.
- **Guarantee:** Explains structure, not a solver certificate.
- **Caveat:** Graph readability matters more than path optimality here.
- **Phù hợp với 15-puzzle chuẩn:** Không giải trực tiếp: trình bày graph biến/ràng buộc để đọc cấu trúc CSP, không phải solver path. GIF là model evidence, không phải path tới goal.
- **Source:** `live_streamlit_browser_capture` via `agent-browser screenshot`.
- **web_run_status:** `ran_model_not_goal_path` - ran successfully as model evidence, not a solved path.
- **Result message:** Constraint Graph for 15-Puzzle CSP (T=1)  Nodes: Variables (X[t][p] and A[t]) Edges: Constraints between variables  For T=1:   Position variables: X[0][0..15], X[1][0..15], ... X[1][0..15]   Action variables: A[0], A[1], ... A[1-1]  Constra
- **Manifest:** termination `model_success`, profile `algorithm`, frames `6`, verified `2026-06-27`.

## AI-vs-AI Tournament

**Mục tiêu:** Compare agents, robustness and chance models without pretending the puzzle has a natural opponent.

### AI-vs-AI Tournament

<p><img src="assets/algorithm-demos/ai-vs-ai-tournament.gif" alt="AI-vs-AI Tournament" width="720"></p>

- **Learning goal:** Score two agents against the same A* reference.
- **Mechanism:** Run two solvers and classify verified trajectories.
- **Trace evidence:** points, optimal cost, excess cost and invalid-path penalties.
- **Guarantee:** Fair benchmark when the reference certificate exists.
- **Caveat:** Tournament is not a natural adversarial PEAS model.
- **Phù hợp với 15-puzzle chuẩn:** Không phải thuật toán giải puzzle: là lớp chấm điểm hai solver bằng A* reference và verified trajectory.
- **Source:** `live_streamlit_browser_capture` via `agent-browser screenshot`.
- **web_run_status:** `ran_tournament_model` - scored tournament model, not one solution path.
- **Result message:** Tournament scoring run
- **Manifest:** termination `tournament_scored`, profile `algorithm`, frames `6`, verified `2026-06-27`.

### Minimax

<p><img src="assets/algorithm-demos/minimax.gif" alt="Minimax" width="720"></p>

- **Learning goal:** Interpret MIN as worst-case robustness, not a real puzzle opponent.
- **Mechanism:** Alternate MAX promising moves with MIN worst-case legal continuations.
- **Trace evidence:** MAX/MIN nodes, utility and selected root action.
- **Guarantee:** Depth-limited worst-case decision rule.
- **Caveat:** Both sides share legal blank moves because 15-puzzle has no natural adversary.
- **Phù hợp với 15-puzzle chuẩn:** Không phải solver tự nhiên của 15-puzzle: MIN là nhánh worst-case robustness, không phải đối thủ thật.
- **Source:** `live_streamlit_browser_capture` via `agent-browser screenshot`.
- **web_run_status:** `solved_not_optimal` - reached goal without an optimality certificate.
- **Result message:** Minimax (depth=2) Completed depth 2 Best utility: 1000.0 MAX selects the most promising legal move. MIN branch models worst-case legal continuations, not a real opponent. Standard 15-puzzle has no natural adversary; this is robustness analy
- **Manifest:** termination `goal`, profile `algorithm`, frames `6`, verified `2026-06-27`.

### Alpha-Beta Pruning

<p><img src="assets/algorithm-demos/alpha-beta-pruning.gif" alt="Alpha-Beta Pruning" width="720"></p>

- **Learning goal:** Learn branch-and-bound pruning over the same worst-case tree.
- **Mechanism:** Prune branches that cannot change the minimax root value.
- **Trace evidence:** alpha, beta, pruned branches and root utility.
- **Guarantee:** Same root value as full Minimax for the searched tree.
- **Caveat:** Pruning saves nodes; it does not turn the puzzle into a real two-player game.
- **Phù hợp với 15-puzzle chuẩn:** Không phải solver tự nhiên của 15-puzzle: chỉ prune cây Minimax worst-case cùng root value, không đổi puzzle thành game hai người.
- **Source:** `live_streamlit_browser_capture` via `agent-browser screenshot`.
- **web_run_status:** `solved_not_optimal` - reached goal without an optimality certificate.
- **Result message:** Alpha-Beta Pruning (depth=2) Completed depth 2 Best utility: 1000.0 Nodes expanded: 8 Cutoff events: 1 MIN branch models worst-case legal continuations, not a real opponent. With identical ordering, no timeout, and a completed depth, Alpha-
- **Manifest:** termination `goal`, profile `algorithm`, frames `6`, verified `2026-06-27`.

### Expectimax

<p><img src="assets/algorithm-demos/expectimax.gif" alt="Expectimax" width="720"></p>

- **Learning goal:** Compare expected value against worst-case reasoning.
- **Mechanism:** Replace MIN with CHANCE outcomes and success probability.
- **Trace evidence:** CHANCE nodes, probabilities and expected utility.
- **Guarantee:** Depth-limited expected-value policy under the chosen probability model.
- **Caveat:** Probability model is educational and must be stated before interpreting the result.
- **Phù hợp với 15-puzzle chuẩn:** Không phải solver chuẩn: dùng CHANCE/probability model để so expected value, xác suất là mô hình giáo dục.
- **Source:** `live_streamlit_browser_capture` via `agent-browser screenshot`.
- **web_run_status:** `solved_not_optimal` - reached goal without an optimality certificate.
- **Result message:** Expectimax (depth=2, success_prob=0.75) Completed depth 2 Expected utility from start: 749.5 Nodes expanded: 4  Comparison with Minimax:   Minimax: evaluates WORST-CASE legal continuations   Expectimax: computes EXPECTED outcome with CHANCE
- **Manifest:** termination `goal`, profile `algorithm`, frames `6`, verified `2026-06-27`.

## Tái tạo

```bash
python scripts/generate-readme-gifs.py --featured --profile all --theme dark
python scripts/generate-readme-gifs.py --all --profile algorithm --theme dark
python scripts/generate-readme-gifs.py --check --check-readability
```
