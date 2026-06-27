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
| GIF README | `scripts/readme_gif_renderer.py` | board, action, metrics, reason/caveat; profiles `hero/group/algorithm` |

## Search Tree Readability

- Readable Tree là view mặc định cho người học.
- Solution spine được phóng lớn hơn node phụ.
- Frontier/reached snapshot đặt cạnh tree để không phải suy luận từ DOT nhỏ.
- Graphviz vẫn có để audit edge parent-child.
- Với cây lớn, UI lọc solution path, expanded neighborhood hoặc first N nodes thay vì ép toàn bộ vào một hình nhỏ.

## GIF Theme Setting

Generator hỗ trợ hai palette:

```bash
python scripts/generate-readme-gifs.py --featured --profile all --theme light
python scripts/generate-readme-gifs.py --featured --profile all --theme dark
```

- `light`: ưu tiên đọc rõ trong GitHub README.
- `dark`: đồng bộ cảm giác app Streamlit.
- Hai theme dùng cùng solver/model evidence; chỉ đổi màu render.

## Tile Palette

Number tiles dùng neutral palette ổn định theo tile value band. Vị trí đúng chỉ dùng outline/indicator, không đổi màu toàn bộ tile theo hàng hiện tại. Điều này tránh lỗi “di chuyển là đổi màu” và làm UI chuyên nghiệp hơn.
