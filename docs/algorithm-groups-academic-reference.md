# Tham chiếu học thuật về các nhóm thuật toán

Tài liệu này dùng cho phần bảo vệ cuối kỳ của ứng dụng 15-Puzzle AI Algorithm Simulator. Nội dung bám theo code hiện tại trong `algorithms/`, `core/academic.py`, `core/academic_proofs.py`, `core/heuristics.py`, và cách UI tách "standard solver lab" khỏi "advanced concept lab".

## 1. Mô hình bài toán chuẩn

15-puzzle chuẩn trong repo là một bài toán tìm kiếm trạng thái đơn tác tử.

| Thuộc tính | Kết luận học thuật | Ý nghĩa trong app |
|---|---|---|
| Quan sát | Fully observable | Agent thấy toàn bộ 4x4 board. |
| Tính xác định | Deterministic | Một hành động hợp lệ luôn sinh đúng một trạng thái kế tiếp. |
| Tính động | Static | Board không tự đổi khi agent suy nghĩ. |
| Rời rạc | Discrete | State, action, path cost đều rời rạc. |
| Tuần tự | Sequential | Quyết định hiện tại ảnh hưởng các trạng thái sau. |
| Tác tử | Single-agent | Không có đối thủ trong bài toán chuẩn. |
| Chi phí | Unit step cost | Mỗi lần trượt ô trống có cost 1. |

PEAS chuẩn:

| PEAS | Diễn giải |
|---|---|
| Performance | Đến goal, ít bước, ít node mở rộng, ít bộ nhớ, runtime thấp. |
| Environment | Board 4x4, deterministic, fully observable, static, discrete, sequential, single-agent. |
| Actuators | Trượt ô trống theo L/R/U/D khi hợp lệ. |
| Sensors | Trạng thái board đầy đủ, vị trí ô trống, legal moves, heuristic estimates. |

Ranh giới quan trọng: CSP, AND-OR, no/partial observation, LRTA*, Minimax, Alpha-Beta, Expectimax là phần mở rộng học thuật. Chúng giúp trình bày nhiều mô hình AI hơn, nhưng không phải solver tự nhiên của 15-puzzle chuẩn. Caro/Gomoku mới là ví dụ đối kháng tự nhiên cho Minimax và Alpha-Beta.

## 2. Bảng phân loại nhanh

| Vai trò | Thuật toán | Có nên dùng làm solver chính? | Điểm bảo vệ |
|---|---|---:|---|
| Real Solver | BFS, UCS, IDS, A*, IDA* | Có | Dùng để chứng minh lời giải hợp lệ, tính đầy đủ, tối ưu trong điều kiện phù hợp. |
| Contrast Demo | DFS, Greedy Best-First, local search variants | Không | Dùng để chỉ ra trade-off, suboptimality, local optimum, plateau, hoặc thiếu guarantee. |
| Illustrative Extension | CSP, AND-OR, No Observation, Partial Observation, LRTA* | Không | Dùng để giải thích cách đổi mô hình bài toán và môi trường. |
| Stochastic/Game Demo | Minimax, Alpha-Beta, Expectimax, Caro/Gomoku | Chỉ Caro là game tự nhiên | Dùng để giải thích game tree, pruning, chance node, utility. |

Khi bảo vệ, nên nói rõ ba tầng bằng chứng:

1. Legal path certificate: mỗi cạnh trong path phải là một move hợp lệ.
2. Goal reachability: path kết thúc đúng goal hay chỉ là partial/selected/sample path.
3. Optimality certificate: thuật toán và heuristic có đủ điều kiện để chứng minh cost tối ưu hay không.

## 3. Uninformed Search

Nhóm uninformed search không dùng heuristic. Frontier được điều khiển bởi depth, stack/queue, hoặc path cost.

| Thuật toán | Frontier/evaluation | Complete | Optimal | Bộ nhớ | Ghi chú |
|---|---|---:|---:|---|---|
| BFS | FIFO queue, mở theo depth | Có nếu branching hữu hạn | Có với unit cost | Rất cao, thường O(b^d) | Dễ chứng minh shortest path nhưng nhanh hết bộ nhớ. |
| DFS | Stack/depth-first | Không đảm bảo trong graph/lúc giới hạn | Không | Thấp, thường O(bm) | Contrast demo: tiết kiệm bộ nhớ nhưng dễ đi sâu sai hướng. |
| UCS | Priority queue theo g(n) | Có với cost dương | Có | Cao | Với 15-puzzle unit cost, UCS tương đương BFS về thứ tự cost. |
| IDS | Lặp depth-limited search | Có với branching hữu hạn | Có với unit cost | Thấp, O(bd) | Tốt để giải thích đổi runtime lấy bộ nhớ thấp. |

