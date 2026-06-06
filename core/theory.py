"""Academic theory notes for all 27 algorithms across 6 groups."""

THEORY = {}

# ============================================================
# GROUP 1: UNINFORMED SEARCH
# ============================================================

THEORY["BFS"] = {
    "name": "BFS — Breadth-First Search",
    "group": "Uninformed Search",
    "goal": "Tìm đường đi ngắn nhất trong không gian trạng thái (mỗi bước cost = 1).",
    "idea": "Duyệt theo mức: mở rộng tất cả node ở depth d trước khi sang depth d+1. Dùng hàng đợi FIFO.",
    "data_structure": "Queue (FIFO) cho Frontier, Set/Dict cho Reached.",
    "formula": "Mỗi node có g(n) = depth từ root. BFS ưu tiên node có g nhỏ nhất (FIFO guarantee).",
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
    "application": "Duyệt theo chiều rộng, đảm bảo tìm thấy lời giải ngắn nhất nếu cost mỗi bước bằng nhau. Tuy nhiên frontier tăng theo cấp số nhân — cần rất nhiều bộ nhớ cho 15-puzzle sâu.",
    "suitable": "Phù hợp về mặt lý thuyết (optimal, complete) nhưng THỰC TẾ rất tốn bộ nhớ. Chỉ nên dùng scramble depth ≤ 10.",
    "pros": ["Complete (với không gian hữu hạn)", "Optimal (với unit cost)", "Đơn giản cài đặt"],
    "cons": ["Bộ nhớ O(b^d) — cực lớn", "Frontier có thể hàng triệu node cho 15-puzzle", "Chậm với puzzle sâu"],
    "complexity": "Thời gian: O(b^d), Bộ nhớ: O(b^d), b=branching factor, d=depth",
    "bad_example": "Scramble depth 20: BFS cần mở rộng ~3^20 ≈ 3.5 tỷ node. Không thể chạy trong thực tế.",
    "comparison": "BFS tối ưu hơn DFS nhưng tốn bộ nhớ hơn. IDS có tính chất tối ưu của BFS nhưng tiết kiệm bộ nhớ.",
    "exam_tips": "BFS ⇒ optimal cho unit cost. BFS ⇒ complete. BFS tốn bộ nhớ nhất trong 3 thuật toán cơ bản (BFS, DFS, UCS).",
}

THEORY["DFS"] = {
    "name": "DFS — Depth-First Search",
    "group": "Uninformed Search",
    "goal": "Duyệt sâu nhất có thể trước khi quay lui. Không đảm bảo tối ưu.",
    "idea": "Dùng Stack LIFO. Đi xuống sâu nhất nhánh trước, quay lui khi không còn lựa chọn. Cần depth limit để tránh vô hạn.",
    "data_structure": "Stack (LIFO) cho Frontier, Set cho visited.",
    "formula": "Không có hàm đánh giá. Chỉ ưu tiên node sâu nhất.",
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
    "application": "DFS ít tốn bộ nhớ (chỉ lưu đường đi hiện tại) nhưng có thể đi rất sâu và tìm đường rất dài. Cho 15-puzzle, DFS có thể tạo đường đi hàng ngàn bước.",
    "suitable": "KHÔNG phù hợp cho 15-puzzle vì không đảm bảo tối ưu và đường đi có thể rất dài. Chỉ dùng để minh họa.",
    "pros": ["Tiết kiệm bộ nhớ O(b*d)", "Đơn giản", "Tìm nhanh một lời giải (không nhất thiết tối ưu)"],
    "cons": ["Không tối ưu", "Không complete (với depth limit)", "Đường đi có thể rất dài"],
    "complexity": "Thời gian: O(b^m) với m=max depth, Bộ nhớ: O(b*d) với d=chiều sâu.getCurrent",
    "bad_example": "DFS có thể đi đường dài 100+ bước cho puzzle chỉ cần 10 bước tối ưu.",
    "comparison": "DFS tiết kiệm bộ nhớ hơn BFS rất nhiều nhưng đường đi tệ hơn. IDS kết hợp ưu điểm cả hai.",
    "exam_tips": "DFS ⇒ KHÔNG optimal, KHÔNG complete (với depth limit). DFS ⇒ tiết kiệm bộ nhớ. DFS ⇒ có thể bị kẹt nhánh sai.",
}

