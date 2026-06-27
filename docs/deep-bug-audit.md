# Deep Bug Audit

Ngày kiểm: 2026-06-27.

## Kết luận

Chưa phát hiện bug core nghiêm trọng kiểu solver trả path sai, success nhưng không tới goal, hoặc optimality certificate sai trong bộ kiểm hiện tại. Những rủi ro còn lại chủ yếu nằm ở UX evidence, wording và bảo trì file lớn.

## Static Scan

| Chủ đề | Kết quả | Quyết định |
|---|---|---|
| `unsafe_allow_html=True` | Có nhiều điểm trong UI vì Streamlit cần render board/cards/tree bằng HTML. | Chấp nhận có kiểm soát; message động phải escape trước khi đưa vào HTML. |
| `except Exception` | Có ở fallback UI/belief planner và một số boundary hiển thị lỗi. | Chấp nhận khi có trace/fallback reason; không swallow lỗi solver core âm thầm. |
| `path_verified` vs `goal_reached` | Đã tách trong `SearchResult`. | Test contract khóa legal path không đồng nghĩa solution. |
| Belief fallback | Trace có `planner_votes`, `fallback_votes`, `fallback_reason`. | Giữ, vì người học cần biết planner thật hay heuristic fallback. |
| Tournament scoring | Chỉ chấm meaningful khi path legal và goal reached; reference A* dùng làm optimal cost. | Giữ regression tests. |
| GIF docs | Manifest có profile, source, capture tool, `web_run_status`, learning goal, guarantee, caveat. | README/gallery render từ catalog để giảm lệch docs and false claims. |

## Verification Commands

```bash
python -m compileall -q app.py core algorithms ui scripts
python scripts/generate-readme-gifs.py --check --check-readability
python -m pytest tests -q --cov=core --cov=algorithms --cov-report=term-missing --cov-fail-under=65
git diff --check
```

## Follow-up Không Chặn Release

- Tách `ui/styles.py` theo component khi có vòng UI refactor.
- Tách `ui/web_gif_capture.py` nếu thêm nhiều browser-capture layouts hoặc theme thật.
- Thêm visual regression tự động so ảnh nếu repo chuyển sang CI có browser snapshot artifact.
