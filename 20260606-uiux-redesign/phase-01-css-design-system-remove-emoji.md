---
phase: 1
title: CSS Design System & Remove Emoji
status: completed
priority: P0
effort: 2h
dependencies: []
---

# Phase 1: CSS Design System & Remove Emoji

## Overview

Thay toàn bộ CSS hiện tại bằng design system chuyên nghiệp (slate/indigo palette, Inter font).
Gỡ tất cả emoji trong `app.py` — tabs, buttons, titles, sidebar, status messages.

## Requirements

- Functional: App chạy không emoji, giao diện tối chuyên nghiệp
- Non-functional: CSS phải có hierarchy rõ ràng, dễ maintain

## Architecture

### Color Palette

| Token | Value | Usage |
|-------|-------|-------|
| `--bg-app` | `#0f1117` | Background chính |
| `--bg-surface` | `#1a1d27` | Card, board container |
| `--bg-elevated` | `#222636` | Hover states |
| `--accent` | `#6366f1` | Primary buttons, links |
| `--accent-hover` | `#818cf8` | Hover accent |
| `--success` | `#22c55e` | Correct tiles |
| `--error` | `#ef4444` | Error states |
| `--text-primary` | `#e2e8f0` | Headings, body |
| `--text-secondary` | `#94a3b8` | Captions, labels |

### Typography

```css
font-family: 'Inter', 'Segoe UI', system-ui, -apple-system, sans-serif;
```

### Spacing Scale

4px base: 4, 8, 12, 16, 20, 24, 32, 48

### Border Radius

- Cards: 8px
- Tiles: 12px
- Board: 16px
- Buttons: 8px

### Shadows

- `sm`: `0 1px 3px rgba(0,0,0,0.3)`
- `md`: `0 4px 14px rgba(0,0,0,0.4)`
- `lg`: `0 8px 30px rgba(0,0,0,0.5)`
- `glow-accent`: `0 0 20px rgba(99,102,241,0.3)`
- `glow-success`: `0 0 20px rgba(34,197,94,0.3)`

## Related Code Files

- **Modify:** `ui/styles.py` — full CSS rewrite
- **Modify:** `app.py` — remove all emoji characters

## Implementation Steps

1. **Rewrite `STYLES` string** in `ui/styles.py`:
   - New CSS custom properties on `.stApp`
   - Puzzle grid styles (`.puzzle-grid`, `.puzzle-cell`, variants)
   - Mini puzzle styles for trace tables
   - Group badges (`.group-badge`, 6 color variants)
   - Metric cards, result cards, scrollbar styles
   - Keep existing animation keyframes (`@keyframes goalPulse`, `slideIn`)

2. **Remove all emoji** from `app.py`:
   - `page_icon=""` (empty string)
   - Tab labels: `"Play"`, `"Run Algorithm"`, `"Step Trace"`, `"Compare"`, `"Theory"`, `"Advanced"`
   - Sidebar title: `"15-Puzzle AI"`
   - All button labels: strip emoji prefix
   - All `st.success()` / `st.error()` / `st.warning()` messages: strip emoji
   - `st.balloons()` → remove or replace with `st.success()` text-only

3. **Verify**: `streamlit run app.py` → tất cả 6 tabs không còn emoji, màu sắc đúng palette

## Success Criteria

- [ ] CSS loaded không lỗi (Streamlit không warning về unsafe HTML)
- [ ] 0 emoji trong toàn bộ `app.py` (grep: `[\u{1F300}-\u{1FAFF}]` )
- [ ] Color palette đúng: bg #0f1117, accent #6366f1, text #e2e8f0
- [ ] 67 tests vẫn pass
