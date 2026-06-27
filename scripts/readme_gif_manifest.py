"""Manifest and validation helpers for generated README GIFs."""

from __future__ import annotations

import json
import re
from pathlib import Path

from PIL import Image, ImageSequence

from scripts.readme_gif_runner import DemoEvidence
from scripts.readme_gif_specs import FEATURED_SPECS, build_specs


def manifest_record(evidence: DemoEvidence, gif_meta: dict, path: Path) -> dict:
    spec = evidence.spec
    return {
        "algorithm": spec.algorithm,
        "group": spec.group,
        "function": spec.function_name if spec.mode != "tournament" else "run_ai_vs_ai_tournament",
        "slug": spec.slug,
        "path": str(path.as_posix()),
        "start": list(spec.start),
        "goal": list(spec.goal),
        "seed": spec.seed,
        "parameters": spec.params,
        "termination": evidence.termination,
        "path_verified": evidence.path_verified,
        "goal_reached": evidence.goal_reached,
        "optimality_proven": evidence.optimality_proven,
        **gif_meta,
    }


def write_manifest(records: list[dict], output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(
        json.dumps({"records": sorted(records, key=lambda row: row["algorithm"])}, indent=2),
        encoding="utf-8",
    )
    return manifest_path


def check_generated_assets(root: Path) -> None:
    manifest_path = root / "docs/assets/algorithm-demos/manifest.json"
    if not manifest_path.exists():
        raise FileNotFoundError("Missing algorithm GIF manifest")
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    records = data.get("records", [])
    expected = {spec.algorithm for spec in build_specs()}
    actual = {record.get("algorithm") for record in records}
    if actual != expected:
        raise AssertionError(f"Manifest algorithms mismatch: {expected ^ actual}")
    for record in records:
        path = root / record["path"]
        _check_gif(path, record)
    _check_docs_references(root)


def _check_gif(path: Path, record: dict) -> None:
    if not path.exists():
        raise FileNotFoundError(path)
    with Image.open(path) as image:
        frames = sum(1 for _ in ImageSequence.Iterator(image))
        if frames != record["frame_count"]:
            raise AssertionError(f"{path} frame count changed")
        if list(image.size) != record["dimensions"]:
            raise AssertionError(f"{path} dimensions changed")
    if path.stat().st_size != record["file_bytes"]:
        raise AssertionError(f"{path} file size changed")
    if record["file_bytes"] <= 0:
        raise AssertionError(f"{path} is empty")


def _check_docs_references(root: Path) -> None:
    docs = [root / "README.md", root / "docs/algorithm-demo-gallery.md"]
    refs: set[Path] = set()
    display_refs: set[str] = set()
    pattern = re.compile(r"\]\(((?:docs/)?assets/[^)]+\.gif)\)")
    for doc in docs:
        if not doc.exists():
            raise FileNotFoundError(doc)
        for ref in pattern.findall(doc.read_text(encoding="utf-8")):
            display_refs.add(ref)
            refs.add(root / ref if ref.startswith("docs/") else doc.parent / ref)
    required = {f"docs/assets/readme/{slug}.gif" for slug in FEATURED_SPECS}
    missing = required - display_refs
    if missing:
        raise AssertionError(f"README/gallery missing featured refs: {sorted(missing)}")
    for ref in refs:
        if not ref.exists():
            raise FileNotFoundError(ref)
