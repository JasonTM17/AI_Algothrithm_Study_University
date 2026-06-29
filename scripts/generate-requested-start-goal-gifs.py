"""Generate requested IDS, DFS and A* GIFs from the live Streamlit app."""

from __future__ import annotations

import argparse
import importlib.util
import subprocess
import sys
from dataclasses import replace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.puzzle import parse_state, validate_state
from scripts.readme_gif_runner import run_demo
from scripts.readme_gif_specs import get_spec, slugify

_GENERATOR_PATH = ROOT / "scripts/generate-readme-gifs.py"
_GENERATOR_SPEC = importlib.util.spec_from_file_location("generate_readme_gifs", _GENERATOR_PATH)
if _GENERATOR_SPEC is None or _GENERATOR_SPEC.loader is None:
    raise RuntimeError(f"Cannot load {_GENERATOR_PATH}")
_GENERATOR = importlib.util.module_from_spec(_GENERATOR_SPEC)
_GENERATOR_SPEC.loader.exec_module(_GENERATOR)

DEFAULT_START = "2,5,7,3,1,6,11,4,9,10,0,8,13,14,15,12"
DEFAULT_GOAL = "1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,0"
DEFAULT_ALGORITHMS = ("IDS", "DFS", "A*")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", default=DEFAULT_START)
    parser.add_argument("--goal", default=DEFAULT_GOAL)
    parser.add_argument("--algorithm", action="append", choices=DEFAULT_ALGORITHMS)
    parser.add_argument("--output-dir", default="docs/assets/requested-gifs")
    parser.add_argument("--port", type=int)
    parser.add_argument("--keep-server", action="store_true")
    parser.add_argument("--max-depth", type=int, default=80)
    parser.add_argument("--max-nodes", type=int, default=2_000_000)
    parser.add_argument("--timeout", type=float, default=180.0)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    start = parse_state(args.start)
    goal = parse_state(args.goal)
    validate_state(start)
    validate_state(goal)

    output_dir = (ROOT / args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    algorithms = tuple(args.algorithm or DEFAULT_ALGORITHMS)

    server = None
    try:
        port = args.port or _GENERATOR._free_port()
        if not _GENERATOR._health_ok(port):
            server = _GENERATOR._start_streamlit(port, ROOT)
        _GENERATOR._browser(["close", "--all"], check=False)
        _GENERATOR._browser(["open", "about:blank"])

        for algorithm in algorithms:
            spec = _custom_spec(algorithm, start, goal, args)
            evidence = run_demo(spec)
            if not (evidence.path_verified and evidence.goal_reached):
                raise RuntimeError(f"{algorithm} did not produce a verified goal path")

            output_path = output_dir / f"{slugify(algorithm)}-requested-start-goal.gif"
            meta = _GENERATOR._capture_gif(
                evidence,
                output_path,
                base_url=f"http://localhost:{port}",
                profile="algorithm",
                image_mode=False,
                theme="dark",
                output_root=ROOT,
                query_params={
                    "capture_start": args.start,
                    "capture_goal": args.goal,
                    "capture_max_depth": str(args.max_depth),
                    "capture_max_nodes": str(args.max_nodes),
                    "capture_timeout": str(args.timeout),
                },
            )
            relative = output_path.relative_to(ROOT)
            print(
                f"captured {relative} "
                f"[{meta['web_run_status']}, frames={meta['frame_count']}, bytes={meta['file_bytes']}]"
            )
    finally:
        _GENERATOR._browser(["close", "--all"], check=False)
        if server is not None and not args.keep_server:
            server.terminate()
            try:
                server.wait(timeout=8)
            except subprocess.TimeoutExpired:
                server.kill()
    return 0


def _custom_spec(
    algorithm: str,
    start: tuple[int, ...],
    goal: tuple[int, ...],
    args: argparse.Namespace,
):
    spec = get_spec(algorithm)
    params = dict(spec.params)
    params.update(
        {
            "max_nodes": args.max_nodes,
            "timeout": args.timeout,
        }
    )
    if algorithm in {"DFS", "IDS"}:
        params["max_depth"] = args.max_depth
    return replace(spec, start=start, goal=goal, params=params, featured_slug=None)


if __name__ == "__main__":
    raise SystemExit(main())
