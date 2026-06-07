"""Academic theory notes for all 27 algorithms across 6 groups."""

THEORY = {}

# ============================================================
# GROUP 1: UNINFORMED SEARCH
# ============================================================

THEORY["BFS"] = {
    "name": "BFS — Breadth-First Search",
    "group": "Uninformed Search",
    "goal": "Tìm đường đi ngắn nhất trong không gian trạng thái (mỗi bước cost = 1).",
    "goal_en": "Find the shortest path in the state space (unit step cost = 1).",
    "idea": "Duyệt theo mức: mở rộng tất cả node ở depth d trước khi sang depth d+1. Dùng hàng đợi FIFO.",
    "idea_en": "Level-by-level exploration: expand all nodes at depth d before moving to d+1. Uses a FIFO queue.",
    "data_structure": "Queue (FIFO) cho Frontier, Set/Dict cho Reached.",
    "data_structure_en": "Queue (FIFO) for Frontier, Set/Dict for Reached.",
    "formula": "Mỗi node có g(n) = depth từ root. BFS ưu tiên node có g nhỏ nhất (FIFO guarantee).",
    "formula_en": "Each node has g(n) = depth from root. BFS prioritizes nodes with the lowest g (FIFO guarantee).",
    "pseudocode": """BFS(start, goal):
  Frontier ← Queue chứa start
  Reached ← {start: 0}
  while Frontier không rỗng:
    node ← Frontier.dequeue()
    if node.state == goal: return path
    for mỗi neighbor của node:
      if neighbor.state not in Reached hoặc neighbor.g < Reached[neighbor.state]:
        Reached[neighbor.state] = neighbor.g
        Frontier.enqueue(neighbor)
  return failure""",
    "pseudocode_en": """BFS(start, goal):
  Frontier ← Queue containing start
  Reached ← {start: 0}
  while Frontier is not empty:
    node ← Frontier.dequeue()
    if node.state == goal: return path
    for each neighbor of node:
      if neighbor.state not in Reached or neighbor.g < Reached[neighbor.state]:
        Reached[neighbor.state] = neighbor.g
        Frontier.enqueue(neighbor)
  return failure""",
    "application": "Duyệt theo chiều rộng, đảm bảo tìm thấy lời giải ngắn nhất nếu cost mỗi bước bằng nhau. Tuy nhiên frontier tăng theo cấp số nhân — cần rất nhiều bộ nhớ cho 15-puzzle sâu.",
    "application_en": "Explores width-first, guaranteeing the shortest solution when step costs are uniform. However, frontier size grows exponentially — requires significant memory for deep 15-puzzles.",
    "suitable": "Phù hợp về mặt lý thuyết (optimal, complete) nhưng THỰC TẾ rất tốn bộ nhớ. Chỉ nên dùng scramble depth ≤ 10.",
    "suitable_en": "Theoretically optimal and complete, but in practice extremely memory-intensive. Recommended for scramble depths <= 10.",
    "pros": ["Complete (với không gian hữu hạn)", "Optimal (với unit cost)", "Đơn giản cài đặt"],
    "pros_en": ["Complete (for finite state spaces)", "Optimal (for unit cost)", "Simple to implement"],
    "cons": ["Bộ nhớ O(b^d) — cực lớn", "Frontier có thể hàng triệu node cho 15-puzzle", "Chậm với puzzle sâu"],
    "cons_en": ["O(b^d) memory complexity — extremely high", "Frontier can reach millions of nodes for deeper puzzles", "Slow for deep puzzles"],
    "complexity": "Thời gian: O(b^d), Bộ nhớ: O(b^d), b=branching factor, d=depth",
    "complexity_en": "Time: O(b^d), Space: O(b^d), where b is branching factor and d is depth",
    "bad_example": "Scramble depth 20: BFS cần mở rộng ~3^20 ≈ 3.5 tỷ node. Không thể chạy trong thực tế.",
    "bad_example_en": "Scramble depth 20: BFS needs to expand ~3^20 ≈ 3.5 billion nodes. Impossible to run in practice.",
    "comparison": "BFS tối ưu hơn DFS nhưng tốn bộ nhớ hơn. IDS có tính chất tối ưu của BFS nhưng tiết kiệm bộ nhớ.",
    "comparison_en": "More optimal than DFS but uses much more memory. IDS achieves BFS optimality while using DFS memory efficiency.",
    "exam_tips": "BFS ⇒ optimal cho unit cost. BFS ⇒ complete. BFS tốn bộ nhớ nhất trong 3 thuật toán cơ bản (BFS, DFS, UCS).",
    "exam_tips_en": "BFS is optimal for unit cost. BFS is complete. BFS is the most memory-intensive among basic algorithms.",
}

THEORY["DFS"] = {
    "name": "DFS — Depth-First Search",
    "group": "Uninformed Search",
    "goal": "Duyệt sâu nhất có thể trước khi quay lui. Không đảm bảo tối ưu.",
    "goal_en": "Explore as deep as possible before backtracking. Does not guarantee optimality.",
    "idea": "Dùng Stack LIFO. Đi xuống sâu nhất nhánh trước, quay lui khi không còn lựa chọn. Cần depth limit để tránh vô hạn.",
    "idea_en": "Uses a LIFO stack. Descends to the deepest branch first, backtracking when no options remain. Needs depth limit to avoid infinite paths.",
    "data_structure": "Stack (LIFO) cho Frontier, Set cho visited.",
    "data_structure_en": "Stack (LIFO) for Frontier, Set for visited.",
    "formula": "Không có hàm đánh giá. Chỉ ưu tiên node sâu nhất.",
    "formula_en": "No evaluation function. Prioritizes the deepest node.",
    "pseudocode": """DFS(start, goal, max_depth):
  Stack ← [start]
  Visited ← set()
  while Stack không rỗng:
    node ← Stack.pop()
    if node.depth > max_depth: continue
    if node.state == goal: return path
    if node.state in Visited: continue
    Visited.add(node.state)
    for neighbor của node (reverse order):
      Stack.push(neighbor)""",
    "pseudocode_en": """DFS(start, goal, max_depth):
  Stack ← [start]
  Visited ← set()
  while Stack is not empty:
    node ← Stack.pop()
    if node.depth > max_depth: continue
    if node.state == goal: return path
    if node.state in Visited: continue
    Visited.add(node.state)
    for neighbor of node (reverse order):
      Stack.push(neighbor)""",
    "application": "DFS ít tốn bộ nhớ (chỉ lưu đường đi hiện tại) nhưng có thể đi rất sâu và tìm đường rất dài. Cho 15-puzzle, DFS có thể tạo đường đi hàng ngàn bước.",
    "application_en": "DFS consumes very little memory (only stores the current path) but can go extremely deep, returning long paths. For the 15-puzzle, DFS can generate paths of thousands of steps.",
    "suitable": "KHÔNG phù hợp cho 15-puzzle vì không đảm bảo tối ưu và đường đi có thể rất dài. Chỉ dùng để minh họa.",
    "suitable_en": "NOT suitable for 15-puzzle because it does not guarantee optimality and solutions are too long. Only for educational demonstration.",
    "pros": ["Tiết kiệm bộ nhớ O(b*d)", "Đơn giản", "Tìm nhanh một lời giải (không nhất thiết tối ưu)"],
    "pros_en": ["Low memory consumption O(bd)", "Simple", "Finds a solution quickly (not necessarily optimal)"],
    "cons": ["Không tối ưu", "Không complete (với depth limit)", "Đường đi có thể rất dài"],
    "cons_en": ["Not optimal", "Not complete (with depth limit)", "Paths can be extremely long"],
    "complexity": "Thời gian: O(b^m) với m=max depth, Bộ nhớ: O(b*d) với d là độ sâu lời giải",
    "complexity_en": "Time: O(b^m) where m is max depth, Space: O(bd) where d is depth of current path",
    "bad_example": "DFS có thể đi đường dài 100+ bước cho puzzle chỉ cần 10 bước tối ưu.",
    "bad_example_en": "DFS can generate a path of 100+ steps for a puzzle solvable in just 10 optimal steps.",
    "comparison": "DFS tiết kiệm bộ nhớ hơn BFS rất nhiều nhưng đường đi tệ hơn. IDS kết hợp ưu điểm cả hai.",
    "comparison_en": "Consumes far less memory than BFS but solutions are much worse. IDS combines the best of both.",
    "exam_tips": "DFS ⇒ KHÔNG optimal, KHÔNG complete (với depth limit). DFS ⇒ tiết kiệm bộ nhớ. DFS ⇒ có thể bị kẹt nhánh sai.",
    "exam_tips_en": "DFS is NOT optimal, NOT complete (with depth limit). DFS is memory efficient. DFS can get stuck in infinite loops/wrong branches.",
}

