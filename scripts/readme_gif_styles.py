"""Shared visual profiles for verified README GIFs."""

from __future__ import annotations

from dataclasses import dataclass

from PIL import ImageFont


@dataclass(frozen=True)
class RenderProfile:
    name: str
    width: int
    height: int
    board_size: int
    title_size: int
    tile_size: int
    body_size: int
    small_size: int


@dataclass(frozen=True)
class ThemePalette:
    bg: tuple[int, int, int]
    wash: tuple[int, int, int]
    panel: tuple[int, int, int]
    card: tuple[int, int, int]
    text: tuple[int, int, int]
    muted: tuple[int, int, int]
    faint: tuple[int, int, int]
    teal: tuple[int, int, int]
    teal_dark: tuple[int, int, int]
    mint: tuple[int, int, int]
    blue: tuple[int, int, int]
    gold: tuple[int, int, int]
    red: tuple[int, int, int]
    grid: tuple[int, int, int]


PROFILES = {
    "hero": RenderProfile("hero", 1280, 720, 430, 44, 32, 24, 18),
    "group": RenderProfile("group", 960, 540, 300, 34, 28, 20, 15),
    "algorithm": RenderProfile("algorithm", 960, 540, 300, 34, 28, 20, 15),
}

BG = (242, 247, 247)
WASH = (222, 246, 241)
PANEL = (255, 255, 255)
CARD = (248, 251, 251)
TEXT = (20, 30, 45)
MUTED = (102, 116, 138)
FAINT = (149, 162, 179)
TEAL = (16, 154, 139)
TEAL_DARK = (13, 119, 108)
MINT = (214, 246, 239)
BLUE = (62, 109, 190)
GOLD = (198, 138, 57)
RED = (190, 83, 71)
GRID = (214, 226, 232)

THEMES = {
    "light": ThemePalette(BG, WASH, PANEL, CARD, TEXT, MUTED, FAINT, TEAL, TEAL_DARK, MINT, BLUE, GOLD, RED, GRID),
    "dark": ThemePalette(
        (9, 15, 13), (19, 35, 29), (19, 24, 22), (15, 21, 18),
        (244, 241, 232), (172, 170, 158), (99, 107, 99),
        (127, 175, 111), (144, 195, 128), (32, 54, 38),
        (94, 173, 214), (238, 181, 91), (214, 116, 92), (58, 69, 62),
    ),
}


def fonts(profile: RenderProfile) -> dict[str, ImageFont.ImageFont]:
    def load(size: int, bold: bool = False):
        names = [
            "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf",
            "arialbd.ttf" if bold else "arial.ttf",
        ]
        for name in names:
            try:
                return ImageFont.truetype(name, size)
            except OSError:
                continue
        return ImageFont.load_default()

    return {
        "title": load(profile.title_size, True),
        "subtitle": load(profile.body_size, False),
        "tile": load(profile.tile_size, True),
        "metric": load(profile.tile_size + 2, True),
        "body": load(profile.body_size, False),
        "body_bold": load(profile.body_size, True),
        "small": load(profile.small_size, True),
        "tiny": load(max(11, profile.small_size - 3), False),
    }
