"""Regression tests for academic presentation data."""

import inspect
from pathlib import Path

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
from core.algorithm_comparison import (
    ALGORITHM_COMPARISON_ROWS,
    comparison_rows_for_group,
)
from core.syllabus_coverage import (
    HEURISTIC_GENERATION_ROWS,
    HILL_CLIMBING_ISSUE_ROWS,
    REQUIRED_SYLLABUS_TOPICS,
    SEARCH_FOUNDATION_ROWS,
    SYLLABUS_COVERAGE_ROWS,
    TREE_GRAPH_SEARCH_ROWS,
)
from core.theory import THEORY
from core.puzzle import GOAL_STATE, is_solvable, scramble
from core.solver_dispatch import CSP_EXPLANATORY_FUNCTIONS, build_solver_kwargs
from algorithms.informed import a_star, greedy_best_first, ida_star
from algorithms.uninformed import bfs, dfs, ids, ucs
from ui.localization import LOC
from ui.academic_panels import EXAM_PATH_STEPS
from ui.components import comparison_row_for_algorithm, render_clickable_board, render_image_board
from ui.run_and_or_panel import run_algorithm_groups
from ui.sample_images import SAMPLE_IMAGES
from ui.styles import ALGORITHM_GROUPS, COMPARISON_TABLE, STYLES


def test_taxonomy_covers_all_displayed_algorithms():
    displayed = {name for names in ALGORITHM_GROUPS.values() for name in names}

    assert len(displayed) == 28
    assert set(ALGORITHM_TAXONOMY) == displayed
    assert len(taxonomy_rows()) == 28


def test_complexity_comparison_covers_every_algorithm_by_display_group():
    compared = {row["Algorithm"] for row in ALGORITHM_COMPARISON_ROWS}
    displayed = {name for names in ALGORITHM_GROUPS.values() for name in names}

    assert compared == displayed
    for group, algorithms in ALGORITHM_GROUPS.items():
        rows = comparison_rows_for_group(group)
        assert [row["Algorithm"] for row in rows] == algorithms
        for row in rows:
            assert row["Time"]
            assert row["Space"]
            assert row["Steps / output"]
            assert row["Guarantee"]


def test_run_evaluation_table_uses_exact_display_algorithm_names():
    displayed = {name for names in ALGORITHM_GROUPS.values() for name in names}
    evaluation_rows = {row["Algorithm"] for row in COMPARISON_TABLE}

    assert evaluation_rows == displayed
    for algorithm in displayed:
        row = comparison_row_for_algorithm(algorithm)
        assert row is not None
        assert row["Algorithm"] == algorithm


def test_priority_search_sources_match_academic_contracts():
    dfs_source = inspect.getsource(dfs)
    greedy_source = inspect.getsource(greedy_best_first)
    a_star_source = inspect.getsource(a_star)
    ucs_source = inspect.getsource(ucs)

    assert "best_depth: dict" in dfs_source
    assert "child.depth >= prev_depth" in dfs_source
    assert "seen_states = {start}" not in dfs_source
    assert "reject_cycle" in dfs_source
    assert "reject_duplicate" not in dfs_source
    assert "reached = {start}" not in dfs_source
    assert "child.g < reached" not in greedy_source
    assert "best_h: dict[tuple[int, ...], float] = {start: start_h}" in greedy_source
    assert "sorted(frontier)" not in greedy_source
    assert "sorted(frontier)" not in a_star_source
    assert "sorted(frontier)" not in ucs_source


def test_theory_pseudocode_matches_depth_and_heuristic_duplicate_policies():
    assert "best_depth" in THEORY["DFS"]["pseudocode_en"]
    assert "ancestor" in THEORY["DFS"]["pseudocode_en"].lower()
    assert "best_h" in THEORY["Greedy"]["pseudocode_en"]
    assert "Reached set" not in THEORY["Greedy"]["pseudocode_en"]


def test_academic_docs_do_not_restore_stale_search_or_adversary_wording():
    readme = Path("README.md").read_text(encoding="utf-8")
    reference = Path("docs/algorithm-groups-academic-reference.md").read_text(encoding="utf-8")
    combined = f"{readme}\n{reference}"

    assert "code có reached set" not in combined
    assert "MIN làm xấu utility" not in combined
    assert "MIN không phải đối thủ thật" in combined
    assert "binary support switch" in reference


def test_extension_theory_has_real_english_learning_fields():
    fields = tuple(
        f"{field}_en"
        for field in (
            "goal", "idea", "data_structure", "formula", "pseudocode", "application",
            "suitable", "pros", "cons", "complexity", "bad_example", "comparison",
            "exam_tips",
        )
    )
    algorithms = [
        "Simple HC", "Steepest Ascent HC", "Stochastic HC", "Random-Restart HC",
        "Local Beam Search", "Simulated Annealing", "AND-OR", "No Observation",
        "Partially Observable", "LRTA*", "CSP Definition", "Constraint Propagation",
        "Path Consistency", "Global Constraints", "Backtracking Search", "Min-Conflicts",
        "Constraint Graphs",
    ]
    vietnamese_letters = set("ăâđêôơưáàảãạấầẩẫậắằẳẵặéèẻẽẹếềểễệíìỉĩịóòỏõọốồổỗộớờởỡợúùủũụứừửữựýỳỷỹỵ")

    for algorithm in algorithms:
        for field in fields:
            value = THEORY[algorithm].get(field, "")
            assert value, f"{algorithm} is missing {field}"
            text = " ".join(value) if isinstance(value, list) else value
            assert not vietnamese_letters.intersection(text.lower()), (algorithm, field, text)


