"""Render README atlas and full GIF gallery from the verified demo catalog."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.readme_gif_catalog import GROUP_GUIDES
from scripts.readme_gif_specs import build_specs
from ui.styles import ALGORITHM_GROUPS


STANDARD_SOLVER_ALGORITHMS = {"BFS", "UCS", "IDS", "A*", "IDA*"}


def main() -> int:
    records = _manifest_records()
    specs = build_specs()
    (ROOT / "README.md").write_text(_readme(specs, records), encoding="utf-8")
    (ROOT / "docs/algorithm-demo-gallery.md").write_text(_gallery(specs, records), encoding="utf-8")
    return 0


def _manifest_records() -> dict[str, dict]:
    path = ROOT / "docs/assets/algorithm-demos/manifest.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    return {record["algorithm"]: record for record in data["records"]}


def _readme(specs, records: dict[str, dict]) -> str:
    by_group = _by_group(specs)
    lines = [
        "# 15-Puzzle AI Algorithm Simulator",
        "",
        "[![Web quality](https://github.com/JasonTM17/AI_Algothrithm_Study_University/actions/workflows/quality.yml/badge.svg)](https://github.com/JasonTM17/AI_Algothrithm_Study_University/actions/workflows/quality.yml)",
        "![Python 3.12](https://img.shields.io/badge/Python-3.12-3776AB?logo=python&logoColor=white)",
        "![Streamlit](https://img.shields.io/badge/Streamlit-app-FF4B4B?logo=streamlit&logoColor=white)",
        "![24 algorithms](https://img.shields.io/badge/AI-24%20algorithms-7FAF6F)",
        "",
        "**Tác giả:** JasonTM17",
        "",
        "Ứng dụng Streamlit để học và bảo vệ đồ án Trí tuệ nhân tạo qua 15-puzzle. Repo không chỉ in ra đáp án; nó trình bày `state`, `action`, `frontier`, `reached`, heuristic, trace, certificate, GIF chạy thật và ranh giới học thuật của từng nhóm thuật toán.",
        "",
        "<p align=\"center\"><img src=\"docs/assets/readme/a-star-image-replay.gif\" alt=\"A* image puzzle replay\" width=\"960\"></p>",
        "",
        "GIF hero ở trên được chụp từ live Streamlit browser capture bằng `agent-browser screenshot`: A* Search, Manhattan Distance, `f(n)=g(n)+h(n)`, legal blank moves và image tiles đi theo cùng trajectory. Không dùng mockup renderer.",
        "",
        "## Mục Lục",
        "",
        "- [Chạy Nhanh](#chạy-nhanh)",
        "- [Kết Quả Quét Lại 24 Thuật Toán](#kết-quả-quét-lại-24-thuật-toán)",
        "- [Bản Đồ 6 Nhóm](#bản-đồ-6-nhóm)",
        "- [Cách Đọc Từng Nhóm](#cách-đọc-từng-nhóm)",
        "- [So Sánh Thuật Toán Trong Nhóm](#so-sánh-thuật-toán-trong-nhóm)",
        "- [Atlas 24 Thuật Toán Có GIF Chạy Thật](#atlas-24-thuật-toán-có-gif-chạy-thật)",
        "- [Cách Đọc Evidence](#cách-đọc-evidence)",
        "- [Tài Liệu](#tài-liệu)",
        "",
        "## Chạy Nhanh",
        "",
        "```bash",
        "python -m venv .venv",
        "source .venv/bin/activate",
        "pip install -r requirements.txt",
        "streamlit run app.py",
        "```",
        "",
        "Windows PowerShell:",
        "",
        "```powershell",
        "python -m venv .venv",
        ".\\.venv\\Scripts\\Activate.ps1",
        "pip install -r requirements.txt",
        "streamlit run app.py",
        "```",
        "",
        "Kiểm tra phát triển:",
        "",
        "```bash",
        "pip install -r requirements-dev.txt",
        "python -m compileall -q app.py core algorithms ui scripts",
        "python scripts/generate-readme-gifs.py --check --check-readability",
        "python -m pytest tests -q --cov=core --cov=algorithms --cov-report=term-missing --cov-fail-under=65",
        "```",
        "",
    ]
    lines += _run_audit_summary(specs, records)
    lines += [
        "## Bản Đồ 6 Nhóm",
        "",
        "`ALGORITHM_GROUPS` là contract chính: 6 nhóm, 24 thuật toán. Mỗi GIF dưới đây là live Streamlit browser capture, không phải mockup.",
        "",
    ]
    for group, items in ALGORITHM_GROUPS.items():
        featured = _featured_path(group)
        guide = GROUP_GUIDES[group]
        lines += [
            f"### {group}",
            "",
            f"<p><img src=\"{featured}\" alt=\"{group}\" width=\"620\"></p>",
            "",
            f"- **Vai trò:** {guide['purpose']}",
            f"- **Câu hỏi học thuật:** {guide['question']}",
            f"- **Thuật toán:** {', '.join(items)}",
            "",
        ]
    lines += [
        "## Cách Đọc Từng Nhóm",
        "",
        "| Nhóm | Cách đọc đúng | Sai lầm cần tránh |",
        "|---|---|---|",
        "| Uninformed Search | So sánh FIFO, LIFO, cost queue và iterative deepening khi không có h(n). | Gọi DFS là optimal hoặc quên memory của BFS. |",
        "| Informed Search | Đọc h(n), g(n), f(n), admissible/consistent và certificate. | Gọi Greedy là optimal chỉ vì một run tình cờ ngắn. |",
        "| Local Search | Xem candidate được xét/chọn/từ chối và lý do dừng. | Nhầm legal trajectory thành solution path. |",
        "| Complex Environments | Đọc conditional, conformant và contingent policy theo đúng belief-state model. | Ép policy thành đường đi tuyến tính giả hoặc để hidden state điều khiển agent. |",
        "| CSP | Đọc variables, domains, constraints, propagation và horizon. | Gọi CSP model definition là shortest-path solver. |",
        "| AI-vs-AI Tournament | Đọc scoring, robustness, pruning và expected value. | Gọi MIN là đối thủ thật của 15-puzzle. |",
        "",
    ]
    lines += _group_comparison_sections()
    lines += [
        "## Atlas 24 Thuật Toán Có GIF Chạy Thật",
        "",
        "Mỗi mục dưới đây có GIF riêng. GIF được tạo từ `scripts/generate-readme-gifs.py`, mở app thật, chụp frame thật từ route `?capture_demo=...`, dùng start/goal/seed/resource limit cố định và được khóa bằng manifest semantic. Dòng **Kết luận chạy / độ phù hợp** nói rõ demo có tới goal hay không và thuật toán có được dùng làm solver chuẩn hay chỉ là mô hình giáo dục.",
        "",
    ]
    counter = 1
    for group, group_specs in by_group.items():
        lines += [f"## {group}: từng thuật toán", ""]
        for spec in group_specs:
            record = records[spec.algorithm]
            lines += _algorithm_section(counter, spec, record)
            counter += 1
    lines += _evidence_and_workflow_sections()
    return "\n".join(lines).rstrip() + "\n"


def _algorithm_section(index: int, spec, record: dict) -> list[str]:
    img = f"docs/assets/algorithm-demos/{spec.slug}.gif"
    params = record.get("parameters") or {}
    param_text = ", ".join(f"`{k}={v}`" for k, v in params.items()) or "default demo parameters"
    result_message = _table_cell(record.get("result_message", ""))
    return [
        f"### {index}. {spec.algorithm}",
        "",
        f"<p><img src=\"{img}\" alt=\"{spec.algorithm} real GIF\" width=\"560\"></p>",
        "",
        "| Trục đọc | Nội dung |",
        "|---|---|",
        f"| Nhóm | {spec.group} |",
        f"| Vai trò | {spec.role} |",
        f"| Learning goal | {spec.learning_goal} |",
        f"| Cơ chế | {spec.mechanism} |",
        f"| Evidence trong GIF | {spec.evidence} |",
        f"| Guarantee | {spec.guarantee} |",
        f"| Caveat | {spec.academic_caveat} |",
        f"| Phù hợp với 15-puzzle chuẩn | {_standard_15_puzzle_fit(spec, record)} |",
        f"| Kết luận chạy / độ phù hợp | **{_run_fit_conclusion(spec, record)}** |",
        f"| Web capture source | `{record.get('source', 'unknown')}` via `{record.get('capture_tool', 'unknown')}` |",
        f"| web_run_status | `{record.get('web_run_status', 'unknown')}` - {_status_label(record.get('web_run_status', 'unknown'))} |",
        f"| Demo input | seed `{record['seed']}`, termination `{record['termination']}`, {param_text} |",
        f"| Certificate flags | `path_verified={record['path_verified']}`, `goal_reached={record['goal_reached']}`, `optimality_proven={record['optimality_proven']}` |",
        f"| Result message | {result_message} |",
        "",
    ]


def _group_comparison_sections() -> list[str]:
    return [
        "## So Sánh Thuật Toán Trong Nhóm",
        "",
        "### Uninformed Search",
        "",
        "| Thuật toán | Frontier/decision rule | Evidence cần nhìn | Guarantee đúng | Caveat |",
        "|---|---|---|---|---|",
        "| BFS | FIFO queue, mở theo tầng. | frontier/reached, path cost, depth. | Complete, optimal với unit step cost. | Memory tăng rất nhanh. |",
        "| DFS | LIFO stack, đi sâu trước. | depth, expanded, legal trajectory. | Không có shortest-path guarantee. | Có thể đi nhánh sâu và bỏ lỡ đường ngắn. |",
        "| UCS | Priority queue theo `g(n)`. | cumulative cost, frontier/reached. | Complete, optimal với non-negative cost. | Với 15-puzzle unit cost gần giống BFS nhưng nêu rõ cost model. |",
        "| IDS | DFS giới hạn độ sâu, tăng limit. | cutoff/exhausted theo từng limit. | Complete, optimal với unit step cost khi limit đủ. | Lặp lại work qua nhiều iteration. |",
        "",
        "### Informed Search",
        "",
        "| Thuật toán | Evaluation rule | Evidence cần nhìn | Guarantee đúng | Caveat |",
        "|---|---|---|---|---|",
        "| Greedy Best-First | Ưu tiên `h(n)` nhỏ nhất. | selected h, frontier, goal flag. | Không optimality certificate. | Nhanh nhưng có thể bị heuristic đánh lừa. |",
        "| A* | Ưu tiên `f(n)=g(n)+h(n)`. | g/h/f, expanded/generated/frontier. | Optimal nếu h admissible/consistent và không bị limit. | Certificate chỉ đúng cho goal/heuristic đã chọn. |",
        "| IDA* | DFS bounded bởi threshold `f`. | threshold, best_g/reached, path. | Optimal với admissible heuristic và threshold đủ. | Tiết kiệm memory nhưng revisit nhiều state. |",
        "",
        "### Local Search",
        "",
        "| Thuật toán | Candidate rule | Evidence cần nhìn | Output đúng | Caveat |",
        "|---|---|---|---|---|",
        "| Simple Hill Climbing | Chọn candidate cải thiện đầu tiên. | candidate được xét, selected action. | Legal local trajectory nếu có action. | Dễ kẹt local optimum. |",
        "| Steepest-Ascent HC | Xét toàn bộ neighbor rồi chọn tốt nhất. | evaluated candidates, best candidate. | Local improvement trace. | Tốn xét neighbor nhưng vẫn local. |",
        "| Stochastic HC | Random trong nhóm candidate cải thiện. | seed, candidate pool, chosen action. | Reproducible khi seed cố định. | Kết quả phụ thuộc seed. |",
        "| Random-Restart HC | Nhiều lần start lại rồi hill climb. | restart index, best h. | So sánh nhiều basin cục bộ. | Không biến thành shortest-path solver. |",
        "| Local Beam Search | Giữ `k` state tốt nhất mỗi vòng. | beam states, selected successors. | Population-based local evidence. | Beam nhỏ có thể mất nhánh tốt. |",
        "| Simulated Annealing | Có thể accept bước xấu theo temperature. | temperature, delta h, accept/reject. | Legal trajectory, đôi khi thoát local optimum. | Không claim solved nếu chưa tới goal. |",
        "",
        "### Complex Environments",
        "",
        "| Thuật toán | Mô hình output | Evidence cần nhìn | Guarantee đúng | Caveat |",
        "|---|---|---|---|---|",
        "| AND-OR Search | Conditional plan/policy. | AND node, OR action, deflection support. | Plan hợp lệ trong depth/support đã chọn. | Không phải linear path giả; support switch không phải probability weight. |",
        "| Searching with no observation | Conformant graph search trên belief state. | Predict(B,a), belief frontier/reached, duplicate rejection, goal coverage. | Một action sequence phải đúng cho mọi state được biểu diễn. | Belief hữu hạn là approximation; bounded failure không chứng minh impossible toàn cục. |",
        "| Partially observable search | Contingent belief-state AND-OR. | predicted belief, observation partitions, updated beliefs, branch coverage. | Mọi observation branch phải có subpolicy. | Hidden actual state chỉ để audit, không xây policy. |",
        "",
        "### CSP",
        "",
        "| Thuật toán | CSP concept | Evidence cần nhìn | Output đúng | Caveat |",
        "|---|---|---|---|---|",
        "| Backtracking | Chronological state-chain assignment. | assignments, consistency checks, backtracks. | Exact-T legal chain khi thành công. | Failure chỉ đúng trong horizon/resource bound. |",
        "| Backtracking + Forward Checking | Assignment kèm prune domain kế tiếp. | values pruned, domain wipe-out, backtracks. | Cùng ordering để so sánh công bằng với Backtracking. | Worst case vẫn exponential. |",
        "| AC-3 | Arc-consistency propagation trên state chain. | arc queue, REVISE, values removed, domain sizes. | Sound propagation; replay chỉ từ exact legal chain. | Arc-consistent không tự động nghĩa unique solution. |",
        "| Min-Conflicts | Seeded local repair của complete state-chain assignment. | conflicted variable, conflict count, iteration. | Replay chỉ khi zero conflict và mọi move legal. | Không complete, không optimal. |",
        "",
        "### AI-vs-AI Tournament",
        "",
        "| Thuật toán | Decision model | Evidence cần nhìn | Output đúng | Caveat |",
        "|---|---|---|---|---|",
        "| AI-vs-AI Tournament | Scored benchmark against A* reference. | score, optimal cost, verified trajectory. | Fair score if reference certificate exists. | Không phải một đối thủ tự nhiên trong 15-puzzle. |",
        "| Minimax | MAX vs worst-case MIN branch. | utility, depth, selected root action. | Depth-limited worst-case decision. | MIN không phải người chơi thật; cả hai dùng legal blank moves. |",
        "| Alpha-Beta Pruning | Minimax with branch-and-bound pruning. | alpha, beta, cutoff events. | Same root value as full Minimax under same searched tree. | Pruning tiết kiệm node, không đổi PEAS thành game thật. |",
        "| Expectimax | Expected value with CHANCE nodes. | probability model, expected utility. | Depth-limited expected-value policy. | Probability model là giáo dục và phải nêu rõ. |",
        "",
    ]


def _status_label(status: str) -> str:
    return {
        "solved_optimal": "reached goal with an optimality certificate",
        "solved_not_optimal": "reached goal without an optimality certificate",
        "ran_model_not_goal_path": "ran successfully as model evidence, not a solved path",
        "not_solved_in_demo": "web demo completed without a solution claim",
        "ran_tournament_model": "scored tournament model, not one solution path",
    }.get(status, "unknown run status")


def _run_fit_conclusion(spec, record: dict) -> str:
    """State what the verified demo proved without overstating solver fitness."""

    status = record.get("web_run_status", "unknown")
    termination = record.get("termination", "unknown")
    if status == "solved_optimal":
        if spec.algorithm not in STANDARD_SOLVER_ALGORITHMS:
            return _table_cell(
                "TRẠNG THÁI KHÔNG NHẤT QUÁN — manifest báo tối ưu cho một thuật toán "
                "không thuộc tập solver chuẩn; cần kiểm tra lại trước khi công bố."
            )
        return _table_cell(
            "PHÙ HỢP LÀM SOLVER CHUẨN — Demo thật đã tới goal bằng legal path "
            "và có chứng chỉ tối ưu cho cấu hình đã chạy."
        )
    if status == "solved_not_optimal":
        return _table_cell(
            "CHẠY ĐƯỢC, DEMO TỚI GOAL NHƯNG KHÔNG CÓ CHỨNG CHỈ TỐI ƯU — "
            "Không dùng run này để claim shortest path hoặc solver chuẩn tối ưu."
        )
    if status == "not_solved_in_demo":
        return _table_cell(
            f"CHẠY ĐƯỢC NHƯNG DEMO KHÔNG TỚI GOAL — Run dừng có kiểm soát "
            f"(`termination={termination}`), không phải crash; trajectory/evidence không được gọi là lời giải."
        )
    if status == "ran_model_not_goal_path":
        if spec.algorithm == "AND-OR Search":
            return _table_cell(
                "CHẠY ĐƯỢC VÀ TRẢ CONDITIONAL PLAN — Output đúng là kế hoạch có nhánh, "
                "không phải một linear path tới goal của 15-puzzle deterministic."
            )
        return _table_cell(
            "CHẠY ĐƯỢC Ở CHẾ ĐỘ MÔ HÌNH/EVIDENCE — Không sinh legal solution path "
            "tới goal; mục này dùng để minh họa khái niệm, không phải solver 15-puzzle chuẩn."
        )
    if status == "ran_tournament_model":
        return _table_cell(
            "CHẠY ĐƯỢC Ở CHẾ ĐỘ CHẤM ĐIỂM — Đây là benchmark hai agent, "
            "không phải một thuật toán sinh solution path riêng."
        )
    return _table_cell(
        "CHƯA CÓ KẾT LUẬN KIỂM CHỨNG — Không công bố khả năng giải trước khi "
        "web_run_status và certificate được xác minh."
    )


def _run_audit_summary(specs, records: dict[str, dict]) -> list[str]:
    by_status: dict[str, list[str]] = {}
    for spec in specs:
        status = records[spec.algorithm].get("web_run_status", "unknown")
        by_status.setdefault(status, []).append(spec.algorithm)

    optimal = by_status.get("solved_optimal", [])
    reached = by_status.get("solved_not_optimal", [])
    stopped = by_status.get("not_solved_in_demo", [])
    model_only = by_status.get("ran_model_not_goal_path", [])
    tournament = by_status.get("ran_tournament_model", [])
    return [
        "## Kết Quả Quét Lại 24 Thuật Toán",
        "",
        "Quét trực tiếp toàn bộ demo specs bằng cùng runner dùng để tạo GIF. "
        "Kết quả hiện tại: **24/24 mục thực thi không phát sinh exception**. "
        "`Không tới goal` không đồng nghĩa `không chạy được`; README tách riêng crash, "
        "run dừng chưa giải xong, model evidence và solution path.",
        "",
        f"- **Solver chuẩn, demo tới goal và có chứng chỉ tối ưu ({len(optimal)}):** {', '.join(optimal)}.",
        f"- **Demo tới goal nhưng không có chứng chỉ tối ưu ({len(reached)}):** {', '.join(reached)}.",
        f"- **Chạy được nhưng demo không tới goal ({len(stopped)}):** {', '.join(stopped)}.",
        f"- **Chỉ tạo model evidence/conditional plan, không tạo goal path ({len(model_only)}):** {', '.join(model_only)}.",
        f"- **Chỉ chạy lớp chấm điểm tournament ({len(tournament)}):** {', '.join(tournament)}.",
        "",
        "Chỉ nhóm đầu được README gọi là **solver chuẩn có chứng chỉ tối ưu** cho cấu hình demo. "
        "Các mục còn lại vẫn có giá trị học thuật, nhưng phải đọc đúng output và caveat ghi ngay tại từng thuật toán.",
        "",
    ]


def _standard_15_puzzle_fit(spec, record: dict) -> str:
    notes = {
        "BFS": "Solver chuẩn cho ca nông: complete và optimal với unit step cost, nhưng frontier/reached tăng rất nhanh nên không hợp cho 15-puzzle sâu.",
        "DFS": "Không dùng làm solver chuẩn: có thể tìm được một path hợp lệ nhưng không bảo đảm ngắn nhất và dễ đi sâu vào nhánh kém.",
        "UCS": "Solver chuẩn khi chi phí bước không âm. Với 15-puzzle unit cost, UCS gần tương đương BFS nhưng giữ rõ mô hình path cost g(n).",
        "IDS": "Solver chuẩn cho unit-cost khi depth limit đủ lớn: tiết kiệm bộ nhớ hơn BFS nhưng lặp lại nhiều lần qua các giới hạn độ sâu.",
        "Greedy Best-First": "Không dùng để chứng minh tối ưu: h(n) giúp chạy nhanh hơn nhưng bỏ qua g(n), nên path có thể dài hơn A*.",
        "A*": "Solver chuẩn chính của app: với Manhattan Distance admissible/consistent và unit step cost, có thể bật optimality_proven khi tới goal.",
        "IDA*": "Solver chuẩn memory-bounded: hợp với 15-puzzle sâu hơn A* về bộ nhớ, đổi lại có thể revisit nhiều state theo threshold.",
        "Simple Hill Climbing": "Không ổn làm solver chuẩn: chỉ đi theo cải thiện cục bộ và có thể dừng ở local optimum dù goal chưa đạt.",
        "Steepest-Ascent Hill Climbing": "Không ổn làm solver chuẩn: xét hết neighbor cục bộ tốt hơn Simple HC nhưng vẫn kẹt plateau/local optimum.",
        "Stochastic Hill Climbing": "Không ổn làm solver chuẩn: seed khác có thể cho trajectory khác, không có completeness hay optimality certificate.",
        "Random-Restart Hill Climbing": "Không ổn làm solver chuẩn: restart tăng cơ hội thoát basin xấu nhưng vẫn không chứng minh được shortest path.",
        "Local Beam Search": "Không ổn làm solver chuẩn: giữ nhiều candidate giúp minh họa tìm kiếm cục bộ, nhưng beam nhỏ có thể bỏ mất route tốt.",
        "Simulated Annealing": "Không ổn làm solver chuẩn: có thể nhận bước xấu để thoát local optimum, nhưng legal trajectory không đồng nghĩa solved hoặc optimal.",
        "AND-OR Search": "Không phải solver tuyến tính của 15-puzzle deterministic: dùng để minh họa conditional plan khi môi trường có outcome lệch.",
        "Searching with no observation": "Không phải solver chuẩn full-observation: conformant sequence phải đúng cho mọi state trong belief hữu hạn và không được đọc hidden state.",
        "Searching for partially observable problems": "Không phải linear solver chuẩn: output là contingent policy phân nhánh theo observation của blank và tile kề.",
        "Backtracking": "CSP assignment search theo exact horizon: chỉ replay verified legal chain; không claim shortest path hoặc unsolvable toàn cục.",
        "Backtracking + Forward Checking": "CSP assignment search có domain pruning; dùng cùng ordering với Backtracking để so sánh, nhưng worst case vẫn exponential.",
        "AC-3": "Propagation trên exact-horizon state chain; arc consistency là evidence, chỉ replay khi trích được exact legal chain.",
        "Min-Conflicts": "Local repair trên complete state-chain assignment; chỉ gọi thành công khi conflict bằng 0 và mọi transition là legal blank move.",
        "AI-vs-AI Tournament": "Không phải thuật toán giải puzzle: là lớp chấm điểm hai solver bằng A* reference và verified trajectory.",
        "Minimax": "Không phải solver tự nhiên của 15-puzzle: MIN là nhánh worst-case robustness, không phải đối thủ thật.",
        "Alpha-Beta Pruning": "Không phải solver tự nhiên của 15-puzzle: chỉ prune cây Minimax worst-case cùng root value, không đổi puzzle thành game hai người.",
        "Expectimax": "Không phải solver chuẩn: dùng CHANCE/probability model để so expected value, xác suất là mô hình giáo dục.",
    }
    note = notes.get(spec.algorithm, spec.academic_caveat)
    status = record.get("web_run_status", "unknown")
    if status == "not_solved_in_demo":
        note += " GIF ghi trung thực rằng demo không tạo solution claim."
    elif status == "ran_model_not_goal_path":
        note += " GIF là model evidence, không phải path tới goal."
    return _table_cell(note)


def _table_cell(value: object) -> str:
    text = str(value).replace("\n", " ").replace("|", "/").strip()
    return text or "-"


def _evidence_and_workflow_sections() -> list[str]:
    return [
        "## Cách Đọc Evidence",
        "",
        "| Trường | Nghĩa |",
        "|---|---|",
        "| `path_verified` | Chuỗi action là legal blank moves. |",
        "| `goal_reached` | State cuối bằng goal đã chọn. |",
        "| `optimality_proven` | Chỉ true khi thuật toán optimal, path hợp lệ, tới goal và termination là `goal`. |",
        "| `frontier` | Node đang chờ xét. |",
        "| `reached` | State/record đã biết trong reached, best_g hoặc best_depth. |",
        "| `g(n)` | Path cost từ start tới node. |",
        "| `h(n)` | Heuristic estimate tới goal. |",
        "| `f(n)` | Priority của A*: `g(n)+h(n)`. |",
        "| `trace` | Bằng chứng từng bước: generate, expand, select, prune, accept/reject. |",
        "| `web_run_status` | Trạng thái thật của browser capture: solved, partial/model, not solved hoặc tournament. |",
        "| `source` | Phải là `live_streamlit_browser_capture`; nếu khác thì asset không được xem là GIF web thật. |",
        "",
        "Ba tầng chứng minh phải đọc riêng:",
        "",
        "```text",
        "Path legal       !=  Goal reached",
        "Goal reached     !=  Optimal",
        "Algorithm success !=  Solver chuẩn của 15-puzzle",
        "```",
        "",
        "## Tài Liệu",
        "",
        "- [Algorithm demo gallery](docs/algorithm-demo-gallery.md)",
        "- [Algorithm correctness matrix](docs/algorithm-correctness-matrix.md)",
        "- [UI/UX evidence surfaces](docs/ui-ux-evidence-surfaces.md)",
        "- [Known limitations](docs/known-limitations.md)",
        "- [Deep bug audit](docs/deep-bug-audit.md)",
        "- [Project overview/PDR](docs/project-overview-pdr.md)",
        "- [Codebase summary](docs/codebase-summary.md)",
        "- [System architecture](docs/system-architecture.md)",
        "- [Algorithm test plan](docs/algorithm-test-plan.md)",
        "- [Academic reference for groups](docs/algorithm-groups-academic-reference.md)",
        "- [Project roadmap](docs/project-roadmap.md)",
    ]


def _gallery(specs, records: dict[str, dict]) -> str:
    lines = [
        "# Algorithm Demo Gallery",
        "",
        "Trang này nhúng đủ 24 GIF chạy thật. Mỗi GIF lấy frame từ live Streamlit browser capture bằng `agent-browser screenshot` và có manifest semantic tại `docs/assets/algorithm-demos/manifest.json`.",
        "",
    ]
    for group, group_specs in _by_group(specs).items():
        guide = GROUP_GUIDES[group]
        lines += [f"## {group}", "", f"**Mục tiêu:** {guide['purpose']}", ""]
        for spec in group_specs:
            record = records[spec.algorithm]
            lines += [
                f"### {spec.algorithm}",
                "",
                f"<p><img src=\"assets/algorithm-demos/{spec.slug}.gif\" alt=\"{spec.algorithm}\" width=\"720\"></p>",
                "",
                f"- **Learning goal:** {spec.learning_goal}",
                f"- **Mechanism:** {spec.mechanism}",
                f"- **Trace evidence:** {spec.evidence}",
                f"- **Guarantee:** {spec.guarantee}",
                f"- **Caveat:** {spec.academic_caveat}",
                f"- **Phù hợp với 15-puzzle chuẩn:** {_standard_15_puzzle_fit(spec, record)}",
                f"- **Kết luận chạy / độ phù hợp:** **{_run_fit_conclusion(spec, record)}**",
                f"- **Source:** `{record.get('source', 'unknown')}` via `{record.get('capture_tool', 'unknown')}`.",
                f"- **web_run_status:** `{record.get('web_run_status', 'unknown')}` - {_status_label(record.get('web_run_status', 'unknown'))}.",
                f"- **Result message:** {_table_cell(record.get('result_message', ''))}",
                f"- **Manifest:** termination `{record['termination']}`, profile `{record['profile']}`, frames `{record['frame_count']}`, verified `{record['verified_at']}`.",
                "",
            ]
    lines += [
        "## Tái tạo",
        "",
        "```bash",
        "python scripts/generate-readme-gifs.py --featured --profile all --theme dark",
        "python scripts/generate-readme-gifs.py --all --profile algorithm --theme dark",
        "python scripts/generate-readme-gifs.py --check --check-readability",
        "```",
    ]
    return "\n".join(lines).rstrip() + "\n"


def _by_group(specs) -> dict[str, list]:
    return {
        group: [spec for spec in specs if spec.group == group]
        for group in ALGORITHM_GROUPS
    }


def _featured_path(group: str) -> str:
    return {
        "Uninformed Search": "docs/assets/readme/uninformed-search.gif",
        "Informed Search": "docs/assets/readme/informed-search.gif",
        "Local Search": "docs/assets/readme/local-search.gif",
        "Complex Environments": "docs/assets/readme/complex-environments.gif",
        "CSP": "docs/assets/readme/csp.gif",
        "AI-vs-AI Tournament": "docs/assets/readme/ai-vs-ai-tournament.gif",
    }[group]


if __name__ == "__main__":
    raise SystemExit(main())
