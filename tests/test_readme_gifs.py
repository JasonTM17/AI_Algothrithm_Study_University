"""Regression tests for verified README and gallery GIF assets."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageChops, ImageSequence

from scripts.readme_gif_manifest import check_generated_assets, manifest_record
from scripts.readme_gif_runner import run_demo
from scripts.readme_gif_specs import build_specs, registry_summary
from ui.styles import ALGORITHM_GROUPS


ROOT = Path(__file__).resolve().parents[1]


def test_gif_registry_covers_canonical_algorithm_groups():
    summary = registry_summary()
    assert summary == {
        "groups": len(ALGORITHM_GROUPS),
        "algorithms": sum(len(items) for items in ALGORITHM_GROUPS.values()),
        "specs": 28,
    }
    assert {spec.algorithm for spec in build_specs()} == {
        algorithm for algorithms in ALGORITHM_GROUPS.values() for algorithm in algorithms
    }


def test_demo_specs_run_real_algorithm_evidence():
    for spec in build_specs():
        evidence = run_demo(spec)
        assert evidence.states
        assert evidence.termination
        assert evidence.facts
        if spec.expects_goal_path:
            assert evidence.path_verified is True
            assert evidence.goal_reached is True


def test_semantic_manifest_is_deterministic_without_runtime_fields():
    first = []
    second = []
    fake_meta = {"frame_count": 6, "dimensions": [800, 450], "file_bytes": 123}
    for spec in build_specs():
        path = Path(f"docs/assets/algorithm-demos/{spec.slug}.gif")
        first.append(manifest_record(run_demo(spec), fake_meta, path))
        second.append(manifest_record(run_demo(spec), fake_meta, path))
    assert first == second


def test_committed_gifs_match_manifest_and_are_nonblank():
    check_generated_assets(ROOT)
    for gif_path in (ROOT / "docs/assets").rglob("*.gif"):
        with Image.open(gif_path) as image:
            frames = [frame.convert("RGB") for frame in ImageSequence.Iterator(image)]
        assert 6 <= len(frames) <= 10
        assert frames[0].size == (800, 450)
        assert gif_path.stat().st_size < 350 * 1024
        assert ImageChops.difference(frames[0], Image.new("RGB", frames[0].size)).getbbox()


def test_readme_is_short_and_points_to_gallery():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert len(readme.splitlines()) < 300
    assert "JasonTM17" in readme
    assert "docs/algorithm-demo-gallery.md" in readme


def test_number_tile_palette_stays_restrained():
    text = (
        (ROOT / "ui/styles.py").read_text(encoding="utf-8")
        + (ROOT / "scripts/readme_gif_renderer.py").read_text(encoding="utf-8")
    )
    noisy_tile_colors = {
        "#dec49a",
        "#a77a4a",
        "#bfd0ad",
        "#697d5f",
        "#d9c6a6",
        "#9b8466",
    }
    assert noisy_tile_colors.isdisjoint(text)
