"""Streamlit integration tests for the web-only learning flow."""

from streamlit.testing.v1 import AppTest

from core.academic_proofs import BENCHMARK_PRESETS
from algorithms.uninformed import bfs
from core.puzzle import GOAL_STATE, validate_solution_path
from ui.play_tab import VICTORY_MESSAGE_KEYS


ONE_MOVE = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 0, 15)
TWO_MOVE = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 0, 11, 13, 14, 15, 12)


def state_text(state):
    return " ".join(str(tile) for tile in state)


def matrix_state_text(state):
    return "\n".join(
        " ".join(str(tile) for tile in state[row_start:row_start + 4])
        for row_start in range(0, 16, 4)
    )


def test_web_app_initial_playground_renders_without_exception():
    app = AppTest.from_file("app.py", default_timeout=10).run()
    assert not app.exception
    markdown_text = "\n".join(getattr(markdown, "value", "") for markdown in app.markdown)
    assert any(
        "Bàn cờ Tương tác" in title.value or "Interactive Board" in title.value
        for title in app.title
    )
    assert app.button(key="btn_ai_solve")
    assert app.button(key="btn_play_reset")
    assert app.button(key="btn_play_undo")
    assert "play-status-grid" in markdown_text
    assert '\n    <div class="play-status-card">' not in markdown_text
    assert "btn_prove_optimal" not in {button.key for button in app.button}
    assert "btn_load_teaching_preset" not in {button.key for button in app.button}
    assert "teaching_preset_select" not in {selectbox.key for selectbox in app.selectbox}
    assert "sidebar-active-contract-grid" not in markdown_text
    assert "Trace từng bước" not in app.radio(key="main_tab_label").options
    assert "Step Trace" not in app.radio(key="main_tab_label").options


def test_vietnamese_navigation_and_advanced_labels_render():
    app = AppTest.from_file("app.py", default_timeout=15).run()

    assert "Chạy thuật toán" in app.radio(key="main_tab_label").options
    assert "Nâng cao" in app.radio(key="main_tab_label").options

    app.radio(key="main_tab_label").set_value("Nâng cao").run()

    assert app.selectbox(key="complex_mode_v2").label == "Thuật toán / Mô hình"
    assert not app.exception


def test_navigation_recovers_from_legacy_string_widget_state():
    app = AppTest.from_file("app.py", default_timeout=15)
    app.session_state["global_lang_select"] = "English"
    app.session_state["main_tab_label"] = "Run Algorithm"
    app.run()

    markdown_text = "\n".join(getattr(markdown, "value", "") for markdown in app.markdown)
    assert app.session_state["main_tab_value"] == "Run Algorithm"
    assert app.radio(key="main_tab_label").value == "Run Algorithm"
    assert "sidebar-active-contract-grid" not in markdown_text
    assert not app.exception


def test_play_image_mode_uses_image_tiles_for_manual_board():
    app = AppTest.from_file("app.py", default_timeout=10).run()

    markdown_values = [getattr(markdown, "value", "") for markdown in app.markdown]

    assert not any('<div class="interactive-board-container-image"></div>' in value for value in markdown_values)
    assert app.session_state.play_board_mode == "number"
    assert app.button(key="btn_play_reset")
    assert not app.session_state.image_tiles

    app.button(key="btn_load_sample").click().run()

    image_markdown_values = [getattr(markdown, "value", "") for markdown in app.markdown]
    assert any(
        '<div class="interactive-board-container-image"></div>' in value
        for value in image_markdown_values
    )
    assert app.session_state.image_tiles
    assert app.session_state.play_board_mode == "image"
    assert not app.exception


def test_play_image_tile_click_moves_without_query_link_reload():
    app = AppTest.from_file("app.py", default_timeout=15).run()
    app.button(key="btn_load_sample").click().run()
    app.session_state.start_state = ONE_MOVE
    app.run()

    markdown_values = [getattr(markdown, "value", "") for markdown in app.markdown]
    style_blob = "\n".join(markdown_values)
    assert ".st-key-play_main_image_hit_15 button" in style_blob
    assert ".st-key-play_main_image_hit_15_3_3 button" not in style_blob
    assert ":has(.play-image-button-play_main_image" not in style_blob

    app.button(key="play_main_image_hit_15").click().run()

    assert app.session_state.play_state == GOAL_STATE
    assert app.session_state.play_moves == 1
    assert "play_slide" not in app.query_params
    assert not app.exception


def test_ai_solver_replay_keeps_play_history_certifiable():
    app = AppTest.from_file("app.py", default_timeout=15).run()
    app.session_state.start_state = ONE_MOVE
    app.run()

    app.button(key="btn_ai_solve").click().run()
    app.button(key="btn_play_next").click().run()

    valid, message = validate_solution_path(
        app.session_state.play_history,
        list(app.session_state.play_solution_actions[: len(app.session_state.play_history) - 1]),
        GOAL_STATE,
    )
    assert app.session_state.play_state == GOAL_STATE
    assert app.session_state.play_moves == 1
    assert app.session_state.play_assisted is True
    assert app.session_state.play_victory_message_key in VICTORY_MESSAGE_KEYS
    assert app.session_state.play_victory_balloons_pending is False
    assert valid, message
    assert not app.exception


def test_play_ai_solver_panel_exposes_visible_replay_controls():
    app = AppTest.from_file("app.py", default_timeout=15)
    app.session_state["global_lang_select"] = "English"
    app.session_state["main_tab_label"] = "Play Puzzle"
    app.session_state["start_state"] = ONE_MOVE
    app.run()

    markdown_text = "\n".join(getattr(markdown, "value", "") for markdown in app.markdown)
    caption_text = "\n".join(getattr(caption, "value", "") for caption in app.caption)

    assert "hands-on puzzle work" in markdown_text
    assert "Click Find Solution" in caption_text
    assert "A* Search" in markdown_text
    assert "f(n)=g(n)+h(n)" in markdown_text
    assert "Manhattan Distance" in markdown_text

    app.button(key="btn_ai_solve").click().run()

    solved_markdown_text = "\n".join(getattr(markdown, "value", "") for markdown in app.markdown)
    expander_labels = [expander.label for expander in app.expander]
    assert app.session_state.play_solution_path
    assert "A* Node / Frontier / Reached Evidence" in expander_labels
    assert "Search Tree Visualization" in solved_markdown_text
    assert "search-tree-readable" in solved_markdown_text
    assert "Current A* replay step" in solved_markdown_text
    assert "play-ai-evidence-grid" in solved_markdown_text
    assert "Frontier / Reached" in solved_markdown_text
    assert app.button(key="btn_play_next")
    assert app.button(key="btn_play_auto")

    assert app.session_state.play_solution_idx == 0
    assert app.session_state.play_state == app.session_state.play_solution_path[0]
    assert app.session_state.play_auto_run is False
    success_values = [getattr(success, "value", "") for success in app.success]
    assert "AI Auto-solving complete!" not in success_values

    app.button(key="btn_play_next").click().run()
    assert app.session_state.play_solution_idx == 1
    assert app.session_state.play_state == GOAL_STATE
    assert app.session_state.play_victory_message_key in VICTORY_MESSAGE_KEYS
    assert not app.exception


