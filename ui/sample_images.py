"""Built-in sample images for instant image puzzle play."""
import io
import os
import base64
import math
from PIL import Image, ImageDraw

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


def _generate_gradient_raw(colors, grid=4, px=100):
    """Create a vertical gradient image from list of (r,g,b) colors."""
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
    return img


def sunset_gradient_raw():
    """Warm sunset: deep orange → pink → purple."""
    return _generate_gradient_raw([
        (255, 94, 0),    # deep orange
        (255, 154, 0),   # orange
        (255, 94, 77),   # coral
        (180, 50, 140),  # magenta
        (75, 0, 130),    # indigo
    ])


def sunset_gradient():
    return _img_to_tiles(sunset_gradient_raw())


def ocean_blues_raw():
    """Ocean blues: light cyan → deep navy."""
    return _generate_gradient_raw([
        (0, 206, 209),   # turquoise
        (0, 150, 199),   # ocean blue
        (0, 100, 180),   # deep blue
        (25, 55, 140),   # navy
        (5, 25, 80),     # dark navy
    ])


def ocean_blues():
    return _img_to_tiles(ocean_blues_raw())


def forest_green_raw():
    """Forest: lime → emerald → dark green."""
    return _generate_gradient_raw([
        (144, 238, 144),  # light green
        (80, 200, 120),   # medium green
        (34, 139, 34),    # forest green
        (0, 100, 0),      # dark green
        (0, 60, 0),       # deep forest
    ])


def forest_green():
    return _img_to_tiles(forest_green_raw())


def neon_synthwave_raw():
    """Synthwave neon: cyan → magenta → purple grid."""
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
    return img


def neon_synthwave():
    return _img_to_tiles(neon_synthwave_raw())


def geometric_mandala_raw():
    """Geometric pattern with concentric shapes."""
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
        rad = math.radians(angle)
        ex, ey = cx + 180 * math.cos(rad), cy + 180 * math.sin(rad)
        draw.line([(cx, cy), (ex, ey)], fill=(150, 100, 255, 60), width=2)
    return img


def geometric_mandala():
    return _img_to_tiles(geometric_mandala_raw())


def load_real_image_raw(filename):
    """Load a real image and crop to square from center."""
    base_paths = [
        os.path.join("ui", "assets", filename),
        os.path.join("assets", filename),
        filename
    ]
    img_path = None
    for p in base_paths:
        if os.path.exists(p):
            img_path = p
            break
            
    if img_path:
        try:
            img = Image.open(img_path)
            img = img.convert("RGBA")
            w, h = img.size
            size = min(w, h)
            left = (w - size) // 2
            top = (h - size) // 2
            return img.crop((left, top, left + size, top + size))
        except Exception as e:
            import logging
            logging.warning(f"Failed to load image raw {filename}: {e}")
    return None


def load_real_image(filename):
    """Load real image and return sliced tiles."""
    img = load_real_image_raw(filename)
    if img:
        return _img_to_tiles(img, grid_size=4, tile_px=100)
    return sunset_gradient()


def cyberpunk_city():
    return load_real_image("cyberpunk_city.png")


def cosmic_cat():
    return load_real_image("cosmic_cat.png")


def magic_castle():
    return load_real_image("magic_castle.png")


def autumn_zen_garden():
    return load_real_image("autumn_zen_garden.png")


def shiba_inu_scholar():
    return load_real_image("shiba_inu_scholar.png")


def steampunk_locomotive():
    return load_real_image("steampunk_locomotive.png")


def cozy_winter_cabin():
    return load_real_image("cozy_winter_cabin.png")


def coral_reef_fish():
    return load_real_image("coral_reef_fish.png")


SAMPLE_IMAGES = {
    "🏙️ Cyberpunk City": cyberpunk_city,
    "🐱 Cosmic Astronaut Cat": cosmic_cat,
    "🏰 Floating Magic Castle": magic_castle,
    "🍁 Autumn Zen Garden": autumn_zen_garden,
    "🐕 Shiba Inu Scholar": shiba_inu_scholar,
    "🚂 Steampunk Locomotive": steampunk_locomotive,
    "🏡 Cozy Winter Cabin": cozy_winter_cabin,
    "🐠 Colorful Coral Reef": coral_reef_fish,
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


def get_full_sample_image(name: str):
    """Return a PIL Image object representing the full un-sliced sample choice."""
    mapping = {
        "🏙️ Cyberpunk City": lambda: load_real_image_raw("cyberpunk_city.png"),
        "🐱 Cosmic Astronaut Cat": lambda: load_real_image_raw("cosmic_cat.png"),
        "🏰 Floating Magic Castle": lambda: load_real_image_raw("magic_castle.png"),
        "🍁 Autumn Zen Garden": lambda: load_real_image_raw("autumn_zen_garden.png"),
        "🐕 Shiba Inu Scholar": lambda: load_real_image_raw("shiba_inu_scholar.png"),
        "🚂 Steampunk Locomotive": lambda: load_real_image_raw("steampunk_locomotive.png"),
        "🏡 Cozy Winter Cabin": lambda: load_real_image_raw("cozy_winter_cabin.png"),
        "🐠 Colorful Coral Reef": lambda: load_real_image_raw("coral_reef_fish.png"),
        "Sunset Gradient": sunset_gradient_raw,
        "Ocean Blues": ocean_blues_raw,
        "Forest Green": forest_green_raw,
        "Neon Synthwave": neon_synthwave_raw,
        "Geometric Mandala": geometric_mandala_raw,
    }
    
    fn = mapping.get(name)
    if fn:
        img = fn()
        if img:
            return img
    # Fallback to sunset gradient raw
    return sunset_gradient_raw()
