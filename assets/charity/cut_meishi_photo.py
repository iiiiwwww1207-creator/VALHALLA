#!/usr/bin/env python3
"""限定名刺用に、宣材写真から人物だけを切り抜く。

記者会見のカットは背景のバックパネルに他社ロゴが並んでいて、
支援の対価として配る名刺にはそのまま使えない。人物だけを抜いてしまえば
ロゴは一緒に消えるので、背景は自前のデザインに差し替えられる。

切り抜きの手順はメインビジュアルと同じ考え方:
  1. 人物専用モデル（u2net_human_seg）で意味的に抜く
  2. まず粗く当たりを取り、人物の周りだけを切り出してからもう一度かける
     （U2Net は入力を 320x320 に縮めるため、全体を渡すとマスクが粗くなる）
  3. alpha matting で境界を引き直す
  4. 輪郭を平滑化してギザつきを取る

入力 : ~/Desktop/VALHALLA_受領素材_20260911/*.jpg
出力 : assets/charity/meishi/<名前>_cut.png（背景透過）
"""
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageFilter
from rembg import new_session, remove

SRC = Path.home() / "Desktop" / "VALHALLA_受領素材_20260911"
OUT = Path(__file__).resolve().parent / "meishi"
FILES = ("9497_260522_HOSTCALL-Edit-Edit.jpg", "1240_260701_VALHALLA-PV-Edit-Edit.jpg")


def refine(rgba: Image.Image) -> Image.Image:
    """輪郭の階段とノイズを取る。境界が甘いと合成したときに貼り付いて見える。"""
    a = np.array(rgba.getchannel("A"))
    a = cv2.medianBlur(a, 9)
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11))
    a = cv2.morphologyEx(a, cv2.MORPH_CLOSE, k)
    a = cv2.morphologyEx(a, cv2.MORPH_OPEN, k)
    a = cv2.GaussianBlur(a, (0, 0), 2.8)
    a = np.clip((a.astype(np.int16) - 118) * 5 + 128, 0, 255).astype(np.uint8)
    rgba.putalpha(Image.fromarray(a))
    return rgba


def cut(path: Path, session) -> Image.Image:
    im = Image.open(path).convert("RGB")

    # ① 粗く抜いて、人物のいる範囲を知る
    rough = remove(im, session=session)
    box = rough.getchannel("A").point(lambda v: 255 if v > 40 else 0).getbbox()
    pad = round(max(im.size) * 0.03)
    box = (max(0, box[0] - pad), max(0, box[1] - pad),
           min(im.width, box[2] + pad), min(im.height, box[3] + pad))

    # ② その範囲だけを渡して抜き直す。同じ 320x320 に人物が大きく収まる
    crop = im.crop(box)
    cutout = remove(crop, session=session, alpha_matting=True,
                    alpha_matting_foreground_threshold=250,
                    alpha_matting_background_threshold=15,
                    alpha_matting_erode_size=12)
    cutout = refine(cutout.convert("RGBA"))
    return cutout.crop(cutout.getchannel("A").point(
        lambda v: 255 if v > 12 else 0).getbbox())


def main() -> None:
    OUT.mkdir(exist_ok=True)
    session = new_session("u2net_human_seg")
    for name in FILES:
        src = SRC / name
        if not src.exists():
            raise FileNotFoundError(src)
        out = cut(src, session)
        dst = OUT / (name.split("_")[2].split("-")[0].lower() + "_cut.png")
        out.save(dst)
        opaque = int((np.array(out.getchannel("A")) > 200).sum())
        print(f"{dst.name} | {out.width}x{out.height} | 不透明 {opaque:,}px")


if __name__ == "__main__":
    main()
