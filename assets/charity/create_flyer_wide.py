#!/usr/bin/env python3
"""Create the 16:9 CAMPFIRE hero image from the existing vertical flyer."""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageChops
import os


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "group_field.jpg"
VENUE = HERE / "venue" / "celavi_red_hero.jpg"
OUTPUT = HERE / "flyer_wide.jpg"

W, H = 1920, 1080
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
    # Near-black field with deep crimson rising softly from the lower edge.
    im = Image.new("RGB", (W, H), BLACK)
    px = im.load()
    for y in range(H):
        t = y / (H - 1)
        for x in range(W):
            nx = x / (W - 1)
            # A broad, subdued bloom: #6E0A12 at the foot, tending toward
            # #8E1019 as it diffuses upward before disappearing into #050307.
            lower = max(0.0, (t - 0.22) / 0.78) ** 1.5
            upper_tint = max(0.0, 1.0 - abs(t - 0.64) / 0.48) ** 2
            red = tuple(
                round(DEEPEST_CRIMSON[i] * (1 - 0.34 * upper_tint)
                      + DARK_CRIMSON[i] * 0.34 * upper_tint)
                for i in range(3)
            )
            # Slightly favor the right/photo side and preserve a very dark text field.
            spatial = (0.68 + 0.32 * max(0.0, (nx - 0.10) / 0.90))
            amount = min(0.82, lower * spatial)
            edge = max(0.0, abs(nx - 0.5) - 0.38) / 0.12
            vignette = 1.0 - 0.12 * min(1.0, edge) ** 2
            px[x, y] = tuple(round((BLACK[i] * (1 - amount) + red[i] * amount) * vignette)
                             for i in range(3))

    # CÉ LA VI laser texture, screen-like and deliberately faint. The left 55%
    # is attenuated again so typography remains the highest-contrast element.
    venue = Image.open(VENUE).convert("RGB")
    scale = max(W / venue.width, H / venue.height)
    venue = venue.resize((round(venue.width * scale), round(venue.height * scale)),
                         Image.Resampling.LANCZOS)
    left = (venue.width - W) // 2
    top = (venue.height - H) // 2
    venue = venue.crop((left, top, left + W, top + H))
    venue = ImageEnhance.Color(venue).enhance(0.72)
    venue = ImageEnhance.Contrast(venue).enhance(1.08)
    screened = ImageChops.screen(im, venue)
    texture_mask = Image.new("L", (W, H), 0)
    tm = texture_mask.load()
    for y in range(H):
        for x in range(W):
            nx = x / (W - 1)
            # 17% on the text side, rising smoothly to 23% on the portrait side.
            strength = 0.17 + 0.06 * max(0.0, min(1.0, (nx - 0.55) / 0.20))
            tm[x, y] = round(255 * strength)
    im = Image.composite(screened, im, texture_mask)

    # A final dark veil over the left 55% keeps venue highlights behind the copy.
    veil = Image.new("RGB", (W, H), BLACK)
    veil_mask = Image.new("L", (W, H), 0)
    vm = veil_mask.load()
    for x in range(round(W * 0.62)):
        fade = max(0.0, min(1.0, (0.62 - x / W) / 0.12))
        for y in range(H):
            vm[x, y] = round(255 * 0.14 * fade)
    return Image.composite(veil, im, veil_mask)


def add_people(base: Image.Image) -> None:
    src = Image.open(SOURCE).convert("RGB")
    # Keep the full width so the left shoe and the right member both retain
    # breathing room.  Most of the sky/scoreboard is removed while the crop
    # still includes all three figures from hair to feet.
    portrait = src.crop((0, 916, 2443, 3664))
    target_w, target_h = 1040, 1170
    portrait = portrait.resize((target_w, target_h), Image.Resampling.LANCZOS)

    # Preserve the source photograph exactly as-is apart from resizing. Only
    # its left edge dissolves into the text-side background.
    mask = Image.new("L", portrait.size, 255)
    m = mask.load()
    fade_width = round(portrait.width * 0.12)
    for x in range(fade_width):
        alpha = round(255 * x / max(1, fade_width - 1))
        for y in range(portrait.height):
            m[x, y] = alpha

    photo_pos = (840, -20)
    layer = Image.new("RGB", (W, H), (0, 0, 0))
    alpha = Image.new("L", (W, H), 0)
    pos = photo_pos
    layer.paste(portrait, pos)
    alpha.paste(mask, pos)
    base.paste(layer, (0, 0), alpha)


def add_type(base: Image.Image) -> None:
    draw = ImageDraw.Draw(base)
    x = 112

    eyebrow = font(OPTIMA, 25)
    tracked_text(draw, (x, 82), "VALHALLA CHARITY LIVE", eyebrow, CRIMSON, 7)

    valhalla = font(DIDOT, 126)
    tracked_text(draw, (x - 2, 128), "VALHALLA", valhalla, CREAM, 7)

    # The official flyer catch copy is the primary reading moment: a solid
    # dark-crimson band and the heaviest available Hiragino Sans face.
    catch = font(HIRAGINO_BOLD, 56)
    catch_text = "ビジュアル系文化を守り、継ぐ。"
    bbox = draw.textbbox((0, 0), catch_text, font=catch)
    catch_y = 288
    padding_x, padding_y = 22, 14
    band = (x - padding_x, catch_y - padding_y,
            x + (bbox[2] - bbox[0]) + padding_x,
            catch_y + (bbox[3] - bbox[1]) + padding_y)
    draw.rectangle(band, fill=DARK_CRIMSON)
    draw.text((x, catch_y), catch_text, font=catch, fill=(255, 255, 255))

    detail = font(HIRAGINO_BOLD, 25)
    draw.text(
        (x, 405), "アコースティックライブ ＆ ホストコール体験",
        font=detail, fill=SILVER,
    )

    draw.line((x, 472, 844, 472), fill=CRIMSON, width=2)

    date = font(DIDOT, 58)
    tracked_text(draw, (x, 514), "2026 . 10 . 18 SUN", date, CREAM, 3)

    info = font(HIRAGINO_BOLD, 24)
    draw.text((x, 620), "OPEN 19:00 ／ START 19:30", font=info, fill=SILVER)
    draw.text((x, 670), "CÉ LA VI TOKYO（渋谷・17F）", font=info, fill=SILVER)

    names = font(OPTIMA, 34)
    tracked_text(draw, (x + 1, 742), "MIO / RAY / KØU", names, SILVER, 4)


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
