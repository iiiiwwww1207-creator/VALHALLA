#!/usr/bin/env python3
"""長い文章が続く章に差し込む図版をつくる。

CAMPFIRE 掲載ページは CHAPTER 03〜09 の約4,000字に図版が1枚も無く、
そこだけ文字の壁になっていた。飾りで埋めるのではなく、
「文章で説明すると長くなるもの」を図に移して、読む量そのものを減らす。

つくるもの:
    ch03_entame     鳴らし続けている間だけ残る（引用＋実写）
    ch04_ai         have to を AI に（既存のAI図版の回路を地に使う）
    ch05_havetowant 一日の内訳が変わる（24時間の帯・2本）
    ch07_loop       3つは一周してつながる（循環図）★本文の核
    ch08_pass       見せる → 伝える → 増える
    ch13_schedule   公開から支援の報告まで（年表）

使い方: python3 assets/charity/create_chapter_banners.py
"""
from __future__ import annotations

import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter

from banner_kit import (ASH, BLACK, CREAM, CRIMSON, DARK_CRIMSON, H, LATIN,
                        MINCHO, SANS, SANS_B, SCALE, SILVER, SW, SH, W, arrow,
                        centered, eyebrow, face, finish, footer, ground, node,
                        sbox, spos, tracked)
from logo_watermark import stamp

HERE = Path(__file__).resolve().parent


def photo(path: Path, box, darken: float = 0.42, blur: float = 0.0,
          span: tuple[float, float] | None = None,
          tint: float = 0.0, vfocus: float = 0.5) -> Image.Image:
    """写真を box（実寸）に収めて切り抜き、地に馴染むまで落とす。

    span … 先に横方向を切り出す範囲（幅に対する比）。3人並びから1人だけ抜くため
    tint … 白飛びした地を黒地に馴染ませるため、深紅を重ねる強さ（0〜1）
    vfocus … 縦の切り取り位置（0=上端寄せ / 0.5=中央）。顔が切れるのを避ける
    """
    x0, y0, x1, y1 = box
    tw, th = round((x1 - x0) * SCALE), round((y1 - y0) * SCALE)
    im = Image.open(path).convert("RGB")
    if span:
        a, b = span
        im = im.crop((round(im.width * a), 0, round(im.width * b), im.height))
    s = max(tw / im.width, th / im.height)
    im = im.resize((math.ceil(im.width * s), math.ceil(im.height * s)),
                   Image.Resampling.LANCZOS)
    left = (im.width - tw) // 2
    top = round((im.height - th) * vfocus)
    im = im.crop((left, top, left + tw, top + th))
    if blur:
        im = im.filter(ImageFilter.GaussianBlur(blur * SCALE))
    im = ImageEnhance.Brightness(im).enhance(darken)
    if tint:
        wash = Image.new("RGB", im.size, DARK_CRIMSON)
        im = Image.blend(im, wash, tint)
    return im.convert("RGBA")


def fade_left(layer: Image.Image, box, hard: float = 0.30) -> Image.Image:
    """写真の左端を黒へ溶かす。文字を載せる側を空けるため。"""
    x0, y0, x1, y1 = box
    w = round((x1 - x0) * SCALE)
    h = round((y1 - y0) * SCALE)
    mask = Image.new("L", (w, h))
    md = ImageDraw.Draw(mask)
    edge = round(w * hard)
    for x in range(w):
        md.line([(x, 0), (x, h)], fill=255 if x >= edge else round(255 * x / edge))
    layer.putalpha(mask)
    return layer


# ───────────────────────────────── CHAPTER 03

