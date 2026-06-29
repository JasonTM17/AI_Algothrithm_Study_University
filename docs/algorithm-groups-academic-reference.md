# Tham chiếu học thuật về các nhóm thuật toán

Tài liệu này dùng cho phần bảo vệ cuối kỳ của 15-Puzzle AI Algorithm Simulator. Nội dung bám theo `algorithms/`, `core/academic.py`, `core/algorithm_comparison.py`, `core/heuristics.py`, `core/metrics.py` và cách UI tách solver chuẩn khỏi concept lab.

## 1. Mô hình bài toán chuẩn

15-puzzle chuẩn trong repo là bài toán tìm kiếm trạng thái một tác tử.

| Thuộc tính | Kết luận học thuật | Ý nghĩa trong app |
|---|---|---|
| Quan sát | Fully observable | Agent thấy toàn bộ board 4x4. |
| Xác định | Deterministic | Một action hợp lệ luôn sinh đúng một state kế tiếp. |
| Động/tĩnh | Static | Board không tự đổi khi agent đang suy nghĩ. |
| Rời rạc | Discrete | State, action và path cost đều rời rạc. |
| Tuần tự | Sequential | Quyết định hiện tại ảnh hưởng các state sau. |
| Tác tử | Single-agent | Không có đối thủ trong bài toán chuẩn. |
| Chi phí | Unit step cost | Mỗi lần trượt ô trống có cost 1. |

PEAS chuẩn:

| PEAS | Diễn giải |
|---|---|
| Performance | Tới goal, ít bước, ít node mở rộng, ít bộ nhớ, runtime thấp. |
| Environment | Board 4x4, deterministic, fully observable, static, discrete, sequential, single-agent. |
| Actuators | Trượt ô trống theo `L/R/U/D` khi hợp lệ. |
| Sensors | Board đầy đủ, vị trí ô trống, legal moves và heuristic estimates. |

Ranh giới quan trọng: CSP, AND-OR, no/partial observation, Minimax, Alpha-Beta và Expectimax là phần mở rộng học thuật. AI-vs-AI Tournament là lớp chấm điểm giữa hai solver agent cùng giải 15-puzzle; nó không biến 15-puzzle thành môi trường có MIN player.

## 2. Phân loại nhanh

| Vai trò | Thuật toán | Có nên dùng làm solver chính? | Điểm bảo vệ |
|---|---|---:|---|
| Solver chuẩn | BFS, UCS, IDS, A*, IDA* | Có | Chứng minh lời giải hợp lệ, tính đầy đủ và tối ưu trong điều kiện phù hợp. |
| Demo đối chiếu | DFS, Greedy Best-First, local search variants | Không | Chỉ ra trade-off, suboptimality, local optimum, plateau hoặc thiếu guarantee. |
| Mở rộng minh họa | CSP, AND-OR, No Observation, Partial Observation | Không | Giải thích cách đổi mô hình bài toán, sensor hoặc environment. |
| Tournament/game/chance | AI-vs-AI Tournament, Minimax, Alpha-Beta, Expectimax | Tournament là scoring layer | Tournament chấm điểm hai agent; game/chance mode là extension giáo dục. |

Khi bảo vệ, luôn tách ba tầng bằng chứng:

1. Legal path certificate: mỗi cạnh trong path phải là legal blank move.
2. Goal reachability: path kết thúc đúng goal hay chỉ là partial/model/sample path.
3. Optimality certificate: thuật toán và heuristic có đủ điều kiện để chứng minh cost tối ưu hay không.

## 3. Dùng thuật toán nào là hợp lý cho 15-puzzle?

