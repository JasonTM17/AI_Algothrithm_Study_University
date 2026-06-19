"""Streamlit integration tests for the web-only learning flow."""

from streamlit.testing.v1 import AppTest

from algorithms.uninformed import bfs
from core.gameplay import validate_player_run
from core.puzzle import GOAL_STATE
from ui.trace_tab import trace_rows


ONE_MOVE = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 0, 15)


def test_web_app_initial_playground_renders_without_exception():
    app = AppTest.from_file("app.py", default_timeout=10).run()
    assert not app.exception
    assert any("Interactive Board" in title.value for title in app.title)
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

    reset_button = next(button for button in app.button if button.label == "Reset Play Board")
    reset_button.click().run()

    assert app.session_state.play_assisted is False
    assert app.session_state.play_history == [ONE_MOVE]
    assert app.session_state.play_moves == 0
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


def test_graph_coloring_stays_hidden_until_selected():
    app = AppTest.from_file("app.py", default_timeout=15)
    app.session_state["global_lang_select"] = "English"
    app.session_state["main_tab_label"] = "Advanced Mode"
    app.run()
    assert not [widget for widget in app.selectbox if widget.key == "graph_coloring_map"]

    app.selectbox(key="complex_mode_v2").set_value("Graph Coloring (Map CSP)").run()
    maps = [widget for widget in app.selectbox if widget.key == "graph_coloring_map"]
    assert maps
    assert "12" in maps[0].value
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