def test_play_image_mode_is_available_in_the_main_workbench():
    app = AppTest.from_file("app.py", default_timeout=15)
    app.session_state["global_lang_select"] = "English"
    app.session_state["main_tab_label"] = "Play Puzzle"
    app.run()

    assert app.session_state["play_board_mode"] == "number"

    app.radio(key="play_board_mode_choice").set_value("Image puzzle").run()

    markdown_text = "\n".join(getattr(markdown, "value", "") for markdown in app.markdown)
    assert "interactive-board-container-image" in markdown_text
    assert app.session_state["image_tiles"]
    assert app.session_state["image_active"] is True
    assert app.session_state["play_board_mode"] == "image"
    assert app.session_state["play_board_mode_choice"] == "Image puzzle"
    assert not app.exception


def test_play_ai_replay_updates_the_main_image_board_step_by_step():
    app = AppTest.from_file("app.py", default_timeout=15)
    app.session_state["global_lang_select"] = "English"
    app.session_state["main_tab_label"] = "Play Puzzle"
    app.session_state["start_state"] = TWO_MOVE
    app.session_state["image_tiles"] = {
        tile: "data:image/png;base64,iVBORw0KGgo="
        for tile in range(1, 16)
    }
    app.session_state["image_active"] = True
    app.session_state["play_board_mode"] = "image"
    app.run()

    app.button(key="btn_ai_solve").click().run()

    markdown_text = "\n".join(getattr(markdown, "value", "") for markdown in app.markdown)
    assert "interactive-board-container-image" in markdown_text
    assert "solution-step-mode-image" in markdown_text
    assert "puzzle-grid-mini-image" in markdown_text
    assert "solution-mini-image-tile" in markdown_text
    assert '<img src="data:image' not in markdown_text
    assert "--play-image-tile-solution-step-1" in markdown_text
    assert "--play-image-tile-search-tree-1" in markdown_text
    assert app.session_state.play_solution_idx == 0
    assert app.session_state.play_state == app.session_state.play_solution_path[0]

    app.button(key="btn_play_next").click().run()
    assert app.session_state.play_solution_idx == 1
    assert app.session_state.play_state == app.session_state.play_solution_path[1]
    assert not app.exception


def test_play_auto_replay_advances_one_step_per_tick():
    app = AppTest.from_file("app.py", default_timeout=15)
    app.session_state["global_lang_select"] = "English"
    app.session_state["main_tab_label"] = "Play Puzzle"
    app.session_state["start_state"] = TWO_MOVE
    app.run()

    app.button(key="btn_ai_solve").click().run()
    assert len(app.session_state.play_solution_path) == 3
    assert app.session_state.play_solution_idx == 0
    assert app.session_state.play_state == app.session_state.play_solution_path[0]
    assert app.session_state.play_auto_run is False

    app.button(key="btn_play_auto").click().run()
    assert app.session_state.play_solution_idx == 0
    assert app.session_state.play_state == app.session_state.play_solution_path[0]
    assert app.session_state.play_auto_run is True

    app.run()
    assert app.session_state.play_solution_idx == 1
    assert app.session_state.play_state == app.session_state.play_solution_path[1]
    assert app.session_state.play_auto_run is True

    app.run()
    assert app.session_state.play_solution_idx == 2
    assert app.session_state.play_state == app.session_state.play_solution_path[2]
    assert app.session_state.play_auto_run is False
    assert not app.exception


def test_play_replay_slider_can_jump_without_session_state_exception():
    app = AppTest.from_file("app.py", default_timeout=15)
    app.session_state["global_lang_select"] = "English"
    app.session_state["main_tab_label"] = "Play Puzzle"
    app.session_state["start_state"] = TWO_MOVE
    app.run()

    app.button(key="btn_ai_solve").click().run()
    slider_key = f"play_slider_val_{app.session_state.play_slider_version}"
    app.slider(key=slider_key).set_value(2).run()

    assert app.session_state.play_solution_idx == 2
    assert app.session_state.play_state == app.session_state.play_solution_path[2]
    assert app.session_state.play_state == GOAL_STATE
    assert not app.exception


def test_play_ai_solution_exposes_the_verified_step_order():
    app = AppTest.from_file("app.py", default_timeout=15)
    app.session_state["global_lang_select"] = "English"
    app.session_state["main_tab_label"] = "Play Puzzle"
    app.session_state["start_state"] = TWO_MOVE
    app.run()

    app.button(key="btn_ai_solve").click().run()

    markdown_text = "\n".join(getattr(markdown, "value", "") for markdown in app.markdown)
    assert "Verified solution steps" in markdown_text
    assert "solution-step-table-wrap" in markdown_text
    assert "solution-step-mode-number" in markdown_text
    assert "solution-step-list" in markdown_text
    assert "solution-step-board" in markdown_text
    assert '<div class="puzzle-grid-mini puzzle-grid-mini-image">' not in markdown_text
    assert "--play-image-tile-solution-step-1" not in markdown_text
    assert "&lt;tr" not in markdown_text
    assert 'style="border-bottom' not in markdown_text
    assert not app.exception


