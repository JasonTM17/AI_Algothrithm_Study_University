"""Academic notes used by README GIF assets and documentation."""

from __future__ import annotations

from dataclasses import dataclass


MEDIA_VERIFIED_AT = "2026-06-29"


@dataclass(frozen=True)
class DemoNote:
    role: str
    learning_goal: str
    mechanism: str
    evidence: str
    guarantee: str
    academic_caveat: str


GROUP_GUIDES = {
    "Uninformed Search": {
        "purpose": "Duyet state-space without heuristic; evidence focuses on frontier/reached and legal path.",
        "question": "If every move costs 1 and no domain estimate is used, how does queue discipline change behavior?",
    },
    "Informed Search": {
        "purpose": "Add h(n), then combine with g(n) for optimal informed search.",
        "question": "When is a heuristic only fast, and when does it justify an optimality certificate?",
    },
    "Local Search": {
        "purpose": "Show candidate-level choices without treating the run as guaranteed path search.",
        "question": "Which neighbor was considered, chosen, rejected or accepted probabilistically?",
    },
    "Complex Environments": {
        "purpose": "Model conditional, conformant and contingent planning over explicit belief states.",
        "question": "What does the agent know, and is the output a conditional plan, conformant sequence or observation policy?",
    },
    "CSP": {
        "purpose": "Reframe puzzle planning as variables, domains and constraints.",
        "question": "Which variable/domain/constraint evidence is being shown instead of a shortest path claim?",
    },
    "AI-vs-AI Tournament": {
        "purpose": "Compare agents, robustness and chance models without pretending the puzzle has a natural opponent.",
        "question": "Is this a scored benchmark, a worst-case branch or an expected-value model?",
    },
}


