# 15-Puzzle AI Algorithm Simulator

Ung dung Streamlit dung cho do an / bai thi cuoi ky Tri tue nhan tao. Repo nay mo phong 15-puzzle de giai thich PEAS, khong gian trang thai, heuristic, trace tim kiem, bang so sanh thuat toan, va cac mo hinh mo rong nhu CSP, belief-state, LRTA*, Minimax, Alpha-Beta, Expectimax, AI-vs-AI Tournament.

Muc tieu quan trong nhat: noi dung phai dung ve hoc thuat. 15-puzzle chuan la bai toan single-agent, deterministic, fully observable. Vi vay BFS, UCS, IDS, A*, IDA* la solver chuan; DFS, Greedy, local search la demo doi chieu; CSP/game/chance/belief-state la mo rong giao duc, khong phai solver tu nhien cua 15-puzzle chuan.

## Quick Start

```bash
pip install -r requirements.txt
streamlit run app.py
```

Kiem tra nhanh tren Windows PowerShell:

```powershell
$files = @('app.py') + (Get-ChildItem core,algorithms,ui -Filter *.py | ForEach-Object { $_.FullName })
python -m py_compile @files
python -m pytest tests/ -q
```

Dung day du moi truong dev:

```bash
pip install -r requirements-dev.txt
python -m compileall -q app.py core algorithms ui
python -m pytest tests/ -q
```

## Cach Di Qua Dashboard Khi Bao Ve

| Buoc | Tab | Nen trinh bay |
|---|---|---|
| 1 | Play | Trang thai start/goal, co the chinh tu sidebar hoac khung Start / Goal tren cac trang chay thuat toan; o trong `0`, move hop le, solvability theo parity. |
| 2 | Run Algorithm | Chon mot thuat toan, giai thich frontier, reached set, trace, `g/h/f`, certificate; AND-OR nam trong alias `Nhom 3 - Moi truong phuc tap` de chay demo conditional plan. |
| 3 | Compare | So sanh nhieu solver bang cung seed, depth, timeout, max nodes, heuristic. |
| 4 | Theory/PEAS | Bao ve PEAS, role cua tung thuat toan, guarantee, proof card. |
| 5 | Hand-Tracing | Tap mo rong node thu cong, kiem tra thu tu frontier va cay Graphviz. |
| 6 | Advanced | Chay CSP, complex environments, game/chance, AI-vs-AI Tournament nhu concept lab. |

## Mo Hinh Bai Toan 15-Puzzle

| Thanh phan | Mo ta |
|---|---|
| State | Tuple 16 phan tu, la hoan vi cua `0..15`; `0` la o trong. |
| Goal mac dinh | `(1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 0)`. |
| Action | `L`, `R`, `U`, `D`: truot o trong sang trai/phai/len/xuong neu hop le. |
| Transition | Deterministic: cung state va action hop le luon cho dung mot next state. |
| Cost | Moi move co cost `1`, nen path cost bang so action. |
| Solvability | Hai state reach duoc nhau neu parity class bang nhau. Code dung `(inversions + blank_row_from_bottom) % 2`. |
| Certificate | Path hop le khi moi action ap dung len state truoc sinh dung state sau va state cuoi bang goal. |

## PEAS

| PEAS | Dien giai trong bai 15-puzzle |
|---|---|
| Performance | Den goal, it buoc, it node expanded/generated, it bo nho, runtime thap. |
| Environment | Board 4x4, fully observable, deterministic, static, discrete, sequential, single-agent. |
| Actuators | Truot o trong theo `L/R/U/D` khi action hop le. |
| Sensors | Toan bo board, vi tri o trong, legal moves, heuristic estimate. |

## Phan Loai Thuat Toan

| Vai tro | Thuat toan | Cach noi khi bao ve |
|---|---|---|
| Real Solver | BFS, UCS, IDS, A*, IDA* | Co the dung de giai 15-puzzle chuan; co guarantee neu khong bi timeout/node cap va dieu kien ly thuyet thoa. |
| Contrast Demo | DFS, Greedy Best-First, local search variants | Dung de chi trade-off, thieu optimality, local optimum, plateau, randomness. |
| Illustrative Extension | CSP, AND-OR, No Observation, Partial Observation, LRTA* | Doi mo hinh bai toan/moi truong de hoc them AI, khong phai solver tu nhien nhat. |
| Tournament/Game-Chance | AI-vs-AI Tournament, Minimax, Alpha-Beta, Expectimax | Tournament la scoring layer; Minimax/Alpha-Beta/Expectimax la game/chance extension. |

