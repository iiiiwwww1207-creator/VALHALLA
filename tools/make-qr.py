#!/usr/bin/env python3
"""フライヤーや配布物に貼る QR コードを作る。

印刷に耐えるよう、誤り訂正は H（30%まで復元できる）で出す。
汚れや折れに強く、中央にロゴを置く余地も残る。

使い方:
  python3 tools/make-qr.py "https://camp-fire.jp/..." 出力名 [ラベル]

出力: assets/charity/qr/<出力名>.png（1200px・余白4モジュール）
      assets/charity/qr/<出力名>.svg（拡大しても劣化しない・印刷入稿向け）
"""
import sys
from pathlib import Path

import segno

OUT = Path(__file__).resolve().parent.parent / "assets" / "charity" / "qr"


def main() -> None:
    if len(sys.argv) < 3:
        raise SystemExit(__doc__)
    url, name = sys.argv[1], sys.argv[2]
    if not url.startswith(("http://", "https://")):
        raise SystemExit(f"URL が http(s) で始まっていません: {url}")

    OUT.mkdir(parents=True, exist_ok=True)
    qr = segno.make(url, error="h")

    png = OUT / f"{name}.png"
    svg = OUT / f"{name}.svg"
    qr.save(png, scale=1, border=4)           # いったん最小で出して倍率を決める
    from PIL import Image
    im = Image.open(png)
    scale = max(1, round(1200 / im.width))
    qr.save(png, scale=scale, border=4, dark="#0a0709", light="#ffffff")
    qr.save(svg, scale=10, border=4, dark="#0a0709", light="#ffffff")

    im = Image.open(png)
    print(f"{png}  {im.width}x{im.height}px  誤り訂正H  version={qr.version}")
    print(f"{svg}  （入稿用）")
    print(f"中身: {url}")


if __name__ == "__main__":
    main()