| Kết luận sử dụng | Thuật toán | Mức hợp lý cho 15-puzzle chuẩn | Cách nói chính xác |
|---|---|---:|---|
| Nên dùng làm solver chính khi cần lời giải có chứng cứ | A*, IDA* | Rất cao | Đây là lựa chọn hợp lý nhất cho demo solver: state-space search đúng bản chất bài toán, tận dụng heuristic, có optimality certificate khi điều kiện heuristic và tài nguyên thỏa. |
| Nên dùng để chứng minh nền tảng trên puzzle nông | BFS, UCS, IDS | Cao | BFS/UCS/IDS hợp lý vì bài toán có unit step cost; chúng complete/optimal trong điều kiện hữu hạn, nhưng BFS/UCS dễ bùng nổ bộ nhớ. |
| Dùng được để đối chiếu, không dùng làm kết luận solver tốt | DFS | Thấp | DFS phù hợp để nói về memory trade-off và depth limit; không được nói DFS tối ưu. |
| Dùng được để chứng minh heuristic không đủ | Greedy Best-First | Thấp | Greedy hợp lý như baseline nhanh hoặc ví dụ sai lầm; không được nói Greedy tối ưu vì nó bỏ qua `g(n)`. |
| Dùng được để dạy failure mode của local search | Hill Climbing variants, Local Beam, Simulated Annealing | Thấp cho solving, cao cho minh họa | Các thuật toán này hợp lý khi mục tiêu là local optimum, plateau, ridge, randomness; không hợp lý nếu xem là solver chuẩn đáng tin cậy. |
| Chỉ dùng như mô hình hóa CSP hoặc bằng chứng horizon nhỏ | Backtracking, Backtracking + Forward Checking, AC-3, Min-Conflicts | Không phải solver chuẩn | CSP hợp lý để học state-chain variables/domains/constraints; không hợp lý nếu claim là hướng tự nhiên nhất để giải 15-puzzle sâu. |
| Chỉ dùng khi cố ý đổi sensor/environment | AND-OR, No Observation, Partial Observation | Không phải solver chuẩn | Các thuật toán này hợp lý cho nondeterministic hoặc belief-state search; không nên so trực tiếp với A*/IDA* như cùng mô hình. |
| Chỉ dùng cho scoring/game/chance extension | AI-vs-AI Tournament, Minimax, Alpha-Beta, Expectimax | Không phải solver chuẩn | Tournament hợp lý để chấm hai solver bằng A* reference; Minimax/Alpha-Beta/Expectimax hợp lý để dạy game/chance, không hợp lý nếu nói 15-puzzle có đối thủ tự nhiên. |

Quy tắc ngắn: nếu mục tiêu là giải 15-puzzle chuẩn, ưu tiên A*/IDA*, dùng BFS/UCS/IDS cho puzzle nông và chứng minh lý thuyết. Các nhóm còn lại chỉ hợp lý khi mục tiêu là minh họa trade-off, failure mode hoặc mô hình AI mở rộng.

## 4. Các bước search nên nói theo thứ tự

| Bước | Nội dung | Bằng chứng trong app |
|---|---|---|
| 1 | Initial state và goal | Start/Goal contract trên các tab chạy. |
| 2 | Goal test | `goal_reached` tách riêng với `success`. |
| 3 | Frontier selection | Queue, stack, priority queue, beam hoặc temperature rule. |
| 4 | Expand legal actions | Chỉ sinh `L/R/U/D` hợp lệ của blank. |
| 5 | Reached/duplicate handling | `reached`, `best_g` hoặc path-set tùy thuật toán. |
| 6 | Termination/certificate | `termination_reason`, `path_verified`, `optimality_proven`. |

Tree search xem mỗi đường đi sinh ra là một node riêng, nên có thể lặp state. Graph search ghi nhớ state đã đến hoặc cost tốt nhất để tránh duplicate. App vẽ search tree bằng parent-child edge để minh họa quá trình sinh node, còn các solver chuẩn vẫn dùng duplicate handling để giữ tính đúng thực thi.

## 5. Chi tiết tham số kỹ thuật trong code

Các tham số dưới đây là phần dễ bị thiếu khi chỉ đọc lý thuyết. Chúng được đối chiếu từ `algorithms/`, `core/solver_dispatch.py` và `core/randomness.py`.

