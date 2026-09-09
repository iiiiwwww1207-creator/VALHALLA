#!/usr/bin/env python3
"""「文化 × エンタメ × AI」の3語を1枚で説明する縦3段のバナー。

段の並びと見出しの寄せ方は kazuma の指定どおり:

    1段目  文化      見出しは左上   背景に根津神社
    2段目  エンタメ  見出しは右     枠に入れた MV・ライブの画像
    3段目  AI        見出しは左     背景に Codex で生成したテクノロジーの絵

見出しの寄せが 左→右→左 と振れるので、3段が同じ顔にならず、
上から下へ視線が「く」の字に落ちる。本文の一行はページ §3-1 と同じ文言を使う
（同じ言葉が画像とページの両方に出ることで、読んだ人の中で結びつく）。

出力: assets/charity/concept_banner.jpg
"""

from __future__ import annotations

from pathlib import Path

from PIL import (Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter,
                 ImageFont)

HERE = Path(__file__).resolve().parent
SRC = HERE / "concept"
OUTPUT = HERE / "concept_banner.jpg"

W, BAND = 1920, 360
H = BAND * 3
SCALE = 2
SW, SH = W * SCALE, H * SCALE

CRIMSON = (193, 18, 31)
DARK_CRIMSON = (142, 16, 25)
DEEPEST_CRIMSON = (110, 10, 18)
CREAM = (245, 239, 228)
INK = (9, 6, 8)

MINCHO = "/System/Library/Fonts/ヒラギノ明朝 ProN.ttc"
MINCHO_W6 = 2
SANS = "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc"
DIDOT = "/System/Library/Fonts/Supplemental/Didot.ttc"

# 3段の中身。copy は docs/campfire-project-body.md §3-1 からそのまま。
BANDS = (
    {
        "label": "文化",
        "roman": "CULTURE",
        "copy": "歴史を重んじることで、自分たちのやることが文化のつながりになる",
        "note": "2026年5月 ｜ 国指定重要文化財・根津神社「ONE WORLD SPECIAL EVENT」出演",
        "align": "left",
        "photo": "nezu_senbon.jpg",
        "focus": 0.30,
        "credit": "Photo: BWard 1997 / CC BY 4.0 via Wikimedia Commons",
    },
    {
        "label": "エンタメ",
        "roman": "ENTERTAINMENT",
        "copy": "僕たちが盛り上げたい業界。その中で選んだのが、ビジュアル系バンドでした",
        "note": "VALHALLA ｜ MIO / RAY / KØU",
        "align": "right",
        "faces": ("face_ray.jpg", "face_kou.jpg", "face_mio.jpg"),
        "names": ("RAY", "KØU", "MIO"),
    },
    {
        "label": "AI",
        "roman": "TECHNOLOGY",
        "copy": "経営をしながらバンドができているのは、AI で時間をつくれているからです",
        "note": "空いた時間を、好きなことに使う",
        "align": "left",
        "photo": "ai_tech.jpg",
        "dark": 0.18,
    },
)


def face(path: str, size: int, index: int = -1) -> ImageFont.FreeTypeFont:
    if index < 0:
        index = MINCHO_W6 if path == MINCHO else 0
    return ImageFont.truetype(path, size=size * SCALE, index=index)


def cover(path: Path, box: tuple[int, int], focus: float = 0.5) -> Image.Image:
    """箱を埋めるように写真を拡大して切り抜く。focus は縦の切り出し位置。"""
    im = Image.open(path).convert("RGB")
    bw, bh = box
    k = max(bw / im.width, bh / im.height)
    im = im.resize((max(bw, round(im.width * k)), max(bh, round(im.height * k))),
                   Image.Resampling.LANCZOS)
    x = (im.width - bw) // 2
    y = round((im.height - bh) * focus)
    return im.crop((x, y, x + bw, y + bh))


def darken(im: Image.Image, amount: float, saturation: float = 1.12) -> Image.Image:
    """白い見出しを乗せるぶんだけ落とす。色は少し上げて写真を死なせない。"""
    im = ImageEnhance.Color(im).enhance(saturation)
    return Image.blend(im, Image.new("RGB", im.size, INK), amount)


