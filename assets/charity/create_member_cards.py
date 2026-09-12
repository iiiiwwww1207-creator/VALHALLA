#!/usr/bin/env python3
"""出演者3人の写真を、16:9 のカードに組む。

元の宣材は 2:3 の縦位置で、そのまま 16:9 に切ると衣装が全部落ちて
顔だけになる。ビジュアル系は衣装と髪が本体なので、それでは意味がない。
そこで切らずに、縦の写真を左に立てて、右に名前を置いた台紙にする。
ページ内の他の図版と画角が揃い、写真は一切損なわれない。

出力: assets/charity/members/<mio|rei|kou>_card.jpg （各 1920x1080）
"""
from pathlib import Path
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
from logo_watermark import stamp

HERE = Path(__file__).resolve().parent
OUT = HERE / "members"

W, H = 1920, 1080
INK = (10, 7, 9)
CREAM = (245, 239, 228)
CRIMSON = (193, 18, 31)
DEEPEST_CRIMSON = (110, 10, 18)

MINCHO = "/System/Library/Fonts/ヒラギノ明朝 ProN.ttc"
MINCHO_W6 = 2
SANS = "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc"
DIDOT = "/System/Library/Fonts/Supplemental/Didot.ttc"

# 併記は MIO だけ（2026-09-11 kazuma 判断）。「社美緒」は経営者としての名前なので
# 併記して矛盾しない。RAY と KØU はホスト表記しか無いので英字のみで通す。
CARDS = (
    ("mio_card.jpg", "mio.jpg", "MIO", "社美緒", "Guitar ／ 主宰",
     "Group Yggdrasill 会長"),
    ("rei_card.jpg", "rei.jpg", "RAY", "", "Guitar", ""),
    ("kou_card.jpg", "kou.jpg", "KØU", "", "Vocal", ""),
)


def face(path: str, size: int, index: int = -1) -> ImageFont.FreeTypeFont:
    if index < 0:
        index = MINCHO_W6 if path == MINCHO else 0
    return ImageFont.truetype(path, size=size, index=index)


def tracked(d: ImageDraw.ImageDraw, xy, text, font, fill, tracking: float) -> None:
    x, y = xy
    for c in text:
        d.text((x, y), c, font=font, fill=fill)
        x += d.textlength(c, font=font) + tracking


def photo_panel(src: Path, box: tuple[int, int]) -> Image.Image:
    """縦の写真を、箱の高さいっぱいに立てる。切るのは左右だけ。"""
    im = Image.open(src).convert("RGB")
    k = box[1] / im.height
    im = im.resize((round(im.width * k), box[1]), Image.Resampling.LANCZOS)
    if im.width > box[0]:                      # はみ出したぶんは左右から均等に
        x = (im.width - box[0]) // 2
        im = im.crop((x, 0, x + box[0], box[1]))
    return im


def build(out_name: str, photo: str, roman: str, kanji: str, part: str,
          note: str) -> None:
    base = Image.new("RGB", (W, H), INK).convert("RGBA")

    # 地：中央から右へ向かう淡いクリムゾンの滲み
    glow = Image.new("L", (W // 8, H // 8), 0)
    ImageDraw.Draw(glow).ellipse((W * 0.30 / 8, -H * 0.25 / 8,
                                  W * 1.25 / 8, H * 1.10 / 8), fill=76)
    glow = glow.resize((W, H), Image.Resampling.BILINEAR).filter(
        ImageFilter.GaussianBlur(150))
    base = Image.composite(Image.new("RGBA", (W, H), DEEPEST_CRIMSON + (255,)),
                           base, glow)
    base = stamp(base, scale=0.62, opacity=20, center=(0.74, 0.52))

    # 写真は左を裁ち落としにする。左に黒い帯を残すと、貼っただけに見える
    # 2:3 の写真を高さいっぱいに立てると幅は 720 前後。切るのは、はみ出した時だけ
    panel = photo_panel(HERE / photo, (840, H)).convert("RGBA")
    pw = panel.width

    # 右端は不透明度を落として地に溶かす。地の色で塗りつぶすと段差が出る
    grad = Image.new("L", (pw, 1), 255)
    gp = grad.load()
    for i in range(200):
        gp[pw - 1 - i, 0] = round(255 * (i / 199) ** 1.3)
    panel.putalpha(grad.resize((pw, H)))
    base.alpha_composite(panel, (0, 0))

    d = ImageDraw.Draw(base)
    x = pw + 190
    d.line((x, 300, x + 96, 300), fill=CRIMSON + (255,), width=3)

    tracked(d, (x, 340), roman, face(DIDOT, 132), CREAM + (255,), 12)
    y = 520
    if kanji:
        d.text((x + 4, y), kanji, font=face(MINCHO, 56), fill=(236, 224, 220, 255))
        y += 96
    d.text((x + 4, y), part, font=face(SANS, 30), fill=(206, 190, 190, 255))
    if note:
        d.text((x + 4, y + 52), note, font=face(SANS, 26), fill=(184, 170, 172, 255))

    eyebrow = face(DIDOT, 22)
    tracked(d, (x, 244), "VALHALLA", eyebrow, (222, 190, 190, 235), 10)

    OUT.mkdir(exist_ok=True)
    dst = OUT / out_name
    base.convert("RGB").save(dst, quality=92, subsampling=0, optimize=True)
    print(f"{dst.name} | {W}x{H} | {dst.stat().st_size} bytes")


def main() -> None:
    for args in CARDS:
        build(*args)


if __name__ == "__main__":
    main()
