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

Ranh giới quan trọng: CSP, AND-OR, no/partial observation, LRTA*, Minimax, Alpha-Beta và Expectimax là phần mở rộng học thuật. AI-vs-AI Tournament là lớp chấm điểm giữa hai solver agent cùng giải 15-puzzle; nó không biến 15-puzzle thành môi trường có MIN player.

## 2. Phân loại nhanh

| Vai trò | Thuật toán | Có nên dùng làm solver chính? | Điểm bảo vệ |
|---|---|---:|---|
| Solver chuẩn | BFS, UCS, IDS, A*, IDA* | Có | Chứng minh lời giải hợp lệ, tính đầy đủ và tối ưu trong điều kiện phù hợp. |
| Demo đối chiếu | DFS, Greedy Best-First, local search variants | Không | Chỉ ra trade-off, suboptimality, local optimum, plateau hoặc thiếu guarantee. |
| Mở rộng minh họa | CSP, AND-OR, No Observation, Partial Observation, LRTA* | Không | Giải thích cách đổi mô hình bài toán, sensor hoặc environment. |
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
| Chỉ dùng như mô hình hóa CSP hoặc bằng chứng horizon nhỏ | CSP Definition, Constraint Propagation, Path Consistency, Global Constraints, Backtracking Search, Min-Conflicts, Constraint Graphs | Không phải solver chuẩn | CSP hợp lý để học `X, D, C`, AllDifferent và AC-3; không hợp lý nếu claim là hướng tự nhiên nhất để giải 15-puzzle sâu. |
| Chỉ dùng khi cố ý đổi sensor/environment | AND-OR, No Observation, Partial Observation, LRTA* | Không phải solver chuẩn | Các thuật toán này hợp lý cho nondeterministic, belief-state, partial sensor hoặc online agent; không nên so trực tiếp với A*/IDA* như cùng mô hình. |
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

## 5. Uninformed Search

Uninformed search không dùng heuristic. Frontier được điều khiển bởi depth, stack/queue hoặc path cost.

| Thuật toán | Frontier/evaluation | Complete | Optimal | Bộ nhớ | Ghi chú |
|---|---|---:|---:|---|---|
| BFS | FIFO queue, mở theo depth | Có nếu branching hữu hạn | Có với unit cost | `O(b^d)` | Dễ chứng minh shortest path nhưng nhanh hết bộ nhớ. |
| DFS | Stack/depth-first | Không đảm bảo trong graph/bounded run | Không | Thấp | Demo đối chiếu: tiết kiệm bộ nhớ nhưng dễ đi sâu sai hướng. |
| UCS | Priority queue theo `g(n)` | Có với cost dương | Có | Cao | Với 15-puzzle unit cost, gần BFS theo cost layer. |
| IDS | Lặp depth-limited search | Có với branching hữu hạn | Có với unit cost | `O(bd)` | Đổi runtime lấy bộ nhớ thấp. |

`b` là branching factor, `d` là độ sâu lời giải ngắn nhất, `m` là depth tối đa đang xét.

## 6. Informed Search và heuristic

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

## 7. Local Search

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
| Local optimum | Không neighbor nào tốt hơn current nhưng chưa tới goal. | Teaching preset và result caveat. |
| Plateau/shoulder | Nhiều neighbor có cùng `h`, strict improvement không có hướng đi. | Theory và local-search trace. |
| Ridge | Cần đi ngang hoặc tạm thời xấu hơn mới tốt về sau. | Simulated Annealing có xác suất nhận move xấu khi temperature còn cao. |
| Randomness dependence | Seed khác nhau sinh trajectory khác nhau. | Stochastic HC, Random-Restart HC, Simulated Annealing. |

## 8. CSP trong 15-puzzle

CSP mô hình hóa bài toán bằng biến `X`, miền giá trị `D` và ràng buộc `C`. Với 15-puzzle, có thể mô hình planning bằng biến theo time step, nhưng không tự nhiên bằng state-space search vì số biến/ràng buộc tăng theo horizon.

| Thành phần | Trong app | Ý nghĩa học thuật |
|---|---|---|
| CSP Definition | Trình bày `X[t][p]`, `A[t]`, initial, goal, AllDifferent, transition, legal move | Đổi cách nhìn từ path search sang constraint satisfaction. |
| Constraint Propagation | AC-3 trên chuỗi state `S[0]..S[T]` | Thu hẹp domain; trả exact-horizon path hoặc domain wipe-out. |
| Path Consistency | Consistency bậc cao hơn arc consistency | Kiểm tra ràng buộc giữa nhiều biến. |
| Global Constraints | AllDifferent | Tóm gọn nhiều ràng buộc nhị phân. |
| Backtracking Search | Bounded transition planning | Minh họa DFS theo horizon, không phải solver chính. |
| Min-Conflicts | Local repair trên tile placement | Hợp với N-Queens hơn 15-puzzle transition planning. |
| Constraint Graphs | Đồ thị biến-ràng buộc | Giải thích liên kết và độ phình. |

Backtracking CSP trong app dùng heuristic value ordering. Không gọi là MRV/LCV hay forward checking đầy đủ vì code không cài đặt đầy đủ các heuristic CSP đó.