ALGORITHM_NOTES: dict[str, DemoNote] = {
    "BFS": DemoNote(
        "Standard solver",
        "Understand level-order expansion and why unit-cost BFS can certify shortest paths.",
        "FIFO frontier over puzzle states.",
        "frontier size, reached set, legal path and path cost.",
        "Complete and optimal for unit step cost if resources suffice.",
        "Memory grows quickly; good for shallow teaching cases, not deep 15-puzzle production search.",
    ),
    "DFS": DemoNote(
        "Contrast demo",
        "See how depth-first commitment differs from optimal state-space search.",
        "LIFO stack with depth-aware duplicate handling.",
        "expanded nodes, depth limit and legal trajectory when present.",
        "No shortest-path guarantee in this app setting.",
        "Can chase a deep branch and miss a shorter path.",
    ),
    "UCS": DemoNote(
        "Standard solver",
        "Connect path cost g(n) to optimal search.",
        "Priority queue ordered by cumulative path cost.",
        "g(n), frontier, reached and cost certificate.",
        "Complete and optimal for non-negative costs.",
        "On unit-cost 15-puzzle it behaves like BFS but keeps the general cost model explicit.",
    ),
    "IDS": DemoNote(
        "Standard solver",
        "Trade BFS optimality for DFS-like memory by increasing the depth limit.",
        "Repeated depth-limited DFS with cutoff tracking.",
        "depth limit, cutoff/exhausted reason and legal path.",
        "Complete and optimal for unit step cost if the limit reaches the solution depth.",
        "Repeats work across iterations; the trace should be read by limit, not as one queue.",
    ),
    "Greedy Best-First": DemoNote(
        "Contrast demo",
        "Show why h(n) alone is fast but not a certificate.",
        "Priority queue ordered only by heuristic h(n).",
        "selected h(n), frontier and whether the final path reaches goal.",
        "No optimality guarantee.",
        "May find a longer path or get misled by a locally attractive state.",
    ),
    "A*": DemoNote(
        "Standard solver",
        "Read f(n)=g(n)+h(n) and the Manhattan optimality condition.",
        "Priority queue ordered by g(n)+h(n).",
        "g/h/f, expanded/generated/frontier, legal path and optimality flag.",
        "Optimal with admissible and consistent heuristic when resources do not stop the run.",
        "The certificate is valid only for the selected goal and heuristic contract.",
    ),
    "IDA*": DemoNote(
        "Standard solver",
        "Combine A* evaluation with memory-bounded iterative thresholds.",
        "Depth-first search bounded by increasing f-threshold.",
        "threshold, reached metric, legal path and optimality flag.",
        "Optimal with admissible heuristic and sufficient threshold iterations.",
        "May revisit many states; trace is threshold-based, not a single frontier queue.",
    ),
    "Simple Hill Climbing": DemoNote(
        "Contrast demo",
        "Watch the first improving candidate win or the search stop.",
        "Scan neighbors and move to the first lower h(n).",
        "candidate h, selected action and stop reason.",
        "No completeness or optimality guarantee.",
        "Local optimum can stop the run far from the goal.",
    ),
    "Steepest-Ascent Hill Climbing": DemoNote(
        "Contrast demo",
        "Compare all local neighbors before moving.",
        "Choose the neighbor with best h(n) decrease.",
        "evaluated candidates, best candidate and reject/accept reason.",
        "No completeness or optimality guarantee.",
        "Still local; evaluating every neighbor does not solve plateaus.",
    ),
    "Stochastic Hill Climbing": DemoNote(
        "Contrast demo",
        "See randomness among improving candidates.",
        "Sample one improving move using a fixed seed.",
        "candidate pool, chosen action, seed and legal trajectory.",
        "No deterministic optimality guarantee.",
        "Different seeds can produce different partial trajectories.",
    ),
    "Random-Restart Hill Climbing": DemoNote(
        "Contrast demo",
        "Use restarts to escape one bad local basin.",
        "Run multiple hill climbs from deterministic restart states.",
        "restart index, best h(n) and selected trajectory.",
        "Still not a complete 15-puzzle solver here.",
        "More restarts improve chances but do not prove optimality.",
    ),
    "Local Beam Search": DemoNote(
        "Contrast demo",
        "Track several local candidates at once.",
        "Keep k best states per iteration.",
        "beam width, candidate scores and selected beam states.",
        "No optimality guarantee.",
        "The beam can collapse to similar states and miss the global route.",
    ),
    "Simulated Annealing": DemoNote(
        "Contrast demo",
        "Understand probabilistic acceptance of worse moves.",
        "Temperature-controlled accept/reject over neighbors.",
        "temperature, probability, accepted flag and legal trajectory.",
        "No certificate of reaching or optimizing the goal.",
        "A legal trajectory is not automatically a solution.",
    ),
    "AND-OR Search": DemoNote(
        "Extension",
        "Read a conditional plan under possible outcome deflections.",
        "OR chooses action; AND requires subplans for supported outcomes.",
        "conditional branches, depth limit and deflection support mode.",
        "Returns a policy-like conditional plan, not a linear shortest path.",
        "The support switch is not probability weighting.",
    ),
    "Searching with no observation": DemoNote(
        "Extension",
        "Find one conformant action sequence without reading the hidden state.",
        "Graph-search finite belief states using Predict(B,a), with illegal actions defined as no-op.",
        "belief frontier/reached, duplicate rejection, action sequence and goal coverage.",
        "Success means every represented initial state reaches the goal under one sequence.",
        "The finite reconstructed belief is an approximation, and bounded failure is not a global impossibility proof.",
    ),
    "Searching for partially observable problems": DemoNote(
        "Extension",
        "Build a contingent policy that covers every possible local observation.",
        "Predict a belief, partition by blank-and-neighbor percept, then recurse on each updated belief.",
        "predicted belief, observation partitions, branch coverage and policy depth.",
        "Success requires a subpolicy for every represented observation branch.",
        "The sensor and finite belief approximation are explicit; hidden state never builds the policy.",
    ),
    "Backtracking": DemoNote("Extension", "Assign an exact-horizon state chain chronologically.", "Backtrack when a neighboring state violates the legal blank-move constraint.", "assignments, checks, backtracks and verified path when found.", "Sound within the represented horizon and resource bounds.", "Horizon failure is not global unsolvability or a shortest-path certificate."),
    "Backtracking + Forward Checking": DemoNote("Extension", "Compare early domain pruning with plain backtracking.", "After assignment, remove unsupported values from the next state domain.", "assignments, values pruned, domain wipe-out and backtracks.", "Uses the same ordering as Backtracking for a fair empirical comparison.", "Worst-case complexity remains exponential and failure is horizon-bounded."),
    "AC-3": DemoNote("Extension", "Read arc consistency without confusing propagation with a solved path.", "REVISE directed arcs between adjacent state variables.", "arc queue, revisions, values removed and domain sizes.", "Sound propagation; replay appears only after extracting an exact legal chain.", "Arc-consistent non-singleton domains are not by themselves a unique solution."),
    "Min-Conflicts": DemoNote("Extension", "Repair a complete state-chain assignment by reducing violated transitions.", "Select a conflicted variable and a value with lower total conflict.", "iteration, conflicted variable, conflict count and fixed seed.", "A zero-conflict verified chain is replayable.", "Not complete or optimal; iteration failure returns repair evidence only."),
    "AI-vs-AI Tournament": DemoNote("Scoring layer", "Score two agents against the same A* reference.", "Run two solvers and classify verified trajectories.", "points, optimal cost, excess cost and invalid-path penalties.", "Fair benchmark when the reference certificate exists.", "Tournament is not a natural adversarial PEAS model."),
    "Minimax": DemoNote("Robustness demo", "Interpret MIN as worst-case robustness, not a real puzzle opponent.", "Alternate MAX promising moves with MIN worst-case legal continuations.", "MAX/MIN nodes, utility and selected root action.", "Depth-limited worst-case decision rule.", "Both sides share legal blank moves because 15-puzzle has no natural adversary."),
    "Alpha-Beta Pruning": DemoNote("Robustness demo", "Learn branch-and-bound pruning over the same worst-case tree.", "Prune branches that cannot change the minimax root value.", "alpha, beta, pruned branches and root utility.", "Same root value as full Minimax for the searched tree.", "Pruning saves nodes; it does not turn the puzzle into a real two-player game."),
    "Expectimax": DemoNote("Chance demo", "Compare expected value against worst-case reasoning.", "Replace MIN with CHANCE outcomes and success probability.", "CHANCE nodes, probabilities and expected utility.", "Depth-limited expected-value policy under the chosen probability model.", "Probability model is educational and must be stated before interpreting the result."),
}


def note_for(algorithm: str) -> DemoNote:
    return ALGORITHM_NOTES[algorithm]
