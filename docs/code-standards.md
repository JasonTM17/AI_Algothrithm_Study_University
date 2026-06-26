# Chuẩn code và quy ước phát triển

## Nguyên tắc chung

- Giữ thay đổi nhỏ, đúng phạm vi và bám theo module hiện có.
- Không đổi hành vi solver nếu chỉ đang sửa tài liệu hoặc UI copy.
- Mọi claim về thuật toán phải đối chiếu với code thật trong `algorithms/`, `core/` và test tương ứng.
- Không thêm fake data, mock tạm hoặc shortcut để làm xanh test.
- Không commit secret, `.env`, token, credential hoặc dữ liệu cá nhân.
- Markdown dùng tiếng Việt có dấu, UTF-8 sạch, không để mojibake.

## Cấu trúc code

| Khu vực | Quy ước |
|---|---|
| `app.py` | Chỉ giữ entrypoint, session state cơ bản, sidebar và tab router. |
| `core/` | Logic domain, model dữ liệu, certificate, taxonomy, scoring. |
| `algorithms/` | Implement thuật toán, trả `SearchResult`, không render Streamlit. |
| `ui/` | Render Streamlit, gọi solver qua dispatcher, không nhúng logic thuật toán nặng. |
| `tests/` | Regression theo contract học thuật, UI, runtime và certificate. |
| `docs/` | Tài liệu evergreen, tên file kebab-case, mỗi file dưới 800 dòng. |

## Quy ước solver

- Solver nhận `start` và `goal`; không giả định goal mặc định nếu UI đã truyền goal tùy chỉnh.
- Solver trả `SearchResult` để UI có chung contract.
- Nếu path được trả về, `len(path) == len(actions) + 1`.
- Mỗi action phải là legal blank move theo `core.puzzle._move_blank`.
- `goal_state` phải được ghi kể cả khi fail, timeout hoặc model-success.
- `optimality_proven` không được set thủ công; để `SearchResult` phân loại từ `success`, `is_optimal`, `path_verified`, `goal_reached` và `termination_reason`.
- Timeout, node limit, depth limit hoặc horizon limit phải được phản ánh trong `message` hoặc `termination_reason`.

## Quy ước học thuật

| Claim | Điều kiện được nói |
|---|---|
| Path hợp lệ | `path_verified=True`. |
| Đã tới goal | `goal_reached=True` và state cuối bằng `goal_state`. |
| Tối ưu | `optimality_proven=True`; thuật toán optimal, certificate đủ và không bị resource limit. |
| Complete | Chỉ nói theo điều kiện lý thuyết và giới hạn thực thi hiện tại. |
| Extension | CSP/game/chance/belief-state phải được label là mở rộng hoặc concept lab. |
| Tournament | Chỉ là scoring layer, không phải môi trường đối kháng tự nhiên của 15-puzzle. |

## Localization và text

- Text người dùng trong Streamlit đi qua `ui.localization` khi có thể.
- Giữ thuật ngữ thuật toán, công thức, tên file, code và khóa cấu hình bằng tiếng Anh khi đó là định danh.
- Không dùng emoji trang trí trong nội dung học thuật chính.
- Test `tests/test_text_quality.py` và `tests/test_localization.py` là hàng rào cho lỗi mã hóa và hardcoded UI text.

## UI

- Board, trace, cards và bảng phải đọc được trên desktop và mobile.
- Tránh horizontal overflow ở viewport nhỏ.
- Nút điều khiển cần có trạng thái rõ ràng; không dựa vào gesture-only.
- Các demo mở rộng trong Advanced phải có caveat ngay gần kết quả.
- Runtime và node count chỉ là evidence mô tả; không dùng chúng để tạo winner khi chất lượng lời giải hòa.

## Test và validation

Chạy kiểm tra hẹp trước, rồi mở rộng khi đụng contract chung.

```bash
python -m compileall -q app.py core algorithms ui
python -m pytest tests -q
```

Khi sửa tài liệu, tối thiểu cần kiểm tra link nội bộ Markdown, lỗi mã hóa và các test text/localization liên quan. Khi sửa thuật toán hoặc UI, chạy test đúng nhóm bị ảnh hưởng và cân nhắc full suite.

## Git và tài liệu

- Không revert thay đổi của người khác trong worktree.
- Không để tài liệu mâu thuẫn với code; nếu chưa xác minh được thì viết ở mức intent cao hoặc bỏ claim.
- Tài liệu quan trọng trong `docs/`: PDR, code standards, summary, design, deployment, architecture, roadmap, test plan và academic reference.