def side_scrim(im: Image.Image, align: str) -> Image.Image:
    """見出しが乗る側だけ、さらに暗いグラデーションを敷いて可読性を確保する。"""
    w, h = im.size
    grad = Image.new("L", (w, 1))
    px = grad.load()
    for x in range(w):
        t = x / (w - 1)
        if align == "right":
            t = 1 - t
        px[x, 0] = round(255 * max(0.0, 1 - t / 0.62) ** 1.5)
    mask = grad.resize((w, h))
    return Image.composite(Image.new("RGB", (w, h), INK), im, mask.point(lambda v: v * 0.80))


def text_with_shadow(d: ImageDraw.ImageDraw, xy, text, font, fill, layer,
                     blur: int = 12) -> None:
    """背景が明るくても沈まないよう、文字の下に薄い影を敷いてから本体を描く。"""
    shade = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    ImageDraw.Draw(shade).text(xy, text, font=font, fill=(4, 2, 4, 210))
    layer.alpha_composite(shade.filter(ImageFilter.GaussianBlur(blur * SCALE)))
    d.text(xy, text, font=font, fill=fill)


def tracked(d: ImageDraw.ImageDraw, xy, text, font, fill, tracking: float,
            anchor_right: float = None) -> float:
    """字間を開けて描く。anchor_right を渡すとその x で右揃えになる。"""
    widths = [d.textlength(c, font=font) for c in text]
    total = sum(widths) + tracking * SCALE * (len(text) - 1)
    x = (anchor_right - total) if anchor_right is not None else xy[0]
    for c, w in zip(text, widths):
        d.text((x, xy[1]), c, font=font, fill=fill)
        x += w + tracking * SCALE
    return total


def wrap(d: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont,
         limit: float) -> list[str]:
    """日本語なので単語で切れない。幅を見ながら1文字ずつ送って折り返す。

    行頭に来てはいけない約物（読点・句点・閉じ括弧）は前の行に残す。
    """
    forbidden = "、。」』）"
    lines, cur = [], ""
    for ch in text:
        if d.textlength(cur + ch, font=font) > limit and cur:
            if ch in forbidden:
                cur += ch
                lines.append(cur)
                cur = ""
                continue
            lines.append(cur)
            cur = ch
        else:
            cur += ch
    if cur:
        lines.append(cur)
    return lines


def faces_ground(box: tuple[int, int], names: tuple[str, ...]) -> Image.Image:
    """2段目の地。3人それぞれのライブ中の顔を横に並べ、背景に溶かし込む。

    枠に入れたカードだと「貼った画像」に見えるので、周囲を羽根ぼかしで
    落として地と一体にする。右側は見出しが乗るので、そこへ向けて消していく。
    帯いっぱいに1人を伸ばすと顔が寄りすぎるので、3人ぶんの帯は
    画面の3分の2に収めて、拡大率を 1.5 倍あたりに抑えている。
    """
    bw, bh = box
    ground = Image.new("RGB", box, INK)

    # 隣と重ねてから溶かすので、重なるぶんを足して1枚あたりの幅を決める
    strip = round(bw * 0.42)          # 3人ぶんの合計幅。帯が浅いので、
                                  # 幅で拡大率が決まると顔が寄りすぎる。
                                  # 高さ側で決まるところまで細くする
    n = len(names)
    col = round(strip / (n - (n - 1) * 0.30))
    seam = round(col * 0.30)

    # 左右のにじみ（横1行）と足元の沈み（縦1列）を作って掛け合わせる
    row = Image.new("L", (col, 1), 255)
    rp = row.load()
    for t in range(seam):
        v = round(255 * (t / seam) ** 0.75)
        rp[t, 0] = v
        rp[col - 1 - t, 0] = v
    fade = round(bh * 0.22)
    colm = Image.new("L", (1, bh), 255)
    cp = colm.load()
    for t in range(fade):
        cp[0, bh - 1 - t] = round(255 * (t / fade) ** 0.9)
    mask = ImageChops.multiply(row.resize((col, bh)), colm.resize((col, bh)))
    mask = mask.filter(ImageFilter.GaussianBlur(seam * 0.45))

    for i, name in enumerate(names):
        tile = cover(SRC / name, (col, bh), focus=0.12)
        tile = ImageEnhance.Color(tile).enhance(1.16)
        ground.paste(tile, (i * (col - seam), 0), mask)

    return ground


