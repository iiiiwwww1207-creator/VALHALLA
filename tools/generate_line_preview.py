#!/usr/bin/env python3
"""Generate a LINE official-account image placement preview."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[1]
COVER_PATH = ROOT / "dist" / "line_cover.png"
ICON_PATH = ROOT / "dist" / "line_icon.png"
OUTPUT_PATH = ROOT / "dist" / "line_preview_check.png"

CANVAS_WIDTH = 1400
SIDE_PADDING = 100
TOP_BOTTOM_PADDING = 80
SECTION_GAP = 48
LABEL_CONTENT_GAP = 20
BACKGROUND = (242, 242, 245, 255)
LABEL_COLOR = (51, 51, 51, 255)


def load_font(size: int) -> ImageFont.ImageFont:
    for path in (
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
    ):
        try:
            return ImageFont.truetype(path, size=size)
        except (OSError, ValueError):
            pass
    return ImageFont.load_default()


def text_size(font: ImageFont.ImageFont, text: str) -> tuple[int, int]:
    box = font.getbbox(text)
    return box[2] - box[0], box[3] - box[1]


def circular_icon(source: Image.Image, diameter: int) -> Image.Image:
    fitted = ImageOps.fit(source.convert("RGB"), (diameter, diameter), Image.Resampling.LANCZOS)

    # Draw the mask large and reduce it for a clean antialiased circular edge.
    scale = 4
    mask_large = Image.new("L", (diameter * scale, diameter * scale), 0)
    ImageDraw.Draw(mask_large).ellipse(
        (0, 0, diameter * scale - 1, diameter * scale - 1), fill=255
    )
    mask = mask_large.resize((diameter, diameter), Image.Resampling.LANCZOS)

    result = Image.new("RGBA", (diameter, diameter), (0, 0, 0, 0))
    result.paste(fitted, (0, 0), mask)
    ImageDraw.Draw(result).ellipse(
        (1, 1, diameter - 2, diameter - 2),
        outline=(200, 200, 205, 255),
        width=2,
    )
    return result


def centered_text(
    draw: ImageDraw.ImageDraw,
    center: tuple[float, float],
    text: str,
    font: ImageFont.ImageFont,
    fill: tuple[int, int, int, int],
) -> None:
    draw.text(center, text, font=font, fill=fill, anchor="mm")


def main() -> None:
    label_font = load_font(28)
    note_font = load_font(24)
    small_font = load_font(20)

    label_a = "COVER 1200x600 - overlay safe area"
    label_b = "PROFILE ICON - circular crop"
    label_c = "ICON at real display sizes"
    label_height = max(text_size(label_font, text)[1] for text in (label_a, label_b, label_c))

    cover_height = 600
    icon_large = 360
    real_sizes = (120, 72, 44)
    size_label_gap = 16
    small_label_height = max(text_size(small_font, f"{size}px")[1] for size in real_sizes)
    section_c_content_height = max(real_sizes) + size_label_gap + small_label_height

    section_a_height = label_height + LABEL_CONTENT_GAP + cover_height
    section_b_height = label_height + LABEL_CONTENT_GAP + icon_large
    section_c_height = label_height + LABEL_CONTENT_GAP + section_c_content_height
    canvas_height = (
        TOP_BOTTOM_PADDING * 2
        + section_a_height
        + section_b_height
        + section_c_height
        + SECTION_GAP * 2
    )

    canvas = Image.new("RGBA", (CANVAS_WIDTH, canvas_height), BACKGROUND)
    draw = ImageDraw.Draw(canvas)
    x = SIDE_PADDING
    y = TOP_BOTTOM_PADDING

    with Image.open(COVER_PATH) as cover_source:
        cover = cover_source.convert("RGBA")
        if cover.size != (1200, 600):
            cover = cover.resize((1200, 600), Image.Resampling.LANCZOS)

    draw.text((x, y), label_a, font=label_font, fill=LABEL_COLOR)
    cover_y = y + label_height + LABEL_CONTENT_GAP
    canvas.alpha_composite(cover, (x, cover_y))

    overlay = Image.new("RGBA", cover.size, (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    side_width = 120
    bottom_height = 150
    overlay_draw.rectangle((0, 0, side_width - 1, 599), fill=(0, 0, 0, round(255 * 0.18)))
    overlay_draw.rectangle((1200 - side_width, 0, 1199, 599), fill=(0, 0, 0, round(255 * 0.18)))
    overlay_draw.rectangle(
        (0, 600 - bottom_height, 1199, 599), fill=(220, 40, 50, round(255 * 0.25))
    )
    overlay_draw.line((0, 600 - bottom_height, 1199, 600 - bottom_height), fill=(220, 40, 50, 255), width=3)

    overlay_draw.text(
        (12, 20),
        "may be cropped",
        font=note_font,
        fill=(255, 255, 255, 255),
        anchor="la",
    )
    overlay_draw.text(
        (1188, 20),
        "may be cropped",
        font=note_font,
        fill=(255, 255, 255, 255),
        anchor="ra",
    )
    centered_text(
        overlay_draw,
        (600, 600 - bottom_height / 2),
        "LINE overlays account name / ID here",
        note_font,
        (255, 255, 255, 255),
    )
    canvas.alpha_composite(overlay, (x, cover_y))

    y += section_a_height + SECTION_GAP
    draw.text((x, y), label_b, font=label_font, fill=LABEL_COLOR)
    icon_y = y + label_height + LABEL_CONTENT_GAP

    with Image.open(ICON_PATH) as icon_source:
        icon = icon_source.convert("RGB")
        canvas.alpha_composite(circular_icon(icon, icon_large), (x, icon_y))

        y += section_b_height + SECTION_GAP
        draw.text((x, y), label_c, font=label_font, fill=LABEL_COLOR)
        row_y = y + label_height + LABEL_CONTENT_GAP
        current_x = x
        for diameter in real_sizes:
            canvas.alpha_composite(circular_icon(icon, diameter), (current_x, row_y))
            centered_text(
                draw,
                (current_x + diameter / 2, row_y + diameter + size_label_gap + small_label_height / 2),
                f"{diameter}px",
                small_font,
                LABEL_COLOR,
            )
            current_x += diameter + 60

    canvas.convert("RGB").save(OUTPUT_PATH, format="PNG", optimize=True)
    print(f"{OUTPUT_PATH.relative_to(ROOT)} {CANVAS_WIDTH}x{canvas_height}")


if __name__ == "__main__":
    main()
