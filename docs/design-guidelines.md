# Design Guidelines

## Visual Direction

Use a restrained academic dashboard style:

- Neutral dark background with teal, blue, amber, and violet accents.
- Compact cards and tables for scanability.
- Badges for algorithm role and environment model.
- Minimal decorative emoji in primary academic content.
- Use text-first academic labels; avoid emoji as command/status icons.
- Provide visible keyboard focus states and reduced-motion support.
- Render core PEAS/rubric/taxonomy content as responsive cards before detailed tables.
- Prefer sober dashboard hierarchy over game-like decoration: the board is evidence, not a hero illustration.
- Keep cards 8-10px radius with consistent borders, shadow, and density.

## UI Priorities

- Make the correct academic classification visible before detailed prose.
- Show the exam path near the top of Play, Run, Compare, Theory/PEAS, and Hand-Tracing.
- Put PEAS, guarantees, and selection rubric near the top of Theory/Compare pages.
- Keep Play usable as a puzzle board, but frame it as a solver lab.
- Keep Advanced modes explicitly labeled as extensions.
- Preserve mobile usability: no horizontal scroll, readable cards, and sidebar labels that wrap.
- Treat launcher/app mode as the recommended classroom entrypoint; keep Streamlit web mode as the developer fallback.

## Content Rules

- Do not imply CSP, Minimax, Alpha-Beta, Expectimax, no-observation, or partial-observation modes are natural 15-puzzle solvers.
- Present graph coloring through map coloring or another graph game, never as a direct 15-puzzle algorithm.
- When an algorithm is not optimal or not complete, state that directly.
- Prefer concise tables and cards over long paragraphs for exam-facing material.
- Preserve existing solver behavior unless a dedicated algorithm fix is planned.
- Provide an instructor-facing grading report with PEAS, taxonomy, proof cards, benchmark caveats, and verification commands.