def draw_band(base: Image.Image, index: int, spec: dict) -> None:
    top = index * BAND * SCALE
    box = (SW, BAND * SCALE)

    if "faces" in spec:
        # 顔は背景として使うので、写真の段より一段深く沈める
        art = darken(faces_ground(box, spec["faces"]), 0.70, saturation=1.04)
        art = side_scrim(art, spec["align"])
    elif "photo" in spec:
        art = darken(cover(SRC / spec["photo"], box, spec.get("focus", 0.5)),
                     spec.get("dark", 0.52))
        art = side_scrim(art, spec["align"])
    else:
        # 写真を敷かない段。真っ黒だと右半分が抜けて見えるので、
        # 中央から外へ向かうクリムゾンの淡い滲みを1枚だけ置く。
        art = Image.new("RGB", box, INK)
        glow = Image.new("L", (box[0] // 8, box[1] // 8), 0)
        ImageDraw.Draw(glow).ellipse(
            (int(box[0] * 0.42 / 8), int(-box[1] * 0.30 / 8),
             int(box[0] * 1.16 / 8), int(box[1] * 1.05 / 8)), fill=70)
        glow = glow.resize(box, Image.Resampling.BILINEAR)
        glow = glow.filter(ImageFilter.GaussianBlur(170))
        art = Image.composite(Image.new("RGB", box, DEEPEST_CRIMSON), art, glow)
    base.paste(art, (0, top))

    layer = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)

    right = spec["align"] == "right"
    margin = 56 * SCALE
    x = (SW - margin) if right else margin
    y = top + 46 * SCALE

    # 欧文の小見出し。字間を開けた大文字で、上に細い罫を1本
    roman_f = face(DIDOT, 16)
    rw = tracked(d, (x, y), spec["roman"], roman_f, (236, 214, 214, 230), 11,
                 anchor_right=x if right else None)
    ry = y - 14 * SCALE
    if right:
        d.line((x - rw, ry, x - rw + 56 * SCALE, ry), fill=CRIMSON + (255,), width=3)
    else:
        d.line((x, ry, x + 56 * SCALE, ry), fill=CRIMSON + (255,), width=3)

    # 見出し本体
    label_f = face(MINCHO, 74)
    lw = d.textlength(spec["label"], font=label_f)
    ly = y + 32 * SCALE
    lx = (x - lw) if right else x
    text_with_shadow(d, (lx, ly), spec["label"], label_f, CREAM + (255,), layer, 16)

    # 説明文。ページ本文と同じ文言を、文字段の幅で折り返す
    limit = (860 if right else 1180) * SCALE
    copy_f = face(MINCHO, 21)
    cy = ly + 112 * SCALE
    for line in wrap(d, spec["copy"], copy_f, limit):
        lwx = d.textlength(line, font=copy_f)
        text_with_shadow(d, ((x - lwx) if right else x, cy), line, copy_f,
                         (243, 236, 226, 255), layer, 9)
        cy += 32 * SCALE

    # 補足の一行（事実の裏付け）。小さく、少し落とした色で
    note_f = face(SANS, 16)
    ny = cy + 6 * SCALE
    for line in wrap(d, spec["note"], note_f, limit):
        nwx = d.textlength(line, font=note_f)
        text_with_shadow(d, ((x - nwx) if right else x, ny), line, note_f,
                         (214, 200, 196, 235), layer, 7)
        ny += 24 * SCALE

    if spec.get("credit"):
        cf = face(SANS, 11)
        w = d.textlength(spec["credit"], font=cf)
        cxp, cyp = SW - margin - w, top + (BAND - 24) * SCALE
        text_with_shadow(d, (cxp, cyp), spec["credit"], cf,
                         (232, 220, 216, 185), layer, 5)

    base.alpha_composite(layer) if base.mode == "RGBA" else base.paste(
        Image.alpha_composite(base.convert("RGBA"), layer).convert("RGB"), (0, 0))


def main() -> None:
    base = Image.new("RGB", (SW, SH), INK)
    for i, spec in enumerate(BANDS):
        draw_band(base, i, spec)

    d = ImageDraw.Draw(base)
    for i in (1, 2):
        y = i * BAND * SCALE
        d.line((0, y, SW, y), fill=DEEPEST_CRIMSON, width=3)

    out = base.resize((W, H), Image.Resampling.LANCZOS)
    out.save(OUTPUT, quality=92, subsampling=0)
    print(f"{OUTPUT} | {out.size[0]}x{out.size[1]} | {OUTPUT.stat().st_size} bytes")


if __name__ == "__main__":
    main()
