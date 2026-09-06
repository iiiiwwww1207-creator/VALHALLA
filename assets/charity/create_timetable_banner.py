#!/usr/bin/env python3
"""Create the night-edition CAMPFIRE charity timetable banner with Pillow."""

# Hallmark · pre-emit critique: P5 H5 E5 S5 R5 V4

from __future__ import annotations

import math
import os
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "timetable_banner.jpg"

W, H = 1774, 887
SCALE = 2  # render large, then downsample for clean circular edges and type
SW, SH = W * SCALE, H * SCALE

BLACK = (5, 3, 7)
CRIMSON = (193, 18, 31)
DARK_CRIMSON = (142, 16, 25)
DEEPEST_CRIMSON = (110, 10, 18)
CREAM = (245, 239, 228)
SILVER = (198, 198, 205)


def first_font(*candidates: str) -> str:
    for candidate in candidates:
        if Path(candidate).exists():
            return candidate
    for root in (Path("/System/Library/Fonts"), Path("/Library/Fonts")):
        if not root.exists():
            continue
        for pattern in ("*.ttc", "*.otf", "*.ttf"):
            found = next(root.rglob(pattern), None)
            if found:
                return str(found)
    raise FileNotFoundError("No macOS TrueType/OpenType font found")


MINCHO = first_font(
    "/System/Library/Fonts/ヒラギノ明朝 ProN.ttc",
    "/System/Library/Fonts/ヒラギノ明朝 ProN.ttc",
    "/System/Library/Fonts/NewYork.ttf",
    "/System/Library/Fonts/Times.ttc",
)
SANS = first_font(
    "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc",
    "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc",
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
)
LATIN = first_font(
    "/System/Library/Fonts/Optima.ttc",
    "/System/Library/Fonts/Avenir Next.ttc",
    "/System/Library/Fonts/HelveticaNeue.ttc",
)


def face(path: str, size: int, index: int = 0) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size=size * SCALE, index=index)


def sbox(box: tuple[float, float, float, float]) -> tuple[int, int, int, int]:
    return tuple(round(v * SCALE) for v in box)


def spos(point: tuple[float, float]) -> tuple[int, int]:
    return tuple(round(v * SCALE) for v in point)


def make_background() -> Image.Image:
    base = Image.new("RGB", (SW, SH), BLACK)

    # Two restrained crimson blooms, blurred heavily into the near-black field.
    bloom = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
    bd = ImageDraw.Draw(bloom)
    bd.ellipse(sbox((-210, 40, 910, 1030)), fill=(*DEEPEST_CRIMSON, 104))
    bd.ellipse(sbox((930, -250, 2180, 760)), fill=(*DEEPEST_CRIMSON, 72))
    bloom = bloom.filter(ImageFilter.GaussianBlur(230 * SCALE))
    base = Image.alpha_composite(base.convert("RGBA"), bloom)

    # Quiet edge vignette keeps attention on the horizontal flow.
    vignette = Image.new("L", (SW, SH), 0)
    vd = ImageDraw.Draw(vignette)
    vd.ellipse(sbox((60, -220, W - 60, H + 255)), fill=205)
    vignette = vignette.filter(ImageFilter.GaussianBlur(135 * SCALE))
    dark = Image.new("RGBA", (SW, SH), (*BLACK, 255))
    base = Image.composite(base, dark, vignette)
    return base


def draw_tracked(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str,
                 font: ImageFont.FreeTypeFont, fill: tuple[int, ...], tracking: int) -> None:
    x, y = spos(xy)
    for char in text:
        draw.text((x, y), char, font=font, fill=fill)
        x += draw.textlength(char, font=font) + tracking * SCALE


