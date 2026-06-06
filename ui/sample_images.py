"""Built-in sample images for instant image puzzle play."""
import io
import base64


def _img_to_tiles(img, grid_size=4, tile_px=100):
    """Convert PIL Image to dict of {tile_val: base64_data_url}."""
    tiles = {}
    img = img.resize((grid_size * tile_px, grid_size * tile_px))
    for idx in range(1, grid_size * grid_size):
        r, c = (idx - 1) // grid_size, (idx - 1) % grid_size
        tile = img.crop((c * tile_px, r * tile_px, (c + 1) * tile_px, (r + 1) * tile_px))
        buf = io.BytesIO()
        tile.save(buf, format="PNG")
        tiles[idx] = f"data:image/png;base64,{base64.b64encode(buf.getvalue()).decode()}"
    return tiles


def _create_gradient_image(colors, grid=4, px=100):
    """Create a vertical gradient image from list of (r,g,b) colors."""
    from PIL import Image
    w, h = grid * px, grid * px
    img = Image.new("RGBA", (w, h))
    pixels = img.load()
    for y in range(h):
        t = y / h
        idx = t * (len(colors) - 1)
        i0, i1 = int(idx), min(int(idx) + 1, len(colors) - 1)
        frac = idx - i0
        r = int(colors[i0][0] * (1 - frac) + colors[i1][0] * frac)
        g = int(colors[i0][1] * (1 - frac) + colors[i1][1] * frac)
        b = int(colors[i0][2] * (1 - frac) + colors[i1][2] * frac)
        for x in range(w):
            pixels[x, y] = (r, g, b, 255)
    return _img_to_tiles(img, grid, px)


def sunset_gradient():
    """Warm sunset: deep orange → pink → purple."""
    return _create_gradient_image([
        (255, 94, 0),    # deep orange
        (255, 154, 0),   # orange
        (255, 94, 77),   # coral
        (180, 50, 140),  # magenta
        (75, 0, 130),    # indigo
    ])


def ocean_blues():
    """Ocean blues: light cyan → deep navy."""
    return _create_gradient_image([
        (0, 206, 209),   # turquoise
        (0, 150, 199),   # ocean blue
        (0, 100, 180),   # deep blue
        (25, 55, 140),   # navy
        (5, 25, 80),     # dark navy
    ])


def forest_green():
    """Forest: lime → emerald → dark green."""
    return _create_gradient_image([
        (144, 238, 144),  # light green
        (80, 200, 120),   # medium green
        (34, 139, 34),    # forest green
        (0, 100, 0),      # dark green
        (0, 60, 0),       # deep forest
    ])


def neon_synthwave():
    """Synthwave neon: cyan → magenta → purple grid."""
    from PIL import Image, ImageDraw
    px, grid = 100, 4
    w = h = grid * px
    img = Image.new("RGBA", (w, h))
    pixels = img.load()
    for y in range(h):
        t = y / h
        r = int(180 * (1 - t) + 255 * t * 0.5)
        g = int(50 * (1 - t) + 20 * t)
        b = int(100 * (1 - t) + 180 * t)
        for x in range(w):
            pixels[x, y] = (r, g, b, 255)

    draw = ImageDraw.Draw(img)
    for i in range(1, grid):
        draw.line([(i * px, 0), (i * px, h)], fill=(0, 255, 255, 80), width=2)
        draw.line([(0, i * px), (w, i * px)], fill=(255, 0, 255, 80), width=2)
    return _img_to_tiles(img, grid, px)


def geometric_mandala():
    """Geometric pattern with concentric shapes."""
    from PIL import Image, ImageDraw
    px, grid = 100, 4
    w = h = grid * px
    img = Image.new("RGBA", (w, h), (15, 15, 30, 255))
    draw = ImageDraw.Draw(img)
    cx, cy = w // 2, h // 2
    for i in range(6):
        r = 20 + i * 30
        color = (100 + i * 25, 80 + i * 15, 200 - i * 20, 150)
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=color, width=3)
    for angle in range(0, 360, 45):
        import math
        rad = math.radians(angle)
        ex, ey = cx + 180 * math.cos(rad), cy + 180 * math.sin(rad)
        draw.line([(cx, cy), (ex, ey)], fill=(150, 100, 255, 60), width=2)
    return _img_to_tiles(img, grid, px)


SAMPLE_IMAGES = {
    "Sunset Gradient": sunset_gradient,
    "Ocean Blues": ocean_blues,
    "Forest Green": forest_green,
    "Neon Synthwave": neon_synthwave,
    "Geometric Mandala": geometric_mandala,
}


def generate_sample_tiles(name: str) -> dict:
    """Generate puzzle tiles for a named sample image."""
    fn = SAMPLE_IMAGES.get(name)
    if fn:
        return fn()
    return {}