| Khu vực | Chi tiết triển khai | Ý nghĩa khi bảo vệ |
|---|---|---|
| Action order | Solver nhận `action_order`, mặc định `LRUD`; UI có thể đổi thứ tự action mỗi run. | Node count, trace và path có thể đổi theo thứ tự sinh neighbor; benchmark phải ghi action order. |
| Tie-breaker | UCS, Greedy và A* hỗ trợ `FIFO`, `LIFO`, `Min-g`, `Max-g`. | Tie-breaker chỉ phá hòa trong priority queue; không tự tạo optimality nếu thuật toán không optimal. |
| Resource limit | BFS/UCS/Greedy mặc định `max_nodes=50000`, A*/IDA* `100000`; DFS/IDS có thêm `max_depth=50`; timeout mặc định thường là `60s`, A*/IDA* là `120s`. | Timeout, node cap hoặc depth cap làm mất chứng cứ thực nghiệm; phải đọc `termination_reason` trước khi claim. |
| Run variation | `RunVariation` ghi seed, action order, tie-breaker, solver seed và cờ `randomizes_path`. | Run/Advanced giữ metadata nội bộ để kiểm thử; UI kết quả chính không hiển thị các dòng kỹ thuật gây nhiễu. |
| Solver thật sự dùng seed | Stochastic HC, Random-Restart HC, Simulated Annealing, Min-Conflicts, No Observation, Partial Observation và Expectimax. | Compare có thể hiển thị seed khi cần tái lập; Run/Advanced chỉ lưu nội bộ. |
| Non-path variation | AND-OR và belief-state policy không randomize path. | Đây là conditional/conformant/contingent output, không nên diễn giải như trajectory puzzle tuyến tính. |
| Dispatcher kwargs | `core/solver_dispatch.py` chỉ truyền tham số mà từng solver nhận được; CSP explanatory functions chỉ nhận start/goal, CSP search nhận timeout. | UI tránh truyền sai signature; khi audit lỗi run, kiểm `build_solver_kwargs` trước. |
| CSP horizon cap | `csp_definition` và `constraint_propagation` bị cap `time_horizon <= 5`; `solve_csp_constraint_graphs` cap `time_horizon <= 3`. | CSP demo cố ý bounded để dễ chạy; AC-3 exact-horizon không phải shortest-path proof toàn cục. |
| Backtracking CSP | `max_steps` mặc định `5000`, timeout `30s`, dùng heuristic value ordering. | Không gọi là MRV/LCV/forward checking đầy đủ; fail không chứng minh unsolvable. |
| Min-Conflicts | `max_iterations=10000`, timeout `30s`, seed tùy chọn; thao tác là repair/swap assignment. | Có thể đạt arrangement goal nhưng không phải legal blank-move solution. |
| Local Beam | `beam_width=3`, `max_iterations=10000`. | Beam hẹp có thể bỏ mất nhánh đúng; đây là demo heuristic/local search. |
| Random-Restart HC | `max_iterations=5000`, `max_restarts=20`, seed tùy chọn. | Nhiều restart tăng cơ hội nhưng không biến thành complete/optimal solver. |
| Simulated Annealing | `max_iterations=50000`, `initial_temp=100.0`, `cooling_rate=0.9995`, `min_temp=0.01`, seed tùy chọn. | Probability nhận move xấu phụ thuộc temperature; schedule là caveat quan trọng. |
| AND-OR | `max_depth=10`; UI dùng mode `Intended outcome only` hoặc `Include all legal deflections`. `nondet_prob` còn trong signature để tương thích và chỉ là binary support switch. | Output là conditional plan; OR là agent chọn, AND là mọi outcome phải xử lý, không rank bằng xác suất. |
| No/Partial Observation | `num_belief_states=5`, `max_steps=20`, seed tùy chọn; finite belief approximation. | Đây là conformant/contingent belief-state demo, không so node count trực tiếp với A*. |
| Minimax/Alpha-Beta | `depth=3`, heuristic mặc định Manhattan, timeout `60s`. | Depth-limited game-tree utility, không phải optimal certificate của puzzle chuẩn. |
| Expectimax | `depth=3`, `success_prob=0.8`, seed tùy chọn; returned actions là một sampled outcome path. | Expected utility cần mô hình xác suất; path hiển thị không phải full stochastic policy. |

## 6. Uninformed Search

Uninformed search không dùng heuristic. Frontier được điều khiển bởi depth, stack/queue hoặc path cost.

| Thuật toán | Frontier/evaluation | Complete | Optimal | Bộ nhớ | Ghi chú |
|---|---|---:|---:|---|---|
| BFS | FIFO queue, mở theo depth | Có nếu branching hữu hạn | Có với unit cost | `O(b^d)` | Dễ chứng minh shortest path nhưng nhanh hết bộ nhớ. |
| DFS | Stack/depth-first | Không đảm bảo trong graph/bounded run | Không | Thấp | Demo đối chiếu: tiết kiệm bộ nhớ nhưng dễ đi sâu sai hướng. |
| UCS | Priority queue theo `g(n)` | Có với cost dương | Có | Cao | Với 15-puzzle unit cost, gần BFS theo cost layer. |
| IDS | Lặp depth-limited search | Có với branching hữu hạn | Có với unit cost | `O(bd)` | Đổi runtime lấy bộ nhớ thấp. |