THEORY["UCS"] = {
    "name": "UCS — Uniform Cost Search",
    "group": "Uninformed Search",
    "goal": "Tìm đường đi chi phí thấp nhất, cho phép cost mỗi bước khác nhau.",
    "goal_en": "Find the lowest-cost path, allowing variable step costs.",
    "idea": "Giống BFS nhưng dùng Priority Queue theo g(n). Khi cost mỗi bước = 1, UCS tương đương BFS.",
    "idea_en": "Similar to BFS but uses a Priority Queue sorted by path cost g(n). Equivalent to BFS when step costs are uniform (= 1).",
    "data_structure": "Priority Queue (min-heap) theo g(n), Dict cho best_g.",
    "data_structure_en": "Priority Queue (min-heap) sorted by g(n), Dict for best_g.",
    "formula": "Ưu tiên node có g(n) nhỏ nhất. g(n) = tổng cost từ start đến n.",
    "formula_en": "Prioritizes node with the lowest g(n) (total path cost from start to n).",
    "pseudocode": """UCS(start, goal):
  Frontier ← PriorityQueue [(0, start)]
  best_g ← {start: 0}
  while Frontier không rỗng:
    node ← Frontier.dequeue_min()
    if node.state == goal: return path
    if node.g > best_g[node.state]: continue
    for neighbor của node:
      new_g = node.g + cost(node, neighbor)
      if new_g < best_g.get(neighbor.state, ∞):
        best_g[neighbor.state] = new_g
        Frontier.insert((new_g, neighbor))""",
    "pseudocode_en": """UCS(start, goal):
  Frontier ← PriorityQueue [(0, start)]
  best_g ← {start: 0}
  while Frontier is not empty:
    node ← Frontier.dequeue_min()
    if node.state == goal: return path
    if node.g > best_g[node.state]: continue
    for neighbor of node:
      new_g = node.g + cost(node, neighbor)
      if new_g < best_g.get(neighbor.state, ∞):
        best_g[neighbor.state] = new_g
        Frontier.insert((new_g, neighbor))""",
    "application": "Khi cost mỗi bước = 1 (như 15-puzzle), UCS giống hệt BFS. Chỉ có lợi khi cost khác nhau.",
    "application_en": "When step costs are uniform (like 15-puzzle), UCS behaves identically to BFS. Only advantageous when step costs vary.",
    "suitable": "Về lý thuyết optimal và complete, nhưng thực tế giống BFS — tốn bộ nhớ. Không có lợi cho 15-puzzle vì cost đồng nhất.",
    "suitable_en": "Optimal and complete, but in practice identical to BFS — memory-intensive. No added benefit for 15-puzzle.",
    "pros": ["Optimal (luôn tìm đường chi phí thấp nhất)", "Complete", "Total order trên g(n)"],
    "pros_en": ["Optimal (always finds the lowest-cost path)", "Complete", "Total order on g(n)"],
    "cons": ["Tốn bộ nhớ như BFS", "Với unit cost, tương đương BFS — không thêm lợi ích", "Priority queue overhead"],
    "cons_en": ["Memory-intensive like BFS", "Equivalent to BFS under unit costs", "Priority queue overhead"],
    "complexity": "Thời gian: O(b^(C*/ε)), Bộ nhớ: O(b^(C*/ε)), C*=optimal cost, ε=min step cost",
    "complexity_en": "Time: O(b^(C*/ε)), Space: O(b^(C*/ε)) where C* is optimal cost and ε is minimum step cost",
    "bad_example": "UCS cho 15-puzzle cho kết quả giống BFS nhưng chậm hơn do priority queue overhead.",
    "bad_example_en": "UCS on 15-puzzle yields identical results to BFS but runs slower due to priority queue overhead.",
    "comparison": "UCS = BFS khi cost đều. UCS > BFS khi cost khác nhau. UCS < A* khi có heuristic tốt.",
    "comparison_en": "UCS is BFS under unit costs. UCS is better than BFS with variable costs. UCS is worse than A* when heuristic is available.",
    "exam_tips": "UCS ⇒ optimal và complete. UCS với unit cost = BFS. UCS mở rộng theo g(n) tăng dần.",
    "exam_tips_en": "UCS is optimal and complete. UCS with unit cost = BFS. UCS expands nodes in increasing order of g(n).",
}

