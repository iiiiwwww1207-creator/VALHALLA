#!/usr/bin/env python3
"""CAMPFIRE のメインビジュアル（1920x1080）を組む。

主役は「VALHALLA CHARITY LIVE」の文字。その下に補足として
「文化 × エンタメ × AI」を置き、どちらも3人の頭の上にアーチ状に並べる。

人物は明度で判定せず、rembg のセマンティックなマットで白ホリゾントから
切り抜く。白い衣装を背景と取り違えないことが、この方法を使う理由。
"""
import math
import random

import cv2
import numpy as np
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
DIDOT_BOLD_INDEX = 2   # 日付だけ太いウェイトにして重さを出す


def face(path: str, size: int, index: int = -1) -> ImageFont.FreeTypeFont:
    if index < 0:
        index = MINCHO_W6 if path == MINCHO else 0
    return ImageFont.truetype(path, size=size, index=index)


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


def laser_layer(size: tuple[int, int], seed: int = 20261018,
                beams_per_side: int = 7, gain: float = 1.0) -> Image.Image:
    """黒地に赤いレーザーだけを描いた層を返す。

    背景に加算するのにも、白ホリゾントを塗り替えるのにも使う。
    """
    rnd = random.Random(seed)
    core = Image.new("RGB", size, (0, 0, 0))
    glow = Image.new("RGB", size, (0, 0, 0))
    dc, dg = ImageDraw.Draw(core), ImageDraw.Draw(glow)
    w, h = size
    beams = []
    for _ in range(beams_per_side):
        x0 = rnd.randint(round(-w * 0.26), round(w * 0.47))
        x1 = x0 + rnd.randint(round(w * 0.78), round(w * 1.35))
        y0 = rnd.randint(round(-h * 0.15), round(h * 0.48))
        y1 = y0 + rnd.randint(round(h * 0.22), round(h * 0.70))
        beams.append((x0, y0, x1, y1, rnd.uniform(0.45, 1.0) * gain,
                      rnd.choice((1, 2, 2, 3)), rnd.choice((10, 16, 22))))
    beams += [(w - x0, y0, w - x1, y1, b, cw, gw)
              for x0, y0, x1, y1, b, cw, gw in beams]
    for x0, y0, x1, y1, bright, cw, gw in beams:
        b = min(1.0, bright)
        dc.line((x0, y0, x1, y1),
                fill=(round(255 * b), round(32 * b), round(54 * b)), width=cw)
        dg.line((x0, y0, x1, y1), fill=(round(150 * b), 12, 22), width=gw)
    return ImageChops.add(glow.filter(ImageFilter.GaussianBlur(26)),
                          core.filter(ImageFilter.GaussianBlur(1.2)))


def add_lasers(base: Image.Image) -> Image.Image:
    """背景にレーザーを加算する。加算なので光が「発している」ように見える。"""
    return ImageChops.add(base.convert("RGB"), laser_layer((W, H)))


CUTOUT = HERE / "members_cutout.png"   # rembg で人物だけを抜いたもの


def refine_edges(rgba: Image.Image) -> Image.Image:
    """縁に残る白ホリゾントの色を取り除き、輪郭を締める。

    半透明の縁は「人物の色」と「背景の白」が混ざった状態なので、
    背景ぶんを引き算して人物本来の色に戻す。これをやらないと、
    暗い渋谷の上に置いたとき縁が白く光って切り抜き感が出る。
    """
    raw = np.asarray(rgba).copy()

    # 輪郭のギザつきを均す。
    # 左の2人は黒衣装なので背景との明度差が64あり、境界がはっきり出る。
    # レイは白衣装で差が7しかなく、判定が揺れて縁がギザつく。
    # 真の輪郭は滑らかな服の線なので、点状のノイズを中央値で消し、
    # 開閉で トゲと欠けを均し、ぼかしてから閾値で戻して曲線にする。
    alpha = cv2.medianBlur(raw[:, :, 3], 9)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11))
    alpha = cv2.morphologyEx(alpha, cv2.MORPH_CLOSE, kernel)
    alpha = cv2.morphologyEx(alpha, cv2.MORPH_OPEN, kernel)
    alpha = cv2.GaussianBlur(alpha, (0, 0), 2.8)
    alpha = np.clip((alpha.astype(np.float32) - 118) * 5.0 + 128, 0, 255)
    raw[:, :, 3] = alpha.astype(np.uint8)

    arr = raw.astype(np.float32)
    a = arr[:, :, 3:4] / 255.0
    bg = np.array([244.0, 244.0, 244.0], np.float32)   # 白ホリゾントの実測値
    clean = np.clip((arr[:, :, :3] - (1 - a) * bg) / np.clip(a, 0.18, 1.0), 0, 255)
    # ごく薄い縁は背景側とみなして落とす（輪郭の締め）
    tight = np.clip((a - 0.14) / (1 - 0.14), 0, 1)
    out = np.concatenate([clean, tight * 255], axis=2).astype(np.uint8)
    return Image.fromarray(out).convert("RGBA")