Ký hiệu: `b` là branching factor, `d` là độ sâu lời giải ngắn nhất, `m` là depth tối đa đang xét.

### BFS

BFS mở rộng tất cả node depth `0`, rồi depth `1`, rồi depth `2`, ... Vì mỗi move cost 1, node goal đầu tiên được lấy ra ở depth nhỏ nhất. Đây là chứng minh tối ưu rất phù hợp cho bài bảo vệ.

Điểm yếu: frontier và reached set tăng theo hàm mũ. Với 15-puzzle sâu, BFS/UCS nhanh bị áp lực bộ nhớ dù guarantee đẹp.

### DFS

DFS đi sâu theo một nhánh trước. Nó có thể tìm lời giải nhanh nếu may mắn, nhưng không chứng minh shortest path. Trong app, DFS bị đặt depth/node/time limit để tránh treo UI; vì vậy càng không nên gọi DFS là complete solver thực tế.

Nên dùng DFS để so sánh: "low memory does not imply reliable optimal solving".

### UCS

UCS mở node có `g(n)` nhỏ nhất. Với mọi move cost 1, `g(n)` chính là depth, nên UCS và BFS có cùng bản chất tối ưu trong 15-puzzle chuẩn. UCS vẫn đáng trình bày vì là phiên bản tổng quát hơn khi action cost không bằng nhau.

### IDS

IDS chạy DFS giới hạn depth 0, rồi 1, rồi 2, ... Nó lặp lại một số node nhưng giữ bộ nhớ thấp. Với unit cost, goal đầu tiên tại depth `d` là lời giải tối ưu. Đây là lựa chọn tốt khi muốn chứng minh completeness/optimality mà vẫn nói được về memory efficiency.

## 4. Informed Search và heuristic

Nhóm informed search dùng heuristic `h(n)` để ước lượng cost còn lại.

| Thuật toán | Evaluation | Complete | Optimal | Vai trò |
|---|---|---:|---:|---|
| Greedy Best-First | Ưu tiên h(n) nhỏ nhất | Không đảm bảo trong thực hành graph search | Không | Contrast demo cho heuristic-only failure. |
| A* | f(n)=g(n)+h(n) | Có nếu heuristic admissible/consistent và tài nguyên đủ | Có | Solver tham chiếu chính. |
| IDA* | DFS theo ngưỡng f-cost tăng dần | Có trong điều kiện hữu hạn | Có với admissible heuristic | Solver tối ưu tiết kiệm bộ nhớ hơn A*. |

### Heuristic trong repo

| Heuristic | Định nghĩa | Quan hệ sức mạnh | Dùng để bảo vệ |
|---|---|---|---|
| Misplaced Tiles | Đếm tile sai vị trí, bỏ qua blank | Yếu nhất trong ba heuristic | Dễ giải thích admissible vì một tile sai cần ít nhất một move. |
| Manhattan Distance | Tổng khoảng cách hàng+cột tới goal | Mạnh hơn Misplaced | Chuẩn để chứng minh A* optimality. |
| Linear Conflict | Manhattan + 2 lần số conflict độc lập | Mạnh hơn Manhattan | Cho thấy heuristic mạnh hơn nhưng vẫn admissible. |

Admissible nghĩa là `h(n) <= h*(n)`, không bao giờ overestimate true remaining cost. Consistent nghĩa là `h(n) <= c(n,n') + h(n')` với mọi cạnh hợp lệ. Với unit cost, Manhattan consistent vì một slide chỉ làm tổng Manhattan đổi nhiều nhất 1.

### Greedy Best-First

Greedy chỉ nhìn `h(n)`, bỏ qua `g(n)`. Nó có thể chạy nhanh và đôi khi tìm đường tốt, nhưng không có chứng minh tối ưu. Teaching preset trong app dùng Greedy để chỉ ra trường hợp A* trả path ngắn hơn Greedy.

Câu bảo vệ nên dùng: "Greedy is a heuristic baseline, not an optimal solver. It may choose a state that looks close to goal while taking a longer route."

### A*

A* cân bằng cost đã đi và estimate còn lại bằng `f(n)=g(n)+h(n)`. Với heuristic admissible và consistent như Manhattan/Linear Conflict trong app, A* graph search có thể chứng minh optimal path khi không bị timeout/node cap.

Điểm cần nói rõ: nếu run bị timeout hoặc node cap, kết quả thực nghiệm không còn là optimality certificate, dù tính chất lý thuyết của A* vẫn đúng dưới giả định đủ tài nguyên.

