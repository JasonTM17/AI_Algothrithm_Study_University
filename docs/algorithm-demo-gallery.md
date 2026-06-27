# Algorithm Demo Gallery

Mỗi GIF trong trang này được sinh bởi `scripts/generate-readme-gifs.py` từ solver/model thật. Manifest semantic nằm ở `docs/assets/algorithm-demos/manifest.json` và ghi rõ start, goal, seed, tham số, termination, `path_verified`, `goal_reached` và `optimality_proven`.

## Uninformed Search

| Thuật toán | Demo |
|---|---|
| BFS | ![BFS](assets/algorithm-demos/bfs.gif) |
| DFS | ![DFS](assets/algorithm-demos/dfs.gif) |
| UCS | ![UCS](assets/algorithm-demos/ucs.gif) |
| IDS | ![IDS](assets/algorithm-demos/ids.gif) |

## Informed Search

| Thuật toán | Demo |
|---|---|
| Greedy Best-First | ![Greedy Best-First](assets/algorithm-demos/greedy-best-first.gif) |
| A* | ![A*](assets/algorithm-demos/astar.gif) |
| IDA* | ![IDA*](assets/algorithm-demos/idastar.gif) |

## Local Search

| Thuật toán | Demo |
|---|---|
| Simple Hill Climbing | ![Simple Hill Climbing](assets/algorithm-demos/simple-hill-climbing.gif) |
| Steepest-Ascent Hill Climbing | ![Steepest-Ascent Hill Climbing](assets/algorithm-demos/steepest-ascent-hill-climbing.gif) |
| Stochastic Hill Climbing | ![Stochastic Hill Climbing](assets/algorithm-demos/stochastic-hill-climbing.gif) |
| Random-Restart Hill Climbing | ![Random-Restart Hill Climbing](assets/algorithm-demos/random-restart-hill-climbing.gif) |
| Local Beam Search | ![Local Beam Search](assets/algorithm-demos/local-beam-search.gif) |
| Simulated Annealing | ![Simulated Annealing](assets/algorithm-demos/simulated-annealing.gif) |

## Complex Environments

| Thuật toán | Demo |
|---|---|
| AND-OR Search | ![AND-OR Search](assets/algorithm-demos/and-or-search.gif) |
| Searching with no observation | ![Searching with no observation](assets/algorithm-demos/searching-with-no-observation.gif) |
| Searching for partially observable problems | ![Searching for partially observable problems](assets/algorithm-demos/searching-for-partially-observable-problems.gif) |
| LRTA* | ![LRTA*](assets/algorithm-demos/lrtastar.gif) |

## CSP

| Thuật toán | Demo |
|---|---|
| CSP Definition | ![CSP Definition](assets/algorithm-demos/csp-definition.gif) |
| Constraint Propagation | ![Constraint Propagation](assets/algorithm-demos/constraint-propagation.gif) |
| Path Consistency | ![Path Consistency](assets/algorithm-demos/path-consistency.gif) |
| Global Constraints | ![Global Constraints](assets/algorithm-demos/global-constraints.gif) |
| Backtracking Search | ![Backtracking Search](assets/algorithm-demos/backtracking-search.gif) |
| Min-Conflicts | ![Min-Conflicts](assets/algorithm-demos/min-conflicts.gif) |
| Constraint Graphs | ![Constraint Graphs](assets/algorithm-demos/constraint-graphs.gif) |

## AI-vs-AI Tournament

| Thuật toán | Demo |
|---|---|
| AI-vs-AI Tournament | ![AI-vs-AI Tournament](assets/algorithm-demos/ai-vs-ai-tournament.gif) |
| Minimax | ![Minimax](assets/algorithm-demos/minimax.gif) |
| Alpha-Beta Pruning | ![Alpha-Beta Pruning](assets/algorithm-demos/alpha-beta-pruning.gif) |
| Expectimax | ![Expectimax](assets/algorithm-demos/expectimax.gif) |

## Tái Tạo

```bash
python scripts/generate-readme-gifs.py --featured
python scripts/generate-readme-gifs.py --all
python scripts/generate-readme-gifs.py --check
```