`b` là branching factor, `d` là độ sâu lời giải ngắn nhất, `m` là depth tối đa đang xét.

## 7. Informed Search và heuristic

| Thuật toán | Evaluation | Complete | Optimal | Vai trò |
|---|---|---:|---:|---|
| Greedy Best-First | Ưu tiên `h(n)` nhỏ nhất | Không đảm bảo trong bounded graph search | Không | Baseline heuristic-only để so với A*. |
| A* | `f(n)=g(n)+h(n)` | Có nếu heuristic admissible/consistent và đủ tài nguyên | Có | Solver tham chiếu chính. |
| IDA* | DFS theo ngưỡng `f` tăng dần | Có trong điều kiện hữu hạn | Có với admissible heuristic | Solver tối ưu tiết kiệm bộ nhớ hơn A*. |

Heuristic trong repo:

| Heuristic | Định nghĩa | Quan hệ sức mạnh | Dùng để bảo vệ |
|---|---|---|---|
| Misplaced Tiles | Đếm tile sai vị trí, bỏ qua blank | Yếu nhất | Dễ giải thích admissible. |
| Manhattan Distance | Tổng khoảng cách hàng/cột tới goal | Mạnh hơn Misplaced | Chuẩn để chứng minh A* optimality. |
| Linear Conflict | Manhattan cộng penalty conflict hợp lệ | Mạnh hơn Manhattan | Cho thấy heuristic mạnh hơn nhưng vẫn admissible. |

Admissible nghĩa là `h(n) <= h*(n)`. Consistent nghĩa là `h(n) <= c(n,n') + h(n')` với mọi cạnh hợp lệ. Nếu A* hoặc IDA* bị timeout/node cap, kết quả thực nghiệm không còn là optimality certificate.

## 8. Local Search

Local search không duy trì frontier đầy đủ. Nó giữ một state hiện tại, một vài state tốt nhất hoặc chấp nhận move xấu theo xác suất.

| Thuật toán | Cách chọn bước | Complete | Optimal | Failure mode |
|---|---|---:|---:|---|
| Simple Hill Climbing | Chọn cải thiện đầu tiên | Không | Không | Local optimum, plateau. |
| Steepest-Ascent Hill Climbing | Chọn neighbor tốt nhất | Không | Không | Kẹt nếu mọi neighbor không tốt hơn. |
| Stochastic Hill Climbing | Chọn cải thiện ngẫu nhiên | Không | Không | Phụ thuộc seed. |
| Random-Restart Hill Climbing | Chạy lại từ nhiều điểm | Không tuyệt đối | Không | Tăng xác suất thành công, không chứng minh tối ưu. |
| Local Beam Search | Giữ `k` state tốt nhất | Không | Không | Beam hẹp có thể mất nhánh lời giải. |
| Simulated Annealing | Có thể nhận move xấu theo temperature | Không hữu hạn | Không | Schedule kém có thể hội tụ kém. |

Các vấn đề hill climbing cần nói rõ:

| Vấn đề | Ý nghĩa | Cách app minh họa |
|---|---|---|
| Local optimum | Không neighbor nào tốt hơn current nhưng chưa tới goal. | Audited regression case và result caveat. |
| Plateau/shoulder | Nhiều neighbor có cùng `h`, strict improvement không có hướng đi. | Theory và local-search trace. |
| Ridge | Cần đi ngang hoặc tạm thời xấu hơn mới tốt về sau. | Simulated Annealing có xác suất nhận move xấu khi temperature còn cao. |
| Randomness dependence | Seed khác nhau sinh trajectory khác nhau. | Stochastic HC, Random-Restart HC, Simulated Annealing. |

## 9. CSP trong 15-puzzle

CSP mô hình hóa bài toán bằng biến `X`, miền giá trị `D` và ràng buộc `C`. Với 15-puzzle, có thể mô hình planning bằng biến theo time step, nhưng không tự nhiên bằng state-space search vì số biến/ràng buộc tăng theo horizon.

