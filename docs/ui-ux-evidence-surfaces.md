# UI/UX Evidence Surfaces

App ưu tiên giao diện học thuật: người học phải thấy thuật toán đang làm gì, không chỉ thấy kết quả cuối.

## Surfaces Chính

| Surface | File chính | Evidence phải thấy |
|---|---|---|
| Play Solver Replay | `ui/play_tab.py`, `ui/path_solver_runner.py`, `ui/components.py` | 13 thuật toán tuyến tính có replay ảnh, runtime/số bước, frontier/reached hoặc candidate local |
| Play Group 6 Lab | `ui/group6_decision_lab.py`, `ui/group6_tree_viewer.py` | MAX/worst-case/CHANCE role frames, root value, pruning, probability, profiler và board ảnh không số |
| Run Algorithm | `ui/run_tab.py` | Selector 6 nhóm ở đầu, metrics, trace, trajectory, readable search tree |
| Compare | `ui/compare_tab.py`, `ui/image_algorithm_race.py` | Legal path, reached goal, optimality, runtime, steps, synchronized image replay, seed/action order |
| Theory | `ui/theory_tab.py` | Taxonomy, PEAS, pseudocode, transferable concept, caveat |
| Advanced | `ui/advanced_tab.py`, `ui/belief_controls.py` | known-tile matrix, AND-OR support mode, CSP workbench, Group 6 robustness |
| GIF README | `ui/web_gif_capture.py`, `scripts/generate-readme-gifs.py` | live browser board, action, metrics, truth status, reason/caveat; profiles `hero/group/algorithm` |

## Search Tree Readability

- Readable Tree là view mặc định cho người học.
- Solution spine được phóng lớn hơn node phụ.
- Frontier/reached snapshot đặt cạnh tree để không phải suy luận từ DOT nhỏ.
- Graphviz vẫn có để audit edge parent-child.
- Full Graphviz mở kèm zoom 75–300%, nút thu/phóng/vừa khung và vùng cuộn; mức mặc định 150% để nhãn node đọc được.
- Với cây lớn, UI lọc solution path, expanded neighborhood hoặc first N nodes thay vì ép toàn bộ vào một hình nhỏ.
- Tree không gọi mọi legal path là lời giải: nếu `path_verified=True` nhưng `goal_reached=False`, readable view dùng nhãn `Verified Trajectory` và màu hổ phách thay vì `Solution Path`.

## GIF Capture Contract

Generator chụp web thật, không dựng mockup:

```bash
python scripts/generate-readme-gifs.py --featured --profile all --theme dark
python scripts/generate-readme-gifs.py --all --profile algorithm --theme dark
```

- Frame source là Streamlit route `?capture_demo=...`.
- Capture tool là `agent-browser screenshot`.
- Manifest phải có `source=live_streamlit_browser_capture` và `web_run_status`.
- Chỉ legal trajectory mới dùng `Move x/y` và `g/h/f`.
- Conditional plan/model dùng `Trace event` hoặc `Evidence frame`; không dựng path giả.
- Local Search dùng local move và `h(n)`; Group 6 dùng ply/utility; Tournament dùng scored-agent move và điểm thật.
- CSP dùng arc checks, candidate states, trace/model status; `frontier/reached` chỉ hiện khi thuật toán thật sự có semantics đó.

## Tile Palette

Number tiles dùng neutral palette ổn định theo tile value band. Vị trí đúng chỉ dùng outline/indicator, không đổi màu toàn bộ tile theo hàng hiện tại. Điều này tránh lỗi “di chuyển là đổi màu” và làm UI chuyên nghiệp hơn.

## Play Image Algorithm Comparison

- Đổi ảnh mẫu trong sidebar cập nhật `image_tiles` ngay; benchmark state không bị mất nếu Start/Goal không đổi.
- Play hiển thị đủ 6 nhóm canonical, nhưng chỉ dùng runner chung cho 13 thuật toán có khả năng sinh quỹ đạo tuyến tính để benchmark trên cùng Start/Goal/limit.
- Bàn ảnh chính replay kết quả của thuật toán đang chọn, không phủ số khi người học muốn quan sát mảnh ảnh thuần.
- Biểu đồ thời gian và số bước chỉ xếp hạng `path_verified=True` và `goal_reached=True`.
- Legal partial trajectory, failure và model/conditional output được tách khỏi ranking; 6 nhóm/24 mục vẫn giữ trong taxonomy để học thuật không bị mất.

## Group 6 Decision / Policy Lab

- Policy Comparison dùng hai board độc lập để so chính sách, không gọi là hai người chơi cùng một bàn.
- Robustness Game Variant dùng một board chung: MAX cố giảm Manhattan, MIN là worst-case environment branch.
- Chance Outcome Lab chỉ dành cho Expectimax: MAX chọn intended action, CHANCE sample outcome theo probability/seed.
- Puzzle ảnh trong cả ba mode không phủ số; mỗi tick chỉ áp dụng tối đa một legal blank move.
- Cycle được đánh dấu thay vì gọi là tiến bộ.
- `Frontier/reached` hiển thị `N/A`; space proxy dùng generated nodes, captured trace/tree nodes, depth và prune count.
- Tree viewer có principal variation, evaluated events, pruned events, zoom, pan và fullscreen.
- Depth sweep chỉ so các run cùng fingerprint; expected value không được xếp trực tiếp với worst-case utility.
