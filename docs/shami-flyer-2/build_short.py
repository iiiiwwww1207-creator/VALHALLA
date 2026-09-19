#!/usr/bin/env python3
"""Build the short, single-column version of the second Shagakuen flyer."""

from pathlib import Path
import re

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parent
COPY = ROOT / "copy_short.md"
BG = ROOT / "ref/bg.png"
MIO = ROOT / "ref/mio.jpg"
OUT = ROOT / "out/flyer2_short.png"

W, H = 1122, 1402
FONT = "/System/Library/Fonts/ヒラギノ明朝 ProN.ttc"
TEXT_X, TEXT_RIGHT = 60, 760
WIDE_RIGHT = 1060
PHOTO_BOX = (780, 640, 1122, 1402)
CTA_BAND = (60, 1292, 1062, 1372)
BODY_SIZE = 28
LEADING = round(BODY_SIZE * 1.55)
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


def gold_layer(size, mask):
    grad = Image.new("RGBA", size)
    gd = ImageDraw.Draw(grad)
    for y in range(size[1]):
        t = (y % 90) / 89
        color = tuple(round(GOLD_TOP[i] * (1 - t) + GOLD_BOTTOM[i] * t)
                      for i in range(3)) + (255,)
        gd.line((0, y, size[0], y), fill=color)
    return Image.composite(grad, Image.new("RGBA", size), mask)


def gold_text(base, xy, text, f, anchor="la", stroke=0):
    mask = Image.new("L", base.size, 0)
    ImageDraw.Draw(mask).text(
        xy, text, font=f, anchor=anchor, fill=255,
        stroke_width=stroke, stroke_fill=255,
    )
    shadow = Image.new("RGBA", base.size)
    shadow.paste((150, 88, 12, 150), (0, 4),
                 mask.filter(ImageFilter.GaussianBlur(5)))
    base.alpha_composite(shadow)
    base.alpha_composite(gold_layer(base.size, mask))


def add_portrait(base):
    """Place the portrait in the exact requested box; the CTA later masks its foot."""
    src = Image.open(MIO).convert("RGB").crop((250, 65, 995, 1510))
    pw, ph = PHOTO_BOX[2] - PHOTO_BOX[0], PHOTO_BOX[3] - PHOTO_BOX[1]
    scale = max(pw / src.width, ph / src.height)
    src = src.resize((round(src.width * scale), round(src.height * scale)),
                     Image.Resampling.LANCZOS)
    left = (src.width - pw) // 2
    src = src.crop((left, 0, left + pw, ph))
    src = ImageEnhance.Brightness(ImageEnhance.Contrast(src).enhance(1.08)).enhance(.82)
    pic = Image.new("RGBA", (pw, ph))
    pic.paste(src, (0, 0))
    mask = Image.new("L", (pw, ph), 0)
    p = mask.load()
    for y in range(ph):
        for x in range(pw):
            p[x, y] = min(242, int(min(1, x / 72) * min(1, y / 85) * 255))
    pic.putalpha(mask.filter(ImageFilter.GaussianBlur(10)))
    base.alpha_composite(pic, PHOTO_BOX[:2])


