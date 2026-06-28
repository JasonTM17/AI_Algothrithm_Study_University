# Design guidelines

## Hướng thị giác

Ứng dụng là dashboard phòng thí nghiệm solver, không phải landing page marketing. Giao diện cần ưu tiên bằng chứng, khả năng đọc và tính nghiêm túc khi bảo vệ.

| Khu vực | Quy chuẩn |
|---|---|
| Nền | Graphite/off-black workbench, tránh gradient AI tím/xanh chung chung. |
| Accent | Copper/amber cho đo lường; green/red chỉ dùng cho valid/failure state. |
| Typography | Dễ đọc tiếng Việt; số liệu và trace dùng monospace khi cần. |
| Board | 15-puzzle board dạng vật lý, tile rõ, ô trống dễ nhận biết. |
| Cards | Dùng cho record/metric/algorithm role; không lồng card trong card. |
| Motion | Nhẹ, GPU-safe, hỗ trợ reduced-motion. |
| Emoji | Không dùng emoji trang trí trong nội dung học thuật chính. |

## Ưu tiên UX

- Luôn làm rõ start/goal contract trước khi chạy thuật toán.
- Hiển thị PEAS, role và guarantee gần nơi người dùng đọc kết quả.
- Tách solver chuẩn khỏi extension trong copy và layout.
- Trace, frontier, reached và search tree là evidence; không giấu sau prose dài.
- Compare phải ghi seed, heuristic, action order, timeout và max nodes.
- Advanced phải label rõ CSP/game/chance/belief-state là concept lab.
- Tournament phải show A* reference, score reason, legality status, excess cost và replay.
- Mobile không được vỡ layout bởi bảng trace hoặc sidebar.

## Quy tắc nội dung

- Text người dùng trong Streamlit nên đi qua `ui.localization`.
- Giữ tên thuật toán và công thức ở dạng chuẩn: BFS, UCS, IDS, A*, IDA*, `g(n)`, `h(n)`, `f(n)`.
- Không nói "Greedy tối ưu", "DFS tối ưu" hoặc "Minimax là solver tự nhiên của 15-puzzle".
- Không dùng runtime hoặc node count để quyết định winner khi chất lượng lời giải hòa.
- Khi thuật toán không complete hoặc không optimal, nói thẳng.
- Khi run bị timeout, node cap, depth limit hoặc horizon limit, UI phải thể hiện rõ certificate bị giới hạn.
- Với game/chance demos, gọi output là selected variation hoặc sample outcome path.
- Với AC-3, gọi output là exact-horizon path hoặc domain wipe-out cho horizon đã chọn.

## Layout theo tab

| Tab | Điểm cần thấy sớm |
|---|---|
| Play | Board, start/goal, solvability, A* replay controls, trajectory and evidence. |
| Run Algorithm | Algorithm group, role, controls, run certificate, trace/search tree. |
| Compare | Preset, list thuật toán, seed/limits, bảng kết quả, caveat so sánh. |
| Hand-Tracing | Frontier order, thao tác mở rộng, graph edge do người học chọn. |
| Theory | PEAS, taxonomy, group comparison, proof card, exam defense. |
| Advanced | Mode cards, caveat extension, result evidence và replay nếu có. |

## Kiểm tra chất lượng UI

- `tests/test_streamlit_app.py` là regression chính cho workflow Streamlit.
- `tests/test_academic.py` kiểm tra CSS/accessibility contract và nội dung học thuật.
- `tests/test_localization.py` kiểm tra localization key và hardcoded text.
- `tests/test_text_quality.py` kiểm tra lỗi mã hóa.