def cutouts() -> list[Image.Image]:
    """3人を1人ずつ、シルエットどおりに切り出して返す（左から順）。

    白ホリゾント撮影のため、明度や輪郭で抜くと白スーツ（明度251）が
    白背景（242）より明るく、必ず一緒に消える。そこで rembg（U2Net）で
    意味的に抜く。モデルは手元にあるのでオフラインで動く。

    ただし U2Net は入力を 320x320 に縮めて判定するので、幅1600の写真を
    そのまま渡すとマスクが粗くなり、袖や手が塊に潰れる。
    そこで **1人ずつ切り出してから個別にかける**。1人あたりの実効解像度が
    3倍以上になり、輪郭がシルエットどおりに出る。
    """
    from rembg import remove, new_session
    # 人物専用に学習された u2net_human_seg を使う。汎用 u2net と
    # isnet-general-use とレイ（白スーツ）で比較したところ、
    # 縁のノイズが最も少なく、ジャケットの線どおりに抜けた。
    session = new_session("u2net_human_seg")

    def cut(img: Image.Image) -> Image.Image:
        # alpha matting は元画像の色を手がかりに境界を引き直す処理。
        # これが無いとマスクが丸く鈍る。
        return remove(img, session=session, alpha_matting=True,
                      alpha_matting_foreground_threshold=250,
                      alpha_matting_background_threshold=15,
                      alpha_matting_erode_size=12)

    src = Image.open(MEMBERS).convert("RGB")

    # 1回目：全体をざっくり抜いて、3人の位置を掴む
    rough = np.asarray(cut(src))[:, :, 3]
    n, labels, stats, _ = cv2.connectedComponentsWithStats(
        (rough >= 16).astype(np.uint8), connectivity=8)
    order = sorted(range(1, n), key=lambda i: -stats[i, cv2.CC_STAT_AREA])[:3]
    if len(order) != 3:
        raise RuntimeError(f"人物の連結成分が3個見つかりません: {len(order)}個")
    order.sort(key=lambda i: stats[i, cv2.CC_STAT_LEFT])

    # 2回目：1人ずつ、余白をつけて切り出してから高解像度で抜き直す
    people = []
    for number, i in enumerate(order, start=1):
        x, y = stats[i, cv2.CC_STAT_LEFT], stats[i, cv2.CC_STAT_TOP]
        w, h = stats[i, cv2.CC_STAT_WIDTH], stats[i, cv2.CC_STAT_HEIGHT]
        pad = 40
        box = (max(0, x - pad), max(0, y - pad),
               min(src.width, x + w + pad), min(src.height, y + h + pad))
        one = refine_edges(cut(src.crop(box)))
        one = one.crop(one.getbbox())
        people.append(one)
        opaque = int((np.asarray(one)[:, :, 3] > 128).sum())
        print(f"人物{number}: {one.size[0]}x{one.size[1]} / 不透明 {opaque:,}px")

    # 右の人物（白スーツ）が消えていないことを確認する。
    right = np.asarray(people[2])
    lum = cv2.cvtColor(right[:, :, :3], cv2.COLOR_RGB2GRAY)
    solid = right[:, :, 3] > 128
    white = int(np.count_nonzero(solid & (lum >= 235)))
    ratio = white / max(1, int(solid.sum()))
    print(f"右メンバー白スーツ検証: 高明度かつ不透明 {white:,}px ({ratio:.1%})")
    if ratio < 0.30:
        raise RuntimeError("右メンバーの白スーツが十分に残っていません")
    return people