THEORY["IDS"] = {
    "name": "IDS — Iterative Deepening Search",
    "group": "Uninformed Search",
    "goal": "Kết hợp ưu điểm BFS (optimal) và DFS (tiết kiệm bộ nhớ).",
    "goal_en": "Combine BFS optimality and DFS space efficiency.",
    "idea": "Chạy DFS với depth limit tăng dần: 0, 1, 2, 3, ... Mỗi vòng lặp lại duyệt từ đầu nhưng chỉ sâu đến limit hiện tại.",
    "idea_en": "Runs DFS with an increasing depth limit: 0, 1, 2, ... Each iteration searches from scratch up to the current depth limit.",
    "data_structure": "Stack cho DFS, lặp từ depth 0 đến depth tối đa.",
    "data_structure_en": "Stack for DFS, loop from depth 0 to max depth.",
    "formula": "IDS(0) → DFS(depth=0) → IDS(1) → DFS(depth=1) → IDS(2) → DFS(depth=2) → ...",
    "formula_en": "IDS(0) → DFS(depth=0) → IDS(1) → DFS(depth=1) → ...",
    "pseudocode": """IDS(start, goal):
  for depth = 0, 1, 2, ...:
    result = DFS_with_limit(start, goal, depth)
    if result == FOUND: return path
    if result == CUTOFF: continue
  return failure""",
    "pseudocode_en": """IDS(start, goal):
  for depth = 0, 1, 2, ...:
    result = DFS_with_limit(start, goal, depth)
    if result == FOUND: return path
    if result == CUTOFF: continue
  return failure""",
    "application": "Tối ưu như BFS (unit cost) nhưng chỉ tốn bộ nhớ O(b*d). Expand lại node nhiều lần nhưng overhead nhỏ vì số node ở level sâu nhất chiếm đa số.",
    "application_en": "Optimal like BFS (for unit step costs) but only uses O(bd) space. Re-expands nodes but overhead is low because the deepest level contains the majority of nodes.",
    "suitable": "Rất phù hợp cho 15-puzzle vì tiết kiệm bộ nhớ và vẫn optimal. Preferrred hơn BFS cho bài toán lớn.",
    "suitable_en": "Highly suitable for 15-puzzle as it saves memory while ensuring optimality. Preferred over BFS for larger problems.",
    "pros": ["Optimal (unit cost)", "Complete", "Tiết kiệm bộ nhớ O(b*d)", "Kết hợp ưu BFS + DFS"],
    "pros_en": ["Optimal (unit cost)", "Complete", "Memory-efficient O(bd)", "Combines BFS + DFS benefits"],
    "cons": ["Expand lại node nhiều lần (nhưng overhead nhỏ)", "Chậm hơn BFS chút ít do lặp lại"],
    "complexity": "Thời gian: O(b^d) (như BFS), Bộ nhớ: O(b*d) (như DFS)",
    "complexity_en": "Time: O(b^d), Space: O(bd)",
    "bad_example": "IDS lặp lại DFS nhiều lần. Với b=3, d=10: tổng node ≈ b^d/(b-1) gần như BFS. Overhead nhỏ.",
    "bad_example_en": "IDS re-expands nodes. For b=3, d=10: total nodes expanded is ~b^d/(b-1), which is very close to BFS. Overhead is negligible.",
    "comparison": "IDS có tính chất optimal + complete của BFS nhưng bộ nhớ của DFS. Là lựa chọn tốt nhất trong uninformed search cho 15-puzzle.",
    "comparison_en": "IDS has BFS properties (optimal, complete) but DFS memory usage. The best uninformed search for 15-puzzle.",
    "exam_tips": "IDS ⇒ optimal (unit cost), complete, tiết kiệm bộ nhớ. IDS expand lại node nhưng overhead nhỏ. IDS là uninformed search tốt nhất cho bài toán không biết trước depth.",
    "exam_tips_en": "IDS is optimal (unit cost), complete, and memory-efficient. IDS re-expands nodes but has low overhead. IDS is best for uninformed search when target depth is unknown.",
}

THEORY["Greedy"] = {
    "name": "Greedy Best-First Search",
    "group": "Informed Search",
    "goal": "Tìm lời giải nhanh bằng cách ưu tiên node có heuristic nhỏ nhất.",
    "goal_en": "Find a solution quickly by prioritizing the node with the lowest heuristic value.",
    "idea": "Chỉ dùng h(n) để đánh giá, không xét g(n). Chạy nhanh nhưng không đảm bảo tối ưu.",
    "idea_en": "Uses only h(n) for node evaluation, ignoring g(n). Runs fast but does not guarantee optimality.",
    "data_structure": "Priority Queue theo h(n), Dict cho reached.",
    "data_structure_en": "Priority Queue sorted by h(n), Dict for reached.",
    "formula": "Ưu tiên: h(n) nhỏ nhất. h(n) = ước tính chi phí từ n đến goal.",
    "formula_en": "Prioritizes lowest h(n). h(n) = estimated cost from n to goal.",
    "pseudocode": """Greedy(start, goal, h):
  Frontier ← PriorityQueue [(h(start), start)]
  Reached ← {start}
  while Frontier:
    node ← Frontier.dequeue_min_h()
    if node.state == goal: return path
    for mỗi neighbor của node:
      if neighbor.state not in Reached:
        Reached.add(neighbor.state)
        Frontier.insert((h(neighbor.state), neighbor))""",
    "pseudocode_en": """Greedy(start, goal, h):
  Frontier ← PriorityQueue [(h(start), start)]
  Reached ← {start}
  while Frontier is not empty:
    node ← Frontier.dequeue_min_h()
    if node.state == goal: return path
    for each neighbor of node:
      if neighbor.state not in Reached:
        Reached.add(neighbor.state)
        Frontier.insert((h(neighbor.state), neighbor))""",
    "application": "Chạy nhanh cho 15-puzzle vì h(n) dẫn đường, nhưng có thể bị lừa bởi heuristic — chọn đường gần goal hơn nhưng thực ra đường dài hơn.",
    "application_en": "Runs fast for the 15-puzzle because h(n) guides the search, but can be misled by the heuristic — choosing a node closer to the goal that actually lies on a longer path.",
    "suitable": "Nhanh nhưng KHÔNG optimal. Dùng khi cần lời giải nhanh, chấp nhận không tối ưu.",
    "suitable_en": "Fast but NOT optimal. Use when a quick solution is needed and suboptimality is acceptable.",
    "pros": ["Nhanh — ít mở rộng node", "Đơn giản cài đặt", "Dùng heuristic dẫn đường"],
    "pros_en": ["Fast — expands fewer nodes", "Simple to implement", "Guided by heuristic knowledge"],
    "cons": ["KHÔNG optimal", "Có thể bị kẹt local minimum", "Đường đi thường dài hơn A*"],
    "cons_en": ["NOT optimal", "Prone to getting stuck in local minima", "Paths are usually longer than A*"],
    "complexity": "Thời gian: O(b^m) worst case, thường nhanh hơn. Bộ nhớ: O(b^m).",
    "complexity_en": "Time: O(b^m) worst case, Space: O(b^m)",
    "bad_example": "Greedy có thể đi đường gấp khúc quanh local minimum, trong khi A* đi thẳng.",
    "bad_example_en": "Greedy can wander around local minima, whereas A* takes the direct path.",
    "comparison": "Greedy nhanh hơn A* nhưng đường đi tệ hơn. A* = Greedy + g(n) cân bằng.",
    "comparison_en": "Greedy is faster than A* but path quality is worse. A* balances Greedy and UCS.",
    "exam_tips": "Greedy ⇒ KHÔNG optimal, KHÔNG complete. Greedy chỉ dùng h(n). Greedy nhanh nhưng đường đi tệ.",
    "exam_tips_en": "Greedy is NOT optimal, NOT complete. Greedy only uses h(n). Greedy is fast but yields poor paths.",
}