def test_play_ai_search_detail_controls_advance_step():
    app = AppTest.from_file("app.py", default_timeout=15)
    app.session_state["global_lang_select"] = "English"
    app.session_state["main_tab_label"] = "Play Puzzle"
    app.session_state["start_state"] = TWO_MOVE
    app.run()

    app.button(key="btn_ai_solve").click().run()
    app.button(key="play_ai_detail_step_slider_next").click().run()

    markdown_text = "\n".join(getattr(markdown, "value", "") for markdown in app.markdown)
    assert app.session_state["play_ai_detail_step_slider"] == 1
    assert "Trace row: 1/" in markdown_text
    assert "Algorithm step:" in markdown_text
    assert app.session_state.play_solution_res.trace
    assert app.session_state.play_solution_res.search_tree_edges
    assert not app.exception


def test_reset_clears_ai_assistance_disclosure():
    app = AppTest.from_file("app.py", default_timeout=15).run()
    app.session_state.start_state = ONE_MOVE
    app.run()

    app.button(key="btn_ai_solve").click().run()
    app.button(key="btn_play_next").click().run()
    assert app.session_state.play_assisted is True

    reset_button = next(
        button for button in app.button
        if button.label in {"Đặt lại bàn chơi", "Reset Play Board"}
    )
    reset_button.click().run()

    assert app.session_state.play_assisted is False
    assert app.session_state.play_history == [ONE_MOVE]
    assert app.session_state.play_moves == 0
    assert not app.exception


def test_start_state_change_clears_stale_ai_replay():
    app = AppTest.from_file("app.py", default_timeout=15).run()
    app.session_state.start_state = ONE_MOVE
    app.run()

    app.button(key="btn_ai_solve").click().run()
    assert app.session_state.play_solution_path
    slider_key = f"play_slider_val_{app.session_state.play_slider_version}"
    assert slider_key in app.session_state

    app.session_state.start_state = TWO_MOVE
    app.run()

    assert app.session_state.play_state == TWO_MOVE
    assert app.session_state.play_history == [TWO_MOVE]
    assert app.session_state.play_moves == 0
    assert app.session_state.play_solution_path is None
    assert app.session_state.play_solution_actions is None
    assert app.session_state.play_solution_res is None
    assert app.session_state.play_auto_run is False
    assert "play_victory_message_key" not in app.session_state
    assert "play_slider_val" not in app.session_state
    assert app.session_state.play_slider_version == 0
    assert slider_key not in app.session_state
    assert not app.exception


def test_standard_solver_run_renders_verified_search_evidence():
    app = AppTest.from_file("app.py", default_timeout=15)
    app.session_state["start_state"] = ONE_MOVE
    app.session_state["global_lang_select"] = "English"
    app.session_state["main_tab_label"] = "Run Algorithm"
    app.run()
    app.button(key="btn_run").click().run()

    result = app.session_state.last_result
    assert result.algorithm == "BFS"
    assert result.success and result.path_verified
    assert result.search_tree_edges
    assert result.random_seed is not None
    assert sorted(result.variation_action_order) == ["D", "L", "R", "U"]
    expander_labels = [expander.label for expander in app.expander]
    run_expanders = [
        label
        for label in expander_labels
        if label in {
            "Academic Evaluation",
            "Solution Path",
            "Trace Steps",
            "Node / Frontier / Reached Detail",
        }
    ]
    assert run_expanders == [
        "Academic Evaluation",
        "Solution Path",
        "Trace Steps",
        "Node / Frontier / Reached Detail",
    ]
    subheaders = [getattr(subheader, "value", "") for subheader in app.subheader]
    markdown_values = "\n".join(getattr(markdown, "value", "") for markdown in app.markdown)
    caption_values = "\n".join(getattr(caption, "value", "") for caption in app.caption)

    assert "Live Node / Frontier / Reached Replay" in subheaders
    assert "Search Tree Visualization" in markdown_values
    assert "current node, frontier, reached set, and search tree visible" in caption_values
    zoom_key = "search_tree_graphviz_zoom_BFS-24"
    assert app.slider(key=zoom_key).value == 150
    assert app.button(key=f"{zoom_key}_out")
    assert app.button(key=f"{zoom_key}_in")
    assert app.button(key=f"{zoom_key}_fit")

    app.button(key=f"{zoom_key}_in").click().run()
    assert app.session_state[zoom_key] == 175
    zoom_markup = "\n".join(getattr(item, "value", "") for item in app.markdown)
    assert "width: 175% !important" in zoom_markup

    app.button(key=f"{zoom_key}_fit").click().run()
    assert app.session_state[zoom_key] == 100
    assert not app.exception


def test_run_contract_editor_updates_start_and_goal_and_clears_stale_result():
    app = AppTest.from_file("app.py", default_timeout=15)
    app.session_state["start_state"] = ONE_MOVE
    app.session_state["global_lang_select"] = "English"
    app.session_state["main_tab_label"] = "Run Algorithm"
    app.run()
    app.button(key="btn_run").click().run()
    assert "last_result" in app.session_state

    app.text_area(key="active_contract_start_manual_input").set_value(state_text(TWO_MOVE)).run()
    app.button(key="active_contract_apply_start").click().run()

    assert app.session_state.start_state == TWO_MOVE
    assert "last_result" not in app.session_state
    assert app.session_state.benchmark_results == []

    app.text_area(key="active_contract_goal_manual_input").set_value(state_text(ONE_MOVE)).run()
    app.button(key="active_contract_apply_goal").click().run()

    assert app.session_state.goal_state == ONE_MOVE
    assert not app.exception


def test_run_contract_editor_displays_start_and_goal_as_4x4_matrices():
    app = AppTest.from_file("app.py", default_timeout=15)
    app.session_state["start_state"] = TWO_MOVE
    app.session_state["goal_state"] = GOAL_STATE
    app.session_state["global_lang_select"] = "English"
    app.session_state["main_tab_label"] = "Run Algorithm"
    app.run()

    assert app.text_area(key="active_contract_start_manual_input").value == matrix_state_text(TWO_MOVE)
    assert app.text_area(key="active_contract_goal_manual_input").value == matrix_state_text(GOAL_STATE)
    assert "one row per line" in app.text_area(key="active_contract_start_manual_input").label
    assert "one row per line" in app.text_area(key="active_contract_goal_manual_input").label
    markdown_text = "\n".join(getattr(item, "value", "") for item in app.markdown)
    assert markdown_text.count("start-goal-matrix-preview") >= 2
    assert 'data-state-role="start"' in markdown_text
    assert 'data-state-role="goal"' in markdown_text
    assert not app.exception


