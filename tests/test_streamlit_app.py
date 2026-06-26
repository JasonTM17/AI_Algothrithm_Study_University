"""Streamlit integration tests for the web-only learning flow."""

from streamlit.testing.v1 import AppTest

from core.academic_proofs import BENCHMARK_PRESETS
from algorithms.uninformed import bfs
from core.gameplay import validate_player_run
from core.puzzle import GOAL_STATE
from ui.trace_tab import trace_rows
from ui.play_tab import VICTORY_MESSAGE_KEYS


ONE_MOVE = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 0, 15)
TWO_MOVE = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 0, 11, 13, 14, 15, 12)


def state_text(state):
    return " ".join(str(tile) for tile in state)


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
    assert app.button(key="btn_prove_optimal")


def test_vietnamese_navigation_and_advanced_labels_render():
    app = AppTest.from_file("app.py", default_timeout=15).run()

    assert "Chạy thuật toán" in app.radio(key="main_tab_label").options
    assert "Nâng cao" in app.radio(key="main_tab_label").options

    app.radio(key="main_tab_label").set_value("Nâng cao").run()

    assert app.selectbox(key="complex_mode_v2").label == "Thuật toán / Mô hình"
    assert not app.exception


def test_play_image_mode_uses_image_tiles_for_manual_board():
    app = AppTest.from_file("app.py", default_timeout=10).run()

    markdown_values = [getattr(markdown, "value", "") for markdown in app.markdown]

    assert not any('<div class="interactive-board-container-image"></div>' in value for value in markdown_values)
    assert any('<div class="interactive-board-container-number"></div>' in value for value in markdown_values)
    assert not app.session_state.image_tiles

    app.button(key="btn_load_sample").click().run()

    image_markdown_values = [getattr(markdown, "value", "") for markdown in app.markdown]
    assert any(
        '<div class="interactive-board-container-image"></div>' in value
        for value in image_markdown_values
    )
    assert app.session_state.image_tiles
    assert not app.exception


def test_play_image_tile_click_moves_without_query_link_reload():
    app = AppTest.from_file("app.py", default_timeout=15).run()
    app.button(key="btn_load_sample").click().run()
    app.session_state.start_state = ONE_MOVE
    app.run()

    markdown_values = [getattr(markdown, "value", "") for markdown in app.markdown]
    style_blob = "\n".join(markdown_values)
    assert ".st-key-play_image_hit_15_3_3 button" in style_blob
    assert ":has(.play-image-button-play_image" not in style_blob

    app.button(key="play_image_hit_15_3_3").click().run()

    assert app.session_state.play_state == GOAL_STATE
    assert app.session_state.play_moves == 1
    assert "play_slide" not in app.query_params
    assert not app.exception


def test_challenge_mode_produces_verified_optimal_certificate():
    app = AppTest.from_file("app.py", default_timeout=10).run()
    app.session_state.start_state = ONE_MOVE
    app.run()
    app.button(key="btn_prove_optimal").click().run()

    proof = app.session_state.play_optimal_result
    assert proof.success
    assert proof.path_verified
    assert proof.optimality_proven
    assert proof.cost == 1
    assert not app.exception


def test_ai_solver_replay_keeps_play_history_certifiable():
    app = AppTest.from_file("app.py", default_timeout=15).run()
    app.session_state.start_state = ONE_MOVE
    app.run()

    app.button(key="btn_ai_solve").click().run()
    app.button(key="btn_play_next").click().run()

    cert = validate_player_run(app.session_state.play_history, GOAL_STATE)
    assert app.session_state.play_state == GOAL_STATE
    assert app.session_state.play_moves == 1
    assert app.session_state.play_assisted is True
    assert app.session_state.play_victory_message_key in VICTORY_MESSAGE_KEYS
    assert app.session_state.play_victory_balloons_pending is False
    assert cert.is_legal
    assert cert.reaches_goal
    assert cert.actions == ("R",)
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
    assert "**A* Search**" not in markdown_text

    app.button(key="btn_ai_solve").click().run()

    solved_markdown_text = "\n".join(getattr(markdown, "value", "") for markdown in app.markdown)
    expander_labels = [expander.label for expander in app.expander]
    assert app.session_state.play_solution_path
    assert "A* Node / Frontier / Reached Evidence" in expander_labels
    assert "Search Tree Visualization" in solved_markdown_text
    assert "Next action" in solved_markdown_text
    assert app.button(key="btn_play_next")
    assert app.button(key="btn_play_auto")

    app.button(key="btn_play_auto").click().run()

    assert app.session_state.play_solution_idx == len(app.session_state.play_solution_path) - 1
    assert app.session_state.play_state == GOAL_STATE
    assert app.session_state.play_victory_message_key in VICTORY_MESSAGE_KEYS
    success_values = [getattr(success, "value", "") for success in app.success]
    assert "AI Auto-solving complete!" in success_values
    assert "Replay reached the requested goal." in success_values
    assert not app.exception