THEORY["A*"] = {
    "name": "A* Search",
    "group": "Informed Search",
    "goal": "Tìm đường đi tối ưu bằng cách cân bằng g(n) và h(n).",
    "goal_en": "Find the optimal path by balancing path cost g(n) and heuristic cost h(n).",
    "idea": "f(n) = g(n) + h(n). Nếu h admissible (không overestimate) và consistent, A* đảm bảo tối ưu.",
    "idea_en": "f(n) = g(n) + h(n). If h is admissible (never overestimates) and consistent, A* guarantees optimality.",
    "data_structure": "Priority Queue theo f(n)=g(n)+h(n), Dict cho best_g.",
    "data_structure_en": "Priority Queue sorted by f(n)=g(n)+h(n), Dict for best_g.",
    "formula": "f(n) = g(n) + h(n). g(n) = cost từ start đến n. h(n) = ước lượng chi phí từ n đến goal.",
    "formula_en": "f(n) = g(n) + h(n). g(n) = path cost from start to n. h(n) = estimated cost from n to goal.",
    "pseudocode": """A*(start, goal, h):
  Frontier ← PriorityQueue [(f(start), start)]
  best_g ← {start: 0}
  while Frontier:
    node ← Frontier.dequeue_min_f()
    if node.state == goal: return path
    if node.g > best_g[node.state]: continue  # skip outdated
    for neighbor của node:
      new_g = node.g + cost(node, neighbor)
      if new_g < best_g.get(neighbor.state, ∞):
        best_g[neighbor.state] = new_g
        f = new_g + h(neighbor.state)
        Frontier.insert((f, neighbor))""",
    "pseudocode_en": """A*(start, goal, h):
  Frontier ← PriorityQueue [(f(start), start)]
  best_g ← {start: 0}
  while Frontier is not empty:
    node ← Frontier.dequeue_min_f()
    if node.state == goal: return path
    if node.g > best_g[node.state]: continue  # skip outdated
    for each neighbor of node:
      new_g = node.g + cost(node, neighbor)
      if new_g < best_g.get(neighbor.state, ∞):
        best_g[neighbor.state] = new_g
        f = new_g + h(neighbor.state)
        Frontier.insert((f, neighbor))""",
    "application": "Thuật toán tốt nhất cho 15-puzzle khi dùng Manhattan hoặc Linear Conflict heuristic. Cân bằng giữa tốc độ và tối ưu.",
    "application_en": "The best algorithm for 15-puzzle when using Manhattan or Linear Conflict heuristics. Perfectly balances speed and path quality.",
    "suitable": "RẤT phù hợp cho 15-puzzle. Là thuật toán chuẩn để giải 15-puzzle. Với heuristic mạnh (Manhattan, Linear Conflict), A* giải được puzzle sâu 50+ bước.",
    "suitable_en": "HIGHLY suitable for 15-puzzle. The gold standard solver. With strong heuristics (Manhattan, Linear Conflict), A* can solve puzzles 50+ steps deep.",
    "pros": ["Optimal (với heuristic admissible + consistent)", "Complete", "Hiệu quả hơn BFS/UCS khi có heuristic tốt", "Lựa chọn tốt nhất cho 15-puzzle"],
    "pros_en": ["Optimal (with admissible + consistent heuristics)", "Complete", "More efficient than BFS/UCS with a good heuristic", "Best choice for 15-puzzle"],
    "cons": ["Tốn bộ nhớ O(b^d)", "Chậm hơn Greedy vì mở rộng nhiều node hơn", "Heuristic yếu → gần BFS"],
    "cons_en": ["O(b^d) memory complexity", "Slower than Greedy because it expands more nodes", "Behaves like BFS if heuristic is weak"],
    "complexity": "Thời gian: O(b^d) worst, nhưng thường O(b^(εd)) với ε phụ thuộc heuristic. Bộ nhớ: O(b^d).",
    "complexity_en": "Time: O(b^d) worst-case, but often O(b^(εd)) where ε depends on heuristic strength. Space: O(b^d).",
    "bad_example": "Với h=0 (không heuristic), A* = UCS = BFS. Heuristic yếu cho kết quả chậm.",
    "bad_example_en": "With h=0 (no heuristic), A* = UCS = BFS. Weak heuristics lead to slow execution.",
    "comparison": "A* = Greedy + UCS. A* tối ưu, Greedy thì không. A* dùng f=g+h, Greedy chỉ dùng h.",
    "comparison_en": "A* = Greedy + UCS. A* is optimal, Greedy is not. A* uses f=g+h, Greedy only uses h.",
    "exam_tips": "A* ⇒ optimal NẾU h admissible + consistent. A* ⇒ complete. A* mở rộng node theo f tăng dần. Manhattan là consistent heuristic cho 15-puzzle.",
    "exam_tips_en": "A* is optimal IF h is admissible + consistent. A* is complete. A* expands nodes in increasing order of f. Manhattan is a consistent heuristic for the 15-puzzle.",
}

THEORY["IDA*"] = {
    "name": "IDA* — Iterative Deepening A*",
    "group": "Informed Search",
    "goal": "A* tiết kiệm bộ nhớ bằng iterative deepening trên f-cost.",
    "goal_en": "Memory-efficient A* search using iterative deepening on f-cost thresholds.",
    "idea": "Chạy DFS với f-limit. Mỗi vòng tăng threshold lên min f-cost vượt threshold trước. Kết hợp A* và IDS.",
    "idea_en": "Runs DFS with an f-limit. Each iteration increases the threshold to the minimum f-cost exceeding the previous threshold. Combines A* and IDS.",
    "data_structure": "Stack cho DFS, không cần Priority Queue. Chỉ cần lưu đường đi hiện tại.",
    "data_structure_en": "Stack for DFS, no Priority Queue. Only stores the current search path.",
    "formula": "Threshold ban đầu = h(start). DFS chỉ mở rộng node có f(n) ≤ threshold. Next threshold = min f(n) > current threshold.",
    "formula_en": "Initial threshold = h(start). DFS only expands nodes with f(n) <= threshold. Next threshold = min f(n) > current threshold.",
    "pseudocode": """IDA*(start, goal, h):
  threshold = h(start)
  while True:
    result, next_t = DFS_f_limit(start, goal, threshold, h)
    if result == FOUND: return path
    if next_t == ∞: return failure
    threshold = next_t""",
    "pseudocode_en": """IDA*(start, goal, h):
  threshold = h(start)
  while True:
    result, next_t = DFS_f_limit(start, goal, threshold, h)
    if result == FOUND: return path
    if next_t == ∞: return failure
    threshold = next_t""",
    "application": "Tiết kiệm bộ nhớ hơn A* đáng kể (chỉ O(b*d)). Phù hợp cho 15-puzzle khi A* hết bộ nhớ. Expand lại node nhưng overhead chấp nhận được.",
    "application_en": "Saves significant memory compared to A* (only O(bd) space). Ideal for 15-puzzle when A* runs out of memory. Re-expands nodes but overhead is acceptable.",
    "suitable": "Rất phù hợp cho 15-puzzle, đặc biệt puzzle sâu. Là lựa chọn khi A* hết RAM.",
    "suitable_en": "Highly suitable for 15-puzzle, especially deep scrambles. The go-to choice when A* runs out of RAM.",
    "pros": ["Optimal (với heuristic admissible)", "Tiết kiệm bộ nhớ O(b*d)", "Complete"],
    "pros_en": ["Optimal (with admissible heuristics)", "Memory efficient O(bd)", "Complete"],
    "cons": ["Expand lại node nhiều lần hơn A*", "Chậm hơn A* khi bộ nhớ đủ", "Threshold tăng nhỏ giọt nếu heuristic không sát"],
    "cons_en": ["Re-expands nodes more times than A*", "Slower than A* when RAM is sufficient", "Threshold increases very slowly if heuristic is not tight"],
    "complexity": "Thời gian: O(b^d), Bộ nhớ: O(b*d) — tiết kiệm hơn A* rất nhiều.",
    "complexity_en": "Time: O(b^d), Space: O(bd) — massive memory savings over A*.",
    "bad_example": "IDA* với h=0 → tương đương IDS. Iteration tăng 1 mỗi vòng, rất chậm.",
    "bad_example_en": "IDA* with h=0 behaves like IDS. The threshold increases by only 1 each iteration, which is extremely slow.",
    "comparison": "IDA* có tính chất A* nhưng bộ nhớ IDS. IDA* lặp lại nhiều vòng nhưng mỗi vòng nhanh vì DFS.",
    "comparison_en": "IDA* shares A* properties but uses IDS memory structure. IDA* runs multiple iterations, but each is fast because of DFS.",
    "exam_tips": "IDA* ⇒ optimal (h admissible), O(b*d) memory. IDA* dùng threshold thay vì priority queue. IDA* là A* + IDS.",
    "exam_tips_en": "IDA* is optimal (h admissible). IDA* uses O(bd) memory. IDA* uses thresholds instead of priority queues. IDA* is A* + IDS.",
}

