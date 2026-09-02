#!/usr/bin/env python3
"""Create the night-edition CAMPFIRE charity flow banner with Pillow."""

# Hallmark · pre-emit critique: P5 H5 E5 S5 R5 V4

from __future__ import annotations

import math
import os
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps


HERE = Path(__file__).resolve().parent
CELAVI = HERE / "venue" / "celavi_red.jpg"
HUG_LOGO = HERE / "logo_hug.png"
OUTPUT = HERE / "flow_banner.jpg"

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


def cover_square(path: Path, size: int, focal_x: float = 0.5, focal_y: float = 0.5,
                 zoom: float = 1.0) -> Image.Image:
    src = Image.open(path).convert("RGB")
    side = round(min(src.width, src.height) / zoom)
    left = round((src.width - side) * focal_x)
    top = round((src.height - side) * focal_y)
    left = max(0, min(src.width - side, left))
    top = max(0, min(src.height - side, top))
    return src.crop((left, top, left + side, top + side)).resize(
        (size, size), Image.Resampling.LANCZOS
    )


def circle_photo(base: Image.Image, path: Path, center: tuple[int, int], diameter: int,
                 focal_x: float = 0.5, focal_y: float = 0.5, zoom: float = 1.0,
                 brightness: float = 1.0) -> None:
    size = diameter * SCALE
    photo = cover_square(path, size, focal_x, focal_y, zoom)
    photo = ImageOps.autocontrast(photo, cutoff=(1, 1))
    if brightness != 1.0:
        photo = ImageEnhance.Brightness(photo).enhance(brightness)
    tint = Image.new("RGB", photo.size, DEEPEST_CRIMSON)
    photo = Image.blend(photo, tint, 0.10)

    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse((2, 2, size - 3, size - 3), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(0.55 * SCALE))
    x = round((center[0] - diameter / 2) * SCALE)
    y = round((center[1] - diameter / 2) * SCALE)
    base.paste(photo.convert("RGBA"), (x, y), mask)


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
    # Symmetric outer margins and a slightly larger, higher visual band make
    # fuller use of the 2:1 canvas without crowding the masthead or closing line.
    centers_x = (172, 530, 887, 1244, 1602)
    cy, diameter = 340, 246
    for x in centers_x:
        add_node_glow(base, (x, cy), diameter)

    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    # 1: converging light particles.
    cx = centers_x[0]
    for inset, alpha, width in ((0, 165, 3), (22, 88, 2), (49, 54, 2)):
        r = diameter / 2 - inset
        d.ellipse(sbox((cx - r, cy - r, cx + r, cy + r)),
                  outline=(*CRIMSON, alpha), width=width * SCALE)
    rng = random.Random(31018)
    for _ in range(72):
        angle = rng.random() * math.tau
        radius = (rng.random() ** 1.65) * (diameter * 0.43)
        px, py = cx + math.cos(angle) * radius, cy + math.sin(angle) * radius
        rr = rng.choice((1.2, 1.5, 2.0, 2.8))
        d.ellipse(sbox((px - rr, py - rr, px + rr, py + rr)),
                  fill=(255, 55, 70, rng.randint(90, 225)))
    d.ellipse(sbox((cx - 8, cy - 8, cx + 8, cy + 8)), fill=(255, 91, 103, 235))

    # 2: CAMPFIRE wordmark treatment in a precise crimson ring.
    ring(d, (centers_x[1], cy), diameter)
    ring(d, (centers_x[1], cy), diameter - 18, 1, (*CRIMSON, 105))
    camp = face(LATIN, 23)
    d.text(spos((centers_x[1], cy)), "CAMPFIRE", font=camp, fill=CREAM,
           anchor="mm", stroke_width=0)

    # 3: circular, antialiased photo window.
    base.alpha_composite(layer)
    circle_photo(base, CELAVI, (centers_x[2], cy), diameter, 0.50, 0.46)

    outlines = Image.new("RGBA", base.size, (0, 0, 0, 0))
    od = ImageDraw.Draw(outlines)
    ring(od, (centers_x[2], cy), diameter, 3)

    # 4: the foundation's official logo, unaltered except for proportional scaling.
    logo_center = (centers_x[3], cy)
    circle_size = diameter * SCALE
    circle_x = round((logo_center[0] - diameter / 2) * SCALE)
    circle_y = round((logo_center[1] - diameter / 2) * SCALE)
    white_circle = Image.new("RGBA", (circle_size, circle_size), (255, 255, 255, 255))
    circle_mask = Image.new("L", (circle_size, circle_size), 0)
    ImageDraw.Draw(circle_mask).ellipse((2, 2, circle_size - 3, circle_size - 3), fill=255)
    base.paste(white_circle, (circle_x, circle_y), circle_mask)

    logo_box = round(diameter * 0.74 * SCALE)
    logo = Image.open(HUG_LOGO).convert("RGB")
    logo.thumbnail((logo_box, logo_box), Image.Resampling.LANCZOS)
    logo_x = round(logo_center[0] * SCALE - logo.width / 2)
    logo_y = round(logo_center[1] * SCALE - logo.height / 2)
    base.paste(logo, (logo_x, logo_y))
    ring(od, logo_center, diameter)

    # 5: culture passing onward — fine arcs expanding toward the next generation.
    cx = centers_x[4]
    ring(od, (cx, cy), diameter)
    for radius, start, end, alpha in (
        (34, 205, 335, 225),
        (61, 205, 335, 175),
        (88, 205, 335, 120),
    ):
        od.arc(sbox((cx - radius, cy - radius, cx + radius, cy + radius)),
               start=start, end=end, fill=(*CREAM, alpha), width=3 * SCALE)
    od.ellipse(sbox((cx - 7, cy - 7, cx + 7, cy + 7)), fill=(*CREAM, 230))
    base.alpha_composite(outlines)

    # Labels share a baseline and remain comfortably readable when reduced.
    td = ImageDraw.Draw(base)
    label_font = face(MINCHO, 35)
    small_font = face(SANS, 16)
    labels = (
        "支援者の想い",
        "クラウドファンディング",
        "一夜限りのライブ",
        "収益は全て寄付",
        "文化を、次の世代へ",
    )
    for x, text in zip(centers_x, labels):
        # Slightly smaller only where needed; all still use the same Mincho face.
        f = face(MINCHO, 32) if len(text) >= 10 else label_font
        td.text(spos((x, 493)), text, font=f, fill=CREAM, anchor="ma")

    td.text(spos((centers_x[2], 549)), "CÉ LA VI TOKYO（渋谷・17F）",
            font=small_font, fill=SILVER, anchor="ma")
    td.text(spos((centers_x[3], 549)), "公益財団法人クロノス保全財団",
            font=small_font, fill=SILVER, anchor="ma")
    td.text(spos((centers_x[4], 549)), "教育・文化を支える活動へ",
            font=small_font, fill=SILVER, anchor="ma")


def add_typography(base: Image.Image) -> None:
    d = ImageDraw.Draw(base)
    # Hiragino keeps the requested full-width separator available while the
    # generous tracking retains the restrained editorial look.
    eyebrow = face(SANS, 18)
    draw_tracked(d, (68, 47), "VALHALLA CHARITY LIVE ／ 2026.10.18 SUN",
                 eyebrow, CRIMSON, 3)

    # The closing thought is deliberately detached from the mechanism above.
    closing = face(MINCHO, 35)
    d.line(spos((1374, 719, 1698, 719)), fill=(*CRIMSON, 170), width=2 * SCALE)
    d.text(spos((1698, 751)), "その一夜が、\n文化を継ぐ。", font=closing,
           fill=CREAM, anchor="ra", align="right", spacing=12 * SCALE)


def main() -> None:
    if not CELAVI.exists() or not HUG_LOGO.exists():
        raise FileNotFoundError("Required image assets are missing")

    canvas = make_background()
    add_light_ribbon(canvas, y=340, start=54, end=1720)
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