THEORY["UCS"] = {
    "name": "UCS — Uniform Cost Search",
    "group": "Uninformed Search",
    "goal": "Tìm đường đi chi phí thấp nhất, cho phép cost mỗi bước khác nhau.",
    "idea": "Giống BFS nhưng dùng Priority Queue theo g(n). Khi cost mỗi bước = 1, UCS tương đương BFS.",
    "data_structure": "Priority Queue (min-heap) theo g(n), Dict cho best_g.",
    "formula": "Ưu tiên node có g(n) nhỏ nhất. g(n) = tổng cost từ start đến n.",
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
    "application": "Khi cost mỗi bước = 1 (như 15-puzzle), UCS giống hệt BFS. Chỉ có lợi khi cost khác nhau.",
    "suitable": "Về lý thuyết optimal và complete, nhưng thực tế giống BFS — tốn bộ nhớ. Không có lợi cho 15-puzzle vì cost đồng nhất.",
    "pros": ["Optimal (luôn tìm đường chi phí thấp nhất)", "Complete", "Total order trên g(n)"],
    "cons": ["Tốn bộ nhớ như BFS", "Với unit cost, tương đương BFS — không thêm lợi ích", "Priority queue overhead"],
    "complexity": "Thời gian: O(b^(C*/ε)), Bộ nhớ: O(b^(C*/ε)), C*=optimal cost, ε=min step cost",
    "bad_example": "UCS cho 15-puzzle cho kết quả giống BFS nhưng chậm hơn do priority queue overhead.",
    "comparison": "UCS = BFS khi cost đều. UCS > BFS khi cost khác nhau. UCS < A* khi có heuristic tốt.",
    "exam_tips": "UCS ⇒ optimal và complete. UCS với unit cost = BFS. UCS mở rộng theo g(n) tăng dần.",
}

THEORY["IDS"] = {
    "name": "IDS — Iterative Deepening Search",
    "group": "Uninformed Search",
    "goal": "Kết hợp ưu điểm BFS (optimal) và DFS (tiết kiệm bộ nhớ).",
    "idea": "Chạy DFS với depth limit tăng dần: 0, 1, 2, 3, ... Mỗi vòng lặp lại duyệt từ đầu nhưng chỉ sâu đến limit hiện tại.",
    "data_structure": "Stack cho DFS, lặp từ depth 0 đến depth tối đa.",
    "formula": "IDS(0) → DFS(depth=0) → IDS(1) → DFS(depth=1) → IDS(2) → DFS(depth=2) → ...",
    "pseudocode": """IDS(start, goal):
  for depth = 0, 1, 2, ...:
    result = DFS_with_limit(start, goal, depth)
    if result == FOUND: return path
    if result == CUTOFF: continue
  return failure""",
    "application": "Tối ưu như BFS (unit cost) nhưng chỉ tốn bộ nhớ O(b*d). Expand lại node nhiều lần nhưng overhead nhỏ vì số node ở level sâu nhất chiếm đa số.",
    "suitable": "Rất phù hợp cho 15-puzzle vì tiết kiệm bộ nhớ và vẫn optimal. Preferrred hơn BFS cho bài toán lớn.",
    "pros": ["Optimal (unit cost)", "Complete", "Tiết kiệm bộ nhớ O(b*d)", "Kết hợp ưu BFS + DFS"],
    "cons": ["Expand lại node nhiều lần (nhưng overhead nhỏ)", "Chậm hơn BFS chút ít do lặp lại"],
    "complexity": "Thời gian: O(b^d) (như BFS), Bộ nhớ: O(b*d) (như DFS)",
    "bad_example": "IDS lặp lại DFS nhiều lần. Với b=3, d=10: tổng node ≈ b^d/(b-1) gần như BFS. Overhead nhỏ.",
    "comparison": "IDS có tính chất optimal + complete của BFS nhưng bộ nhớ của DFS. Là lựa chọn tốt nhất trong uninformed search cho 15-puzzle.",
    "exam_tips": "IDS ⇒ optimal (unit cost), complete, tiết kiệm bộ nhớ. IDS expand lại node nhưng overhead nhỏ. IDS là uninformed search tốt nhất cho bài toán неизвест trước depth.",
}

