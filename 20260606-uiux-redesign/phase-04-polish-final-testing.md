---
phase: 4
title: Polish & Final Testing
status: completed
priority: P1
effort: 1.5h
dependencies:
  - 3
---

# Phase 4: Polish & Final Testing

## Overview

CSS fine-tuning, edge case fixes, full regression test (67 tests + manual QA 6 tabs).

## Requirements

- Functional: Tất cả 27 thuật toán chạy, 6 tabs hoạt động
- Non-functional: Không visual glitch, animation consistent

## Related Code Files

- **Modify:** `ui/styles.py` — polish CSS
- **Modify:** `ui/components.py` — bug fixes
- **Modify:** `app.py` — edge cases

## Implementation Steps

1. **CSS Polish** in `ui/styles.py`:
   - Fix Streamlit default style overrides (sidebar, metric labels)
   - Ensure scrollbar styled consistently
   - Fix any z-index stacking issues
   - Tune spacing between sections
   - Verify all 6 group badge colors render correctly

2. **Edge Case Fixes** in `app.py` + `ui/components.py`:
   - Unsolvable state: disable Run button with clear message
   - Empty image tiles dict: graceful fallback to number mode
   - Very long algorithm runs: timeout handling
   - Path animation with image mode: handle step-by-step

3. **Manual QA — 6 tabs**:
   - **Play**: Scramble → click-to-slide → solve. Toggle number/image mode.
   - **Run Algorithm**: Run A* with Manhattan. Verify metrics, trace, tree.
   - **Step Trace**: Slider through steps, verify Node/Frontier/Reached panels.
   - **Compare**: Run 3+ algorithms, verify comparison table.
   - **Theory**: Browse all 6 groups, verify Vietnamese content renders.
   - **Advanced**: Test each CSP/Complex/Game mode.

4. **Regression Test**:
   ```bash
   python -m pytest tests/ -v
   ```
   All 67 tests MUST pass.

5. **Visual Check**:
   - Resize browser → layout không vỡ
   - Dark theme consistent mọi tab
   - No emoji anywhere (visual scan)
   - Hover effects trên tiles mượt

## Success Criteria

- [ ] 67/67 tests pass
- [ ] Tất cả 27 thuật toán chạy không lỗi
- [ ] 6 tabs render đúng, không visual glitch
- [ ] Click-to-slide hoạt động trong cả number và image mode
- [ ] Image upload → puzzle → solve hoạt động end-to-end
- [ ] 0 emoji trong toàn bộ UI
- [ ] Animation mượt, không giật lag