# ============================================================
# GROUP 3: LOCAL SEARCH
# ============================================================

for algo_name, algo_data in [
    ("Simple HC", {
        "name": "Simple Hill Climbing",
        "group": "Local Search",
        "goal": "Tìm trạng thái tốt hơn hiện tại bằng cách chọn neighbor đầu tiên có h thấp hơn.",
        "idea": "Xét neighbor theo thứ tự. Chọn neighbor đầu tiên có h < h(current). Dừng khi không có neighbor tốt hơn.",
        "data_structure": "Chỉ lưu current state. Không cần Frontier hay Reached.",
        "formula": "Chọn neighbor đầu tiên: h(neighbor) < h(current). Không có → local optimum.",
        "application": "Nhanh nhưng dễ kẹt local optimum. Cho 15-puzzle, thường kẹt ở h=2 hoặc h=4.",
        "suitable": "KHÔNG phù hợp cho 15-puzzle. Dễ kẹt local optimum vì heuristic landscape có nhiều plateaus.",
    }),
    ("Steepest Ascent HC", {
        "name": "Steepest-Ascent Hill Climbing",
        "group": "Local Search",
        "goal": "Chọn neighbor tốt nhất (h nhỏ nhất) trong tất cả neighbor.",
        "idea": "So sánh TẤT CẢ neighbor, chọn neighbor có h nhỏ nhất. Dừng khi không có neighbor tốt hơn current.",
        "data_structure": "Chỉ lưu current state + tạm thời tất cả neighbor.",
        "formula": "next = argmin h(neighbor) cho mọi neighbor. Nếu h(next) >= h(current) → dừng.",
        "application": "Tốt hơn Simple HC vì chọn hướng tốt nhất. Vẫn kẹt local optimum.",
        "suitable": "KHÔNG phù hợp cho 15-puzzle. Tốt hơn Simple HC nhưng vẫn kẹt.",
    }),
    ("Stochastic HC", {
        "name": "Stochastic Hill Climbing",
        "group": "Local Search",
        "goal": "Chọn ngẫu nhiên trong các neighbor tốt hơn. Thêm randomness để tránh kẹt.",
        "idea": "Tập hợp các neighbor có h < h(current). Chọn ngẫu nhiên 1 trong số đó.",
        "data_structure": "Current state + random generator.",
        "formula": "Better = {n ∈ neighbors | h(n) < h(current)}. Chọn ngẫu nhiên từ Better.",
        "application": "Thêm yếu tố ngẫu nhiên giúp khám phá nhiều đường khác nhau. Vẫn kẹt local optimum nhưng có thể tìm đường khác khi restart.",
        "suitable": "Không phù hợp cho 15-puzzle vì vẫn kẹt. Nhưng tốt hơn deterministic HC.",
    }),
    ("Random-Restart HC", {
        "name": "Random-Restart Hill Climbing",
        "group": "Local Search",
        "goal": "Chạy Hill Climbing nhiều lần từ nhiều điểm bắt đầu khác nhau.",
        "idea": "Nếu kẹt local optimum → restart từ điểm ngẫu nhiên mới. Với xác suất cao, sẽ tìm được global optimum sau nhiều restart.",
        "data_structure": "Current state + best-so-far + random restart points.",
        "formula": "Lặp: HC(start_i) → kẹt → start_{i+1} = random solvable state. Giữ best path.",
        "application": "Cải thiện đáng kể Hill Climbing. Với 15-puzzle, cần nhiều restart nhưng có thể tìm lời giải.",
        "suitable": "Có thể tìm lời giải cho 15-puzzle nếu đủ restart. Không đảm bảo tối ưu.",
    }),
    ("Local Beam Search", {
        "name": "Local Beam Search",
        "group": "Local Search",
        "goal": "Giữ k trạng thái tốt nhất, mở rộng tất cả neighbor, chọn k tốt nhất.",
        "idea": "Thay vì 1 state, duy trì k state (beam). Mỗi bước sinh tất cả neighbor, chọn k tốt nhất theo h.",
        "data_structure": "Danh sách k state, sắp xếp theo h.",
        "formula": "Beam = top k states by h. Mỗi bước: expand all → get all neighbors → select top k.",
        "application": "Tốt hơn Hill Climbing vì giữ nhiều candidate. Mutually reinforcing — một beam member có thể giúp member khác.",
        "suitable": "Tốt hơn HC đơn lẻ nhưng vẫn kẹt. Beam width lớn hơn → nhiều khả năng tìm lời giải.",
    }),
    ("Simulated Annealing", {
        "name": "Simulated Annealing",
        "group": "Local Search",
        "goal": "Cho phép nhận bước đi xấu với xác suất giảm dần theo 'nhiệt độ'.",
        "idea": "Khởi tạo nhiệt độ T cao. Bước xấu được nhận với xác suất exp(-δ/T). T giảm dần → ít nhận bước xấu hơn.",
        "data_structure": "Current state, best-so-far, temperature schedule.",
        "formula": "δ = h(new) - h(current). Nếu δ < 0 → accept. Nếu δ ≥ 0 → accept với P = exp(-δ/T). T(t) = T₀ × α^t.",
        "application": "Có thể thoát local optimum nhờ xác suất nhận bước xấu. Nhiệt độ cao đầu → khám phá rộng. Nhiệt độ thấp cuối → exploit.",
        "suitable": "Có thể tìm lời giải cho 15-puzzle nhưng không đảm bảo. Cần tuning cooling schedule.",
    }),
]:
    THEORY[algo_name] = algo_data

# Fill in common fields for local search algorithms
for key in THEORY:
    d = THEORY[key]
    if d.get("group") == "Local Search" and "pros" not in d:
        d["pros"] = ["Nhanh", "Tiết kiệm bộ nhớ", "Không cần lưu đường đi"]
        d["cons"] = ["Không đảm bảo tối ưu", "Không đảm bảo complete", "Dễ kẹt local optimum"]
        d["complexity"] = "Thời gian: O(max_iterations), Bộ nhớ: O(1) hoặc O(k) cho beam"
        d["comparison"] = "Local Search nhanh nhưng không đảm bảo tìm lời giải. Hill Climbing dễ kẹt. SA và Random-Restart giảm kẹt."
        d["exam_tips"] = "Local Search ⇒ KHÔNG complete, KHÔNG optimal. SA ⇒ có thể thoát local optimum. Beam ⇒ giữ nhiều candidate."
        d["pseudocode"] = d.get("pseudocode", "See algorithm description above.")
        d["bad_example"] = d.get("bad_example", "Hill Climbing kẹt ở h=2, không thể xuống h=0 dù chỉ cần 2 bước.")

# ============================================================
# GROUP 4: COMPLEX ENVIRONMENTS
# ============================================================

