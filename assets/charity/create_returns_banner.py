#!/usr/bin/env python3
"""Create the CAMPFIRE charity support-course banner with Pillow."""

from __future__ import annotations

import math
import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps


HERE = Path(__file__).resolve().parent
YASUDA = HERE / "venue" / "yasuda_dusk.jpg"
OUTPUT = HERE / "returns_banner.jpg"

W, H = 1774, 887
SCALE = 2
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
        if root.exists():
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


def face(path: str, size: int, index: int = 0) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size=size * SCALE, index=index)


def sbox(box: tuple[float, ...]) -> tuple[int, ...]:
    return tuple(round(value * SCALE) for value in box)


def spos(point: tuple[float, ...]) -> tuple[int, ...]:
    return tuple(round(value * SCALE) for value in point)


def make_background() -> Image.Image:
    base = Image.new("RGB", (SW, SH), BLACK).convert("RGBA")
    bloom = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
    bd = ImageDraw.Draw(bloom)
    bd.ellipse(sbox((-260, 110, 920, 1120)), fill=(*DEEPEST_CRIMSON, 92))
    bd.ellipse(sbox((920, -350, 2180, 680)), fill=(*DEEPEST_CRIMSON, 68))
    base = Image.alpha_composite(base, bloom.filter(ImageFilter.GaussianBlur(235 * SCALE)))

    vignette = Image.new("L", (SW, SH), 0)
    ImageDraw.Draw(vignette).ellipse(sbox((50, -230, W - 50, H + 250)), fill=212)
    vignette = vignette.filter(ImageFilter.GaussianBlur(140 * SCALE))
    return Image.composite(base, Image.new("RGBA", base.size, (*BLACK, 255)), vignette)


def draw_tracked(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str,
                 font: ImageFont.FreeTypeFont, fill: tuple[int, ...], tracking: int) -> None:
    x, y = spos(xy)
    for char in text:
        draw.text((x, y), char, font=font, fill=fill)
        x += draw.textlength(char, font=font) + tracking * SCALE


