# System Architecture

```mermaid
flowchart LR
    U[Browser learner] --> S[Streamlit UI]
    S --> P[Puzzle game]
    S --> R[Standard solver lab]
    S --> A[Advanced concept lab]
    R --> C[Core puzzle and heuristics]
    R --> G[Run certificate and search graph]
    P --> C
    P --> G
    A --> M[Map CSP and extension models]
```

The standard solver lab accepts only deterministic 15-puzzle algorithms. Extension environments remain isolated in the Advanced concept lab and are not ranked against standard solvers.

Every successful puzzle run contains a legal state/action path certificate. The search visualization draws an edge only when applying its recorded action to the parent produces the child state. Trace capture is bounded for browser responsiveness and reports truncation explicitly.
