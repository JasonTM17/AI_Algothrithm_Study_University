# Hướng dẫn triển khai

## Sản phẩm được hỗ trợ

Sản phẩm chính thức là ứng dụng web Streamlit chạy từ `app.py`. Desktop window, EXE bundle hoặc service backend riêng không thuộc kiến trúc hiện tại.

## Chạy local

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
streamlit run app.py --server.port 8510
```

Health endpoint:

```text
http://127.0.0.1:8510/_stcore/health
```

Nếu dùng trong LAN lớp học:

```powershell
streamlit run app.py --server.port 8510 --server.address 0.0.0.0
```

Chỉ mở port trên mạng tin cậy. App không cần database hoặc secret.

## Chạy môi trường phát triển

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python -m compileall -q app.py core algorithms ui
python -m pytest tests -q
```

`requirements-dev.txt` đã include `requirements.txt`, nên không cần cài hai lần nếu dùng môi trường dev.

Nên kiểm tra trong venv riêng. `pip check` trên Python global có thể báo xung đột từ package ngoài repo; ví dụ một package user-site khác có thể yêu cầu version `playwright`, `pydantic` hoặc `httpx` không trùng dự án này.

## Triển khai hosted Streamlit

| Trường | Giá trị |
|---|---|
| Entrypoint | `app.py` |
| Python | 3.12 theo CI |
| Dependencies | `requirements.txt` |
| Secrets | Không yêu cầu |
| Database | Không yêu cầu |
| Health | `/_stcore/health` |

Giữ timeout, max nodes và trace cap trong UI. BFS, UCS và A* có thể tăng bộ nhớ rất nhanh trên puzzle sâu.

## CI và release

Workflow `.github/workflows/quality.yml` chạy trên push/pull request vào `master`:

1. Checkout source.
2. Setup Python 3.12.
3. `pip install -r requirements-dev.txt`.
4. `python -m compileall -q app.py core algorithms ui`.
5. `python -m pytest tests -q --cov=core --cov=algorithms --cov-report=term-missing --cov-fail-under=65`.
6. Khởi động Streamlit trên port 8510 và poll health endpoint.
7. Khi smoke test thủ công, xác nhận page title/body đúng `15-Puzzle AI`; đừng chỉ tin health endpoint nếu máy đang có Streamlit cũ chạy trên port khác.

Release công khai nên dùng đúng revision `master` đã qua workflow này.