def test_ui_styles_keep_required_markers_without_duplicate_blocks():
    assert STYLES.count('div[data-testid="stSelectbox"] label p {') == 1
    assert STYLES.count(".ai-contract-grid {") == 2  # desktop + mobile override
    assert STYLES.count(".search-tree-readable-summary {") == 2  # desktop + mobile override
    assert STYLES.count("/* Prevent grey out/dimming of stale elements during script rerun/autoplay */") == 1
    assert "interactive-board-container-image" in STYLES


def test_syllabus_coverage_matrix_covers_uploaded_screenshot_topics():
    required_topics = {
        "Main steps of search algorithms",
        "Tree search and graph search",
        "Uninformed search algorithms",
        "Breadth-first search, Depth-first search and variants",
        "Best-first search",
        "A* search",
        "Heuristic functions generation",
        "Hill-climbing search",
        "Issues of hill-climbing search",
        "Local beam search",
        "Simulated annealing",
        "AND-OR search",
        "Searching with no observation",
        "Searching for partially observable problems",
        "Online search",
        "Definition of a constraint satisfaction problem",
        "Constraint propagation",
        "Path consistency",
        "Global constraints",
        "Backtracking search",
        "Min-conflicts algorithm",
        "Solve CSPs using constraint graphs",
        "Minimax",
        "Alpha-Beta",
        "Expectimax",
    }

    assert required_topics <= set(REQUIRED_SYLLABUS_TOPICS)
    assert len(SYLLABUS_COVERAGE_ROWS) == len(REQUIRED_SYLLABUS_TOPICS)
    for row in SYLLABUS_COVERAGE_ROWS:
        assert row["Syllabus topic"]
        assert row["App surface"]
        assert row["Evidence"]
        assert row["Defense note"]


def test_foundation_panels_have_academic_evidence_rows():
    assert [row["Step"] for row in SEARCH_FOUNDATION_ROWS] == [
        "1. Initial state",
        "2. Goal test",
        "3. Frontier selection",
        "4. Expansion",
        "5. Reached handling",
        "6. Termination/certificate",
    ]
    assert {row["Model"] for row in TREE_GRAPH_SEARCH_ROWS} == {
        "Tree search",
        "Graph search",
        "Hand tracing",
    }
    assert {row["Heuristic"] for row in HEURISTIC_GENERATION_ROWS} == {
        "Misplaced Tiles",
        "Manhattan Distance",
        "Linear Conflict",
    }
    assert {
        "Local optimum",
        "Plateau / shoulder",
        "Ridge",
        "Randomness dependence",
    } <= {row["Issue"] for row in HILL_CLIMBING_ISSUE_ROWS}


def test_csp_backtracking_label_does_not_claim_mrv_lcv():
    backtracking_rows = [
        row for row in COMPARISON_TABLE
        if row["Group"] == "CSP" and row["Algorithm"] == "Backtracking Search"
    ]

    assert backtracking_rows
    assert backtracking_rows[0]["Heuristic"] == "Manhattan Distance"
    assert "MRV+LCV" not in " ".join(str(row) for row in COMPARISON_TABLE)


def test_run_selector_exposes_full_academic_taxonomy_with_extension_caveats():
    groups = run_algorithm_groups(lambda key, **kwargs: key)
    displayed = {name for names in groups.values() for name in names}

    assert groups == ALGORITHM_GROUPS
    assert list(groups) == [
        "Uninformed Search",
        "Informed Search",
        "Local Search",
        "Complex Environments",
        "CSP",
        "AI-vs-AI Tournament",
    ]
    assert "A*" in displayed
    assert "Minimax" in displayed
    assert "AI-vs-AI Tournament" in displayed
    assert "Min-Conflicts" in displayed
    assert "AND-OR Search" in displayed
    for algorithm in ["Minimax", "AI-vs-AI Tournament", "Min-Conflicts", "AND-OR Search"]:
        assert ALGORITHM_TAXONOMY[algorithm].role in {
            ILLUSTRATIVE_EXTENSION,
            STOCHASTIC_GAME_DEMO,
        }


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
        "Searching with no observation",
        "Searching for partially observable problems",
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
        assert preset["start_state"] == first_state
        assert preset["goal_state"] == GOAL_STATE
        assert is_solvable(first_state)
        assert first_state != GOAL_STATE
        assert 0 < preset["max_nodes"] <= 20000
        assert 0 < preset["timeout"] <= 30
        assert preset["heuristic"]
        assert preset["comparison_goal"]
        assert preset["recommended_algorithms"]
        assert preset["expected_outcome"]
        assert preset["caveat"]


