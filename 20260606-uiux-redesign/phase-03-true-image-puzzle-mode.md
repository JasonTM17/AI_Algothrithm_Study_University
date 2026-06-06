---
phase: 3
title: True Image Puzzle Mode
status: completed
priority: P0
effort: 2h
dependencies:
  - 2
---

# Phase 3: True Image Puzzle Mode

## Overview

Tính năng signature: upload ảnh → cắt 15 mảnh, hiển thị ảnh thuần (không số overlay).
Click-to-slide trên ảnh. Blank tile trống.

## Requirements

- Functional: Upload → 15 mảnh ảnh. Click tile ảnh → slide. Không số.
- Non-functional: Ảnh load nhanh, tile piece rõ nét

## Architecture

### Image Processing (PIL)

```python
def process_uploaded_image(image_file, grid_size=4, tile_px=80):
    """Crop image into grid_size*grid_size tiles, return base64 dict for tiles 1..15."""
    from PIL import Image
    import io, base64

    img = Image.open(image_file).convert("RGBA")
    size = min(img.size)
    img = img.crop((0, 0, size, size))
    img = img.resize((grid_size * tile_px, grid_size * tile_px), Image.LANCZOS)

    tiles = {}
    for idx in range(1, grid_size * grid_size):
        r, c = (idx - 1) // grid_size, (idx - 1) % grid_size
        tile = img.crop((c * tile_px, r * tile_px, (c+1) * tile_px, (r+1) * tile_px))
        buf = io.BytesIO()
        tile.save(buf, format="PNG")
        tiles[idx] = f"data:image/png;base64,{base64.b64encode(buf.getvalue()).decode()}"
    return tiles
```

### Image Board Rendering

Mỗi cell hiển thị `<img>` với CSS background. Click behavior giống number mode.

```python
def render_image_board(state, image_tiles, key_prefix="img"):
    """Render 4x4 board with image tiles (no number overlay)."""
    for r in range(4):
        cols = st.columns(4)
        for c in range(4):
            idx = r * 4 + c
            val = state[idx]
            with cols[c]:
                if val == 0:
                    _render_blank_cell(key_prefix, idx)
                elif _is_adjacent_to_blank(state, idx):
                    direction = _get_slide_direction(state, idx)
                    _render_image_button(image_tiles[val], key_prefix, val,
                                        on_click=_handle_slide, args=(direction,))
                else:
                    _render_image_button(image_tiles[val], key_prefix, val, disabled=True)
```

### Mode Toggle

Sidebar toggle: "Number Mode" / "Image Mode". Session state `puzzle_mode`.

```python
st.sidebar.radio("Puzzle Mode", ["Number", "Image"], key="puzzle_mode")
```

### CSS for Image Tiles

```css
.puzzle-tile.image-tile {
    background: transparent !important;
    padding: 0;
    overflow: hidden;
}
.puzzle-tile.image-tile img {
    width: 100%; height: 100%;
    object-fit: cover;
    border-radius: 10px;
}
```

## Related Code Files

- **Modify:** `ui/components.py` — `render_image_board()`, update `process_uploaded_image()`
- **Modify:** `ui/styles.py` — image tile CSS
- **Modify:** `app.py` — mode toggle in sidebar, conditional rendering in Play tab

## Implementation Steps

1. **Update `process_uploaded_image()`** in `ui/components.py`:
   - Increase tile resolution to 160px (2x for retina)
   - Handle non-square images better (center crop)
   - Return dict mapping tile value → base64 data URL

2. **Create `render_image_board()`** in `ui/components.py`:
   - Same layout as number board but cells show `<img>` only
   - Correct tiles get subtle green border glow
   - Blank cell is empty with dashed border

3. **Add mode toggle** in `app.py` sidebar:
   - Radio: "Number" / "Image"
   - Image uploader chỉ hiện khi Image mode active

4. **Update Play tab** in `app.py`:
   - Conditional: if image mode + image loaded → `render_image_board()`
   - Else → `render_clickable_board()`
   - Remove old `render_puzzle_with_image()` (overlay style)

5. **Update solution path display** (Run Algorithm tab):
   - When result has path + image mode → show image tiles in animation
   - Else → show number tiles

## Success Criteria

- [ ] Upload ảnh JPG/PNG → 15 tile pieces hiển thị đúng
- [ ] Click tile ảnh → slide animation visible
- [ ] Không có số overlay trên ảnh
- [ ] Blank tile trống (transparent/dashed)
- [ ] Toggle Number ↔ Image hoạt động mượt
- [ ] Solve puzzle ảnh → success message
