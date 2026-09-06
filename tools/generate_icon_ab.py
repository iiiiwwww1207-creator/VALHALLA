#!/usr/bin/env python3
"""Generate an A/B comparison sheet for LINE profile icons."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


ROOT = Path(__file__).resolve().parents[1]
ICON_A_PATH = ROOT / "dist" / "line_icon.png"
ICON_B_PATH = ROOT / "dist" / "line_icon_b.png"
OUTPUT_PATH = ROOT / "dist" / "line_icon_ab.png"

CANVAS_WIDTH = 1200
SIDE_PADDING = 80
TOP_BOTTOM_PADDING = 64
CONTENT_WIDTH = CANVAS_WIDTH - SIDE_PADDING * 2
BACKGROUND = (242, 242, 245, 255)
TEXT_COLOR = (51, 51, 51, 255)
CHAT_TEXT_COLOR = (17, 17, 17, 255)
OUTLINE_COLOR = (200, 200, 205, 255)

TITLE = "PROFILE ICON  A / B  at real display sizes"
ICON_SIZES = (240, 120, 72, 44)
LABEL_WIDTH = 220
ICON_GAP = 56
ROW_GAP = 64
SIZE_LABEL_GAP = 14


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


def text_height(font: ImageFont.ImageFont, text: str) -> int:
    box = font.getbbox(text)
    return box[3] - box[1]


def circular_icon(source: Image.Image, diameter: int) -> Image.Image:
    fitted = ImageOps.fit(
        source.convert("RGB"), (diameter, diameter), Image.Resampling.LANCZOS
    )

    scale = 4
    mask_large = Image.new("L", (diameter * scale, diameter * scale), 0)
    ImageDraw.Draw(mask_large).ellipse(
        (0, 0, diameter * scale - 1, diameter * scale - 1), fill=255
    )
    mask = mask_large.resize((diameter, diameter), Image.Resampling.LANCZOS)

    result = Image.new("RGBA", (diameter, diameter), (0, 0, 0, 0))
    result.paste(fitted, (0, 0), mask)
    ImageDraw.Draw(result).ellipse(
        (1, 1, diameter - 2, diameter - 2), outline=OUTLINE_COLOR, width=2
    )
    return result


def draw_icon_row(
    canvas: Image.Image,
    draw: ImageDraw.ImageDraw,
    source: Image.Image,
    label: str,
    top: int,
    row_height: int,
    label_font: ImageFont.ImageFont,
    size_font: ImageFont.ImageFont,
) -> None:
    circle_area_height = max(ICON_SIZES)
    draw.text(
        (SIDE_PADDING, top + circle_area_height / 2),
        label,
        font=label_font,
        fill=TEXT_COLOR,
        anchor="lm",
    )

    current_x = SIDE_PADDING + LABEL_WIDTH
    for diameter in ICON_SIZES:
        icon_y = top + (circle_area_height - diameter) // 2
        canvas.alpha_composite(circular_icon(source, diameter), (current_x, icon_y))
        draw.text(
            (current_x + diameter / 2, top + circle_area_height + SIZE_LABEL_GAP),
            f"{diameter}px",
            font=size_font,
            fill=TEXT_COLOR,
            anchor="ma",
        )
        current_x += diameter + ICON_GAP


def main() -> None:
    title_font = load_font(32)
    row_label_font = load_font(24)
    size_font = load_font(18)
    chat_font = load_font(22)

    title_height = text_height(title_font, TITLE)
    size_label_height = max(text_height(size_font, f"{size}px") for size in ICON_SIZES)
    row_height = max(ICON_SIZES) + SIZE_LABEL_GAP + size_label_height

    title_to_rows_gap = 48
    rows_to_chat_gap = 64
    chat_label_gap = 20
    chat_label_height = text_height(row_label_font, "in a chat list (56px)")
    band_height = 88
    band_gap = 16
    canvas_height = (
        TOP_BOTTOM_PADDING
        + title_height
        + title_to_rows_gap
        + row_height * 2
        + ROW_GAP
        + rows_to_chat_gap
        + chat_label_height
        + chat_label_gap
        + band_height * 2
        + band_gap
        + TOP_BOTTOM_PADDING
    )

    canvas = Image.new("RGBA", (CANVAS_WIDTH, canvas_height), BACKGROUND)
    draw = ImageDraw.Draw(canvas)

    y = TOP_BOTTOM_PADDING
    draw.text((SIDE_PADDING, y), TITLE, font=title_font, fill=TEXT_COLOR)
    y += title_height + title_to_rows_gap

    with Image.open(ICON_A_PATH) as source_a, Image.open(ICON_B_PATH) as source_b:
        icon_a = source_a.convert("RGB")
        icon_b = source_b.convert("RGB")

        draw_icon_row(
            canvas, draw, icon_a, "A  logo + text", y, row_height, row_label_font, size_font
        )
        y += row_height + ROW_GAP
        draw_icon_row(
            canvas, draw, icon_b, "B  logo first", y, row_height, row_label_font, size_font
        )
        y += row_height + rows_to_chat_gap

        draw.text(
            (SIDE_PADDING, y),
            "in a chat list (56px)",
            font=row_label_font,
            fill=TEXT_COLOR,
        )
        y += chat_label_height + chat_label_gap

        for source in (icon_a, icon_b):
            draw.rounded_rectangle(
                (SIDE_PADDING, y, SIDE_PADDING + CONTENT_WIDTH - 1, y + band_height - 1),
                radius=12,
                fill=(255, 255, 255, 255),
            )
            icon_x = SIDE_PADDING + 20
            icon_y = y + (band_height - 56) // 2
            canvas.alpha_composite(circular_icon(source, 56), (icon_x, icon_y))
            draw.text(
                (icon_x + 56 + 24, y + band_height / 2),
                "VALHALLA CHARITYLIVE",
                font=chat_font,
                fill=CHAT_TEXT_COLOR,
                anchor="lm",
            )
            y += band_height + band_gap

    canvas.convert("RGB").save(OUTPUT_PATH, format="PNG", optimize=True)
    print(f"{OUTPUT_PATH.relative_to(ROOT)} {CANVAS_WIDTH}x{canvas_height}")


if __name__ == "__main__":
    main()
