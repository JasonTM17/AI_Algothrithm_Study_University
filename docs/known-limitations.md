# Known Limitations

Các giới hạn dưới đây là chủ ý học thuật hoặc nợ kỹ thuật đã được ghi nhận. Không nên xóa caveat này khỏi README/UI.

## Thuật Toán

- DFS, Greedy và Local Search là demo đối chiếu; chúng có thể có legal path nhưng không có optimality certificate.
- AND-OR trả conditional plan. Nếu nondeterministic outcome support bật, mọi outcome được hỗ trợ cần có subplan trong depth limit.
- No/Partial Observation dùng hidden actual state để debug nhưng agent quyết định từ belief set.
- LRTA* là online learning demo, không phải solver offline tối ưu.
- CSP demos phụ thuộc horizon/model; model definition hoặc propagation không tự động là solution.
- Minimax/Alpha-Beta dùng MIN như worst-case robustness branch. 15-puzzle không có adversary tự nhiên.
- Expectimax phụ thuộc probability model đã chọn; expected outcome không phải worst-case guarantee.

## UI Và Media

- GIF README là evidence snapshot cố định theo seed/limit, không thay thế full UI trace.
- Graphviz tree có thể nhỏ nếu xem toàn bộ cây; Readable Tree là view ưu tiên.
- README nhúng 28 GIF nên tải nặng hơn bản ngắn. Gallery vẫn tồn tại để người đọc mở từng thuật toán riêng.
- Dark/Light GIF themes không đổi dữ liệu thuật toán, chỉ đổi palette render.

## Maintainability Debt

- `ui/styles.py`, `ui/components.py`, `ui/play_tab.py` và `algorithms/complex_env.py` còn lớn. Chỉ tách tiếp khi có refactor UI/algorithm riêng và tests khóa đủ behavior.
- `scripts/readme_gif_renderer.py` gom nhiều drawing helper để giữ pipeline đơn giản; nếu thêm renderer mới, nên tách thành `draw_board`, `draw_panel`, `draw_theme`.
- Không thêm heuristic lớn như pattern database nếu chưa có optimality corpus và docs caveat tương ứng.