## Heuristic Trong Repo

| Heuristic | Cong thuc/y tuong | Uu diem | Nhuoc diem |
|---|---|---|---|
| Misplaced Tiles | Dem tile sai vi tri, bo qua blank. | Don gian, admissible, de giai thich. | Yeu, khong biet tile cach goal bao xa. |
| Manhattan Distance | Tong `abs(row-row_goal)+abs(col-col_goal)` cua moi tile, bo qua blank. | Admissible, consistent, rat hop voi 15-puzzle. | Van co the mo rong nhieu node voi puzzle sau. |
| Linear Conflict | Manhattan + `2 * so conflict doc/lien quan` hop le. | Manh hon Manhattan, van admissible/consistent trong repo. | Tinh phuc tap hon; loi ich phu thuoc state. |

Quy tac quan trong: A* va IDA* chi co optimality certificate khi heuristic admissible, path verified, goal reached, va run khong bi dung do resource limit.

## Nhom 1 - Uninformed Search

| Thuat toan | Cach chay | Do phuc tap ly thuyet | Uu diem trong 15-puzzle | Nhuoc diem/caveat |
|---|---|---|---|---|
| BFS | Dung FIFO queue, mo node theo tung depth. | Time `O(b^d)`, space `O(b^d)`. | Complete va optimal voi unit cost; de chung minh shortest path. | Rat ton bo nho; khong phu hop puzzle sau. |
| DFS | Dung stack/depth-first voi `max_depth`; code co reached set. | Time `O(b^m)`, space `O(bm)` neu de quy/stack theo path. | It bo nho, de minh hoa tim kiem sau. | Khong optimal; khong complete khi depth limit thap; co the di sai huong rat lau. |
| UCS | Priority queue theo `g(n)`; tie-breaker co FIFO/LIFO/Min-g/Max-g. | Voi unit cost gan BFS; tong quat phu thuoc cost toi uu `C*`. | Complete, optimal voi cost duong; trong 15-puzzle tuong duong BFS ve cost layer. | Ton bo nho cao; vi moi move cost 1 nen khong them nhieu gia tri so voi BFS. |
| IDS | Lap Depth-Limited Search tu depth 0 den `max_depth`. | Time `O(b^d)`, space `O(bd)`. | Complete va optimal voi unit cost; tiet kiem bo nho hon BFS. | Expand lai node nhieu lan; bi gioi han boi `max_depth`, timeout, max nodes. |

## Nhom 2 - Informed Search

| Thuat toan | Ham danh gia | Do phuc tap | Uu diem trong 15-puzzle | Nhuoc diem/caveat |
|---|---|---|---|---|
| Greedy Best-First | Uu tien `h(n)` nho nhat, bo qua `g(n)`. | Worst-case van exponential; space cao do priority queue. | Thuong nhanh tren demo nong; rat tot de so voi A*. | Khong optimal; khong dam bao complete trong thuc hanh bounded graph search; de bi heuristic danh lua. |
| A* | Uu tien `f(n)=g(n)+h(n)`. | Worst-case exponential time/space, nhung heuristic tot giam node. | Solver tham chieu chinh; complete/optimal voi admissible consistent heuristic va tai nguyen du. | Ton RAM do frontier/reached; timeout/node cap lam mat certificate thuc nghiem. |
| IDA* | DFS lap theo threshold `f`; threshold moi la `f` nho nhat bi cat. | Time exponential; space `O(bd)`. | Chat luong gan A* voi bo nho thap; phu hop puzzle sau hon BFS/A*. | Re-expand node nhieu lan; cham neu heuristic yeu hoac threshold tang nho. |

## Nhom 3 - Local Search

Local search khong giu frontier day du. No toi uu truc tiep heuristic cua current state/beam, nen phu hop lam demo failure hon lam solver chuan.