def add_people(base: Image.Image):
    """中央を大きく、左右を小さく下げて、中央へ視線が集まる形にする。

    ここでは背後のもやまでを描き、(配置, もやのマスク, シルエット) を返す。
    人物そのものは paste_people で最後に貼る。文字より後に貼ることで、
    文字が人物にかからない（人物が手前に立つ）。
    """
    people = cutouts()
    base_y = 968                                   # 足元をそろえる高さ
    plan = ((0, 0.52, -420), (1, 0.62, 0), (2, 0.52, 420))
    placed = []
    for idx, ratio, dx in plan:
        person = people[idx]
        ph = round(H * ratio)
        pw = round(person.width * ph / person.height)
        person = person.resize((pw, ph), Image.Resampling.LANCZOS)
        x = W // 2 + dx - pw // 2
        y = base_y - ph
        placed.append((person, x, y))

    # 足元にごく淡い影。人物より先に一枚の層で敷き、互いを暗くしない。
    shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    for person, x, _ in placed:
        half_width = round(person.width * 0.36)
        center_x = x + person.width // 2
        shadow_draw.ellipse(
            (center_x - half_width, base_y - 48,
             center_x + half_width, base_y - 16),
            fill=(0, 0, 0, 68))
    base.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(18)))

    # 3人のシルエットを1枚にまとめる。もやの元にも、
    # レーザーを止める範囲にも使う。
    solid = Image.new("L", (W, H), 0)
    for person, x, y in placed:
        layer = Image.new("L", (W, H), 0)
        layer.paste(person.getchannel("A"), (x, y))
        solid = ImageChops.lighter(solid, layer)

    # 背後のもやは、そのシルエットを大きくぼかして作る。
    # 四角い箱にならず、体の形に沿った光になる。
    haze = solid.filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(70))
    haze = haze.point(lambda v: min(255, round(v * 1.5)))

    white = Image.new("RGBA", (W, H), (246, 242, 244, 255))
    white.putalpha(haze.point(lambda v: round(v * 0.62)))
    base.alpha_composite(white)

    return placed, haze, solid