| Thành phần | Trong app | Ý nghĩa học thuật |
|---|---|---|
| Backtracking | Chronological assignment trên chuỗi state `S[0]..S[T]` | Minh họa exact-horizon CSP search. |
| Backtracking + Forward Checking | Backtracking kèm prune domain kế tiếp | So sánh pruning với backtracking thuần. |
| AC-3 | Arc consistency trên chuỗi state `S[0]..S[T]` | Thu hẹp domain; chỉ replay khi trích được exact legal path. |
| Min-Conflicts | Local repair trên complete state-chain assignment | Hợp với N-Queens hơn 15-puzzle transition planning; không complete/optimal. |

Backtracking CSP trong app dùng bounded state-chain domains. Forward Checking là biến thể riêng; AC-3 là propagation; Min-Conflicts là local repair, không phải shortest-path solver.

AC-3 executable dùng biến trạng thái đầy đủ để tránh bộ ràng buộc `X[t][p]` quá lớn trong demo. Hai đầu mút bị cố định bởi start và goal; mỗi cặp state liên tiếp phải cách nhau đúng một legal blank move. Kết quả chỉ cho horizon `T` đã chọn, không tự động chứng minh đường ngắn nhất toàn cục.

## 10. Complex Environments

Trong Run Algorithm, AND-OR có thể xuất hiện bằng alias để khớp đề cương. Đây chỉ là alias UI; taxonomy vẫn là `Complex Environments` và vai trò vẫn là `Illustrative Extension`.

| Thuật toán | Môi trường | Output | Ranh giới |
|---|---|---|---|
| AND-OR Search | Nondeterministic | Conditional plan | UI mặc định intended-only. All-deflections là stress test worst-case có safety cap; dừng vì cap/timeout không chứng minh không tồn tại plan. |
| No Observation Search | Không quan sát state thật | Conformant action sequence | Sensor bị yếu đi có chủ ý; hidden actual state không điều khiển policy. |
| Partially Observable Search | Quan sát một phần | Contingent policy theo observation | Không phải solver chuẩn; mọi branch observation phải được cover. |

Nếu sensor, transition hoặc observability thay đổi, biểu diễn state và thuật toán cũng thay đổi. Không so sánh node count của nhóm này với A*/IDA* như thể cùng một bài toán.

## 11. AI-vs-AI Tournament và game/chance extension

15-puzzle chuẩn là single-agent. Tournament trong app là lớp chấm điểm giữa hai agent giải cùng board, không phải đối kháng tự nhiên trong môi trường puzzle.

| Thành phần | Mô hình | Guarantee | Nên trình bày |
|---|---|---|---|
| AI-vs-AI Tournament | Hai solver agent chạy trên cùng start/goal | Điểm dựa trên A* reference optimal certificate | So sánh chất lượng lời giải, failure, runtime, nodes. |
| Minimax | MAX chọn move hứa hẹn; MIN là nhánh worst-case robustness trên cùng tập legal blank moves | Tối ưu theo utility nếu game tree/depth đúng và duyệt đủ | MIN không phải đối thủ thật của 15-puzzle; transferable concept là worst-case decision rule. |
| Alpha-Beta Pruning | Minimax có cắt tỉa | Giữ cùng root value với Minimax nếu điều kiện duyệt đủ | Pruning giảm node mà không đổi quyết định. |
| Expectimax | MAX/CHANCE tree | Tối ưu kỳ vọng theo xác suất mô hình | Ra quyết định khi có chance outcome. |

Scoring Tournament:

| Kết quả agent | Điểm |
|---|---:|
| Path hợp lệ, tới goal, cost bằng optimal cost | +100 |
| Path hợp lệ, tới goal, cost dài hơn optimal | `max(10, round(100 * optimal_cost / actual_cost))` |
| Path hợp lệ nhưng không tới goal | -10 |
| Timeout/resource limit/no path | -20 |
| Exception, path không verify, action sai luật, state/action mismatch | -50 |

Mỗi round chạy A* làm reference. Nếu A* reference không chứng minh được optimal path, round đó được báo `reference failed` và không chấm điểm. Tie-break theo tổng điểm, số round optimal, số round solved và total excess cost thấp hơn; nếu vẫn hòa thì draw.

