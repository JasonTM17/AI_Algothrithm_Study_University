# UI/UX Evidence Surfaces

App ưu tiên giao diện học thuật: người học phải thấy thuật toán đang làm gì, không chỉ thấy kết quả cuối.

## Surfaces Chính

| Surface | File chính | Evidence phải thấy |
|---|---|---|
| Play number/image | `ui/play_tab.py`, `ui/components.py` | A* step index, previous/next action, board hiện tại, `g/h/f`, frontier/reached |
| Run Algorithm | `ui/run_tab.py` | Selector 6 nhóm ở đầu, metrics, trace, trajectory, readable search tree |
| Compare | `ui/compare_tab.py` | Legal path, reached goal, optimality, runtime, nodes, seed/action order |
| Theory | `ui/theory_tab.py` | Taxonomy, PEAS, pseudocode, transferable concept, caveat |
| Advanced | `ui/advanced_tab.py`, `ui/belief_controls.py` | known-tile matrix, AND-OR support mode, LRTA* online step, Group 6 robustness |
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