| Thuat toan | Cach chon buoc | Uu diem | Nhuoc diem trong 15-puzzle |
|---|---|---|---|
| Simple Hill Climbing | Chon neighbor dau tien co `h` tot hon current. | Don gian, trace de hieu. | Ket local optimum/plateau; khong complete, khong optimal. |
| Steepest-Ascent Hill Climbing | Xet tat ca neighbor, chon neighbor co `h` nho nhat. | Tot hon simple neu neighbor tot nam sau trong action order. | Van ket neu khong co neighbor tot hon; khong nhin duong dai hon tam thoi xau. |
| Stochastic Hill Climbing | Random trong cac neighbor tot hon. | Giai thich vai tro seed/randomness; co the tranh mot vai tie xau. | Van chi nhan move tot hon, van ket; ket qua phu thuoc seed. |
| Random-Restart Hill Climbing | Restart bang random walk hop le roi leo doi lai. | Tang xac suat thoat diem xau; demo restarts ro. | Khong chung minh solution/optimality; nhieu restart van co the that bai. |
| Local Beam Search | Giu `k` state tot nhat, sinh neighbor cua toan beam. | Manh hon single-state hill climbing; memory `O(k)`. | Beam hep co the loai mat path dung; khong complete/optimal. |
| Simulated Annealing | Chap nhan move xau voi xac suat `exp(-delta/T)`, `T` giam dan. | Co co che thoat local optimum; minh hoa temperature schedule. | Khong co finite optimality guarantee; schedule/seed anh huong manh. |

## Nhom 4 - Complex Environments

Day la cac mo hinh mo rong de hoc agent trong moi truong khac. Khong nen so sanh truc tiep voi A*/IDA* nhu cung mot bai toan.

Trong Run Algorithm, AND-OR duoc dua ra bang alias `Nhom 3 - Moi truong phuc tap` theo de cuong. Taxonomy hoc thuat van giu la `Complex Environments / Illustrative Extension`, khong phai Local Search.

| Thuat toan | Mo hinh | Output | Uu diem hoc thuat | Caveat |
|---|---|---|---|---|
| AND-OR Search | Moi truong nondeterministic: action co nhieu outcome. | Conditional plan `IF outcome THEN plan`. | Giai thich OR node la agent chon, AND node la moi outcome phai xu ly. | 15-puzzle chuan deterministic nen khong can AND-OR. |
| No Observation Search | Agent khong nhin thay state thuc, giu belief set. | Belief-action trace/representative path. | Cho thay sensor yeu lam state thanh tap kha nang. | Demo bounded, khong phai solver chuan. |
| Partially Observable Search | Agent thay blank + tile quanh blank, update belief bang observation. | Actual path + belief trace. | Minh hoa filtering va partial sensor. | Ket qua phu thuoc belief setup/seed; khong optimal. |
| LRTA* | Online learning: di tung buoc va cap nhat bang `H(state)`. | Path hoc online. | Giai thich agent khong lap ke hoach toan cuc truoc. | Co the lap/di dai; khong bang A* offline ve optimality. |

## Nhom 5 - CSP

15-puzzle co the mo hinh nhu CSP planning, nhung state-space search tu nhien hon. CSP can bien theo time step va horizon nen tang rat nhanh.

| Thuat toan/demo | Cach mo hinh | Uu diem | Nhuoc diem/caveat |
|---|---|---|---|
| CSP Definition | Bien `X[t][p]` la tile o position `p`, action `A[t]`; rang buoc initial, goal, AllDifferent, transition, legal move. | Day du de giai thich `X, D, C`. | Chua phai solver; so bien tang theo horizon. |
| Constraint Propagation | AC-3 tren chuoi state `S[0]..S[T]`, endpoint co dinh, canh la mot blank move hop le. | Co executable evidence: exact-horizon path hoac domain wipe-out. | Chi dung voi horizon `T` da chon; khong chung minh shortest path toan cuc. |
| Path Consistency | Kiem tra tinh nhat quan cua bo ba bien. | Giai thich consistency cao hon arc consistency. | Rat ton chi phi voi domain lon; chu yeu la minh hoa. |
| Global Constraints | AllDifferent tren 16 tile moi time step. | Manh hon nhieu rang buoc `!=` nhi phan rieng le. | Van khong giai quyet du transition planning sau. |
| Backtracking Search | DFS bounded transition planning, neighbor order theo heuristic. | Co the tim path nho trong horizon nho; de noi ve backtracking. | Khong dung MRV/forward checking day du; fail khong phai proof unsolvable. |
| Min-Conflicts | Local repair tren tile-placement conflicts. | Huu ich de so sanh voi N-Queens/min-conflicts. | Swap tile khong phai legal blank move; khong la solver 15-puzzle hop le. |
| Constraint Graphs | Bieu dien bien va rang buoc theo time horizon. | Giup thay vi sao planning CSP phinh to. | Artifact giai thich, khong sinh loi giai. |

## Nhom 6 - AI-vs-AI, Game Tree, Chance

