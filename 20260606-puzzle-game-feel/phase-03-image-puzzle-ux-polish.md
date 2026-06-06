---
phase: 3
title: Image Puzzle UX Polish
status: completed
priority: P1
effort: 1.5h
dependencies:
  - 2
---

# Phase 3: Image Puzzle UX Polish

## Overview

Hoàn thiện trải nghiệm image puzzle: ảnh thuần 100%, blank checkerboard rõ, preview thumbnail, progress indicator, auto-solve animation.

## Requirements

- Functional: Image puzzle hiển thị ảnh thuần, blank rõ, có preview goal
- Non-functional: Mượt, responsive, game-like feel

## Architecture

### Pure Image Board (không số)

`render_image_board()` đã có từ lần implement trước. Cần polish:
- Tăng tile size lên 100px cho ảnh rõ hơn
- Thêm subtle border cho mỗi tile ảnh để phân biệt ranh giới
- Blank tile: checkerboard pattern CSS (đã có từ Phase 1)
- Goal preview: hiển thị ảnh đầy đủ nhỏ bên cạnh board

### Progress Indicator

```python
# Dưới board, hiển thị:
correct = sum(1 for i, v in enumerate(state) if v == GOAL_STATE[i] and v != 0)
st.progress(correct / 15, text=f"{correct}/15 tiles correct")
```

### Goal Preview Thumbnail

```python
# Bên cạnh board hoặc trong sidebar:
if image_tiles:
    # Ghép 16 tiles lại thành ảnh đầy đủ để preview
    st.sidebar.image(assembled_preview, caption="Goal", width=150)
```

### Click-to-Slide trên ảnh

Đảm bảo `render_image_board()` cho phép click-to-slide:
- Tile ảnh kề blank → clickable, có hover glow
- Tile ảnh xa blank → static, cursor default
- Blank → checkerboard, không clickable

## Related Code Files

- **Modify:** `ui/components.py` — polish render_image_board, add progress, preview
- **Modify:** `ui/styles.py` — image tile polish CSS
- **Modify:** `app.py` — progress bar, goal preview in sidebar

## Implementation Steps

1. **Polish `render_image_board()`**: 
   - Tăng rendering resolution
   - Thêm `1px solid rgba(255,255,255,0.1)` border cho mỗi tile ảnh
   - Clickable tiles có subtle highlight
   - Blank tile có checkerboard pattern

2. **Add progress bar**: `st.progress()` hiển thị % hoàn thành

3. **Add goal preview**: Ghép ảnh từ 16 tiles → hiển thị thumbnail trong sidebar

4. **Auto-solve animation teaser**: Khi solve xong → animation mừng (confetti text hoặc pulse effect)

5. **Edge cases**: 
   - Switch giữa number/image mode khi đang chơi dở
   - Upload ảnh mới khi đang chơi → reset board
   - Blank tile luôn hiển thị rõ (không bị lẫn với dark background)

6. **Test end-to-end**: Upload ảnh → chơi → solve → animation

## Success Criteria

- [ ] Image puzzle: 100% ảnh thuần, không số, không overlay
- [ ] Blank tile hiển thị checkerboard rõ ràng
- [ ] Progress bar hiển thị % hoàn thành
- [ ] Goal preview thumbnail trong sidebar
- [ ] Click tile ảnh → slide animation mượt
- [ ] Solve → animation mừng
- [ ] 67 tests pass
