# Tham chieu hoc thuat ve cac nhom thuat toan

Tai lieu nay dung cho phan bao ve cuoi ky cua ung dung 15-Puzzle AI Algorithm Simulator. Noi dung bam theo code hien tai trong `algorithms/`, `core/academic.py`, `core/academic_proofs.py`, `core/heuristics.py`, va cach UI tach "standard solver lab" khoi "advanced concept lab".

## 1. Mo hinh bai toan chuan

15-puzzle chuan trong repo la bai toan tim kiem trang thai don tac tu.

| Thuoc tinh | Ket luan hoc thuat | Y nghia trong app |
|---|---|---|
| Quan sat | Fully observable | Agent thay toan bo 4x4 board. |
| Tinh xac dinh | Deterministic | Mot hanh dong hop le luon sinh dung mot trang thai ke tiep. |
| Tinh dong | Static | Board khong tu doi khi agent suy nghi. |
| Roi rac | Discrete | State, action, path cost deu roi rac. |
| Tuan tu | Sequential | Quyet dinh hien tai anh huong cac trang thai sau. |
| Tac tu | Single-agent | Khong co doi thu trong bai toan chuan. |
| Chi phi | Unit step cost | Moi lan truot o trong co cost 1. |

PEAS chuan:

| PEAS | Dien giai |
|---|---|
| Performance | Den goal, it buoc, it node mo rong, it bo nho, runtime thap. |
| Environment | Board 4x4, deterministic, fully observable, static, discrete, sequential, single-agent. |
| Actuators | Truot o trong theo L/R/U/D khi hop le. |
| Sensors | Trang thai board day du, vi tri o trong, legal moves, heuristic estimates. |

Ranh gioi quan trong: CSP, AND-OR, no/partial observation, LRTA*, Minimax, Alpha-Beta, va Expectimax la phan mo rong hoc thuat. AI-vs-AI Tournament la lop cham diem giua hai solver agent cung giai 15-puzzle; no khong bien 15-puzzle thanh moi truong co MIN player.

## 2. Bang phan loai nhanh

| Vai tro | Thuat toan | Co nen dung lam solver chinh? | Diem bao ve |
|---|---|---:|---|
| Real Solver | BFS, UCS, IDS, A*, IDA* | Co | Chung minh loi giai hop le, tinh day du, toi uu trong dieu kien phu hop. |
| Contrast Demo | DFS, Greedy Best-First, local search variants | Khong | Chi ra trade-off, suboptimality, local optimum, plateau, hoac thieu guarantee. |
| Illustrative Extension | CSP, AND-OR, No Observation, Partial Observation, LRTA* | Khong | Giai thich cach doi mo hinh bai toan va moi truong. |
| AI-vs-AI/Game-Chance | AI-vs-AI Tournament, Minimax, Alpha-Beta, Expectimax | Tournament la scoring layer | Tournament cham diem hai agent; game/chance mode chi la extension giao duc. |

Khi bao ve, nen noi ro ba tang bang chung:

1. Legal path certificate: moi canh trong path phai la mot move hop le.
2. Goal reachability: path ket thuc dung goal hay chi la partial/selected/sample path.
3. Optimality certificate: thuat toan va heuristic co du dieu kien de chung minh cost toi uu hay khong.

## 2.1. Doi chieu truc tiep voi de cuong trong anh

Theory/PEAS co them nhom panel "Direct Syllabus Audit" de map tung muc trong de cuong sang web:

