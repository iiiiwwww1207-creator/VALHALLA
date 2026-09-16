#!/usr/bin/env python3
"""出演者3人の写真を、16:9 のカードに組む。

元の宣材は 2:3 の縦位置で、そのまま 16:9 に切ると衣装が全部落ちて
顔だけになる。ビジュアル系は衣装と髪が本体なので、それでは意味がない。
そこで切らずに、縦の写真を左に立てて、右に名前を置いた台紙にする。
ページ内の他の図版と画角が揃い、写真は一切損なわれない。

2026-09-16 差し替え：私服のスナップをやめ、3人とも「黒地に切り抜き」で揃えた。
MIO は単体の黒スーツ写真（先方支給）、RAY と KØU は宣材から1人ずつ抜いている。
MIO のカードにだけ MIO YASHIRO のロゴを添える。

出力: assets/charity/members/<mio|rei|kou>_card.jpg （各 1920x1080）
"""
from pathlib import Path
import sys

import cv2
import numpy as np
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
RECEIVED = HERE / "received"
GROUP_CUT = HERE / "group_band_cutout.png"

# 宣材の中で3人が占める横位置（不透明画素を数えて実測した値）
SPANS = {"mio": (0.020, 0.315), "kou": (0.350, 0.668), "ray": (0.700, 1.000)}

CARDS = (
    # 出力名, 写真の出どころ, 英字, 和名, パート, 補足, ロゴを添えるか
    ("mio_card.jpg", ("solo", RECEIVED / "mio_suit_cut.png"), "MIO", "社美緒",
     "Guitar ／ 主宰", "Group Yggdrasill 会長", True),
    ("rei_card.jpg", ("group", "ray"), "RAY", "", "Guitar", "", False),
    ("kou_card.jpg", ("group", "kou"), "KØU", "", "Vocal", "", False),
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


def smooth_alpha(im: Image.Image) -> Image.Image:
    """切り抜きの縁を均す。

    白いスーツ（RAY）は白い背景との差が小さいので、抜いたままだと
    縁が階段状に欠ける。中央値ぼかしと開閉で粒を落としてから、
    わずかにぼかして急な閾値で戻すと、輪郭が滑らかになる。
    """
    a = np.array(im.convert("RGBA"))
    alpha = a[..., 3]
    alpha = cv2.medianBlur(alpha, 7)
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (9, 9))
    alpha = cv2.morphologyEx(alpha, cv2.MORPH_CLOSE, k)
    alpha = cv2.morphologyEx(alpha, cv2.MORPH_OPEN, k)

    solid = (alpha > 60).astype(np.uint8)      # 浮いた破片を落とす
    n, lab, st, _ = cv2.connectedComponentsWithStats(solid, 8)
    if n > 1:
        biggest = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
        alpha[lab != biggest] = 0

    alpha = cv2.GaussianBlur(alpha, (0, 0), 2.2)
    alpha = np.clip((alpha.astype(np.float32) - 128) * 6 + 128, 0, 255)
    alpha = cv2.GaussianBlur(alpha.astype(np.uint8), (0, 0), 0.9)
    a[..., 3] = alpha
    return Image.fromarray(a, "RGBA")


def trim(im: Image.Image) -> Image.Image:
    """切り抜きの周りの透明な余白を落とす。"""
    box = im.getchannel("A").point(lambda v: 255 if v > 8 else 0).getbbox()
    return im.crop(box) if box else im


def cutout(source) -> Image.Image:
    """カードに立てる人物を、背景を外した状態で返す。"""
    kind, ref = source
    if kind == "solo":
        return trim(Image.open(ref).convert("RGBA"))
    im = Image.open(GROUP_CUT).convert("RGBA")
    a, b = SPANS[ref]
    part = im.crop((round(im.width * a), 0, round(im.width * b), im.height))
    return trim(smooth_alpha(part))


def stand(src: Image.Image, height: int, headroom: int = 46) -> Image.Image:
    """人物を、カードの高さに合わせて立てる。頭の上に少しだけ空きを残す。"""
    k = (height - headroom) / src.height
    return src.resize((max(1, round(src.width * k)),
                       max(1, round(src.height * k))), Image.Resampling.LANCZOS)


def build(out_name: str, source, roman: str, kanji: str, part: str,
          note: str, with_logo: bool = False) -> None:
    base = Image.new("RGB", (W, H), INK).convert("RGBA")

    # 地：中央から右へ向かう淡いクリムゾンの滲み
    glow = Image.new("L", (W // 8, H // 8), 0)
    ImageDraw.Draw(glow).ellipse((W * 0.30 / 8, -H * 0.25 / 8,
                                  W * 1.25 / 8, H * 1.10 / 8), fill=76)
    glow = glow.resize((W, H), Image.Resampling.BILINEAR).filter(
        ImageFilter.GaussianBlur(150))
    base = Image.composite(Image.new("RGBA", (W, H), DEEPEST_CRIMSON + (255,)),
                           base, glow)
    # 透かしは小さく、文字の無いところへ（2026-09-16）。
    # 大きく敷くと木の部分が枠で切れて茶色い塊に見え、名前に線がかぶる
    base = stamp(base, scale=0.30, opacity=14, center=(0.80, 0.82))

    # 人物は背景を外してある。四角い写真を貼ると「貼っただけ」に見えるので、
    # 切り抜きのまま黒地に立てる
    person = stand(cutout(source), H)
    if person.width > 760:                     # 幅が出すぎたら高さで詰める
        person = stand(cutout(source), round(H * 760 / person.width))
    px = max(40, (760 - person.width) // 2 + 40)
    base.alpha_composite(person, (px, H - person.height))

    d = ImageDraw.Draw(base)
    x = 880
    d.line((x, 300, x + 96, 300), fill=CRIMSON + (255,), width=3)

    tracked(d, (x, 340), roman, face(DIDOT, 132), CREAM + (255,), 12)
    y = 520
    if kanji:
        d.text((x + 4, y), kanji, font=face(MINCHO, 56), fill=(236, 224, 220, 255))
        y += 96
    d.text((x + 4, y), part, font=face(SANS, 30), fill=(206, 190, 190, 255))
    if note:
        d.text((x + 4, y + 52), note, font=face(SANS, 26), fill=(184, 170, 172, 255))
        y += 52
    if with_logo:
        # MIO YASHIRO のロゴ。原画が 296px なので、それ以上には伸ばさない
        logo = Image.open(RECEIVED / "mio_yashiro_logo.png").convert("RGBA")
        lw = min(logo.width, 268)
        logo = logo.resize((lw, round(logo.height * lw / logo.width)),
                           Image.Resampling.LANCZOS)
        d.line((x + 4, y + 110, x + 4 + 72, y + 110), fill=CRIMSON + (255,), width=2)
        base.alpha_composite(logo, (x + 2, y + 140))

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
