#!/usr/bin/env python3
"""Create the text-free 4:5 base photo for the charity livestream banner."""

from pathlib import Path

from PIL import Image, ImageEnhance, ImageStat


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "group_field_stream.jpg"
OUTPUT = HERE / "stream_base_1080x1350.jpg"

OUTPUT_SIZE = (1080, 1350)

# Source-space crop: 2240 x 2800 = 4:5. It keeps all three faces and their
# upper bodies, while shifting slightly right to balance the group in-frame.
CROP_BOX = (203, 700, 2443, 3500)

# Manually inspected approximate face centres in the 2443 x 3664 source.
FACE_CENTRES = {
    "left / blue hair": (945, 1750),
    "centre / black hair": (1300, 2180),
    "right / white hair": (1605, 1390),
}


def smoothstep(value: float) -> float:
    """Return a smooth 0..1 interpolation with soft ends."""
    value = max(0.0, min(1.0, value))
    return value * value * (3.0 - 2.0 * value)


def vertical_black_gradient(
    size: tuple[int, int],
    start_y: int,
    end_y: int,
    start_alpha: float,
    end_alpha: float,
    curve_power: float = 1.0,
) -> Image.Image:
    """Build an RGBA black overlay whose alpha varies smoothly by row."""
    width, height = size
    span = max(1, end_y - start_y)
    row_values = []
    for y in range(height):
        linear_t = max(0.0, min(1.0, (y - start_y) / span))
        t = smoothstep(linear_t**curve_power)
        alpha = start_alpha + (end_alpha - start_alpha) * t
        if y < start_y:
            alpha = start_alpha
        elif y > end_y:
            alpha = end_alpha
        row_values.append(round(255 * alpha))

    alpha_strip = Image.new("L", (1, height))
    alpha_strip.putdata(row_values)
    alpha_mask = alpha_strip.resize((width, height))
    overlay = Image.new("RGBA", size, (0, 0, 0, 0))
    overlay.putalpha(alpha_mask)
    return overlay


def vignette_overlay(size: tuple[int, int], max_alpha: float = 0.13) -> Image.Image:
    """Create a restrained elliptical vignette, reaching max_alpha at corners."""
    width, height = size
    cx = (width - 1) / 2.0
    cy = (height - 1) / 2.0
    corner_distance = (cx * cx + cy * cy) ** 0.5
    pixels = []
    for y in range(height):
        dy = y - cy
        for x in range(width):
            distance = (((x - cx) ** 2 + dy * dy) ** 0.5) / corner_distance
            # The centre and broad middle stay untouched; falloff begins at 55%.
            amount = smoothstep((distance - 0.55) / 0.45)
            pixels.append(round(255 * max_alpha * amount))

    mask = Image.new("L", size)
    mask.putdata(pixels)
    overlay = Image.new("RGBA", size, (0, 0, 0, 0))
    overlay.putalpha(mask)
    return overlay


def composite_black(image: Image.Image, overlay: Image.Image) -> Image.Image:
    return Image.alpha_composite(image.convert("RGBA"), overlay)


def main() -> None:
    with Image.open(SOURCE) as source:
        source = source.convert("RGB")
        if source.size != (2443, 3664):
            raise ValueError(f"Unexpected source size: {source.size}; expected (2443, 3664)")

        image = source.crop(CROP_BOX)
        image = image.resize(OUTPUT_SIZE, Image.Resampling.LANCZOS)

    image = ImageEnhance.Brightness(image).enhance(0.82)
    image = ImageEnhance.Contrast(image).enhance(1.08)
    image = ImageEnhance.Color(image).enhance(0.92)

    width, height = image.size

    # Bottom 45%: transparent at 55% height, smoothly reaching 0.88 at bottom.
    bottom_start = round(height * 0.55)
    image = composite_black(
        image,
        # A mild 0.8 power brings darkness in a little earlier, leaving a broad
        # quiet area for white type while retaining a soft, monotonic fade.
        vertical_black_gradient(
            image.size, bottom_start, height - 1, 0.0, 0.88, curve_power=0.8
        ),
    )

    # Top: 0.55 at the first row, smoothly fading to clear at 18% height.
    top_end = round(height * 0.18)
    image = composite_black(
        image,
        vertical_black_gradient(image.size, 0, top_end, 0.55, 0.0),
    )

    image = composite_black(image, vignette_overlay(image.size)).convert("RGB")
    image.save(OUTPUT, "JPEG", quality=94, optimize=True)

    # Measure the encoded deliverable, not the pre-JPEG working image.
    with Image.open(OUTPUT) as result:
        result.load()
        lower_region = result.crop((0, bottom_start, width, height)).convert("L")
        lower_mean = ImageStat.Stat(lower_region).mean[0]

    crop_left, crop_top, crop_right, crop_bottom = CROP_BOX
    print(f"Wrote: {OUTPUT}")
    print(f"Output size: {width}x{height}")
    print(f"Crop box: x={crop_left}..{crop_right}, y={crop_top}..{crop_bottom}")
    for label, (face_x, face_y) in FACE_CENTRES.items():
        output_y = (face_y - crop_top) * height / (crop_bottom - crop_top)
        print(f"Face {label}: source y={face_y}, output y≈{output_y:.1f}")
    print(f"Lower 45% mean luminance: {lower_mean:.2f} / 255")


if __name__ == "__main__":
    main()
