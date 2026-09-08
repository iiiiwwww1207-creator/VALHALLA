#!/usr/bin/env python3
"""CAMPFIRE のメインビジュアル（1920x1080）を組む。

主役は「VALHALLA CHARITY LIVE」の文字。その下に補足として
「文化 × エンタメ × AI」を置き、どちらも3人の頭の上にアーチ状に並べる。

■ 白背景を抜かずに渋谷を透けさせている理由
メンバー写真は白ホリゾント撮影で、白衣装の人の明度（中央値251）が
背景（242）より高い。つまり背景を消すしきい値は必ず衣装も消すので、
自動での切り抜きは原理的にできない。
そこで写真は矩形のまま使い、**縁に向かってアルファを落として**
渋谷の夜景に溶かしている。人物のまわりだけ白が残るが、
スポットライトのように見えるので不自然にならない。
"""
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = Path(__file__).resolve().parent
MEMBERS = HERE / "members_white.jpg"
VENUE = HERE / "venue" / "shibuya_night.jpg"
OUTPUT = HERE / "flyer_wide.jpg"

W, H = 1920, 1080
BLACK = (5, 3, 7)
CRIMSON = (193, 18, 31)
DARK_CRIMSON = (142, 16, 25)
DEEPEST_CRIMSON = (110, 10, 18)
CREAM = (245, 239, 228)

MINCHO = "/System/Library/Fonts/ヒラギノ明朝 ProN.ttc"
MINCHO_W6 = 2
DIDOT = "/System/Library/Fonts/Supplemental/Didot.ttc"


def face(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size=size,
                              index=MINCHO_W6 if path == MINCHO else 0)


def background() -> Image.Image:
    """渋谷の夜景。彩度と明度を落とし、クリムゾンで画面を支配させる。"""
    venue = Image.open(VENUE).convert("RGB")
    scale = max(W / venue.width, H / venue.height)
    venue = venue.resize((round(venue.width * scale), round(venue.height * scale)),
                         Image.Resampling.LANCZOS)
    im = venue.crop((0, 0, W, H))
    im = Image.blend(im, im.convert("L").convert("RGB"), 0.45)
    im = Image.blend(im, Image.new("RGB", im.size, BLACK), 0.50)
    im = Image.blend(im, Image.new("RGB", im.size, DARK_CRIMSON), 0.34)
    return im


def members_panel() -> Image.Image:
    """メンバー写真を、縁に向かって透明にした板として返す。"""
    src = Image.open(MEMBERS).convert("RGB")
    ph = 830
    pw = round(src.width * ph / src.height)
    panel = src.resize((pw, ph), Image.Resampling.LANCZOS).convert("RGBA")

    # 縁のフェード幅。左右は広く取り、渋谷へ溶け込ませる。
    fx, fy = 300, 190
    mask = Image.new("L", (pw, ph), 255)
    px = mask.load()
    for x in range(pw):
        ax = min(1.0, x / fx, (pw - 1 - x) / fx)
        ax = ax * ax * (3 - 2 * ax)                    # なめらかに
        for y in range(ph):
            ay = min(1.0, y / fy, (ph - 1 - y) / (fy * 1.6))
            ay = ay * ay * (3 - 2 * ay)
            px[x, y] = round(255 * min(ax, ay))
    # 白ホリゾントの白がそのままだと画面に白い塊ができるので、
    # 背景と同じ暗いクリムゾン側へ寄せて、光が当たっているくらいに落とす。
    tinted = Image.blend(panel.convert("RGB"),
                         Image.new("RGB", panel.size, DARK_CRIMSON), 0.30)
    tinted = Image.blend(tinted, Image.new("RGB", panel.size, BLACK), 0.16)
    panel = tinted.convert("RGBA")
    panel.putalpha(mask.filter(ImageFilter.GaussianBlur(12)))
    return panel


def arc_text(base: Image.Image, text: str, font: ImageFont.FreeTypeFont,
             fill, cx: int, cy: int, radius: float, tracking: float = 0.0) -> None:
    """円弧に沿って1文字ずつ回転させて描く（上に凸のアーチ）。

    中心を画面の下方に置き、文字を円周上に並べる。各文字は自分がいる
    角度と同じだけ回転させるので、文字の足元が常に中心を向く。
    """
    d = ImageDraw.Draw(base)
    widths = [d.textlength(c, font=font) + tracking for c in text]
    total = sum(widths)
    # 弧の長さ = 半径 × 角度。文字送りを角度に換算する。
    angle = -total / radius / 2                        # 左端から始める
    for ch, w in zip(text, widths):
        angle += (w / radius) / 2
        glyph = Image.new("RGBA", (round(w) + 60, font.size + 70), (0, 0, 0, 0))
        ImageDraw.Draw(glyph).text((30, 20), ch, font=font, fill=fill)
        deg = math.degrees(angle)
        rot = glyph.rotate(-deg, resample=Image.Resampling.BICUBIC, expand=True)
        x = cx + radius * math.sin(angle)
        y = cy - radius * math.cos(angle)
        base.alpha_composite(rot, (round(x - rot.width / 2), round(y - rot.height / 2)))
        angle += (w / radius) / 2


def add_type(base: Image.Image) -> None:
    d = ImageDraw.Draw(base)

    # 主役：イベント名。頭の上に大きなアーチで置く。
    arc_text(base, "VALHALLA CHARITY LIVE", face(DIDOT, 104), CREAM + (255,),
             W // 2, 3050, 2830, tracking=10)

    # 補足：3語のスローガン。主役より一回り小さく、内側のアーチに。
    arc_text(base, "文化 × エンタメ × AI", face(MINCHO, 52), CREAM + (255,),
             W // 2, 3050, 2690, tracking=14)

    # 最下部：日付と寄付の一行を帯にして必ず読ませる。
    band = H - 148
    d.rectangle((0, band, W, H), fill=DEEPEST_CRIMSON + (255,))
    date_f, place_f = face(DIDOT, 54), face(MINCHO, 34)
    date_t, place_t = "2026 . 10 . 18 SUN", "渋谷"
    dw = sum(d.textlength(c, font=date_f) for c in date_t) + 4 * (len(date_t) - 1)
    pw = d.textlength(place_t, font=place_f)
    x = (W - (dw + 40 + pw)) / 2
    for c in date_t:
        d.text((x, band + 20), c, font=date_f, fill=CREAM + (255,))
        x += d.textlength(c, font=date_f) + 4
    d.text((x + 36, band + 32), place_t, font=place_f, fill=CREAM + (255,))
    note = "収益から必要経費を差し引いた全額を、然るべき団体へ寄付します"
    nf = face(MINCHO, 29)
    d.text(((W - d.textlength(note, font=nf)) / 2, band + 96), note, font=nf,
           fill=CREAM + (255,))


def main() -> None:
    canvas = background().convert("RGBA")
    panel = members_panel()
    canvas.alpha_composite(panel, ((W - panel.width) // 2, 232))
    add_type(canvas)
    out = canvas.convert("RGB")
    out.save(OUTPUT, quality=92, subsampling=0, optimize=True)
    print(f"{OUTPUT} | {out.width}x{out.height} | {OUTPUT.stat().st_size} bytes")


if __name__ == "__main__":
    main()
