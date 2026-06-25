# Design Guidelines

## Visual Direction

Use a tactile solver-laboratory dashboard style:

- Graphite/off-black workbench background with copper/amber measurement accents.
- One dominant accent color; semantic green/red remain only for validity and failure states.
- Technical Vietnamese-safe typography with monospace numerals for metrics and trace data.
- Physical, instrument-like 15-puzzle board with slate tray, beveled tiles, and recessed blank slot.
- Lab-record cards, dividers, and role tags for algorithm role and environment model.
- No decorative emoji in primary academic content.
- Use text-first academic labels; avoid emoji as command/status icons.
- Provide visible keyboard focus states and reduced-motion support.
- Render core PEAS/rubric/taxonomy content as responsive cards before detailed tables.
- Prefer solver-lab hierarchy over generic SaaS cards: the board is evidence, not a hero illustration.
- Use tinted inner borders and shadows instead of neon glow or generic purple/blue AI gradients.
- Keep motion GPU-safe: transform and opacity only, with reduced-motion support.

## UI Priorities

- Make the correct academic classification visible before detailed prose.
- Show the exam path near the top of Play, Run, Compare, Theory/PEAS, and Hand-Tracing.
- Put PEAS, guarantees, and selection rubric near the top of Theory/Compare pages.
- Keep Play usable as a puzzle board, but frame it as a solver lab.
- Keep Advanced modes explicitly labeled as extensions.
- Preserve mobile usability: no horizontal scroll, readable cards, and sidebar labels that wrap.
- Keep input/control text at least 16px on mobile to avoid forced zoom.
- Treat the Streamlit browser app as the single classroom entrypoint; do not reintroduce desktop launchers.

## Content Rules

- Do not imply CSP, Minimax, Alpha-Beta, Expectimax, no-observation, or partial-observation modes are natural 15-puzzle solvers.
- Present AC-3 as bounded exact-horizon CSP evidence: domain sizes, revisions, removed values, legal replay when found, and domain wipe-out otherwise.
- Keep group comparison columns stable and scannable: step rule, time, space, steps/output, and guarantee.
- For game/chance demos, label returned actions as selected variation or sample outcome paths, not full game trees or optimal puzzle certificates.
- For AI-vs-AI Tournament, show the A* optimal reference, path efficiency, score reason, legality status, excess cost, runtime, nodes, and deterministic tie-break result.
- Replay both certified AI trajectories on one shared step control; a shorter trajectory stays on its final state while the other continues.
- Do not use raw runtime or cross-family node counts to manufacture a winner when solution quality is tied.
- State that tournament scoring compares agents on the same puzzle; it is not a natural adversarial PEAS model for 15-puzzle.
- When an algorithm is not optimal or not complete, state that directly.
- Prefer concise tables and cards over long paragraphs for exam-facing material.
- Preserve existing solver behavior unless a dedicated algorithm fix is planned.
- Provide an instructor-facing grading report with PEAS, taxonomy, proof cards, benchmark caveats, and verification commands.