## 12. Cách chọn thuật toán khi bảo vệ

| Nhu cầu | Nên dùng | Tránh nói |
|---|---|---|
| Chứng minh shortest path nông | BFS/UCS/IDS | "DFS tối ưu" |
| Solver chuẩn tốt nhất | A* với Manhattan hoặc Linear Conflict | "Greedy cũng tối ưu vì có heuristic" |
| Puzzle sâu, ít bộ nhớ hơn A* | IDA* | "BFS phù hợp puzzle sâu" |
| Chứng minh heuristic failure | Greedy, Hill Climbing preset | "Local search là solver đáng tin cậy" |
| Giải thích môi trường phức tạp | AND-OR, belief-state | "Đây là cùng bài toán chuẩn" |
| Giải thích CSP | CSP planning, AC-3, constraint graph | "CSP là cách tự nhiên nhất cho 15-puzzle" |
| So sánh hai AI | AI-vs-AI Tournament | "15-puzzle có đối thủ tự nhiên" |

## 13. Checklist vấn đáp

- Nêu PEAS trước khi chọn thuật toán.
- Phân biệt solver chuẩn, demo đối chiếu, extension và tournament/game demo.
- Với mọi path, hỏi: path có hợp lệ không, có tới goal không, có chứng minh tối ưu không.
- Với A*/IDA*, nhắc điều kiện heuristic admissible/consistent và giới hạn timeout/node cap.
- Với BFS/UCS/IDS, nhắc unit step cost là lý do optimality.
- Với DFS/Greedy/local search, nêu failure mode cụ thể.
- Với CSP/game/chance/tournament, nói rõ đây là đổi mô hình hoặc lớp đánh giá.
- Khi dùng benchmark/tournament, nêu seed, depth, heuristic, max nodes, timeout và caveat.

## 14. Câu trả lời ngắn cho giảng viên

| Câu hỏi | Câu trả lời gợi ý |
|---|---|
| Vì sao A* tối ưu? | Vì A* dùng `f=g+h`; với Manhattan/Linear Conflict admissible và consistent, goal đầu tiên được chọn từ frontier có cost tối ưu nếu không bị giới hạn tài nguyên. |
| Vì sao UCS giống BFS ở đây? | Vì mỗi slide có cost 1, nên thứ tự tăng `g(n)` của UCS trùng với thứ tự depth của BFS. |
| Vì sao Greedy không đủ? | Greedy chỉ tối thiểu hóa `h(n)`, bỏ qua cost đã đi `g(n)`, nên có thể chọn đường nhìn gần goal nhưng dài hơn. |
| Vì sao local search kẹt? | Nó tối ưu cục bộ, không giữ frontier toàn cục, nên local optimum/plateau có thể chặn đường tới goal. |
| Vì sao CSP không phải solver chính? | CSP planning cần biến theo time step và horizon; với 15-puzzle chuẩn, state-space search tự nhiên và trực tiếp hơn. |

## 15. Nguồn Học Thuật Đối Chiếu

- [AIMA, Constraint Satisfaction Problems](https://aima.cs.berkeley.edu/4th-ed/pdfs/newchap05.pdf): CSP `(X, D, C)`, backtracking, arc/path consistency và global constraints.
- [AIMA, AC-3 slides](https://aima.cs.berkeley.edu/slides-pdf/chapter05.pdf): queue of arcs, revise và domain reduction.
- [AIMA Search subsystem](https://aima.cs.berkeley.edu/lisp/doc/overview-SEARCH.html): Minimax và Alpha-Beta; Alpha-Beta giữ quyết định Minimax trên cùng cây/cutoff nhưng xét ít node hơn.
- [AIMA contents](https://aima.cs.berkeley.edu/contents.htm): no observation, partial observation, online search, adversarial search và games.

Các nguồn trên là chuẩn đối chiếu khái niệm. Contract executable của repo vẫn phải được xác minh bằng `SearchResult`, trace, path replay và test corpus; tài liệu không thay thế bằng chứng runtime.
| Vì sao có AI-vs-AI Tournament? | Để chấm điểm hai solver agent trên cùng puzzle bằng A* reference: đúng/tối ưu được điểm cao, đường dài hơn bị giảm, sai hoặc thất bại bị trừ điểm. |
