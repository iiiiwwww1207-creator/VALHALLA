#!/usr/bin/env python3
"""会場のフロア図を、支援者が読める形に描き直す。

会場から受け取った図（floor.jpg）は卓番号（V1〜V6・S1〜S4・DJ1/DJ2）のままで、
初めて見る人には「DJ席・V4・V1 から先着順で選べます」が何のことか分からない。
図をそのまま出すのではなく、区画に色を敷いて、コース名で読めるようにする。

会場の図面そのものは動かさない。上に色と凡例を重ねるだけなので、
実際の配置と食い違わない。

区画の対応（docs/campfire-project-body.md より）:
    VVIP席  … DJ1・DJ2・V4・V1
    S席     … V2・V3・V5・V6・S1〜S4
    中央    … ステージとスタンディング
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

from banner_kit import (ASH, BLACK, CREAM, CRIMSON, DARK_CRIMSON, H, SANS,
                        SANS_B, SCALE, SH, SILVER, SW, W, MINCHO, centered,
                        eyebrow, face, finish, ground, sbox, spos, tracked)

HERE = Path(__file__).resolve().parent
PLAN = HERE / "floor.jpg"
OUTPUT = HERE / "floor_banner.jpg"

# floor.jpg（1280x1280）上での各区画のおおよその中心
ZONES = {
    "DJ1": (478, 285), "DJ2": (350, 380), "V4": (452, 560), "V1": (878, 560),
    "V6": (350, 625), "V5": (452, 715), "V3": (1005, 622), "V2": (878, 715),
    "S4": (160, 782), "S3": (333, 910), "S1": (1105, 795), "S2": (1000, 925),
    "BAR": (663, 993), "FRONT": (663, 585), "FLOOR": (663, 790),
}
VVIP = ("DJ1", "DJ2", "V4", "V1")
SSEAT = ("V2", "V3", "V5", "V6", "S1", "S2", "S3", "S4")

GOLD = (201, 169, 97)
BLUE = (108, 140, 196)


def plan_layer(size: int) -> tuple[Image.Image, float, tuple[int, int]]:
    """会場の図を、地の黒に馴染む明るさで置く。倍率と貼り位置を返す。"""
    im = Image.open(PLAN).convert("RGB")
    k = size / im.width
    im = im.resize((size, round(im.height * k)), Image.Resampling.LANCZOS)
    im = ImageEnhance.Brightness(im).enhance(0.92)
    # 会場図の黒地はこちらの地より明るく、四角い板が乗ったように見える。
    # 明るさをそのまま不透明度にして、黒い部分を地に溶かす
    lum = im.convert("L").point(lambda v: min(255, round(v * 3.4)))
    rgba = im.convert("RGBA")
    rgba.putalpha(lum)
    return rgba, k, (0, 0)


def pin(draw: ImageDraw.ImageDraw, xy, r: float, color, width: float = 2.4) -> None:
    x, y = xy
    draw.ellipse(sbox((x - r, y - r, x + r, y + r)), outline=color,
                 width=round(width * SCALE))


def build(out: Path) -> None:
    img = ground()

    # 図は左側に。右は凡例に使う
    size = 760
    plan, k, _ = plan_layer(size * SCALE)
    ox, oy = round(70 * SCALE), round((H * SCALE - plan.height) / 2)
    img.alpha_composite(plan, (ox, oy))

    d = ImageDraw.Draw(img)
    eyebrow(d, "VALHALLA CHARITY LIVE ／ フロア")

    def at(name: str) -> tuple[float, float]:
        """会場図の座標を、この図版の座標に直す。"""
        px, py = ZONES[name]
        return ((ox + px * k) / SCALE, (oy + py * k) / SCALE)

    # 区画に印を打つ。VVIP は金、S席は青
    for name in VVIP:
        pin(d, at(name), 34, GOLD, 2.6)
    for name in SSEAT:
        pin(d, at(name), 27, BLUE, 2.0)

    # DJブースのすぐ手前が最前列。丸ではなく楕円で、前方だけを囲う
    fx, fy = at("FRONT")
    rx, ry = 82, 32
    d.ellipse(sbox((fx - rx, fy - ry, fx + rx, fy + ry)), outline=CRIMSON,
              width=round(2.4 * SCALE))
    centered(d, fx, fy - 13, "最前列席", face(SANS_B, 21), CREAM)

    # その後ろがライブ席（スタンディング）
    bx, by_ = at("FLOOR")
    centered(d, bx, by_ - 12, "ライブ席", face(SANS_B, 21), (214, 170, 176))
    centered(d, bx, by_ + 16, "スタンディング", face(SANS, 16), ASH)

    # 右側の凡例
    x = 900
    y = 176
    rows = [
        (GOLD, "VVIP席", "図の金色の4区画から、先着順でお選びいただけます"),
        (BLUE, "S席・MIOタイム", "図の青色の区画。お席は主催者が指定します"),
        (CRIMSON, "最前列席", "DJブース前の最前列エリアで立ってご覧いただきます"),
        (None, "ライブ席", "その後ろの中央フロアで立ってご覧いただきます"),
    ]
    for color, title, sub in rows:
        if color:
            pin(d, (x + 15, y + 15), 15, color, 2.4)
        d.text(spos((x + 48, y - 2)), title, font=face(SANS_B, 27), fill=CREAM)
        d.text(spos((x + 48, y + 36)), sub, font=face(SANS, 19), fill=SILVER)
        d.line(sbox((x, y + 78, 1704, y + 78)), fill=(58, 48, 52), width=SCALE)
        y += 106

    y += 16
    d.text(spos((x, y)), "お席はすべて相席です", font=face(SANS_B, 24), fill=CREAM)
    for i, line in enumerate([
            "着席のコース（S席・VVIP席）は、グループごとの",
            "個室・貸切ではありません。ほかのお客様と同じ",
            "区画・同じテーブルになります。"]):
        d.text(spos((x, y + 40 + i * 32)), line, font=face(SANS, 19), fill=SILVER)

    y += 156
    d.text(spos((x, y)), "着席 50名 ／ スタンディング 130名", font=face(SANS_B, 22), fill=GOLD)
    d.text(spos((x, y + 36)), "ドリンクは会場（図の BAR）が提供します",
           font=face(SANS, 19), fill=ASH)

    finish(img, out)


if __name__ == "__main__":
    build(OUTPUT)
