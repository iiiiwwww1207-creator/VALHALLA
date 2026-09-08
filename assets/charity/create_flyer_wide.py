#!/usr/bin/env python3
"""Create the 16:9 CAMPFIRE hero image from the existing vertical flyer."""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import os


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "group_field.jpg"
VENUE = HERE / "venue" / "shibuya_night.jpg"
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

    # Lay the Shibuya night photograph — the same one the official flyer uses —
    # under the left of the group image, dimmed so it reads as a background
    # rather than a subject, then dissolved into the group photograph over a
    # wide, smoothstep-eased 650 px transition.
    venue = Image.open(VENUE).convert("RGB")
    venue = Image.blend(venue, Image.new("RGB", venue.size, BLACK), 0.34)
    scale = H / venue.height
    venue = venue.resize((round(venue.width * scale), round(venue.height * scale)),
                         Image.Resampling.LANCZOS)
    venue_layer = Image.new("RGB", (W, H), BLACK)
    venue_layer.paste(venue, (0, 0))
    venue_mask = Image.new("L", (W, H), 0)
    venue_mask_px = venue_mask.load()
    fade_start, fade_end = 430, 1060
    for y in range(H):
        for x in range(W):
            t = max(0.0, min(1.0, (x - fade_start) / (fade_end - fade_start)))
            smooth = t * t * (3.0 - 2.0 * t)
            venue_mask_px[x, y] = round(255 * 1.0 * (1.0 - smooth))
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
    im = Image.composite(scrim, im, scrim_mask)

    # 左右で色が割れていたのが一覧での弱点だったので、
    # 最後に全体へクリムゾンを薄く被せて、写真2枚のトーンを1つにまとめる。
    im = Image.blend(im, Image.new("RGB", im.size, DARK_CRIMSON), 0.22)

    # 最下段は寄付の一行を置く帯なので、落としておく。
    foot = Image.new("RGB", im.size, BLACK)
    fmask = Image.new("L", im.size)
    fpx = fmask.load()
    for y in range(H):
        t = max(0.0, (y - H * 0.86) / (H * 0.14))
        v = round(255 * min(1.0, t) * 0.9)
        for x in range(W):
            fpx[x, y] = v
    return Image.composite(foot, im, fmask)


def add_type(base: Image.Image) -> None:
    """一覧で縮んだときに読めるものだけを、左半分に大きく置く。

    OPEN/START・会場注記・メンバー名は横 300px では潰れて読めないので載せない。
    それらはページ本文にある。ここに残すのは
    「誰が」「何を掲げて」「いつ・どこで」と、寄付の一行だけ。
    """
    draw = ImageDraw.Draw(base)
    x = 104

    eyebrow = font(OPTIMA, 27)
    tracked_text(draw, (x, 96), "VALHALLA CHARITY LIVE", eyebrow, SILVER, 8)

    valhalla = font(DIDOT, 104)
    tracked_text(draw, (x - 2, 138), "VALHALLA", valhalla, CREAM, 6)

    # 主役：キャッチコピー。画面でいちばん大きい要素にする。
    catch_text = "文化 × エンタメ × AI"
    catch = font(HIRAGINO_BOLD, 74)
    bbox = draw.textbbox((0, 0), catch_text, font=catch)
    cw, ch = bbox[2] - bbox[0], bbox[3] - bbox[1]
    cy = 296
    pad_x, pad_y = 26, 18
    draw.rectangle((x - pad_x, cy - pad_y, x + cw + pad_x, cy + ch + pad_y),
                   fill=DARK_CRIMSON)
    draw.text((x - bbox[0], cy - bbox[1]), catch_text, font=catch, fill=(255, 255, 255))

    # 目的の一行。3語だけでは何をするのか伝わらないので必ず添える。
    lead = font(HIRAGINO_BOLD, 38)
    draw.text((x, 452), "その一夜の収益を、次の世代へ。", font=lead, fill=CREAM)

    draw.line((x, 546, x + 640, 546), fill=CRIMSON, width=3)

    date = font(DIDOT, 76)
    tracked_text(draw, (x, 590), "2026 . 10 . 18 SUN", date, CREAM, 4)

    place = font(HIRAGINO_BOLD, 34)
    draw.text((x, 712), "渋谷", font=place, fill=SILVER)

    # 最下段：寄付の一行を帯にして必ず読ませる。
    note = font(HIRAGINO_BOLD, 30)
    note_text = "収益から必要経費を差し引いた全額を、然るべき団体へ寄付します"
    nw = draw.textlength(note_text, font=note)
    draw.rectangle((0, H - 92, W, H), fill=DEEPEST_CRIMSON)
    draw.text(((W - nw) / 2, H - 74), note_text, font=note, fill=CREAM)


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
