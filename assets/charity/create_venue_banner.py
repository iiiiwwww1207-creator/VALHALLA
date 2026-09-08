#!/usr/bin/env python3
"""イベント概要の章に置く、会場の告知画像を作る。

会場名はまだ公開できない（§6.5 の方針）ので、渋谷の夜景の上に
「近日公開予定」と置いて、隠しているのではなく引いている絵にする。

使い方: python3 assets/charity/create_venue_banner.py
出力  : assets/charity/venue_banner.jpg（1774x887）
"""
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFont

HERE = Path(__file__).resolve().parent
VENUE = HERE / "venue" / "shibuya_night.jpg"
OUTPUT = HERE / "venue_banner.jpg"

W, H = 1774, 887
BLACK = (5, 3, 7)
CRIMSON = (193, 18, 31)
CREAM = (245, 239, 228)
SILVER = (198, 198, 205)

MINCHO = "/System/Library/Fonts/ヒラギノ明朝 ProN.ttc"
MINCHO_W6 = 2
DIDOT = "/System/Library/Fonts/Supplemental/Didot.ttc"


def face(path: str, size: int, index: int = -1) -> ImageFont.FreeTypeFont:
    if index < 0:
        index = MINCHO_W6 if path == MINCHO else 0
    return ImageFont.truetype(path, size=size, index=index)


def tracked(draw, text, font, cy, fill, tracking):
    """字間を開けて中央に置く。欧文を締まって見せるための組み方。"""
    widths = [draw.textlength(c, font=font) for c in text]
    x = (W - (sum(widths) + tracking * (len(text) - 1))) / 2
    for c, w in zip(text, widths):
        draw.text((x, cy), c, font=font, fill=fill)
        x += w + tracking
    return x


def background() -> Image.Image:
    """渋谷の夜景。色は殺さず、文字が読むぶんだけ落とす。"""
    src = Image.open(VENUE).convert("RGB")
    scale = max(W / src.width, H / src.height)
    im = src.resize((round(src.width * scale), round(src.height * scale)),
                    Image.Resampling.LANCZOS)
    top = round((im.height - H) * 0.34)
    im = im.crop((0, top, W, top + H))
    im = ImageEnhance.Color(im).enhance(1.25)
    im = Image.blend(im, Image.new("RGB", im.size, BLACK), 0.35)

    # 四隅を落として中央に視線を集める
    vignette = Image.new("RGB", im.size, BLACK)
    mask = Image.new("L", im.size)
    px = mask.load()
    for y in range(H):
        dy = abs(y - H / 2) / (H / 2)
        for x in range(0, W, 2):
            dx = abs(x - W / 2) / (W / 2)
            v = round(255 * min(1.0, max(0.0, (max(dx, dy) - 0.42) / 0.58)) * 0.72)
            px[x, y] = v
            if x + 1 < W:
                px[x + 1, y] = v
    return Image.composite(vignette, im, mask)


def main() -> None:
    im = background()
    d = ImageDraw.Draw(im)

    # 「VENUE」は看板の上に乗ると沈むので、先に影を敷いてから描く
    for dx, dy, fill in ((3, 3, (6, 3, 6)), (0, 0, CREAM)):
        tracked(d, "VENUE", face(DIDOT, 36), 262 + dy, fill, 22)

    # 主役。「近日公開予定」を画面でいちばん大きい要素にする。
    head_f = face(MINCHO, 128)
    head = "近日公開予定"
    hw = sum(d.textlength(c, font=head_f) for c in head) + 22 * (len(head) - 1)
    # 影を敷いてから本体を描く。夜景のネオンの上でも沈まないように。
    for blur_pass in (4, 0):
        x = (W - hw) / 2
        for c in head:
            d.text((x + blur_pass, 372 + blur_pass), c, font=head_f,
                   fill=(6, 3, 6) if blur_pass else CREAM)
            x += d.textlength(c, font=head_f) + 22

    # 見出しの左右へ細い罫線を伸ばし、情報の塊として囲う
    rule_y = 372 + 128 // 2 + 8
    for x0, x1 in (((W - hw) / 2 - 190, (W - hw) / 2 - 56),
                   ((W + hw) / 2 + 56, (W + hw) / 2 + 190)):
        d.line((x0, rule_y, x1, rule_y), fill=(226, 200, 200), width=2)

    note_f = face(MINCHO, 34)
    note = "会場は東京・渋谷。詳細は追ってお知らせします。"
    d.text(((W - d.textlength(note, font=note_f)) / 2, 594), note,
           font=note_f, fill=(232, 214, 210))

    d.line((W / 2 - 60, 690, W / 2 + 60, 690), fill=CRIMSON, width=3)

    im.save(OUTPUT, quality=92, subsampling=0, optimize=True)
    print(f"{OUTPUT} | {im.width}x{im.height} | {OUTPUT.stat().st_size} bytes")


if __name__ == "__main__":
    main()
