"""Group 6 Play lab variants beyond standard solver replay.

These helpers keep Minimax, Alpha-Beta and Expectimax out of the standard
15-puzzle solver contract. They expose two educational variants:

* Robustness Game Variant: MAX alternates with a worst-case environment.
* Chance Outcome Lab: Expectimax decisions are sampled through a chance model.
"""

# BẢN ĐỒ ĐỌC FILE — MODE 2 VÀ MODE 3
# -----------------------------------
# File này chứa state machine cho hai mô hình giáo dục chạy trên MỘT bàn cờ:
#
# * Robustness Game Variant (Mode 2): MAX và MIN luân phiên. MAX dùng
#   Minimax/Alpha-Beta để tiến về Goal; MIN là môi trường worst-case giả lập,
#   không phải đối thủ tự nhiên của 15-puzzle.
# * Chance Outcome Lab (Mode 3): Expectimax chọn intended action, sau đó CHANCE
#   lấy mẫu realized action theo success_probability và seed.
#
# Cả hai mode chỉ đánh giá decision/policy trong giới hạn depth, turn và runtime.
# Chúng không thuộc contract solver đường đi ngắn nhất của 15-puzzle chuẩn.

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import hashlib
import json
import random
import statistics

from core.group6_decision_lab import Group6LabSettings, run_group6_algorithm
from core.heuristics import get_heuristic
from core.puzzle import _move_blank


State = tuple[int, ...]
# Robustness chỉ có MAX/MIN nên không nhận Expectimax; Chance Lab cố định dùng
# Expectimax vì đây là mô hình duy nhất trong nhóm có CHANCE node.
ROBUSTNESS_ALGORITHMS = ("Minimax", "Alpha-Beta Pruning")
CHANCE_ALGORITHM = "Expectimax"
GROUP6_VARIANT_TERMINAL_STATUSES = {
    "goal",
    "cycle",
    "timeout",
    "no_action",
    "invalid_transition",
    "turn_limit",
    "total_budget",
}


@dataclass(frozen=True)
class Group6RobustnessSettings:
    """Settings for the artificial MAX/MIN robustness game variant."""

    algorithm: str = "Minimax"
    depth: int = 3
    per_turn_timeout: float = 1.0
    total_budget: float = 20.0
    max_turns: int = 30
    heuristic: str = "Manhattan Distance"
    action_order: str = "LRUD"
    utility_penalty: float = -1000.0

    def validate(self) -> None:
        if self.algorithm not in ROBUSTNESS_ALGORITHMS:
            raise ValueError("Robustness mode supports only Minimax and Alpha-Beta Pruning")
        Group6LabSettings(
            depth=self.depth,
            timeout=self.per_turn_timeout,
            heuristic=self.heuristic,
            action_order=self.action_order,
        ).validate()
        if self.total_budget <= 0:
            raise ValueError("total_budget must be positive")
        if self.max_turns < 1:
            raise ValueError("max_turns must be positive")


@dataclass(frozen=True)
class Group6ChanceSettings:
    """Settings for the Expectimax chance-outcome lab."""

    depth: int = 3
    per_turn_timeout: float = 1.0
    total_budget: float = 20.0
    max_turns: int = 30
    heuristic: str = "Manhattan Distance"
    action_order: str = "LRUD"
    success_probability: float = 0.8
    seed: int = 42
    sample_count: int = 10
    utility_penalty: float = -1000.0

    def validate(self) -> None:
        Group6LabSettings(
            depth=self.depth,
            timeout=self.per_turn_timeout,
            heuristic=self.heuristic,
            action_order=self.action_order,
            success_probability=self.success_probability,
            seed=self.seed,
        ).validate()
        if self.total_budget <= 0:
            raise ValueError("total_budget must be positive")
        if self.max_turns < 1:
            raise ValueError("max_turns must be positive")
        if self.sample_count < 1:
            raise ValueError("sample_count must be positive")


