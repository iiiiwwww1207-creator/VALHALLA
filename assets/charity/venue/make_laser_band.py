#!/usr/bin/env python3
"""Create anonymized red-laser bands from the venue photograph."""

from pathlib import Path

from PIL import Image, ImageEnhance, ImageFilter


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "celavi_red.jpg"
OUTPUT_A = HERE / "laser_band_a.jpg"
OUTPUT_B = HERE / "laser_band_b.jpg"

EXPECTED_SOURCE_SIZE = (2560, 1708)
OUTPUT_SIZE = (2560, 500)
EDGE_FADE_FRACTION = 0.15
JPEG_QUALITY = 92


def fade_sides_to_black(image: Image.Image) -> Image.Image:
    """Linearly fade the outer 15% of each side to black."""
    width, height = image.size
    fade_width = round(width * EDGE_FADE_FRACTION)

    alpha_row = []
    for x in range(width):
        if x < fade_width:
            factor = x / fade_width
        elif x >= width - fade_width:
            factor = (width - 1 - x) / fade_width
        else:
            factor = 1.0
        alpha_row.append(round(255 * max(0.0, min(1.0, factor))))

    mask = Image.new("L", (width, 1))
    mask.putdata(alpha_row)
    mask = mask.resize((width, height))
    return Image.composite(image, Image.new("RGB", image.size, "black"), mask)


def save_jpeg(image: Image.Image, destination: Path) -> None:
    image.save(destination, "JPEG", quality=JPEG_QUALITY)


def main() -> None:
    with Image.open(SOURCE) as source:
        source.load()
        if source.size != EXPECTED_SOURCE_SIZE:
            raise ValueError(
                f"Expected source size {EXPECTED_SOURCE_SIZE}, got {source.size}"
            )
        source = source.convert("RGB")

    # Upper ceiling band only; no floor, seating, back bar, windows, or skyline.
    band_a = source.crop((0, 40, 2560, 540))
    band_a = fade_sides_to_black(band_a)
    save_jpeg(band_a, OUTPUT_A)

    # Tighter ceiling crop, stretched horizontally and abstracted after resizing.
    band_b = source.crop((560, 120, 1980, 620))
    band_b = band_b.resize(OUTPUT_SIZE, Image.Resampling.LANCZOS)
    band_b = band_b.filter(ImageFilter.GaussianBlur(radius=6))
    band_b = ImageEnhance.Contrast(band_b).enhance(1.15)
    band_b = ImageEnhance.Color(band_b).enhance(1.1)
    band_b = fade_sides_to_black(band_b)
    save_jpeg(band_b, OUTPUT_B)


if __name__ == "__main__":
    main()
