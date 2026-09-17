#!/usr/bin/env python3
"""Create the text-free 4:5 base photo for the charity livestream banner."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageStat


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "group_field_stream.jpg"
OUTPUT = HERE / "stream_base_1080x1350.jpg"

OUTPUT_SIZE = (1080, 1350)

# Source-space crop: 2108 x 2635 = 4:5. Keep the source's right and bottom
# edges to protect all three people while placing KØU's face centre at about
# y=583 in the finished frame. RAY retains visible headroom at the top.
CROP_BOX = (335, 1029, 2443, 3664)

# Face bounds measured in the 2443 x 3664 source and visually checked against
# the eyes, chin and hairline. Values are (left, top, right, bottom).
FACE_BOXES = {
    "left / blue hair": (823, 1648, 1039, 1864),
    "centre / black hair (KOU)": (1189, 2055, 1413, 2279),
    "right / white hair (RAY)": (1479, 1259, 1699, 1479),
}

# Topmost visible white strand, measured in the source image.
RAY_HEAD_TOP_Y = 1110

# Keep the fade entirely below KOU's measured chin. The extra source-space
# margin prevents resampling from leaking the black overlay onto the face.
KOU_FACE_BOTTOM_Y = FACE_BOXES["centre / black hair (KOU)"][3]
BOTTOM_GRADIENT_MARGIN_SOURCE = 28


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


def output_point(source_x: float, source_y: float) -> tuple[float, float]:
    """Map a point from source space into the resized output."""
    crop_left, crop_top, crop_right, crop_bottom = CROP_BOX
    output_width, output_height = OUTPUT_SIZE
    return (
        (source_x - crop_left) * output_width / (crop_right - crop_left),
        (source_y - crop_top) * output_height / (crop_bottom - crop_top),
    )


def lift_kou_face(image: Image.Image, amount: float = 1.12) -> Image.Image:
    """Gently lift KOU's face with a generously feathered elliptical mask."""
    left, top, right, bottom = FACE_BOXES["centre / black hair (KOU)"]
    centre_x, centre_y = output_point((left + right) / 2, (top + bottom) / 2)
    face_width = (right - left) * OUTPUT_SIZE[0] / (CROP_BOX[2] - CROP_BOX[0])
    face_height = (bottom - top) * OUTPUT_SIZE[1] / (CROP_BOX[3] - CROP_BOX[1])

    # The solid ellipse covers the face; the blur makes the transition around
    # it broad enough to remain invisible after JPEG encoding.
    radius_x = face_width * 0.58
    radius_y = face_height * 0.62
    mask = Image.new("L", image.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse(
        (
            round(centre_x - radius_x),
            round(centre_y - radius_y),
            round(centre_x + radius_x),
            round(centre_y + radius_y),
        ),
        fill=255,
    )
    mask = mask.filter(ImageFilter.GaussianBlur(radius=42))
    lifted = ImageEnhance.Brightness(image).enhance(amount)
    return Image.composite(lifted, image, mask)


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
    image = lift_kou_face(image)

    width, height = image.size

    kou_face_bottom_output = output_point(0, KOU_FACE_BOTTOM_Y)[1]
    bottom_start = round(
        output_point(0, KOU_FACE_BOTTOM_Y + BOTTOM_GRADIENT_MARGIN_SOURCE)[1]
    )
    image = composite_black(
        image,
        vertical_black_gradient(
            image.size, bottom_start, height - 1, 0.0, 0.92, curve_power=0.9
        ),
    )

    # No top gradient: only a very light edge vignette remains.
    image = composite_black(
        image, vignette_overlay(image.size, max_alpha=0.07)
    ).convert("RGB")
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
    for label, (left, top, right, bottom) in FACE_BOXES.items():
        face_y = (top + bottom) / 2
        output_y = output_point((left + right) / 2, face_y)[1]
        print(f"Face {label}: source centre y={face_y:.1f}, output y={output_y:.1f}")
    ray_headroom = output_point(0, RAY_HEAD_TOP_Y)[1]
    print(
        f"KOU face bottom: source y={KOU_FACE_BOTTOM_Y}, "
        f"output y={kou_face_bottom_output:.1f}"
    )
    print(
        f"Bottom gradient: output start y={bottom_start} "
        f"({bottom_start - kou_face_bottom_output:.1f}px below KOU face)"
    )
    print(
        f"RAY headroom: source {RAY_HEAD_TOP_Y - crop_top}px, "
        f"output {ray_headroom:.1f}px ({ray_headroom / height:.1%})"
    )
    print(f"Gradient region mean luminance: {lower_mean:.2f} / 255")


if __name__ == "__main__":
    main()
