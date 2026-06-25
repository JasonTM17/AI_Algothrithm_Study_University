"""Regression tests for academic presentation data."""

from core.academic import (
    ALGORITHM_TAXONOMY,
    ILLUSTRATIVE_EXTENSION,
    PEAS_TABLE,
    REAL_SOLVER,
    RECOMMENDATION_RUBRIC,
    STOCHASTIC_GAME_DEMO,
    taxonomy_rows,
)
from core.academic_proofs import (
    BENCHMARK_PRESETS,
    DECISION_GUIDE,
    EXAM_ANSWER_TEMPLATES,
    PROOF_CARDS,
)
from core.academic_report import build_grading_report
from core.theory import THEORY
from core.puzzle import GOAL_STATE, is_solvable, scramble
from core.solver_dispatch import CSP_EXPLANATORY_FUNCTIONS, build_solver_kwargs
from ui.localization import LOC
from ui.academic_panels import EXAM_PATH_STEPS
from ui.sample_images import SAMPLE_IMAGES
from ui.styles import ALGORITHM_GROUPS, SOLVER_GROUPS, STYLES


def test_taxonomy_covers_all_displayed_algorithms():
    displayed = {name for names in ALGORITHM_GROUPS.values() for name in names}

    assert len(displayed) == 28
    assert set(ALGORITHM_TAXONOMY) == displayed
    assert len(taxonomy_rows()) == 28


def test_standard_solver_pages_exclude_extension_environment_models():
    displayed = {name for names in SOLVER_GROUPS.values() for name in names}
    assert "A*" in displayed
    assert "Minimax" not in displayed
    assert "AI-vs-AI Tournament" not in displayed
    assert "Min-Conflicts" not in displayed
    assert "AND-OR Search" not in displayed


def test_real_solvers_are_limited_to_standard_search_algorithms():
    real_solvers = {
        name for name, item in ALGORITHM_TAXONOMY.items()
        if item.role == REAL_SOLVER
    }

    assert real_solvers == {"BFS", "UCS", "IDS", "A*", "IDA*"}


def test_csp_complex_and_game_algorithms_are_not_real_solvers():
    for name in [
        "CSP Definition",
        "Constraint Propagation",
        "Backtracking Search",
        "Min-Conflicts",
        "AND-OR Search",
        "No Observation Search",
        "AI-vs-AI Tournament",
        "Minimax",
        "Alpha-Beta Pruning",
        "Expectimax",
    ]:
        assert ALGORITHM_TAXONOMY[name].role in {
            ILLUSTRATIVE_EXTENSION,
            STOCHASTIC_GAME_DEMO,
        }


def test_removed_board_game_and_color_csp_are_absent_from_academic_surface():
    displayed = {name for names in ALGORITHM_GROUPS.values() for name in names}
    removed_game = "".join(["Ca", "ro", " / ", "Go", "moku"])
    removed_color_csp = "Graph " + "Coloring"

    assert removed_game not in displayed
    assert removed_color_csp not in displayed
    assert "AI-vs-AI Tournament" in displayed


def test_peas_table_has_complete_four_part_model():
    assert [row["PEAS"] for row in PEAS_TABLE] == [
        "Performance",
        "Environment",
        "Actuators",
        "Sensors",
    ]
    for row in PEAS_TABLE:
        assert row["Academic meaning"]
        assert row["15-puzzle instance"]
        assert row["Exam emphasis"]


def test_recommendation_rubric_is_actionable():
    assert len(RECOMMENDATION_RUBRIC) >= 5
    for row in RECOMMENDATION_RUBRIC:
        assert row["Need"]
        assert row["Use"]
        assert row["Avoid"]
        assert row["Reason"]


def test_required_proof_cards_are_present():
    required_cards = {
        "BFS/UCS optimality",
        "Manhattan admissible",
        "Manhattan consistent",
        "Linear Conflict admissible",
        "Solvability parity",
        "Greedy/Hill Climbing failure",
    }

    assert required_cards.issubset(PROOF_CARDS)
    for card in PROOF_CARDS.values():
        assert card["claim"]
        assert card["reason"]
        assert card["exam_use"]