| Cum noi dung trong de cuong | Noi xem tren web | Bang chung can chi |
|---|---|---|
| Main steps of search algorithms | Theory/PEAS -> Search Foundations; Run Algorithm | Initial state, goal test, frontier, expand, reached, termination/certificate. |
| Tree search and graph search | Theory/PEAS -> Tree Search vs Graph Search; Step Trace; Hand-Tracing | Cay Graphviz co parent-child edge; graph search co reached/best_g. |
| Best-first search, A* search | Theory/PEAS -> Informed Search; Run Algorithm | Greedy dung h(n), A* dung f(n)=g(n)+h(n). |
| Heuristic functions generation | Theory/PEAS -> Heuristic Generation | Misplaced, Manhattan, Linear Conflict va ly do admissible/consistent. |
| Issues of hill-climbing search | Theory/PEAS -> Hill-Climbing Issues; teaching preset | Local optimum, plateau/shoulder, ridge, randomness/sideways caveat. |
| CSP continuation | Advanced -> CSP modes | AC-3 exact horizon, path consistency, global constraints, bounded backtracking, min-conflicts, constraint graph. |
| Tim kiem doi khang | Advanced -> Minimax/Alpha-Beta/Expectimax | Game/chance extension, khong phai solver tu nhien cua 15-puzzle. |

Quy tac bao ve: neu giang vien chi vao mot dong trong de cuong, hay mo panel coverage matrix truoc, roi chuyen sang Run/Advanced de cho bang chung chay duoc.

## 2.2. Cac buoc search nen noi theo thu tu

| Buoc | Noi dung | Bang chung trong app |
|---|---|---|
| 1 | Initial state va goal | Start/Goal contract tren moi trang chay. |
| 2 | Goal test | `goal_reached` tach rieng voi `success`. |
| 3 | Frontier selection | Queue, stack, priority queue, beam, hoac temperature rule. |
| 4 | Expand legal actions | Chi sinh L/R/U/D hop le cua blank. |
| 5 | Reached/duplicate handling | `reached`, `best_g`, hoac path-set tuy thuat toan. |
| 6 | Termination/certificate | `termination_reason`, `path_verified`, `optimality_proven`. |

Tree search xem moi duong di sinh ra la mot node rieng, nen de lap lai state. Graph search ghi nho state da den hoac cost tot nhat (`reached`, `best_g`) de tranh duplicate bi tri. App ve search tree bang parent-child edge de minh hoa qua trinh sinh node, nhung cac solver chuan van dung duplicate handling de giu tinh dung.

## 3. Uninformed Search

Nhom uninformed search khong dung heuristic. Frontier duoc dieu khien boi depth, stack/queue, hoac path cost.

| Thuat toan | Frontier/evaluation | Complete | Optimal | Bo nho | Ghi chu |
|---|---|---:|---:|---|---|
| BFS | FIFO queue, mo theo depth | Co neu branching huu han | Co voi unit cost | Rat cao, O(b^d) | De chung minh shortest path nhung nhanh het bo nho. |
| DFS | Stack/depth-first | Khong dam bao trong graph/luc gioi han | Khong | Thap, O(bm) | Contrast demo: tiet kiem bo nho nhung de di sau sai huong. |
| UCS | Priority queue theo g(n) | Co voi cost duong | Co | Cao | Voi 15-puzzle unit cost, UCS tuong duong BFS ve thu tu cost. |
| IDS | Lap depth-limited search | Co voi branching huu han | Co voi unit cost | Thap, O(bd) | Doi runtime lay bo nho thap. |

`b` la branching factor, `d` la do sau loi giai ngan nhat, `m` la depth toi da dang xet.

## 4. Informed Search va heuristic

| Thuat toan | Evaluation | Complete | Optimal | Vai tro |
|---|---|---:|---:|---|
| Greedy Best-First | Uu tien h(n) nho nhat | Khong dam bao trong thuc hanh graph search | Khong | Contrast demo cho heuristic-only failure. |
| A* | f(n)=g(n)+h(n) | Co neu heuristic admissible/consistent va tai nguyen du | Co | Solver tham chieu chinh. |
| IDA* | DFS theo nguong f-cost tang dan | Co trong dieu kien huu han | Co voi admissible heuristic | Solver toi uu tiet kiem bo nho hon A*. |

Heuristic trong repo:

