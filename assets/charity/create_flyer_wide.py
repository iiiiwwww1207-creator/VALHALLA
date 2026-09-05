#!/usr/bin/env python3
"""Create the 16:9 CAMPFIRE hero image from the existing vertical flyer."""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
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

    # Place the ungraded CÉ LA VI photograph over the full-height group image.
    # Its strongest laser field is kept at the left, then dissolved into the
    # group photograph over a wide, smoothstep-eased 650 px transition.
    venue = Image.open(VENUE).convert("RGB")
    scale = H / venue.height
    venue = venue.resize((round(venue.width * scale), round(venue.height * scale)),
                         Image.Resampling.LANCZOS)
    venue_layer = Image.new("RGB", (W, H), BLACK)
    venue_layer.paste(venue, (0, 0))
    venue_mask = Image.new("L", (W, H), 0)
    venue_mask_px = venue_mask.load()
    fade_start, fade_end = 500, 1150
    for y in range(H):
        for x in range(W):
            t = max(0.0, min(1.0, (x - fade_start) / (fade_end - fade_start)))
            smooth = t * t * (3.0 - 2.0 * t)
            venue_mask_px[x, y] = round(255 * 0.98 * (1.0 - smooth))
    im = Image.composite(venue_layer, im, venue_mask)

    # A near-black scrim protects the type while leaving the venue's laser
    # shapes and red light visible.  The broad horizontal falloff darkens the
    # left 55% of the frame; a second, softly feathered vertical component
    # concentrates that protection behind the complete type block.
    scrim = Image.new("RGB", (W, H), BLACK)
    scrim_mask = Image.new("L", (W, H), 0)
    scrim_px = scrim_mask.load()
    for y in range(H):
        for x in range(W):
            # Stay fully effective beneath the copy, then dissolve smoothly
            # beyond it so no vertical seam is introduced near the photos.
            left_t = max(0.0, min(1.0, (x - 720.0) / 430.0))
            left_fade = 1.0 - left_t * left_t * (3.0 - 2.0 * left_t)

            # Soft entry at the very top and a long exit below the artist names.
            top_t = max(0.0, min(1.0, y / 105.0))
            top_rise = top_t * top_t * (3.0 - 2.0 * top_t)
            bottom_t = max(0.0, min(1.0, (y - 760.0) / 210.0))
            bottom_fall = 1.0 - bottom_t * bottom_t * (3.0 - 2.0 * bottom_t)
            type_band = top_rise * bottom_fall

            alpha = min(0.60, left_fade * (0.29 + 0.30 * type_band))
            scrim_px[x, y] = round(255 * alpha)
    return Image.composite(scrim, im, scrim_mask)


def add_type(base: Image.Image) -> None:
    draw = ImageDraw.Draw(base)
    x = 112

    eyebrow = font(OPTIMA, 25)
    tracked_text(draw, (x, 82), "VALHALLA CHARITY LIVE", eyebrow, SILVER, 7)

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
        (x, 405), "アコースティックライブ ＆ スペシャルタイム",
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
