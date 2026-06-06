---
phase: 1
title: Real Slide Animation + Tile Design
status: completed
priority: P0
effort: 2h
dependencies: []
---

# Phase 1: Real Slide Animation + Tile Design

## Overview

Overhaul CSS + render logic để tiles có animation trượt thật sự và thiết kế giống game puzzle mobile.

## Requirements

- Functional: Click tile → animation trượt vào vị trí blank
- Non-functional: 60fps feel, tile depth rõ ràng

## Architecture

### Slide Animation Strategy

Vì Streamlit rerender toàn bộ page mỗi lần click, CSS transition trên element position sẽ không work như SPA.
**Giải pháp:** Dùng CSS `@keyframes` slide-in animation trên từng tile khi board thay đổi.

```css
@keyframes tileSlide {
    from { transform: translate(var(--slide-x), var(--slide-y)); }
    to   { transform: translate(0, 0); }
}
.puzzle-tile.animate-slide {
    animation: tileSlide 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}
```

Mỗi tile khi render sẽ biết hướng di chuyển của nó (blank di chuyển L/R/U/D → tile di chuyển ngược lại).

### Tile 3D Design

```css
.puzzle-tile {
    width: 80px; height: 80px;
    border-radius: 14px;
    font-size: 30px; font-weight: 800;
    /* 3D gradient with highlight edge */
    background: linear-gradient(145deg, #7c3aed, #5b21b6);
    /* Multi-layer shadow for depth */
    box-shadow:
        0 6px 20px rgba(0,0,0,0.4),           /* ambient */
        0 2px 6px rgba(0,0,0,0.3),            /* contact */
        inset 0 2px 0 rgba(255,255,255,0.2),   /* top highlight */
        inset 0 -2px 4px rgba(0,0,0,0.15);     /* bottom shadow */
    color: #fff;
    text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    cursor: pointer;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
    user-select: none;
}
.puzzle-tile:hover:not([disabled]) {
    transform: translateY(-3px);
    box-shadow:
        0 10px 28px rgba(0,0,0,0.5),
        0 4px 10px rgba(0,0,0,0.35),
        inset 0 2px 0 rgba(255,255,255,0.25),
        inset 0 -2px 4px rgba(0,0,0,0.15);
}
.puzzle-tile:active:not([disabled]) {
    transform: scale(0.94);
    box-shadow:
        0 2px 8px rgba(0,0,0,0.4),
        inset 0 1px 0 rgba(255,255,255,0.1);
}
.puzzle-tile.correct {
    background: linear-gradient(145deg, #22c55e, #15803d);
    box-shadow:
        0 6px 20px rgba(34,197,94,0.4),
        0 2px 6px rgba(0,0,0,0.2),
        inset 0 2px 0 rgba(255,255,255,0.2);
}
.puzzle-tile.blank {
    background: #1a1d27;
    box-shadow: inset 0 4px 16px rgba(0,0,0,0.6);
    border: 1px dashed rgba(255,255,255,0.08);
    cursor: default;
}
```

### Tile Color Palette (per number)

Mỗi tile có màu gradient riêng dựa trên hàng của nó:
- Row 0: purple tones (#7c3aed → #5b21b6)
- Row 1: blue tones (#6366f1 → #4f46e5)
- Row 2: cyan tones (#0891b2 → #0e7490)
- Row 3: pink tones (#db2777 → #be185d)

### Checkerboard Blank Pattern

```css
.puzzle-tile.blank::after {
    content: '';
    position: absolute;
    inset: 0;
    background-image:
        linear-gradient(45deg, rgba(255,255,255,0.03) 25%, transparent 25%),
        linear-gradient(-45deg, rgba(255,255,255,0.03) 25%, transparent 25%),
        linear-gradient(45deg, transparent 75%, rgba(255,255,255,0.03) 75%),
        linear-gradient(-45deg, transparent 75%, rgba(255,255,255,0.03) 75%);
    background-size: 20px 20px;
    background-position: 0 0, 0 10px, 10px -10px, -10px 0px;
    border-radius: 14px;
}
```

## Related Code Files

- **Modify:** `ui/styles.py` — new tile CSS with 3D, checkerboard, animations
- **Modify:** `ui/components.py` — `render_clickable_board()` add slide animation class
- **Modify:** `app.py` — track previous state for animation direction

## Implementation Steps

1. **Rewrite tile CSS** in `ui/styles.py`: 3D gradient, multi-layer shadow, hover lift, active press, checkerboard blank, row-based colors
2. **Add slide animation** in `ui/components.py`: track previous board state, compute slide direction per tile, add `animate-slide` class with `--slide-x`/`--slide-y` CSS vars
3. **Update `render_clickable_board`**: wrap tiles in `st.markdown` HTML with animation classes (bypass Streamlit button for better animation control)
4. **Test**: click tiles liên tục → animation mượt, không giật

## Success Criteria

- [ ] Click tile → thấy tile "trượt" vào vị trí mới (animation visible)
- [ ] Tiles có bóng 3D rõ ràng (highlight top + shadow bottom)
- [ ] Hover: tile nâng lên + glow
- [ ] Active: tile nhấn xuống
- [ ] Blank tile có checkerboard pattern
- [ ] Mỗi hàng tiles có màu gradient riêng
- [ ] 67 tests pass