def add_light_ribbon(base: Image.Image, y: int, start: int, end: int) -> None:
    glow = Image.new("RGBA", base.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    sy = y * SCALE
    gd.line((start * SCALE, sy, end * SCALE, sy), fill=(*CRIMSON, 150), width=5 * SCALE)
    soft = glow.filter(ImageFilter.GaussianBlur(22 * SCALE))
    base.alpha_composite(soft)

    sharp = Image.new("RGBA", base.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(sharp)
    steps = 330
    for i in range(steps):
        t0, t1 = i / steps, (i + 1) / steps
        x0 = start + (end - start) * t0
        x1 = start + (end - start) * t1 + 1
        edge_fade = math.sin(math.pi * ((t0 + t1) / 2)) ** 0.55
        alpha = round(28 + 190 * edge_fade)
        sd.rectangle(sbox((x0, y - 2, x1, y + 2)), fill=(*CRIMSON, alpha))
    sd.line((start * SCALE, sy, end * SCALE, sy), fill=(255, 77, 91, 120), width=SCALE)
    base.alpha_composite(sharp)

    # A deterministic stream of fine particles sits on and around the ribbon.
    rng = random.Random(20261018)
    particles = Image.new("RGBA", base.size, (0, 0, 0, 0))
    pd = ImageDraw.Draw(particles)
    for _ in range(155):
        x = rng.uniform(start, end)
        dy = rng.gauss(0, 13)
        radius = rng.choice((1.0, 1.2, 1.6, 2.1))
        fade = math.sin(math.pi * (x - start) / (end - start)) ** 0.45
        alpha = round(rng.randint(45, 150) * fade)
        pd.ellipse(sbox((x - radius, y + dy - radius, x + radius, y + dy + radius)),
                   fill=(*CRIMSON, alpha))
    base.alpha_composite(particles)


def add_node_glow(base: Image.Image, center: tuple[int, int], diameter: int) -> None:
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    cx, cy = center
    for expand, alpha, width in ((24, 34, 3), (11, 55, 2)):
        r = diameter / 2 + expand
        ld.ellipse(sbox((cx - r, cy - r, cx + r, cy + r)),
                   outline=(*CRIMSON, alpha), width=width * SCALE)
    base.alpha_composite(layer.filter(ImageFilter.GaussianBlur(9 * SCALE)))


def ring(draw: ImageDraw.ImageDraw, center: tuple[int, int], diameter: int,
         width: int = 3, fill: tuple[int, ...] = (*CRIMSON, 255)) -> None:
    cx, cy = center
    r = diameter / 2
    draw.ellipse(sbox((cx - r, cy - r, cx + r, cy + r)), outline=fill, width=width * SCALE)


def add_nodes(base: Image.Image) -> None:
    # Five equal-size nodes on an exact 345 px rhythm, centered on the canvas.
    centers_x = (197, 542, 887, 1232, 1577)
    cy, diameter = 520, 190

    # Keep the crimson ribbon strictly between adjacent circles.
    radius = diameter // 2
    for left, right in zip(centers_x, centers_x[1:]):
        add_light_ribbon(base, y=cy, start=left + radius, end=right - radius)

    for x in centers_x:
        add_node_glow(base, (x, cy), diameter)

    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for x in centers_x:
        ring(d, (x, cy), diameter, 2)
    base.alpha_composite(layer)

    td = ImageDraw.Draw(base)
    cue_font = face(LATIN, 18)
    time_font = face(LATIN, 60)
    label_font = face(MINCHO, 29)
    cues = ("OPEN", "START", "", "", "END")
    times = ("19:00", "19:30", "20:00", "20:10", "21:30")
    labels = ("開場", "開演", "バンド終了", "MIOタイム", "終演")
    for x, cue, time, label in zip(centers_x, cues, times, labels):
        if cue:
            cue_width = sum(td.textlength(char, font=cue_font) for char in cue)
            cue_width += 5 * SCALE * (len(cue) - 1)
            draw_tracked(td, (round(x - cue_width / (2 * SCALE)), 394), cue,
                         cue_font, CRIMSON, 5)
        td.text(spos((x, cy + 2)), time, font=time_font, fill=CREAM, anchor="mm")
        td.text(spos((x, 660)), label, font=label_font, fill=CREAM, anchor="mm")


def add_typography(base: Image.Image) -> None:
    d = ImageDraw.Draw(base)
    # Hiragino keeps the requested full-width separator available while the
    # generous tracking retains the restrained editorial look.
    eyebrow = face(SANS, 18)
    draw_tracked(d, (68, 47), "VALHALLA CHARITY LIVE ／ TIMETABLE",
                 eyebrow, CRIMSON, 3)

    title = face(MINCHO, 52)
    d.text(spos((W // 2, 275)), "当日の流れ", font=title, fill=CREAM, anchor="mm")

    footer = face(SANS, 17)
    d.text(spos((W // 2, 827)), "2026.10.18 SUN　CÉ LA VI TOKYO（渋谷・17F）",
           font=footer, fill=SILVER, anchor="mm")


def main() -> None:
    canvas = make_background()
    add_nodes(canvas)
    add_typography(canvas)
    canvas = canvas.convert("RGB").resize((W, H), Image.Resampling.LANCZOS)
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
