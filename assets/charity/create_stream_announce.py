#!/usr/bin/env python3
"""配信告知の画像をつくる。

素材は野球場で撮った3人（group_field.jpg）。この写真は青空と芝の明るい絵で、
本文図版の黒地とは別物なので、無理に暗く沈めない。写真を主役に置いて、
写真の中にすでに写っている「スコアボード」の見た目を借りて情報を載せる。

出力:
    stream_1x1.jpg   1080x1080  Instagram / X 用
    stream_9x16.jpg  1080x1920  ストーリー / TikTok 用

使い方: python3 assets/charity/create_stream_announce.py
"""
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

HERE = Path(__file__).resolve().parent
PHOTO = HERE / "group_field.jpg"

SCALE = 2
INK = (12, 16, 26)
CREAM = (247, 249, 252)
# スコアボードの青。写真から拾った色
BOARD = (18, 96, 176)
BOARD_DARK = (10, 30, 56)
AMBER = (247, 196, 72)

MINCHO = "/System/Library/Fonts/ヒラギノ明朝 ProN.ttc"
SANS = "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc"
SANS_B = "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc"
DIDOT = "/System/Library/Fonts/Supplemental/Didot.ttc"
# スコアボードの文字は太いサンセリフ。数字もそれに合わせる
# （Didot は旧式数字で「1」が小さく、日付が読みにくい）
HELV = "/System/Library/Fonts/HelveticaNeue.ttc"
HELV_BOLD = 1


def face(path: str, size: int, index: int = 0) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size=size * SCALE, index=index)


def sbox(b) -> tuple:
    return tuple(round(v * SCALE) for v in b)


def spos(p) -> tuple:
    return tuple(round(v * SCALE) for v in p)


def tracked(d, xy, text, font, fill, tracking=0):
    x, y = spos(xy)
    for ch in text:
        d.text((x, y), ch, font=font, fill=fill)
        x += round(d.textlength(ch, font=font)) + tracking * SCALE
    return (x - spos(xy)[0]) / SCALE


def centered(d, cx, y, text, font, fill):
    w = d.textlength(text, font=font) / SCALE
    d.text(spos((cx - w / 2, y)), text, font=font, fill=fill)


def photo_fill(box, focus_y: float = 0.42) -> Image.Image:
    """写真を箱いっぱいに。3人が中心に来るよう、縦の取り方だけ指定する。"""
    w, h = box
    tw, th = w * SCALE, h * SCALE
    im = Image.open(PHOTO).convert("RGB")
    k = max(tw / im.width, th / im.height)
    im = im.resize((round(im.width * k), round(im.height * k)), Image.Resampling.LANCZOS)
    left = (im.width - tw) // 2
    top = max(0, min(im.height - th, round((im.height - th) * focus_y)))
    return im.crop((left, top, left + tw, top + th))


def scrim(size, top_a: int, bot_a: int, split: float = 0.5) -> Image.Image:
    """上下から黒を落とす。文字を載せる側だけ濃くする。"""
    w, h = size
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for y in range(h):
        t = y / (h - 1)
        a = round(top_a * max(0.0, 1 - t / split)) if t < split else \
            round(bot_a * ((t - split) / (1 - split)) ** 1.25)
        d.line([(0, y), (w, y)], fill=(4, 8, 16, a))
    return layer


def board(d, box, radius: float = 10) -> None:
    """スコアボード風の板。青い枠に黒い面。"""
    x0, y0, x1, y1 = box
    d.rounded_rectangle(sbox(box), radius=round(radius * SCALE),
                        fill=(*BOARD_DARK, 236), outline=BOARD,
                        width=round(3 * SCALE))


def build(out: Path, W: int, H: int, story: bool) -> None:
    img = photo_fill((W, H), focus_y=0.56 if story else 0.60).convert("RGBA")
    img = Image.alpha_composite(
        img, scrim((W * SCALE, H * SCALE), 118 if story else 96, 200, 0.30))
    d = ImageDraw.Draw(img)

    # 上：バンド名
    tracked(d, (W * 0.5 - 118, H * (0.055 if story else 0.06)), "VALHALLA",
            face(DIDOT, 30), CREAM, tracking=11)

    # 下：スコアボード風の板に情報をまとめる
    pad = W * 0.072
    bh = H * (0.26 if story else 0.30)
    by = H - bh - H * 0.045
    board(d, (pad, by, W - pad, by + bh))

    cx = W / 2
    y = by + bh * 0.10

    tw = tracked(d, (0, -9999), "LIVE 配信", face(SANS_B, 23), AMBER, tracking=4)
    tracked(d, (cx - tw / 2, y), "LIVE 配信", face(SANS_B, 23), AMBER, tracking=4)
    y += bh * 0.185

    # 日付と時刻を1行に。スコアボードらしく太いサンセリフで
    big = face(HELV, 78 if story else 72, HELV_BOLD)
    small = face(HELV, 30 if story else 28, HELV_BOLD)
    wd = d.textlength("9.18", font=big) / SCALE
    ws = d.textlength("  FRI  19:00", font=small) / SCALE
    x0 = cx - (wd + ws) / 2
    d.text(spos((x0, y)), "9.18", font=big, fill=CREAM)
    d.text(spos((x0 + wd, y + (18 if story else 16))), "  FRI  19:00",
           font=small, fill=AMBER)
    y += bh * 0.345

    d.line(sbox((cx - W * 0.15, y, cx + W * 0.15, y)), fill=BOARD,
           width=round(2 * SCALE))
    y += bh * 0.075

    centered(d, cx, y, "MIO ／ KØU", face(SANS_B, 30 if story else 28), CREAM)
    y += bh * 0.155
    centered(d, cx, y, "クラウドファンディング、同時公開",
             face(SANS, 19 if story else 18), (198, 216, 238))

    flat = img.convert("RGB").resize((W, H), Image.Resampling.LANCZOS)
    for q in (92, 88, 82, 76):
        flat.save(out, "JPEG", quality=q, optimize=True, progressive=True)
        if out.stat().st_size <= 2 * 1024 * 1024:
            break
    print(f"{out.name:<20}{W}x{H}  {out.stat().st_size//1024}KB")


if __name__ == "__main__":
    build(HERE / "stream_1x1.jpg", 1080, 1080, story=False)
    build(HERE / "stream_9x16.jpg", 1080, 1920, story=True)