# ============================================================
# GROUP 2: INFORMED SEARCH
# ============================================================

THEORY["Greedy"] = {
    "name": "Greedy Best-First Search",
    "group": "Informed Search",
    "goal": "Tìm lời giải nhanh bằng cách ưu tiên node có heuristic nhỏ nhất.",
    "idea": "Chỉ dùng h(n) để đánh giá, không xét g(n). Chạy nhanh nhưng không đảm bảo tối ưu.",
    "data_structure": "Priority Queue theo h(n), Dict cho reached.",
    "formula": "Ưu tiên: h(n) nhỏ nhất. h(n) =估计 chi phí từ n đến goal.",
    "pseudocode": """Greedy(start, goal, h):
  Frontier ← PriorityQueue [(h(start), start)]
  Reached ← {start}
  while Frontier:
    node ← Frontier.dequeue_min_h()
    if node.state == goal: return path
    for neighbor của node:
      if neighbor.state not in Reached:
        Reached.add(neighbor.state)
        Frontier.insert((h(neighbor.state), neighbor))""",
    "application": "Chạy nhanh cho 15-puzzle vì h(n) dẫn đường, nhưng có thể bị lừa bởi heuristic — chọn đường gần goal hơn nhưng thực ra đường dài hơn.",
    "suitable": "Nhanh nhưng KHÔNG optimal. Dùng khi cần lời giải nhanh, chấp nhận không tối ưu.",
    "pros": ["Nhanh — ít mở rộng node", "Đơn giản cài đặt", "Dùng heuristic dẫn đường"],
    "cons": ["KHÔNG optimal", "Có thể bị kẹt local minimum", "Đường đi thường dài hơn A*"],
    "complexity": "Thời gian: O(b^m) worst case, thường nhanh hơn. Bộ nhớ: O(b^m).",
    "bad_example": "Greedy có thể đi đường gấp khúc quanh local minimum, trong khi A* đi thẳng.",
    "comparison": "Greedy nhanh hơn A* nhưng đường đi tệ hơn. A* = Greedy + g(n) cân bằng.",
    "exam_tips": "Greedy ⇒ KHÔNG optimal, KHÔNG complete. Greedy chỉ dùng h(n). Greedy nhanh nhưng đường đi tệ.",
}

THEORY["A*"] = {
    "name": "A* Search",
    "group": "Informed Search",
    "goal": "Tìm đường đi tối ưu bằng cách cân bằng g(n) và h(n).",
    "idea": "f(n) = g(n) + h(n). Nếu h admissible (không overestimate) và consistent, A* đảm bảo tối ưu.",
    "data_structure": "Priority Queue theo f(n)=g(n)+h(n), Dict cho best_g.",
    "formula": "f(n) = g(n) + h(n). g(n) = cost từ start đến n. h(n) = ước lượng chi phí từ n đến goal.",
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
    "application": "Thuật toán tốt nhất cho 15-puzzle khi dùng Manhattan hoặc Linear Conflict heuristic. Cân bằng giữa tốc độ và tối ưu.",
    "suitable": "RẤT phù hợp cho 15-puzzle. Là thuật toán chuẩn để giải 15-puzzle. Với heuristic mạnh (Manhattan, Linear Conflict), A* giải được puzzle sâu 50+ bước.",
    "pros": ["Optimal (với heuristic admissible + consistent)", "Complete", "Hiệu quả hơn BFS/UCS khi có heuristic tốt", "Lựa chọn tốt nhất cho 15-puzzle"],
    "cons": ["Tốn bộ nhớ O(b^d)", "Chậm hơn Greedy vì mở rộng nhiều node hơn", "Heuristic yếu → gần BFS"],
    "complexity": "Thời gian: O(b^d) worst, nhưng thường O(b^(εd)) với ε phụ thuộc heuristic. Bộ nhớ: O(b^d).",
    "bad_example": "Với h=0 (không heuristic), A* = UCS = BFS. Heuristic yếu cho kết quả chậm.",
    "comparison": "A* = Greedy + UCS. A* tối ưu, Greedy thì không. A* dùng f=g+h, Greedy chỉ dùng h.",
    "exam_tips": "A* ⇒ optimal NẾU h admissible + consistent. A* ⇒ complete. A* mở rộng node theo f tăng dần. Manhattan là consistent heuristic cho 15-puzzle.",
}

