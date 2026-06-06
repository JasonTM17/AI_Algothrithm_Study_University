---
phase: 2
title: Puzzle Board Redesign + Click-to-Slide
status: completed
priority: P0
effort: 3h
dependencies:
  - 1
---

# Phase 2: Puzzle Board Redesign + Click-to-Slide

## Overview

Thiết kế lại puzzle board với tile 3D chuyên nghiệp, animation hover/active.
Thêm click-to-slide: click trực tiếp vào tile kề blank để di chuyển.

## Requirements

- Functional: Click tile kề blank → tile slide. Tile không kề blank → disabled.
- Non-functional: Animation mượt < 200ms, hover feedback rõ ràng

## Architecture

### Puzzle Board Layout (Streamlit)

```
┌────────────────────────────┐
│  st.columns(4) row 0       │
│  [btn] [btn] [btn] [btn]  │  ← mỗi cell là st.button
│  st.columns(4) row 1       │
│  [btn] [btn] [btn] [btn]  │
│  st.columns(4) row 2       │
│  [btn] [btn] [btn] [btn]  │
│  st.columns(4) row 3       │
│  [btn] [btn] [btn] [btn]  │
└────────────────────────────┘
```

### Click-to-Slide Logic

```python
def _is_adjacent_to_blank(state, tile_idx):
    """Check if tile at tile_idx is adjacent to blank."""
    blank_idx = state.index(0)
    br, bc = blank_idx // 4, blank_idx % 4
    tr, tc = tile_idx // 4, tile_idx % 4
    return abs(br - tr) + abs(bc - tc) == 1

def _get_slide_direction(state, tile_idx):
    """Return action that would slide tile_idx into blank."""
    blank_idx = state.index(0)
    if tile_idx == blank_idx - 1: return "R"  # blank moves right = tile moves left
    if tile_idx == blank_idx + 1: return "L"
    if tile_idx == blank_idx - 4: return "D"
    if tile_idx == blank_idx + 4: return "U"
    return None
```

### Tile Rendering (HTML via st.markdown)

Each tile: `<div>` with gradient bg, number centered, 3D shadow.

```python
def render_clickable_board(state, key_prefix="board"):
    """Render 4x4 board where adjacent tiles are clickable buttons."""
    for r in range(4):
        cols = st.columns(4)
        for c in range(4):
            idx = r * 4 + c
            val = state[idx]
            with cols[c]:
                if val == 0:
                    st.button("", key=f"{key_prefix}_blank", disabled=True)
                elif _is_adjacent_to_blank(state, idx):
                    direction = _get_slide_direction(state, idx)
                    st.button(str(val), key=f"{key_prefix}_{val}",
                             on_click=_handle_slide, args=(direction,),
                             type="primary")
                else:
                    st.button(str(val), key=f"{key_prefix}_{val}",
                             disabled=True)
```

### CSS for Tiles

```css
.puzzle-tile {
    width: 80px; height: 80px;
    border-radius: 12px;
    font-size: 28px; font-weight: 800;
    background: linear-gradient(145deg, #6366f1, #4f46e5);
    color: #fff;
    box-shadow: 0 4px 14px rgba(99,102,241,0.4), inset 0 1px 0 rgba(255,255,255,0.15);
    transition: transform 0.15s cubic-bezier(0.4,0,0.2,1),
                box-shadow 0.15s ease;
}
.puzzle-tile:hover {
    transform: scale(1.05);
    box-shadow: 0 6px 20px rgba(99,102,241,0.6);
}
.puzzle-tile:active {
    transform: scale(0.95);
}
.puzzle-tile.correct {
    background: linear-gradient(145deg, #22c55e, #16a34a);
    box-shadow: 0 4px 14px rgba(34,197,94,0.4);
}
.puzzle-tile.blank {
    background: transparent;
    box-shadow: inset 0 3px 10px rgba(0,0,0,0.5);
    border: 1px dashed rgba(255,255,255,0.08);
}
```

## Related Code Files

- **Modify:** `ui/styles.py` — new tile CSS
- **Modify:** `ui/components.py` — `render_clickable_board()` function
- **Modify:** `app.py` — replace old `render_puzzle_board` calls in Play tab

## Implementation Steps

1. **Add helper functions** to `ui/components.py`:
   - `_is_adjacent_to_blank(state, idx)` → bool
   - `_get_slide_direction(state, idx)` → str | None
   - `render_clickable_board(state, key_prefix)` → renders interactive board

2. **Rewrite tile CSS** in `ui/styles.py`:
   - `.puzzle-tile` base + variants (filled, correct, blank, hover, active)
   - `.puzzle-grid` container
   - Replace old `.puzzle-cell` styles

3. **Update Play tab** in `app.py`:
   - Replace arrow button block with `render_clickable_board()`
   - Keep move counter, Manhattan metric
   - Keep Reset button
   - Remove old `col_l, col_u, col_d, col_r` arrow button layout

4. **Update other tabs** that render puzzle boards:
   - Run Algorithm tab: use render_clickable_board for result display (read-only mode)
   - Step Trace tab: keep using mini/static board for trace inspection

5. **Test interactive play**: scramble → click tiles → solve puzzle hoàn toàn bằng click

## Success Criteria

- [ ] Click tile kề blank → tile moves, move counter increments
- [ ] Click tile không kề blank → nothing happens (disabled)
- [ ] Hover effect visible (scale + glow)
- [ ] Active/press effect visible (scale down)
- [ ] Correct tiles highlight green
- [ ] Manual play solve được puzzle (reach goal → success message)
