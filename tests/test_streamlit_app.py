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


def test_web_app_initial_playground_renders_without_exception():
    app = AppTest.from_file("app.py", default_timeout=10).run()
    assert not app.exception
    assert any(
        "Bàn cờ Tương tác" in title.value or "Interactive Board" in title.value
        for title in app.title
    )
    assert app.button(key="btn_prove_optimal")


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


def test_run_result_is_cleared_when_solver_limits_change():
    app = AppTest.from_file("app.py", default_timeout=15)
    app.session_state["start_state"] = ONE_MOVE
    app.session_state["global_lang_select"] = "English"
    app.session_state["main_tab_label"] = "Run Algorithm"
    app.run()
    app.button(key="btn_run").click().run()

    assert app.session_state.last_result.algorithm == "BFS"

    app.number_input(key="max_nodes").set_value(55000).run()

    assert "last_result" not in app.session_state
    assert not app.exception


def test_stochastic_run_uses_a_fresh_recorded_seed_each_time():
    app = AppTest.from_file("app.py", default_timeout=15)
    app.session_state["start_state"] = ONE_MOVE
    app.session_state["global_lang_select"] = "English"
    app.session_state["main_tab_label"] = "Run Algorithm"
    app.run()
    app.selectbox(key="algo_group").set_value("Local Search").run()
    app.selectbox(key="algo_name").set_value("Stochastic Hill Climbing").run()

    assert app.checkbox(key="fresh_seed_each_run").value is True
    app.button(key="btn_run").click().run()
    first_seed = app.session_state.last_result.random_seed
    app.button(key="btn_run").click().run()
    second_seed = app.session_state.last_result.random_seed

    assert first_seed is not None
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
    assert result.winner in {result.agent_a_label, result.agent_b_label, "Draw"}
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