THEORY["IDA*"] = {
    "name": "IDA* — Iterative Deepening A*",
    "group": "Informed Search",
    "goal": "A* tiết kiệm bộ nhớ bằng iterative deepening trên f-cost.",
    "idea": "Chạy DFS với f-limit. Mỗi vòng tăng threshold lên min f-cost vượt threshold trước. Kết hợp A* và IDS.",
    "data_structure": "Stack cho DFS, không cần Priority Queue. Chỉ cần lưu đường đi hiện tại.",
    "formula": "Threshold ban đầu = h(start). DFS chỉ mở rộng node có f(n) ≤ threshold. Next threshold = min f(n) > current threshold.",
    "pseudocode": """IDA*(start, goal, h):
  threshold = h(start)
  while True:
    result, next_t = DFS_f_limit(start, goal, threshold, h)
    if result == FOUND: return path
    if next_t == ∞: return failure
    threshold = next_t""",
    "application": "Tiết kiệm bộ nhớ hơn A* đáng kể (chỉ O(b*d)). Phù hợp cho 15-puzzle khi A* hết bộ nhớ. Expand lại node nhưng overhead chấp nhận được.",
    "suitable": "Rất phù hợp cho 15-puzzle, đặc biệt puzzle sâu. Là lựa chọn khi A* hết RAM.",
    "pros": ["Optimal (với heuristic admissible)", "Tiết kiệm bộ nhớ O(b*d)", "Complete"],
    "cons": ["Expand lại node nhiều lần hơn A*", "Chậm hơn A* khi bộ nhớ đủ", "Threshold tăng nhỏ giọt nếu heuristic không sát"],
    "complexity": "Thời gian: O(b^d), Bộ nhớ: O(b*d) — tiết kiệm hơn A* rất nhiều.",
    "bad_example": "IDA* với h=0 → tương đương IDS. Iteration tăng 1 mỗi vòng, rất chậm.",
    "comparison": "IDA* có tính chất A* nhưng bộ nhớ IDS. IDA* lặp lại nhiều vòng nhưng mỗi vòng nhanh vì DFS.",
    "exam_tips": "IDA* ⇒ optimal (h admissible), O(b*d) memory. IDA* dùng threshold thay vì priority queue. IDA* là A* + IDS.",
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
    "goal": "Tìm chiến lược tối ưu trong game 2 người zero-sum. MAX максимin, MIN minimax.",
    "idea": "MAX chọn action tối đa hóa utility. MIN chọn action tối tiểu hóa utility. Depth-limited với evaluation function.",
    "data_structure": "Game tree. MAX node: chọn max. MIN node: chọn min.",
    "formula": "Minimax(s) = utility(s) if terminal. Max_a Minimax(Result(s,a)) if MAX. Min_a Minimax(Result(s,a)) if MIN.",
    "pseudocode": """Minimax(state, depth, isMax):
  if terminal(state) or depth == 0:
    return evaluate(state)
  if isMax:
    return max(Minimax(Result(state, a), depth-1, False) for a in actions)
  else:
    return min(Minimax(Result(state, a), depth-1, True) for a in actions)""",
    "application": "15-puzzle KHÔNG phải game 2 người. Mô phỏng: MAX = solver, MIN = adversary cố gắng làm MAX xa goal.",
    "suitable": "KHÔNG phù hợp cho 15-puzzle chuẩn. Chỉ minh họa khái niệm game tree.",
    "pros": ["Optimal trong game 2 người zero-sum", "Complete với evaluation function"],
    "cons": ["O(b^m) thời gian", "Không phải thuật toán chuẩn cho 15-puzzle", "MIN không có ý nghĩa cho puzzle"],
    "complexity": "Thời gian: O(b^m), Bộ nhớ: O(b×m) với depth-first.",
    "bad_example": "Game tree cho 15-puzzle: mỗi node có 2-4 nhánh, depth 3 đã hàng trăm node.",
    "comparison": "Minimax → game 2 người. Alpha-Beta → Minimax + pruning. Expectimax → game ngẫu nhiên.",
    "exam_tips": "Minimax: MAX chọn max, MIN chọn min. Zero-sum game. Alpha-Beta cắt nhánh không ảnh hưởng kết quả.",
}

