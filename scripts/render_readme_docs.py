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
        "![28 algorithms](https://img.shields.io/badge/AI-28%20algorithms-7FAF6F)",
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
        "- [Bản Đồ 6 Nhóm](#bản-đồ-6-nhóm)",
        "- [Cách Đọc Từng Nhóm](#cách-đọc-từng-nhóm)",
        "- [Atlas 28 Thuật Toán Có GIF Chạy Thật](#atlas-28-thuật-toán-có-gif-chạy-thật)",
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
        "## Bản Đồ 6 Nhóm",
        "",
        "`ALGORITHM_GROUPS` là contract chính: 6 nhóm, 28 thuật toán. Mỗi GIF dưới đây là live Streamlit browser capture, không phải mockup.",
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
        "| Complex Environments | Đọc belief, conditional plan, online update theo đúng mô hình mở rộng. | Ép AND-OR/belief thành đường đi tuyến tính giả. |",
        "| CSP | Đọc variables, domains, constraints, propagation và horizon. | Gọi CSP model definition là shortest-path solver. |",
        "| AI-vs-AI Tournament | Đọc scoring, robustness, pruning và expected value. | Gọi MIN là đối thủ thật của 15-puzzle. |",
        "",
        "## Atlas 28 Thuật Toán Có GIF Chạy Thật",
        "",
        "Mỗi mục dưới đây có GIF riêng. GIF được tạo từ `scripts/generate-readme-gifs.py`, mở app thật, chụp frame thật từ route `?capture_demo=...`, dùng start/goal/seed/resource limit cố định và được khóa bằng manifest semantic. Trường `web_run_status` ghi trung thực: solved, partial/model, not solved hoặc tournament.",
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
        f"| Web capture source | `{record.get('source', 'unknown')}` via `{record.get('capture_tool', 'unknown')}` |",
        f"| web_run_status | `{record.get('web_run_status', 'unknown')}` - {_status_label(record.get('web_run_status', 'unknown'))} |",
        f"| Demo input | seed `{record['seed']}`, termination `{record['termination']}`, {param_text} |",
        f"| Certificate flags | `path_verified={record['path_verified']}`, `goal_reached={record['goal_reached']}`, `optimality_proven={record['optimality_proven']}` |",
        f"| Result message | {result_message} |",
        "",
        "Khi thuyết trình:",
        "",
        "1. Nói rõ state/action/cost model trước khi giải thích hình.",
        "2. Chỉ vào evidence chính trên GIF: frontier, reached, candidate, belief, domain, utility hoặc score.",
        "3. Kết thúc bằng guarantee và caveat để không claim quá mức.",
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
        "Trang này nhúng đủ 28 GIF chạy thật. Mỗi GIF lấy frame từ live Streamlit browser capture bằng `agent-browser screenshot` và có manifest semantic tại `docs/assets/algorithm-demos/manifest.json`.",
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
