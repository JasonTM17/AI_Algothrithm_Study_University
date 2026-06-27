"""Demo specifications for README and gallery GIF generation."""

from __future__ import annotations

from dataclasses import dataclass, field

from core.puzzle import GOAL_STATE, TEACHING_PRESETS, scramble
from ui.styles import ALGORITHM_FN_MAP, ALGORITHM_GROUPS


FEATURED_SPECS = {
    "a-star-image-replay": "A*",
    "uninformed-search": "BFS",
    "informed-search": "IDA*",
    "local-search": "Steepest-Ascent Hill Climbing",
    "complex-environments": "Searching for partially observable problems",
    "csp": "Constraint Propagation",
    "ai-vs-ai-tournament": "AI-vs-AI Tournament",
}

HERO_START = (1, 6, 2, 7, 5, 0, 4, 3, 9, 10, 11, 8, 13, 14, 15, 12)
SEARCH_START = scramble(GOAL_STATE, depth=5, seed=17)
LOCAL_START = TEACHING_PRESETS["Hill Climbing stuck: local optimum h=4"]["state"]
ONE_MOVE_START = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 0, 15)


@dataclass(frozen=True)
class DemoSpec:
    algorithm: str
    group: str
    slug: str
    mode: str
    start: tuple[int, ...] = SEARCH_START
    goal: tuple[int, ...] = GOAL_STATE
    seed: int = 42
    params: dict[str, object] = field(default_factory=dict)
    expects_goal_path: bool = False
    featured_slug: str | None = None

    @property
    def function_name(self) -> str:
        return ALGORITHM_FN_MAP[self.algorithm]


def slugify(name: str) -> str:
    text = name.lower().replace("*", "star")
    keep = [ch if ch.isalnum() else "-" for ch in text]
    return "-".join(part for part in "".join(keep).split("-") if part)


def _group_for_algorithm(algorithm: str) -> str:
    for group, algorithms in ALGORITHM_GROUPS.items():
        if algorithm in algorithms:
            return group
    raise KeyError(f"Unknown algorithm: {algorithm}")


def _mode_for_group(group: str, algorithm: str) -> str:
    if group in {"Uninformed Search", "Informed Search"}:
        return "graph"
    if group == "Local Search":
        return "local"
    if group == "Complex Environments":
        return "complex"
    if group == "CSP":
        return "csp"
    if algorithm == "AI-vs-AI Tournament":
        return "tournament"
    return "adversarial"


def build_specs() -> list[DemoSpec]:
    specs: list[DemoSpec] = []
    for group, algorithms in ALGORITHM_GROUPS.items():
        for algorithm in algorithms:
            specs.append(_build_spec(algorithm, group))
    return specs


def _build_spec(algorithm: str, group: str) -> DemoSpec:
    mode = _mode_for_group(group, algorithm)
    slug = slugify(algorithm)
    params: dict[str, object] = {}
    start = SEARCH_START
    expects_goal = group in {"Uninformed Search", "Informed Search"}

    if algorithm == "A*":
        start = HERO_START
        expects_goal = True
    elif algorithm in {"DFS", "IDS"}:
        params["max_depth"] = 12
    elif algorithm == "IDA*":
        start = scramble(GOAL_STATE, depth=4, seed=9)
    elif mode == "local":
        start = LOCAL_START
        params["max_iterations"] = 40
        if "Stochastic" in algorithm or algorithm in {"Random-Restart Hill Climbing", "Simulated Annealing"}:
            params["seed"] = 7
        if algorithm == "Random-Restart Hill Climbing":
            params["max_restarts"] = 3
        if algorithm == "Local Beam Search":
            params["beam_width"] = 3
    elif algorithm == "AND-OR Search":
        start = ONE_MOVE_START
        params.update({"max_depth": 2, "nondet_prob": 0.0})
    elif algorithm in {"Searching with no observation", "Searching for partially observable problems"}:
        start = ONE_MOVE_START
        params.update({
            "max_steps": 3,
            "num_belief_states": 4,
            "known_positions": {14: 15},
            "seed": 42,
        })
    elif algorithm == "LRTA*":
        params["max_steps"] = 8
    elif mode == "csp":
        start = ONE_MOVE_START
        if algorithm in {"CSP Definition", "Constraint Propagation", "Constraint Graphs"}:
            params["time_horizon"] = 2
        elif algorithm == "Backtracking Search":
            params["max_steps"] = 600
        elif algorithm == "Min-Conflicts":
            params["max_iterations"] = 80
    elif mode == "adversarial":
        start = ONE_MOVE_START
        params["depth"] = 2
        if algorithm == "Expectimax":
            params.update({"success_prob": 0.75, "seed": 11})

    featured = next((key for key, value in FEATURED_SPECS.items() if value == algorithm), None)
    return DemoSpec(
        algorithm=algorithm,
        group=group,
        slug=slug,
        mode=mode,
        start=start,
        params=params,
        expects_goal_path=expects_goal,
        featured_slug=featured,
    )


def get_spec(algorithm_or_slug: str) -> DemoSpec:
    query = algorithm_or_slug.strip().lower()
    for spec in build_specs():
        if spec.algorithm.lower() == query or spec.slug == query:
            return spec
    raise KeyError(f"No GIF demo registered for {algorithm_or_slug!r}")


def featured_specs() -> list[DemoSpec]:
    specs = build_specs()
    by_algorithm = {spec.algorithm: spec for spec in specs}
    return [
        by_algorithm[algorithm]
        for _, algorithm in FEATURED_SPECS.items()
    ]


def registry_summary() -> dict[str, int]:
    return {
        "groups": len(ALGORITHM_GROUPS),
        "algorithms": sum(len(items) for items in ALGORITHM_GROUPS.values()),
        "specs": len(build_specs()),
    }