@dataclass(frozen=True)
class Group6TurnFrame:
    """One applied edge in a Group 6 educational variant."""

    mode: str
    turn: int
    role: str
    algorithm: str
    before_state: State
    after_state: State
    intended_action: str
    realized_action: str
    root_value: float | None
    utility: float
    probability: float | None
    alpha: float | None
    beta: float | None
    pruned: int
    expanded: int
    generated: int
    runtime: float
    termination: str
    expected_utility: float | None = None
    repeated_state: bool = False


@dataclass
class Group6RobustnessGame:
    """Mutable state for the single-board MAX/MIN robustness game."""

    start: State
    goal: State
    settings: Group6RobustnessSettings
    fingerprint: str
    current_state: State
    history: list[State] = field(default_factory=list)
    frames: list[Group6TurnFrame] = field(default_factory=list)
    status: str = "ready"
    running: bool = False
    cumulative_runtime: float = 0.0
    cumulative_expanded: int = 0
    cumulative_generated: int = 0
    cumulative_pruned: int = 0

    @property
    def active(self) -> bool:
        return self.status not in GROUP6_VARIANT_TERMINAL_STATUSES

    def export_summary(self) -> dict[str, object]:
        return {
            "mode": "robustness_game_variant",
            "fingerprint": self.fingerprint,
            "start": list(self.start),
            "goal": list(self.goal),
            "settings": asdict(self.settings),
            "status": self.status,
            "cumulative_runtime": self.cumulative_runtime,
            "cumulative_expanded": self.cumulative_expanded,
            "cumulative_generated": self.cumulative_generated,
            "cumulative_pruned": self.cumulative_pruned,
            "history": [list(state) for state in self.history],
            "frames": [_frame_payload(frame) for frame in self.frames],
        }


@dataclass
class Group6ChanceLab:
    """Mutable state for Expectimax plus sampled chance outcomes."""

    start: State
    goal: State
    settings: Group6ChanceSettings
    fingerprint: str
    current_state: State
    history: list[State] = field(default_factory=list)
    frames: list[Group6TurnFrame] = field(default_factory=list)
    status: str = "ready"
    running: bool = False
    cumulative_runtime: float = 0.0
    cumulative_expanded: int = 0
    cumulative_generated: int = 0

    @property
    def active(self) -> bool:
        return self.status not in GROUP6_VARIANT_TERMINAL_STATUSES

    def export_summary(self) -> dict[str, object]:
        return {
            "mode": "chance_outcome_lab",
            "fingerprint": self.fingerprint,
            "start": list(self.start),
            "goal": list(self.goal),
            "settings": asdict(self.settings),
            "status": self.status,
            "cumulative_runtime": self.cumulative_runtime,
            "cumulative_expanded": self.cumulative_expanded,
            "cumulative_generated": self.cumulative_generated,
            "history": [list(state) for state in self.history],
            "frames": [_frame_payload(frame) for frame in self.frames],
        }


def _frame_payload(frame: Group6TurnFrame) -> dict[str, object]:
    payload = asdict(frame)
    payload["before_state"] = list(frame.before_state)
    payload["after_state"] = list(frame.after_state)
    return payload


