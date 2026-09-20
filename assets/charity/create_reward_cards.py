#!/usr/bin/env python3
"""CAMPFIRE のリターン1件ずつに付ける画像（1200x800）を書き出す。

支援コース図版（create_returns_banner.py）と同じ意匠のまま、
1枚につき1プランだけを載せる。カード上で見えるのは
「いくらで」「何口で」「何が付くか」の3つだけにする。

使い方: python3 assets/charity/create_reward_cards.py
出力  : assets/charity/reward_live.jpg ほか計4点
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from logo_watermark import stamp

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = Path(__file__).resolve().parent

W, H = 1200, 800
SCALE = 2
SW, SH = W * SCALE, H * SCALE

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
    raise FileNotFoundError("フォントが見つかりません")


MINCHO = first_font("/System/Library/Fonts/ヒラギノ明朝 ProN.ttc",
                    "/System/Library/Fonts/Times.ttc")
SANS = first_font("/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc",
                  "/System/Library/Fonts/Hiragino Sans GB.ttc")
SANS_B = first_font("/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc",
                    "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc")


def face(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size=size * SCALE)


def sbox(box):
    return tuple(round(v * SCALE) for v in box)


def spos(point):
    return tuple(round(v * SCALE) for v in point)


def make_background() -> Image.Image:
    base = Image.new("RGB", (SW, SH), BLACK).convert("RGBA")
    bloom = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
    bd = ImageDraw.Draw(bloom)
    bd.ellipse(sbox((-200, 90, 700, 980)), fill=(*DEEPEST_CRIMSON, 96))
    bd.ellipse(sbox((680, -300, 1500, 560)), fill=(*DEEPEST_CRIMSON, 70))
    base = Image.alpha_composite(base, bloom.filter(ImageFilter.GaussianBlur(190 * SCALE)))

    vignette = Image.new("L", (SW, SH), 0)
    ImageDraw.Draw(vignette).ellipse(sbox((40, -200, W - 40, H + 210)), fill=212)
    vignette = vignette.filter(ImageFilter.GaussianBlur(120 * SCALE))
    return Image.composite(base, Image.new("RGBA", base.size, (*BLACK, 255)), vignette)


def draw_tracked(draw, xy, text, font, fill, tracking) -> None:
    x, y = spos(xy)
    for char in text:
        draw.text((x, y), char, font=font, fill=fill)
        x += draw.textlength(char, font=font) + tracking * SCALE


# (出力名, 見出し, プラン名, 金額, 条件, 箇条書き, 強調するか)
CARDS = [
    ("reward_support.jpg", "SUPPORT", "応援プラン", "¥1,000",
     "口数の制限なし ／ 来場なし",
     ("限定名刺（デジタル版）をLINE公式でお届け",), False),
    ("reward_live.jpg", "LIVE", "ライブプラン", "¥10,000",
     "限定30口 ／ スタンディング後方",
     ("アコースティックライブ観覧（スタンディング後方）",
      "フリードリンク（飲み放題）"), False),
    ("reward_vip.jpg", "FRONT ROW", "VIPプラン", "¥50,000",
     "限定15口 ／ スタンディング最前列 ／ 18:00 先行入場",
     ("ステージ前の最前列エリアで観覧",
      "MIO とのチェキ撮影＋ハイタッチ（18:15〜）",
      "限定名刺（サイン入り／ネックストラップ付き）",
      "フリードリンク（飲み放題）",
      "［11/28］MIO が梵字をお書きします",
      "［11/28］シャンパンコール観覧・うちわ・ゲーム"), False),
    ("reward_vvip.jpg", "VVIP", "VVIPプラン", "¥330,000",
     "限定5口 ／ 同伴1名まで可（特典は2名分）／ ソファー席",
     ("MIO がお席にご挨拶に伺い、6分前後",
      "お席を当日のご到着順で（1口につき1区画）",
      "チェキ／写真／動画の撮影ができます",
      "限定名刺・なりきりグッズ（＋トートバッグ）",
      "［11/28］30分のグループセッション",
      "［11/28］梵字Tシャツ・MIO が浄化したクリスタル",
      "社学園へのご優待"), True),
]

FOOTER = "収益から必要経費を除いた全額を、教育文化セキュリティ財団へお渡しします"


def build(name, kicker, title, amount, meta, bullets, emphasized) -> Path:
    base = make_background()
    d = ImageDraw.Draw(base)

    # 枠。VVIP だけ太く明るくする（値段ではなく枠で違いを出す）
    d.rounded_rectangle(
        sbox((40, 40, W - 40, H - 40)), radius=18 * SCALE,
        outline=(*CRIMSON, 255) if emphasized else (*DARK_CRIMSON, 210),
        width=(5 if emphasized else 2) * SCALE,
    )

    draw_tracked(d, (78, 78), "VALHALLA CHARITY LIVE ／ 2026.10.18 SUN ／ 渋谷",
                 face(SANS, 16), CRIMSON, 3)

    draw_tracked(d, (78, 152), kicker, face(SANS, 17), CRIMSON, 4)
    d.text(spos((78, 188)), title, font=face(MINCHO, 62), fill=CREAM, anchor="la")
    d.text(spos((78, 286)), amount, font=face(SANS_B, 76), fill=CREAM, anchor="la")
    d.text(spos((78, 392)), meta, font=face(SANS, 21), fill=SILVER, anchor="la")

    d.line(spos((78, 434, W - 78, 434)), fill=(*DARK_CRIMSON, 220), width=SCALE)

    step = 40 if len(bullets) <= 6 else 36
    bullet_font = face(SANS, 21)
    for i, line in enumerate(bullets):
        y = 462 + i * step
        d.ellipse(sbox((79, y + 9, 85, y + 15)), fill=CRIMSON)
        d.text(spos((100, y)), line, font=bullet_font, fill=SILVER, anchor="la")

    d.text(spos((W / 2, H - 82)), FOOTER, font=face(SANS, 16), fill=SILVER, anchor="ma")

    base = stamp(base, scale=0.34, opacity=14, center=(0.80, 0.30))
    out = HERE / name
    base.convert("RGB").save(out, "JPEG", quality=90, subsampling="4:2:0",
                             optimize=False, progressive=False)
    if base.size != (SW, SH):
        raise RuntimeError("サイズが不正です")
    size = os.path.getsize(out)
    if size > 2 * 1024 * 1024:
        raise RuntimeError(f"2MB 超過: {size}")
    return out


def main() -> None:
    for spec in CARDS:
        out = build(*spec)
        im = Image.open(out)
        # 本番と同じ 1200x800 に落とす（作画は2倍で行っている）
        im.resize((W, H), Image.Resampling.LANCZOS).save(
            out, "JPEG", quality=90, optimize=False, progressive=False)
        print(f"{out.name}  {W}x{H}  {os.path.getsize(out)//1024} KB")


if __name__ == "__main__":
    main()
