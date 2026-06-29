"""Generate README GIFs from live Streamlit browser captures."""

from __future__ import annotations

import argparse
import json
import shutil
import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path
from urllib.parse import quote, urlencode

from PIL import Image, ImageSequence

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.readme_gif_manifest import check_generated_assets, manifest_record, write_manifest
from scripts.readme_gif_runner import DemoEvidence, run_demo
from scripts.readme_gif_specs import build_specs, featured_specs, get_spec
from scripts.readme_gif_styles import PROFILES


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--featured", action="store_true", help="Generate hero and six group GIFs.")
    parser.add_argument("--all", action="store_true", help="Generate all 24 algorithm GIFs.")
    parser.add_argument("--algorithm", help="Generate one algorithm GIF by name or slug.")
    parser.add_argument("--check", action="store_true", help="Validate generated assets and manifest.")
    parser.add_argument("--profile", choices=["hero", "group", "algorithm", "all"], default="all")
    parser.add_argument("--theme", choices=["light", "dark"], default="dark",
                        help="Kept for manifest compatibility; live web capture uses the Streamlit theme.")
    parser.add_argument("--contact-sheet", action="store_true", help="Create tmp_visual_checks/readme-gif-contact-sheet.png.")
    parser.add_argument("--check-readability", action="store_true", help="Check dimensions, frames and nonblank pixels.")
    parser.add_argument("--output-dir", default=".", help="Project root or temp output root.")
    parser.add_argument("--port", type=int, help="Use an existing or new Streamlit port.")
    parser.add_argument("--keep-server", action="store_true", help="Do not stop the Streamlit server started by this script.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_root = Path(args.output_dir).resolve()
    if args.check and not (args.featured or args.all or args.algorithm):
        check_generated_assets(output_root)
        if args.check_readability:
            check_readability(output_root)
        if args.contact_sheet:
            write_contact_sheet(output_root)
        print("README GIF assets check passed")
        return 0

    specs = _selected_specs(args) or featured_specs()
    _delete_stale_outputs(specs, args, output_root)

    server = None
    records: list[dict] = []
    try:
        port = args.port or _free_port()
        if not _health_ok(port):
            server = _start_streamlit(port, output_root)
        _browser(["close", "--all"], check=False)
        _browser(["open", "about:blank"])

        for spec in specs:
            evidence = run_demo(spec)
            relative_path, image_mode = _output_path(spec, args, output_root)
            profile = _profile_for(spec, args)
            meta = _capture_gif(
                evidence,
                relative_path,
                base_url=f"http://localhost:{port}",
                profile=profile,
                image_mode=image_mode,
                theme=args.theme,
                output_root=output_root,
            )
            records.append(manifest_record(evidence, meta, relative_path.relative_to(output_root)))
            print(f"captured {relative_path.relative_to(output_root)} [{meta['web_run_status']}]")
    finally:
        _browser(["close", "--all"], check=False)
        if server is not None and not args.keep_server:
            server.terminate()
            try:
                server.wait(timeout=8)
            except subprocess.TimeoutExpired:
                server.kill()

    if args.all:
        write_manifest(records, output_root / "docs/assets/algorithm-demos")
    if args.check:
        check_generated_assets(output_root)
        if args.check_readability:
            check_readability(output_root)
    if args.contact_sheet:
        write_contact_sheet(output_root)
    return 0


def _selected_specs(args: argparse.Namespace):
    if args.algorithm:
        return [get_spec(args.algorithm)]
    if args.all:
        return build_specs()
    if args.featured:
        return featured_specs()
    return []


def _output_path(spec, args: argparse.Namespace, output_root: Path) -> tuple[Path, bool]:
    if args.featured and spec.featured_slug == "a-star-image-replay":
        return output_root / "docs/assets/readme/a-star-image-replay.gif", True
    if args.featured and spec.featured_slug:
        return output_root / f"docs/assets/readme/{spec.featured_slug}.gif", False
    return output_root / f"docs/assets/algorithm-demos/{spec.slug}.gif", False


def _profile_for(spec, args: argparse.Namespace) -> str:
    if args.profile != "all":
        return args.profile
    if args.featured and spec.featured_slug == "a-star-image-replay":
        return "hero"
    if args.featured and spec.featured_slug:
        return "group"
    return "algorithm"


def _delete_stale_outputs(specs, args: argparse.Namespace, output_root: Path) -> None:
    if args.all:
        for gif_path in (output_root / "docs/assets/algorithm-demos").glob("*.gif"):
            gif_path.unlink()
    if args.featured:
        for gif_path in (output_root / "docs/assets/readme").glob("*.gif"):
            gif_path.unlink()
    if args.algorithm:
        for spec in specs:
            path, _ = _output_path(spec, args, output_root)
            path.unlink(missing_ok=True)


def _capture_gif(
    evidence: DemoEvidence,
    output_path: Path,
    *,
    base_url: str,
    profile: str,
    image_mode: bool,
    theme: str,
    output_root: Path,
    query_params: dict[str, str] | None = None,
) -> dict:
    render_profile = PROFILES[profile]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    frame_dir = output_root / "tmp_visual_checks/live-gif-frames" / output_path.stem
    if frame_dir.exists():
        shutil.rmtree(frame_dir)
    frame_dir.mkdir(parents=True, exist_ok=True)

    _browser(["set", "viewport", str(render_profile.width), str(render_profile.height)])
    frames: list[Image.Image] = []
    for index in range(len(evidence.states)):
        params = {
            "capture_demo": evidence.spec.slug,
            "capture_frame": str(index),
            "capture_image": "1" if image_mode else "0",
        }
        if query_params:
            params.update(query_params)
        url = f"{base_url}/?{urlencode(params, quote_via=quote)}"
        frame_path = frame_dir / f"frame-{index:02d}.png"
        _browser(["open", url])
        _browser(["wait", "--text", f"capture-ready-{evidence.spec.slug}-{index}"])
        _browser(["screenshot", str(frame_path)])
        with Image.open(frame_path) as image:
            frames.append(_normalize_frame(image.convert("RGB"), render_profile.width, render_profile.height))

    paletted = [frame.convert("P", palette=Image.Palette.ADAPTIVE, colors=128) for frame in frames]
    paletted[0].save(
        output_path,
        save_all=True,
        append_images=paletted[1:],
        duration=760 if profile == "hero" else 700,
        loop=0,
        optimize=True,
    )
    return {
        "profile": profile,
        "theme": theme,
        "source": "live_streamlit_browser_capture",
        "capture_tool": "agent-browser screenshot",
        "frame_count": len(frames),
        "dimensions": [render_profile.width, render_profile.height],
        "file_bytes": output_path.stat().st_size,
        "web_run_status": _web_run_status(evidence),
        "result_success": bool(evidence.result.success) if evidence.result else True,
        "result_message": (evidence.result.message if evidence.result else "Tournament scoring run")[:240],
    }


def _normalize_frame(image: Image.Image, width: int, height: int) -> Image.Image:
    if image.size == (width, height):
        return image
    if image.size[0] >= width and image.size[1] >= height:
        return image.crop((0, 0, width, height))
    return image.resize((width, height), Image.Resampling.LANCZOS)


def _web_run_status(evidence: DemoEvidence) -> str:
    result = evidence.result
    if result is None:
        return "ran_tournament_model"
    if evidence.spec.algorithm in {"Minimax", "Alpha-Beta Pruning", "Expectimax"}:
        return "decision_policy_demo"
    if result.success and result.goal_reached:
        return "solved_optimal" if result.optimality_proven else "solved_not_optimal"
    if result.success:
        return "ran_model_not_goal_path"
    return "not_solved_in_demo"


def _browser(args: list[str], *, check: bool = True) -> subprocess.CompletedProcess:
    executable = _agent_browser_executable()
    return subprocess.run([executable, *args], cwd=ROOT, check=check, text=True)


def _agent_browser_executable() -> str:
    executable = shutil.which("agent-browser") or shutil.which("agent-browser.cmd")
    if executable:
        path = Path(executable)
        if path.suffix.lower() in {".cmd", ".bat", ".ps1"}:
            native = path.parent / "node_modules" / "agent-browser" / "bin" / "agent-browser-win32-x64.exe"
            if native.exists():
                return str(native)
        return executable
    return "agent-browser"


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def _health_ok(port: int) -> bool:
    try:
        with urllib.request.urlopen(f"http://localhost:{port}/_stcore/health", timeout=2) as response:
            return response.read().decode("utf-8", errors="ignore").strip() == "ok"
    except OSError:
        return False


def _start_streamlit(port: int, output_root: Path) -> subprocess.Popen:
    log_dir = output_root / "tmp_visual_checks"
    log_dir.mkdir(parents=True, exist_ok=True)
    stdout = (log_dir / f"streamlit-gif-{port}.log").open("w", encoding="utf-8")
    stderr = (log_dir / f"streamlit-gif-{port}.err.log").open("w", encoding="utf-8")
    process = subprocess.Popen(
        [
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port", str(port),
            "--server.headless", "true",
            "--browser.gatherUsageStats", "false",
        ],
        cwd=ROOT,
        stdout=stdout,
        stderr=stderr,
    )
    deadline = time.time() + 45
    while time.time() < deadline:
        if process.poll() is not None:
            raise RuntimeError(f"Streamlit exited while starting on port {port}")
        if _health_ok(port):
            return process
        time.sleep(0.5)
    process.terminate()
    raise TimeoutError(f"Streamlit did not become healthy on port {port}")


def check_readability(root: Path) -> None:
    for path in (root / "docs/assets").rglob("*.gif"):
        with Image.open(path) as image:
            frames = [frame.convert("RGB") for frame in ImageSequence.Iterator(image)]
        if len(frames) < 6:
            raise AssertionError(f"{path} has too few frames")
        if frames[0].size[0] < PROFILES["group"].width and path.name != "a-star-image-replay.gif":
            raise AssertionError(f"{path} is too narrow for README readability")
        if all(low == high for low, high in frames[0].getextrema()):
            raise AssertionError(f"{path} appears blank")


def write_contact_sheet(root: Path) -> Path:
    gif_paths = sorted((root / "docs/assets/readme").glob("*.gif"))
    gif_paths += sorted((root / "docs/assets/algorithm-demos").glob("*.gif"))
    thumbs: list[tuple[str, Image.Image]] = []
    for path in gif_paths:
        with Image.open(path) as image:
            frame = next(ImageSequence.Iterator(image)).convert("RGB")
        frame.thumbnail((300, 170))
        thumbs.append((path.stem, frame.copy()))
    cols, cell_w, cell_h = 3, 340, 225
    rows = max(1, (len(thumbs) + cols - 1) // cols)
    sheet = Image.new("RGB", (cols * cell_w, rows * cell_h), (18, 22, 20))
    for index, (label, thumb) in enumerate(thumbs):
        col, row = index % cols, index // cols
        x, y = col * cell_w + 20, row * cell_h + 18
        sheet.paste(thumb, (x, y))
    output = root / "tmp_visual_checks/readme-gif-contact-sheet.png"
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output)
    print(f"contact sheet: {output.relative_to(root)}")
    return output


if __name__ == "__main__":
    raise SystemExit(main())