def test_run_tab_exposes_canonical_complex_environment_group():
    app = AppTest.from_file("app.py", default_timeout=15)
    app.session_state["start_state"] = ONE_MOVE
    app.session_state["global_lang_select"] = "English"
    app.session_state["main_tab_label"] = "Run Algorithm"
    app.run()

    assert app.selectbox(key="algo_group").options == [
        "Uninformed Search",
        "Informed Search",
        "Local Search",
        "Complex Environments",
        "CSP",
        "AI-vs-AI Tournament",
    ]

    app.selectbox(key="algo_group").set_value("Complex Environments").run()

    assert app.selectbox(key="algo_name").options == [
        "AND-OR Search",
        "Searching with no observation",
        "Searching for partially observable problems",
        "LRTA*",
    ]
    assert app.selectbox(key="algo_name").value == "AND-OR Search"
    assert not [widget for widget in app.slider if widget.key == "run_andor_prob"]
    assert app.radio(key="run_andor_deflection_mode").options == [
        "Intended outcome only",
        "Include all legal deflections",
    ]
    assert app.radio(key="run_andor_deflection_mode").value == "Intended outcome only"
    assert not app.exception


def test_run_tab_runs_added_complex_environment_algorithms():
    cases = [
        ("Searching with no observation", "Searching with no observation"),
        ("Searching for partially observable problems", "Searching for partially observable problems"),
    ]
    for label, expected_algorithm in cases:
        app = AppTest.from_file("app.py", default_timeout=15)
        app.session_state["start_state"] = ONE_MOVE
        app.session_state["global_lang_select"] = "English"
        app.session_state["main_tab_label"] = "Run Algorithm"
        app.run()
        app.selectbox(key="algo_group").set_value("Complex Environments").run()
        app.selectbox(key="algo_name").set_value(label).run()
        app.number_input(key="max_depth").set_value(1).run()

        app.button(key="btn_run").click().run()

        assert app.session_state.last_result.algorithm == expected_algorithm
        assert not app.exception


def test_run_and_or_deterministic_support_outputs_conditional_plan_without_goal_claim():
    app = AppTest.from_file("app.py", default_timeout=15)
    app.session_state["start_state"] = ONE_MOVE
    app.session_state["global_lang_select"] = "English"
    app.session_state["main_tab_label"] = "Run Algorithm"
    app.run()
    app.selectbox(key="algo_group").set_value("Complex Environments").run()
    app.number_input(key="max_depth").set_value(1).run()
    app.radio(key="run_andor_deflection_mode").set_value("Intended outcome only").run()

    app.button(key="btn_run").click().run()

    result = app.session_state.last_result
    markdown_text = "\n".join(getattr(markdown, "value", "") for markdown in app.markdown)

    assert result.algorithm == "AND-OR Search"
    assert result.success
    assert "Conditional plan found" in result.message
    assert "OR: choose action" in result.message
    assert not result.goal_reached
    assert not result.optimality_proven
    assert result.actions == []
    assert "OR node" in markdown_text
    assert "AND node" in markdown_text
    assert "conditional plan, not a linear 15-puzzle path" in markdown_text
    assert not app.exception


def test_run_and_or_deflection_support_requires_all_outcomes():
    app = AppTest.from_file("app.py", default_timeout=15)
    app.session_state["start_state"] = ONE_MOVE
    app.session_state["global_lang_select"] = "English"
    app.session_state["main_tab_label"] = "Run Algorithm"
    app.run()
    app.selectbox(key="algo_group").set_value("Complex Environments").run()
    app.number_input(key="max_depth").set_value(1).run()
    app.radio(key="run_andor_deflection_mode").set_value("Include all legal deflections").run()

    app.button(key="btn_run").click().run()

    result = app.session_state.last_result

    assert result.algorithm == "AND-OR Search"
    assert not result.success
    assert "No conditional plan found" in result.message
    assert not result.goal_reached
    assert not result.optimality_proven
    assert result.nodes_expanded > 0
    assert result.nodes_generated > 1
    assert not app.exception


def test_advanced_and_or_uses_deflection_mode_radio():
    app = AppTest.from_file("app.py", default_timeout=15)
    app.session_state["start_state"] = ONE_MOVE
    app.session_state["global_lang_select"] = "English"
    app.session_state["main_tab_label"] = "Advanced Mode"
    app.run()
    app.selectbox(key="complex_mode_v2").set_value("AND-OR Search (Nondeterministic)").run()

    assert not [widget for widget in app.slider if widget.key == "andor_prob"]
    assert app.radio(key="andor_deflection_mode").options == [
        "Intended outcome only",
        "Include all legal deflections",
    ]

    app.number_input(key="andor_depth").set_value(1).run()
    app.radio(key="andor_deflection_mode").set_value("Intended outcome only").run()
    app.button(key="adv_run_and_or_search__nondeterministic").click().run()

    result = app.session_state.advanced_outputs[0]["result"]
    assert result.algorithm == "AND-OR Search"
    assert result.success
    assert "not probability-weighted" in result.message
    assert not app.exception


def test_run_lrta_caption_explains_node_cap_as_online_steps():
    app = AppTest.from_file("app.py", default_timeout=15)
    app.session_state["start_state"] = ONE_MOVE
    app.session_state["global_lang_select"] = "English"
    app.session_state["main_tab_label"] = "Run Algorithm"
    app.run()
    app.selectbox(key="algo_group").set_value("Complex Environments").run()
    app.selectbox(key="algo_name").set_value("LRTA*").run()

    caption_text = "\n".join(getattr(caption, "value", "") for caption in app.caption)
    assert "maximum number of online action steps" in caption_text
    assert not app.exception


