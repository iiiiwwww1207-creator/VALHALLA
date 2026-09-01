#!/usr/bin/env python3
"""Create the 16:9 CAMPFIRE hero image from the existing vertical flyer."""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import math
import os


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "flyer.jpg"
OUTPUT = HERE / "flyer_wide.jpg"

W, H = 1920, 1080
GOLD = (201, 169, 97)
IVORY = (245, 239, 224)


def first_font(*candidates: str) -> str:
    for candidate in candidates:
        if Path(candidate).exists():
            return candidate
    roots = (Path("/System/Library/Fonts"), Path("/Library/Fonts"))
    for root in roots:
        for pattern in ("*.ttf", "*.ttc", "*.otf"):
            found = next(root.rglob(pattern), None)
            if found:
                return str(found)
    raise FileNotFoundError("No TrueType/OpenType font found")


DIDOT = first_font(
    "/System/Library/Fonts/Supplemental/Didot.ttc",
    "/System/Library/Fonts/NewYork.ttf",
    "/System/Library/Fonts/Times.ttc",
)
OPTIMA = first_font(
    "/System/Library/Fonts/Optima.ttc",
    "/System/Library/Fonts/Supplemental/Times New Roman.ttf",
)
HIRAGINO_BOLD = first_font(
    "/System/Library/Fonts/ヒラギノ角ゴシック W8.ttc",
    "/System/Library/Fonts/ヒラギノ角ゴシック W9.ttc",
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
)


def font(path: str, size: int, index: int = 0) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size=size, index=index)


def tracked_width(draw: ImageDraw.ImageDraw, text: str, face, tracking: int) -> int:
    if not text:
        return 0
    widths = [draw.textlength(ch, font=face) for ch in text]
    return int(round(sum(widths) + tracking * (len(text) - 1)))


def tracked_text(draw, xy, text, face, fill, tracking, stroke_width=0, stroke_fill=None):
    x, y = xy
    for ch in text:
        draw.text(
            (x, y), ch, font=face, fill=fill,
            stroke_width=stroke_width, stroke_fill=stroke_fill,
        )
        x += draw.textlength(ch, font=face) + tracking


def make_background() -> Image.Image:
    im = Image.new("RGB", (W, H))
    px = im.load()
    top = (188, 193, 201)
    mid = (62, 63, 73)
    bottom = (6, 4, 12)
    for y in range(H):
        t = y / (H - 1)
        if t < 0.48:
            q = (t / 0.48) ** 0.9
            a, b = top, mid
        else:
            q = ((t - 0.48) / 0.52) ** 0.72
            a, b = mid, bottom
        row = tuple(round(a[i] * (1 - q) + b[i] * q) for i in range(3))
        for x in range(W):
            # Keep the photographic side subdued so pale wardrobe stays distinct.
            right = max(0.0, (x / (W - 1) - 0.48) / 0.52)
            right_shade = 1.0 - 0.19 * right ** 1.25
            # Gentle edge vignette keeps the white text readable at thumbnail size.
            edge = max(0.0, abs(x - W / 2) / (W / 2) - 0.52) / 0.48
            shade = 1.0 - 0.10 * edge * edge
            px[x, y] = tuple(round(c * shade * right_shade) for c in row)
    return im


def add_people(base: Image.Image) -> None:
    src = Image.open(SOURCE).convert("RGB")
    # Only the portrait area is used; all typography in the source is excluded.
    portrait = src.crop((45, 100, 1055, 715))
    target_w = 1350
    target_h = round(portrait.height * target_w / portrait.width)
    portrait = portrait.resize((target_w, target_h), Image.Resampling.LANCZOS)
    portrait = portrait.filter(ImageFilter.GaussianBlur(0.25))
    portrait = ImageEnhance.Brightness(portrait).enhance(0.82)
    portrait = ImageEnhance.Contrast(portrait).enhance(1.08)

    # Photograph enters softly from the left and dissolves into black at the bottom.
    mask = Image.new("L", portrait.size, 0)
    m = mask.load()
    for y in range(portrait.height):
        ty = y / max(1, portrait.height - 1)
        if ty < 0.035:
            vertical = 0.5 - 0.5 * math.cos(math.pi * ty / 0.035)
        elif ty < 0.85:
            vertical = 1.0
        else:
            u = (ty - 0.85) / 0.15
            vertical = 0.5 * (1.0 + math.cos(math.pi * min(1.0, u)))
        for x in range(portrait.width):
            tx = x / max(1, portrait.width - 1)
            horizontal = min(1.0, max(0.0, (tx - 0.02) / 0.18))
            m[x, y] = round(255 * vertical * horizontal)
    mask = mask.filter(ImageFilter.GaussianBlur(12))
    layer = Image.new("RGB", (W, H), (0, 0, 0))
    alpha = Image.new("L", (W, H), 0)
    pos = (730, 170)
    layer.paste(portrait, pos)
    alpha.paste(mask, pos)
    base.paste(layer, (0, 0), alpha)

    # Reinforce only the final 15% of the lower dissolve.
    veil = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    vp = veil.load()
    fade_start = round(H * 0.85)
    for y in range(fade_start, H):
        a = int(215 * ((y - fade_start) / (H - fade_start)) ** 1.35)
        for x in range(720, W):
            vp[x, y] = (10, 7, 16, a)
    base.paste(veil, (0, 0), veil)


def add_type(base: Image.Image) -> None:
    draw = ImageDraw.Draw(base)
    x = 112

    small = font(OPTIMA, 31)
    tracked_text(draw, (x, 126), "CHARITY LIVE 2026", small, GOLD, 9)

    valhalla = font(DIDOT, 128)
    tracked_text(draw, (x - 2, 201), "VALHALLA", valhalla, GOLD, 7)

    live = font(DIDOT, 61)
    tracked_text(draw, (x + 2, 354), "CHARITY LIVE", live, IVORY, 5)

    # Japanese line is the main message; a restrained dark shadow protects contrast.
    catch = font(HIRAGINO_BOLD, 64)
    draw.text(
        (x, 472), "その夜の全てを、寄付へ。", font=catch, fill=IVORY,
        stroke_width=2, stroke_fill=(40, 36, 42),
    )

    draw.line((x, 610, 844, 610), fill=GOLD, width=2)

    collab = font(OPTIMA, 27)
    tracked_text(
        draw, (x, 654), "CÉ LA VI SHIBUYA × THE UNIVERSITY of TOKYO",
        collab, GOLD, 1,
    )

    date = font(DIDOT, 56)
    tracked_text(draw, (x, 755), "2026 . 10 . 18 SUN", date, GOLD, 4)

    names = font(OPTIMA, 39)
    tracked_text(draw, (x + 2, 864), "MIO / KØU / RAY", names, IVORY, 5)


def main() -> None:
    canvas = make_background()
    add_people(canvas)
    add_type(canvas)
    canvas.save(
        OUTPUT,
        "JPEG",
        quality=88,
        optimize=True,
        progressive=True,
        subsampling="4:2:0",
        dpi=(72, 72),
    )
    size = os.path.getsize(OUTPUT)
    if size > 2 * 1024 * 1024:
        raise RuntimeError(f"Output exceeds 2 MB: {size} bytes")
    print(f"{OUTPUT} | {canvas.width}x{canvas.height} | {size} bytes")


if __name__ == "__main__":
    main()
