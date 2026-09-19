#!/usr/bin/env python3
"""Build flyer2 short v3 with a top-right portrait and school-life plate."""

from pathlib import Path
import re

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent
COPY = ROOT / "copy_short.md"
BG = ROOT / "ref/bg.png"
MIO = ROOT / "ref/mio.jpg"
SCHOOL = ROOT / "ref/school.png"
OUT = ROOT / "out/flyer2_short_v3.png"

W, H = 1122, 1402
FONT = "/System/Library/Fonts/ヒラギノ明朝 ProN.ttc"
TEXT_X, NARROW_RIGHT, WIDE_RIGHT = 60, 680, 1060
PHOTO_BOX = (690, 0, 1122, 620)
CTA_BAND = (60, 1292, 1062, 1372)
CREAM = (245, 239, 228, 255)
GOLD_TOP = (255, 231, 157, 255)
GOLD_BOTTOM = (178, 122, 35, 255)


def font(size, bold=False):
    return ImageFont.truetype(FONT, size, index=2 if bold else 0)


def sections(path):
    result = {}
    raw = path.read_text(encoding="utf-8")
    for chunk in re.split(r"^## ", raw, flags=re.M)[1:]:
        title, body = chunk.split("\n", 1)
        result[title.strip()] = body.strip().replace("**", "")
    return result


def cover(im, size, focus_y=.5):
    scale = max(size[0] / im.width, size[1] / im.height)
    im = im.resize((round(im.width * scale), round(im.height * scale)), Image.Resampling.LANCZOS)
    left = (im.width - size[0]) // 2
    top = round((im.height - size[1]) * focus_y)
    return im.crop((left, top, left + size[0], top + size[1]))


def add_school(base):
    """Composite the generated plate at y=900..1402 with the requested reveal."""
    plate = cover(Image.open(SCHOOL).convert("RGBA"), (W, H - 900), .62)
    # Forty percent black scrim.
    scrim = Image.new("RGBA", plate.size, (0, 0, 0, 102))
    plate = Image.alpha_composite(plate, scrim)
    alpha = Image.new("L", plate.size)
    ap = alpha.load()
    for y in range(plate.height):
        # transparent at 900, reaching 70% opacity at 1120, then staying there
        a = min(178, round(178 * y / 220))
        for x in range(plate.width):
            ap[x, y] = a
    plate.putalpha(alpha)
    base.alpha_composite(plate, (0, 900))


def add_portrait(base):
    """Place MIO at upper-right, preserving the top of the head."""
    pw, ph = PHOTO_BOX[2] - PHOTO_BOX[0], PHOTO_BOX[3] - PHOTO_BOX[1]
    src = Image.open(MIO).convert("RGB")
    # This crop keeps all hair above the face and brings the face toward upper-right.
    crop = src.crop((250, 0, 1045, 1140))
    crop = cover(crop, (pw, ph), .0)
    crop = ImageEnhance.Brightness(ImageEnhance.Contrast(crop).enhance(1.05)).enhance(.82)
    pic = Image.new("RGBA", (pw, ph))
    pic.paste(crop, (0, 0))
    mask = Image.new("L", (pw, ph))
    mp = mask.load()
    for y in range(ph):
        for x in range(pw):
            left = max(0.0, min(1.0, x / 70))
            bottom = max(0.0, min(1.0, (620 - y) / 100))
            mp[x, y] = round(255 * left * bottom)
    pic.putalpha(mask.filter(ImageFilter.GaussianBlur(4)))
    base.alpha_composite(pic, PHOTO_BOX[:2])


def gold_layer(size, mask):
    grad = Image.new("RGBA", size)
    gd = ImageDraw.Draw(grad)
    for y in range(size[1]):
        t = (y % 90) / 89
        color = tuple(round(GOLD_TOP[i] * (1 - t) + GOLD_BOTTOM[i] * t) for i in range(3)) + (255,)
        gd.line((0, y, size[0], y), fill=color)
    return Image.composite(grad, Image.new("RGBA", size), mask)


def gold_text(base, xy, text, f, anchor="la", stroke=0):
    mask = Image.new("L", base.size, 0)
    ImageDraw.Draw(mask).text(xy, text, font=f, anchor=anchor, fill=255,
                              stroke_width=stroke, stroke_fill=255)
    shadow = Image.new("RGBA", base.size)
    shadow.paste((150, 88, 12, 150), (0, 4), mask.filter(ImageFilter.GaussianBlur(5)))
    base.alpha_composite(shadow)
    base.alpha_composite(gold_layer(base.size, mask))


