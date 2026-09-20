#!/usr/bin/env python3
"""会場のフロア図を、支援者が読める形に描き直す。

会場から受け取った図（floor.jpg）は卓番号（V1〜V6・S1〜S4・DJ1/DJ2）のままで、
初めて見る人には「DJ席・V4・V1 から当日のご到着順で選べます」が何のことか分からない。
図をそのまま出すのではなく、区画に色を敷いて、コース名で読めるようにする。

会場の図面そのものは動かさない。上に色と凡例を重ねるだけなので、
実際の配置と食い違わない。

区画の対応（2026-09-20 更新。15万円のコースが無くなり、席は VVIP に一本化）:
    お席（10区画） … V1〜V6・S1〜S4 ── VVIP が選べる（DJ1・DJ2 は対象外）
    最前列エリア     … VIPプラン（スタンディング）
    ライブエリア     … ライブプラン（スタンディング）
    1口につき1区画。ほかのお客様と同じ区画にはならない。
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
# 15万円のコースが無くなったので、席は VVIP が選べる。
# DJ1・DJ2 は対象外。残る10区画なら、VVIP が10口に増えても1口1区画が保てる
VVIP = ("V1", "V2", "V3", "V4", "V5", "V6", "S1", "S2", "S3", "S4")

# 会場図の地が赤紫〜マゼンタなので、そこに近い色は沈む。
# 金は明るい琥珀へ、青は水色寄りへ振って、地から離す
GOLD = (255, 205, 112)
BLUE = (104, 205, 255)
FRONT_RED = (255, 92, 104)
SEAT_RED  = (255, 92, 104)
FRONT_BLUE = (104, 205, 255)


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
    """凡例用の小さな印。輪郭だけで足りる。"""
    x, y = xy
    draw.ellipse(sbox((x - r, y - r, x + r, y + r)), outline=color,
                 width=round(width * SCALE))


def zone_mark(img: Image.Image, xy, r: float, color, width: float = 3.4) -> None:
    """図の上の区画印。

    細い輪郭1本だと、会場図の光る卓に紛れて読めない。
    ① 外側に黒い影を落として地から切り離し
    ② 内側を薄く塗って面として見せ（卓番号は透ける濃さに留める）
    ③ 明るい輪郭を太めに引く
    の3枚重ねにする。
    """
    x, y = xy
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    # ① 影
    d.ellipse(sbox((x - r - 3, y - r - 3, x + r + 3, y + r + 3)),
              fill=(0, 0, 0, 150))
    layer = layer.filter(ImageFilter.GaussianBlur(round(2.2 * SCALE)))
    d = ImageDraw.Draw(layer)
    # ② 面。卓番号が読める濃さで
    d.ellipse(sbox((x - r, y - r, x + r, y + r)), fill=color + (58,))
    # ③ 輪郭
    d.ellipse(sbox((x - r, y - r, x + r, y + r)), outline=color + (255,),
              width=round(width * SCALE))
    img.alpha_composite(layer)


def build(out: Path) -> None:
    img = ground()

    # 図は左側に。右は凡例に使う
    size = 760
    plan, k, _ = plan_layer(size * SCALE)
    ox, oy = round(70 * SCALE), round((H * SCALE - plan.height) / 2)
    img.alpha_composite(plan, (ox, oy))

    # 会場図には「DJ BOOTH」と刷られているが、この日は生演奏の舞台になる。
    # 紫の弧はそのまま活かし、文字のところだけ溶かして置き換える
    box = sbox((380, 281, 556, 337))
    patch = img.crop(box)
    # 白い文字をそのままぼかすと、白が広がって灰色の板になる。
    # 先に明るいところだけ弧の色まで落としてから、ぼかして均す
    cap = 96
    patch = Image.merge("RGBA", [
        ch.point(lambda v: min(v, cap)) if i < 3 else ch
        for i, ch in enumerate(patch.split())])
    patch = patch.filter(ImageFilter.GaussianBlur(round(9 * SCALE)))
    # 縁は羽根にして、板に見えないようにする
    mask = Image.new("L", patch.size, 0)
    ImageDraw.Draw(mask).rounded_rectangle(
        (round(4 * SCALE), round(4 * SCALE),
         patch.width - round(4 * SCALE), patch.height - round(4 * SCALE)),
        radius=round(12 * SCALE), fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(round(6 * SCALE)))
    img.paste(patch, box, mask)

    d = ImageDraw.Draw(img)
    centered(d, 467, 297, "ステージ", face(SANS_B, 24), (246, 238, 240))
    eyebrow(d, "VALHALLA CHARITY LIVE ／ フロア")

    def at(name: str) -> tuple[float, float]:
        """会場図の座標を、この図版の座標に直す。"""
        px, py = ZONES[name]
        return ((ox + px * k) / SCALE, (oy + py * k) / SCALE)

    # 席の区画はすべて金。どれを選んでも VVIP の席という意味になる
    for name in VVIP:
        zone_mark(img, at(name), 30, GOLD, 3.6)
    d = ImageDraw.Draw(img)

    # ステージのすぐ手前が最前列。丸ではなく楕円で、前方だけを囲う
    fx, fy = at("FRONT")
    rx, ry = 82, 32
    front = Image.new("RGBA", img.size, (0, 0, 0, 0))
    fd = ImageDraw.Draw(front)
    fd.ellipse(sbox((fx - rx - 3, fy - ry - 3, fx + rx + 3, fy + ry + 3)),
               fill=(0, 0, 0, 150))
    front = front.filter(ImageFilter.GaussianBlur(round(2.2 * SCALE)))
    fd = ImageDraw.Draw(front)
    fd.ellipse(sbox((fx - rx, fy - ry, fx + rx, fy + ry)), fill=FRONT_BLUE + (56,))
    fd.ellipse(sbox((fx - rx, fy - ry, fx + rx, fy + ry)),
               outline=FRONT_BLUE + (255,), width=round(3.4 * SCALE))
    img.alpha_composite(front)
    d = ImageDraw.Draw(img)
    centered(d, fx, fy - 13, "最前列エリア", face(SANS_B, 21), CREAM)

    # その後ろがライブ席（スタンディング）
    bx, by_ = at("FLOOR")
    centered(d, bx, by_ - 12, "ライブエリア", face(SANS_B, 21), SEAT_RED)
    centered(d, bx, by_ + 16, "スタンディング", face(SANS, 16), ASH)

    # 右側の凡例
    x = 900
    y = 176
    rows = [
        (GOLD, "VVIPプラン", "図の金色の10区画から、当日のご到着順で1区画をお選びいただけます"),
        (FRONT_BLUE, "VIPプラン", "ステージ前の最前列エリア（青の楕円）で立ってご覧いただきます"),
        (FRONT_BLUE, "VIPチェキタイム", "18:15〜 ステージ前でチェキ＋ハイタッチ（VIPプランの方）"),
        (SEAT_RED, "ライブプラン", "中央のライブエリア（スタンディング）でご覧いただきます"),
    ]
    for color, title, sub in rows:
        if color:
            pin(d, (x + 15, y + 15), 15, color, 3.2)
        d.text(spos((x + 48, y - 2)), title, font=face(SANS_B, 27), fill=CREAM)
        d.text(spos((x + 48, y + 36)), sub, font=face(SANS, 19), fill=SILVER)
        d.line(sbox((x, y + 78, 1704, y + 78)), fill=(58, 48, 52), width=SCALE)
        y += 106

    y += 16
    d.text(spos((x, y)), "1口につき、1区画", font=face(SANS_B, 24), fill=CREAM)
    for i, line in enumerate([
            "お席のご用意は VVIPプランのみです。1口につき",
            "1区画をお使いいただけます。ほかのお客様と",
            "同じ区画になることはありません。"]):
        d.text(spos((x, y + 40 + i * 32)), line, font=face(SANS, 19), fill=SILVER)

    y += 156
    d.text(spos((x, y)), "着席は VVIPプランのみ　ほかのコースはスタンディングです", font=face(SANS_B, 22), fill=GOLD)
    lead, lead_f = "ドリンクは会場（図の BAR）が提供します　", face(SANS, 19)
    d.text(spos((x, y + 36)), lead, font=lead_f, fill=SILVER)
    d.text(spos((x + d.textlength(lead, font=lead_f) / SCALE, y + 36)),
           "全コース飲み放題", font=face(SANS_B, 19), fill=GOLD)
    d.text(spos((x, y + 68)), "※ お席を選べる順番は当日のご到着順です。ご支援の順番ではありません。",
           font=face(SANS, 17), fill=ASH)

    finish(img, out)


if __name__ == "__main__":
    build(OUTPUT)

# 作ったら、その場で本文へ流し込む。分けると古い絵が残る。
_BODY = Path.home() / "Desktop" / "VALHALLA_本文にはめる画像" / "IMAGE-20.jpg"
if _BODY.parent.is_dir():
    from PIL import Image as _I
    _I.open(OUTPUT).convert("RGB").resize((1500, 844), _I.Resampling.LANCZOS).save(
        _BODY, "JPEG", quality=90, optimize=True, progressive=True)
    print(f"→ {_BODY.name} へ流し込み")
