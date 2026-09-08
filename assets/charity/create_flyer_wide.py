#!/usr/bin/env python3
"""CAMPFIRE用の16:9メインビジュアルを生成する。"""

from math import atan, degrees
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


HERE = Path(__file__).resolve().parent
MEMBERS = HERE / "members_white.jpg"
VENUE = HERE / "venue" / "shibuya_night.jpg"
OUTPUT = HERE / "flyer_wide.jpg"

W, H = 1920, 1080
CREAM = (245, 239, 228)
CRIMSON = (193, 18, 31)
DARK_CRIMSON = (110, 10, 18)
HIRAGINO = "/System/Library/Fonts/ヒラギノ明朝 ProN.ttc"
DIDOT = "/System/Library/Fonts/Supplemental/Didot.ttc"


def font(path: str, size: int, index: int = 0) -> ImageFont.FreeTypeFont:
    """書体を明示し、意図しないゴシック体へのフォールバックを防ぐ。"""
    return ImageFont.truetype(path, size=size, index=index)


def cover(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    """縦横比を保ったまま中央トリミングし、背景に隙間を作らない。"""
    target_w, target_h = size
    scale = max(target_w / image.width, target_h / image.height)
    resized = image.resize(
        (round(image.width * scale), round(image.height * scale)),
        Image.Resampling.LANCZOS,
    )
    left = (resized.width - target_w) // 2
    top = (resized.height - target_h) // 2
    return resized.crop((left, top, left + target_w, top + target_h))


def make_background() -> Image.Image:
    """夜景を暗くし、クリムゾンを重ねて人物と文字を前に出す。"""
    night = cover(Image.open(VENUE).convert("RGB"), (W, H))
    night = Image.blend(night, Image.new("RGB", (W, H), (0, 0, 0)), 0.50)
    return Image.blend(night, Image.new("RGB", (W, H), (142, 16, 25)), 0.25)


def cut_out_members() -> Image.Image:
    """写真端からつながる白背景だけを抜き、白い衣装は残す。"""
    source = Image.open(MEMBERS).convert("RGB")

    # 背景色に近い画素を候補にする。低彩度・高明度だけを使うことで髪や肌を守る。
    pixels = source.load()
    candidate = Image.new("L", source.size, 0)
    candidate_pixels = candidate.load()
    for y in range(source.height):
        for x in range(source.width):
            r, g, b = pixels[x, y]
            if min(r, g, b) >= 205 and max(r, g, b) - min(r, g, b) <= 32:
                candidate_pixels[x, y] = 255

    # 右人物の白い衣装は背景と同じ条件に入るため、人物内部の安全な範囲を候補から除く。
    # 輪郭そのものは色判定に任せ、内側だけを保護するので背景の白い塊は残らない。
    ImageDraw.Draw(candidate).polygon(
        [
            (1168, 510), (1125, 565), (1135, 690), (1172, 850),
            (1188, 1065), (1435, 1065), (1385, 855), (1332, 695), (1325, 565),
        ],
        fill=0,
    )

    # 端に接している候補だけを背景とみなす。これで白いスーツの内部が消えない。
    background = Image.new("L", source.size, 0)
    bg = background.load()
    seen = bytearray(source.width * source.height)
    stack: list[tuple[int, int]] = []
    for x in range(source.width):
        stack.extend(((x, 0), (x, source.height - 1)))
    for y in range(source.height):
        stack.extend(((0, y), (source.width - 1, y)))

    while stack:
        x, y = stack.pop()
        i = y * source.width + x
        if seen[i] or candidate_pixels[x, y] == 0:
            continue
        seen[i] = 1
        bg[x, y] = 255
        if x:
            stack.append((x - 1, y))
        if x + 1 < source.width:
            stack.append((x + 1, y))
        if y:
            stack.append((x, y - 1))
        if y + 1 < source.height:
            stack.append((x, y + 1))

    # マスクを少し広げてぼかし、白い撮影背景の縁を暗い夜景上で目立たなくする。
    background = background.filter(ImageFilter.MaxFilter(5)).filter(
        ImageFilter.GaussianBlur(1.4)
    )
    alpha = Image.eval(background, lambda value: 255 - value)
    rgba = source.convert("RGBA")
    rgba.putalpha(alpha)
    return rgba


def place_members(canvas: Image.Image) -> None:
    """元写真全体を画面高の約70%に収め、引きの構図にする。"""
    people = cut_out_members()
    target_h = round(H * 0.70)
    target_w = round(people.width * target_h / people.height)
    people = people.resize((target_w, target_h), Image.Resampling.LANCZOS)
    x = (W - target_w) // 2
    y = H - 152 - target_h + 30
    canvas.alpha_composite(people, (x, y))


def tracked_width(draw: ImageDraw.ImageDraw, text: str, face, tracking: int) -> float:
    return sum(draw.textlength(char, font=face) for char in text) + tracking * (len(text) - 1)


def draw_tracked_center(
    draw: ImageDraw.ImageDraw,
    text: str,
    face: ImageFont.FreeTypeFont,
    y: int,
    fill: tuple[int, int, int],
    tracking: int,
) -> None:
    """欧文見出しに広い字間を与え、中央揃えで描く。"""
    x = (W - tracked_width(draw, text, face, tracking)) / 2
    for char in text:
        draw.text((x, y), char, font=face, fill=fill)
        x += draw.textlength(char, font=face) + tracking


def draw_arch_text(
    canvas: Image.Image,
    text: str,
    face: ImageFont.FreeTypeFont,
    center_y: float,
    tracking: int,
) -> None:
    """各文字を放物線上に置き、その位置の接線角へ回転して上凸の円弧感を作る。"""
    measure = ImageDraw.Draw(canvas)
    widths = [measure.textlength(char, font=face) for char in text]
    total = sum(widths) + tracking * (len(text) - 1)
    x = (W - total) / 2
    curve = 0.00025

    for char, char_w in zip(text, widths):
        char_x = x + char_w / 2
        offset = char_x - W / 2
        char_y = center_y + curve * offset * offset
        # Pillowの正角は反時計回りなので、画面座標の接線角とは符号を反転する。
        angle = -degrees(atan(2 * curve * offset))

        bbox = face.getbbox(char, stroke_width=2)
        glyph = Image.new("RGBA", (max(1, bbox[2] - bbox[0] + 40), bbox[3] - bbox[1] + 40))
        glyph_draw = ImageDraw.Draw(glyph)
        glyph_draw.text(
            (20 - bbox[0], 20 - bbox[1]),
            char,
            font=face,
            fill=CREAM + (255,),
            stroke_width=2,
            stroke_fill=(70, 8, 13, 150),
        )
        glyph = glyph.rotate(angle, resample=Image.Resampling.BICUBIC, expand=True)
        canvas.alpha_composite(glyph, (round(char_x - glyph.width / 2), round(char_y - glyph.height / 2)))
        x += char_w + tracking


def add_type(canvas: Image.Image) -> None:
    """縮小表示でも主見出しが残るサイズとコントラストで文字を配置する。"""
    draw = ImageDraw.Draw(canvas)
    draw_tracked_center(draw, "VALHALLA CHARITY LIVE", font(DIDOT, 34), 54, CRIMSON, 14)
    draw_arch_text(canvas, "文化 × エンタメ × AI", font(HIRAGINO, 132, index=2), 176, 9)

    # 下帯は情報の背景を完全に落とし、一覧サムネイルでも日付を読ませる。
    band_top = H - 152
    draw.rectangle((0, band_top, W, H), fill=DARK_CRIMSON + (255,))

    date_face = font(DIDOT, 53)
    place_face = font(HIRAGINO, 37, index=2)
    date_text, place_text = "2026 . 10 . 18 SUN", "渋谷"
    date_tracking, gap = 4, 38
    date_w = tracked_width(draw, date_text, date_face, date_tracking)
    place_w = draw.textlength(place_text, font=place_face)
    x = (W - date_w - gap - place_w) / 2
    for char in date_text:
        draw.text((x, band_top + 15), char, font=date_face, fill=CREAM)
        x += draw.textlength(char, font=date_face) + date_tracking
    draw.text((x + gap, band_top + 25), place_text, font=place_face, fill=CREAM)

    donation = "収益から必要経費を差し引いた全額を、然るべき団体へ寄付します"
    donation_face = font(HIRAGINO, 27, index=2)
    donation_w = draw.textlength(donation, font=donation_face)
    draw.text(((W - donation_w) / 2, band_top + 98), donation, font=donation_face, fill=CREAM)


def main() -> None:
    canvas = make_background().convert("RGBA")
    place_members(canvas)
    add_type(canvas)
    canvas.convert("RGB").save(
        OUTPUT,
        "JPEG",
        quality=92,
        optimize=True,
        progressive=True,
        subsampling="4:2:0",
    )
    with Image.open(OUTPUT) as result:
        if result.size != (W, H) or result.format != "JPEG":
            raise RuntimeError("出力画像の形式または寸法が不正です")
    print(f"{OUTPUT} | {W}x{H} | JPEG quality=92")


if __name__ == "__main__":
    main()