def add_light_ribbon(base: Image.Image, y: int, start: int, end: int) -> None:
    glow = Image.new("RGBA", base.size, (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.line(spos((start, y, end, y)), fill=(*CRIMSON, 145), width=5 * SCALE)
    base.alpha_composite(glow.filter(ImageFilter.GaussianBlur(22 * SCALE)))

    sharp = Image.new("RGBA", base.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(sharp)
    for i in range(300):
        t0, t1 = i / 300, (i + 1) / 300
        fade = math.sin(math.pi * (t0 + t1) / 2) ** 0.55
        x0, x1 = start + (end - start) * t0, start + (end - start) * t1 + 1
        sd.rectangle(sbox((x0, y - 2, x1, y + 2)), fill=(*CRIMSON, round(25 + 185 * fade)))
    sd.line(spos((start, y, end, y)), fill=(255, 77, 91, 110), width=SCALE)
    base.alpha_composite(sharp)


def cover_square(path: Path, size: int, focal_x: float, focal_y: float,
                 zoom: float) -> Image.Image:
    src = Image.open(path).convert("RGB")
    side = round(min(src.width, src.height) / zoom)
    left = max(0, min(src.width - side, round((src.width - side) * focal_x)))
    top = max(0, min(src.height - side, round((src.height - side) * focal_y)))
    return src.crop((left, top, left + side, top + side)).resize(
        (size, size), Image.Resampling.LANCZOS
    )


def circle_photo(base: Image.Image, center: tuple[int, int], diameter: int) -> None:
    size = diameter * SCALE
    # Zoom keeps the clock-tower block dominant and excludes excess paving/branches.
    photo = cover_square(YASUDA, size, focal_x=0.50, focal_y=0.46, zoom=1.28)
    photo = ImageOps.autocontrast(photo, cutoff=(1, 1))
    photo = ImageEnhance.Brightness(photo).enhance(1.07)
    photo = Image.blend(photo, Image.new("RGB", photo.size, DEEPEST_CRIMSON), 0.08)
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).ellipse((2, 2, size - 3, size - 3), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(0.55 * SCALE))
    x = round((center[0] - diameter / 2) * SCALE)
    y = round((center[1] - diameter / 2) * SCALE)
    base.paste(photo.convert("RGBA"), (x, y), mask)


def draw_ring(draw: ImageDraw.ImageDraw, center: tuple[int, int], diameter: int,
              width: int = 2) -> None:
    cx, cy = center
    r = diameter / 2
    draw.ellipse(sbox((cx - r, cy - r, cx + r, cy + r)),
                 outline=(*CRIMSON, 235), width=width * SCALE)


def draw_torii(draw: ImageDraw.ImageDraw, center: tuple[int, int]) -> None:
    cx, cy = center
    color = (*CRIMSON, 245)
    thin = 5 * SCALE
    # KASAGI: a restrained shallow upward curve, then the shorter shimaki.
    points = [(cx - 79, cy - 49), (cx - 42, cy - 55), (cx, cy - 57),
              (cx + 42, cy - 55), (cx + 79, cy - 49)]
    draw.line([spos(p) for p in points], fill=color, width=thin, joint="curve")
    draw.line(spos((cx - 66, cy - 40, cx + 66, cy - 40)), fill=color, width=4 * SCALE)
    # Slightly splayed pillars and the penetrating nuki crossbeam.
    draw.line(spos((cx - 43, cy - 39, cx - 51, cy + 66)), fill=color, width=6 * SCALE)
    draw.line(spos((cx + 43, cy - 39, cx + 51, cy + 66)), fill=color, width=6 * SCALE)
    draw.line(spos((cx - 65, cy - 3, cx + 65, cy - 3)), fill=color, width=5 * SCALE)
    draw.line(spos((cx - 56, cy + 5, cx + 56, cy + 5)), fill=(*DARK_CRIMSON, 240), width=2 * SCALE)


def add_timeline(base: Image.Image) -> None:
    left, right = (500, 290), (1274, 290)
    diameter = 226
    add_light_ribbon(base, y=290, start=90, end=1684)

    art = Image.new("RGBA", base.size, (0, 0, 0, 0))
    ad = ImageDraw.Draw(art)
    draw_ring(ad, left, diameter)
    draw_torii(ad, left)
    base.alpha_composite(art)
    circle_photo(base, right, diameter)
    outline = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw_ring(ImageDraw.Draw(outline), right, diameter)
    base.alpha_composite(outline)

    d = ImageDraw.Draw(base)
    label = face(MINCHO, 30)
    detail = face(SANS, 16)
    d.text(spos((left[0], 421)), "前回 ／ 根津神社", font=label, fill=CREAM, anchor="ma")
    d.text(spos((left[0], 465)), "2026.5.23-24　国指定重要文化財", font=detail, fill=SILVER, anchor="ma")
    d.text(spos((right[0], 421)), "今回 ／ 東京大学", font=label, fill=CREAM, anchor="ma")
    d.text(spos((right[0], 465)), "2026.10.18　安田講堂 ＋ CÉ LA VI 渋谷",
           font=detail, fill=SILVER, anchor="ma")


def fit_card_title_font(draw: ImageDraw.ImageDraw, titles: tuple[tuple[str, ...], ...],
                        max_width: int) -> ImageFont.FreeTypeFont:
    """Choose one font size that fits every explicitly specified title line."""
    for size in range(30, 23, -1):
        font = face(MINCHO, size)
        if all(
            draw.textlength(line, font=font) <= max_width * SCALE
            for lines in titles
            for line in lines
        ):
            return font
    raise ValueError("Card titles cannot fit at the minimum shared font size")


def add_cards(base: Image.Image) -> None:
    margin, gap = 50, 18
    width = (W - margin * 2 - gap * 3) // 4
    height, top = 570, 184
    cards = (
        ("LIVE", "ライブ席", "¥10,000", "100名",
         ("アコースティックライブ観覧",)),
        ("BOT", "社bot", "¥50,000", "",
         ("社bot を期間限定で利用可",)),
        ("MIO TIME", "みおタイム", "¥150,000", "20席 ／ 20:10〜",
         ("チェキ（1分）／動画OK", "やしろ語録動画", "限定名刺", "ライブ観覧")),
        ("VVIP", "VVIP席", "¥330,000", "10卓 ／ 20:30〜",
         ("ホストコール体験", "シャンパンサービス", "チェキ／写真／動画OK", "限定名刺",
          "ライブ観覧", "別日 ファンミーティング30分")),
    )
    d = ImageDraw.Draw(base)
    kicker = face(SANS, 16)
    title_font = face(MINCHO, 29)
    amount_font = face(SANS, 48)
    meta_font = face(SANS, 17)
    bullet_font = face(SANS, 17)
    for index, (small, title, amount, note, bullets) in enumerate(cards):
        x = margin + index * (width + gap)
        emphasized = index == 3
        d.rounded_rectangle(
            sbox((x, top, x + width, top + height)), radius=15 * SCALE,
            fill=(*DEEPEST_CRIMSON, 255) if emphasized else None,
            outline=(*CRIMSON, 255) if emphasized else (*DARK_CRIMSON, 235),
            width=(5 if emphasized else 2) * SCALE,
        )
        d.text(spos((x + 28, top + 25)), small, font=kicker, fill=CRIMSON, anchor="la")
        d.text(spos((x + 28, top + 62)), title, font=title_font, fill=CREAM, anchor="la")
        d.text(spos((x + 28, top + 116)), amount, font=amount_font, fill=CREAM, anchor="la")
        d.text(spos((x + 28, top + 190)), note, font=meta_font, fill=SILVER, anchor="la")
        d.line(
            spos((x + 28, top + 226, x + width - 28, top + 226)),
            fill=(*DARK_CRIMSON, 220), width=SCALE,
        )
        for line_no, line in enumerate(bullets):
            cy = top + 254 + line_no * 48
            d.ellipse(sbox((x + 29, cy + 8, x + 35, cy + 14)), fill=CRIMSON)
            d.text(spos((x + 48, cy)), line, font=bullet_font, fill=SILVER, anchor="la")


def add_header(base: Image.Image) -> None:
    d = ImageDraw.Draw(base)
    draw_tracked(d, (68, 34), "VALHALLA CHARITY LIVE ／ SUPPORT",
                 face(SANS, 16), CRIMSON, 3)
    d.text(spos((W / 2, 82)), "支援コース", font=face(MINCHO, 47),
           fill=CREAM, anchor="ma")


def add_footer(base: Image.Image) -> None:
    d = ImageDraw.Draw(base)
    text = (
        "2026.10.18 SUN　CÉ LA VI TOKYO（渋谷・17F）　OPEN 19:00 ／ START 19:30 ／ "
        "終演 21:30　※収益は必要経費を除いた全額を寄付します"
    )
    footer_font = face(SANS, 16)
    if d.textlength(text, font=footer_font) > (W - 100) * SCALE:
        footer_font = face(SANS, 14)
    d.text(
        spos((W / 2, 840)),
        text,
        font=footer_font, fill=SILVER, anchor="ma",
    )


def main() -> None:
    canvas = make_background()
    add_header(canvas)
    add_cards(canvas)
    add_footer(canvas)
    canvas = canvas.convert("RGB").resize((W, H), Image.Resampling.LANCZOS)
    canvas.save(OUTPUT, "JPEG", quality=88, optimize=True, progressive=True,
                subsampling="4:2:0", dpi=(72, 72))
    size = os.path.getsize(OUTPUT)
    if size > 2 * 1024 * 1024:
        raise RuntimeError(f"Output exceeds 2 MB: {size} bytes")
    print(f"{OUTPUT} | {canvas.width}x{canvas.height} | {size} bytes")


if __name__ == "__main__":
    main()