THEORY["Alpha-Beta"] = {
    "name": "Alpha-Beta Pruning",
    "group": "Adversarial/Stochastic",
    "goal": "Tối ưu Minimax bằng cách cắt nhánh không ảnh hưởng kết quả.",
    "idea": "Alpha: best value MAX đã thấy. Beta: best value MIN đã thấy. Cắt khi alpha ≥ beta.",
    "data_structure": "Giống Minimax + alpha/beta bounds.",
    "formula": "Alpha-beta: if alpha ≥ beta → PRUNE. Result = same as Minimax but faster.",
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
    "suitable": "Không phù hợp cho 15-puzzle chuẩn. Minh họa pruning technique.",
    "pros": ["Kết quả giống Minimax", "Duyệt ít node hơn", "Tối ưu khi node được sắp xếp tốt"],
    "cons": ["Worst case vẫn O(b^m)", "Không phải thuật toán cho 15-puzzle", "Cần good move ordering"],
    "complexity": "Best: O(b^(m/2)), Worst: O(b^m) giống Minimax. Average: significantly better.",
    "bad_example": "Với bad move ordering, Alpha-Beta duyệt gần bằng Minimax.",
    "comparison": "Alpha-Beta = Minimax + pruning. Kết quả giống hệt. Node duyệt ít hơn (đặc biệt khi sắp xếp nước đi tốt).",
    "exam_tips": "Alpha-beta pruning ⇒ kết quả GIỐNG Minimax, node duyệt ÍT HƠN. Alpha = best for MAX, Beta = best for MIN. Cắt khi α ≥ β.",
}

THEORY["Expectimax"] = {
    "name": "Expectimax",
    "group": "Adversarial/Stochastic",
    "goal": "Tính kỳ vọng utility khi có yếu tố ngẫu nhiên (chance node).",
    "idea": "MAX node: chọn max. CHANCE node: tính kỳ vọng dựa trên xác suất. Không giả sử đối thủ xấu nhất.",
    "data_structure": "Game tree với MAX node và CHANCE node.",
    "formula": "Expectimax(s) = utility if terminal. Max_a Expectimax(Result(s,a)) if MAX. Σ P(a) × Expectimax(Result(s,a)) if CHANCE.",
    "pseudocode": """Expectimax(state, depth, nodeType):
  if terminal or depth == 0: return evaluate(state)
  if nodeType == MAX:
    return max(Expectimax(Result(s,a), depth-1, CHANCE) for a in actions)
  elif nodeType == CHANCE:
    return Σ P(a) × Expectimax(Result(s,a), depth-1, MAX) for a in outcomes""",
    "application": "15-puzzle mở rộng: action có xác suất thành công (ví dụ 80% đúng, 20% lệch).",
    "suitable": "Không phải thuật toán cho 15-puzzle chuẩn. Minh họa decision-making dưới uncertainty.",
    "pros": ["Tính kỳ vọng thay vì worst-case", "Phù hợp môi trường ngẫu nhiên", "Thực tế hơn Minimax khi không có đối thủ"],
    "cons": ["Không pruning được như alpha-beta", "Cần biết xác suất", "O(b^m) như Minimax nhưng không cắt được"],
    "complexity": "O(b^m) — không thể pruning vì cần tính tất cả outcomes.",
    "bad_example": "Expectimax tạo nhiều node hơn Minimax vì mỗi MAX node sinh CHANCE node với nhiều outcomes.",
    "comparison": "Minimax ⇒ giả sử đối thủ xấu nhất. Expectimax ⇒ tính kỳ vọng theo xác suất. Expectimax không cắt được như alpha-beta.",
    "exam_tips": "Expectimax ⇒ MAX + CHANCE node. CHANCE node tính kỳ vọng. Không pruning được. Kết quả khác Minimax khi xác suất ≠ worst-case.",
}