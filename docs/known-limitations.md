# Known Limitations

Các giới hạn dưới đây là chủ ý học thuật hoặc nợ kỹ thuật đã được ghi nhận. Không nên xóa caveat này khỏi README/UI.

## Thuật Toán

- DFS, Greedy và Local Search là demo đối chiếu; chúng có thể có legal path nhưng không có optimality certificate.
- AND-OR trả conditional plan. Mặc định UI dùng intended-only; nếu bật mọi deflection, mọi outcome hợp lệ đều cần subplan. Search có safety cap và phải báo `resource_limit`/`timeout`, không được diễn giải lần dừng này thành chứng minh không tồn tại plan.
- No/Partial Observation dùng hidden actual state để debug nhưng agent quyết định từ belief set.
- LRTA* là online learning demo, không phải solver offline tối ưu.
- CSP demos phụ thuộc horizon/model; model definition hoặc propagation không tự động là solution.
- Minimax/Alpha-Beta dùng MIN như worst-case robustness branch. 15-puzzle không có adversary tự nhiên.
- Expectimax phụ thuộc probability model đã chọn; expected outcome không phải worst-case guarantee.

## UI Và Media

- GIF README là evidence snapshot cố định theo seed/limit, không thay thế full UI trace.
- Readable Tree là view ưu tiên. Full Graphviz có zoom 75–300%, nút vừa khung và vùng cuộn để đọc node/cạnh mà không ép toàn cây vào một ảnh nhỏ.
- README nhúng 28 GIF nên tải nặng hơn bản ngắn. Gallery vẫn tồn tại để người đọc mở từng thuật toán riêng.
- `--theme` trong GIF generator hiện là metadata tương thích; hình ảnh phải đến từ live Streamlit browser capture.

## Maintainability Debt

- `ui/styles.py`, `ui/components.py`, `ui/play_tab.py` và `algorithms/complex_env.py` còn lớn. Chỉ tách tiếp khi có refactor UI/algorithm riêng và tests khóa đủ behavior.
- GIF pipeline phụ thuộc browser capture; nếu capture route đổi UI lớn, cần regenerate assets và kiểm manifest/readability.
- Không thêm heuristic lớn như pattern database nếu chưa có optimality corpus và docs caveat tương ứng.
