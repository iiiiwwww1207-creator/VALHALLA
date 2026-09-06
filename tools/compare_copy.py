#!/usr/bin/env python3
"""Create a vertical comparison of the LINE blocks in three flyer variants."""

from pathlib import Path

import cv2
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
INPUTS = [DIST / f"_copy_{variant}.png" for variant in "abc"]
OUTPUT = DIST / "copy_compare.png"

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


def detect_qr_bounds(path: Path) -> tuple[int, int, int, int]:
    image = cv2.imread(str(path))
    if image is None:
        raise FileNotFoundError(f"Could not read image: {path}")

    _decoded, points, _straight = cv2.QRCodeDetector().detectAndDecode(image)
    if points is None or points.size == 0:
        raise RuntimeError(f"QR code was not detected in: {path}")

    points = points.reshape(-1, 2)
    x0 = int(points[:, 0].min())
    y0 = int(points[:, 1].min())
    # Pillow's right and lower crop edges are exclusive.
    x1 = int(points[:, 0].max()) + 1
    y1 = int(points[:, 1].max()) + 1
    return x0, y0, x1, y1


def expanded_crop_box(
    qr_box: tuple[int, int, int, int], image_size: tuple[int, int]
) -> tuple[int, int, int, int]:
    x0, y0, x1, y1 = qr_box
    qr_width = x1 - x0
    qr_height = y1 - y0
    image_width, image_height = image_size

    left = max(0, int(x0 - qr_width * 0.75))
    top = max(0, int(y0 - qr_height * 0.85))
    right = min(image_width, int(x1 + qr_width * 0.75))
    bottom = min(image_height, int(y1 + qr_height * 1.30))
    return left, top, right, bottom


def text_height(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont) -> int:
    box = draw.textbbox((0, 0), text, font=font)
    return box[3] - box[1]


def main() -> None:
    qr_box = detect_qr_bounds(INPUTS[0])

    source_images = [Image.open(path).convert("RGB") for path in INPUTS]
    try:
        crop_box = expanded_crop_box(qr_box, source_images[0].size)
        crops = [image.crop(crop_box) for image in source_images]
    finally:
        for image in source_images:
            image.close()

    crop_width, crop_height = crops[0].size
    if any(crop.size != (crop_width, crop_height) for crop in crops):
        raise RuntimeError("The three crops do not have matching dimensions")

    title_font = load_font(TITLE_SIZE)
    label_font = load_font(LABEL_SIZE)
    measure = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    title = "LINE BLOCK - copy variants"
    title_height = text_height(measure, title, title_font)
    label_heights = [text_height(measure, label, label_font) for label in "ABC"]

    first_label_y = TOP_PADDING + title_height + TITLE_TO_LABEL
    first_image_y = first_label_y + label_heights[0] + LABEL_TO_IMAGE
    image_ys = [first_image_y + index * (crop_height + IMAGE_GAP) for index in range(3)]
    label_ys = [first_label_y]
    for index in range(1, 3):
        label_ys.append(image_ys[index] - LABEL_TO_IMAGE - label_heights[index])

    canvas_width = crop_width + SIDE_PADDING * 2
    canvas_height = image_ys[-1] + crop_height + BOTTOM_PADDING
    canvas = Image.new("RGB", (canvas_width, canvas_height), BACKGROUND)
    draw = ImageDraw.Draw(canvas)
    draw.text((SIDE_PADDING, TOP_PADDING), title, font=title_font, fill=TEXT_COLOR)

    for label, label_y, crop, image_y in zip("ABC", label_ys, crops, image_ys):
        draw.text((SIDE_PADDING, label_y), label, font=label_font, fill=TEXT_COLOR)
        canvas.paste(crop, (SIDE_PADDING, image_y))
        crop.close()

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(OUTPUT)
    print(f"QR bounds: {qr_box}")
    print(f"Crop box: {crop_box}")
    print(f"Output: {OUTPUT}")
    print(f"Size: {canvas.size[0]}x{canvas.size[1]} px")


if __name__ == "__main__":
    main()
