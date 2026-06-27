"""Regression tests for verified README and gallery GIF assets."""

from __future__ import annotations

import json
import importlib.util
from pathlib import Path

from PIL import Image, ImageChops, ImageSequence
from streamlit.testing.v1 import AppTest

from scripts.readme_gif_catalog import ALGORITHM_NOTES
from scripts.readme_gif_manifest import check_generated_assets, manifest_record
from scripts.readme_gif_runner import run_demo
from scripts.readme_gif_specs import build_specs, registry_summary
from scripts.readme_gif_styles import PROFILES
from ui.styles import ALGORITHM_GROUPS


ROOT = Path(__file__).resolve().parents[1]
_GENERATOR_SPEC = importlib.util.spec_from_file_location(
    "generate_readme_gifs", ROOT / "scripts/generate-readme-gifs.py"
)
assert _GENERATOR_SPEC and _GENERATOR_SPEC.loader
_GENERATOR_MODULE = importlib.util.module_from_spec(_GENERATOR_SPEC)
_GENERATOR_SPEC.loader.exec_module(_GENERATOR_MODULE)
_web_run_status = _GENERATOR_MODULE._web_run_status


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
    fake_meta = {
        "profile": "algorithm",
        "theme": "dark",
        "source": "live_streamlit_browser_capture",
        "capture_tool": "agent-browser screenshot",
        "frame_count": 6,
        "dimensions": [960, 540],
        "file_bytes": 123,
        "web_run_status": "solved_optimal",
        "result_success": True,
        "result_message": "demo",
    }
    first = []
    second = []
    for spec in build_specs():
        path = Path(f"docs/assets/algorithm-demos/{spec.slug}.gif")
        first.append(manifest_record(run_demo(spec), fake_meta, path))
        second.append(manifest_record(run_demo(spec), fake_meta, path))
    assert first == second


def test_committed_gifs_match_manifest_and_are_nonblank():
    check_generated_assets(ROOT)
    manifest = json.loads((ROOT / "docs/assets/algorithm-demos/manifest.json").read_text(encoding="utf-8"))
    records = {record["path"]: record for record in manifest["records"]}
    allowed_statuses = {
        "solved_optimal",
        "solved_not_optimal",
        "ran_model_not_goal_path",
        "not_solved_in_demo",
        "ran_tournament_model",
    }
    for gif_path in (ROOT / "docs/assets").rglob("*.gif"):
        with Image.open(gif_path) as image:
            frames = [frame.convert("RGB") for frame in ImageSequence.Iterator(image)]
        assert 6 <= len(frames) <= 11
        if "algorithm-demos" in gif_path.parts:
            record = records[gif_path.relative_to(ROOT).as_posix()]
            profile = PROFILES[record["profile"]]
            assert frames[0].size == (profile.width, profile.height)
            assert record["theme"] in {"light", "dark"}
            assert record["source"] == "live_streamlit_browser_capture"
            assert record["capture_tool"] == "agent-browser screenshot"
            assert record["web_run_status"] in allowed_statuses
            assert record["learning_goal"]
            assert record["academic_caveat"]
        else:
            assert frames[0].size in {(1280, 720), (960, 540)}
        assert gif_path.stat().st_size < 3_500 * 1024
        assert ImageChops.difference(frames[0], Image.new("RGB", frames[0].size)).getbbox()


def test_readme_is_academic_atlas_with_all_algorithm_gifs():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert 700 <= len(readme.splitlines()) <= 1150
    assert "JasonTM17" in readme
    assert "docs/algorithm-demo-gallery.md" in readme
    assert "live Streamlit browser capture" in readme
    assert "web_run_status" in readme
    for group in ALGORITHM_GROUPS:
        assert group in readme
    for spec in build_specs():
        assert spec.algorithm in readme
        assert f"docs/assets/algorithm-demos/{spec.slug}.gif" in readme


def test_algorithm_gallery_has_full_academic_metadata():
    gallery = (ROOT / "docs/algorithm-demo-gallery.md").read_text(encoding="utf-8")
    assert "28 GIF" in gallery
    assert "live Streamlit browser capture" in gallery
    assert "web_run_status" in gallery
    for algorithm, note in ALGORITHM_NOTES.items():
        assert algorithm in gallery
        assert note.learning_goal in gallery
        assert note.academic_caveat in gallery


def test_generator_uses_live_streamlit_capture_instead_of_mock_renderer():
    text = (ROOT / "scripts/generate-readme-gifs.py").read_text(encoding="utf-8")
    assert "readme_gif_renderer" not in text
    assert "save_demo_gif" not in text
    assert "agent-browser" in text
    assert "capture_demo" in text
    assert "live_streamlit_browser_capture" in text


def test_web_capture_route_renders_real_streamlit_frame_with_truth_status():
    app = AppTest.from_file("app.py", default_timeout=20)
    app.query_params["capture_demo"] = "bfs"
    app.query_params["capture_frame"] = "0"
    app.run()
    assert not app.exception
    markdown_text = "\n".join(getattr(markdown, "value", "") for markdown in app.markdown)
    assert "Source: live Streamlit browser capture" in markdown_text
    assert "WEB RUN: SOLVED + OPTIMAL" in markdown_text
    assert "capture-ready-bfs-0" in markdown_text
    assert "No mockup renderer" in markdown_text


def test_web_run_status_distinguishes_solution_model_failure_and_tournament():
    statuses = {spec.algorithm: _web_run_status(run_demo(spec)) for spec in build_specs()}
    assert statuses["BFS"] == "solved_optimal"
    assert statuses["A*"] == "solved_optimal"
    assert statuses["AI-vs-AI Tournament"] == "ran_tournament_model"
    assert any(status == "ran_model_not_goal_path" for status in statuses.values())
    assert set(statuses.values()) <= {
        "solved_optimal",
        "solved_not_optimal",
        "ran_model_not_goal_path",
        "not_solved_in_demo",
        "ran_tournament_model",
    }


def test_number_tile_palette_stays_restrained():
    text = (ROOT / "ui/styles.py").read_text(encoding="utf-8")
    noisy_tile_colors = {
        "#dec49a",
        "#a77a4a",
        "#bfd0ad",
        "#697d5f",
        "#d9c6a6",
        "#9b8466",
    }
    assert noisy_tile_colors.isdisjoint(text)
