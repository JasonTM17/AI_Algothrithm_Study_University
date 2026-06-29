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
from scripts.render_readme_docs import (
    STANDARD_SOLVER_ALGORITHMS,
    _run_fit_conclusion,
)
from ui.styles import ALGORITHM_GROUPS
import ui.web_gif_capture as web_gif_capture


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
        "specs": 24,
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
        "decision_policy_demo",
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
    assert "Khi thuyết trình" not in readme
    assert readme.count("docs/assets/algorithm-demos/") == 24
    assert "24/24" in readme
    assert "28/28" not in readme
    assert "24 algorithms" in readme
    assert "28 algorithms" not in readme
    assert "LRTA*" not in readme
    assert "Backtracking + Forward Checking" in readme
    assert "AC-3" in readme
    assert "state-chain" in readme
    assert "Complete assignment" in readme
    assert "Frontier/decision rule" in readme
    assert "Same root value as full Minimax" in readme
    assert "decision_policy_demo" in readme
    assert "root decision / policy evidence" in readme
    assert "support switch không phải probability weight" in readme
    for group in ALGORITHM_GROUPS:
        assert group in readme
    for spec in build_specs():
        assert spec.algorithm in readme
        assert f"docs/assets/algorithm-demos/{spec.slug}.gif" in readme


def test_algorithm_gallery_has_full_academic_metadata():
    gallery = (ROOT / "docs/algorithm-demo-gallery.md").read_text(encoding="utf-8")
    assert "24 GIF" in gallery
    assert "28 GIF" not in gallery
    assert "live Streamlit browser capture" in gallery
    assert "web_run_status" in gallery
    assert "Khi thuyết trình" not in gallery
    assert gallery.count('<img src="assets/algorithm-demos/') == 24
    assert "LRTA*" not in gallery
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
    assert statuses["Minimax"] == "decision_policy_demo"
    assert statuses["Alpha-Beta Pruning"] == "decision_policy_demo"
    assert statuses["Expectimax"] == "decision_policy_demo"
    assert any(status == "ran_model_not_goal_path" for status in statuses.values())
    assert set(statuses.values()) <= {
        "solved_optimal",
        "solved_not_optimal",
        "decision_policy_demo",
        "ran_model_not_goal_path",
        "not_solved_in_demo",
        "ran_tournament_model",
    }


def test_each_algorithm_has_an_explicit_truthful_run_and_fit_conclusion():
    expected_standard = {"BFS", "UCS", "IDS", "A*", "IDA*"}
    assert STANDARD_SOLVER_ALGORITHMS == expected_standard

    conclusions = {}
    statuses = {}
    for spec in build_specs():
        evidence = run_demo(spec)
        status = _web_run_status(evidence)
        record = {
            "web_run_status": status,
            "termination": evidence.termination,
        }
        conclusion = _run_fit_conclusion(spec, record)
        conclusions[spec.algorithm] = conclusion
        statuses[spec.algorithm] = status

        assert conclusion
        assert "không chạy được" not in conclusion.lower()
        if status == "solved_optimal":
            assert spec.algorithm in expected_standard
            assert "PHÙ HỢP LÀM SOLVER CHUẨN" in conclusion
        elif status == "solved_not_optimal":
            assert "DEMO TỚI GOAL" in conclusion
            assert "KHÔNG CÓ CHỨNG CHỈ TỐI ƯU" in conclusion
        elif status == "decision_policy_demo":
            assert "DECISION / POLICY EVIDENCE" in conclusion
            assert "shortest solver" in conclusion
        elif status == "not_solved_in_demo":
            assert "CHẠY ĐƯỢC NHƯNG DEMO KHÔNG TỚI GOAL" in conclusion
            assert "không phải crash" in conclusion
        elif status == "ran_model_not_goal_path":
            if spec.algorithm == "AND-OR Search":
                assert "TRẢ CONDITIONAL PLAN" in conclusion
            else:
                assert "CHẾ ĐỘ MÔ HÌNH/EVIDENCE" in conclusion
        elif status == "ran_tournament_model":
            assert "CHẾ ĐỘ CHẤM ĐIỂM" in conclusion

    assert len(conclusions) == 24
    assert sum(value == "not_solved_in_demo" for value in statuses.values()) == 5
    assert sum(value == "ran_model_not_goal_path" for value in statuses.values()) == 3
    assert sum(value == "decision_policy_demo" for value in statuses.values()) == 3


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


def test_capture_progress_never_exceeds_its_semantic_total():
    assert hasattr(web_gif_capture, "_progress_evidence")
    for spec in build_specs():
        evidence = run_demo(spec)
        for frame_index in range(len(evidence.states)):
            progress = web_gif_capture._progress_evidence(evidence, frame_index)
            assert 0 <= progress.current <= progress.total, (
                spec.algorithm,
                progress,
            )
        assert web_gif_capture._progress_evidence(
            evidence,
            len(evidence.states) - 1,
        ).current == web_gif_capture._progress_evidence(
            evidence,
            len(evidence.states) - 1,
        ).total


def test_model_only_demos_do_not_invent_start_goal_trajectories():
    for spec in build_specs():
        evidence = run_demo(spec)
        if evidence.result is not None and not evidence.result.path and not evidence.result.trace:
            assert set(evidence.states) == {spec.start}, spec.algorithm


def test_tournament_capture_replays_a_real_scored_agent_path():
    spec = next(spec for spec in build_specs() if spec.algorithm == "AI-vs-AI Tournament")
    evidence = run_demo(spec)

    assert evidence.path_verified
    assert evidence.goal_reached
    assert evidence.actions
    assert evidence.states[0] == spec.start
    assert evidence.states[-1] == spec.goal
    assert any("replay=" in fact for fact in evidence.facts)


def test_featured_ac3_uses_a_satisfiable_exact_horizon():
    spec = next(spec for spec in build_specs() if spec.algorithm == "AC-3")
    evidence = run_demo(spec)

    assert spec.params["time_horizon"] == 1
    assert evidence.result is not None
    assert evidence.result.success
    assert evidence.result.path_verified
    assert evidence.result.goal_reached


def test_capture_metrics_do_not_invent_path_cost_for_model_extensions():
    for spec in build_specs():
        evidence = run_demo(spec)
        progress = web_gif_capture._progress_evidence(evidence, 0)
        labels = {
            label
            for label, _ in web_gif_capture._capture_metrics(
                evidence,
                evidence.states[0],
                progress,
            )
        }
        if spec.mode in {"csp", "complex", "adversarial", "tournament"}:
            assert "g / h / f" not in labels, spec.algorithm


def test_and_or_and_csp_metrics_name_their_real_evidence():
    by_name = {spec.algorithm: spec for spec in build_specs()}

    and_or = run_demo(by_name["AND-OR Search"])
    and_or_metrics = dict(
        web_gif_capture._capture_metrics(
            and_or,
            and_or.states[-1],
            web_gif_capture._progress_evidence(and_or, len(and_or.states) - 1),
        )
    )
    assert and_or_metrics["Depth limit"] == "2"

    propagation = run_demo(by_name["AC-3"])
    propagation_metrics = dict(
        web_gif_capture._capture_metrics(
            propagation,
            propagation.states[-1],
            web_gif_capture._progress_evidence(
                propagation,
                len(propagation.states) - 1,
            ),
        )
    )
    assert "Arc checks" in propagation_metrics
    assert "Candidate states" in propagation_metrics
    assert "g / h / f" not in propagation_metrics