def test_run_no_observation_uses_known_tile_belief_controls():
    app = AppTest.from_file("app.py", default_timeout=15)
    app.session_state["start_state"] = ONE_MOVE
    app.session_state["global_lang_select"] = "English"
    app.session_state["main_tab_label"] = "Run Algorithm"
    app.run()
    app.selectbox(key="algo_group").set_value("Complex Environments").run()
    app.selectbox(key="algo_name").set_value("Searching with no observation").run()

    known_matrix = app.text_area(key="no_observation_search_known_matrix")
    assert known_matrix.label == "Known tiles matrix"
    assert known_matrix.value == "_ _ _ _\n_ _ _ _\n_ _ _ _\n_ _ _ _"
    assert app.selectbox(key="no_observation_search_belief_planner").options == [
        "BFS",
        "A* Search",
        "Stochastic Hill Climbing",
    ]

    app.text_area(key="no_observation_search_known_matrix").set_value(
        "1 2 _ _\n_ _ _ _\n_ _ _ _\n_ _ _ _"
    ).run()
    app.selectbox(key="no_observation_search_belief_planner").set_value("BFS").run()
    app.button(key="btn_run").click().run()

    result = app.session_state.last_result
    reasons = " ".join(step.reason for step in result.trace)
    assert result.algorithm == "Searching with no observation"
    assert "known positions=2" in reasons
    assert "planner=BFS" in reasons
    assert not app.exception


def test_advanced_partial_observation_accepts_two_known_tiles_matrix():
    app = AppTest.from_file("app.py", default_timeout=15)
    app.session_state["start_state"] = ONE_MOVE
    app.session_state["global_lang_select"] = "English"
    app.session_state["main_tab_label"] = "Advanced Mode"
    app.run()
    app.selectbox(key="complex_mode_v2").set_value("Partially Observable").run()

    app.text_area(key="po_known_matrix").set_value(
        "1 2 _ _\n_ _ _ _\n_ _ _ _\n_ _ _ _"
    ).run()
    app.selectbox(key="po_belief_planner").set_value("BFS").run()
    app.button(key="adv_run_partially_observable").click().run()

    result = app.session_state.advanced_outputs[0]["result"]
    reasons = " ".join(step.reason for step in result.trace)
    assert "known positions=2" in reasons
    assert "planner=BFS" in reasons
    assert not app.exception


def test_run_local_search_renders_candidate_evaluation_evidence():
    app = AppTest.from_file("app.py", default_timeout=15)
    app.session_state["start_state"] = TWO_MOVE
    app.session_state["global_lang_select"] = "English"
    app.session_state["main_tab_label"] = "Run Algorithm"
    app.run()
    app.selectbox(key="algo_group").set_value("Local Search").run()
    app.button(key="btn_run").click().run()

    result = app.session_state.last_result
    assert any("Evaluate candidate" in step.reason for step in result.trace)
    assert any(
        "Evaluate candidate" in str(getattr(table, "value", ""))
        for table in app.dataframe
    )
    assert not app.exception


def test_repeated_standard_solver_runs_get_fresh_variation_metadata():
    app = AppTest.from_file("app.py", default_timeout=15)
    app.session_state["start_state"] = ONE_MOVE
    app.session_state["global_lang_select"] = "English"
    app.session_state["main_tab_label"] = "Run Algorithm"
    app.run()

    app.button(key="btn_run").click().run()
    first = app.session_state.last_result
    first_seed = first.random_seed
    first_order = first.variation_action_order

    app.button(key="btn_run").click().run()
    second = app.session_state.last_result

    assert second.random_seed != first_seed
    assert second.variation_action_order != first_order
    assert sorted(second.variation_action_order) == ["D", "L", "R", "U"]
    assert second.path_verified
    assert not app.exception


def test_solver_run_uses_custom_goal_state():
    app = AppTest.from_file("app.py", default_timeout=15)
    app.session_state["start_state"] = GOAL_STATE
    app.session_state["goal_state"] = ONE_MOVE
    app.session_state["global_lang_select"] = "English"
    app.session_state["main_tab_label"] = "Run Algorithm"
    app.run()
    app.button(key="btn_run").click().run()

    result = app.session_state.last_result
    assert result.success
    assert result.goal_state == ONE_MOVE
    assert result.path[-1] == ONE_MOVE
    assert result.path_verified
    assert not app.exception


def test_run_solution_animation_controls_do_not_raise_streamlit_state_error():
    app = AppTest.from_file("app.py", default_timeout=15)
    app.session_state["start_state"] = ONE_MOVE
    app.session_state["global_lang_select"] = "English"
    app.session_state["main_tab_label"] = "Run Algorithm"
    app.run()
    app.button(key="btn_run").click().run()

    app.button(key="solution_path_next").click().run()
    assert app.session_state["solution_path_slider"] == 1
    assert not app.exception

    app.button(key="solution_path_prev").click().run()
    assert app.session_state["solution_path_slider"] == 0
    assert not app.exception

    app.button(key="solution_path_next").click().run()
    app.button(key="solution_path_reset").click().run()
    assert app.session_state["solution_path_slider"] == 0
    assert not app.exception

    app.button(key="solution_path_play_btn").click().run()
    assert app.session_state["solution_path_slider"] == 1
    assert not app.exception


def test_run_live_search_detail_controls_advance_step():
    app = AppTest.from_file("app.py", default_timeout=15)
    app.session_state["start_state"] = TWO_MOVE
    app.session_state["global_lang_select"] = "English"
    app.session_state["main_tab_label"] = "Run Algorithm"
    app.run()
    app.button(key="btn_run").click().run()

    app.button(key="run_detail_step_slider_next").click().run()

    assert app.session_state["run_detail_step_slider"] == 1
    assert not app.exception


def test_run_result_is_cleared_when_solver_limits_change():
    app = AppTest.from_file("app.py", default_timeout=15)
    app.session_state["start_state"] = ONE_MOVE
    app.session_state["global_lang_select"] = "English"
    app.session_state["main_tab_label"] = "Run Algorithm"
    app.run()
    app.button(key="btn_run").click().run()

    assert app.session_state.last_result.algorithm == "BFS"

    app.number_input(key="max_nodes").set_value(15000).run()

    assert "last_result" not in app.session_state
    assert not app.exception


def test_run_node_limit_is_bounded_for_readable_layout():
    app = AppTest.from_file("app.py", default_timeout=15)
    app.session_state["global_lang_select"] = "English"
    app.session_state["main_tab_label"] = "Run Algorithm"
    app.run()

    max_nodes_input = app.number_input(key="max_nodes")

    assert max_nodes_input.value == 10000
    assert max_nodes_input.min == 1000
    assert max_nodes_input.max == 20000
    assert max_nodes_input.step == 1000
    assert not app.exception