THEORY["AND-OR"] = {
    "name": "AND-OR Search",
    "group": "Complex Environments",
    "goal": "Tìm conditional plan cho môi trường nondeterministic.",
    "idea": "OR node: agent chọn action. AND node: tất cả outcome có thể xảy ra. Plan = IF-THEN structure.",
    "data_structure": "AND-OR tree. OR node: 1 action được chọn. AND node: tất cả outcome phải xử lý.",
    "formula": "OR node: chọn action tốt nhất. AND node: phải có plan cho MỖI outcome.",
    "pseudocode": """AND-OR-Search(state):
  if state == goal: return empty plan
  for action in actions(state):
    outcomes = get_possible_outcomes(state, action)
    plans = [AND-OR-Search(outcome) for outcome in outcomes]
    if all plans found: return (action, {outcome: plan for outcome, plan in zip(outcomes, plans)})""",
    "application": "15-puzzle chuẩn là deterministic. AND-OR chỉ cần khi action có thể bị lệch. Ví dụ: chọn U nhưng môi trường có thể thực hiện L thay.",
    "suitable": "KHÔNG phải thuật toán chuẩn cho 15-puzzle. Đây là mở rộng minh họa cho môi trường nondeterministic.",
    "pros": ["Hoạt động trong môi trường không xác định", "Tìm conditional plan"],
    "cons": ["Phức tạp hơn search thường", "Kích thước AND-OR tree lớn", "Không cần cho 15-puzzle chuẩn"],
    "complexity": "Thời gian và bộ nhớ: phụ thuộc vào kích thước AND-OR tree, có thể rất lớn.",
    "bad_example": "Với nhiều outcome có thể, AND-OR tree bùng nổ tổ hợp.",
    "comparison": "AND-OR → môi trường nondeterministic. A* → môi trường deterministic. 15-puzzle chuẩn → dùng A*.",
    "exam_tips": "AND-OR dùng khi action có nhiều outcome có thể. OR node = agent chọn. AND node = môi trường quyết định.",
}

THEORY["No Observation"] = {
    "name": "Searching with No Observation",
    "group": "Complex Environments",
    "goal": "Tìm hành động khi agent không quan sát được trạng thái (belief state search).",
    "idea": "Agent duy trì belief state = tập các trạng thái có thể. Mỗi bước, cập nhật belief dựa trên action.",
    "data_structure": "Belief state = set of states. Mỗi action → cập nhật toàn bộ belief.",
    "formula": "b' = {result(s, a) | s ∈ b, result hợp lệ} ∪ {s | result(s, a) không hợp lệ, s ∈ b}",
    "pseudocode": """No-Obs-Search(belief_0, goal):
  b = belief_0
  while not all(s == goal for s in b):
    for action in actions:
      b_new = update_belief(b, action)
      if size(b_new) < size(b) or progress(b_new):
        choose action, b = b_new""",
    "application": "15-puzzle chuẩn là fully observable — agent biết chính xác state. No observation dùng khi agent bịt mắt.",
    "suitable": "KHÔNG phù hợp cho 15-puzzle chuẩn. Minh họa khái niệm belief state.",
    "pros": ["Hoạt động khi không có quan sát", "Chính quy về mặt lý thuyết"],
    "cons": ["Belief state có thể rất lớn", "Tính toán cập nhật belief tốn thời gian", "Không thực tế cho bài toán lớn"],
    "complexity": "Belief state kích thước ≤ |S|. Cập nhật: O(|b| × |A|).",
    "bad_example": "Với 16! trạng thái 15-puzzle, belief state ban đầu có thể rất lớn.",
    "comparison": "No observation → belief state = nhiều trạng thái. Partial observable → thu hẹp belief bằng quan sát. Fully observable → belief state = 1 trạng thái.",
    "exam_tips": "Belief state = tập trạng thái có thể. No observation ⇒ khó nhất. Partial observation ⇒ vừa phải. Fully observable ⇒ dễ nhất.",
}

THEORY["Partially Observable"] = {
    "name": "Partially Observable Search",
    "group": "Complex Environments",
    "goal": "Tìm hành động khi agent chỉ quan sát được phần trạng thái.",
    "idea": "Agent quan sát được một phần (ví dụ: vị trí ô trống + tiles kề). Dùng quan sát thu hẹp belief state.",
    "data_structure": "Belief state + observation model + update function.",
    "formula": "b' = {s ∈ update(b, a) | observation(s) == obs}. Lọc belief bằng observation.",
    "pseudocode": "See algorithm description in complex_env.py",
    "application": "Giữa no observation và fully observable. Quan sát giúp thu hẹp belief state nhanh hơn.",
    "suitable": "Không phải thuật toán chuẩn cho 15-puzzle. Minh họa khái niệm partial observability.",
    "pros": ["Thu hẹp belief nhanh hơn no observation", "Thực tế hơn no observation"],
    "cons": ["Vẫn phức tạp hơn fully observable", "Observation model cần thiết kế"],
    "complexity": "Belief size giảm sau mỗi observation. Tốt nhất: 1 state (fully observable). Tệ nhất: kích thước ban đầu (no observation).",
    "bad_example": "Observation không rõ ràng → belief không thu hẹp đủ nhanh.",
    "comparison": "No obs < Partial < Full về khả năng tìm lời giải. Partial obs lọc belief bằng quan sát.",
    "exam_tips": "Partial observable ⇒ observation thu hẹp belief state. Fitness function cho belief: số states trong belief.",
}

THEORY["LRTA*"] = {
    "name": "Online Search — LRTA*",
    "group": "Complex Environments",
    "goal": "Agent tìm đường đi MÀ ĐI, cập nhật heuristic trong quá trình đi.",
    "idea": "Không biết trước bản đồ. Tại mỗi state, chọn neighbor có cost + H nhỏ nhất. Sau khi đi, cập nhật H(current).",
    "data_structure": "H-table: lưu heuristic đã cập nhật cho mỗi state đã thăm.",
    "formula": "H(s) ban đầu = h(s). Chọn: argmin [c(s,a) + H(result(s,a))]. Cập nhật: H(s) = c(s,a) + H(s').",
    "pseudocode": """LRTA*(start, goal, h):
  H = {} # heuristic table
  current = start
  while current ≠ goal:
    H[current] = max(H.get(current, h(current)),
                     min(c(current,a) + H.get(result(current,a), h(result(current,a))) for a in actions))
    next = argmin [c(current,a) + H.get(result(current,a), h(result(current,a)))]
    move to next
    current = next""",
    "application": "Agent phải hành động TRONG KHI tìm hiểu môi trường. Mỗi bước vừa đi vừa học.",
    "suitable": "Không phải thuật toán chuẩn cho 15-puzzle (vì 15-puzzle đã biết trước model). Minh họa online search.",
    "pros": ["Không cần biết trước môi trường", "Học heuristic trong quá trình đi", "Tiến về goal dần dần"],
    "cons": ["Có thể đi đường vòng", "Cần nhiều lần chạy để tối ưu", "Chậm hơn offline search"],
    "complexity": "Phụ thuộc vào heuristic ban đầu và cấu trúc môi trường. Dần dần cải thiện.",
    "bad_example": "LRTA* lần đầu có thể đi đường rất dài. Chỉ tối ưu sau nhiều lần chạy.",
    "comparison": "LRTA* → online, học heuristic trong quá trình đi. A* → offline, biết trước toàn bộ môi trường.",
    "exam_tips": "Online search ⇒ không biết trước môi trường. LRTA* cập nhật H(s) sau mỗi bước. Offline search (A*) ⇒ biết trước môi trường.",
}

