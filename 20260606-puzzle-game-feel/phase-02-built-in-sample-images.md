---
phase: 2
title: Built-in Sample Images
status: completed
priority: P0
effort: 1.5h
dependencies:
  - 1
---

# Phase 2: Built-in Sample Images

## Overview

Tạo 5 ảnh mẫu built-in (gradient art + pattern) để người chơi có thể chơi puzzle ảnh NGAY LẬP TỨC không cần upload. Chọn ảnh từ sidebar dropdown.

## Requirements

- Functional: Chọn ảnh mẫu → puzzle hiển thị ảnh đã cắt → chơi được ngay
- Non-functional: Ảnh generate bằng Python PIL, không cần network

## Architecture

### Sample Image Generator (Python/PIL)

```python
import io, base64
from PIL import Image, ImageDraw

def generate_gradient_sunset(tile_size=80, grid=4):
    """Sunset gradient image."""
    w = h = tile_size * grid
    img = Image.new('RGBA', (w, h))
    for y in range(h):
        r = int(255 * (1 - y/h))
        g = int(100 + 100 * y/h)
        b = int(180 * y/h)
        for x in range(w):
            img.putpixel((x, y), (r, g, b, 255))
    return _img_to_tiles(img, grid, tile_size)

def generate_mandala_pattern(tile_size=80, grid=4):
    """Geometric mandala pattern."""
    # Draw concentric shapes with ImageDraw
    ...

def generate_nature_landscape(tile_size=80, grid=4):
    """Simple landscape with sky, mountains, grass."""
    ...

SAMPLE_IMAGES = {
    "Sunset Gradient": generate_gradient_sunset,
    "Ocean Blue": generate_ocean_gradient,
    "Geometric Mandala": generate_mandala_pattern,
    "Mountain Landscape": generate_nature_landscape,
    "Neon Grid": generate_neon_pattern,
}
```

### Sidebar Selector

```python
# In app.py sidebar, after image upload section:
st.sidebar.markdown("---")
st.sidebar.subheader("Sample Images")
sample_choice = st.sidebar.selectbox(
    "Built-in images",
    ["None"] + list(SAMPLE_IMAGES.keys()),
    key="sample_image"
)
if sample_choice != "None":
    tiles = generate_sample_tiles(sample_choice)
    st.session_state.image_tiles = tiles
```

### Auto-load Default Image

Khi app start lần đầu, tự động load 1 ảnh mẫu mặc định ("Sunset Gradient") để showcase ngay image puzzle mode.

## Related Code Files

- **Create:** `ui/sample_images.py` — built-in image generators
- **Modify:** `ui/components.py` — export `generate_sample_tiles()`
- **Modify:** `app.py` — sample image selector in sidebar

## Implementation Steps

1. **Create `ui/sample_images.py`**: 5 image generators dùng PIL. Mỗi hàm trả về dict `{1..15: base64_data_url}`
2. **Add sidebar selector** in `app.py`: dropdown chọn ảnh mẫu, auto-apply vào `st.session_state.image_tiles`
3. **Auto-load default**: Khi `image_tiles` rỗng và chưa upload → tự động load "Sunset Gradient"
4. **Show preview thumbnail**: Khi chọn ảnh mẫu, hiển thị thumbnail nhỏ để xem trước
5. **Test**: chọn từng ảnh mẫu → puzzle hiển thị đúng, chơi được

## Success Criteria

- [ ] 5 ảnh mẫu có sẵn, chọn được từ sidebar
- [ ] Chọn ảnh → puzzle tự động chuyển sang image mode
- [ ] Ảnh mẫu đẹp, màu sắc rõ ràng, dễ phân biệt các mảnh
- [ ] Không cần network để load ảnh
- [ ] 67 tests pass