def ch03_entame(out: Path) -> None:
    img = ground()
    box = (887, 0, W, H)
    shot = fade_left(photo(HERE / "group_band.jpg", box, darken=0.30,
                           span=(0.26, 0.73), tint=0.30, vfocus=0.22), box, hard=0.46)
    img.alpha_composite(shot, spos((box[0], box[1])))
    img = stamp(img, scale=0.62, opacity=30, center=(0.30, 0.52))
    d = ImageDraw.Draw(img)
    eyebrow(d, "CHAPTER 03 ／ エンタメ")

    big = face(MINCHO, 54)
    for i, line in enumerate(["文化は、語られて", "残るのではありません。"]):
        d.text(spos((70, 300 + i * 78)), line, font=big, fill=CREAM)
    d.line(sbox((70, 480, 300, 480)), fill=CRIMSON, width=2 * SCALE)
    for i, line in enumerate(["鳴らし続けている間だけ、", "残ります。"]):
        d.text(spos((70, 516 + i * 78)), line, font=big, fill=CREAM)

    tracked(d, (70, 700), "だから私たちは、鳴らす側と聴きに来る側が出会える場所を用意しました。",
            face(SANS, 22), SILVER, tracking=1)
    finish(img, out)


# ───────────────────────────────── CHAPTER 04

def ch04_ai(out: Path) -> None:
    """既存の concept_banner の下段（AIの回路）を地として使い直す。"""
    img = ground()
    src = Image.open(HERE / "concept_banner.jpg").convert("RGB")
    # 既存図版の AI 段は左側に見出しが入っているので、回路だけの右側を切り出す
    band = src.crop((round(src.width * 0.42), round(src.height * 0.63),
                     src.width, src.height))
    band = band.resize((SW, round(SW * band.height / band.width)),
                       Image.Resampling.LANCZOS)
    band = ImageEnhance.Brightness(band).enhance(0.78).convert("RGBA")

    mask = Image.new("L", band.size)
    md = ImageDraw.Draw(mask)
    for y in range(band.height):
        md.line([(0, y), (band.width, y)],
                fill=round(255 * min(1.0, y / (band.height * 0.55))))
    band.putalpha(mask)
    img.alpha_composite(band, (0, SH - band.height))

    img = stamp(img, scale=0.70, opacity=26, center=(0.50, 0.40))
    d = ImageDraw.Draw(img)
    eyebrow(d, "CHAPTER 04 ／ AI")

    big = face(MINCHO, 58)
    centered(d, W / 2, 210, "have to を、AI に。", big, CREAM)
    centered(d, W / 2, 292, "空いた時間を、音楽に。", big, CREAM)
    d.line(sbox((W / 2 - 110, 400, W / 2 + 110, 400)), fill=CRIMSON, width=2 * SCALE)
    centered(d, W / 2, 428,
             "好きなことに使う時間は、勝手には生まれません。",
             face(SANS, 23), SILVER)
    centered(d, W / 2, 468,
             "AI をどう使いこなすかが分かっていないと、その時間はつくれない。",
             face(SANS, 23), SILVER)
    finish(img, out)


# ───────────────────────────────── CHAPTER 05

def ch05_havetowant(out: Path) -> None:
    img = stamp(ground(), scale=0.78, opacity=18, center=(0.50, 0.52))
    d = ImageDraw.Draw(img)
    eyebrow(d, "CHAPTER 05 ／ have to と want to")

    centered(d, W / 2, 96, "一日は24時間しかない。変えられるのは、中身の比率です。",
             face(SANS, 25), SILVER)

    left, right = 300, 1474
    span = right - left

    def bar(y: float, ratio: float, caption: str) -> None:
        h = 62
        cut = left + span * ratio
        d.rectangle(sbox((left, y, cut, y + h)), fill=DARK_CRIMSON)
        d.rectangle(sbox((cut, y, right, y + h)), fill=(228, 222, 210))
        d.rectangle(sbox((left, y, right, y + h)), outline=(70, 60, 62),
                    width=round(1 * SCALE))
        # 帯の中の呼び名。狭いほうは外に出す
        ht = face(SANS_B, 24)
        if ratio > 0.22:
            centered(d, (left + cut) / 2, y + 17, "have to", ht, (236, 210, 210))
        if 1 - ratio > 0.16:
            centered(d, (cut + right) / 2, y + 17, "want to", ht, (52, 40, 42))
        d.text(spos((left - 148, y + 14)), caption, font=face(MINCHO, 30), fill=CREAM)
        return cut

    cut1 = bar(228, 0.90, "い ま")
    cut2 = bar(452, 0.60, "これから")

    # 2本の帯のあいだ。AI が境目を左へ押す
    for x in (cut1,):
        d.line(sbox((x, 296, x, 440)), fill=(96, 84, 88), width=round(1 * SCALE))
    arrow(d, (cut1 - 6, 372), (cut2 + 8, 372), color=CRIMSON, width=1.8, head=13)
    lbl = "AI が have to を肩代わりする"
    w = d.textlength(lbl, font=face(SANS, 22)) / SCALE
    mid = (cut1 + cut2) / 2
    d.rectangle(sbox((mid - w / 2 - 14, 336, mid + w / 2 + 14, 368)), fill=BLACK)
    centered(d, mid, 340, lbl, face(SANS, 22), CREAM)

    centered(d, (cut2 + right) / 2, 548, "ここが広がる", face(SANS, 21), ASH)
    img = footer(img, ["空いた時間を、", "やりたいことへ。"])
    finish(img, out)