15-puzzle khong co doi thu tu nhien. Nhom nay ton tai de bao ve them kien thuc game/chance va cach cham diem hai solver.

| Thanh phan | Y tuong | Uu diem | Nhuoc diem/caveat |
|---|---|---|---|
| AI-vs-AI Tournament | Hai solver chay cung start/goal; A* lam reference optimal cost. | Cham diem cong bang theo legal path, optimality, failure, invalid path; co replay dong bo. | La scoring layer, khong bien PEAS thanh adversarial. |
| Minimax | MAX muon giam heuristic/den goal, MIN muon lam xau utility. | Giai thich game 2 nguoi zero-sum va depth-limited tree. | Mo hinh nhan tao; selected variation khong la optimal certificate cho puzzle chuan. |
| Alpha-Beta Pruning | Minimax co `alpha`, `beta`, cat cac nhanh khong anh huong root value neu dieu kien du. | Giam node so voi Minimax, nhat la action ordering tot. | Worst-case van `O(b^m)`; chi dung trong game-tree model. |
| Expectimax | MAX chon action, CHANCE lay expected utility theo probability. | Giai thich ra quyet dinh khi outcome ngau nhien. | Can xac suat dung; kho prune nhu alpha-beta; path tra ve la sample/variation. |

Tournament scoring trong code:

| Ket qua agent | Diem |
|---|---:|
| Path hop le, toi goal, cost bang optimal cost | `+100` |
| Path hop le, toi goal, cost dai hon optimal | `max(10, round(100 * optimal_cost / actual_cost))` |
| Path hop le nhung chua toi goal | `-10` |
| Timeout/resource limit/no path | `-20` |
| Exception/path invalid/action sai/state mismatch | `-50` |

## Cach Doc Ket Qua Mot Run

| Truong | Y nghia |
|---|---|
| `success` | Algorithm bao thanh cong theo mo hinh cua no. Voi extension, success co the la model-success, khong nhat thiet la goal puzzle. |
| `path_verified` | Moi action trong path la legal blank move. |
| `goal_reached` | State cuoi bang goal duoc chon. |
| `optimality_proven` | Chi true khi success, path legal, goal reached, algorithm optimal, termination la `goal`. |
| `nodes_expanded` | So node/state duoc mo rong; giua cac ho thuat toan khong luon so sanh 1-1. |
| `nodes_generated` | So candidate sinh ra. |
| `max_frontier_size` | Dinh bo nho frontier. BFS/A* thuong cao, IDS/IDA* thap hon. |
| `trace` | Bang evidence: action, parent, frontier/reached, `g/h/f`, reason. Trace co gioi han de UI khong cham. |

## Project Structure

```text
app.py                         Streamlit entrypoint va tab router
core/                          puzzle logic, heuristic, metrics, taxonomy, tournament scoring
algorithms/                    uninformed, informed, local, CSP, complex, adversarial algorithms
ui/                            Streamlit tabs, panels, components, styles, localization
docs/                          tai lieu hoc thuat, architecture, test plan, PDR
tests/                         solver, heuristic, runtime, tournament, UI, academic regression tests
```

## Tai Lieu Chuyen Sau

- [Tham chieu hoc thuat ve cac nhom thuat toan](docs/algorithm-groups-academic-reference.md)
- [Ke hoach kiem thu thuat toan 15-Puzzle AI](docs/algorithm-test-plan.md)
- [System Architecture](docs/system-architecture.md)
- [Project Overview PDR](docs/project-overview-pdr.md)
- [Codebase Summary](docs/codebase-summary.md)
- [Branch and Release Tree](docs/branch-and-release-tree.md)

## Ghi Chu Bao Ve Nhanh

- Noi ro PEAS truoc khi noi thuat toan.
- A* la solver tham chieu tot nhat khi dung Manhattan/Linear Conflict va khong bi cap tai nguyen.
- UCS va BFS deu optimal vi moi move cost 1; UCS chi tong quat hon khi cost khac nhau.
- Greedy co heuristic nhung khong optimal vi bo qua `g(n)`.
- Hill climbing/local search tot de minh hoa local optimum, khong nen goi la solver dang tin cay.
- CSP/game/chance/no-observation la extension hoc thuat, phai tach khoi 15-puzzle chuan.
- Moi benchmark phai ghi seed, depth, heuristic, action order, timeout, max nodes.
- Path hop le, den goal, va toi uu la ba claim khac nhau; dung certificate cua app de chung minh.