def paste_people(base: Image.Image, placed) -> None:
    """左右を先に、中央を最後に置いて、中央人物を視覚的な主役にする。"""
    for person, x, y in (placed[0], placed[2], placed[1]):
        base.alpha_composite(person, (x, y))


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

    # 2行とも、弧を浅くして横の余白まで使い切る。半径を大きくすると
    # 弧は平たくなり、同じ文字量でも横に伸びて上への張り出しが減る。
    # 半径を揃えてあるので、2行の間隔は端まで一定に保たれる。
    #
    #   R = 4600 / 字間で幅を作る / 頂点 y は下の実測値から決めた
    #     Didot 104 …… 弧の点から見て 上 45px・下 33px にインクが乗る
    #     明朝  100 …… 同じく 上 63px・下 32px
    #
    ARC_R = 4600

    # 主役：イベント名。頂点 78 → インクの上端 33 で、天地とも切れない。
    arc_text(base, "VALHALLA CHARITY LIVE", face(DIDOT, 104), CREAM + (255,),
             W // 2, 78 + ARC_R, ARC_R, tracking=18)

    # 3語。イベント名と同じ大きさのまま、字間だけ開けて横幅を稼ぐ。
    # 頂点 209 → インク下端 241。いちばん高い頭（y≈298）まで 57px 空く。
    arc_text(base, "文化 × エンタメ × AI", face(MINCHO, 100), CREAM + (255,),
             W // 2, 209 + ARC_R, ARC_R, tracking=52)


def add_band(base: Image.Image) -> None:
    """最下部の帯。人物より前に描いて、日付と寄付の一行を必ず読ませる。

    組み方は、支援を集めているクラウドファンディングのヘッダーを参考にした。
    ・細い罫線で情報の塊を囲い、帯を「デザインされた面」に見せる
    ・欧文は字間を大きく開けた小さめの大文字で、締まった印象をつくる
    ・日付は大きく置く。数字は一瞬で読めるので、いちばん効く情報
    """
    d = ImageDraw.Draw(base)
    band = H - 224
    d.rectangle((0, band, W, H), fill=DEEPEST_CRIMSON + (255,))

    line = (232, 206, 206, 90)
    d.line((0, band, W, band), fill=(236, 210, 210, 200), width=2)

    # ① 字間を開けた欧文の小見出し
    eyebrow_f = face(DIDOT, 25)
    eyebrow = "VALHALLA CHARITY LIVE"
    ew = sum(d.textlength(c, font=eyebrow_f) for c in eyebrow) + 13 * (len(eyebrow) - 1)
    x = (W - ew) / 2
    for c in eyebrow:
        d.text((x, band + 26), c, font=eyebrow_f, fill=(238, 214, 214, 235))
        x += d.textlength(c, font=eyebrow_f) + 13
    # 小見出しの左右に細い罫線を伸ばす
    d.line((W / 2 - ew / 2 - 130, band + 40, W / 2 - ew / 2 - 34, band + 40),
           fill=line, width=1)
    d.line((W / 2 + ew / 2 + 34, band + 40, W / 2 + ew / 2 + 130, band + 40),
           fill=line, width=1)

    # ② 日付。数字を大きく、字間を開けて置く
    date_f = face(DIDOT, 84, DIDOT_BOLD_INDEX)
    date_t = "2026.10.18"
    dw = sum(d.textlength(c, font=date_f) for c in date_t) + 5 * (len(date_t) - 1)
    sun_f = face(DIDOT, 42, DIDOT_BOLD_INDEX)
    sun_t = "SUN"
    sw = sum(d.textlength(c, font=sun_f) for c in sun_t) + 8 * (len(sun_t) - 1)
    place_f = face(MINCHO, 38)
    place_t = "渋谷"
    pw = d.textlength(place_t, font=place_f)

    gap, rule_gap = 30, 34
    total = dw + gap + sw + rule_gap * 2 + 1 + pw
    x = (W - total) / 2
    for c in date_t:
        d.text((x, band + 62), c, font=date_f, fill=CREAM + (255,))
        x += d.textlength(c, font=date_f) + 5
    x += gap - 5
    for c in sun_t:
        d.text((x, band + 98), c, font=sun_f, fill=(238, 214, 214, 255))
        x += d.textlength(c, font=sun_f) + 8
    x += rule_gap - 8
    d.line((x, band + 72, x, band + 136), fill=line, width=1)   # 縦の区切り罫
    x += rule_gap
    d.text((x, band + 90), place_t, font=place_f, fill=CREAM + (255,))

    # ③ 寄付の一行。ここだけ和文で、静かに置く
    note = "収益から必要経費を差し引いた全額を、然るべき団体へ寄付します"
    nf = face(MINCHO, 27)
    d.text(((W - d.textlength(note, font=nf)) / 2, band + 178), note, font=nf,
           fill=(236, 214, 214, 235))


def main() -> None:
    canvas = add_lasers(background()).convert("RGBA")
    placed, haze, solid = add_people(canvas)

    # 文字を先に描き、そのあとに人物を貼る。こうすると文字が
    # 人物の上に乗らず、3人が文字の手前に立っているように見える。
    add_type(canvas)
    paste_people(canvas, placed)
    add_band(canvas)

    # 人物の前にもレーザーを走らせる。ただし
    #   ・3人の体の上には一切かけない（シルエットで完全に止める）
    #   ・その背後のもやの上でも弱める
    # 顔や衣装に線が乗ると、切り抜いた人物が背景に沈んで見えるため。
    over = laser_layer((W, H), seed=4471, beams_per_side=11, gain=0.9)
    block = ImageChops.lighter(
        solid.filter(ImageFilter.MaxFilter(7)).filter(ImageFilter.GaussianBlur(3)),
        haze.point(lambda v: min(255, round(v * 1.25))))
    keep = ImageChops.invert(block)
    over = Image.merge("RGB", [ImageChops.multiply(ch, keep) for ch in over.split()])
    canvas = ImageChops.add(canvas.convert("RGB"), over).convert("RGBA")
    out = canvas.convert("RGB")
    out.save(OUTPUT, quality=92, subsampling=0, optimize=True)
    if out.size != (W, H):
        raise RuntimeError(f"出力サイズが不正です: {out.size}")
    if OUTPUT.stat().st_size > 2 * 1024 * 1024:
        raise RuntimeError(f"出力が2MBを超えています: {OUTPUT.stat().st_size} bytes")
    print(f"{OUTPUT} | {out.width}x{out.height} | {OUTPUT.stat().st_size} bytes")


if __name__ == "__main__":
    main()