def test_play_ai_search_detail_controls_advance_step():
    app = AppTest.from_file("app.py", default_timeout=15)
    app.session_state["global_lang_select"] = "English"
    app.session_state["main_tab_label"] = "Play Puzzle"
    app.session_state["start_state"] = TWO_MOVE
    app.run()

    app.button(key="btn_ai_solve").click().run()
    app.button(key="play_ai_detail_step_slider_next").click().run()

    assert app.session_state["play_ai_detail_step_slider"] == 1
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


def test_run_tab_exposes_group_3_and_or_extension():
    app = AppTest.from_file("app.py", default_timeout=15)
    app.session_state["start_state"] = ONE_MOVE
    app.session_state["global_lang_select"] = "English"
    app.session_state["main_tab_label"] = "Run Algorithm"
    app.run()

    assert "Group 3 - Complex Environments" in app.selectbox(key="algo_group").options

    app.selectbox(key="algo_group").set_value("Group 3 - Complex Environments").run()

    assert app.selectbox(key="algo_name").options == ["AND-OR Search"]
    assert app.selectbox(key="algo_name").value == "AND-OR Search"
    assert app.slider(key="run_andor_prob").value == 0.3
    assert not app.exception


def test_run_and_or_deterministic_support_outputs_conditional_plan_without_goal_claim():
    app = AppTest.from_file("app.py", default_timeout=15)
    app.session_state["start_state"] = ONE_MOVE
    app.session_state["global_lang_select"] = "English"
    app.session_state["main_tab_label"] = "Run Algorithm"
    app.run()
    app.selectbox(key="algo_group").set_value("Group 3 - Complex Environments").run()
    app.number_input(key="max_depth").set_value(1).run()
    app.slider(key="run_andor_prob").set_value(0.0).run()

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
    app.selectbox(key="algo_group").set_value("Group 3 - Complex Environments").run()
    app.number_input(key="max_depth").set_value(1).run()
    app.slider(key="run_andor_prob").set_value(0.3).run()

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


def test_trace_rows_show_frontier_nodes_not_only_counts():
    result = bfs(TWO_MOVE, timeout=5)

    rows = trace_rows(result.trace)

    frontier_values = [str(row.get("Frontier", "")) for row in rows if row.get("Frontier")]
    assert frontier_values
    assert any(value.startswith("(") and "g=" in value for value in frontier_values)


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
    app.selectbox(key="complex_mode_v2").set_value("Backtracking & Min-Conflicts").run()
    app.button(key="adv_run_backtracking___min_conflicts").click().run()

    outputs = app.session_state.advanced_outputs
    planning = outputs[0]["result"]

    assert planning.algorithm == "Backtracking Search"
    assert planning.goal_state == ONE_MOVE
    assert planning.path_verified
    assert planning.goal_reached
    assert planning.random_seed is not None
    assert sorted(planning.variation_action_order) == ["D", "L", "R", "U"]
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
    app.button(key="adv_run_partially_observable").click().run()

    result = app.session_state.advanced_outputs[0]["result"]
    info_values = "\n".join(getattr(info, "value", "") for info in app.info)
    metric_labels = [metric.label for metric in app.metric]

    assert result.algorithm == "Partially Observable Search"
    assert any(step.observation for step in result.trace)
    assert "Strict criterion" in info_values
    assert "Belief Size" in metric_labels
    assert "Observation" in metric_labels
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
    assert propagation.variation_randomizes_path
    assert "AC-3 State-Chain CSP" in propagation.message
    assert not app.exception


def test_trace_tab_exposes_csv_download():
    app = AppTest.from_file("app.py", default_timeout=15)
    app.session_state["global_lang_select"] = "English"
    app.session_state["main_tab_label"] = "Step Trace"
    app.session_state["last_result"] = bfs(ONE_MOVE, timeout=5)
    app.run()
    rows = trace_rows(app.session_state["last_result"].trace)
    assert rows and "Event" in rows[0]
    assert not app.exception


def test_empty_states_are_actionable_not_blank():
    trace_app = AppTest.from_file("app.py", default_timeout=15)
    trace_app.session_state["global_lang_select"] = "English"
    trace_app.session_state["main_tab_label"] = "Step Trace"
    trace_app.run()
    trace_markdown = "\n".join(getattr(markdown, "value", "") for markdown in trace_app.markdown)
    assert "No Trace has been produced yet" in trace_markdown
    assert trace_app.button(key="trace_empty_go_run")
    assert not trace_app.exception

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