| Heuristic | Dinh nghia | Quan he suc manh | Dung de bao ve |
|---|---|---|---|
| Misplaced Tiles | Dem tile sai vi tri, bo qua blank | Yeu nhat | De giai thich admissible. |
| Manhattan Distance | Tong khoang cach hang+cot toi goal | Manh hon Misplaced | Chuan de chung minh A* optimality. |
| Linear Conflict | Manhattan + conflict penalty hop le | Manh hon Manhattan | Cho thay heuristic manh hon nhung van admissible. |

Admissible nghia la `h(n) <= h*(n)`. Consistent nghia la `h(n) <= c(n,n') + h(n')` voi moi canh hop le. Neu A* bi timeout hoac node cap, ket qua thuc nghiem khong con la optimality certificate.

Heuristic generation trong 15-puzzle:

| Heuristic | Cach sinh hoc thuat | Bao ve ngan |
|---|---|---|
| Misplaced Tiles | Relax khoang cach, chi dem tile sai vi tri. | Moi tile sai can it nhat mot dong thai de sua, nen khong overestimate. |
| Manhattan Distance | Relax viec bi tile khac chan duong, moi tile van phai di theo hang/cot toi goal. | Moi slide chi giam/tang tong Manhattan toi da 1, nen consistent voi unit cost. |
| Linear Conflict | Them chi phi bat buoc khi hai tile cung goal-row/goal-column bi nguoc thu tu. | Conflict can it nhat 2 move them, nen manh hon Manhattan ma van admissible trong app. |

## 5. Local Search

Local search khong duy tri frontier day du. No giu mot state hien tai, mot vai state tot nhat, hoac chap nhan move xau theo xac suat.

| Thuat toan | Cach chon buoc | Complete | Optimal | Failure mode |
|---|---|---:|---:|---|
| Simple Hill Climbing | Chon cai thien dau tien | Khong | Khong | Local optimum, plateau. |
| Steepest-Ascent Hill Climbing | Chon neighbor tot nhat | Khong | Khong | Ket neu moi neighbor khong tot hon. |
| Stochastic Hill Climbing | Chon cai thien ngau nhien | Khong | Khong | Phu thuoc seed. |
| Random-Restart Hill Climbing | Chay lai tu nhieu diem | Khong tuyet doi | Khong | Tang xac suat thanh cong, khong chung minh toi uu. |
| Local Beam Search | Giu k state tot nhat | Khong | Khong | Beam hep co the mat nhanh loi giai. |
| Simulated Annealing | Co the nhan move xau theo temperature | Khong huu han | Khong | Schedule kem co the hoi tu kem. |

Trong 15-puzzle, nhom nay huu ich nhat o vai tro giao duc: heuristic tot khong du neu thuat toan chi toi uu cuc bo.

Issues of hill-climbing nen noi ro:

| Van de | Y nghia | Cach app minh hoa |
|---|---|---|
| Local optimum | Khong neighbor nao tot hon current, dung truoc goal. | Teaching preset `Hill Climbing stuck: local optimum h=4`. |
| Plateau/shoulder | Nhieu neighbor co cung h, strict improvement khong co huong di. | Theory/PEAS -> Hill-Climbing Issues. |
| Ridge | Can di ngang hoac tam thoi xau hon moi xuong duoc heuristic ve sau. | Simulated Annealing co xac suat nhan move xau khi T con cao. |
| Randomness dependence | Seed khac nhau sinh trajectory khac nhau. | Stochastic HC, Random-Restart HC, Simulated Annealing hien seed. |

Backtracking CSP trong app la bounded transition planning voi heuristic value ordering. Khong goi la MRV/LCV hay forward-checking day du, vi code khong cai dat day du cac heuristic CSP do.

## 6. CSP trong 15-puzzle

CSP mo hinh hoa bai toan bang bien `X`, mien gia tri `D`, va rang buoc `C`. Voi 15-puzzle, co the mo hinh planning bang bien theo time step, nhung khong tu nhien bang state-space search vi so bien/rang buoc tang theo horizon.

