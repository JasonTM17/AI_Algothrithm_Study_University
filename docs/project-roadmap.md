# Roadmap dự án

## Trạng thái hiện tại

Dự án đã có một web app Streamlit đầy đủ cho bài thi AI: Play, Run Algorithm, Compare, Step Trace, Hand-Tracing, Theory và Advanced. Các contract quan trọng đã có test: puzzle validity, heuristic, solver, custom goal, search tree evidence, CSP AC-3, Tournament, localization, text quality và Streamlit AppTest.

## Ưu tiên ngắn hạn

| Ưu tiên | Việc cần làm | Lý do |
|---|---|---|
| P0 | Giữ tài liệu tiếng Việt có dấu, đúng code hiện tại. | Đây là bề mặt chấm bài và onboarding chính. |
| P0 | Chạy full test suite trước release. | Solver/certificate sai sẽ phá tính đúng học thuật. |
| P1 | Rà lại UI mobile cho board, trace và table. | Lớp học có thể dùng màn hình nhỏ. |
| P1 | Chuẩn hóa thêm copy localization còn sót trong UI. | Tránh hardcoded text và lỗi mã hóa. |
| P1 | Tối ưu presentation của trace lớn. | Trace là evidence chính nhưng có thể nặng trên puzzle sâu. |

## Cải tiến trung hạn

| Hạng mục | Mô tả | Điều kiện chấp nhận |
|---|---|---|
| Benchmark presets rõ hơn | Thêm preset theo độ sâu và mục tiêu học thuật. | Mỗi preset ghi seed, expected difficulty và thuật toán khuyến nghị. |
| Report bảo vệ tốt hơn | Mở rộng grading report với bảng kết quả Compare/Tournament. | Report download được, không claim quá mức. |
| Documentation index | Thêm trang index nếu số lượng docs tiếp tục tăng. | Link nội bộ kiểm tra được, không trùng nội dung README. |
| UI trace filtering | Lọc event goal/generate/reject và node id. | Không đổi `TraceStep` contract nếu không cần. |
| Accessibility pass | Kiểm tra keyboard focus, contrast và responsive table. | AppTest hoặc kiểm tra thủ công ghi lại trong test plan. |

## Cải tiến dài hạn

| Hạng mục | Ghi chú |
|---|---|
| Solver nâng cao | Pattern database hoặc stronger heuristic chỉ nên thêm khi có test optimality/certificate đủ. |
| Larger puzzle variants | Chỉ mở rộng nếu tách rõ state contract khỏi 4x4 hiện tại. |
| Export artifact | Có thể xuất report HTML/PDF, nhưng không thay web app làm sản phẩm chính. |
| Docs site | Mintlify hoặc static docs chỉ cần khi README/docs hiện tại quá dài cho người chấm. |

## Rủi ro cần quản lý

- Gọi extension là solver chuẩn làm sai PEAS.
- Claim optimality khi run bị timeout hoặc node cap.
- So sánh node count giữa các họ thuật toán như cùng một đơn vị tuyệt đối.
- Dùng runtime để phân thắng thua khi hai path có cùng chất lượng.
- Sửa UI text nhưng không cập nhật localization/test.
- Tài liệu không dấu hoặc lỗi mã hóa làm giảm độ tin cậy khi bảo vệ.

## Definition of done cho release

```bash
python -m compileall -q app.py core algorithms ui
python -m pytest tests -q
```

Ngoài test, kiểm tra thủ công các tab Play, Run Algorithm, Compare, Step Trace, Hand-Tracing, Theory và Advanced trên một board nông để bảo đảm app trình bày đúng certificate và caveat.
