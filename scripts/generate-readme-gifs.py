"""Generate verified GIF assets for README and algorithm gallery."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.readme_gif_manifest import check_generated_assets, manifest_record, write_manifest
from scripts.readme_gif_renderer import save_demo_gif
from scripts.readme_gif_runner import run_demo
from scripts.readme_gif_specs import build_specs, featured_specs, get_spec


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--featured", action="store_true", help="Generate hero and six group GIFs.")
    parser.add_argument("--all", action="store_true", help="Generate all 28 algorithm GIFs.")
    parser.add_argument("--algorithm", help="Generate one algorithm GIF by name or slug.")
    parser.add_argument("--check", action="store_true", help="Validate generated assets and manifest.")
    parser.add_argument("--output-dir", default=".", help="Project root or temp output root.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_root = Path(args.output_dir).resolve()
    if args.check and not (args.featured or args.all or args.algorithm):
        check_generated_assets(output_root)
        print("README GIF assets check passed")
        return 0

    specs = _selected_specs(args)
    if not specs:
        specs = featured_specs()

    records: list[dict] = []
    for spec in specs:
        evidence = run_demo(spec)
        relative_path, image_mode = _output_path(spec, args, output_root)
        meta = save_demo_gif(evidence, relative_path, image_mode=image_mode)
        records.append(manifest_record(evidence, meta, relative_path.relative_to(output_root)))
        print(f"generated {relative_path.relative_to(output_root)}")

    if args.all:
        write_manifest(records, output_root / "docs/assets/algorithm-demos")
    if args.check:
        check_generated_assets(output_root)
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


if __name__ == "__main__":
    raise SystemExit(main())
