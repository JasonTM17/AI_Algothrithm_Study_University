# Roadmap Dự Án

## Trạng Thái Hiện Tại

App đã có đủ workflow bảo vệ đồ án: Play, Run Algorithm, Compare, Step Trace, Hand-Tracing, Theory và Advanced. Contract học thuật hiện tại:

- 6 nhóm / 28 thuật toán.
- Puzzle số và puzzle ảnh replay theo state thật.
- Search tree có readable view và Graphviz evidence.
- Belief-state UI có known-tile matrix.
- Group 6 dùng framing worst-case robustness/chance.
- README là atlas học thuật, nhúng 28 GIF chạy thật.
- GIF pipeline có profile `hero/group/algorithm`, theme `light/dark`, manifest semantic và contact sheet.

## Ưu Tiên Ngắn Hạn

| Ưu tiên | Việc cần làm | Lý do |
|---|---|---|
| P0 | Giữ full suite và GIF manifest check xanh trước release. | Solver/certificate/media sai sẽ làm mất độ tin cậy học thuật. |
| P0 | Không để wording cũ quay lại: probability/adversary/solver chuẩn sai ngữ cảnh. | Người học dễ hiểu sai PEAS. |
| P1 | Tiếp tục kiểm visual Play/Run trên mobile. | Board, trace và tree là phần người dùng nhìn nhiều nhất. |
| P1 | Giữ tile number palette trung tính, stable by value. | Tránh cảm giác rối màu, thiếu chuyên nghiệp. |
| P1 | Dùng `--theme light` cho README GitHub, `--theme dark` khi cần demo đồng bộ app. | Hai môi trường xem có nền khác nhau. |

## Nợ Kỹ Thuật Được Ghi Nhận

| File | Nợ | Hướng xử lý |
|---|---|---|
| `ui/styles.py` | CSS lớn. | Tách theo tab/component khi có vòng UI refactor riêng. |
| `ui/components.py` | Board, trace, tree, cards cùng một file. | Tách renderer board/tree nếu cần sửa lớn. |
| `ui/play_tab.py` | Replay, scoring, image setup cùng module. | Tách state/replay helpers khi thêm mode mới. |
| `ui/localization.py` | Dictionary lớn. | Có thể tách namespace hoặc JSON khi copy tăng thêm. |
| `algorithms/complex_env.py` | Nhiều model giáo dục trong cùng file. | Chỉ tách khi signature và tests đủ ổn. |
| `scripts/readme_gif_renderer.py` | Drawing board/layout còn tập trung; panel semantics và theme đã tách riêng. | Chỉ tách `draw_board` khi thêm renderer thứ ba, tránh abstraction sớm. |

## Cải Tiến Trung Hạn

| Hạng mục | Điều kiện chấp nhận |
|---|---|
| Better trace filtering | Lọc generate/select/reject/prune không đổi `TraceStep` contract nếu chưa cần. |
| Report export nâng cao | Xuất Compare/Tournament evidence vào HTML/PDF, không claim quá mức. |
| Stronger heuristic | Chỉ thêm pattern database hoặc heuristic mới khi có optimality corpus và docs caveat. |
| Accessibility pass | Keyboard focus, contrast, responsive tables được kiểm AppTest/manual. |
| Visual regression CI | Lưu screenshot/contact sheet artifact nếu CI runner hỗ trợ browser artifact ổn định. |

## Definition Of Done Cho Release

```bash
python -m compileall -q app.py core algorithms ui scripts
python scripts/generate-readme-gifs.py --check --check-readability
python -m pytest tests -q --cov=core --cov=algorithms --cov-report=term-missing --cov-fail-under=65
git diff --check
```

Sau đó smoke thủ công các tab Play, Run Algorithm, Theory và Advanced trên desktop/mobile; kiểm README/Gallery mở đủ GIF.
