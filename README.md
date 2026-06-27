# 15-Puzzle AI Algorithm Simulator

[![Web quality](https://github.com/JasonTM17/AI_Algothrithm_Study_University/actions/workflows/quality.yml/badge.svg)](https://github.com/JasonTM17/AI_Algothrithm_Study_University/actions/workflows/quality.yml)
![Python 3.12](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-app-FF4B4B?logo=streamlit&logoColor=white)
![28 algorithms](https://img.shields.io/badge/AI-28%20algorithms-7FAF6F)

**Tác giả:** JasonTM17

Phòng thí nghiệm Streamlit để học và bảo vệ đồ án Trí tuệ nhân tạo bằng bài toán 15-puzzle. Dự án không chỉ chạy ra đáp án; nó làm rõ `state`, `action`, `frontier`, `reached`, heuristic, trace, certificate và ranh giới học thuật của từng nhóm thuật toán.

![A* image puzzle replay](docs/assets/readme/a-star-image-replay.gif)

GIF trên được sinh lại từ solver thật trong repo:

- Solver: `A* Search`
- Heuristic: `Manhattan Distance`
- Evaluation: `f(n)=g(n)+h(n)`
- Evidence: legal path, goal reached, optimality certificate
- Image puzzle replay: mảnh ảnh đi theo cùng `play_state` của thuật toán

## Chạy Nhanh

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

Kiểm tra phát triển:

```bash
pip install -r requirements-dev.txt
python -m compileall -q app.py core algorithms ui scripts
python -m pytest tests -q --cov=core --cov=algorithms --cov-report=term-missing --cov-fail-under=65
python scripts/generate-readme-gifs.py --check
```

## Bản Đồ 6 Nhóm

`ALGORITHM_GROUPS` là contract chính: 6 nhóm, 28 thuật toán.

| Nhóm | Vai trò học thuật | GIF |
|---|---|---|
| Uninformed Search | BFS, DFS, UCS, IDS: search không heuristic | ![Uninformed Search](docs/assets/readme/uninformed-search.gif) |
| Informed Search | Greedy, A*, IDA*: search có heuristic | ![Informed Search](docs/assets/readme/informed-search.gif) |
| Local Search | Hill Climbing, Beam, SA: xét candidate cục bộ | ![Local Search](docs/assets/readme/local-search.gif) |
| Complex Environments | AND-OR, belief, partial observation, LRTA* | ![Complex Environments](docs/assets/readme/complex-environments.gif) |
| CSP | Variables, domains, constraints, propagation | ![CSP](docs/assets/readme/csp.gif) |
| AI-vs-AI Tournament | Scoring, Minimax, Alpha-Beta, Expectimax | ![AI-vs-AI Tournament](docs/assets/readme/ai-vs-ai-tournament.gif) |

Gallery đủ 28 GIF riêng nằm ở [docs/algorithm-demo-gallery.md](docs/algorithm-demo-gallery.md). Mỗi GIF có manifest kiểm chứng tại [docs/assets/algorithm-demos/manifest.json](docs/assets/algorithm-demos/manifest.json).

## Ranh Giới Học Thuật

15-puzzle chuẩn là bài toán một tác tử, xác định, quan sát đầy đủ, tĩnh, rời rạc và tuần tự. Vì vậy cần tách rõ các claim:

| Loại | Thuật toán | Có phải solver chuẩn của 15-puzzle? | Cách đọc đúng |
|---|---|---:|---|
| Solver chuẩn | BFS, UCS, IDS, A*, IDA* | Có | State-space search, path legal, goal reached; A*/IDA* tối ưu khi heuristic admissible/consistent |
| Demo đối chiếu | DFS, Greedy, Local Search | Không nên claim chuẩn | Cho thấy trade-off, local optimum, randomness, hoặc suboptimal path |
| Extension giáo dục | CSP, AND-OR, No/Partial Observation, LRTA* | Không | Đổi mô hình bài toán: constraint, belief, nondeterminism, online learning |
| Robustness/game/chance | Minimax, Alpha-Beta, Expectimax | Không | 15-puzzle không có đối thủ tự nhiên; MIN là worst-case branch, CHANCE là stochastic model |
| Tournament | AI-vs-AI Tournament | Không | Lớp chấm điểm solver bằng evidence và A* reference |

Ba tầng chứng minh phải đọc riêng:

```text
Path legal       !=  Goal reached
Goal reached     !=  Optimal
Algorithm success !=  Solver chuẩn của 15-puzzle
```

## Cách Đọc Evidence

| Trường | Nghĩa |
|---|---|
| `path_verified` | Chuỗi action là legal blank moves |
| `goal_reached` | State cuối bằng goal đã chọn |
| `optimality_proven` | Có điều kiện lý thuyết và chứng cứ runtime để claim tối ưu |
| `frontier` | Node đang chờ xét |
| `reached` | State/record đã biết trong cấu trúc reached, best_g hoặc best_depth |
| `g(n)` | Path cost từ start tới node |
| `h(n)` | Heuristic estimate tới goal |
| `f(n)` | Priority của A*: `g(n)+h(n)` |
| `trace` | Bằng chứng từng bước: generate, expand, select, prune, accept/reject |

Search Tree có readable view mặc định: solution spine lớn, legend màu, current node, frontier/reached snapshot. Graphviz evidence vẫn có để audit parent-child edge khi cần.

## Workflow Thuyết Trình

1. **PEAS trước:** performance, environment, actuators, sensors.
2. **Play Puzzle:** chọn board số hoặc puzzle ảnh, bấm A* replay từng bước.
3. **Run Algorithm:** chọn nhóm ở đầu trang, chạy một thuật toán, đọc `frontier/reached/trace`.
4. **Compare:** so solver cùng seed, depth, timeout và heuristic.
5. **Theory:** giải thích guarantee, complexity, pseudocode và caveat.
6. **Advanced:** belief matrix dùng `_` cho unknown, AND-OR conditional plan, LRTA* online update.
7. **Tournament:** so điểm bằng legal path, optimal cost, excess cost, runtime và nodes.

Một câu bảo vệ ngắn:

> Với 15-puzzle chuẩn, em dùng A* vì bài toán là deterministic, fully observable, unit-cost state-space search. A* dùng `f(n)=g(n)+h(n)`, Manhattan Distance là admissible/consistent, nên nếu không timeout và path được verify thì kết quả có optimality certificate.

## Kiến Trúc Repo

```text
app.py                         Streamlit entrypoint và tab router
core/                          puzzle logic, metrics, heuristics, theory, tournament scoring
algorithms/                    uninformed, informed, local, complex, CSP, adversarial
ui/                            tabs, components, styles, localization, image puzzle
scripts/generate-readme-gifs.py verified GIF generator cho README/gallery
docs/                          tài liệu học thuật, kiến trúc, test plan, roadmap
docs/assets/readme/            7 GIF nổi bật trong README
docs/assets/algorithm-demos/   28 GIF riêng và manifest semantic
tests/                         solver, academic, AppTest, media/docs regression
.github/workflows/quality.yml  compile, pytest coverage, GIF manifest check, Streamlit smoke
```

## Tái Tạo GIF

```bash
python scripts/generate-readme-gifs.py --featured
python scripts/generate-readme-gifs.py --all
python scripts/generate-readme-gifs.py --check
```

Lệnh generator lấy frame từ solver/model thật với start, goal, seed, action order và giới hạn cố định. Không dựng state giả, không claim tối ưu khi manifest không có certificate.

## Tài Liệu

- [Algorithm demo gallery](docs/algorithm-demo-gallery.md)
- [Project overview/PDR](docs/project-overview-pdr.md)
- [Codebase summary](docs/codebase-summary.md)
- [System architecture](docs/system-architecture.md)
- [Algorithm test plan](docs/algorithm-test-plan.md)
- [Academic reference for groups](docs/algorithm-groups-academic-reference.md)
- [Project roadmap](docs/project-roadmap.md)