# ───────────────────────────────── CHAPTER 07  ★本文の核

def ch07_loop(out: Path) -> None:
    img = stamp(ground(), scale=0.50, opacity=20, center=(0.285, 0.53))
    d = ImageDraw.Draw(img)
    eyebrow(d, "CHAPTER 07 ／ 3つは、一周してつながる")

    cx, cy, R, r = 505, 470, 212, 74
    steps = [("文化", -90), ("エンタメ", 0), ("AI", 90), ("人", 180)]
    pts = {}
    for label, deg in steps:
        a = math.radians(deg)
        pts[label] = (cx + math.cos(a) * R, cy + math.sin(a) * R)

    # 節どうしを結ぶ弧。時計回りに一周させる
    for i in range(4):
        a0 = math.radians(steps[i][1])
        a1 = math.radians(steps[(i + 1) % 4][1])
        gap = math.asin(min(1.0, (r + 16) / R))
        seg = []
        t = a0 + gap
        end = a1 - gap if a1 > a0 else a1 + 2 * math.pi - gap
        while t < end:
            seg.append((cx + math.cos(t) * R, cy + math.sin(t) * R))
            t += 0.05
        seg.append((cx + math.cos(end) * R, cy + math.sin(end) * R))
        for j in range(len(seg) - 1):
            d.line(sbox((*seg[j], *seg[j + 1])), fill=DARK_CRIMSON,
                   width=round(1.6 * SCALE))
        arrow(d, seg[-2], seg[-1], color=CRIMSON, width=1.6, head=13)

    for label, _ in steps:
        px, py = pts[label]
        d.ellipse(sbox((px - r, py - r, px + r, py + r)), fill=BLACK)
        node(d, (px, py), r, width=2)
        f = face(MINCHO, 34 if len(label) <= 3 else 29)
        tw = d.textlength(label, font=f) / SCALE
        d.text(spos((px - tw / 2, py - 24)), label, font=f, fill=CREAM)


    # 右側に、つながる理由を1行ずつ置く
    x = 1000
    rows = [("文化", "エンタメ", "受け継ぐには、鳴らし続けるしかない"),
            ("エンタメ", "AI", "鳴らし続けるには、時間が要る"),
            ("AI", "人", "空いた時間で、何をしたいのか"),
            ("人", "文化", "やりたいことは、人と会う場所で見つかる")]
    y = 232
    for a, b, why in rows:
        fa = face(SANS_B, 26)
        wa = d.textlength(a, font=fa) / SCALE
        d.text(spos((x, y)), a, font=fa, fill=CREAM)
        d.text(spos((x + wa + 14, y + 3)), "→", font=face(SANS, 24), fill=CRIMSON)
        d.text(spos((x + wa + 52, y)), b, font=fa, fill=CREAM)
        d.text(spos((x, y + 40)), why, font=face(SANS, 21), fill=SILVER)
        d.line(sbox((x, y + 84, 1704, y + 84)), fill=(58, 48, 52), width=SCALE)
        y += 112
    finish(img, out)