def test_exam_answer_templates_cover_algorithm_groups():
    assert set(EXAM_ANSWER_TEMPLATES) == set(ALGORITHM_GROUPS)
    for template in EXAM_ANSWER_TEMPLATES.values():
        assert template["goal"]
        assert template["frontier"]
        assert template["evaluation"]
        assert template["guarantee"]
        assert template["when_to_use"]
        assert template["when_not_to_use"]


def test_benchmark_presets_are_deterministic_and_solvable():
    assert {"Shallow proof case", "Medium heuristic case", "Heuristic failure case", "Memory pressure case"} <= set(BENCHMARK_PRESETS)

    for preset in BENCHMARK_PRESETS.values():
        first_state = scramble(depth=preset["depth"], seed=preset["seed"])
        second_state = scramble(depth=preset["depth"], seed=preset["seed"])

        assert first_state == second_state
        assert is_solvable(first_state)
        assert first_state != GOAL_STATE
        assert preset["max_nodes"] > 0
        assert preset["timeout"] > 0
        assert preset["heuristic"]
        assert preset["caveat"]


def test_decision_guide_has_actionable_exam_paths():
    assert len(DECISION_GUIDE) >= 4
    for row in DECISION_GUIDE:
        assert row["Question"]
        assert row["Use"]
        assert row["Why"]


def test_csp_explanatory_dispatch_keeps_kwargs_minimal():
    for fn_name in CSP_EXPLANATORY_FUNCTIONS:
        kwargs = build_solver_kwargs(
            fn_name,
            start=GOAL_STATE,
            goal=GOAL_STATE,
            timeout=5,
            action_order="LRUD",
            max_nodes=100,
            max_depth=4,
            heuristic="Manhattan Distance",
        )

        assert kwargs["start"] == GOAL_STATE
        assert kwargs["goal"] == GOAL_STATE
        assert "timeout" not in kwargs
        assert "action_order" not in kwargs
        assert "heuristic" not in kwargs


def test_accessibility_css_contract_is_present():
    required_tokens = [
        "color-scheme: dark",
        "box-sizing: border-box",
        "touch-action: manipulation",
        "focus-visible",
        "prefers-reduced-motion",
        "font-variant-numeric: tabular-nums",
        "exam-path",
    ]

    for token in required_tokens:
        assert token in STYLES


def test_exam_path_covers_grading_workflow():
    steps = [step for step, _, _ in EXAM_PATH_STEPS]

    assert steps == ["Play", "Run", "Compare", "Theory/PEAS", "Hand-Tracing"]


def test_academic_grading_report_contains_required_sections():
    report = build_grading_report(GOAL_STATE, [])

    for section in [
        "PEAS Model",
        "Algorithm Taxonomy",
        "Proof Cards",
        "Benchmark Methodology",
        "Known Limitations",
        "Verification Commands",
    ]:
        assert section in report
    assert "educational extensions" in report
    assert "python -m pytest tests/ -q" in report


def test_game_tree_theory_states_resource_bound_caveats():
    alpha_beta = THEORY["Alpha-Beta"]
    minimax = THEORY["Minimax"]
    combined_alpha_beta_text = " ".join(
        str(value) for value in alpha_beta.values()
    )

    assert "fully searched" in alpha_beta["comparison_en"]
    assert "timeout" in alpha_beta["comparison_en"]
    assert "finite game tree is searched completely" in minimax["pros_en"][0]
    assert "Yields IDENTICAL results" not in combined_alpha_beta_text
    assert "Complete with evaluation function" not in " ".join(str(value) for value in minimax.values())


def test_primary_labels_do_not_use_decorative_emoji():
    forbidden_ranges = [
        range(0x1F000, 0x1FAFF + 1),
    ]
    forbidden_codepoints = {
        0x21A9,
        0x23F5,
        0x23F8,
        0x25B2,
        0x25B6,
        0x25BC,
        0x25C0,
        0x2699,
        0x26A1,
        0x2705,
        0x274C,
    }

    def has_forbidden_symbol(value: str) -> bool:
        return any(
            ord(char) in forbidden_codepoints
            or any(ord(char) in forbidden_range for forbidden_range in forbidden_ranges)
            for char in value
        )

    for language_entries in LOC.values():
        for value in language_entries.values():
            assert not has_forbidden_symbol(value)
    for sample_name in SAMPLE_IMAGES:
        assert not has_forbidden_symbol(sample_name)
