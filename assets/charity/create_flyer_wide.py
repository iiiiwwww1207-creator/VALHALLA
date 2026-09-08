#!/usr/bin/env python3
"""Create the 16:9 CAMPFIRE hero image from the existing vertical flyer."""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import os


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "members_white.jpg"   # フライヤーと同じ3人写真（横位置）
VENUE = HERE / "venue" / "shibuya_night.jpg"
OUTPUT = HERE / "flyer_wide.jpg"

W, H = 1920, 1080
BLACK = (5, 3, 7)
CRIMSON = (193, 18, 31)
DARK_CRIMSON = (142, 16, 25)
DEEPEST_CRIMSON = (110, 10, 18)
CREAM = (245, 239, 228)
SILVER = (198, 198, 205)
INK = (23, 18, 24)
PAPER = (247, 245, 246)


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
MINCHO = "/System/Library/Fonts/ヒラギノ明朝 ProN.ttc"
MINCHO_W6 = 2  # ProN W6
HIRAGINO_BOLD = MINCHO  # 既存の呼び出しをそのまま明朝に向ける


def font(path: str, size: int, index: int = 0) -> ImageFont.FreeTypeFont:
    # 明朝は W6（index=2）を使う
    if path == MINCHO and index == 0:
        index = MINCHO_W6
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
    """フライヤーと同じ3人写真（横位置・白背景）を全面に敷く。

    3人が横に並んで立っていて、頭の上に白い余白があるので、
    中央にコピーを置いても顔と重ならない。白基調のまま使うことで、
    暗い画像が並ぶ CAMPFIRE の一覧の中でむしろ目立つ。
    """
    src = Image.open(SOURCE).convert("RGB")
    band = round(src.width * H / W)            # 16:9 に必要な高さ
    photo = src.crop((0, 0, src.width, min(src.height, band)))
    im = photo.resize((W, H), Image.Resampling.LANCZOS)

    # 白を少しだけ締めて、紙色に寄せる
    # 地色をわずかにクリムゾン側へ振る。純白のままだと「色」が無く、
    # 一覧に並んだときブランドの印象が残らない。淡く染めることで画面が
    # 1色に支配され、下のクリムゾン帯とも地続きになる。
    im = Image.blend(im, Image.new("RGB", im.size, (250, 243, 243)), 0.45)
    im = Image.blend(im, Image.new("RGB", im.size, CRIMSON), 0.06)
    return im


def center(draw, text, face, y, fill, tracking=0):
    if tracking:
        w = tracked_width(draw, text, face, tracking)
        tracked_text(draw, ((W - w) // 2, y), text, face, fill, tracking)
    else:
        w = draw.textlength(text, font=face)
        draw.text(((W - w) / 2, y), text, font=face, fill=fill)


def add_type(base: Image.Image) -> None:
    """白い余白に、一覧で縮んでも読めるものだけを中央に置く。

    OPEN/START・会場注記・メンバー名は横 300px では潰れるので載せない。
    残すのは「何を掲げて」「いつ・どこで」と、寄付の一行だけ。
    """
    draw = ImageDraw.Draw(base)
    cx = W // 2

    center(draw, "VALHALLA CHARITY LIVE", font(OPTIMA, 30), 88, CRIMSON, tracking=14)

    # 主役：キャッチコピー。頭の上の白い余白に、画面で最大の要素として置く。
    catch_text = "文化 × エンタメ × AI"
    catch = font(HIRAGINO_BOLD, 132)
    bbox = draw.textbbox((0, 0), catch_text, font=catch)
    cw = bbox[2] - bbox[0]
    draw.text((cx - cw // 2 - bbox[0], 148 - bbox[1]), catch_text, font=catch, fill=INK)

    # 目的の一行。3語だけでは何をするのか伝わらないので必ず添える。
    center(draw, "その一夜の収益を、次の世代へ。", font(HIRAGINO_BOLD, 44), 300, INK)

    # 下：クリムゾンの帯に日付と寄付の一行をまとめて、必ず読ませる。
    band_top = H - 150
    draw.rectangle((0, band_top, W, H), fill=DARK_CRIMSON)
    # Didot に日本語が無いので、日付と「渋谷」は別の書体で並べて中央に置く
    date_face, place_face = font(DIDOT, 54), font(HIRAGINO_BOLD, 34)
    date_text, place_text = "2026 . 10 . 18 SUN", "渋谷"
    gap = 34
    dw = tracked_width(draw, date_text, date_face, 4)
    pw = draw.textlength(place_text, font=place_face)
    x = (W - (dw + gap + pw)) / 2
    tracked_text(draw, (x, band_top + 22), date_text, date_face, CREAM, 4)
    draw.text((x + dw + gap, band_top + 36), place_text, font=place_face, fill=CREAM)
    center(draw, "収益から必要経費を差し引いた全額を、然るべき団体へ寄付します",
           font(HIRAGINO_BOLD, 28), band_top + 100, CREAM)


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