def test_compare_preset_declares_start_goal_and_recommended_algorithms():
    preset_name = next(iter(BENCHMARK_PRESETS))
    preset = BENCHMARK_PRESETS[preset_name]
    app = AppTest.from_file("app.py", default_timeout=20)
    app.session_state["global_lang_select"] = "English"
    app.session_state["main_tab_label"] = "Compare"
    app.run()

    caption_values = "\n".join(getattr(caption, "value", "") for caption in app.caption)

    assert "Preset start" in caption_values
    assert "Preset goal" in caption_values
    assert preset["comparison_goal"] in caption_values
    assert ", ".join(preset["recommended_algorithms"]) in caption_values
    assert app.multiselect(key="compare_groups").value == list(preset["recommended_groups"])
    for group in preset["recommended_groups"]:
        expected = [
            algorithm
            for algorithm in preset["recommended_algorithms"]
            if algorithm in app.multiselect(key=f"compare_{group}").options
        ]
        assert app.multiselect(key=f"compare_{group}").value == expected

    app.button(key="btn_load_benchmark_preset").click().run()

    assert app.session_state.start_state == preset["start_state"]
    assert app.session_state.goal_state == preset["goal_state"]
    assert not app.exception


def test_stochastic_run_uses_fresh_variation_seed_each_time():
    app = AppTest.from_file("app.py", default_timeout=15)
    app.session_state["start_state"] = ONE_MOVE
    app.session_state["global_lang_select"] = "English"
    app.session_state["main_tab_label"] = "Run Algorithm"
    app.run()
    app.selectbox(key="algo_group").set_value("Local Search").run()
    app.selectbox(key="algo_name").set_value("Stochastic Hill Climbing").run()

    app.button(key="btn_run").click().run()
    first_seed = app.session_state.last_result.random_seed
    first_solver_seed = app.session_state.last_result.variation_solver_seed
    app.button(key="btn_run").click().run()
    second_seed = app.session_state.last_result.random_seed

    assert first_seed is not None
    assert first_solver_seed == first_seed
    assert second_seed is not None
    assert first_seed != second_seed
    caption_text = "\n".join(getattr(item, "value", "") for item in app.caption)
    assert "Run variation:" not in caption_text
    assert "The same seed was passed into the stochastic solver" not in caption_text
    assert not app.exception


def test_compare_records_distinct_seeds_for_stochastic_algorithms():
    app = AppTest.from_file("app.py", default_timeout=20)
    app.session_state["start_state"] = ONE_MOVE
    app.session_state["global_lang_select"] = "English"
    app.session_state["main_tab_label"] = "Compare"
    app.run()
    assert app.multiselect(key="compare_groups").options == [
        "Uninformed Search",
        "Informed Search",
        "Local Search",
        "Complex Environments",
        "CSP",
        "AI-vs-AI Tournament",
    ]
    app.multiselect(key="compare_groups").set_value(["Local Search"]).run()
    app.multiselect(key="compare_Local Search").set_value([
        "Stochastic Hill Climbing",
        "Simulated Annealing",
    ]).run()

    assert app.checkbox(key="fresh_benchmark_seeds").value is True
    app.button(key="btn_benchmark").click().run()

    seeds = app.session_state.benchmark_run_seeds
    assert set(seeds) == {"Stochastic Hill Climbing", "Simulated Annealing"}
    assert len(set(seeds.values())) == 2
    assert all(result.random_seed is not None for result in app.session_state.benchmark_results)
    comparison_frame = app.dataframe[0].value
    for column in ("Recorded Steps", "Cost", "Seed / Mode"):
        assert all(isinstance(value, str) for value in comparison_frame[column])
    assert not app.exception


def test_compare_uses_custom_goal_state_for_standard_solvers():
    app = AppTest.from_file("app.py", default_timeout=20)
    app.session_state["start_state"] = GOAL_STATE
    app.session_state["goal_state"] = ONE_MOVE
    app.session_state["global_lang_select"] = "English"
    app.session_state["main_tab_label"] = "Compare"
    app.run()
    app.multiselect(key="compare_groups").set_value(["Uninformed Search"]).run()
    app.multiselect(key="compare_Uninformed Search").set_value(["BFS"]).run()
    app.button(key="btn_benchmark").click().run()

    result = app.session_state.benchmark_results[0]

    assert result.algorithm == "BFS"
    assert result.goal_state == ONE_MOVE
    assert result.path[-1] == ONE_MOVE
    assert result.path_verified
    assert not app.exception


def test_compare_results_clear_when_benchmark_limits_change():
    preset_name = next(iter(BENCHMARK_PRESETS))
    app = AppTest.from_file("app.py", default_timeout=20)
    app.session_state["start_state"] = ONE_MOVE
    app.session_state["global_lang_select"] = "English"
    app.session_state["main_tab_label"] = "Compare"
    app.run()
    app.multiselect(key="compare_groups").set_value(["Local Search"]).run()
    app.multiselect(key="compare_Local Search").set_value(["Simple Hill Climbing"]).run()
    app.button(key="btn_benchmark").click().run()

    assert app.session_state.benchmark_results

    max_nodes_key = f"compare_max_nodes_{preset_name}"
    app.number_input(key=max_nodes_key).set_value(BENCHMARK_PRESETS[preset_name]["max_nodes"] + 1000).run()

    assert app.session_state.benchmark_results == []
    assert app.session_state.benchmark_run_seeds == {}
    assert not app.exception


def test_theory_tab_renders_within_group_complexity_table():
    app = AppTest.from_file("app.py", default_timeout=20)
    app.session_state["global_lang_select"] = "English"
    app.session_state["main_tab_label"] = "PEAS Theory"
    app.run()

    markdown_values = [getattr(markdown, "value", "") for markdown in app.markdown]
    subheaders = [getattr(subheader, "value", "") for subheader in app.subheader]
    captions = [getattr(caption, "value", "") for caption in app.caption]

    assert any("Within-group algorithm comparison" in value for value in markdown_values)
    assert any("academic worst-case bounds" in value for value in captions)
    assert "Syllabus Coverage Matrix" in subheaders
    assert "Search Foundations" in subheaders
    assert "Tree Search vs Graph Search" in subheaders
    assert "Heuristic Generation" in subheaders
    assert "Hill-Climbing Issues" in subheaders
    assert any("Direct Syllabus Audit" in value for value in markdown_values)
    assert any("Main steps of search algorithms" in value for value in markdown_values)
    assert any("Heuristic functions generation" in value for value in markdown_values)
    assert len(app.dataframe) >= 1
    assert not app.exception


