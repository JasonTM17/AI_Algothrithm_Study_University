"""Academic notes used by README GIF assets and documentation."""

from __future__ import annotations

from dataclasses import dataclass


MEDIA_VERIFIED_AT = "2026-06-27"


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
        "purpose": "Model conditional, belief-state and online variants that extend the basic 15-puzzle PEAS.",
        "question": "What does the agent know, and is the output a path, a policy or an online trace?",
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
        "Separate hidden actual state from belief-state decision making.",
        "Maintain a belief set when observations reveal no tile positions.",
        "belief size, planner votes, fallback votes and action trace.",
        "Demonstrates belief reasoning; not a standard full-observation solver.",
        "Hidden state is shown only as debug evidence.",
    ),
    "Searching for partially observable problems": DemoNote(
        "Extension",
        "Use known tile positions to reduce the belief set.",
        "Filter belief candidates using a known-tile matrix.",
        "known positions, belief size, planner votes and fallback reason.",
        "Can propose legal actions under partial knowledge.",
        "With too few known tiles, the belief set can still be ambiguous.",
    ),
    "LRTA*": DemoNote(
        "Extension",
        "Study online heuristic learning one action at a time.",
        "Update H(s) after observing local successors.",
        "online step, H update, chosen action and cap reason.",
        "Online learning demo, not an offline optimal certificate.",
        "The node cap is a max online-step cap in the UI.",
    ),
    "CSP Definition": DemoNote("Extension", "Name variables, domains and constraints.", "Build a state-chain CSP model.", "variables/domains/constraints count.", "Model definition only.", "A model is not yet a solved trajectory."),
    "Constraint Propagation": DemoNote("Extension", "See domains shrink before search.", "Apply AC-3 style propagation.", "domain reductions and wipe-out status.", "Sound pruning for represented constraints.", "Propagation alone may not decide the puzzle."),
    "Path Consistency": DemoNote("Extension", "Inspect consistency across triples of variables.", "Check pair/triple compatibility in the model.", "consistency events and remaining domains.", "Educational consistency evidence.", "Not a shortest-path solver."),
    "Global Constraints": DemoNote("Extension", "Use all-different and structural constraints.", "Apply global constraint checks over the state chain.", "constraint status and domain evidence.", "Rules out impossible assignments.", "Does not replace graph-search optimality."),
    "Backtracking Search": DemoNote("Extension", "Search assignments in the CSP model.", "Depth-first assignment with constraint checks.", "assigned variables, backtrack reason and final path if found.", "Can solve small exact-horizon demos.", "Horizon-bound; not a global shortest-path claim."),
    "Min-Conflicts": DemoNote("Extension", "Repair an assignment by reducing conflicts.", "Randomized local repair over CSP variables.", "conflict count, selected variable and seed.", "Useful concept for CSP repair.", "Better suited to N-Queens style CSPs than canonical 15-puzzle."),
    "Constraint Graphs": DemoNote("Extension", "Visualize variables as a constraint network.", "Build graph nodes/edges from CSP relations.", "constraint graph summary and consistency evidence.", "Explains structure, not a solver certificate.", "Graph readability matters more than path optimality here."),
    "AI-vs-AI Tournament": DemoNote("Scoring layer", "Score two agents against the same A* reference.", "Run two solvers and classify verified trajectories.", "points, optimal cost, excess cost and invalid-path penalties.", "Fair benchmark when the reference certificate exists.", "Tournament is not a natural adversarial PEAS model."),
    "Minimax": DemoNote("Robustness demo", "Interpret MIN as worst-case robustness, not a real puzzle opponent.", "Alternate MAX promising moves with MIN worst-case legal continuations.", "MAX/MIN nodes, utility and selected root action.", "Depth-limited worst-case decision rule.", "Both sides share legal blank moves because 15-puzzle has no natural adversary."),
    "Alpha-Beta Pruning": DemoNote("Robustness demo", "Learn branch-and-bound pruning over the same worst-case tree.", "Prune branches that cannot change the minimax root value.", "alpha, beta, pruned branches and root utility.", "Same root value as full Minimax for the searched tree.", "Pruning saves nodes; it does not turn the puzzle into a real two-player game."),
    "Expectimax": DemoNote("Chance demo", "Compare expected value against worst-case reasoning.", "Replace MIN with CHANCE outcomes and success probability.", "CHANCE nodes, probabilities and expected utility.", "Depth-limited expected-value policy under the chosen probability model.", "Probability model is educational and must be stated before interpreting the result."),
}


def note_for(algorithm: str) -> DemoNote:
    return ALGORITHM_NOTES[algorithm]
