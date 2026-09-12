#!/usr/bin/env python3
"""ページに載せる画像の画角を 16:9（1920x1080）に揃える。

kazuma の指示：写真の画角を全部合わせる。合わせられないものは都度報告する。

やり方は絵によって変える。どれを使ったかは最後にまとめて出力する。

  crop   … 16:9 に切り出す。絵の主役が真ん中の帯に収まっているものだけ
  extend … 幅を合わせて拡大し、足りない上下を地の色で伸ばす。
           2:1 の図版はもともと上下が暗い地なので、継ぎ目が出ない
  mat    … 切ると壊れるもの（ポスター等）は切らずに、
           16:9 の暗い台紙の中央に置く

出力: assets/charity/16x9/<名前>.jpg
使い方: python3 tools/fit-16x9.py
"""
from pathlib import Path

from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
CHARITY = ROOT / "assets" / "charity"
OUT = CHARITY / "16x9"
W, H = 1920, 1080
INK = (10, 7, 9)

# (元ファイル, 方式, 縦の注視点 0=上 1=下)
PLAN = (
    ("axis_banner.jpg",            "extend", 0.5),
    ("timetable_banner.jpg",       "extend", 0.5),
    ("returns_banner.jpg",         "extend", 0.5),
    ("flow_banner.jpg",            "extend", 0.5),
    ("venue_banner.jpg",           "extend", 0.5),
    # 野球場のカットは縦位置で、16:9 に切ると胸から下が落ちる。
    # バンドの宣材（group_band）はもともと 1.77 で、3人の全身が収まっている。
    ("group_band.jpg",             "crop",   0.50),
    ("group.jpg",                  "crop",   0.45),
    ("nezu/oneworld_flyer.jpg",    "mat",    0.5),
)


def crop(im: Image.Image, focus: float) -> Image.Image:
    """16:9 に切り出す。focus は残したい帯の中心（縦位置の比）。"""
    if im.width / im.height > W / H:                 # 横に長い → 左右を切る
        w = round(im.height * W / H)
        x = (im.width - w) // 2
        im = im.crop((x, 0, x + w, im.height))
    else:                                            # 縦に長い → 上下を切る
        h = round(im.width * H / W)
        y = max(0, min(im.height - h, round(im.height * focus - h / 2)))
        im = im.crop((0, y, im.width, y + h))
    return im.resize((W, H), Image.Resampling.LANCZOS)


def extend(im: Image.Image) -> Image.Image:
    """幅を合わせて拡大し、上下に足りないぶんを端の色で伸ばす。"""
    h = round(im.height * W / im.width)
    im = im.resize((W, h), Image.Resampling.LANCZOS)
    if h >= H:
        return crop(im, 0.5)
    top = (H - h) // 2
    canvas = Image.new("RGB", (W, H), INK)
    canvas.paste(im.crop((0, 0, W, 1)).resize((W, top + 2)), (0, 0))
    canvas.paste(im.crop((0, h - 1, W, h)).resize((W, H - h - top + 2)),
                 (0, h + top - 2))
    canvas = canvas.filter(ImageFilter.GaussianBlur(2))   # 継ぎ目をならす
    canvas.paste(im, (0, top))
    return canvas


def mat(im: Image.Image) -> Image.Image:
    """切ると壊れる絵は、切らずに 16:9 の台紙の中央に置く。"""
    k = min(W / im.width, (H - 40) / im.height)
    im = im.resize((round(im.width * k), round(im.height * k)),
                   Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", (W, H), INK)
    canvas.paste(im, ((W - im.width) // 2, (H - im.height) // 2))
    return canvas


def main() -> None:
    OUT.mkdir(exist_ok=True)
    report = []
    for name, how, focus in PLAN:
        src = CHARITY / name
        im = Image.open(src).convert("RGB")
        before = f"{im.width}x{im.height}"
        out = {"crop": lambda: crop(im, focus),
               "extend": lambda: extend(im),
               "mat": lambda: mat(im)}[how]()
        dst = OUT / Path(name).name
        out.save(dst, quality=90, subsampling=0, optimize=True)
        report.append((how, before, Path(name).name))

    for how in ("crop", "extend", "mat"):
        rows = [r for r in report if r[0] == how]
        if rows:
            print(f"\n■ {how}")
            for _, before, name in rows:
                print(f"   {before:>10s} → 1920x1080   {name}")


if __name__ == "__main__":
    main()
