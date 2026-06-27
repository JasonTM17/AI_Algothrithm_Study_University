"""Pillow renderer for deterministic, readable README GIFs."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

from core.heuristics import manhattan_distance
from core.puzzle import GOAL_STATE
from scripts.readme_gif_panel import panel_content
from scripts.readme_gif_runner import DemoEvidence
from scripts.readme_gif_styles import (
    BG, BLUE, CARD, FAINT, GOLD, GRID, MINT, MUTED, PANEL, PROFILES, RED,
    TEAL, TEAL_DARK, TEXT, THEMES, WASH, RenderProfile, fonts,
)


def save_demo_gif(
    evidence: DemoEvidence,
    output_path: Path,
    *,
    image_mode: bool = False,
    profile: str = "algorithm",
    theme: str = "light",
) -> dict:
    _apply_theme(theme)
    render_profile = PROFILES[profile]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    frames = [
        _render_frame(evidence, state, index, render_profile, image_mode=image_mode)
        for index, state in enumerate(evidence.states)
    ]
    paletted = [frame.convert("P", palette=Image.Palette.ADAPTIVE, colors=128) for frame in frames]
    paletted[0].save(
        output_path,
        save_all=True,
        append_images=paletted[1:],
        duration=760 if profile == "hero" else 700,
        loop=0,
        optimize=True,
    )
    return {
        "profile": profile,
        "theme": theme,
        "frame_count": len(frames),
        "dimensions": [render_profile.width, render_profile.height],
        "file_bytes": output_path.stat().st_size,
    }


def _apply_theme(theme: str) -> None:
    palette = THEMES[theme]
    globals().update({
        "BG": palette.bg,
        "WASH": palette.wash,
        "PANEL": palette.panel,
        "CARD": palette.card,
        "TEXT": palette.text,
        "MUTED": palette.muted,
        "FAINT": palette.faint,
        "TEAL": palette.teal,
        "TEAL_DARK": palette.teal_dark,
        "MINT": palette.mint,
        "BLUE": palette.blue,
        "GOLD": palette.gold,
        "RED": palette.red,
        "GRID": palette.grid,
    })


def _render_frame(
    evidence: DemoEvidence,
    state: tuple[int, ...],
    frame_index: int,
    profile: RenderProfile,
    *,
    image_mode: bool,
) -> Image.Image:
    image = Image.new("RGB", (profile.width, profile.height), BG)
    draw = ImageDraw.Draw(image)
    font = fonts(profile)
    _background(draw, profile)
    if profile.name == "hero":
        _hero_layout(image, draw, evidence, state, frame_index, profile, font, image_mode)
    else:
        _standard_layout(image, draw, evidence, state, frame_index, profile, font)
    return image


def _background(draw: ImageDraw.ImageDraw, profile: RenderProfile) -> None:
    draw.rectangle((0, 0, profile.width, profile.height), fill=BG)
    line = (18, 27, 24) if _is_dark_theme() else (236, 244, 245)
    wash_alt = (13, 22, 19) if _is_dark_theme() else (233, 242, 253)
    for y in range(0, profile.height, 18):
        draw.line((0, y, profile.width, y), fill=line, width=1)
    draw.ellipse((profile.width - 210, -90, profile.width + 170, 290), fill=WASH)
    draw.ellipse((-120, profile.height - 150, 240, profile.height + 150), fill=wash_alt)


def _standard_layout(image, draw, evidence, state, frame_index, profile, font) -> None:
    spec = evidence.spec
    draw.text((48, 34), spec.algorithm, fill=TEXT, font=font["title"])
    _chip(draw, (48, 86), evidence.termination.replace("_", " "), TEAL, font["small"])
    _chip(draw, (250, 86), spec.group, BLUE, font["small"])
    board_box = (54, 124, 54 + profile.board_size, 124 + profile.board_size)
    _draw_number_board(draw, state, board_box, font)
    _draw_side_panel(draw, evidence, frame_index, (400, 124, 906, 466), font)
    _footer(draw, evidence, profile, font)
    _progress(draw, frame_index, len(evidence.states), (695, 500), 172)


def _hero_layout(image, draw, evidence, state, frame_index, profile, font, image_mode: bool) -> None:
    spec = evidence.spec
    draw.text((54, 32), "A* Search replay: image tiles move step by step", fill=TEXT, font=font["title"])
    draw.text((56, 86), "f(n)=g(n)+h(n), h(n)=Manhattan Distance, each legal blank move costs 1", fill=MUTED, font=font["subtitle"])
    board_box = (68, 138, 68 + profile.board_size, 138 + profile.board_size)
    if image_mode:
        _draw_image_board(image, draw, state, board_box)
    else:
        _draw_number_board(draw, state, board_box, font)
    draw.text((92, 585), "Main board: tile style is stable; only positions change.", fill=MUTED, font=font["small"])
    panel = (560, 138, 1195, 568)
    draw.rounded_rectangle(panel, radius=24, fill=PANEL, outline=(181, 206, 208), width=2)
    _chip(draw, (590, 170), "A* SEARCH", TEAL, font["small"])
    step = _path_step(evidence, frame_index)
    total = len(evidence.actions) if evidence.actions else max(len(evidence.states) - 1, 1)
    draw.text((590, 214), f"Step {step}/{total}", fill=TEXT, font=font["title"])
    prev_action, next_action = _actions(evidence, step)
    draw.text((590, 272), f"Previous action: {prev_action}", fill=TEXT, font=font["body"])
    draw.text((590, 318), f"Next action: {next_action}", fill=TEAL_DARK, font=font["body"])
    _draw_goal_mini(draw, (992, 172, 1148, 328), font)
    h = manhattan_distance(state, GOAL_STATE)
    metric_y = 382
    for x, label, value, color in (
        (590, "G(N)", str(step), TEAL_DARK),
        (770, "H(N)", f"{h:g}", GOLD),
        (950, "F(N)", f"{step + h:g}", TEXT),
    ):
        _metric_card(draw, (x, metric_y, x + 145, metric_y + 78), label, value, color, font)
    result = evidence.result
    stats = "Expanded: -   Generated: -   Frontier max: -"
    if result is not None:
        stats = f"Expanded: {result.nodes_expanded}   Generated: {result.nodes_generated}   Frontier max: {result.max_frontier_size}"
    draw.text((590, 486), stats, fill=MUTED, font=font["small"])
    _progress(draw, frame_index, len(evidence.states), (590, 640), 605, height=13)


def _draw_side_panel(draw, evidence, frame_index, box, font) -> None:
    x0, y0, x1, y1 = box
    draw.rounded_rectangle(box, radius=18, fill=PANEL, outline=GRID, width=2)
    content = panel_content(evidence, frame_index)
    metrics = content.metrics[:4]
    gap = 8
    available = x1 - x0 - 44
    card_width = (available - gap * (len(metrics) - 1)) // len(metrics)
    for index, (label, value, accent) in enumerate(metrics):
        left = x0 + 22 + index * (card_width + gap)
        _metric_card(
            draw,
            (left, y0 + 22, left + card_width, y0 + 86),
            label,
            value,
            _accent_color(accent),
            font,
        )
    _info_box(
        draw,
        (x0 + 22, y0 + 104, x1 - 22, y0 + 166),
        "ACTION / SELECTION",
        content.selection,
        font,
        max_lines=1,
    )
    _info_box(
        draw,
        (x0 + 22, y0 + 184, x1 - 22, y1 - 18),
        "WHY THIS STEP",
        content.explanation,
        font,
        max_lines=3,
    )


def _draw_number_board(draw, state, box, font) -> None:
    x0, y0, x1, y1 = box
    board_fill = (20, 36, 31) if _is_dark_theme() else (226, 246, 244)
    outline = (56, 75, 65) if _is_dark_theme() else (203, 224, 226)
    draw.rounded_rectangle((x0 - 18, y0 - 18, x1 + 18, y1 + 18), radius=24, fill=board_fill, outline=outline)
    tile = (x1 - x0 - 24) // 4
    for index, value in enumerate(state):
        row, col = divmod(index, 4)
        x, y = x0 + col * (tile + 8), y0 + row * (tile + 8)
        if value == 0:
            fill, border, text_fill = ((23, 45, 37), TEAL, TEAL_DARK) if _is_dark_theme() else ((218, 248, 241), TEAL, TEXT)
        else:
            fill, border, text_fill = ((185, 198, 184), (59, 76, 66), (16, 22, 18)) if _is_dark_theme() else (PANEL, (224, 233, 237), TEXT)
        draw.rounded_rectangle((x, y, x + tile, y + tile), radius=14, fill=fill, outline=border, width=2)
        text = "0" if value == 0 else str(value)
        bbox = draw.textbbox((0, 0), text, font=font["tile"])
        draw.text((x + (tile - bbox[2]) / 2, y + (tile - bbox[3]) / 2 - 2), text, fill=text_fill, font=font["tile"])


def _draw_image_board(image, draw, state, box) -> None:
    sample = _sample_image().resize((box[2] - box[0], box[3] - box[1]))
    x0, y0, x1, _ = box
    tile = (x1 - x0 - 24) // 4
    draw.rounded_rectangle((x0 - 18, y0 - 18, box[2] + 18, box[3] + 18), radius=24, fill=(20, 36, 36), outline=(108, 159, 149), width=2)
    for index, value in enumerate(state):
        row, col = divmod(index, 4)
        x, y = x0 + col * (tile + 8), y0 + row * (tile + 8)
        if value == 0:
            draw.rounded_rectangle((x, y, x + tile, y + tile), radius=14, fill=(14, 24, 24), outline=(45, 66, 64), width=2)
            continue
        sr, sc = divmod(value - 1, 4)
        crop = sample.crop((sc * (tile + 8), sr * (tile + 8), sc * (tile + 8) + tile, sr * (tile + 8) + tile))
        image.paste(crop, (x, y))
        draw.rounded_rectangle((x, y, x + tile, y + tile), radius=14, outline=(126, 190, 115), width=3)


def _draw_goal_mini(draw, box, font) -> None:
    fill = (12, 18, 16) if _is_dark_theme() else (249, 252, 252)
    outline = (84, 70, 50) if _is_dark_theme() else (198, 216, 218)
    draw.rounded_rectangle(box, radius=18, fill=fill, outline=outline, width=2)
    x0, y0, x1, _ = box
    tile = (x1 - x0 - 32) // 4
    for index, value in enumerate(GOAL_STATE):
        row, col = divmod(index, 4)
        x, y = x0 + 16 + col * (tile + 2), y0 + 16 + row * (tile + 2)
        tile_fill = (172, 186, 171) if value else (5, 8, 7)
        draw.rounded_rectangle((x, y, x + tile, y + tile), radius=6, fill=tile_fill)
        label = "_" if value == 0 else str(value)
        bbox = draw.textbbox((0, 0), label, font=font["small"])
        draw.text((x + (tile - bbox[2]) / 2, y + (tile - bbox[3]) / 2 - 1), label, fill=TEXT if value else PANEL, font=font["small"])


def _metric_card(draw, box, label, value, color, font) -> None:
    draw.rounded_rectangle(box, radius=14, fill=CARD, outline=GRID, width=2)
    draw.text((box[0] + 14, box[1] + 10), label, fill=MUTED, font=font["small"])
    draw.text((box[0] + 14, box[1] + 35), value, fill=color, font=font["metric"])


def _accent_color(name: str):
    return {
        "teal": TEAL_DARK,
        "blue": BLUE,
        "gold": GOLD,
        "red": RED,
        "text": TEXT,
    }.get(name, TEXT)


def _info_box(draw, box, label, value, font, *, max_lines: int = 3) -> None:
    draw.rounded_rectangle(box, radius=14, fill=CARD, outline=GRID, width=2)
    draw.text((box[0] + 14, box[1] + 12), label, fill=TEAL_DARK, font=font["small"])
    _wrapped(
        draw,
        value,
        (box[0] + 14, box[1] + 40),
        box[2] - box[0] - 28,
        font["body"],
        TEXT,
        max_lines=max_lines,
    )


def _chip(draw, pos, text, color, font) -> None:
    bbox = draw.textbbox((0, 0), text, font=font)
    draw.rounded_rectangle((pos[0], pos[1], pos[0] + bbox[2] + 24, pos[1] + 30), radius=15, fill=MINT, outline=(221, 232, 238))
    draw.text((pos[0] + 12, pos[1] + 7), text, fill=color, font=font)


def _footer(draw, evidence, profile, font) -> None:
    text = f"Actual core run  |  seed {evidence.spec.seed}  |  {evidence.spec.mechanism}"
    draw.text((54, profile.height - 46), text[:110], fill=MUTED, font=font["small"])


def _progress(draw, index, total, pos, width, height=9) -> None:
    x, y = pos
    track = (40, 51, 44) if _is_dark_theme() else (214, 224, 230)
    dot_idle = (48, 61, 52) if _is_dark_theme() else (207, 218, 225)
    draw.rounded_rectangle((x, y, x + width, y + height), radius=height // 2, fill=track)
    filled = int(width * ((index + 1) / max(total, 1)))
    draw.rounded_rectangle((x, y, x + filled, y + height), radius=height // 2, fill=TEAL)
    for dot in range(total):
        dx = x + dot * min(18, width // max(total, 1))
        draw.ellipse((dx, y - 21, dx + 9, y - 12), fill=TEAL if dot == index else dot_idle)


def _path_step(evidence, frame_index: int) -> int:
    return evidence.state_indices[frame_index] if frame_index < len(evidence.state_indices) else frame_index


def _actions(evidence, step: int) -> tuple[str, str]:
    previous = "Initialize" if step == 0 or not evidence.actions else evidence.actions[min(step - 1, len(evidence.actions) - 1)]
    next_action = "Goal" if step >= len(evidence.actions) else evidence.actions[step]
    return previous, next_action


def _wrapped(draw, text, pos, max_width, font, fill, *, max_lines: int = 4) -> None:
    words, lines, current = text.split(), [], ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if draw.textlength(candidate, font=font) <= max_width:
            current = candidate
        else:
            lines.append(current)
            current = word
    lines.append(current)
    for i, line in enumerate(lines[:max_lines]):
        draw.text((pos[0], pos[1] + i * 28), line, fill=fill if i == 0 else MUTED, font=font)


def _sample_image() -> Image.Image:
    path = Path("ui/assets/cyberpunk_city.png")
    if path.exists():
        return Image.open(path).convert("RGB")
    return Image.linear_gradient("L").resize((430, 430)).convert("RGB")


def _is_dark_theme() -> bool:
    return sum(BG) < 120
