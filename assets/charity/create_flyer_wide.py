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
    src = Image.open(SOURCE).convert("RGB")
    # Include all three figures, from hair to shoes, at their natural aspect
    # ratio. The faithful portrait occupies the right side. Its untouched edge
    # colours are extended beneath the opaque scrim to cover the canvas without
    # introducing another image boundary or changing the photograph's colour.
    crop = src.crop((0, 780, src.width, src.height))
    portrait_w = round(crop.width * H / crop.height)
    portrait = crop.resize((portrait_w, H), Image.Resampling.LANCZOS)
    photo_x = W - portrait_w - 42
    im = portrait.crop((0, 0, 1, H)).resize((W, H))
    im.paste(portrait, (photo_x, 0))
    right_fill = portrait.crop((portrait_w - 1, 0, portrait_w, H)).resize((42, H))
    im.paste(right_fill, (W - 42, 0))

    # CÉ LA VI texture is deliberately faint and confined to the dark left.
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
            fade = max(0.0, min(1.0, (0.56 - nx) / 0.18))
            fade = fade * fade * (3.0 - 2.0 * fade)
            strength = 0.14 * fade
            tm[x, y] = round(255 * strength)
    im = Image.composite(screened, im, texture_mask)

    # One continuous crimson scrim: nearly opaque at the left edge, easing
    # over well over half the canvas and becoming fully transparent before
    # the faces. A subtle lower-edge darkening anchors the information block.
    overlay = Image.new("RGB", (W, H), BLACK)
    overlay_px = overlay.load()
    mask = Image.new("L", (W, H), 0)
    mask_px = mask.load()
    for y in range(H):
        ny = y / (H - 1)
        for x in range(W):
            nx = x / (W - 1)
            progress = max(0.0, min(1.0, nx / 0.70))
            eased = progress * progress * (3.0 - 2.0 * progress)
            alpha = 0.97 * (1.0 - eased)
            lower = max(0.0, (ny - 0.72) / 0.28) ** 2
            alpha = min(0.98, alpha + 0.10 * lower * (1.0 - progress))
            crimson_mix = 0.28 + 0.28 * ny
            overlay_px[x, y] = tuple(round(BLACK[i] * (1 - crimson_mix)
                                                   + DEEPEST_CRIMSON[i] * crimson_mix)
                                      for i in range(3))
            mask_px[x, y] = round(255 * alpha)
    return Image.composite(overlay, im, mask)


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
