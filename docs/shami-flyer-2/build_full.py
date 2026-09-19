#!/usr/bin/env python3
"""Deterministically build the second Shagakuen announcement flyer."""

from pathlib import Path
import re
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent
COPY, BG, MIO = ROOT / "copy.md", ROOT / "ref/bg.png", ROOT / "ref/mio.jpg"
OUT = ROOT / "out/flyer2_final.png"
W, H = 1122, 1402
FONT = "/System/Library/Fonts/ヒラギノ明朝 ProN.ttc"
CREAM, MUTED = (248, 241, 222, 255), (224, 215, 193, 255)
GOLD_TOP, GOLD_BOTTOM = (255, 231, 157, 255), (178, 122, 35, 255)
TEXT_X, TEXT_RIGHT = 60, 760
PHOTO_BOX = (780, 700, 1122, 1255)
BOXES = []


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
        c = tuple(round(GOLD_TOP[i] * (1-t) + GOLD_BOTTOM[i] * t) for i in range(3)) + (255,)
        gd.line((0, y, size[0], y), fill=c)
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
    src = Image.open(MIO).convert("RGB").crop((250, 65, 995, 1510))
    pw, ph = PHOTO_BOX[2] - PHOTO_BOX[0], PHOTO_BOX[3] - PHOTO_BOX[1]
    src.thumbnail((pw, ph), Image.Resampling.LANCZOS)
    pic = Image.new("RGBA", (pw, ph))
    pic.paste(ImageEnhance.Brightness(ImageEnhance.Contrast(src).enhance(1.08)).enhance(.78),
              ((pw-src.width)//2, 0))
    m = Image.new("L", (pw, ph), 0)
    p = m.load()
    for y in range(ph):
        for x in range(pw):
            # Required soft left/top blend; bottom clears the CTA band.
            p[x, y] = min(238, int(min(1, x/72) * min(1, y/85) * min(1, (ph-y)/95) * 255))
    pic.putalpha(m.filter(ImageFilter.GaussianBlur(10)))
    base.alpha_composite(pic, PHOTO_BOX[:2])


def fitted_title(base, text, y):
    """Render every headline at one natural 55px size, without scaling."""
    f = font(55, True)
    cx = W // 2
    gold_text(base, (cx, y), text, f, anchor="ma", stroke=1)
    bb = ImageDraw.Draw(base).textbbox((cx, y), text, font=f, anchor="ma", stroke_width=1)
    assert bb[2] - bb[0] <= 1000, f"headline wider than 1000px: {text}"
    BOXES.append((*bb, text))
    return y + 60


def body_layout(base, s, target_top, target_bottom):
    """Flow 24px copy at 1.5 leading through areas that exclude the portrait."""
    fs = 24
    f, fb, fh = font(fs), font(29, True), font(29, True)
    leading, gap = round(fs * 1.5), 20
    # Two upper columns, then the 700px-wide lane beside the portrait.
    regions = [(60, 545, target_top, 695), (565, 1062, target_top, 695),
               (60, 400, 700, target_bottom), (420, 760, 700, target_bottom)]
    ri, x, right, y, bottom = 0, *regions[0]
    d = ImageDraw.Draw(base)
    boxes = []

    def advance_region(reason=""):
        nonlocal ri, x, right, y, bottom
        ri += 1
        assert ri < len(regions), f"body copy does not fit available regions: {reason}"
        x, right, y, bottom = regions[ri]

    def wrap(text, ff, width):
        out, cur = [], ""
        for ch in text:
            trial = cur + ch
            if cur and ff.getlength(trial) > width:
                out.append(cur); cur = ch
            else:
                cur = trial
        if cur: out.append(cur)
        if len(out) > 1 and len(out[-1]) <= 2 and len(out[-2]) > 3:
            out[-1] = out[-2][-2:] + out[-1]
            out[-2] = out[-2][:-2]
        return out or [""]

    def put(text, kind="body", extra_gap=0):
        nonlocal y
        ff = fh if kind == "hero" else (fb if kind != "body" else f)
        step = max(leading, round(ff.size * 1.28))
        for line in wrap(text, ff, right-x):
            # The region limit applies to visible glyphs, not the following leading.
            if y + ff.getbbox(line, stroke_width=1)[3] > bottom:
                advance_region(f"{line!r} at y={y}, bottom={bottom}")
            if kind == "body":
                d.text((x, y), line, font=ff, fill=(245,239,228,255),
                       stroke_width=1, stroke_fill=(0,0,0,190))
            else:
                gold_text(base, (x, y), line, ff)
            bb = d.textbbox((x, y), line, font=ff, stroke_width=1)
            boxes.append((*bb, line))
            y += step
        y += extra_gap

    def block(lines, gap_after=True):
        nonlocal y
        for line in lines:
            if line:
                # Highlight requested key phrases without shrinking the body copy.
                highlight = any(k in line for k in ("才覚領域", "できる青春"))
                put(line, "gold" if highlight else "body")
            else:
                # Paragraph separation is already represented by the 20px block gap.
                pass
        if gap_after: y += gap

    block(s["リード"].splitlines())
    put("想いを語り、行動に変える。", "gold")
    block(s["想いを語り、行動に変える。"].splitlines())
    put("― MIO YASHIRO からのメッセージ ―", "gold")
    msg = s["MIO YASHIRO からのメッセージ"].splitlines()
    put(msg[0], "hero")
    block(msg[1:-1], gap_after=False)
    put(msg[-1], "gold", gap)
    # This heading and everything after it must live in the left photo lane.
    if ri < 2:
        ri = 1
        advance_region()
    put("そして、その挑戦を仲間と楽しむ。", "gold")
    block(s["そして、その挑戦を仲間と楽しむ。"].splitlines())
    block(s["結び"].splitlines(), gap_after=False)
    return boxes


def assert_no_overlap(boxes):
    for i, a in enumerate(boxes):
        for b in boxes[i+1:]:
            # Touching edges are fine; actual glyph rectangles may not intersect.
            overlap = a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]
            assert not overlap, f"text overlap: {a[4]!r} / {b[4]!r}"
        if a[4] != "10.15 詳細公開":
            assert a[0] >= TEXT_X-2 and a[2] <= 1064, f"text outside field: {a[4]!r}"
        assert not (a[0] < PHOTO_BOX[2] and a[2] > PHOTO_BOX[0] and
                    a[1] < PHOTO_BOX[3] and a[3] > PHOTO_BOX[1]), f"text in photo: {a[4]!r}"


def main():
    global BOXES
    BOXES = []
    s = sections(COPY)
    base = Image.open(BG).convert("RGBA")
    assert base.size == (W, H)
    shade = Image.new("RGBA", base.size)
    ImageDraw.Draw(shade).rectangle((35, 20, 1087, 1382), fill=(0,0,0,92))
    base.alpha_composite(shade)
    add_portrait(base)
    d = ImageDraw.Draw(base)
    d.rounded_rectangle((43, 28, 1079, 1375), radius=8, outline=(205,158,57,180), width=2)

    y = 34
    for line in s["見出し（3行・据え置き）"].splitlines():
        y = fitted_title(base, line, y)
    # Requested fallback (c): 24px beneath the headline.
    body_top = y + 24
    cta_top = 1300
    body_boxes = body_layout(base, s, body_top, cta_top-8)
    BOXES.extend(body_boxes)

    # Full-width bottom anchor, deliberately above the inner frame baseline.
    band = (60, cta_top, 1062, 1370)
    d.rounded_rectangle(band, radius=8, fill=(0,0,0,224), outline=(232,186,76,240), width=2)
    cta = s["CTA"]
    cf = font(64, True)
    gold_text(base, ((band[0]+band[2])//2, (band[1]+band[3])//2), cta, cf, anchor="mm", stroke=1)
    bb = d.textbbox(((band[0]+band[2])//2, (band[1]+band[3])//2), cta, font=cf, anchor="mm", stroke_width=1)
    BOXES.append((*bb, cta))

    assert_no_overlap(BOXES)
    OUT.parent.mkdir(exist_ok=True)
    base.convert("RGB").save(OUT, quality=96)
    assert all(not (b[4].strip() in {"。", "い。", "ば、", "く。"}) for b in BOXES)
    print(f"saved {OUT} ({W}x{H}); {len(BOXES)} line boxes; overlap/photo-field audit OK")


if __name__ == "__main__":
    main()