| Thanh phan | Trong app | Y nghia hoc thuat |
|---|---|---|
| CSP Definition | Trinh bay X, D, C | Doi cach nhin tu path search sang constraint satisfaction. |
| Constraint Propagation | AC-3 tren chuoi trang thai `S[0]..S[T]` | Thu hep domain den khi arc-consistent; tra exact-T legal path hoac domain wipe-out. |
| Path Consistency | Consistency bac cao hon arc consistency | Kiem tra rang buoc giua nhieu bien. |
| Global Constraints | Vi du AllDifferent | Tom gon nhieu rang buoc nhi phan. |
| Backtracking Search | Demo planning co gioi han | Minh hoa bounded transition planning, khong phai solver chinh. |
| Min-Conflicts | Local repair | Hop voi bai toan sua loi rang buoc hon 15-puzzle transition planning. |
| Constraint Graphs | Do thi bien-rang buoc | Giai thich lien ket va do kho. |

Khong con demo to mau ban do trong UI/code. Khi bao ve, chi can noi CSP la cach mo hinh minh hoa, khong phai huong giai tu nhien nhat cho 15-puzzle.

Ban executable AC-3 dung bien trang thai day du de tranh mot bo rang buoc transition `X[t][p]` qua lon trong demo. Mien trung gian gom cac trang thai hop le trong lan can bounded cua start/goal. Rang buoc nhi phan yeu cau `S[t+1]` cach `S[t]` dung mot blank move. Hai dau mut bi co dinh boi start va goal. Do day la constraint graph dang chuoi, sau khi AC-3 khong wipe-out thi app co the trich mot chuoi hop le; tuy nhien ket qua chi cho horizon T da chon, khong tu dong chung minh duong ngan nhat toan cuc.

Moi bang Theory/PEAS so sanh cac thuat toan trong cung nhom bang cung cac cot: quy tac chon buoc, time complexity, space complexity, so buoc/output, va guarantee. Ky hieu Big-O la worst-case ly thuyet; runtime/node count thuc nghiem van phu thuoc input va cach cai dat.

## 7. Complex Environments

Trong man Run Algorithm, AND-OR duoc hien bang alias `Nhom 3 - Moi truong phuc tap` de khop de cuong bao ve. Day chi la alias UI; taxonomy van la `Complex Environments` va vai tro van la `Illustrative Extension`, khong phai Local Search.

| Thuat toan | Moi truong | Output | Ranh gioi |
|---|---|---|---|
| AND-OR Search | Nondeterministic | Conditional plan | Khong can cho 15-puzzle deterministic chuan. |
| No Observation Search | Khong quan sat state that | Belief-state plan/demo | Sensor bi yeu di co chu y. |
| Partially Observable Search | Quan sat mot phan | Belief update trace | Khong phai solver chuan. |
| LRTA* | Online search/learning | Path hoc tung buoc | Co the khong toi uu, dung de ban ve agent online. |

Neu sensor/transition/observability thay doi, bieu dien state va thuat toan cung thay doi. Khong so sanh node count cua nhom nay voi A*/IDA* nhu the cung mot bai toan.

## 8. AI-vs-AI Tournament va game/chance extension

15-puzzle chuan la single-agent. Tournament trong app la lop cham diem giua hai agent giai cung board, khong phai doi khang tu nhien trong moi truong puzzle.

| Thanh phan | Mo hinh | Guarantee | Nen trinh bay |
|---|---|---|---|
| AI-vs-AI Tournament | Hai solver agent chay tren cung start/goal | Diem dua tren A* reference optimal certificate | So sanh chat luong loi giai, failure, runtime, nodes. |
| Minimax | MAX/MIN game tree extension | Toi uu theo utility neu game tree/depth dung va duyet du | Khai niem doi thu toi uu. |
| Alpha-Beta Pruning | Minimax co cat tia | Giu cung root value voi Minimax neu dieu kien duyet du | Pruning giam node ma khong doi quyet dinh. |
| Expectimax | MAX/CHANCE tree | Toi uu ky vong theo xac suat mo hinh | Ra quyet dinh khi co chance outcome. |

Scoring tournament co dinh:

| Ket qua agent | Diem |
|---|---:|
| Path hop le, toi goal, cost bang optimal cost | +100 |
| Path hop le, toi goal, cost dai hon optimal | `max(10, round(100 * optimal_cost / actual_cost))` |
| Path hop le nhung khong toi goal | -10 |
| Timeout/resource limit/no path | -20 |
| Exception, path khong verify, action sai luat, state/action mismatch | -50 |

Moi round chay A* lam reference. Neu A* reference khong chung minh duoc optimal path, round do duoc bao `reference failed` va khong cham diem. Hai trajectory hop le duoc replay tren cung timeline de nguoi hoc theo doi tung action. Tie-break theo thu tu: tong diem, so round optimal, so round solved, total excess cost thap hon; neu van hoa thi draw. Runtime va nodes chi la evidence mo ta vi runtime phu thuoc may, con node/iteration khong dong nghia giua cac ho thuat toan.

Cau bao ve quan trong: "AI-vs-AI Tournament danh gia hai solver agent bang thang diem; no khong tao MIN player trong PEAS chuan cua 15-puzzle."

## 9. Cach chon thuat toan khi bao ve

| Nhu cau | Nen dung | Tranh noi |
|---|---|---|
| Chung minh shortest path nong | BFS/UCS/IDS | "DFS toi uu" |
| Solver chuan tot nhat | A* voi Manhattan hoac Linear Conflict | "Greedy cung toi uu vi co heuristic" |
| Puzzle sau, it bo nho hon A* | IDA* | "BFS phu hop puzzle sau" |
| Chung minh heuristic failure | Greedy, Hill Climbing preset | "Local search la solver dang tin cay" |
| Giai thich moi truong phuc tap | AND-OR, belief-state, LRTA* | "Day la cung bai toan chuan" |
| Giai thich CSP | CSP planning, constraint graph | "CSP la cach tu nhien nhat cho 15-puzzle" |
| So sanh hai AI | AI-vs-AI Tournament | "15-puzzle co doi thu tu nhien" |

## 10. Checklist tra loi van dap

- Neu dung PEAS truoc khi chon thuat toan.
- Phan biet solver chuan, contrast demo, extension, tournament/game demo.
- Voi moi path, hoi: path co hop le khong, co den goal khong, co chung minh toi uu khong.
- Voi A*/IDA*, neu heuristic admissible/consistent va gioi han timeout/node cap.
- Voi BFS/UCS/IDS, neu unit step cost la ly do optimality.
- Voi DFS/Greedy/local search, neu failure mode cu the.
- Voi CSP/game/chance/tournament, noi ro day la doi mo hinh hoac lop danh gia, khong phai solver tu nhien cua 15-puzzle chuan.
- Khi dung benchmark/tournament, neu seed, depth, heuristic, max nodes, timeout va caveat.

## 11. Bang cau noi ngan cho giang vien

| Cau hoi | Cau tra loi goi y |
|---|---|
| Vi sao A* toi uu? | Vi A* dung `f=g+h`; voi Manhattan/Linear Conflict admissible va consistent, goal dau tien duoc chon tu frontier co cost toi uu neu khong bi gioi han tai nguyen. |
| Vi sao UCS giong BFS o day? | Vi moi slide co cost 1, nen thu tu tang `g(n)` cua UCS trung voi thu tu depth cua BFS. |
| Vi sao Greedy khong du? | Greedy chi toi thieu hoa `h(n)`, bo qua cost da di `g(n)`, nen co the chon duong nhin gan goal nhung dai hon. |
| Vi sao local search ket? | No toi uu cuc bo, khong giu frontier toan cuc, nen local optimum/plateau co the chan duong toi goal. |
| Vi sao CSP khong phai solver chinh? | CSP planning can bien theo time step va horizon; voi 15-puzzle chuan, state-space search tu nhien va truc tiep hon. |
| Vi sao co AI-vs-AI Tournament? | De cham diem hai solver agent tren cung puzzle bang A* reference: dung/toi uu duoc diem cao, duong dai hon duoc diem thap hon, sai/that bai bi tru diem. |