# ───────────────────────────────── CHAPTER 08

def ch08_pass(out: Path) -> None:
    img = stamp(ground(), scale=0.86, opacity=22, center=(0.50, 0.54))
    d = ImageDraw.Draw(img)
    eyebrow(d, "CHAPTER 08 ／ 見せて、伝えて、増やす")

    stops = [("見せる", "経営者をやりながら、ステージに立つ"),
             ("伝える", "AIリテラシーと経営を、学べる場に"),
             ("増える", "一人が二人になり、二人が十人になる")]
    cy, r = 420, 96
    xs = [447, 887, 1327]
    for i in range(len(xs) - 1):
        arrow(d, (xs[i] + r + 18, cy), (xs[i + 1] - r - 18, cy),
              color=CRIMSON, width=1.6, head=13)
    for (title, sub), x in zip(stops, xs):
        d.ellipse(sbox((x - r, cy - r, x + r, cy + r)), fill=BLACK)
        node(d, (x, cy), r, width=2)
        centered(d, x, cy - 26, title, face(MINCHO, 40), CREAM)
        centered(d, x, cy + r + 44, sub, face(SANS, 21), SILVER)
    centered(d, W / 2, 168, "背中を見せるだけでは、そこで止まります。",
             face(SANS, 25), SILVER)
    img = footer(img, ["この夜は、", "そのはじまりの一歩です。"])
    finish(img, out)


# ───────────────────────────────── CHAPTER 13

def ch13_schedule(out: Path) -> None:
    img = stamp(ground(), scale=0.86, opacity=20, center=(0.50, 0.54))
    d = ImageDraw.Draw(img)
    eyebrow(d, "CHAPTER 13 ／ スケジュール")

    stops = [("2026.09", "クラウドファンディング公開"),
             ("10.18 昼", "WRAPPING THE EARTH TOKYO 2026"),
             ("10.18 夜", "VALHALLA CHARITY LIVE ／ 渋谷"),
             ("本番後", "収支を活動報告で公開"),
             ("2026.11", "ファンミーティング ／ 資金の活用")]
    y = 452
    left, right = 190, 1584
    d.line(sbox((left, y, right, y)), fill=(72, 58, 62), width=round(1.4 * SCALE))
    step = (right - left) / (len(stops) - 1)
    for i, (when, what) in enumerate(stops):
        x = left + step * i
        big = i in (1, 2)
        rr = 13 if big else 8
        d.ellipse(sbox((x - rr, y - rr, x + rr, y + rr)),
                  fill=CRIMSON if big else BLACK,
                  outline=CRIMSON, width=round(1.8 * SCALE))
        up = i % 2 == 0
        centered(d, x, y - 92 if up else y + 54, when,
                 face(LATIN if when.isascii() else SANS_B, 26), CREAM)
        for j, line in enumerate(_wrap(what, 13)):
            centered(d, x, (y - 56 if up else y + 90) + j * 30, line,
                     face(SANS, 19), SILVER)
    img = footer(img, ["公開から報告まで、", "数字は伏せません。"])
    finish(img, out)


def _wrap(text: str, n: int) -> list[str]:
    out, line = [], ""
    for ch in text:
        line += ch
        if len(line) >= n and ch in "　 ／":
            out.append(line.strip()); line = ""
    if line.strip():
        out.append(line.strip())
    return out or [text]


if __name__ == "__main__":
    jobs = [(ch03_entame, "ch03_entame.jpg"), (ch04_ai, "ch04_ai.jpg"),
            (ch05_havetowant, "ch05_havetowant.jpg"), (ch07_loop, "ch07_loop.jpg"),
            (ch08_pass, "ch08_pass.jpg"), (ch13_schedule, "ch13_schedule.jpg")]
    for fn, name in jobs:
        fn(HERE / name)
