"""Regression tests for verified README and gallery GIF assets."""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageChops, ImageSequence

from scripts.readme_gif_catalog import ALGORITHM_NOTES
from scripts.readme_gif_manifest import check_generated_assets, manifest_record
from scripts.readme_gif_panel import panel_content
from scripts.readme_gif_renderer import save_demo_gif
from scripts.readme_gif_runner import run_demo
from scripts.readme_gif_styles import PROFILES
from scripts.readme_gif_specs import build_specs, get_spec, registry_summary
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
    fake_meta = {"profile": "algorithm", "theme": "light", "frame_count": 6, "dimensions": [960, 540], "file_bytes": 123}
    for spec in build_specs():
        path = Path(f"docs/assets/algorithm-demos/{spec.slug}.gif")
        first.append(manifest_record(run_demo(spec), fake_meta, path))
        second.append(manifest_record(run_demo(spec), fake_meta, path))
    assert first == second


def test_committed_gifs_match_manifest_and_are_nonblank():
    check_generated_assets(ROOT)
    manifest = json.loads((ROOT / "docs/assets/algorithm-demos/manifest.json").read_text(encoding="utf-8"))
    records = {record["path"]: record for record in manifest["records"]}
    for gif_path in (ROOT / "docs/assets").rglob("*.gif"):
        with Image.open(gif_path) as image:
            frames = [frame.convert("RGB") for frame in ImageSequence.Iterator(image)]
        assert 6 <= len(frames) <= 11
        if "algorithm-demos" in gif_path.parts:
            record = records[gif_path.relative_to(ROOT).as_posix()]
            profile = PROFILES[record["profile"]]
            assert frames[0].size == (profile.width, profile.height)
            assert record["theme"] in {"light", "dark"}
            assert record["learning_goal"]
            assert record["academic_caveat"]
        else:
            assert frames[0].size in {(1280, 720), (960, 540)}
        assert gif_path.stat().st_size < 2_500 * 1024
        assert ImageChops.difference(frames[0], Image.new("RGB", frames[0].size)).getbbox()


def test_readme_is_academic_atlas_with_all_algorithm_gifs():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert 700 <= len(readme.splitlines()) <= 1100
    assert "JasonTM17" in readme
    assert "docs/algorithm-demo-gallery.md" in readme
    for group in ALGORITHM_GROUPS:
        assert group in readme
    for spec in build_specs():
        assert spec.algorithm in readme
        assert f"docs/assets/algorithm-demos/{spec.slug}.gif" in readme
    assert "--theme light" in readme
    assert "--theme dark" in readme


def test_algorithm_gallery_has_full_academic_metadata():
    gallery = (ROOT / "docs/algorithm-demo-gallery.md").read_text(encoding="utf-8")
    assert "28 GIF chạy thật" in gallery
    for algorithm, note in ALGORITHM_NOTES.items():
        assert algorithm in gallery
        assert note.learning_goal in gallery
        assert note.academic_caveat in gallery


def test_renderer_supports_light_and_dark_theme_settings(tmp_path):
    evidence = run_demo(get_spec("BFS"))
    for theme in ("light", "dark"):
        output = tmp_path / f"bfs-{theme}.gif"
        meta = save_demo_gif(evidence, output, profile="algorithm", theme=theme)
        assert meta["theme"] == theme
        assert meta["profile"] == "algorithm"
        with Image.open(output) as image:
            assert image.size == (960, 540)
            first = next(ImageSequence.Iterator(image)).convert("RGB")
        assert ImageChops.difference(first, Image.new("RGB", first.size)).getbbox()


def test_algorithm_gifs_use_group_specific_evidence_panels():
    expected_labels = {
        "BFS": {"FRONTIER", "REACHED", "EXPANDED"},
        "A*": {"G(N)", "H(N)", "F(N)"},
        "Simple Hill Climbing": {"CURRENT H", "CANDIDATES", "STATUS"},
        "AND-OR Search": {"OUTCOMES", "OUTPUT", "DEPTH"},
        "Searching for partially observable problems": {"BELIEF", "PLANNER", "FALLBACK"},
        "LRTA*": {"ONLINE STEP", "VISITED", "CAP"},
        "CSP Definition": {"VARIABLES", "DOMAIN", "HORIZON"},
        "Minimax": {"NODE", "UTILITY", "PRUNED"},
        "Expectimax": {"NODE", "UTILITY", "PRUNED"},
    }
    for algorithm, required in expected_labels.items():
        evidence = run_demo(get_spec(algorithm))
        content = panel_content(evidence, 0)
        labels = {label for label, _, _ in content.metrics}
        assert required <= labels
        assert content.selection
        assert content.explanation


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
