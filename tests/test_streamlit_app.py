"""Streamlit integration tests for the web-only learning flow."""

from streamlit.testing.v1 import AppTest


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
