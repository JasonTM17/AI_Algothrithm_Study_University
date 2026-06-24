"""Streamlit UI for the Caro/Gomoku adversarial game demo."""

from __future__ import annotations

import streamlit as st

from algorithms.caro import (
    CaroSearchResult,
    CaroState,
    apply_caro_move,
    caro_alpha_beta,
    caro_minimax,
    create_initial_caro_state,
    evaluate_caro_state,
    legal_caro_moves,
    opponent,
    winner,
)


BOARD_SIZE = 15


def render_caro_game() -> None:
    """Render a compact human-vs-AI Caro board in the Advanced concept lab."""
    st.subheader("Caro / Gomoku Game - Natural adversarial demo")
    st.info(
        "Caro is a real two-player zero-sum game, so Minimax and Alpha-Beta fit "
        "naturally here. The 15-puzzle remains a single-agent solver problem."
    )
    _ensure_state()

    col_a, col_b, col_c, col_d = st.columns(4)
    with col_a:
        algorithm = st.selectbox("AI algorithm", ["Alpha-Beta", "Minimax"], key="caro_algorithm")
    with col_b:
        depth = st.number_input("Search depth", 1, 3, 2, key="caro_depth")
    with col_c:
        human = st.selectbox("Human side", ["X", "O"], key="caro_human_side")
    with col_d:
        if st.button("Reset Caro", key="caro_reset"):
            _reset_state()
            st.session_state.caro_human_side_ref = human

    previous_human = st.session_state.get("caro_human_side_ref")
    if previous_human is None:
        st.session_state.caro_human_side_ref = human
    elif previous_human != human:
        _reset_state()
        st.session_state.caro_human_side_ref = human
        st.info("Side changed; Caro board reset so each mark keeps a consistent owner.")

    state: CaroState = st.session_state.caro_state
    if state.size != BOARD_SIZE:
        _reset_state()
        state = st.session_state.caro_state

    ai_player = opponent(human)
    result = _maybe_run_ai(state, ai_player, algorithm, int(depth))
    if result:
        st.session_state.caro_last_result = result
        state = st.session_state.caro_state

    _render_status(state, human, ai_player)
    _render_board(state, human, ai_player, algorithm, int(depth))
    _render_ai_metrics(st.session_state.get("caro_last_result"))


def _ensure_state() -> None:
    if "caro_state" not in st.session_state:
        _reset_state()
    if "caro_last_result" not in st.session_state:
        st.session_state.caro_last_result = None


def _reset_state() -> None:
    st.session_state.caro_state = create_initial_caro_state(BOARD_SIZE)
    st.session_state.caro_last_result = None


def _maybe_run_ai(
    state: CaroState, ai_player: str, algorithm: str, depth: int,
) -> CaroSearchResult | None:
    if winner(state) or state.current_player != ai_player:
        return None
    if not legal_caro_moves(state):
        return None
    result = _search(state, ai_player, algorithm, depth)
    if result.move:
        st.session_state.caro_state = apply_caro_move(state, *result.move)
    return result


def _render_status(state: CaroState, human: str, ai_player: str) -> None:
    win = winner(state)
    if win:
        st.success(f"{win} wins. {'You win' if win == human else 'AI wins'}.")
        return
    if not legal_caro_moves(state):
        st.warning("Draw: no legal moves remain.")
        return
    turn_owner = "Human" if state.current_player == human else "AI"
    score = evaluate_caro_state(state, ai_player)
    st.caption(f"Turn: {state.current_player} ({turn_owner}) | AI static evaluation: {score}")


def _render_board(
    state: CaroState, human: str, ai_player: str, algorithm: str, depth: int,
) -> None:
    game_over = bool(winner(state)) or not legal_caro_moves(state)
    for row in range(state.size):
        columns = st.columns(state.size, gap="small")
        for col, column in enumerate(columns):
            mark = state.board[row * state.size + col]
            label = mark if mark != "." else " "
            disabled = game_over or state.current_player != human or mark != "."
            if column.button(label, key=f"caro_{row}_{col}", disabled=disabled, use_container_width=True):
                try:
                    after_human = apply_caro_move(state, row, col)
                    st.session_state.caro_state = after_human
                    result = _maybe_run_ai(after_human, ai_player, algorithm, depth)
                    if result:
                        st.session_state.caro_last_result = result
                    st.rerun()
                except ValueError as exc:
                    st.error(str(exc))


def _render_ai_metrics(result: CaroSearchResult | None) -> None:
    if result is None:
        st.caption("AI has not moved yet.")
        return
    move_text = "-" if result.move is None else f"({result.move[0]}, {result.move[1]})"
    metric_a, metric_b, metric_c, metric_d = st.columns(4)
    metric_a.metric("AI move", move_text)
    metric_b.metric("Value", result.value)
    metric_c.metric("Expanded", result.nodes_expanded)
    metric_d.metric("Pruned", result.pruned)
    if result.principal_variation:
        line = " -> ".join(f"({r},{c})" for r, c in result.principal_variation[:8])
        st.code(f"{result.algorithm} PV: {line}", language="text")
    st.caption(
        f"Generated {result.nodes_generated} moves in {result.runtime:.4f}s. "
        "Depth is bounded for classroom responsiveness."
    )


def _search(state: CaroState, ai_player: str, algorithm: str, depth: int) -> CaroSearchResult:
    if algorithm == "Minimax":
        return caro_minimax(state, depth=depth, player=ai_player)
    return caro_alpha_beta(state, depth=depth, player=ai_player)