def _fingerprint(payload: dict[str, object]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()[:16]


def _legal_actions(state: State, action_order: str) -> list[str]:
    return [action for action in action_order if _move_blank(state, action) is not None]


def _utility(
    state: State,
    goal: State,
    heuristic: str,
    *,
    penalty: float,
    terminal_reason: str | None = None,
) -> float:
    # Utility dùng chung cho frame đã áp dụng: Goal nhận bonus lớn; cycle/timeout
    # nhận penalty; state thường nhận giá trị âm của heuristic (gần Goal tốt hơn).
    if state == goal:
        return 1000.0
    if terminal_reason in {"cycle", "timeout", "total_budget"}:
        return float(penalty)
    return -float(get_heuristic(heuristic, goal)(state))


def create_robustness_game(
    *,
    start: State,
    goal: State,
    settings: Group6RobustnessSettings | None = None,
) -> Group6RobustnessGame:
    # Khởi tạo một bàn chung. Khác Policy Comparison, không có lane A/B độc lập.
    settings = settings or Group6RobustnessSettings()
    settings.validate()
    payload = {
        "mode": "robustness_game_variant",
        "start": list(start),
        "goal": list(goal),
        "settings": asdict(settings),
    }
    status = "goal" if tuple(start) == tuple(goal) else "ready"
    return Group6RobustnessGame(
        start=tuple(start),
        goal=tuple(goal),
        settings=settings,
        fingerprint=_fingerprint(payload),
        current_state=tuple(start),
        history=[tuple(start)],
        status=status,
    )


def _lab_settings_from_robustness(settings: Group6RobustnessSettings) -> Group6LabSettings:
    return Group6LabSettings(
        depth=settings.depth,
        timeout=settings.per_turn_timeout,
        heuristic=settings.heuristic,
        action_order=settings.action_order,
    )


def _max_action(
    state: State,
    goal: State,
    settings: Group6RobustnessSettings,
):
    # MAX ủy quyền quyết định cho Minimax hoặc Alpha-Beta và lấy root action đầu.
    decision = run_group6_algorithm(
        settings.algorithm,
        start=state,
        goal=goal,
        settings=_lab_settings_from_robustness(settings),
    )
    if decision.timed_out:
        return decision, "", "timeout"
    if not decision.result.actions:
        return decision, "", "no_action"
    return decision, decision.result.actions[0], "applied"


def _min_worst_case_action(
    state: State,
    goal: State,
    settings: Group6RobustnessSettings,
) -> str:
    # MIN là môi trường xấu nhất: chọn legal move làm heuristic lớn nhất, tức là
    # đẩy bàn xa Goal nhất; action_order được dùng để phá hòa ổn định.
    h_fn = get_heuristic(settings.heuristic, goal)
    candidates: list[tuple[float, str]] = []
    for action in _legal_actions(state, settings.action_order):
        next_state = _move_blank(state, action)
        if next_state is not None:
            candidates.append((float(h_fn(next_state)), action))
    if not candidates:
        return ""
    candidates.sort(key=lambda item: (-item[0], settings.action_order.index(item[1])))
    return candidates[0][1]


def _cycle_safe_action(
    state: State,
    intended_action: str,
    history: list[State],
    goal: State,
    settings: Group6RobustnessSettings,
    *,
    role: str,
) -> str:
    """Prefer an unvisited legal move when the intended move repeats history."""
    # Nếu action dự kiến quay lại state cũ, ưu tiên một legal state chưa thăm.
    # MAX vẫn ưu tiên gần Goal, MIN vẫn ưu tiên xa Goal trong tập thay thế này.
    intended_state = _move_blank(state, intended_action)
    visited = set(history)
    if intended_state is None or intended_state not in visited:
        return intended_action

    h_fn = get_heuristic(settings.heuristic, goal)
    candidates: list[tuple[float, str]] = []
    for action in _legal_actions(state, settings.action_order):
        next_state = _move_blank(state, action)
        if next_state is not None and next_state not in visited:
            candidates.append((float(h_fn(next_state)), action))
    if not candidates:
        return intended_action

    heuristic_direction = -1.0 if role == "MIN" else 1.0
    candidates.sort(
        key=lambda item: (
            heuristic_direction * item[0],
            settings.action_order.index(item[1]),
        )
    )
    return candidates[0][1]


def advance_robustness_game(game: Group6RobustnessGame) -> Group6RobustnessGame:
    """Advance MAX or MIN by one legal move on the shared board."""
    game.settings.validate()
    if not game.active:
        game.running = False
        return game
    if len(game.frames) >= game.settings.max_turns:
        game.status = "turn_limit"
        game.running = False
        return game

    # Frame chẵn bắt đầu bằng MAX, frame lẻ là MIN: cả hai tác động lên cùng bàn.
    role = "MAX" if len(game.frames) % 2 == 0 else "MIN"
    before = game.current_state
    root_value: float | None = None
    runtime = 0.0
    expanded = generated = pruned = 0
    alpha = beta = None

    # MAX dùng principal decision của thuật toán; MIN dùng legal worst-case move.
    if role == "MAX":
        decision, action, termination = _max_action(before, game.goal, game.settings)
        root_value = decision.root_value
        runtime = float(decision.result.runtime)
        expanded = int(decision.result.nodes_expanded)
        generated = int(decision.result.nodes_generated)
        pruned = int(decision.prune_count)
        if decision.frames:
            alpha = decision.frames[0].alpha
            beta = decision.frames[0].beta
    else:
        decision = run_group6_algorithm(
            game.settings.algorithm,
            start=before,
            goal=game.goal,
            settings=_lab_settings_from_robustness(game.settings),
        )
        root_value = decision.root_value
        runtime = float(decision.result.runtime)
        expanded = int(decision.result.nodes_expanded)
        generated = int(decision.result.nodes_generated)
        pruned = int(decision.prune_count)
        action = _min_worst_case_action(before, game.goal, game.settings)
        termination = "applied" if action else "no_action"

    # Metrics được cộng dồn theo từng lượt để UI so effort qua toàn phiên chạy.
    game.cumulative_runtime += runtime
    game.cumulative_expanded += expanded
    game.cumulative_generated += generated
    game.cumulative_pruned += pruned
    if game.cumulative_runtime >= game.settings.total_budget:
        game.status = "total_budget"
        game.running = False
        return game
    if termination != "applied":
        game.status = termination
        game.running = False
        return game

    # ``intended_action`` giữ quyết định ban đầu; ``action`` có thể được thay bằng
    # bước cycle-safe và sẽ trở thành realized action trong frame evidence.
    intended_action = action
    action = _cycle_safe_action(
        before,
        intended_action,
        game.history,
        game.goal,
        game.settings,
        role=role,
    )
    after = _move_blank(before, action)
    if after is None:
        game.status = "invalid_transition"
        game.running = False
        return game

    # Goal/cycle là trạng thái kết thúc của variant, không phải optimal certificate.
    repeated = after in game.history
    status = "cycle" if repeated else ("goal" if after == game.goal else "running")
    frame = Group6TurnFrame(
        mode="robustness_game_variant",
        turn=len(game.frames) + 1,
        role=role,
        algorithm=game.settings.algorithm,
        before_state=before,
        after_state=after,
        intended_action=intended_action,
        realized_action=action,
        root_value=root_value,
        utility=_utility(
            after,
            game.goal,
            game.settings.heuristic,
            penalty=game.settings.utility_penalty,
            terminal_reason=status,
        ),
        probability=None,
        alpha=alpha,
        beta=beta,
        pruned=pruned,
        expanded=expanded,
        generated=generated,
        runtime=runtime,
        termination=status,
        repeated_state=repeated,
    )
    game.frames.append(frame)
    game.current_state = after
    game.history.append(after)
    game.status = status
    game.running = game.running and game.active
    return game


def create_chance_lab(
    *,
    start: State,
    goal: State,
    settings: Group6ChanceSettings | None = None,
) -> Group6ChanceLab:
    # Chance Lab dùng một bàn; seed schedule được ghi vào fingerprint để replay.
    settings = settings or Group6ChanceSettings()
    settings.validate()
    payload = {
        "mode": "chance_outcome_lab",
        "start": list(start),
        "goal": list(goal),
        "settings": asdict(settings),
        "seed_schedule": "seed + turn_index",
    }
    status = "goal" if tuple(start) == tuple(goal) else "ready"
    return Group6ChanceLab(
        start=tuple(start),
        goal=tuple(goal),
        settings=settings,
        fingerprint=_fingerprint(payload),
        current_state=tuple(start),
        history=[tuple(start)],
        status=status,
    )


def _lab_settings_from_chance(settings: Group6ChanceSettings, turn: int) -> Group6LabSettings:
    # Mỗi lượt dùng seed kế tiếp nhằm vừa tái lập được, vừa không lặp cùng sample.
    return Group6LabSettings(
        depth=settings.depth,
        timeout=settings.per_turn_timeout,
        heuristic=settings.heuristic,
        action_order=settings.action_order,
        success_probability=settings.success_probability,
        seed=settings.seed + turn,
    )


def chance_outcome_distribution(
    state: State,
    intended_action: str,
    *,
    success_probability: float,
    action_order: str,
) -> list[tuple[str, State, float]]:
    """Return legal outcomes for one intended action.

    Illegal deflections are omitted. If the intended action is the only legal
    move, its probability is normalized to 1.0.
    """
    # Intended action nhận success_probability; phần xác suất còn lại được chia
    # đều cho các legal deflection. Illegal deflection không có trong support.
    legal = _legal_actions(state, action_order)
    if intended_action not in legal:
        return []
    deflections = [action for action in legal if action != intended_action]
    if not deflections:
        next_state = _move_blank(state, intended_action)
        return [] if next_state is None else [(intended_action, next_state, 1.0)]

    remaining = 1.0 - success_probability
    deflection_probability = remaining / len(deflections)
    rows: list[tuple[str, State, float]] = []
    intended_state = _move_blank(state, intended_action)
    if intended_state is not None:
        rows.append((intended_action, intended_state, success_probability))
    for action in deflections:
        next_state = _move_blank(state, action)
        if next_state is not None:
            rows.append((action, next_state, deflection_probability))
    total = sum(probability for _, _, probability in rows)
    if total and abs(total - 1.0) > 1e-12:
        rows = [(action, next_state, probability / total) for action, next_state, probability in rows]
    return rows


def _sample_outcome(
    outcomes: list[tuple[str, State, float]],
    *,
    seed: int,
) -> tuple[str, State, float]:
    # Lấy một mẫu bằng cumulative probability; Random(seed) giúp test/replay ổn định.
    threshold = random.Random(seed).random()
    cumulative = 0.0
    for action, state, probability in outcomes:
        cumulative += probability
        if threshold <= cumulative:
            return action, state, probability
    return outcomes[-1]


def advance_chance_lab(lab: Group6ChanceLab) -> Group6ChanceLab:
    """Advance Expectimax by one MAX decision and one sampled CHANCE outcome."""
    lab.settings.validate()
    if not lab.active:
        lab.running = False
        return lab
    if len(lab.frames) >= lab.settings.max_turns:
        lab.status = "turn_limit"
        lab.running = False
        return lab

    turn = len(lab.frames) + 1
    before = lab.current_state
    # Bước 1: Expectimax chọn intended root action theo expected utility.
    decision = run_group6_algorithm(
        CHANCE_ALGORITHM,
        start=before,
        goal=lab.goal,
        settings=_lab_settings_from_chance(lab.settings, turn),
    )
    lab.cumulative_runtime += float(decision.result.runtime)
    lab.cumulative_expanded += int(decision.result.nodes_expanded)
    lab.cumulative_generated += int(decision.result.nodes_generated)
    if lab.cumulative_runtime >= lab.settings.total_budget:
        lab.status = "total_budget"
        lab.running = False
        return lab
    if decision.timed_out:
        lab.status = "timeout"
        lab.running = False
        return lab
    if not decision.result.actions:
        lab.status = "no_action"
        lab.running = False
        return lab

    # Bước 2: dựng toàn bộ outcome hợp lệ của action dự kiến.
    intended = decision.result.actions[0]
    outcomes = chance_outcome_distribution(
        before,
        intended,
        success_probability=lab.settings.success_probability,
        action_order=lab.settings.action_order,
    )
    if not outcomes:
        lab.status = "no_action"
        lab.running = False
        return lab

    h_fn = get_heuristic(lab.settings.heuristic, lab.goal)
    # Bước 3: tính kỳ vọng để hiển thị evidence, rồi lấy một outcome thực tế.
    expected_utility = sum(
        probability
        * _utility(
            state,
            lab.goal,
            lab.settings.heuristic,
            penalty=lab.settings.utility_penalty,
        )
        for _, state, probability in outcomes
    )
    realized, after, probability = _sample_outcome(
        outcomes,
        seed=lab.settings.seed + turn,
    )
    # Bước 4: chỉ realized outcome được áp dụng lên bàn và ghi thành một frame.
    repeated = after in lab.history
    status = "cycle" if repeated else ("goal" if after == lab.goal else "running")
    lab.current_state = after
    lab.history.append(after)
    lab.frames.append(
        Group6TurnFrame(
            mode="chance_outcome_lab",
            turn=turn,
            role="CHANCE",
            algorithm=CHANCE_ALGORITHM,
            before_state=before,
            after_state=after,
            intended_action=intended,
            realized_action=realized,
            root_value=decision.root_value,
            utility=_utility(
                after,
                lab.goal,
                lab.settings.heuristic,
                penalty=lab.settings.utility_penalty,
                terminal_reason=status,
            ),
            probability=probability,
            alpha=None,
            beta=None,
            pruned=0,
            expanded=int(decision.result.nodes_expanded),
            generated=int(decision.result.nodes_generated),
            runtime=float(decision.result.runtime),
            termination=status,
            expected_utility=expected_utility,
            repeated_state=repeated,
        )
    )
    # Keep the direct heuristic visible even when utility is a goal bonus.
    _ = h_fn(after)
    lab.status = status
    lab.running = lab.running and lab.active
    return lab


def run_chance_stability_sample(
    *,
    start: State,
    goal: State,
    settings: Group6ChanceSettings,
) -> dict[str, object]:
    """Run multiple deterministic seeds and summarize final heuristic/runtime."""
    # Chạy nhiều seed để tránh kết luận từ một trajectory may/rủi duy nhất.
    settings.validate()
    rows: list[dict[str, object]] = []
    h_fn = get_heuristic(settings.heuristic, goal)
    for offset in range(settings.sample_count):
        seeded_settings = Group6ChanceSettings(
            **{**asdict(settings), "seed": settings.seed + offset}
        )
        lab = create_chance_lab(start=start, goal=goal, settings=seeded_settings)
        while lab.active:
            advance_chance_lab(lab)
        rows.append(
            {
                "seed": seeded_settings.seed,
                "status": lab.status,
                "turns": len(lab.frames),
                "runtime": lab.cumulative_runtime,
                "final_manhattan": float(h_fn(lab.current_state)),
                "goal_reached": lab.current_state == goal,
            }
        )

    runtimes = [float(row["runtime"]) for row in rows]
    final_h = [float(row["final_manhattan"]) for row in rows]
    return {
        "rows": rows,
        "stats": {
            "mean_runtime": statistics.fmean(runtimes),
            "min_runtime": min(runtimes),
            "max_runtime": max(runtimes),
            "std_runtime": statistics.pstdev(runtimes) if len(runtimes) > 1 else 0.0,
            "mean_final_manhattan": statistics.fmean(final_h),
            "min_final_manhattan": min(final_h),
            "max_final_manhattan": max(final_h),
            "std_final_manhattan": statistics.pstdev(final_h) if len(final_h) > 1 else 0.0,
            "goal_reached_count": sum(1 for row in rows if row["goal_reached"]),
        },
    }