# ============================================================
# GROUP 5: CSP
# ============================================================

THEORY["CSP Definition"] = {
    "name": "CSP Definition for 15-Puzzle",
    "group": "CSP",
    "goal": "Mô hình hóa 15-puzzle thành bài toán ràng buộc (Constraint Satisfaction Problem).",
    "idea": "Biến số: X[t][p] = tile tại vị trí p thời điểm t. Ràng buộc: AllDifferent, Transition, Initial, Goal.",
    "data_structure": "Variables, Domains, Constraints.",
    "formula": "CSP = (X, D, C). X = {X[t][p], A[t]}. D = ranges. C = AllDifferent + Transition + Legal + Initial + Goal.",
    "pseudocode": "See csp.py for detailed definition.",
    "application": "15-puzzle thường là state-space search. Có thể mô hình thành CSP planning nhưng phức tạp hơn.",
    "suitable": "CSP không phải mô hình chuẩn cho 15-puzzle. State-space search (A*) phù hợp hơn.",
    "pros": ["Khung bài toán chính quy", "Có thể dùng constraint propagation"],
    "cons": ["CSP planning cho 15-puzzle rất lớn", "Không hiệu quả bằng A*", "Số biến tăng tuyến tính theo horizon"],
    "complexity": "Số biến: O(16 × T + T). Số ràng buộc: AllDifferent (T siêu ràng buộc) + Transition.",
    "bad_example": "Với T=20, cần 16×21+20 = 356 biếnvà AllDifferent constraint cho mỗi timestep.",
    "comparison": "CSP → mô hình hóa bài toán bằng ràng buộc. Search → mô hình hóa bằng trạng thái + hành động.",
    "exam_tips": "CSP = (X, D, C). X=variables, D=domains, C=constraints. 15-puzzle CSP planning: X[t][p] cho mỗi timestep.",
}

for algo_name in ["Constraint Propagation", "Path Consistency", "Global Constraints", "Backtracking Search", "Min-Conflicts", "Constraint Graphs"]:
    if algo_name not in THEORY:
        THEORY[algo_name] = {
            "name": algo_name,
            "group": "CSP",
            "goal": f"CSP technique: {algo_name} for 15-puzzle planning.",
            "idea": f"See detailed explanation in csp.py for {algo_name}.",
            "data_structure": "Various CSP data structures.",
            "formula": "See algorithm implementation.",
            "pseudocode": "See csp.py",
            "application": "CSP techniques for 15-puzzle planning model. Not the standard approach.",
            "suitable": "CSP is not the standard approach for 15-puzzle. These are for academic illustration.",
            "pros": ["Formal framework", "Can use propagation"],
            "cons": ["Very large for deep puzzles", "Less efficient than A*"],
            "complexity": "Depends on number of variables and constraints.",
            "bad_example": "Full CSP planning for 15-puzzle is extremely large.",
            "comparison": "CSP planning vs state-space search: CSP models constraints explicitly, search explores states.",
            "exam_tips": "CSP techniques: arc consistency, path consistency, backtracking with MRV/forward checking, min-conflicts.",
        }

# ============================================================
# GROUP 6: ADVERSARIAL / STOCHASTIC
# ============================================================

THEORY["Minimax"] = {
    "name": "Minimax",
    "group": "Adversarial/Stochastic",
    "goal": "Tìm chiến lược tối ưu trong game 2 người zero-sum. MAX maximize, MIN minimax.",
    "goal_en": "Find the optimal strategy in a 2-player zero-sum game. MAX maximizes utility, MIN minimizes it.",
    "idea": "MAX chọn action tối đa hóa utility. MIN chọn action tối tiểu hóa utility. Depth-limited với evaluation function.",
    "idea_en": "MAX selects actions that maximize utility. MIN selects actions that minimize utility. Depth-limited with an evaluation function.",
    "data_structure": "Game tree. MAX node: chọn max. MIN node: chọn min.",
    "data_structure_en": "Game tree. MAX node: selects max. MIN node: selects min.",
    "formula": "Minimax(s) = utility(s) if terminal. Max_a Minimax(Result(s,a)) if MAX. Min_a Minimax(Result(s,a)) if MIN.",
    "formula_en": "Minimax(s) = utility(s) if terminal. Max_a Minimax(Result(s,a)) if MAX. Min_a Minimax(Result(s,a)) if MIN.",
    "pseudocode": """Minimax(state, depth, isMax):
  if terminal(state) or depth == 0:
    return evaluate(state)
  if isMax:
    return max(Minimax(Result(state, a), depth-1, False) for a in actions)
  else:
    return min(Minimax(Result(state, a), depth-1, True) for a in actions)""",
    "application": "15-puzzle KHÔNG phải game 2 người. Mô phỏng: MAX = solver, MIN = adversary cố gắng làm MAX xa goal.",
    "application_en": "15-puzzle is NOT a 2-player game. Simulation: MAX = solver, MIN = adversary trying to move MAX away from the goal.",
    "suitable": "KHÔNG phù hợp cho 15-puzzle chuẩn. Chỉ minh họa khái niệm game tree.",
    "suitable_en": "NOT suitable for standard 15-puzzle. Only for illustrating game tree concepts.",
    "pros": ["Optimal trong game 2 người zero-sum", "Complete với evaluation function"],
    "pros_en": ["Optimal in 2-player zero-sum games", "Complete with evaluation function"],
    "cons": ["O(b^m) thời gian", "Không phải thuật toán chuẩn cho 15-puzzle", "MIN không có ý nghĩa cho puzzle"],
    "cons_en": ["O(b^m) time complexity", "Not a standard solver for 15-puzzle", "MIN has no physical meaning in puzzle"],
    "complexity": "Thời gian: O(b^m), Bộ nhớ: O(b×m) với depth-first.",
    "complexity_en": "Time: O(b^m), Space: O(bm) with depth-first search",
    "bad_example": "Game tree cho 15-puzzle: mỗi node có 2-4 nhánh, depth 3 đã hàng trăm node.",
    "bad_example_en": "Game tree for 15-puzzle: each node has 2-4 branches, depth 3 already contains hundreds of nodes.",
    "comparison": "Minimax → game 2 người. Alpha-Beta → Minimax + pruning. Expectimax → game ngẫu nhiên.",
    "comparison_en": "Minimax is for 2-player games. Alpha-Beta is Minimax + pruning. Expectimax is for stochastic environments.",
    "exam_tips": "Minimax: MAX chọn max, MIN chọn min. Zero-sum game. Alpha-Beta cắt nhánh không ảnh hưởng kết quả.",
    "exam_tips_en": "Minimax: MAX chooses max, MIN chooses min. Zero-sum games. Alpha-Beta prunes branches that do not affect the outcome.",
}