AC-3 executable dùng biến trạng thái đầy đủ để tránh bộ ràng buộc `X[t][p]` quá lớn trong demo. Hai đầu mút bị cố định bởi start và goal; mỗi cặp state liên tiếp phải cách nhau đúng một legal blank move. Kết quả chỉ cho horizon `T` đã chọn, không tự động chứng minh đường ngắn nhất toàn cục.

## 9. Complex Environments

Trong Run Algorithm, AND-OR có thể xuất hiện bằng alias để khớp đề cương. Đây chỉ là alias UI; taxonomy vẫn là `Complex Environments` và vai trò vẫn là `Illustrative Extension`.

| Thuật toán | Môi trường | Output | Ranh giới |
|---|---|---|---|
| AND-OR Search | Nondeterministic | Conditional plan | Không cần cho 15-puzzle deterministic chuẩn. |
| No Observation Search | Không quan sát state thật | Belief-state action demo | Sensor bị yếu đi có chủ ý. |
| Partially Observable Search | Quan sát một phần | Actual path plus belief/observation trace | Không phải solver chuẩn. |
| LRTA* | Online search/learning | Path học từng bước | Có thể không tối ưu; dùng để bàn về agent online. |

Nếu sensor, transition hoặc observability thay đổi, biểu diễn state và thuật toán cũng thay đổi. Không so sánh node count của nhóm này với A*/IDA* như thể cùng một bài toán.

## 10. AI-vs-AI Tournament và game/chance extension

15-puzzle chuẩn là single-agent. Tournament trong app là lớp chấm điểm giữa hai agent giải cùng board, không phải đối kháng tự nhiên trong môi trường puzzle.

| Thành phần | Mô hình | Guarantee | Nên trình bày |
|---|---|---|---|
| AI-vs-AI Tournament | Hai solver agent chạy trên cùng start/goal | Điểm dựa trên A* reference optimal certificate | So sánh chất lượng lời giải, failure, runtime, nodes. |
| Minimax | MAX/MIN game tree extension | Tối ưu theo utility nếu game tree/depth đúng và duyệt đủ | Khái niệm đối thủ tối ưu. |
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

## 11. Cách chọn thuật toán khi bảo vệ

| Nhu cầu | Nên dùng | Tránh nói |
|---|---|---|
| Chứng minh shortest path nông | BFS/UCS/IDS | "DFS tối ưu" |
| Solver chuẩn tốt nhất | A* với Manhattan hoặc Linear Conflict | "Greedy cũng tối ưu vì có heuristic" |
| Puzzle sâu, ít bộ nhớ hơn A* | IDA* | "BFS phù hợp puzzle sâu" |
| Chứng minh heuristic failure | Greedy, Hill Climbing preset | "Local search là solver đáng tin cậy" |
| Giải thích môi trường phức tạp | AND-OR, belief-state, LRTA* | "Đây là cùng bài toán chuẩn" |
| Giải thích CSP | CSP planning, AC-3, constraint graph | "CSP là cách tự nhiên nhất cho 15-puzzle" |
| So sánh hai AI | AI-vs-AI Tournament | "15-puzzle có đối thủ tự nhiên" |

## 12. Checklist vấn đáp

- Nêu PEAS trước khi chọn thuật toán.
- Phân biệt solver chuẩn, demo đối chiếu, extension và tournament/game demo.
- Với mọi path, hỏi: path có hợp lệ không, có tới goal không, có chứng minh tối ưu không.
- Với A*/IDA*, nhắc điều kiện heuristic admissible/consistent và giới hạn timeout/node cap.
- Với BFS/UCS/IDS, nhắc unit step cost là lý do optimality.
- Với DFS/Greedy/local search, nêu failure mode cụ thể.
- Với CSP/game/chance/tournament, nói rõ đây là đổi mô hình hoặc lớp đánh giá.
- Khi dùng benchmark/tournament, nêu seed, depth, heuristic, max nodes, timeout và caveat.

## 13. Câu trả lời ngắn cho giảng viên

| Câu hỏi | Câu trả lời gợi ý |
|---|---|
| Vì sao A* tối ưu? | Vì A* dùng `f=g+h`; với Manhattan/Linear Conflict admissible và consistent, goal đầu tiên được chọn từ frontier có cost tối ưu nếu không bị giới hạn tài nguyên. |
| Vì sao UCS giống BFS ở đây? | Vì mỗi slide có cost 1, nên thứ tự tăng `g(n)` của UCS trùng với thứ tự depth của BFS. |
| Vì sao Greedy không đủ? | Greedy chỉ tối thiểu hóa `h(n)`, bỏ qua cost đã đi `g(n)`, nên có thể chọn đường nhìn gần goal nhưng dài hơn. |
| Vì sao local search kẹt? | Nó tối ưu cục bộ, không giữ frontier toàn cục, nên local optimum/plateau có thể chặn đường tới goal. |
| Vì sao CSP không phải solver chính? | CSP planning cần biến theo time step và horizon; với 15-puzzle chuẩn, state-space search tự nhiên và trực tiếp hơn. |
| Vì sao có AI-vs-AI Tournament? | Để chấm điểm hai solver agent trên cùng puzzle bằng A* reference: đúng/tối ưu được điểm cao, đường dài hơn bị giảm, sai hoặc thất bại bị trừ điểm. |
