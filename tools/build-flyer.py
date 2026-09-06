#!/usr/bin/env python3
"""公式フライヤーの文言差し替えを、元画像から毎回やり直す形で行う。

なぜ毎回やり直すのか:
  差し替えは「消したい行を、近くの空白帯からコピーして塗り潰す」方式で行う。
  一度書き込んだ画像を次の差し替えの入力にすると、直前に描いた文字が
  空白帯に含まれてしまい、複製されて二重になる事故が起きる。
  そのため常に元画像 SRC から始めて、全ての差し替えを順に適用する。

使い方: python3 tools/build-flyer.py
出力  : assets/charity/flyer_fusion_fixed.png / .pdf
"""
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import os

SRC = os.path.expanduser("~/Downloads/flyer_fusion.png")
OUT_PNG = "assets/charity/flyer_fusion_fixed.png"
OUT_PDF = "assets/charity/flyer_fusion_fixed.pdf"
MINCHO = "/System/Library/Fonts/ヒラギノ明朝 ProN.ttc"


def ink_offset(font: ImageFont.FreeTypeFont, sample: str) -> int:
    """draw.text の y と、実際にインクが乗り始める y の差"""
    probe = Image.new("L", (600, 200), 0)
    ImageDraw.Draw(probe).text((10, 10), sample, font=font, fill=255)
    return probe.getbbox()[1] - 10


def main() -> None:
    im = Image.open(SRC).convert("RGB")
    W, H = im.size
    a = np.asarray(im).copy()

    def wipe(y0, y1, x0, x1, sy0, sy1):
        """y0..y1 を、sy0..sy1 の空白帯で塗り潰す"""
        band = a[sy0:sy1, x0:x1].copy()
        bh = band.shape[0]
        for i, y in enumerate(range(y0, y1)):
            a[y, x0:x1] = band[i % bh]

    # 元画像で完全に空白であることを実測済みの帯だけを複製元に使う
    wipe(2044, 2096, 720, 1675, 1988, 2044)     # サブコピー
    wipe(3028, 3092, 1090, 1600, 2992, 3032)    # チャリティー欄 1行目
    wipe(3096, 3160, 1080, 1600, 2992, 3032)    # チャリティー欄 2行目
    wipe(3180, 3230, 980, 1710, 2992, 3032)     # チャリティー欄 注記
    wipe(3228, H, 0, W, 3233, 3294)             # フッター全体

    img = Image.fromarray(a)
    d = ImageDraw.Draw(img)

    # --- サブコピー（元と同じ 幅917px / 字間 / 装飾罫は残す）---
    f = ImageFont.truetype(MINCHO, 34)
    text = "アコースティックライブ ＆ スペシャルタイム"
    track = (917 - sum(f.getlength(c) for c in text)) / (len(text) - 1)
    x = 734.0
    for c in text:
        d.text((x, 2050 - ink_offset(f, "ア")), c, font=f, fill=(206, 180, 118))
        x += f.getlength(c) + track

    # --- チャリティー欄（中央揃え・元と同じ位置と色）---
    CX = 1341
    for txt, size, top, color in [
        ("経費を除いた収益の", 45, 3040, (224, 224, 224)),
        ("全額を寄付します", 45, 3108, (213, 192, 141)),
        ("寄付先・寄付金額は開催後に本ページにて報告します", 29, 3192, (151, 147, 139)),
    ]:
        ff = ImageFont.truetype(MINCHO, size)
        d.text((CX - ff.getlength(txt) / 2, top - ink_offset(ff, "寄")), txt, font=ff, fill=color)

    # --- フッター ---
    ff = ImageFont.truetype(MINCHO, 20)
    paras = [
        "本イベントの収益から必要経費を差し引いた全額を、然るべき団体へ寄付いたします。"
        "※必要経費には、会場費・出演料・機材費・決済手数料が含まれます。"
        "寄付先の団体名、寄付金額は開催後、本ページにて報告いたします。",
        "主催：VALHALLA ／ 昼の本編「WRAPPING THE EARTH TOKYO 2026」。"
        "お申し込みは CAMPFIRE にて受付予定（案内準備中）。特定商取引法に基づく表記は特設ページに掲載します。",
    ]
    lines = []
    for t in paras:
        cur = ""
        for ch in t:
            if ff.getlength(cur + ch) > 2062 and cur:
                lines.append(cur)
                cur = ch
            else:
                cur += ch
        if cur:
            lines.append(cur)
    off = ink_offset(ff, "本")
    for i, line in enumerate(lines):
        d.text((161, 3262 + i * 30 - off), line, font=ff, fill=(108, 104, 99))

    img.save(OUT_PNG)
    img.save(OUT_PDF, "PDF", resolution=300.0)
    print(f"{OUT_PNG} {img.size} / フッター {len(lines)}行")


if __name__ == "__main__":
    main()
