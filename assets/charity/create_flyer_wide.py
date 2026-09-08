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
import random
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter, ImageFont

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

# 3人が元写真（幅1600）で占める範囲。ここは透過をかけずに守る。
PEOPLE_X = ((150, 520), (585, 1000), (1105, 1520))

MINCHO = "/System/Library/Fonts/ヒラギノ明朝 ProN.ttc"
MINCHO_W6 = 2
DIDOT = "/System/Library/Fonts/Supplemental/Didot.ttc"


def face(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size=size,
                              index=MINCHO_W6 if path == MINCHO else 0)


def background() -> Image.Image:
    """渋谷の夜景を、色を殺さずに敷く。

    以前は全体にクリムゾンを重ねて画面を赤くしていたが、それだと
    ネオンの青・緑・黄が死んで、写真がただの赤い面になってしまう。
    ここでは彩度を上げたうえで、文字が読むぶんだけ暗く落とす。
    """
    venue = Image.open(VENUE).convert("RGB")
    scale = max(W / venue.width, H / venue.height)
    venue = venue.resize((round(venue.width * scale), round(venue.height * scale)),
                         Image.Resampling.LANCZOS)
    im = venue.crop((0, 0, W, H))
    im = ImageEnhance.Color(im).enhance(1.35)      # ネオンの色を立たせる
    im = ImageEnhance.Contrast(im).enhance(1.08)
    im = Image.blend(im, Image.new("RGB", im.size, BLACK), 0.34)  # 可読性のぶんだけ
    return im


def laser_layer(size: tuple[int, int], seed: int = 20261018) -> Image.Image:
    """黒地に赤いレーザーだけを描いた層を返す。

    背景に加算するのにも、白ホリゾントを塗り替えるのにも使う。
    """
    rnd = random.Random(seed)
    core = Image.new("RGB", size, (0, 0, 0))
    glow = Image.new("RGB", size, (0, 0, 0))
    dc, dg = ImageDraw.Draw(core), ImageDraw.Draw(glow)
    w, h = size
    beams = []
    for _ in range(7):
        x0 = rnd.randint(round(-w * 0.26), round(w * 0.47))
        x1 = x0 + rnd.randint(round(w * 0.78), round(w * 1.35))
        y0 = rnd.randint(round(-h * 0.15), round(h * 0.48))
        y1 = y0 + rnd.randint(round(h * 0.22), round(h * 0.70))
        beams.append((x0, y0, x1, y1, rnd.uniform(0.45, 1.0),
                      rnd.choice((1, 2, 2, 3)), rnd.choice((10, 16, 22))))
    beams += [(w - x0, y0, w - x1, y1, b, cw, gw)
              for x0, y0, x1, y1, b, cw, gw in beams]
    for x0, y0, x1, y1, bright, cw, gw in beams:
        dc.line((x0, y0, x1, y1),
                fill=(round(255 * bright), round(32 * bright), round(54 * bright)),
                width=cw)
        dg.line((x0, y0, x1, y1), fill=(round(150 * bright), 12, 22), width=gw)
    return ImageChops.add(glow.filter(ImageFilter.GaussianBlur(26)),
                          core.filter(ImageFilter.GaussianBlur(1.2)))


