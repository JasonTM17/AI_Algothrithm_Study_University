"""Pillow renderer for compact, deterministic README GIFs."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from scripts.readme_gif_runner import DemoEvidence


WIDTH, HEIGHT = 800, 450
BG = (9, 15, 13)
PANEL = (19, 29, 24)
TEXT = (244, 241, 232)
MUTED = (174, 169, 157)
GREEN = (127, 175, 111)
GOLD = (238, 181, 91)
BLUE = (94, 173, 214)
RED = (214, 116, 92)


def save_demo_gif(evidence: DemoEvidence, output_path: Path, *, image_mode: bool = False) -> dict:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    frames = [
        _render_frame(evidence, state, index, image_mode=image_mode)
        for index, state in enumerate(evidence.states)
    ]
    paletted = [
        frame.convert("P", palette=Image.Palette.ADAPTIVE, colors=128)
        for frame in frames
    ]
    paletted[0].save(
        output_path,
        save_all=True,
        append_images=paletted[1:],
        duration=720,
        loop=0,
        optimize=True,
    )
    return {
        "frame_count": len(frames),
        "dimensions": [WIDTH, HEIGHT],
        "file_bytes": output_path.stat().st_size,
    }


def _render_frame(
    evidence: DemoEvidence,
    state: tuple[int, ...],
    frame_index: int,
    *,
    image_mode: bool,
) -> Image.Image:
    image = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(image)
    fonts = _fonts()
    spec = evidence.spec

    draw.rounded_rectangle((18, 18, 782, 432), radius=14, outline=(54, 65, 58), width=2)
    _chip(draw, (36, 32), spec.group, GREEN, fonts["small"])
    draw.text((36, 62), spec.algorithm, fill=TEXT, font=fonts["title"])
    draw.text((36, 102), f"real solver trace | frame {frame_index + 1}/{len(evidence.states)}",
              fill=MUTED, font=fonts["small"])

    board_box = (42, 135, 326, 419)
    if image_mode:
        _draw_image_board(image, state, board_box)
    else:
        _draw_number_board(draw, state, board_box, fonts)

    _draw_evidence_panel(draw, evidence, frame_index, fonts)
    return image


def _draw_number_board(draw: ImageDraw.ImageDraw, state: tuple[int, ...], box: tuple[int, int, int, int], fonts) -> None:
    x0, y0, x1, y1 = box
    tile = (x1 - x0 - 15) // 4
    for index, value in enumerate(state):
        row, col = divmod(index, 4)
        x = x0 + col * (tile + 5)
        y = y0 + row * (tile + 5)
        if value == 0:
            draw.rounded_rectangle((x, y, x + tile, y + tile), radius=8, fill=(5, 8, 7), outline=(45, 52, 47))
            draw.text((x + tile // 2 - 4, y + tile // 2 - 11), "_", fill=(98, 105, 98), font=fonts["body"])
            continue
        fill = _tile_fill(value)
        draw.rounded_rectangle((x, y, x + tile, y + tile), radius=8, fill=fill, outline=(37, 46, 40), width=2)
        text = str(value)
        bbox = draw.textbbox((0, 0), text, font=fonts["tile"])
        draw.text((x + (tile - bbox[2]) / 2, y + (tile - bbox[3]) / 2 - 2), text, fill=(16, 19, 17), font=fonts["tile"])


def _draw_image_board(image: Image.Image, state: tuple[int, ...], box: tuple[int, int, int, int]) -> None:
    sample = _sample_image().resize((284, 284))
    x0, y0, x1, _ = box
    tile = 67
    draw = ImageDraw.Draw(image)
    for index, value in enumerate(state):
        row, col = divmod(index, 4)
        x = x0 + col * (tile + 4)
        y = y0 + row * (tile + 4)
        if value == 0:
            draw.rounded_rectangle((x, y, x + tile, y + tile), radius=8, fill=(4, 6, 6), outline=(47, 55, 50))
            continue
        source_index = value - 1
        sr, sc = divmod(source_index, 4)
        crop = sample.crop((sc * 71, sr * 71, sc * 71 + 67, sr * 71 + 67))
        image.paste(crop, (x, y))
        draw.rounded_rectangle((x, y, x + tile, y + tile), radius=8, outline=GREEN, width=2)


def _draw_evidence_panel(draw: ImageDraw.ImageDraw, evidence: DemoEvidence, frame_index: int, fonts) -> None:
    x = 360
    draw.rounded_rectangle((348, 132, 758, 418), radius=12, fill=PANEL, outline=(54, 65, 58))
    labels = _labels(evidence, frame_index)
    y = 152
    for label, value, color in labels[:4]:
        draw.rounded_rectangle((x, y, x + 178, y + 54), radius=8, fill=(13, 20, 17), outline=(58, 69, 62))
        draw.text((x + 12, y + 9), label, fill=MUTED, font=fonts["small"])
        draw.text((x + 12, y + 28), value, fill=color, font=fonts["metric"])
        x = 560 if x == 360 else 360
        y += 66 if x == 360 else 0
    y = 288
    for fact in evidence.facts[:4]:
        draw.text((368, y), f"- {fact}", fill=TEXT if y == 288 else MUTED, font=fonts["body"])
        y += 27
    draw.text((368, 396), _mode_caption(evidence), fill=GOLD, font=fonts["small"])


def _tile_fill(value: int) -> tuple[int, int, int]:
    """Value-stable but restrained tile shade for academic screenshots."""
    shades = [
        (184, 181, 166),
        (172, 169, 156),
        (160, 160, 148),
        (145, 151, 140),
    ]
    return shades[(value - 1) // 4]


def _labels(evidence: DemoEvidence, frame_index: int) -> list[tuple[str, str, tuple[int, int, int]]]:
    result = evidence.result
    if result is None:
        return [("score A", "A*", GREEN), ("score B", "Greedy", GOLD), ("round", "1", BLUE), ("winner", "see trace", TEXT)]
    trace = result.trace[min(frame_index, len(result.trace) - 1)] if result.trace else None
    h_value = trace.h if trace else 0
    f_value = trace.f if trace else 0
    return [
        ("g(n)", str(frame_index), GREEN),
        ("h(n)", f"{h_value:g}", GOLD),
        ("f(n)", f"{f_value:g}", BLUE),
        ("frontier", str(result.max_frontier_size or (trace.frontier_size if trace else 0)), TEXT),
    ]


def _mode_caption(evidence: DemoEvidence) -> str:
    captions = {
        "graph": "state-space search: frontier/reached/path evidence",
        "local": "local search: candidate evaluation evidence",
        "complex": "belief/conditional/online evidence, not plain path search",
        "csp": "CSP model evidence: variables, domains, constraints",
        "adversarial": "robustness/game-tree evidence: MAX/MIN/CHANCE",
        "tournament": "certificate-first AI-vs-AI scoring",
    }
    return captions.get(evidence.spec.mode, "verified algorithm evidence")


def _chip(draw: ImageDraw.ImageDraw, pos: tuple[int, int], text: str, color: tuple[int, int, int], font) -> None:
    x, y = pos
    bbox = draw.textbbox((0, 0), text, font=font)
    draw.rounded_rectangle((x, y, x + bbox[2] + 18, y + 24), radius=7, fill=(21, 35, 27), outline=color)
    draw.text((x + 9, y + 5), text, fill=color, font=font)


def _fonts() -> dict[str, ImageFont.ImageFont]:
    def load(size: int, bold: bool = False):
        names = ["DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf", "arialbd.ttf" if bold else "arial.ttf"]
        for name in names:
            try:
                return ImageFont.truetype(name, size)
            except OSError:
                continue
        return ImageFont.load_default()

    return {
        "title": load(30, True),
        "tile": load(27, True),
        "metric": load(24, True),
        "body": load(17, False),
        "small": load(13, True),
    }


def _sample_image() -> Image.Image:
    path = Path("ui/assets/cyberpunk_city.png")
    if path.exists():
        return Image.open(path).convert("RGB")
    return Image.linear_gradient("L").resize((284, 284)).convert("RGB")
