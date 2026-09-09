#!/usr/bin/env python3
"""CAMPFIRE「イベント概要」用の会場告知バナーを生成する。"""

from __future__ import annotations

import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "venue" / "shibuya_night.jpg"
OUTPUT = HERE / "venue_banner.jpg"

W, H = 1774, 887
SCALE = 2
SW, SH = W * SCALE, H * SCALE

BLACK = (0, 0, 0)
CRIMSON = (193, 18, 31)
CREAM = (245, 239, 228)
SILVER = (198, 198, 205)

# 指定外の書体へフォールバックすると制作環境ごとに印象が変わるため、
# パスとコレクション内のウェイトを固定する。
MINCHO_PATH = Path("/System/Library/Fonts/ヒラギノ明朝 ProN.ttc")
DIDOT_PATH = Path("/System/Library/Fonts/Supplemental/Didot.ttc")
MINCHO_W6_INDEX = 2
DIDOT_REGULAR_INDEX = 0


def face(path: Path, size: int, index: int) -> ImageFont.FreeTypeFont:
    """縮小後に指定サイズになるよう、2倍解像度のフォントを返す。"""
    return ImageFont.truetype(str(path), size=size * SCALE, index=index)


def scaled_xy(x: float, y: float) -> tuple[int, int]:
    return round(x * SCALE), round(y * SCALE)


def scaled_box(
    left: float, top: float, right: float, bottom: float
) -> tuple[int, int, int, int]:
    return tuple(round(value * SCALE) for value in (left, top, right, bottom))


def crop_nightscape() -> Image.Image:
    """交差点と街の灯りが同時に残る位置から、完成比率で切り出す。"""
    source = Image.open(SOURCE).convert("RGB")
    target_ratio = W / H
    source_ratio = source.width / source.height

    if source_ratio < target_ratio:
        crop_width = source.width
        crop_height = round(crop_width / target_ratio)
        left = 0

        # 写真上部の看板と下部のスクランブル交差点を両方見せつつ、
        # 主見出しの背後に交差点中央の比較的暗い領域が来るよう調整する。
        preferred_top = 420
        top = max(0, min(preferred_top, source.height - crop_height))
    else:
        crop_height = source.height
        crop_width = round(crop_height * target_ratio)
        left = (source.width - crop_width) // 2
        top = 0

    cropped = source.crop((left, top, left + crop_width, top + crop_height))
    return cropped.resize((SW, SH), Image.Resampling.LANCZOS)


def darken_for_type(photo: Image.Image) -> Image.Image:
    """彩度を操作せず、黒とのブレンドだけで文字の可読性をつくる。"""
    darkness = Image.new("RGB", photo.size, BLACK)
    return Image.blend(photo, darkness, 0.36)


def add_corner_vignette(photo: Image.Image) -> Image.Image:
    """中央は保ったまま四隅だけを穏やかに沈め、視線を中央へ集める。"""
    keep_center = Image.new("L", photo.size, 0)
    draw = ImageDraw.Draw(keep_center)
    draw.ellipse(
        scaled_box(-150, -210, W + 150, H + 210),
        fill=255,
    )
    keep_center = keep_center.filter(ImageFilter.GaussianBlur(120 * SCALE))

    # ビネット側も真っ黒にはせず、元写真を43%だけ黒へ寄せる。
    dark_edges = Image.blend(photo, Image.new("RGB", photo.size, BLACK), 0.43)
    return Image.composite(photo, dark_edges, keep_center)


def tracked_width(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.FreeTypeFont,
    tracking: int,
) -> float:
    glyphs = sum(draw.textlength(char, font=font) for char in text)
    return glyphs + max(0, len(text) - 1) * tracking * SCALE


def draw_tracked_centered(
    draw: ImageDraw.ImageDraw,
    center_x: int,
    y: int,
    text: str,
    font: ImageFont.FreeTypeFont,
    fill: tuple[int, int, int, int],
    tracking: int,
) -> None:
    """Didot の字間を手動で広げ、全体を光学的に中央へ置く。"""
    x = center_x * SCALE - tracked_width(draw, text, font, tracking) / 2
    for char in text:
        draw.text((round(x), y * SCALE), char, font=font, fill=fill, anchor="la")
        x += draw.textlength(char, font=font) + tracking * SCALE


def add_typography(canvas: Image.Image) -> None:
    """会場未公開の状態を、余白と細い罫線で端正に告知する。"""
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    center_x = W // 2

    venue_font = face(DIDOT_PATH, 25, DIDOT_REGULAR_INDEX)
    title_font = face(MINCHO_PATH, 116, MINCHO_W6_INDEX)
    detail_font = face(MINCHO_PATH, 29, MINCHO_W6_INDEX)

    draw_tracked_centered(
        draw,
        center_x,
        270,
        "VENUE",
        venue_font,
        (*SILVER, 255),
        tracking=13,
    )

    # 明るい看板の上でも明朝の細部が失われないよう、ごく薄い影だけを添える。
    draw.text(
        scaled_xy(center_x + 2, 429 + 3),
        "近日公開予定",
        font=title_font,
        fill=(0, 0, 0, 175),
        anchor="mm",
    )
    draw.text(
        scaled_xy(center_x, 429),
        "近日公開予定",
        font=title_font,
        fill=(*CREAM, 255),
        anchor="mm",
    )

    # 見出しの左右に同じ長さの罫線を置き、情報のまとまりを画面中央に固定する。
    line_y = 431
    for start, end in ((150, 480), (1294, 1624)):
        draw.line(
            (*scaled_xy(start, line_y), *scaled_xy(end, line_y)),
            fill=(*CRIMSON, 225),
            width=2 * SCALE,
        )
    for x in (480, 1294):
        draw.ellipse(
            scaled_box(x - 3, line_y - 3, x + 3, line_y + 3),
            fill=(*CRIMSON, 255),
        )

    detail = "会場は東京・渋谷。詳細は追ってお知らせします。"
    draw.text(
        scaled_xy(center_x + 1, 575 + 2),
        detail,
        font=detail_font,
        fill=(0, 0, 0, 150),
        anchor="mm",
    )
    draw.text(
        scaled_xy(center_x, 575),
        detail,
        font=detail_font,
        fill=(*SILVER, 255),
        anchor="mm",
    )

    canvas.alpha_composite(layer)


def validate_inputs() -> None:
    for path in (SOURCE, MINCHO_PATH, DIDOT_PATH):
        if not path.exists():
            raise FileNotFoundError(f"必要な素材が見つかりません: {path}")


def main() -> None:
    validate_inputs()
    canvas = add_corner_vignette(darken_for_type(crop_nightscape())).convert("RGBA")
    add_typography(canvas)

    # 2倍で組んだ文字と罫線を縮小し、JPEGでも輪郭が荒れないようにする。
    finished = canvas.convert("RGB").resize((W, H), Image.Resampling.LANCZOS)
    finished.save(
        OUTPUT,
        "JPEG",
        quality=92,
        optimize=True,
        progressive=True,
        subsampling="4:2:0",
        dpi=(72, 72),
    )

    # 実行時にも納品条件を検査し、壊れた画像を黙って残さない。
    with Image.open(OUTPUT) as check:
        if check.size != (W, H) or check.format != "JPEG":
            raise RuntimeError(
                f"出力条件が不正です: format={check.format}, size={check.size}"
            )
        check.verify()

    size = os.path.getsize(OUTPUT)
    print(f"{OUTPUT} | {W}x{H} | JPEG | {size} bytes")


if __name__ == "__main__":
    main()
