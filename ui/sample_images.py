"""Built-in sample images for instant image puzzle play."""
import io
import os
import base64
from PIL import Image

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
    # Default fallback to blank tiles if failed
    fallback = Image.new("RGBA", (400, 400), (35, 27, 21, 255))
    return _img_to_tiles(fallback, grid_size=4, tile_px=100)


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
    }
    
    fn = mapping.get(name)
    if fn:
        img = fn()
        if img:
            return img
    # Default fallback
    return load_real_image_raw("cyberpunk_city.png")
