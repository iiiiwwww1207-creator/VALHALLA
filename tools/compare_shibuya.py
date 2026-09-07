#!/usr/bin/env python3
"""Create a vertical comparison of three venue bands in flyer exports."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
INPUTS = (
    ("CURRENT  unknown source, upscaled from 710px", DIST / "flyer_fusion.png"),
    ("A  Unsplash 3000x4500  (neon-red)", DIST / "_sh_a.png"),
    ("B  Unsplash 3000x4500  (wide)", DIST / "_sh_b.png"),
)
OUTPUT = DIST / "shibuya_compare.png"

CROP_BOX = (0, 1580, 2382, 2110)
IMAGE_WIDTH = 1240
BACKGROUND = "#F2F2F5"
TEXT_COLOR = "#333333"
SIDE_PADDING = 60
TOP_PADDING = 48
BOTTOM_PADDING = 60
TITLE_SIZE = 34
LABEL_SIZE = 28
TITLE_TO_LABEL = 42
LABEL_TO_IMAGE = 14
IMAGE_GAP = 56


def load_font(size: int) -> ImageFont.ImageFont:
    for path in (
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
    ):
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            pass
    return ImageFont.load_default()


def text_height(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont) -> int:
    box = draw.textbbox((0, 0), text, font=font)
    return box[3] - box[1]


def make_crop(path: Path) -> Image.Image:
    with Image.open(path) as source:
        if source.size != (2382, 3369):
            raise ValueError(f"Unexpected input size for {path}: {source.size}")
        crop = source.convert("RGB").crop(CROP_BOX)

    output_height = round(crop.height * IMAGE_WIDTH / crop.width)
    resized = crop.resize((IMAGE_WIDTH, output_height), Image.Resampling.LANCZOS)
    crop.close()
    return resized


def main() -> None:
    crops = [make_crop(path) for _label, path in INPUTS]
    title = "VENUE BAND - current vs free stock"
    title_font = load_font(TITLE_SIZE)
    label_font = load_font(LABEL_SIZE)
    measure = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    title_height = text_height(measure, title, title_font)
    label_heights = [text_height(measure, label, label_font) for label, _ in INPUTS]

    title_y = TOP_PADDING
    label_y = title_y + title_height + TITLE_TO_LABEL
    positions = []
    for crop, label_height in zip(crops, label_heights):
        image_y = label_y + label_height + LABEL_TO_IMAGE
        positions.append((label_y, image_y))
        label_y = image_y + crop.height + IMAGE_GAP

    canvas_width = IMAGE_WIDTH + SIDE_PADDING * 2
    canvas_height = positions[-1][1] + crops[-1].height + BOTTOM_PADDING
    canvas = Image.new("RGB", (canvas_width, canvas_height), BACKGROUND)
    draw = ImageDraw.Draw(canvas)
    draw.text((SIDE_PADDING, title_y), title, font=title_font, fill=TEXT_COLOR)

    for ((label, _path), crop, (item_label_y, image_y)) in zip(INPUTS, crops, positions):
        draw.text((SIDE_PADDING, item_label_y), label, font=label_font, fill=TEXT_COLOR)
        canvas.paste(crop, (SIDE_PADDING, image_y))
        crop.close()

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(OUTPUT)
    print(f"Output: {OUTPUT}")
    print(f"Size: {canvas.width}x{canvas.height} px")


if __name__ == "__main__":
    main()
