#!/usr/bin/env python3
"""限定名刺の試作。切り抜いた人物を、自前の背景に載せる。

背景を差し替えてしまえば、元写真に写り込んでいた他社ロゴは残らない。
名刺は支援の対価として配るものなので、そこは必ず断ち切っておく。

仕上がり 55x91mm（縦）／裁ち落とし 3mm ／ 350dpi
  → 61x97mm = 840x1336px。内側の点線が仕上がり線。

出力: assets/charity/meishi/meishi_<名前>.jpg
"""
from pathlib import Path
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
from logo_watermark import stamp

HERE = Path(__file__).resolve().parent
CUT = HERE / "meishi"

DPI = 350
MM = DPI / 25.4
W, H = round(61 * MM), round(97 * MM)          # 裁ち落とし込み
BLEED = round(3 * MM)

INK = (10, 7, 9)
CREAM = (245, 239, 228)
CRIMSON = (193, 18, 31)
DEEPEST_CRIMSON = (110, 10, 18)

MINCHO = "/System/Library/Fonts/ヒラギノ明朝 ProN.ttc"
MINCHO_W6 = 2
SANS = "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc"
DIDOT = "/System/Library/Fonts/Supplemental/Didot.ttc"


def face(path: str, size: int, index: int = -1) -> ImageFont.FreeTypeFont:
    if index < 0:
        index = MINCHO_W6 if path == MINCHO else 0
    return ImageFont.truetype(path, size=size, index=index)


def tracked(d: ImageDraw.ImageDraw, xy, text, font, fill, tracking: float,
            anchor_right: float = None) -> float:
    widths = [d.textlength(c, font=font) for c in text]
    total = sum(widths) + tracking * (len(text) - 1)
    x = (anchor_right - total) if anchor_right is not None else xy[0]
    for c, w in zip(text, widths):
        d.text((x, xy[1]), c, font=font, fill=fill)
        x += w + tracking
    return total


def ground() -> Image.Image:
    base = Image.new("RGB", (W, H), INK).convert("RGBA")
    glow = Image.new("L", (W // 6, H // 6), 0)
    ImageDraw.Draw(glow).ellipse((-W * 0.20 / 6, H * 0.30 / 6,
                                  W * 1.15 / 6, H * 1.35 / 6), fill=96)
    glow = glow.resize((W, H), Image.Resampling.BILINEAR).filter(
        ImageFilter.GaussianBlur(W // 9))
    base = Image.composite(Image.new("RGBA", (W, H), DEEPEST_CRIMSON + (255,)),
                           base, glow)
    return stamp(base, scale=1.05, opacity=26, center=(0.5, 0.42))


def build(cut_name: str, out_name: str) -> None:
    base = ground()

    # 人物は下を裁ち落としにして、名刺の下辺から生やす
    person = Image.open(CUT / cut_name).convert("RGBA")
    ph = round(H * 0.78)
    pw = round(person.width * ph / person.height)
    person = person.resize((pw, ph), Image.Resampling.LANCZOS)
    base.alpha_composite(person, (round(W * 0.52 - pw / 2), H - ph))

    d = ImageDraw.Draw(base)

    # 上：イベント名と肩書き
    tracked(d, (BLEED + round(4 * MM), BLEED + round(5 * MM)),
            "VALHALLA CHARITY LIVE", face(DIDOT, round(2.4 * MM)),
            (232, 208, 208, 255), round(0.6 * MM))
    d.line((BLEED + round(4 * MM), BLEED + round(9.5 * MM),
            BLEED + round(20 * MM), BLEED + round(9.5 * MM)),
           fill=CRIMSON + (255,), width=max(2, round(0.25 * MM)))

    # 名前。名刺なので、いちばん大きいのは名前
    name_f = face(DIDOT, round(11 * MM))
    tracked(d, (BLEED + round(4 * MM), BLEED + round(12 * MM)), "MIO",
            name_f, CREAM + (255,), round(1.0 * MM))
    d.text((BLEED + round(4.5 * MM), BLEED + round(25 * MM)), "Guitar",
           font=face(SANS, round(2.6 * MM)), fill=(212, 196, 196, 255))

    # 下：サインの置き場所。人物の白いパンツの上に文字が来ると読めないので、
    # 先に右下だけ落としてから、本人が手で書くための余白を確保する
    corner = Image.new("L", (W, H), 0)
    ImageDraw.Draw(corner).ellipse(
        (W * 0.30, H * 0.62, W * 1.45, H * 1.30), fill=210)
    corner = corner.filter(ImageFilter.GaussianBlur(W // 8))
    base.alpha_composite(Image.merge(
        "RGBA", [Image.new("L", (W, H), v) for v in (8, 5, 7)] + [corner]))
    d = ImageDraw.Draw(base)
    qf = face(SANS, round(2.0 * MM))
    cap = "Signature"
    d.text((W - BLEED - round(4 * MM) - d.textlength(cap, font=qf),
            H - BLEED - round(13 * MM)),
           cap, font=qf, fill=(150, 126, 122, 255))
    d.line((W - BLEED - round(4 * MM) - round(34 * MM), H - BLEED - round(6 * MM),
            W - BLEED - round(4 * MM), H - BLEED - round(6 * MM)),
           fill=(150, 126, 122, 190), width=2)

    # 仕上がり線（入稿時は消す。いまは確認用）
    guide = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(guide)
    for x in range(BLEED, W - BLEED, 18):
        gd.line((x, BLEED, x + 9, BLEED), fill=(0, 200, 255, 150), width=2)
        gd.line((x, H - BLEED, x + 9, H - BLEED), fill=(0, 200, 255, 150), width=2)
    for y in range(BLEED, H - BLEED, 18):
        gd.line((BLEED, y, BLEED, y + 9), fill=(0, 200, 255, 150), width=2)
        gd.line((W - BLEED, y, W - BLEED, y + 9), fill=(0, 200, 255, 150), width=2)
    base.alpha_composite(guide)

    dst = CUT / out_name
    base.convert("RGB").save(dst, quality=95, subsampling=0, dpi=(DPI, DPI))
    print(f"{dst.name} | {W}x{H}px（61x97mm・裁ち落とし3mm込み）| "
          f"{dst.stat().st_size:,} bytes")


def main() -> None:
    build("valhalla_cut.png", "meishi_mio_pv.jpg")
    build("hostcall_cut.png", "meishi_mio_hostcall.jpg")


if __name__ == "__main__":
    main()