def add_lasers(base: Image.Image) -> Image.Image:
    """赤いレーザーを斜めに走らせる。

    細い芯と、それを大きくぼかしたグローを別々に描き、加算で重ねる。
    加算にすると下の夜景の明るさに足し算されるので、光が「乗っている」
    のではなく「発している」ように見える。
    本数・太さ・明るさをばらけさせて、等間隔の機械的な線にしない。
    """
    rnd = random.Random(20261018)                  # 毎回同じ絵になるよう種を固定
    core = Image.new("RGB", (W, H), (0, 0, 0))
    glow = Image.new("RGB", (W, H), (0, 0, 0))
    dc, dg = ImageDraw.Draw(core), ImageDraw.Draw(glow)

    beams = []
    for _ in range(7):
        # 左上から右下へ抜ける斜めの線。角度と位置をばらす。
        x0 = rnd.randint(-500, 900)
        x1 = x0 + rnd.randint(1500, 2600)
        y0 = rnd.randint(-160, 520)
        y1 = y0 + rnd.randint(240, 760)
        beams.append((x0, y0, x1, y1, rnd.uniform(0.45, 1.0),
                      rnd.choice((1, 2, 2, 3)), rnd.choice((10, 16, 22))))
    # 同じ本数を、左右対称の角度で右側からも入れる。
    # 片側だけだと画面が傾いて見え、ロゴのある左側に光が乗らない。
    beams += [(W - x0, y0, W - x1, y1, b, cw, gw)
              for x0, y0, x1, y1, b, cw, gw in beams]
    for x0, y0, x1, y1, bright, cw, gw in beams:
        red = (round(255 * bright), round(32 * bright), round(54 * bright))
        dc.line((x0, y0, x1, y1), fill=red, width=cw)
        dg.line((x0, y0, x1, y1), fill=(round(150 * bright), 12, 22), width=gw)

    glow = glow.filter(ImageFilter.GaussianBlur(26))
    core = core.filter(ImageFilter.GaussianBlur(1.2))
    lit = ImageChops.add(base.convert("RGB"), glow)
    return ImageChops.add(lit, core)


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
    rgb = panel.convert("RGB")
    lum = rgb.convert("L")

    # 白ホリゾントの明るい画素を拾う重み
    weight = lum.point(lambda v: 0 if v < 224 else min(255, round((v - 224) * 255 / 30)))
    weight = weight.filter(ImageFilter.GaussianBlur(3))

    # 3人が立っている列は守る。明るさだけで処理すると、
    # レイの白スーツ（背景より明るい）が背景と一緒に消えてしまうため。
    protect = Image.new("L", rgb.size, 0)
    pd = ImageDraw.Draw(protect)
    sx, sy = rgb.size[0] / 1600, rgb.size[1] / 1066
    # 守るのは人物が実際にいる範囲だけ。頭より上まで守ると、
    # そこに白ホリゾントの白が帯として残ってしまう。
    # 楕円で描いてから大きくぼかす。四角のまま使うと、
    # 守った範囲が「白い箱」として見えてしまう。
    for x0, x1 in PEOPLE_X:
        cx = (x0 + x1) / 2 * sx
        half = (x1 - x0) / 2 * sx * 0.92
        pd.ellipse((cx - half, 210 * sy, cx + half, rgb.size[1] + 260 * sy), fill=255)
    protect = protect.filter(ImageFilter.GaussianBlur(62))
    fade = ImageChops.multiply(weight, ImageChops.invert(protect))

    # 白ホリゾントを「透かす」と、レイの白スーツ（背景より明るい）まで
    # 必ず一緒に消える。そこで透かすのをやめ、**赤いレーザーの面に塗り替える**。
    # 列の中は塗り替えないので、レイのスーツは白のまま残る。
    tint = Image.new("RGB", rgb.size, (26, 20, 24))
    rgb = Image.composite(Image.blend(rgb, tint, 0.30), rgb, weight)   # 白地を少し落とす
    field = ImageChops.add(Image.new("RGB", rgb.size, (18, 10, 14)),
                           laser_layer(rgb.size, seed=778))
    rgb = Image.composite(field, rgb, fade)                            # 列の外を赤い面に

    # 白スーツは陰影が浅い。コントラストを上げて襟や折り目を出さないと、
    # まわりの明るい面と一体化して形が読めない。
    rgb = ImageEnhance.Contrast(rgb).enhance(1.30)
    rgb = ImageEnhance.Color(rgb).enhance(1.14)

    panel = rgb.convert("RGBA")
    # 明るさによる透過はもう使わない（レイのスーツが消えるため）。
    see_through = Image.new("L", rgb.size, 255)
    # 縁のフェードは人物には効かせない。パネルの右端フェード帯に
    # レイの体がまるごと入っていて、それが透けの主因だった。
    edge = ImageChops.lighter(mask.filter(ImageFilter.GaussianBlur(12)), protect)
    alpha = ImageChops.multiply(edge, see_through)
    panel.putalpha(alpha)
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
        # 背景のネオンが明るいと文字が沈むので、先に淡い影を敷いてから本体を描く
        shade = Image.new("RGBA", glyph.size, (0, 0, 0, 0))
        ImageDraw.Draw(shade).text((30, 20), ch, font=font, fill=(8, 4, 8, 215))
        glyph.alpha_composite(shade.filter(ImageFilter.GaussianBlur(10)))
        glyph.alpha_composite(shade.filter(ImageFilter.GaussianBlur(4)))
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
    canvas = add_lasers(background()).convert("RGBA")
    panel = members_panel()
    canvas.alpha_composite(panel, ((W - panel.width) // 2, 232))
    add_type(canvas)
    out = canvas.convert("RGB")
    out.save(OUTPUT, quality=92, subsampling=0, optimize=True)
    print(f"{OUTPUT} | {out.width}x{out.height} | {OUTPUT.stat().st_size} bytes")


if __name__ == "__main__":
    main()
