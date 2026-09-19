#!/usr/bin/env python3
"""Build the 1122 x 1402 one-column Shagakuen announcement flyer."""

from pathlib import Path
import re
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent
COPY, BG, MIO = ROOT / "copy.md", ROOT / "ref/bg.png", ROOT / "ref/mio.jpg"
OUT = ROOT / "out/flyer2_final.png"
W, H = 1122, 1402
FONT = "/System/Library/Fonts/ヒラギノ明朝 ProN.ttc"
CREAM = (245, 239, 228, 255)
GOLD_TOP, GOLD_BOTTOM = (255, 231, 157, 255), (178, 122, 35, 255)
TEXT_X, TEXT_RIGHT = 60, 760
PHOTO_BOX = (780, 640, 1122, 1402)
CTA_BOX = (60, 1274, 1062, 1370)
BODY_SIZE, BODY_STEP = 21, round(21 * 1.45)


def font(size, bold=False):
    return ImageFont.truetype(FONT, size, index=2 if bold else 0)


def sections(path):
    raw = path.read_text(encoding="utf-8").split("## 短縮版", 1)[0]
    result = {}
    for chunk in re.split(r"^## ", raw, flags=re.M)[1:]:
        title, body = chunk.split("\n", 1)
        result[title.strip()] = body.strip().rstrip("-").strip().replace("**", "")
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
    ImageDraw.Draw(mask).text(xy, text, font=f, anchor=anchor, fill=255,
                              stroke_width=stroke, stroke_fill=255)
    shadow = Image.new("RGBA", base.size)
    shadow.paste((150, 88, 12, 150), (0, 4), mask.filter(ImageFilter.GaussianBlur(5)))
    base.alpha_composite(shadow)
    base.alpha_composite(gold_layer(base.size, mask))


def add_portrait(base):
    """Place the portrait in the specified lower-right field with soft top/left edges."""
    src = Image.open(MIO).convert("RGB").crop((250, 65, 995, 1510))
    pw, ph = PHOTO_BOX[2] - PHOTO_BOX[0], PHOTO_BOX[3] - PHOTO_BOX[1]
    scale = max(pw / src.width, ph / src.height)
    src = src.resize((round(src.width * scale), round(src.height * scale)), Image.Resampling.LANCZOS)
    left = (src.width - pw) // 2
    src = src.crop((left, 0, left + pw, ph))
    src = ImageEnhance.Brightness(ImageEnhance.Contrast(src).enhance(1.08)).enhance(.78)
    pic = src.convert("RGBA")
    mask = Image.new("L", (pw, ph), 0)
    pix = mask.load()
    for y in range(ph):
        for x in range(pw):
            pix[x, y] = min(238, int(min(1, x / 72) * min(1, y / 85) * 255))
    pic.putalpha(mask.filter(ImageFilter.GaussianBlur(10)))
    base.alpha_composite(pic, PHOTO_BOX[:2])


def text_box(draw, xy, text, f, anchor="la", stroke=0):
    return (*draw.textbbox(xy, text, font=f, anchor=anchor, stroke_width=stroke), text)