def test_theory_group6_renders_robustness_cross_comparison_and_transferable_concept():
    app = AppTest.from_file("app.py", default_timeout=20)
    app.session_state["global_lang_select"] = "English"
    app.session_state["main_tab_label"] = "PEAS Theory"
    app.run()
    app.selectbox(key="theory_group").set_value("AI-vs-AI Tournament").run()
    app.selectbox(key="theory_algo").set_value("Minimax").run()

    markdown_text = "\n".join(getattr(markdown, "value", "") for markdown in app.markdown)
    caption_text = "\n".join(getattr(caption, "value", "") for caption in app.caption)

    assert "Group 6 robustness / chance comparison" in markdown_text
    assert "worst-case legal continuations" in caption_text
    assert "Transferable concept" in markdown_text
    assert "Zero-sum decision rule" in markdown_text
    assert len(app.dataframe) >= 2
    assert not app.exception


def test_theory_grading_report_preview_does_not_inject_page_headings():
    app = AppTest.from_file("app.py", default_timeout=20)
    app.session_state["global_lang_select"] = "English"
    app.session_state["main_tab_label"] = "PEAS Theory"
    app.run()

    markdown_text = "\n".join(getattr(markdown, "value", "") for markdown in app.markdown)
    code_text = "\n".join(getattr(code, "value", "") for code in app.code)

    assert "15-Puzzle AI Final Exam Grading Report" not in markdown_text
    assert "Current Start State" not in markdown_text
    assert "15-Puzzle AI Final Exam Grading Report" in code_text
    assert "Current Start State" in code_text
    assert not app.exception


def test_advanced_mode_excludes_removed_board_game_and_color_csp_options():
    app = AppTest.from_file("app.py", default_timeout=15)
    app.session_state["global_lang_select"] = "English"
    app.session_state["main_tab_label"] = "Advanced Mode"
    app.run()
    removed_widget_key = "_".join(["graph", "coloring", "map"])
    removed_color_option = "Graph " + "Coloring (Map CSP)"
    removed_game_option = "".join(["Ca", "ro", " / ", "Go", "moku Game"])
    assert not [widget for widget in app.selectbox if widget.key == removed_widget_key]

    options = app.selectbox(key="complex_mode_v2").options
    assert "AI-vs-AI Tournament" in options
    assert removed_color_option not in options
    assert removed_game_option not in options
    assert not app.exception


def test_advanced_minimax_result_uses_worst_case_robustness_framing():
    app = AppTest.from_file("app.py", default_timeout=15)
    app.session_state["start_state"] = ONE_MOVE
    app.session_state["global_lang_select"] = "English"
    app.session_state["main_tab_label"] = "Advanced Mode"
    app.run()
    app.selectbox(key="complex_mode_v2").set_value("Minimax Game").run()
    app.number_input(key="mm_depth").set_value(1).run()
    app.button(key="adv_run_minimax_game").click().run()

    result = app.session_state.advanced_outputs[0]["result"]
    assert "MIN branch models worst-case legal continuations" in result.message
    assert "not a real opponent" in result.message
    assert "tries to obstruct" not in result.message
    assert not app.exception


def test_ai_vs_ai_tournament_runs_from_advanced_mode():
    app = AppTest.from_file("app.py", default_timeout=15)
    app.session_state["start_state"] = ONE_MOVE
    app.session_state["global_lang_select"] = "English"
    app.session_state["main_tab_label"] = "Advanced Mode"
    app.run()
    app.selectbox(key="complex_mode_v2").set_value("AI-vs-AI Tournament").run()
    app.button(key="btn_run_tournament").click().run()

    result = app.session_state.tournament_result
    assert result.rounds[0].optimal_cost == 1
    assert result.rounds[0].agent_a.path_verified
    assert app.slider(key="tournament_replay_round_1_slider")
    assert app.button(key="tournament_replay_round_1_next")
    assert "Search Tree Visualization" in [expander.label for expander in app.expander]
    assert result.winner in {result.agent_a_label, result.agent_b_label, "Draw"}
    assert not app.exception


def test_tournament_replay_advances_both_agents_on_shared_step():
    app = AppTest.from_file("app.py", default_timeout=15)
    app.session_state["start_state"] = ONE_MOVE
    app.session_state["global_lang_select"] = "English"
    app.session_state["main_tab_label"] = "Advanced Mode"
    app.run()
    app.selectbox(key="complex_mode_v2").set_value("AI-vs-AI Tournament").run()
    app.button(key="btn_run_tournament").click().run()

    app.button(key="tournament_replay_round_1_next").click().run()

    assert app.session_state["tournament_replay_round_1_slider"] == 1
    assert not app.exception


def test_tournament_result_clears_when_start_state_changes():
    app = AppTest.from_file("app.py", default_timeout=15)
    app.session_state["start_state"] = ONE_MOVE
    app.session_state["global_lang_select"] = "English"
    app.session_state["main_tab_label"] = "Advanced Mode"
    app.run()
    app.selectbox(key="complex_mode_v2").set_value("AI-vs-AI Tournament").run()
    app.button(key="btn_run_tournament").click().run()
    assert app.session_state.tournament_result

    app.session_state["start_state"] = GOAL_STATE
    app.run()

    assert "tournament_result" not in app.session_state
    assert not app.exception


