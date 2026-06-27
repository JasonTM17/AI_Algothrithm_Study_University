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

## Vòng Audit Evidence 2026-06-27

Các lỗi đã tái hiện và sửa ở vòng này:

| Finding | Root cause | Contract sau sửa |
|---|---|---|
| GIF hiện `STEP 3/1`, `2/1` | Tử số lấy trace/frame index nhưng mẫu số luôn lấy số linear actions. | Progress phân loại `Move`, `Trace event`, `Evidence frame`, `Principal-variation ply` hoặc `Scored-agent move`; luôn có `0 <= current <= total`. |
| CSP model có `g/h/f` giả | Capture áp Manhattan/path-cost card cho mọi nhóm. | CSP chỉ hiện model status, arc checks/candidate states, trace events hoặc path claim. |
| Tournament xen kẽ start/goal | Fallback media dựng `[start, goal]` dù không phải trajectory. | Replay dùng path thật của agent đã được tournament chấm; nếu không có path thì board giữ nguyên start và ghi rõ unavailable. |
| AC-3 group GIF fail khó hiểu | Demo một-move dùng exact horizon `T=2`, nên parity wipe-out là đúng nhưng không phù hợp mục tiêu minh họa. | Featured/demo dùng `T=1` và solve đúng; test `T=2` vẫn khóa domain wipe-out để giữ bài học exact-horizon. |
| CSP theory nói quá implementation | Sáu mục CSP kế thừa wording generic, gồm MRV/forward checking không có trong bounded backtracking code. | Mỗi mục mô tả đúng executable model và caveat riêng. |
| Tree gọi partial path là solution | UI dùng chung nhãn `Solution Path` cho mọi `path_verified`, kể cả trajectory hợp lệ nhưng chưa tới goal. | Tree phân loại `solution` khi `goal_reached=True`, `trajectory` khi chỉ legal path; legend/metric/node label đổi theo contract. |

Nhánh `origin/update-search-tree-ui` đã là ancestor của `master`; merge trả `Already up to date`, không có commit riêng bị bỏ sót.