def render_title(base, lines, boxes):
    """Three centered, unscaled lines at one font size, all within 1000 px."""
    draw = ImageDraw.Draw(base)
    title_font = font(52, True)
    y = 29
    for line in lines:
        gold_text(base, (W // 2, y), line, title_font, anchor="ma", stroke=1)
        box = text_box(draw, (W // 2, y), line, title_font, "ma", 1)
        assert box[2] - box[0] <= 1000, f"headline wider than 1000px: {line}"
        boxes.append(box)
        y += 57
    return y + 6


def render_copy(base, source, y, boxes):
    """Render copy.md verbatim: one source line is exactly one rendered line."""
    draw = ImageDraw.Draw(base)
    body = font(BODY_SIZE)
    subhead = font(22, True)
    hero = font(28, True)
    blocks = []

    def put(line, f=body, gold=False, x=TEXT_X, anchor="la", step=BODY_STEP):
        nonlocal y
        assert "\n" not in line
        if gold:
            gold_text(base, (x, y), line, f, anchor=anchor)
        else:
            draw.text((x, y), line, font=f, anchor=anchor, fill=CREAM,
                      stroke_width=1, stroke_fill=(0, 0, 0, 190))
        box = text_box(draw, (x, y), line, f, anchor, 1 if not gold else 0)
        boxes.append(box)
        y += step
        return box

    def paragraph_lines(key):
        return [line for line in source[key].splitlines() if line]

    # Above the message heading the available field is 1000 px wide.
    for line in paragraph_lines("リード"):
        put(line, gold=("才覚領域" in line))
    y += 1
    put("想いを語り、行動に変える。", subhead, True)
    for line in paragraph_lines("想いを語り、行動に変える。"):
        put(line)
    y += 1
    message_heading = put("― MIO YASHIRO からのメッセージ ―", subhead, True,
                          x=(TEXT_X + TEXT_RIGHT) // 2, anchor="ma")
    assert message_heading[1] < PHOTO_BOX[1], "message heading must be above portrait"

    # From here on every line is confined to x=60..760 beside the portrait.
    msg = paragraph_lines("MIO YASHIRO からのメッセージ")
    put(msg[0], hero, True, step=34)
    for line in msg[1:-1]:
        put(line)
    y += 0
    put(msg[-1], body, True, x=TEXT_RIGHT, anchor="ra")
    y += 1
    put("そして、その挑戦を仲間と楽しむ。", subhead, True)
    for line in paragraph_lines("そして、その挑戦を仲間と楽しむ。"):
        put(line, gold=("できる青春" in line))
    y += 0
    for line in paragraph_lines("結び"):
        put(line)
    return y


def assert_layout(boxes, message_index):
    punctuation_only = re.compile(r"^[、。，．・！？）」』]+$")
    for i, a in enumerate(boxes):
        assert not punctuation_only.fullmatch(a[4].strip()), f"orphan punctuation: {a[4]!r}"
        for b in boxes[i + 1:]:
            overlap = a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]
            assert not overlap, f"text overlap: {a[4]!r} / {b[4]!r}"
        if i >= message_index:
            assert a[0] >= TEXT_X - 2 and a[2] <= TEXT_RIGHT + 2, f"text outside left lane: {a[4]!r}"
            intrudes = (a[0] < PHOTO_BOX[2] and a[2] > PHOTO_BOX[0] and
                        a[1] < CTA_BOX[1] and a[3] > PHOTO_BOX[1])
            assert not intrudes, f"text in photo: {a[4]!r}"


def main():
    source = sections(COPY)
    forbidden = "\u793e\u3055\u3093"
    assert forbidden not in COPY.read_text(encoding="utf-8"), f"forbidden wording: {forbidden}"
    base = Image.open(BG).convert("RGBA")
    assert base.size == (W, H)
    shade = Image.new("RGBA", base.size)
    ImageDraw.Draw(shade).rectangle((35, 20, 1087, 1382), fill=(0, 0, 0, 92))
    base.alpha_composite(shade)
    add_portrait(base)
    draw = ImageDraw.Draw(base)
    draw.rounded_rectangle((43, 28, 1079, 1375), radius=8,
                           outline=(205, 158, 57, 180), width=2)

    boxes = []
    y = render_title(base, source["見出し（3行・据え置き）"].splitlines(), boxes)
    before = len(boxes)
    y = render_copy(base, source, y, boxes)
    message_index = next(i for i, b in enumerate(boxes)
                         if b[4] == "― MIO YASHIRO からのメッセージ ―") + 1
    assert y <= CTA_BOX[1] - 5, f"copy reaches CTA band: y={y}"

    draw.rounded_rectangle(CTA_BOX, radius=8, fill=(0, 0, 0, 224),
                           outline=(232, 186, 76, 240), width=2)
    cta = source["CTA"]
    cta_font = font(76, True)
    center = ((CTA_BOX[0] + CTA_BOX[2]) // 2, (CTA_BOX[1] + CTA_BOX[3]) // 2)
    gold_text(base, center, cta, cta_font, anchor="mm", stroke=1)
    cta_box = text_box(draw, center, cta, cta_font, "mm", 1)
    assert CTA_BOX[0] <= cta_box[0] and cta_box[2] <= CTA_BOX[2]

    assert_layout(boxes, message_index)
    OUT.parent.mkdir(exist_ok=True)
    base.convert("RGB").save(OUT, quality=96)
    assert Image.open(OUT).size == (1122, 1402)
    print(f"saved {OUT} ({W}x{H}); {len(boxes)} copy lines; final y={y}; audits OK")


if __name__ == "__main__":
    main()