def test_advanced_backtracking_uses_custom_goal_and_variation_metadata():
    app = AppTest.from_file("app.py", default_timeout=15)
    app.session_state["start_state"] = GOAL_STATE
    app.session_state["goal_state"] = ONE_MOVE
    app.session_state["global_lang_select"] = "English"
    app.session_state["main_tab_label"] = "Advanced Mode"
    app.run()
    app.selectbox(key="complex_mode_v2").set_value("Backtracking Search + Manhattan Distance heuristic").run()
    app.button(key="adv_run_backtracking_search___manhattan_distance_heuristic").click().run()

    outputs = app.session_state.advanced_outputs
    planning = outputs[0]["result"]

    assert planning.algorithm == "Backtracking Search"
    assert planning.goal_state == ONE_MOVE
    assert planning.path_verified
    assert planning.goal_reached
    assert planning.search_tree_edges
    assert planning.random_seed is not None
    assert sorted(planning.variation_action_order) == ["D", "L", "R", "U"]
    assert "Search Tree Visualization" in [expander.label for expander in app.expander]
    assert not app.exception


def test_advanced_partial_observation_renders_observation_evidence():
    app = AppTest.from_file("app.py", default_timeout=15)
    app.session_state["start_state"] = ONE_MOVE
    app.session_state["global_lang_select"] = "English"
    app.session_state["main_tab_label"] = "Advanced Mode"
    app.run()
    app.selectbox(key="complex_mode_v2").set_value("Partially Observable").run()
    app.number_input(key="po_n").set_value(2).run()
    app.number_input(key="po_steps").set_value(5).run()
    assert app.text_area(key="po_known_matrix").value == (
        "1 2 _ _\n_ _ _ _\n_ _ _ _\n_ _ _ _"
    )
    assert app.selectbox(key="po_belief_planner").value == "A* Search"
    app.button(key="adv_run_partially_observable").click().run()

    result = app.session_state.advanced_outputs[0]["result"]
    info_values = "\n".join(getattr(info, "value", "") for info in app.info)
    metric_labels = [metric.label for metric in app.metric]

    assert result.algorithm == "Searching for partially observable problems"
    assert any(step.observation for step in result.trace)
    assert any("known positions=2" in step.reason for step in result.trace)
    assert "Strict criterion" in info_values
    assert "Belief Size" in metric_labels
    assert "Observation" in metric_labels
    assert "Search Tree Visualization" in [expander.label for expander in app.expander]
    assert result.random_seed == result.variation_solver_seed
    assert not app.exception


def test_advanced_csp_ac3_produces_replayable_exact_horizon_path():
    app = AppTest.from_file("app.py", default_timeout=15)
    app.session_state["start_state"] = ONE_MOVE
    app.session_state["global_lang_select"] = "English"
    app.session_state["main_tab_label"] = "Advanced Mode"
    app.run()
    app.selectbox(key="complex_mode_v2").set_value("CSP Definition & Propagation").run()
    app.number_input(key="csp_t").set_value(1).run()
    app.button(key="adv_run_csp_definition___propagation").click().run()

    propagation = app.session_state.advanced_outputs[1]["result"]

    assert propagation.algorithm == "Constraint Propagation"
    assert propagation.actions == ["R"]
    assert propagation.path_verified
    assert propagation.goal_reached
    assert propagation.search_tree_edges
    assert propagation.variation_randomizes_path
    assert "Search Tree Visualization" in [expander.label for expander in app.expander]
    assert "AC-3 State-Chain CSP" in propagation.message
    assert not app.exception


def test_legacy_step_trace_label_redirects_to_run_algorithm():
    app = AppTest.from_file("app.py", default_timeout=15)
    app.session_state["global_lang_select"] = "English"
    app.session_state["main_tab_label"] = "Step Trace"
    app.session_state["last_result"] = bfs(ONE_MOVE, timeout=5)
    app.run()

    assert app.session_state["main_tab_value"] == "Run Algorithm"
    assert app.radio(key="main_tab_label").value == "Run Algorithm"
    assert not app.exception


def test_empty_states_are_actionable_not_blank():
    compare_app = AppTest.from_file("app.py", default_timeout=20)
    compare_app.session_state["global_lang_select"] = "English"
    compare_app.session_state["main_tab_label"] = "Compare"
    compare_app.run()
    compare_markdown = "\n".join(getattr(markdown, "value", "") for markdown in compare_app.markdown)
    compare_info = "\n".join(getattr(info, "value", "") for info in compare_app.info)
    assert "Benchmark table is waiting for a run" in compare_markdown
    assert "Run benchmarks to see the comparison table." not in compare_info
    assert not compare_app.exception

    advanced_app = AppTest.from_file("app.py", default_timeout=15)
    advanced_app.session_state["global_lang_select"] = "English"
    advanced_app.session_state["main_tab_label"] = "Advanced Mode"
    advanced_app.run()
    advanced_markdown = "\n".join(getattr(markdown, "value", "") for markdown in advanced_app.markdown)
    assert "Choose an advanced concept to inspect" in advanced_markdown
    assert advanced_app.button(key="adv_pick_ai_vs_ai_tournament")
    assert not advanced_app.exception

    hand_app = AppTest.from_file("app.py", default_timeout=15)
    hand_app.session_state["global_lang_select"] = "English"
    hand_app.session_state["main_tab_label"] = "Hand-Tracing Practice"
    hand_app.run()
    hand_markdown = "\n".join(getattr(markdown, "value", "") for markdown in hand_app.markdown)
    assert "No hand-tracing challenge is active" in hand_markdown
    assert not hand_app.exception


def test_hand_tracing_exam_path_uses_selected_language():
    app = AppTest.from_file("app.py", default_timeout=15)
    app.session_state["global_lang_select"] = "Tiếng Việt"
    app.session_state["main_tab_label"] = "Luyện chạy tay"
    app.run()
    markdown_text = "\n".join(getattr(markdown, "value", "") for markdown in app.markdown)
    assert "Bước 1" in markdown_text
    assert "STEP 1" not in markdown_text
    assert not app.exception


def test_hand_tracing_builds_explicit_graph_edges():
    app = AppTest.from_file("app.py", default_timeout=15)
    app.session_state["global_lang_select"] = "English"
    app.session_state["main_tab_label"] = "Hand-Tracing Practice"
    app.run()
    app.button(key="btn_ht_generate").click().run()
    app.button(key="btn_choose_0").click().run()

    edges = app.session_state["ht_tree_edges"]
    expanded = app.session_state["ht_expanded_node_ids"]
    records = app.session_state["ht_node_records"]

    assert edges
    assert expanded == ["n0"]
    assert "n0" in records
    assert all(edge["parent"] in records and edge["child"] in records for edge in edges)
    assert not app.exception