def main():
    s = sections(COPY)
    base = Image.open(BG).convert("RGBA")
    assert base.size == (W, H)
    shade = Image.new("RGBA", base.size)
    ImageDraw.Draw(shade).rectangle((35, 20, 1087, 1382), fill=(0, 0, 0, 92))
    base.alpha_composite(shade)
    add_portrait(base)
    d = ImageDraw.Draw(base)
    d.rounded_rectangle((43, 28, 1079, 1375), radius=8,
                        outline=(205, 158, 57, 180), width=2)

    boxes = []

    def put(text, x, y, f, color=CREAM, anchor="la", gold=False,
            stroke=1, field_right=TEXT_RIGHT):
        assert "\n" not in text, "automatic or embedded wrapping is forbidden"
        if gold:
            gold_text(base, (x, y), text, f, anchor=anchor, stroke=stroke)
        else:
            d.text((x, y), text, font=f, anchor=anchor, fill=color,
                   stroke_width=stroke, stroke_fill=(0, 0, 0, 190))
        bb = d.textbbox((x, y), text, font=f, anchor=anchor, stroke_width=stroke)
        assert bb[0] >= TEXT_X - 2 and bb[2] <= field_right + 2, (
            f"line outside x={TEXT_X}..{field_right}: {text!r} {bb}"
        )
        boxes.append((*bb, text))
        return bb

    # Three equal-size, naturally rendered (never horizontally scaled) headlines.
    title_f = font(55, True)
    y = 37
    for line in s["見出し（3行・据え置き）"].splitlines():
        bb = put(line, W // 2, y, title_f, anchor="ma", gold=True,
                 stroke=1, field_right=WIDE_RIGHT)
        assert bb[2] - bb[0] <= 1000
        y += 61

    body_f = font(BODY_SIZE)
    gold_body_f = font(BODY_SIZE, True)

    # The lead sits above the portrait and may use the full 1000px text field.
    y += 19
    for line in s["リード"].splitlines():
        highlight = "才覚領域" in line
        put(line, TEXT_X, y, gold_body_f if highlight else body_f,
            gold=highlight, field_right=WIDE_RIGHT)
        y += LEADING

    y += 15
    put("― 社さんからのメッセージ ―", 410, y, font(24, True),
        anchor="ma", gold=True, field_right=TEXT_RIGHT)
    y += 43

    message = s["社さんからのメッセージ"].splitlines()
    put(message[0], TEXT_X, y, font(48, True), gold=True,
        field_right=TEXT_RIGHT)
    y += round(48 * 1.55)
    for line in message[1:-1]:
        if not line:
            y += 12
            continue
        put(line, TEXT_X, y, body_f, field_right=TEXT_RIGHT)
        y += LEADING

    y += 1
    signature = message[-1]
    put(signature, TEXT_RIGHT, y, font(25, True), anchor="ra", gold=True,
        field_right=TEXT_RIGHT)
    assert boxes[-1][4] == "生徒会長　MIO YASHIRO"
    y += 49

    for line in s["結び"].splitlines():
        if not line:
            y += 12
            continue
        highlight = "できる青春" in line
        put(line, TEXT_X, y, gold_body_f if highlight else body_f,
            gold=highlight, field_right=TEXT_RIGHT)
        y += LEADING

    assert y <= CTA_BAND[1] - 8, f"body reaches CTA band: y={y}"

    d.rounded_rectangle(CTA_BAND, radius=8, fill=(0, 0, 0, 232),
                        outline=(232, 186, 76, 240), width=2)
    cta = s["CTA"]
    put(cta, (CTA_BAND[0] + CTA_BAND[2]) // 2,
        (CTA_BAND[1] + CTA_BAND[3]) // 2, font(76, True), anchor="mm",
        gold=True, stroke=1, field_right=WIDE_RIGHT)

    # Audit every visible line box. The CTA masks the portrait, so only the
    # portrait's visible area above the band is an exclusion zone for text.
    photo_visible = (PHOTO_BOX[0], PHOTO_BOX[1], PHOTO_BOX[2], CTA_BAND[1])
    for i, a in enumerate(boxes):
        assert a[4].strip() not in {"、", "。", "，", "．"}, f"orphan punctuation: {a[4]!r}"
        for b in boxes[i + 1:]:
            overlap = a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]
            assert not overlap, f"text overlap: {a[4]!r} / {b[4]!r}"
        intrudes = (a[0] < photo_visible[2] and a[2] > photo_visible[0] and
                    a[1] < photo_visible[3] and a[3] > photo_visible[1])
        assert not intrudes, f"text in visible photo: {a[4]!r}"

    OUT.parent.mkdir(exist_ok=True)
    base.convert("RGB").save(OUT, quality=96)
    print(f"saved {OUT} ({W}x{H}); {len(boxes)} lines; all audits OK")


if __name__ == "__main__":
    main()
