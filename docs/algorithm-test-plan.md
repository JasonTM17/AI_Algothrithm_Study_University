# Ke hoach kiem thu thuat toan 15-Puzzle AI

Tai lieu nay dinh nghia ke hoach kiem thu co he thong cho dashboard 15-Puzzle AI. Muc tieu la chung minh rang thuat toan, trace, UI hoc thuat va cac mo hinh mo rong hoat dong dung theo ranh gioi da cong bo trong repo.

## Pham vi

| Nhom | Thuat toan | Muc tieu kiem thu |
|---|---|---|
| Uninformed Search | BFS, DFS, UCS, IDS | Legal path, completeness/optimality trong dieu kien bounded, frontier/reached, depth limit. |
| Informed Search | Greedy, A*, IDA* | Heuristic goal-relative, admissibility corpus, optimality certificate, tie-breaking. |
| Local Search | Simple/Steepest/Stochastic/Random-Restart HC, Local Beam, Simulated Annealing | Stuck/local optimum, randomness seed, partial trajectory khong bi gan nhan solution sai. |
| CSP | Definition, AC-3 Propagation, Path Consistency, Global Constraints, Backtracking, Min-Conflicts, Constraint Graphs | AC-3 exact-horizon certificate, rang buoc, bounded planning, khong claim solver tu nhien. |
| Complex Environments | AND-OR, No Observation, Partial Observation, LRTA* | Belief state, observation, nondeterministic branches, online update, khong claim solver tu nhien. |
| AI-vs-AI/Game-Chance | AI-vs-AI Tournament, Minimax, Alpha-Beta, Expectimax | Tournament scoring, reference optimal, tie-break; game/chance utility va caveat. |

## Test Oracle

| Oracle | Cach kiem chung |
|---|---|
| Tinh hop le trang thai | Moi state la hoan vi dung cua `0..15`; invalid input bi reject bang `ValueError`. |
| Tinh giai duoc | `is_solvable(start, goal)` phai dung parity class cua goal tuy chinh. |
| Legal path | `validate_solution_path` va `SearchResult.path_verified` xac nhan tung action bang `_move_blank`. |
| Goal reached | `SearchResult.goal_reached` chi true khi state cuoi bang `goal_state` da chon. |
| Optimality | BFS/UCS/A*/IDA*/IDS chi duoc gan `optimality_proven` khi success, legal path, goal reached, termination la `goal`. |
| Heuristic | Misplaced, Manhattan, Linear Conflict phai tinh theo goal tuy chinh va khong vuot exact distance trong corpus nho. |
| Trace evidence | Frontier/Reaching hien thi node dang `(A, R, g, h, f, parent)` va search tree edge phai la legal transition. |
| Randomness | Run/Advanced phai ghi variation seed moi moi lan bam; Compare/Tournament/Hand-Tracing dung seed/order ro de tai lap. |
| Goal metadata | Moi `SearchResult`, ke ca fail/concept model, phai ghi `goal_state` da chon de dashboard khong hien "Not reported" sai ngu canh. |
| Tournament reference | Moi scored round co A* reference optimal cost dung chung cho hai AI. |

## Ma tran test bat buoc