### IDA*

IDA* dùng ngưỡng `f=g+h`, chạy depth-first cho các node không vượt ngưỡng, rồi tăng ngưỡng. Nó giảm memory so với A* vì không giữ toàn bộ frontier lớn. Đổi lại, nó có thể mở lại node nhiều lần.

Câu bảo vệ nên dùng: "IDA* keeps A*'s optimality condition under admissible heuristic but trades repeated work for lower memory."

## 5. Local Search

Local search không duy trì frontier đầy đủ của state-space search. Nó thường giữ một state hiện tại, một vài state tốt nhất, hoặc chấp nhận move xấu theo xác suất.

| Thuật toán | Cách chọn bước | Complete | Optimal | Failure mode |
|---|---|---:|---:|---|
| Simple Hill Climbing | Chọn cải thiện đầu tiên | Không | Không | Local optimum, plateau. |
| Steepest-Ascent Hill Climbing | Chọn neighbor tốt nhất | Không | Không | Vẫn kẹt nếu mọi neighbor không tốt hơn. |
| Stochastic Hill Climbing | Chọn cải thiện ngẫu nhiên | Không | Không | Phụ thuộc seed, vẫn kẹt. |
| Random-Restart Hill Climbing | Chạy lại từ nhiều điểm | Không tuyệt đối | Không | Tăng xác suất thành công nhưng không chứng minh tối ưu. |
| Local Beam Search | Giữ k state tốt nhất | Không | Không | Beam hẹp có thể mất nhánh lời giải. |
| Simulated Annealing | Có thể nhận move xấu theo temperature | Không hữu hạn | Không | Schedule không phù hợp có thể hội tụ kém. |

Trong 15-puzzle, local search hữu ích nhất ở vai trò giáo dục: chứng minh heuristic tốt không đủ nếu thuật toán chỉ tối ưu cục bộ. App dùng nhóm này làm contrast demo, không đưa vào bảng xếp hạng solver chuẩn.

## 6. CSP và map coloring

CSP mô hình hóa bài toán bằng biến `X`, miền giá trị `D`, và ràng buộc `C`. Với 15-puzzle, có thể mô hình hóa planning bằng biến theo time step, nhưng không tự nhiên bằng state-space search vì số biến/ràng buộc tăng lớn theo horizon.

| Thành phần | Trong app | Ý nghĩa học thuật |
|---|---|---|
| CSP Definition | Trình bày X, D, C | Giúp đổi cách nhìn từ path search sang constraint satisfaction. |
| Constraint Propagation | Thu hẹp domain | Giải thích pruning trước/sau assignment. |
| Path Consistency | Consistency bậc cao hơn arc consistency | Cho thấy kiểm tra ràng buộc giữa nhiều biến. |
| Global Constraints | Ví dụ AllDifferent | Tóm gọn nhiều ràng buộc nhị phân. |
| Backtracking Search | Demo planning có giới hạn | Trong app là minh họa bounded transition planning, không phải MRV/forward-checking đầy đủ cho 15-puzzle. |
| Min-Conflicts | Local repair | Hợp với N-Queens hơn 15-puzzle transition planning. |
| Constraint Graphs | Đồ thị biến-ràng buộc | Dùng để giải thích độ liên kết và độ khó. |
| Map Coloring | Thu Duc 2025/Australia | Ví dụ CSP tự nhiên hơn cho tô màu đồ thị. |

Map coloring trong app là ví dụ CSP tự nhiên: mỗi vùng là biến, domain là màu, hai vùng kề nhau không được cùng màu. Bản Thu Duc dùng dữ liệu offline 12 phường hiệu lực 2025-07-01, có trace MRV/degree/forward-checking. Tài liệu và UI không được ngụ ý đây là chứng nhận pháp lý bản đồ; nó là dataset học thuật offline.

## 7. Complex Environments

Nhóm này thay đổi giả định môi trường chuẩn.

| Thuật toán | Môi trường | Output | Ranh giới |
|---|---|---|---|
| AND-OR Search | Nondeterministic | Conditional plan | Không cần cho 15-puzzle deterministic chuẩn. |
| No Observation Search | Không quan sát state thật | Belief-state plan/demo | Sensor bị yếu đi có chủ ý. |
| Partially Observable Search | Quan sát một phần | Belief update trace | Không phải solver chuẩn. |
| LRTA* | Online search/learning | Path học từng bước | Có thể không tối ưu, dùng để bàn về agent online. |

