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


def drop_bystander(rgba: Image.Image) -> Image.Image:
    """記者会見のカットだけ。MIO の後ろに立っている別の人物を消す。

    人物専用モデルは、後ろの人も「人物」として拾ってしまう。縦に切って
    分けようとしても、その人と MIO の頭が重なっているので顔まで切れる。

    そこで色で分ける。MIO の左どなりの帯（x<940・y<1360）に居るのは
    **MIO の青い髪か、後ろの人か**のどちらかしかない。青だけを残せば、
    後ろの人は消えて MIO の髪は残る。
    """
    a = np.array(rgba.convert("RGBA"))
    alpha, rgb = a[..., 3].copy(), a[..., :3].astype(np.int16)
    h, w = alpha.shape

    band = np.zeros(alpha.shape, bool)
    band[0:1360, 0:940] = True
    blue = (rgb[..., 2] > rgb[..., 0] + 12) & (rgb[..., 2] > 55)
    keep = cv2.morphologyEx(blue.astype(np.uint8), cv2.MORPH_CLOSE,
                            cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (31, 31)))
    keep = cv2.dilate(keep, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7)))
    alpha[band & (keep == 0)] = 0

    # 隙間を埋めたぶん、後ろの人の肌と服が戻ってしまう。暖色を落とす。
    # 金のチェーンも暖色なので、チェーンより左（x<790）だけを対象にする。
    warm = rgb[..., 0] > rgb[..., 2] + 8
    left = np.zeros(alpha.shape, bool)
    left[0:1360, 0:790] = True
    alpha[left & warm] = 0

    # 帯より下にも、後ろの人の腕が左端に残る。MIO はそこでは黒いスーツなので、
    # 左端の暖色はすべて落として構わない。
    arm = np.zeros(alpha.shape, bool)
    arm[1360:2700, 0:520] = True
    alpha[arm & warm] = 0

    # 肩のあたりに残る灰色（後ろの人の服）は、青の条件をきつくして落とす
    lower = np.zeros(alpha.shape, bool)
    lower[860:1360, 690:940] = True
    alpha[lower & ~(rgb[..., 2] > rgb[..., 0] + 24)] = 0

    alpha = cv2.GaussianBlur(alpha, (0, 0), 1.6)
    out = a.copy()
    out[..., 3] = alpha
    return Image.fromarray(out)


def fade_shoulder(rgba: Image.Image) -> Image.Image:
    """肩の高さに残る、後ろの人の服を溶かして消す。

    ここだけは色でも質感でも明るさでも分けられなかった。
    後ろの人はピントが外れていて、そこにある MIO の髪も影で沈んでいて、
    どの数字を見ても差が出ない。明るさで切ると髪まで穴が空く。

    なので**切らずに、左へ向かって透明にしていく**。残っているのは
    輪郭のはっきりしない淡い影なので、勾配で薄めれば見えなくなり、
    髪の端も一緒にぼけて自然につながる。暗い地に置く前提の処理。
    """
    a = np.array(rgba.convert("RGBA"))
    alpha = a[..., 3].astype(np.float32)
    y0, y1, x0, x1 = 1020, 1680, 700, 980

    ramp = np.ones(alpha.shape[1], np.float32)
    ramp[:x0] = 0.0
    ramp[x0:x1] = np.linspace(0.0, 1.0, x1 - x0) ** 0.85

    band = np.ones(alpha.shape[0], np.float32)          # 上下も急に変わらないように
    fade = 110
    band[:y0 - fade] = 0.0
    band[y0 - fade:y0] = np.linspace(0.0, 1.0, fade)
    band[y1:y1 + fade] = np.linspace(1.0, 0.0, fade)
    band[y1 + fade:] = 0.0

    w = band[:, None] * (1.0 - ramp)[None, :]           # 効かせる強さ
    alpha *= 1.0 - w
    out = a.copy()
    out[..., 3] = np.clip(alpha, 0, 255).astype(np.uint8)
    return Image.fromarray(out)


def polish(rgba: Image.Image) -> Image.Image:
    """縁を整える。色で人を消したあとの後始末。

    ・浮いた破片を落とす ── いちばん大きい塊だけ残す。
      色で消すと、消しきれなかった灰色が本体から離れて宙に浮く
    ・ギザギザを取る ── 黒いスーツは背景との差が小さく、
      マスクの縁が点々になる。中央値ぼかしと開閉で粒を落とす
    ・最後にわずかにぼかして、紙に置いたときに切り貼りに見えないようにする
    """
    a = np.array(rgba.convert("RGBA"))
    alpha = a[..., 3]

    alpha = cv2.medianBlur(alpha, 15)
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (21, 21))
    alpha = cv2.morphologyEx(alpha, cv2.MORPH_CLOSE, k)
    alpha = cv2.morphologyEx(alpha, cv2.MORPH_OPEN, k)

    solid = (alpha > 60).astype(np.uint8)
    n, lab, st, _ = cv2.connectedComponentsWithStats(solid, 8)
    if n > 1:
        biggest = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
        alpha[lab != biggest] = 0

    alpha = cv2.GaussianBlur(alpha, (0, 0), 3.2)
    alpha = np.clip((alpha.astype(np.int16) - 128) * 3 + 128, 0, 255).astype(np.uint8)
    alpha = cv2.GaussianBlur(alpha, (0, 0), 1.1)

    out = a.copy()
    out[..., 3] = alpha
    return Image.fromarray(out)


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

    # 先に余白を落として原点を確定させる。以降の処理は座標を直に書くので、
    # ここで切っておかないと、切り抜く範囲が毎回ずれる。
    cutout = cutout.crop(cutout.getchannel("A").point(
        lambda v: 255 if v > 12 else 0).getbbox())

    if "HOSTCALL" in path.name:
        cutout = fade_shoulder(polish(drop_bystander(cutout)))
        cutout = cutout.crop(cutout.getchannel("A").point(
            lambda v: 255 if v > 12 else 0).getbbox())
    return cutout


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