| ID | Case | Input | Ky vong |
|---|---|---|---|
| ALG-01 | Goal chuan da giai | `GOAL_STATE` | Solver tra path mot state, cost 0, khong crash UI slider. |
| ALG-02 | Mot buoc toi goal | `(1..14,0,15)` | BFS/A*/UCS tra cost 1, legal action dung. |
| ALG-03 | Goal tuy chinh | `start=GOAL_STATE`, `goal=ONE_MOVE` | Solver dung goal tuy chinh, path cuoi bang `ONE_MOVE`. |
| ALG-04 | Khong giai duoc theo goal | Hai state khac parity | Solver complete tra fail nhanh, khong sinh claim solution. |
| ALG-05 | Node limit | `max_nodes` thap | Termination la resource/depth limit, partial evidence neu co van legal. |
| ALG-06 | Timeout | Timeout rat nho | Khong crash, message/termination the hien timeout. |
| ALG-07 | Tie-breaker | A*/UCS/Greedy voi FIFO/LIFO/Min-g/Max-g | Khong sai legal path; trace phan anh frontier/reached. |
| ALG-08 | Heuristic admissibility | Corpus exact distance nho | `h(state) <= h*(state)` cho Misplaced/Manhattan/Linear Conflict. |
| ALG-09 | Greedy contrast | Preset Greedy suboptimal | Greedy khong duoc claim optimal; A* co optimal certificate. |
| ALG-10 | Hill Climbing stuck | Preset local optimum | Result failure/stuck co caveat, khong gan nhan solved sai. |
| ALG-11 | Variation seeds | Run/Advanced voi deterministic va stochastic algorithms | Fresh seeds khac nhau; action order la hoan vi hop le; stochastic solver nhan cung seed. |
| ALG-12 | Tournament optimal score | A* tren `ONE_MOVE` | Agent nhan 100 diem, optimal cost duoc reference dung chung. |
| ALG-13 | Tournament reduced score | Legal path dai hon optimal | Agent nhan `round(100 * optimal/actual)` voi floor 10; cung excess nhung round kho hon khong bi phat nhu round nong. |
| ALG-14 | Tournament invalid/failure score | Path sai hoac no path | Invalid nhan -50; timeout/no path nhan -20. |
| ALG-15 | Trace export | Sau khi chay solver | CSV co Node/Parent/Frontier/Reaching dang node, khong chi count. |
| ALG-16 | Victory feedback | Play board dat goal tuy chinh | Thong bao thang da dang, balloons chi mot lan moi signature. |
| ALG-17 | AC-3 exact horizon | `ONE_MOVE -> GOAL`, T=1 | Domain arc-consistent, path/action legal, goal certificate dung. |
| ALG-18 | AC-3 parity wipe-out | `ONE_MOVE -> GOAL`, T=2 | Domain wipe-out, fail voi `depth_limit`, khong claim solution. |
| ALG-19 | Group comparison | Moi group tren Theory/PEAS | Moi thuat toan co Time, Space, Steps/Output va Guarantee. |
| ALG-20 | Registry contract sweep | Moi thuat toan trong `ALGORITHM_GROUPS` tru `AI-vs-AI Tournament` | Goi qua dispatch kwargs, dung custom goal, kiem legal path/reached goal/optimality/seed metadata. |

## Kiem thu UI/UX thuat toan

| Man hinh | Checklist |
|---|---|
| Play | Start/Goal preview ro, nhap goal tuy chinh, solvability cap nhat, warning khong tron ngon ngu. |
| Run Algorithm | Start/goal contract ro, moi lan bam co variation seed/action order/tie-break, result metric khong che trace, Frontier co legend ky hieu. |
| Step Trace | Empty state chi ro can chay thuat toan truoc; CSV export ton tai; detail slider khong crash khi trace co 1 dong. |
| Compare | Benchmark reset khi thay input/goal/seed; seed stochastic duoc ghi; bang khong tran ngang o mobile. |
| Theory/PEAS | Khong co thuat toan trong taxonomy thieu theory data; moi group co bang so sanh Time/Space/Steps; ranh gioi CSP/game/no-observation/tournament duoc nhac ro. |
| Advanced | Mode phai bam Run moi chay; AC-3 hien domain evidence va replay path neu co; No/Partial Observation hien belief/observation va strict certificate; AI-vs-AI Tournament co reference optimal cost, score reason, replay hai AI tung buoc tren timeline chung, tong diem va winner/draw tai lap. |
| Hand-Tracing | Frontier option co g/h/f/action; chon sai co giai thich; cay Graphviz co edge hop le. |

## Lenh chay kiem thu

```powershell
python -m compileall -q app.py core algorithms ui
python -m pytest tests/ -q
```

Kiem thu UI bang browser:

```text
Desktop: 1280x900
- Run Algorithm: chay BFS/A*, kiem tra trace tuple va search tree.
- Advanced: chay AI-vs-AI Tournament voi A* vs Greedy tren board mot buoc, bam Next de hai board cung tien mot replay step, winner/draw hien dung.
- Step Trace: kiem tra empty state va CSV export.
- Play: bam chung minh toi uu khi chua solve, phai hien trang thai in-progress thay vi loi score.

Mobile: 390x844
- Sidebar khong che noi dung sau khi dong.
- Bang trace/dataframe khong tao horizontal overflow ngoai container.
- Cac nut chinh co vung bam du lon va feedback ro.
```

## Tieu chi pass

- Khong co exception Streamlit trong cac tab chinh.
- Full test suite pass.
- Moi solver success co `path_verified=True` va state cuoi bang goal da chon.
- Moi result phai giu `goal_state` da chon, ke ca khi fail, timeout, model-success, hoac concept-only khong co path.
- Khong co claim sai nhu "Greedy toi uu" hoac "Minimax la solver tu nhien cua 15-puzzle".
- Tournament khong chay neu reference A* khong chung minh duoc optimal path; UI bao `reference failed`.
- Hai AI cung solver, board va tham so phai draw; runtime noise khong duoc tu tao winner.
- IDS/IDA* phai dung ngay khi cham `max_nodes`, ke ca dang o ben trong recursive pass.
- Trace va search tree la evidence co the bao ve: node label, action, g/h/f, parent, frontier/reached va legal edge.
- Cac demo mo rong duoc label la concept/extension/tournament scoring layer, khong bi tron vao bang xep hang solver chuan.
