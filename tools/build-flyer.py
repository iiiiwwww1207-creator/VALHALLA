#!/usr/bin/env python3
"""新版フライヤー（デザイナー支給PDF）の文言を差し替える。

元の PDF は文字がベクターで、1行が「同じ Tm を持つ小さな BT...ET ブロック群」
として描かれている。差し替えたい行は Tm の y 座標で特定してブロックごと削除し、
同じ位置に新しい文字を重ねる。背景写真・ロゴ・QR には一切触らない。

座標: 外側 cm が .24 倍・y反転、内側が 3.125 倍。よって
      device_x = 0.75 * content_x / device_y = 841.92 - 0.75 * content_y

使い方: python3 tools/build-flyer.py
"""
import io
import os
import re
import subprocess
import tempfile

from PIL import Image, ImageDraw, ImageFont
from pypdf import PdfReader, PdfWriter
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

SRC = "assets/charity/flyer_fusion_source.pdf"
OUT = "assets/charity/flyer_fusion_fixed.pdf"
OUT_PNG = "assets/charity/flyer_fusion_fixed.png"
MINCHO = "/System/Library/Fonts/ヒラギノ明朝 ProN.ttc"
MINCHO_INDEX = 0  # Hiragino Mincho ProN W3
PW, PH = 594.96, 841.92
S = 6  # 描画倍率

# 消す行：Tm の y（content 座標）と、その行の文字サイズ
DROP_LINES = {763.0, 998.0, 1021.0, 1045.0, 1107.0, 0.0}
DROP_SIZES = {12.85, 14.74, 9.82, 7.18}
# 「（案内準備中）」に引かれていた赤い破線。文字を消すと下線だけ残るので一緒に消す。
UNDERLINE = re.compile(r"563 1109 m\n(?:[-\d.]+ [-\d.]+ [ml]\n)+f\n")

CENTER = 301.5   # 下段まんなかの「Charity」欄の中心
CREAM = (243, 237, 225)
WHITE = (255, 255, 255)
NOTE = (177, 173, 165)
FOOT = (108, 104, 100)

# (中央x または None, ベースラインy, 文字, サイズ, 色, 字間比)
DRAW = [
    # CAMPFIRE 帯：「クラウドファンディングにて 後日公開」を差し替える
    (297.5, 269.7, "お申し込みは CAMPFIRE にて", 9.64, CREAM, 0.06),
    # 寄付の文言。ページ・CAMPFIRE と同じ言い回しに揃える。
    (CENTER, 93.4, "収益から必要経費を差し引いた", 11.05, WHITE, 0.05),
    (CENTER, 76.2, "全額を然るべき団体へ寄付します", 11.05, WHITE, 0.05),
    (CENTER, 58.2, "※必要経費には、会場費・出演料・機材費・決済手数料が含まれます。",
     6.6, NOTE, 0.0),
    (CENTER, 47.0, "寄付先の団体名、寄付金額は開催後にご報告します。", 6.6, NOTE, 0.0),
]
FOOTER = ("主催：VALHALLA ／ 昼の本編「WRAPPING THE EARTH TOKYO 2026」"
          "主催：公益財団法人クロノス保全財団。お申し込みは CAMPFIRE にて。"
          "特定商取引法に基づく表記は特設ページに掲載します。")
FOOTER_X, FOOTER_Y, FOOTER_SIZE, FOOTER_MAX = 39.7, 11.7, 5.38, 515.0


def strip(data: bytes) -> bytes:
    s = data.decode("latin-1")
    kept, last, removed = [], 0, 0
    for m in re.finditer(r"BT.*?ET", s, re.S):
        b = m.group(0)
        tm = re.search(r"[-\d.]+ [-\d.]+ [-\d.]+ [-\d.]+ [-\d.]+ ([-\d.]+) Tm", b)
        tf = re.search(r"/\w+ ([\d.]+) Tf", b)
        if not (tm and tf):
            continue
        if round(float(tm.group(1)), 1) in DROP_LINES and \
                round(float(tf.group(1)), 2) in DROP_SIZES:
            kept.append(s[last:m.start()])
            last = m.end()
            removed += 1
    kept.append(s[last:])
    s = "".join(kept)
    s, n = UNDERLINE.subn("", s)
    print(f"  文字ブロック {removed} 個 / 破線 {n} 本を削除")
    return s.encode("latin-1")


def draw_tracked(d, font, text, cx, baseline, color, tracking):
    """字間を足しつつ、中央そろえでベースラインに置く"""
    extra = font.size * tracking
    width = sum(font.getlength(c) for c in text) + extra * (len(text) - 1)
    x = cx * S - width / 2
    for c in text:
        d.text((x, baseline), c, font=font, fill=color, anchor="ls")
        x += font.getlength(c) + extra


def overlay() -> bytes:
    img = Image.new("RGBA", (int(PW * S), int(PH * S)), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    for cx, dy, text, size, color, tracking in DRAW:
        font = ImageFont.truetype(MINCHO, round(size * S), index=MINCHO_INDEX)
        draw_tracked(d, font, text, cx, (PH - dy) * S, color, tracking)

    # フッターは左そろえ。1行に収まらなければサイズを詰める。
    size = FOOTER_SIZE
    while size > 3.5:
        font = ImageFont.truetype(MINCHO, round(size * S), index=MINCHO_INDEX)
        if font.getlength(FOOTER) <= FOOTER_MAX * S:
            break
        size -= 0.1
    d.text((FOOTER_X * S, (PH - FOOTER_Y) * S), FOOTER, font=font,
           fill=FOOT, anchor="ls")
    print(f"  フッター {size:.1f}pt / 幅 {font.getlength(FOOTER)/S:.0f}pt")

    buf = io.BytesIO()
    img.save(buf, "PNG")
    return buf.getvalue()


def main() -> None:
    writer = PdfWriter(clone_from=SRC)
    page = writer.pages[0]
    contents = page.get_contents()
    contents.set_data(strip(contents.get_data()))
    page.replace_contents(contents)

    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(PW, PH))
    c.drawImage(ImageReader(io.BytesIO(overlay())), 0, 0, PW, PH, mask="auto")
    c.save()
    buf.seek(0)
    page.merge_page(PdfReader(buf).pages[0])

    with open(OUT, "wb") as fh:
        writer.write(fh)

    # SNS 用のラスタも作る。PDF を描画できるのは macOS の qlmanage なのでそれを使う。
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(["qlmanage", "-t", "-s", "2480", "-o", tmp, OUT],
                       capture_output=True, check=False)
        made = os.path.join(tmp, os.path.basename(OUT) + ".png")
        if os.path.exists(made):
            Image.open(made).convert("RGB").save(OUT_PNG)
            print(f"{OUT_PNG} {Image.open(OUT_PNG).size}")
        else:
            print("警告: PNG を描画できなかった（qlmanage が失敗）")
    print(OUT)


if __name__ == "__main__":
    main()