def test_recommended_benchmark_algorithms_reach_explicit_goal():
    solver_map = {
        "BFS": bfs,
        "UCS": ucs,
        "IDS": ids,
        "Greedy Best-First": greedy_best_first,
        "A*": a_star,
        "IDA*": ida_star,
    }

    for preset in BENCHMARK_PRESETS.values():
        start = preset["start_state"]
        goal = preset["goal_state"]
        for algorithm in preset["recommended_algorithms"]:
            fn = solver_map[algorithm]
            kwargs = {
                "start": start,
                "goal": goal,
                "timeout": preset["timeout"],
                "action_order": preset.get("action_order", "LRUD"),
            }
            if algorithm in {"BFS", "UCS"}:
                kwargs["max_nodes"] = preset["max_nodes"]
            elif algorithm == "IDS":
                kwargs["max_nodes"] = preset["max_nodes"]
                kwargs["max_depth"] = 30
            else:
                kwargs["max_nodes"] = preset["max_nodes"]
                kwargs["heuristic"] = preset["heuristic"]

            result = fn(**kwargs)

            assert result.success, f"{algorithm} failed preset {preset['comparison_goal']}: {result.message}"
            assert result.goal_state == goal
            assert result.goal_reached
            assert result.path_verified


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


def test_interactive_board_buttons_keep_tile_text_and_touch_stable():
    required_tokens = [
        'button p',
        'color: inherit !important',
        'touch-action: pan-y pinch-zoom',
        'will-change: transform, box-shadow',
        '@media (hover: none)',
        'border-bottom-color: #3d3024',
    ]

    for token in required_tokens:
        assert token in STYLES

    assert 'border-bottom: 2px solid #503720' not in STYLES
    assert 'border-right: 2px solid #503720' not in STYLES
    assert 'div[data-testid="stVerticalBlock"]:has(.interactive-board-container-image) button' not in STYLES
    assert 'number-board-row' not in STYLES
    assert 'div[class*="number_board"] button' in STYLES
    assert 'div[class*="image_board"] div[data-testid="stHorizontalBlock"]' in STYLES
    assert 'grid-template-columns: repeat(4, minmax(0, 1fr))' in STYLES
    assert 'key=f"{key_prefix}_image_board"' in inspect.getsource(render_image_board)
    assert 'row-0' not in STYLES
    assert 'tile-band-0' in STYLES
    assert 'tile-band-' in inspect.getsource(render_clickable_board)
    assert '#b8793e' not in STYLES
    assert '#5f705c' not in STYLES
    assert '#242a27' not in STYLES
    assert 'palette = {' not in inspect.getsource(render_clickable_board)


def test_play_title_compaction_keeps_semantic_heading_accessible():
    title_selector = (
        'div[data-testid="stElementContainer"]:has(h1):has(~ '
        'div[data-testid="stElementContainer"] .play-compact-strip)'
    )
    title_rule = STYLES[STYLES.index(title_selector):STYLES.index(".play-compact-strip h2")]

    assert "position: absolute !important" in title_rule
    assert "clip: rect(0, 0, 0, 0) !important" in title_rule
    assert "display: none !important" not in title_rule


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
    expectimax = THEORY["Expectimax"]
    combined_alpha_beta_text = " ".join(
        str(value) for value in alpha_beta.values()
    )
    combined_minimax_text = " ".join(str(value) for value in minimax.values())

    assert "fully searched" in alpha_beta["comparison_en"]
    assert "timeout" in alpha_beta["comparison_en"]
    assert "finite game tree is searched completely" in minimax["pros_en"][0]
    assert "worst-case robustness" in minimax["transferable_concept_en"]
    assert "Branch-and-bound pruning" in alpha_beta["transferable_concept_en"]
    assert "Expected value under uncertainty" in expectimax["transferable_concept_en"]
    assert "adversary trying to move MAX away from the goal" not in combined_minimax_text
    assert "worst-case branch" in combined_minimax_text
    assert "Yields IDENTICAL results" not in combined_alpha_beta_text
    assert "Complete with evaluation function" not in combined_minimax_text


def test_csp_theory_matches_the_executable_model_boundaries():
    propagation = THEORY["Constraint Propagation"]
    path_consistency_entry = THEORY["Path Consistency"]
    backtracking = THEORY["Backtracking Search"]
    min_conflicts_entry = THEORY["Min-Conflicts"]
    graph = THEORY["Constraint Graphs"]

    assert "exact horizon" in propagation["application_en"]
    assert "does not execute" in path_consistency_entry["application_en"]
    assert "does not provide full MRV" in backtracking["suitable_en"]
    assert "need not be a legal blank move" in min_conflicts_entry["application_en"]
    assert "high-arity factor" in graph["idea_en"]


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
