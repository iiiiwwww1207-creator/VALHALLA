#!/usr/bin/env python3
"""章ごとの図版で共通に使う地・書体・部品。

既存の4枚（axis / concept / flow / timetable）と同じ作りに揃えるための置き場。
寸法 1774x887・SCALE=2（大きく描いて縮める）・黒地に深紅のにじみ・
中央に VALHALLA のロゴを透かし、という約束はここで固定する。

個々の図版は create_chapter_banners.py 側に書く。
"""
from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = Path(__file__).resolve().parent

W, H = 1774, 887
SCALE = 2
SW, SH = W * SCALE, H * SCALE

BLACK = (5, 3, 7)
CRIMSON = (193, 18, 31)
DARK_CRIMSON = (142, 16, 25)
DEEPEST_CRIMSON = (110, 10, 18)
CREAM = (245, 239, 228)
SILVER = (198, 198, 205)
ASH = (128, 126, 130)


def first_font(*candidates: str) -> str:
    for candidate in candidates:
        if Path(candidate).exists():
            return candidate
    raise FileNotFoundError("必要な書体が見つかりません: " + ", ".join(candidates))


MINCHO = first_font("/System/Library/Fonts/ヒラギノ明朝 ProN.ttc",
                    "/System/Library/Fonts/Times.ttc")
SANS = first_font("/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc",
                  "/System/Library/Fonts/Hiragino Sans GB.ttc")
SANS_B = first_font("/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc",
                    "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc")
LATIN = first_font("/System/Library/Fonts/Optima.ttc",
                   "/System/Library/Fonts/HelveticaNeue.ttc")


def face(path: str, size: int, index: int = 0) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size=size * SCALE, index=index)


def sbox(box) -> tuple:
    return tuple(round(v * SCALE) for v in box)


def spos(point) -> tuple:
    return tuple(round(v * SCALE) for v in point)


def ground() -> Image.Image:
    """黒地＋深紅のにじみ＋周辺の落ち。4枚の既存図版と同じ地。"""
    base = Image.new("RGBA", (SW, SH), (*BLACK, 255))

    bloom = Image.new("RGBA", (SW, SH), (0, 0, 0, 0))
    bd = ImageDraw.Draw(bloom)
    bd.ellipse(sbox((-300, 120, 860, 1140)), fill=(*DEEPEST_CRIMSON, 96))
    bd.ellipse(sbox((940, -340, 2160, 700)), fill=(*DEEPEST_CRIMSON, 72))
    base = Image.alpha_composite(base, bloom.filter(ImageFilter.GaussianBlur(230 * SCALE)))

    vignette = Image.new("L", (SW, SH), 0)
    ImageDraw.Draw(vignette).ellipse(sbox((-320, -200, W + 320, H + 200)), fill=255)
    vignette = vignette.filter(ImageFilter.GaussianBlur(190 * SCALE))
    shade = Image.new("RGBA", (SW, SH), (0, 0, 0, 150))
    shade.putalpha(Image.eval(vignette, lambda v: 150 - round(v * 150 / 255)))
    return Image.alpha_composite(base, shade)


def tracked(draw: ImageDraw.ImageDraw, xy, text: str, font, fill, tracking: int = 0):
    """字間を開けて描く。開いた分を含めた幅を返す。"""
    x, y = spos(xy)
    step = tracking * SCALE
    for ch in text:
        draw.text((x, y), ch, font=font, fill=fill)
        x += round(draw.textlength(ch, font=font)) + step
    return (x - spos(xy)[0]) / SCALE


def eyebrow(draw: ImageDraw.ImageDraw, text: str) -> None:
    """左上の小見出し。既存4枚と同じ位置・同じ深紅。"""
    tracked(draw, (70, 40), text, face(SANS, 17), CRIMSON, tracking=5)


def footer(img: Image.Image, lines: list[str], right: float = 1704,
           bottom: float = 838) -> Image.Image:
    """右下の締めの一言。深紅の罫を1本引いて、その下に明朝で置く。"""
    draw = ImageDraw.Draw(img)
    fnt = face(MINCHO, 31)
    heights = len(lines) * 44
    top = bottom - heights
    draw.line(sbox((right - 210, top - 22, right, top - 22)), fill=CRIMSON, width=2 * SCALE)
    for i, line in enumerate(lines):
        w = draw.textlength(line, font=fnt) / SCALE
        draw.text(spos((right - w, top + i * 44)), line, font=fnt, fill=CREAM)
    return img


def node(draw: ImageDraw.ImageDraw, center, radius: float, width: float = 2,
         color=CRIMSON) -> None:
    cx, cy = center
    draw.ellipse(sbox((cx - radius, cy - radius, cx + radius, cy + radius)),
                 outline=color, width=round(width * SCALE))


def centered(draw: ImageDraw.ImageDraw, cx: float, y: float, text: str, font, fill):
    w = draw.textlength(text, font=font) / SCALE
    draw.text(spos((cx - w / 2, y)), text, font=font, fill=fill)


def arrow(draw: ImageDraw.ImageDraw, start, end, color=CRIMSON, width: float = 1.6,
          head: float = 11) -> None:
    draw.line(sbox((*start, *end)), fill=color, width=round(width * SCALE))
    ang = math.atan2(end[1] - start[1], end[0] - start[0])
    for side in (+1, -1):
        a = ang + math.pi + side * 0.40
        draw.line(sbox((end[0], end[1],
                        end[0] + math.cos(a) * head, end[1] + math.sin(a) * head)),
                  fill=color, width=round(width * SCALE))


def finish(img: Image.Image, out: Path, max_mb: float = 2.0) -> None:
    """縮めて保存し、寸法とファイルサイズを検査する。"""
    flat = Image.new("RGB", img.size, BLACK)
    flat.paste(img, mask=img.getchannel("A"))
    flat = flat.resize((W, H), Image.Resampling.LANCZOS)
    for quality in (92, 88, 84, 78, 72):
        flat.save(out, "JPEG", quality=quality, optimize=True, progressive=True)
        if out.stat().st_size <= max_mb * 1024 * 1024:
            break
    else:
        raise RuntimeError(f"{out.name} が {max_mb}MB に収まりません")
    if Image.open(out).size != (W, H):
        raise RuntimeError(f"{out.name} の寸法が {W}x{H} ではありません")
    print(f"{out.name:<26}{W}x{H}  {out.stat().st_size/1024:.0f}KB")