def main():
    s = sections(COPY)
    base = Image.open(BG).convert("RGBA")
    assert base.size == (W, H)
    shade = Image.new("RGBA", base.size)
    ImageDraw.Draw(shade).rectangle((35, 20, 1087, 1382), fill=(0, 0, 0, 112))
    base.alpha_composite(shade)
    add_school(base)
    add_portrait(base)
    d = ImageDraw.Draw(base)
    d.rounded_rectangle((43, 28, 1079, 1375), radius=8, outline=(205, 158, 57, 180), width=2)
    boxes = []

    def put(text, x, y, f, color=CREAM, anchor="la", gold=False, stroke=1, right=WIDE_RIGHT):
        assert "\n" not in text
        if gold:
            gold_text(base, (x, y), text, f, anchor, stroke)
        else:
            d.text((x, y), text, font=f, anchor=anchor, fill=color,
                   stroke_width=stroke, stroke_fill=(0, 0, 0, 210))
        bb = d.textbbox((x, y), text, font=f, anchor=anchor, stroke_width=stroke)
        assert bb[0] >= TEXT_X - 2 and bb[2] <= right + 2, f"line outside field: {text!r} {bb}"
        boxes.append((*bb, text))
        return bb

    # Same natural font size on every title line; 34px is the largest that
    # fits the longest unchanged line into the mandatory 620px field.
    title_f = font(34, True)
    y = 45
    for line in s["見出し（3行・据え置き）"].splitlines():
        bb = put(line, TEXT_X, y, title_f, gold=True, right=NARROW_RIGHT)
        assert bb[2] - bb[0] <= 620
        y += 49

    body_f, body_bold = font(22), font(22, True)
    leading = 36
    y = 218
    for line in s["リード"].splitlines():
        hi = "才覚領域" in line
        put(line, TEXT_X, y, body_bold if hi else body_f, gold=hi, right=NARROW_RIGHT)
        y += leading

    y += 7
    put("― MIO YASHIRO からのメッセージ ―", TEXT_X, y, font(20, True), gold=True, right=NARROW_RIGHT)
    y += 43
    message = s["MIO YASHIRO からのメッセージ"].splitlines()
    put(message[0], TEXT_X, y, font(37, True), gold=True, right=NARROW_RIGHT)
    y += 58
    for line in message[1:-1]:
        if not line:
            y += 9
            continue
        right = NARROW_RIGHT if y < 620 else WIDE_RIGHT
        put(line, TEXT_X, y, body_f, right=right)
        y += leading

    y += 1
    put(message[-1], WIDE_RIGHT, y, font(23, True), anchor="ra", gold=True)
    y += 48
    for line in s["結び"].splitlines():
        if not line:
            y += 9
            continue
        hi = "できる青春" in line
        put(line, TEXT_X, y, body_bold if hi else body_f, gold=hi)
        y += leading
    assert y <= CTA_BAND[1] - 8, f"body reaches CTA: {y}"

    d.rounded_rectangle(CTA_BAND, radius=8, fill=(0, 0, 0, 217),
                        outline=(232, 186, 76, 240), width=2)
    put(s["CTA"], (CTA_BAND[0] + CTA_BAND[2]) // 2,
        (CTA_BAND[1] + CTA_BAND[3]) // 2, font(65, True), anchor="mm", gold=True)

    # Full line-box audit: collision, portrait exclusion, orphan punctuation.
    for i, a in enumerate(boxes):
        stripped = a[4].strip()
        assert stripped not in {"、", "。", "，", "．"}, f"orphan punctuation: {a[4]!r}"
        for b in boxes[i + 1:]:
            overlap = a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]
            assert not overlap, f"text overlap: {a[4]!r} / {b[4]!r}"
        intrudes = a[0] < 1122 and a[2] > 690 and a[1] < 620 and a[3] > 0
        assert not intrudes, f"text in portrait region: {a[4]!r} {a[:4]}"

    OUT.parent.mkdir(exist_ok=True)
    base.convert("RGB").save(OUT, quality=96)
    print(f"saved {OUT} ({W}x{H}); {len(boxes)} lines; all audits OK")


if __name__ == "__main__":
    main()
