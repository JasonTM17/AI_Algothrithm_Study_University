"""Generate verified GIF assets for README and algorithm gallery."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageSequence

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.readme_gif_manifest import check_generated_assets, manifest_record, write_manifest
from scripts.readme_gif_renderer import save_demo_gif
from scripts.readme_gif_runner import run_demo
from scripts.readme_gif_styles import PROFILES
from scripts.readme_gif_specs import build_specs, featured_specs, get_spec


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--featured", action="store_true", help="Generate hero and six group GIFs.")
    parser.add_argument("--all", action="store_true", help="Generate all 28 algorithm GIFs.")
    parser.add_argument("--algorithm", help="Generate one algorithm GIF by name or slug.")
    parser.add_argument("--check", action="store_true", help="Validate generated assets and manifest.")
    parser.add_argument("--profile", choices=["hero", "group", "algorithm", "all"], default="all",
                        help="Render profile. 'all' uses hero/group/algorithm by asset type.")
    parser.add_argument("--theme", choices=["light", "dark"], default="light",
                        help="Color theme for generated GIFs.")
    parser.add_argument("--contact-sheet", action="store_true", help="Create tmp_visual_checks/readme-gif-contact-sheet.png.")
    parser.add_argument("--check-readability", action="store_true", help="Check GIF dimensions, frames and nonblank pixels.")
    parser.add_argument("--output-dir", default=".", help="Project root or temp output root.")
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

    specs = _selected_specs(args)
    if not specs:
        specs = featured_specs()

    records: list[dict] = []
    for spec in specs:
        evidence = run_demo(spec)
        relative_path, image_mode = _output_path(spec, args, output_root)
        profile = _profile_for(spec, args)
        meta = save_demo_gif(evidence, relative_path, image_mode=image_mode, profile=profile, theme=args.theme)
        records.append(manifest_record(evidence, meta, relative_path.relative_to(output_root)))
        print(f"generated {relative_path.relative_to(output_root)}")

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
    sheet = Image.new("RGB", (cols * cell_w, rows * cell_h), (242, 247, 247))
    draw = ImageDraw.Draw(sheet)
    for index, (label, thumb) in enumerate(thumbs):
        col, row = index % cols, index // cols
        x, y = col * cell_w + 20, row * cell_h + 18
        sheet.paste(thumb, (x, y))
        draw.text((x, y + 176), label[:36], fill=(20, 30, 45))
    output = root / "tmp_visual_checks/readme-gif-contact-sheet.png"
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output)
    print(f"contact sheet: {output.relative_to(root)}")
    return output


if __name__ == "__main__":
    raise SystemExit(main())