Khi bảo vệ, dùng nhóm này để nói về PEAS: nếu sensor/transition/observability thay đổi, biểu diễn state và thuật toán cũng thay đổi. Không so sánh trực tiếp node count của nhóm này với A*/IDA* như thể cùng một bài toán.

## 8. Adversarial và stochastic search

15-puzzle chuẩn là single-agent, nên không có MIN player hoặc chance node tự nhiên. App vẫn có Minimax/Alpha-Beta/Expectimax dạng extension để giải thích mô hình game/chance, nhưng kết quả chỉ là selected variation hoặc sample outcome path, không phải chứng chỉ tối ưu puzzle.

| Thuật toán | Mô hình | Guarantee | Nên trình bày |
|---|---|---|---|
| Minimax | MAX/MIN game tree | Tối ưu theo utility nếu game tree/depth đúng và duyệt đủ | Khái niệm đối thủ tối ưu. |
| Alpha-Beta Pruning | Minimax có cắt tỉa | Giữ cùng root value với Minimax nếu điều kiện duyệt đủ | Pruning giảm node mà không đổi quyết định. |
| Expectimax | MAX/CHANCE tree | Tối ưu kỳ vọng theo xác suất mô hình | Ra quyết định khi có chance outcome. |
| Caro/Gomoku | Game hai người zero-sum tự nhiên | Depth-limited search | Ví dụ đúng nhất cho Minimax/Alpha-Beta trong app. |

Câu bảo vệ quan trọng: "Minimax trên 15-puzzle là artificial extension; Caro/Gomoku mới là môi trường đối kháng tự nhiên."

## 9. Cách chọn thuật toán khi bảo vệ

| Nhu cầu | Nên dùng | Tránh nói |
|---|---|---|
| Chứng minh shortest path nông | BFS/UCS/IDS | "DFS tối ưu" |
| Solver chuẩn tốt nhất | A* với Manhattan hoặc Linear Conflict | "Greedy cũng tối ưu vì có heuristic" |
| Puzzle sâu, ít bộ nhớ hơn A* | IDA* | "BFS phù hợp puzzle sâu" |
| Chứng minh heuristic failure | Greedy, Hill Climbing preset | "Local search là solver đáng tin cậy" |
| Giải thích môi trường phức tạp | AND-OR, belief-state, LRTA* | "Đây là cùng bài toán chuẩn" |
| Giải thích CSP | Map coloring, constraint graph | "CSP là cách tự nhiên nhất cho 15-puzzle" |
| Giải thích đối kháng | Caro/Gomoku, Minimax, Alpha-Beta | "15-puzzle có đối thủ" |

## 10. Checklist trả lời vấn đáp

- Nêu đúng PEAS trước khi chọn thuật toán.
- Phân biệt solver chuẩn, contrast demo, extension, game demo.
- Với mỗi path, hỏi: path có hợp lệ không, có đến goal không, có chứng minh tối ưu không.
- Với A*/IDA*, nêu heuristic admissible/consistent và giới hạn timeout/node cap.
- Với BFS/UCS/IDS, nêu unit step cost là lý do optimality.
- Với DFS/Greedy/local search, nêu failure mode cụ thể.
- Với CSP/game/chance, nói rõ đây là đổi mô hình, không phải solver tự nhiên của 15-puzzle chuẩn.
- Khi dùng benchmark, nêu seed, depth, heuristic, max nodes, timeout và caveat.

## 11. Bảng câu nói ngắn cho giảng viên

| Câu hỏi | Câu trả lời gợi ý |
|---|---|
| Vì sao A* tối ưu? | Vì A* dùng `f=g+h`; với Manhattan/Linear Conflict admissible và consistent, goal đầu tiên được chọn từ frontier có cost tối ưu nếu không bị giới hạn tài nguyên. |
| Vì sao UCS giống BFS ở đây? | Vì mọi slide có cost 1, nên thứ tự tăng `g(n)` của UCS trùng với thứ tự depth của BFS. |
| Vì sao Greedy không đủ? | Greedy chỉ tối thiểu hóa `h(n)`, bỏ qua cost đã đi `g(n)`, nên có thể chọn đường nhìn gần goal nhưng dài hơn. |
| Vì sao local search kẹt? | Nó tối ưu cục bộ, không giữ frontier toàn cục, nên local optimum/plateau có thể chặn đường tới goal. |
| Vì sao CSP không phải solver chính? | CSP planning cần biến theo time step và horizon; với 15-puzzle chuẩn, state-space search tự nhiên và trực tiếp hơn. |
| Vì sao có Caro trong repo? | Để minh họa đối kháng tự nhiên cho Minimax/Alpha-Beta; 15-puzzle chuẩn không có đối thủ. |