THEORY["Alpha-Beta"] = {
    "name": "Alpha-Beta Pruning",
    "group": "Adversarial/Stochastic",
    "goal": "Tối ưu Minimax bằng cách cắt nhánh không ảnh hưởng kết quả.",
    "goal_en": "Optimize Minimax by pruning branches that do not affect the final decision.",
    "idea": "Alpha: best value MAX đã thấy. Beta: best value MIN đã thấy. Cắt khi alpha ≥ beta.",
    "idea_en": "Alpha: best value MAX can guarantee. Beta: best value MIN can guarantee. Prune when alpha >= beta.",
    "data_structure": "Giống Minimax + alpha/beta bounds.",
    "data_structure_en": "Same as Minimax with alpha/beta bounds.",
    "formula": "Alpha-beta: if alpha ≥ beta → PRUNE. Result = same as Minimax but faster.",
    "formula_en": "Alpha-beta: if alpha >= beta -> PRUNE. Result is mathematically identical to Minimax but faster.",
    "pseudocode": """Alpha-Beta(state, depth, alpha, beta, isMax):
  if terminal or depth == 0: return evaluate(state)
  if isMax:
    value = -∞
    for a in actions:
      value = max(value, Alpha-Beta(Result(s,a), depth-1, alpha, beta, False))
      alpha = max(alpha, value)
      if alpha ≥ beta: break  # beta cutoff
    return value
  else:
    value = +∞
    for a in actions:
      value = min(value, Alpha-Beta(Result(s,a), depth-1, alpha, beta, True))
      beta = min(beta, value)
      if alpha ≥ beta: break  # alpha cutoff
    return value""",
    "application": "Cùng game tree với Minimax nhưng duyệt ít node hơn. Kết quả GIỐNG HỆT Minimax.",
    "application_en": "Traverses same game tree as Minimax but visits fewer nodes. Yields IDENTICAL results.",
    "suitable": "Không phù hợp cho 15-puzzle chuẩn. Minh họa pruning technique.",
    "suitable_en": "NOT suitable for standard 15-puzzle. Illustrates pruning techniques.",
    "pros": ["Kết quả giống Minimax", "Duyệt ít node hơn", "Tối ưu khi node được sắp xếp tốt"],
    "pros_en": ["Identical outcome to Minimax", "Visits fewer nodes", "Optimal when moves are well ordered"],
    "cons": ["Worst case vẫn O(b^m)", "Không phải thuật toán cho 15-puzzle", "Cần good move ordering"],
    "cons_en": ["Worst case remains O(b^m)", "Not a solver for 15-puzzle", "Requires good move ordering"],
    "complexity": "Best: O(b^(m/2)), Worst: O(b^m) giống Minimax. Average: significantly better.",
    "complexity_en": "Best: O(b^(m/2)), Worst: O(b^m) same as Minimax. Average is significantly better.",
    "bad_example": "Với bad move ordering, Alpha-Beta duyệt gần bằng Minimax.",
    "bad_example_en": "With bad move ordering, Alpha-Beta pruning evaluates almost as many nodes as Minimax.",
    "comparison": "Alpha-Beta = Minimax + pruning. Kết quả giống hệt. Node duyệt ít hơn (đặc biệt khi sắp xếp nước đi tốt).",
    "comparison_en": "Alpha-Beta = Minimax + pruning. Same result, fewer nodes visited (especially with good move ordering).",
    "exam_tips": "Alpha-beta pruning ⇒ kết quả GIỐNG Minimax, node duyệt ÍT HƠN. Alpha = best for MAX, Beta = best for MIN. Cắt khi α ≥ β.",
    "exam_tips_en": "Alpha-beta pruning yields IDENTICAL results to Minimax with FEWER node expansions. Alpha = best for MAX, Beta = best for MIN. Prune when α >= β.",
}

THEORY["Expectimax"] = {
    "name": "Expectimax",
    "group": "Adversarial/Stochastic",
    "goal": "Tính kỳ vọng utility khi có yếu tố ngẫu nhiên (chance node).",
    "goal_en": "Calculate expected utility under random chance nodes.",
    "idea": "MAX node: chọn max. CHANCE node: tính kỳ vọng dựa trên xác suất. Không giả sử đối thủ xấu nhất.",
    "idea_en": "MAX node: selects max. CHANCE node: calculates expected value based on probabilities. Does not assume worst-case play from opponent.",
    "data_structure": "Game tree với MAX node và CHANCE node.",
    "data_structure_en": "Game tree with MAX nodes and CHANCE nodes.",
    "formula": "Expectimax(s) = utility if terminal. Max_a Expectimax(Result(s,a)) if MAX. Σ P(a) × Expectimax(Result(s,a)) if CHANCE.",
    "formula_en": "Expectimax(s) = utility if terminal. Max_a Expectimax(Result(s,a)) if MAX. Sum P(a) * Expectimax(Result(s,a)) if CHANCE.",
    "pseudocode": """Expectimax(state, depth, nodeType):
  if terminal or depth == 0: return evaluate(state)
  if nodeType == MAX:
    return max(Expectimax(Result(s,a), depth-1, CHANCE) for a in actions)
  elif nodeType == CHANCE:
    return Σ P(a) × Expectimax(Result(s,a), depth-1, MAX) for a in outcomes""",
    "application": "15-puzzle mở rộng: action có xác suất thành công (ví dụ 80% đúng, 20% lệch).",
    "application_en": "Extended 15-puzzle: actions have success probabilities (e.g. 80% success, 20% slide failure).",
    "suitable": "Không phải thuật toán cho 15-puzzle chuẩn. Minh họa decision-making dưới uncertainty.",
    "suitable_en": "NOT suitable for standard 15-puzzle. Illustrates decision-making under uncertainty.",
    "pros": ["Tính kỳ vọng thay vì worst-case", "Phù hợp môi trường ngẫu nhiên", "Thực tế hơn Minimax khi không có đối thủ"],
    "pros_en": ["Calculates average utility instead of worst-case", "Ideal for stochastic environments", "More realistic than Minimax when there is no active adversary"],
    "cons": ["Không pruning được như alpha-beta", "Cần biết xác suất", "O(b^m) như Minimax nhưng không cắt được"],
    "cons_en": ["Cannot prune like Alpha-Beta", "Requires known probabilities", "O(b^m) time complexity without cuts"],
    "complexity": "O(b^m) — không thể pruning vì cần tính tất cả outcomes.",
    "complexity_en": "O(b^m) — cannot prune because all outcomes must be evaluated for expectation.",
    "bad_example": "Expectimax tạo nhiều node hơn Minimax vì mỗi MAX node sinh CHANCE node với nhiều outcomes.",
    "bad_example_en": "Expectimax generates more nodes than Minimax because each MAX node spawns CHANCE nodes with multiple outcomes.",
    "comparison": "Minimax ⇒ giả sử đối thủ xấu nhất. Expectimax ⇒ tính kỳ vọng theo xác suất. Expectimax không cắt được như alpha-beta.",
    "comparison_en": "Minimax assumes worst-case opponent. Expectimax computes expectation based on probability. Expectimax cannot be pruned like Alpha-Beta.",
    "exam_tips": "Expectimax ⇒ MAX + CHANCE node. CHANCE node tính kỳ vọng. Không pruning được. Kết quả khác Minimax khi xác suất ≠ worst-case.",
    "exam_tips_en": "Expectimax ⇒ MAX + CHANCE nodes. CHANCE nodes calculate expected value. Pruning is not possible. Results differ from Minimax when probabilities differ from worst-case.",
}


def _build_theory_by_group() -> dict[str, dict[str, dict]]:
    """Group theory notes by algorithm family for UI and future modularization."""
    grouped: dict[str, dict[str, dict]] = {}
    for algorithm_name, theory_data in THEORY.items():
        group = theory_data.get("group", "Other")
        grouped.setdefault(group, {})[algorithm_name] = theory_data
    return grouped


THEORY_BY_GROUP = _build_theory_by_group()
