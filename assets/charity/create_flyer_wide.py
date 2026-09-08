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


def add_people(base: Image.Image) -> Image.Image:
    """中央を大きく、左右を小さく下げて、中央へ視線が集まる形にする。

    3人の背後に白いもやを敷き、そのマスクを返す。
    呼び出し側はこのマスクでレーザーを弱め、人物の背後だけ光を止める。
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

    # 3人の背後に白いもや。人物のアルファを大きくぼかして作るので、
    # 四角い箱にならず、体の形に沿った光になる。
    haze = Image.new("L", (W, H), 0)
    for person, x, y in placed:
        layer = Image.new("L", (W, H), 0)
        layer.paste(person.getchannel("A"), (x, y))
        haze = ImageChops.lighter(haze, layer)
    haze = haze.filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(70))
    haze = haze.point(lambda v: min(255, round(v * 1.5)))

    white = Image.new("RGBA", (W, H), (246, 242, 244, 255))
    white.putalpha(haze.point(lambda v: round(v * 0.62)))
    base.alpha_composite(white)

    # 左右を先に、中央を最後に置いて、中央人物を視覚的な主役にする。
    for person, x, y in (placed[0], placed[2], placed[1]):
        base.alpha_composite(person, (x, y))
    return haze


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
    haze = add_people(canvas)

    # 人物の前にもレーザーを走らせる。ただし3人の背後のもやの上では
    # レーザーを止める。光の中に立っているように見せたいので、
    # そこだけ線が走らないほうが人物が浮き上がる。
    over = laser_layer((W, H), seed=4471, beams_per_side=11, gain=0.9)
    keep = ImageChops.invert(haze.point(lambda v: min(255, round(v * 1.25))))
    over = Image.merge("RGB", [ImageChops.multiply(ch, keep) for ch in over.split()])
    canvas = ImageChops.add(canvas.convert("RGB"), over).convert("RGBA")
    add_type(canvas)
    out = canvas.convert("RGB")
    out.save(OUTPUT, quality=92, subsampling=0, optimize=True)
    if out.size != (W, H):
        raise RuntimeError(f"出力サイズが不正です: {out.size}")
    if OUTPUT.stat().st_size > 2 * 1024 * 1024:
        raise RuntimeError(f"出力が2MBを超えています: {OUTPUT.stat().st_size} bytes")
    print(f"{OUTPUT} | {out.width}x{out.height} | {OUTPUT.stat().st_size} bytes")


if __name__ == "__main__":
    main()
