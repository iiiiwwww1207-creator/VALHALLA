#!/usr/bin/env python3
"""Render three deterministic, wide crimson views from a crowded club floor.

The image is built as a scene rather than a field of laser lines.  Architecture,
floor seams, stage, and lasers share one off-centre vanishing point.  Back beams
are occluded by a dense crowd while a few foreground beams cross over it.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter


HERE = Path(__file__).resolve().parent
OUTPUT_SIZE = (2560, 500)
JPEG_QUALITY = 92
SEEDS = (20261018, 7, 42)
TARGET_MEAN_LUMINANCE = (32.5, 35.0, 37.5)

# The requested palette.  Every emitted colour is neutral or crimson: there is
# intentionally no orange component anywhere in the renderer.
ROOM_BLACK = np.array((8, 5, 6), dtype=np.float32)
DARK_CRIMSON = np.array((60, 8, 12), dtype=np.float32)
MID_CRIMSON = np.array((193, 18, 31), dtype=np.float32)
HIGHLIGHT = np.array((224, 48, 60), dtype=np.float32)
HOT_CORE = np.array((255, 210, 205), dtype=np.float32)
SILHOUETTE = np.array((1, 0, 1), dtype=np.float32)
LUMA_WEIGHTS = np.array((0.2126, 0.7152, 0.0722), dtype=np.float32)


@dataclass(frozen=True)
class Beam:
    start: tuple[float, float]
    end: tuple[float, float]
    root_width: float
    tip_width: float
    strength: float
    foreground: bool


def add_colored_mask(
    canvas: np.ndarray,
    mask: Image.Image,
    color: np.ndarray,
    strength: float,
) -> None:
    alpha = np.asarray(mask, dtype=np.float32)[..., None] / 255.0
    canvas += alpha * color[None, None, :] * strength


def fractal_noise(
    rng: np.random.Generator,
    octaves: tuple[tuple[int, int, float], ...],
) -> np.ndarray:
    width, height = OUTPUT_SIZE
    result = np.zeros((height, width), dtype=np.float32)
    weight_sum = 0.0
    for cells_x, cells_y, weight in octaves:
        grid = rng.random((cells_y + 2, cells_x + 2), dtype=np.float32)
        small = Image.fromarray(np.uint8(np.rint(grid * 255.0)))
        octave = np.asarray(
            small.resize(OUTPUT_SIZE, Image.Resampling.BICUBIC), dtype=np.float32
        ) / 255.0
        result += octave * weight
        weight_sum += weight
    result /= weight_sum
    low, high = np.percentile(result, (2.0, 98.0))
    return np.clip((result - low) / max(high - low, 1e-6), 0.0, 1.0)


def choose_vanishing_point(rng: np.random.Generator) -> tuple[float, float]:
    """Keep the horizon above centre and nudge it visibly to either side."""
    width, height = OUTPUT_SIZE
    side = float(rng.choice((-1.0, 1.0)))
    return (
        width * (0.5 + side * rng.uniform(0.035, 0.075)),
        height * rng.uniform(0.365, 0.415),
    )


def draw_room(
    canvas: np.ndarray,
    vp: tuple[float, float],
    rng: np.random.Generator,
) -> np.ndarray:
    """Draw a low, dark room whose planes all resolve at the vanishing point."""
    width, height = OUTPUT_SIZE
    yy, xx = np.mgrid[0:height, 0:width].astype(np.float32)
    x = xx / (width - 1)
    y = yy / (height - 1)
    vp_x, vp_y = vp

    # The ceiling stays at the specified (8, 5, 6) away from emitted light.
    room_noise = fractal_noise(
        rng, ((5, 2, 1.0), (11, 4, 0.42), (23, 7, 0.15))
    )
    horizon_haze = np.exp(-((y - vp_y / height - 0.11) / 0.19) ** 2)
    canvas += (
        horizon_haze * (0.020 + 0.024 * room_noise)
    )[..., None] * DARK_CRIMSON

    architecture = Image.new("L", OUTPUT_SIZE, 0)
    draw = ImageDraw.Draw(architecture, "L")

    # Ceiling ribs and side-wall edges are faint but make the viewpoint legible.
    ceiling_origins = np.linspace(-240, width + 240, 15)
    ceiling_origins += rng.uniform(-65, 65, size=ceiling_origins.size)
    for index, top_x in enumerate(ceiling_origins):
        value = int(rng.integers(15, 31))
        draw.line((top_x, -8, vp_x, vp_y), fill=value, width=2 if index % 4 else 3)

    for side_x in (-60.0, width + 60.0):
        for wall_y in (62.0, 132.0, 236.0, 365.0):
            draw.line((side_x, wall_y, vp_x, vp_y), fill=22, width=2)

    # Receding cross-members become closer together around the horizon.
    for t in (0.18, 0.33, 0.47, 0.60, 0.72):
        left_x = (1.0 - t) * 0.0 + t * vp_x
        right_x = (1.0 - t) * width + t * vp_x
        rail_y = (1.0 - t) * 18.0 + t * vp_y
        draw.line((left_x, rail_y, right_x, rail_y), fill=18, width=2)

    architecture = architecture.filter(ImageFilter.GaussianBlur(0.65))
    add_colored_mask(canvas, architecture, MID_CRIMSON, 0.28)

    # Only the lowest ~18% reads as exposed floor.  Its edges and seams point
    # back to the same VP; most of it will later be interrupted by bodies.
    floor_top = int(height * 0.82)
    floor = np.clip((y - 0.80) / 0.20, 0.0, 1.0) ** 1.35
    floor *= 0.70 + 0.30 * room_noise
    canvas += floor[..., None] * DARK_CRIMSON * 0.15

    seams = Image.new("L", OUTPUT_SIZE, 0)
    seam_draw = ImageDraw.Draw(seams, "L")
    for bottom_x in np.linspace(-180, width + 180, 18):
        seam_draw.line((vp_x, vp_y, bottom_x, height + 8), fill=19, width=2)
    seam_draw.line((0, floor_top, width, floor_top), fill=18, width=1)
    for fraction in (0.88, 0.94):
        seam_y = int(height * fraction)
        distance = (seam_y - vp_y) / max(height - vp_y, 1.0)
        left = vp_x * (1.0 - distance)
        right = vp_x + (width - vp_x) * distance
        seam_draw.line((left, seam_y, right, seam_y), fill=15, width=1)
    floor_clip = Image.new("L", OUTPUT_SIZE, 0)
    ImageDraw.Draw(floor_clip).rectangle((0, floor_top, width, height), fill=255)
    seams = Image.fromarray(
        np.minimum(np.asarray(seams), np.asarray(floor_clip)).astype(np.uint8)
    )
    add_colored_mask(canvas, seams, MID_CRIMSON, 0.20)
    return room_noise


def render_stage_and_floor(
    canvas: np.ndarray,
    vp: tuple[float, float],
    room_noise: np.ndarray,
    rng: np.random.Generator,
) -> tuple[float, tuple[float, float]]:
    """Place the brightest horizontal band below the VP and reflect it on floor."""
    width, height = OUTPUT_SIZE
    vp_x, vp_y = vp
    stage_y = vp_y + rng.uniform(69.0, 83.0)
    half_width = rng.uniform(520.0, 690.0)
    stage_left = max(28.0, vp_x - half_width)
    stage_right = min(width - 28.0, vp_x + half_width)

    # A dark trapezoidal booth anchors the glow to an object in the room.
    booth = Image.new("L", OUTPUT_SIZE, 0)
    booth_draw = ImageDraw.Draw(booth, "L")
    booth_draw.polygon(
        (
            (stage_left + 85, stage_y + 8),
            (stage_right - 85, stage_y + 8),
            (stage_right + 55, stage_y + 87),
            (stage_left - 55, stage_y + 87),
        ),
        fill=92,
    )
    add_colored_mask(canvas, booth, DARK_CRIMSON, 0.38)

    band = Image.new("L", OUTPUT_SIZE, 0)
    band_draw = ImageDraw.Draw(band, "L")
    band_draw.rounded_rectangle(
        (stage_left, stage_y - 4, stage_right, stage_y + 7),
        radius=5,
        fill=255,
    )
    # Short breaks stop the band reading as an abstract single straight line.
    for _ in range(10):
        gap_x = rng.uniform(stage_left + 30, stage_right - 30)
        gap_w = rng.uniform(5, 17)
        band_draw.rectangle((gap_x, stage_y - 5, gap_x + gap_w, stage_y + 8), fill=90)

    large_glow = band.filter(ImageFilter.GaussianBlur(42.0))
    medium_glow = band.filter(ImageFilter.GaussianBlur(15.0))
    tight_glow = band.filter(ImageFilter.GaussianBlur(3.2))
    add_colored_mask(canvas, large_glow, MID_CRIMSON, 0.68)
    add_colored_mask(canvas, medium_glow, HIGHLIGHT, 1.02)
    add_colored_mask(canvas, tight_glow, HIGHLIGHT, 1.10)
    add_colored_mask(canvas, band, HOT_CORE, 1.34)

    # A few vertical fixtures give the stage a readable back wall.
    fixtures = Image.new("L", OUTPUT_SIZE, 0)
    fixture_draw = ImageDraw.Draw(fixtures, "L")
    for fixture_x in np.linspace(stage_left + 45, stage_right - 45, 11):
        fixture_x += rng.uniform(-21, 21)
        fixture_draw.rectangle(
            (fixture_x - 2, stage_y - rng.uniform(38, 65), fixture_x + 2, stage_y),
            fill=int(rng.integers(75, 145)),
        )
    add_colored_mask(
        canvas, fixtures.filter(ImageFilter.GaussianBlur(5.0)), HIGHLIGHT, 0.44
    )
    add_colored_mask(canvas, fixtures, HIGHLIGHT, 0.34)

    # Weak, vertically stretched reflections only on the lowest 18% of floor.
    reflection = np.zeros((height, width), dtype=np.float32)
    floor_top = int(height * 0.82)
    x_coords = np.arange(width, dtype=np.float32)
    y_coords = np.arange(height, dtype=np.float32)
    for _ in range(30):
        centre = rng.uniform(stage_left, stage_right)
        spread = rng.uniform(4.0, 23.0)
        length = rng.uniform(55.0, 165.0)
        x_profile = np.exp(-np.abs(x_coords - centre) / spread)
        y_profile = np.exp(-(height - 1 - y_coords) / length)
        y_profile[:floor_top] = 0.0
        ripple = 0.62 + 0.38 * np.sin(
            y_coords * rng.uniform(0.09, 0.18) + rng.uniform(0, np.pi * 2)
        )
        reflection += np.outer(y_profile * ripple, x_profile) * rng.uniform(0.18, 0.48)
    reflection *= 0.38 + 0.62 * room_noise
    reflection = np.clip(reflection, 0.0, 1.0)
    reflection_img = Image.fromarray(np.uint8(np.rint(reflection * 255.0)))
    reflection_img = reflection_img.filter(ImageFilter.GaussianBlur(3.5))
    add_colored_mask(canvas, reflection_img, HIGHLIGHT, 0.17)
    return stage_y, (stage_left, stage_right)


def make_beams(
    vp: tuple[float, float], rng: np.random.Generator
) -> tuple[list[Beam], list[tuple[float, float]]]:
    """Make tapered perspective beams with a strict 60/30/10 width mix."""
    width, height = OUTPUT_SIZE
    vp_x, vp_y = vp
    source_count = int(rng.integers(9, 13))
    source_xs = np.linspace(70, width - 70, source_count)
    source_xs += rng.uniform(-90, 90, source_count)
    sources = [
        (float(np.clip(x, 24, width - 24)), float(rng.uniform(16, 108)))
        for x in source_xs
    ]

    geometries: list[tuple[tuple[float, float], tuple[float, float], bool]] = []
    for source_index, source in enumerate(sources):
        sx, sy = source
        beam_count = int(rng.integers(2, 4))
        for beam_index in range(beam_count):
            # Five or six selected rays continue through the VP and over the
            # audience toward the camera.  The remainder terminate near stage.
            foreground = (source_index + beam_index * 4) % 6 == 0
            dx, dy = vp_x - sx, vp_y - sy
            if foreground:
                extension = rng.uniform(1.05, 2.25)
                ex = vp_x + dx * extension + rng.normal(0.0, 34.0)
                ey = vp_y + dy * extension + rng.normal(0.0, 10.0)
                if ey < height * 0.66:
                    ey = rng.uniform(height * 0.72, height * 1.08)
            else:
                extension = rng.uniform(-0.07, 0.42)
                ex = vp_x + dx * extension + rng.normal(0.0, 80.0)
                ey = vp_y + dy * extension + rng.normal(20.0, 46.0)
            geometries.append(
                (
                    (sx + rng.normal(0.0, 2.0), sy + rng.normal(0.0, 1.5)),
                    (float(ex), float(ey)),
                    foreground,
                )
            )

    count = len(geometries)
    classes = np.zeros(count, dtype=np.int8)
    order = rng.permutation(count)
    thin_count = int(round(count * 0.60))
    medium_count = int(round(count * 0.30))
    classes[order[thin_count : thin_count + medium_count]] = 1
    classes[order[thin_count + medium_count :]] = 2

    beams: list[Beam] = []
    for index, (start, end, foreground) in enumerate(geometries):
        width_class = int(classes[index])
        if width_class == 0:
            root_width = rng.uniform(0.8, 1.8)
            tip_width = rng.uniform(4.0, 8.0)
        elif width_class == 1:
            root_width = rng.uniform(1.8, 3.4)
            tip_width = rng.uniform(9.0, 18.0)
        else:
            root_width = rng.uniform(3.5, 6.0)
            tip_width = rng.uniform(21.0, 36.0)
        strength = rng.uniform(0.26, 0.62)
        if foreground:
            strength *= rng.uniform(0.90, 1.18)
            tip_width *= rng.uniform(1.15, 1.45)
        beams.append(
            Beam(
                start,
                end,
                float(root_width),
                float(tip_width),
                float(strength),
                foreground,
            )
        )
    return beams, sources


def cone_polygon(beam: Beam, scale: float) -> list[tuple[float, float]]:
    sx, sy = beam.start
    ex, ey = beam.end
    dx, dy = ex - sx, ey - sy
    length = max(float(np.hypot(dx, dy)), 1.0)
    nx, ny = -dy / length, dx / length
    root = beam.root_width * scale * 0.5
    tip = beam.tip_width * scale * 0.5
    return [
        (sx + nx * root, sy + ny * root),
        (ex + nx * tip, ey + ny * tip),
        (ex - nx * tip, ey - ny * tip),
        (sx - nx * root, sy - ny * root),
    ]


def beam_mask(beams: list[Beam], scale: float, alpha: float) -> Image.Image:
    layer = Image.new("L", OUTPUT_SIZE, 0)
    draw = ImageDraw.Draw(layer, "L")
    for beam in sorted(beams, key=lambda item: item.strength):
        value = int(np.clip(255.0 * beam.strength * alpha, 1, 255))
        draw.polygon(cone_polygon(beam, scale), fill=value)
    return layer


def render_beam_volume(
    beams: list[Beam],
    sources: list[tuple[float, float]],
    include_sources: bool,
) -> np.ndarray:
    """Return nested cone bodies plus restrained scattering as emitted light."""
    width, height = OUTPUT_SIZE
    light = np.zeros((height, width, 3), dtype=np.float32)
    if not beams:
        return light

    outer = beam_mask(beams, 1.0, 0.62)
    middle = beam_mask(beams, 0.48, 0.78)
    inner = beam_mask(beams, 0.13, 1.0)
    add_colored_mask(
        light, outer.filter(ImageFilter.GaussianBlur(2.8)), MID_CRIMSON, 0.24
    )
    add_colored_mask(light, outer, HIGHLIGHT, 0.40)
    add_colored_mask(light, middle, HIGHLIGHT, 0.27)
    add_colored_mask(
        light, inner.filter(ImageFilter.GaussianBlur(0.55)), HOT_CORE, 0.48
    )
    # Two scattering scales keep the beam volumetric without filling the ceiling.
    add_colored_mask(
        light, outer.filter(ImageFilter.GaussianBlur(19.0)), MID_CRIMSON, 0.075
    )
    add_colored_mask(
        light, outer.filter(ImageFilter.GaussianBlur(7.0)), HIGHLIGHT, 0.12
    )

    if include_sources:
        source_layer = Image.new("L", OUTPUT_SIZE, 0)
        source_draw = ImageDraw.Draw(source_layer, "L")
        for sx, sy in sources:
            radius = 3.2
            source_draw.ellipse(
                (sx - radius, sy - radius, sx + radius, sy + radius), fill=205
            )
        add_colored_mask(
            light,
            source_layer.filter(ImageFilter.GaussianBlur(9.0)),
            HIGHLIGHT,
            0.25,
        )
        add_colored_mask(light, source_layer, HOT_CORE, 0.52)
    return light


def add_stage_haze(
    canvas: np.ndarray,
    stage_y: float,
    stage_bounds: tuple[float, float],
    room_noise: np.ndarray,
    rng: np.random.Generator,
) -> None:
    """Add a thin smoky veil in front of the stage, not across the ceiling."""
    width, height = OUTPUT_SIZE
    yy, xx = np.mgrid[0:height, 0:width].astype(np.float32)
    left, right = stage_bounds
    centre = (left + right) * 0.5
    half_width = (right - left) * 0.66
    horizontal = np.exp(-((xx - centre) / half_width) ** 4)
    vertical = np.exp(-((yy - (stage_y + 18.0)) / 55.0) ** 2)
    wisps = fractal_noise(
        rng, ((7, 3, 1.0), (16, 5, 0.38), (32, 9, 0.13))
    )
    haze = horizontal * vertical * (0.30 + 0.42 * wisps + 0.28 * room_noise)
    haze_mask = Image.fromarray(np.uint8(np.rint(np.clip(haze, 0, 1) * 255)))
    haze_mask = haze_mask.filter(ImageFilter.GaussianBlur(8.0))
    add_colored_mask(canvas, haze_mask, MID_CRIMSON, 0.11)


def person_geometry(
    draw: ImageDraw.ImageDraw,
    cx: float,
    head_y: float,
    rx: float,
    ry: float,
    shoulder_width: float,
    bottom: float,
    raised_arm: int,
    fill: int,
) -> None:
    """Draw one faceless oval head and a softly sloped trapezoidal torso."""
    neck_half = rx * 0.42
    shoulder_y = head_y + ry * 0.70
    draw.ellipse((cx - rx, head_y - ry, cx + rx, head_y + ry), fill=fill)
    draw.rectangle(
        (cx - neck_half, head_y + ry * 0.54, cx + neck_half, shoulder_y + 8),
        fill=fill,
    )
    # Ellipse supplies a gradual shoulder curve; the trapezoid carries it down.
    draw.ellipse(
        (
            cx - shoulder_width,
            shoulder_y,
            cx + shoulder_width,
            shoulder_y + ry * 2.4,
        ),
        fill=fill,
    )
    draw.polygon(
        (
            (cx - shoulder_width * 0.88, shoulder_y + ry),
            (cx + shoulder_width * 0.88, shoulder_y + ry),
            (cx + shoulder_width * 0.75, bottom),
            (cx - shoulder_width * 0.75, bottom),
        ),
        fill=fill,
    )

    if raised_arm:
        side = -1.0 if raised_arm < 0 else 1.0
        shoulder_x = cx + side * shoulder_width * 0.62
        elbow_x = shoulder_x + side * rx * 0.62
        elbow_y = shoulder_y - ry * 1.10
        hand_x = elbow_x + side * rx * 0.24
        hand_y = head_y - ry * (2.1 + 0.35 * abs(raised_arm))
        arm_width = max(3.0, rx * 0.34)
        draw.line(
            (shoulder_x, shoulder_y + 4, elbow_x, elbow_y, hand_x, hand_y),
            fill=fill,
            width=max(4, int(round(arm_width * 2.0))),
            joint="curve",
        )
        hand_r = max(2.3, rx * 0.23)
        draw.ellipse(
            (hand_x - hand_r, hand_y - hand_r, hand_x + hand_r, hand_y + hand_r),
            fill=fill,
        )


def person_rim(
    draw: ImageDraw.ImageDraw,
    cx: float,
    head_y: float,
    rx: float,
    ry: float,
    shoulder_width: float,
    raised_arm: int,
    width: int,
    fill: int,
) -> None:
    """Draw only upward-facing edges, never facial marks or a full outline."""
    draw.arc(
        (cx - rx, head_y - ry, cx + rx, head_y + ry),
        start=180,
        end=360,
        fill=fill,
        width=width,
    )
    shoulder_y = head_y + ry * 0.70
    points = [
        (cx - shoulder_width * 0.96, shoulder_y + ry * 0.92),
        (cx - shoulder_width * 0.72, shoulder_y + ry * 0.34),
        (cx - rx * 0.56, shoulder_y + 2),
        (cx + rx * 0.56, shoulder_y + 2),
        (cx + shoulder_width * 0.72, shoulder_y + ry * 0.34),
        (cx + shoulder_width * 0.96, shoulder_y + ry * 0.92),
    ]
    draw.line(points, fill=fill, width=width, joint="curve")
    if raised_arm:
        side = -1.0 if raised_arm < 0 else 1.0
        shoulder_x = cx + side * shoulder_width * 0.62
        elbow_x = shoulder_x + side * rx * 0.62
        elbow_y = shoulder_y - ry * 1.10
        hand_x = elbow_x + side * rx * 0.24
        hand_y = head_y - ry * (2.1 + 0.35 * abs(raised_arm))
        offset = -side * max(1.0, rx * 0.20)
        draw.line(
            (
                shoulder_x + offset,
                shoulder_y,
                elbow_x + offset,
                elbow_y,
                hand_x + offset,
                hand_y,
            ),
            fill=fill,
            width=width,
            joint="curve",
        )


def make_crowd(
    vp: tuple[float, float], rng: np.random.Generator
) -> tuple[np.ndarray, np.ndarray, int, int]:
    """Build 60--100 irregular people, scaled smaller toward the VP."""
    width, height = OUTPUT_SIZE
    crowd = Image.new("L", OUTPUT_SIZE, 0)
    crowd_draw = ImageDraw.Draw(crowd, "L")
    rim = Image.new("L", OUTPUT_SIZE, 0)
    rim_draw = ImageDraw.Draw(rim, "L")

    # Far to near: the deeper rows are smaller, tighter, and higher in frame.
    row_specs = (
        (22, 335.0, 7.5, 10.5, 24.0, 391.0),
        (21, 363.0, 10.5, 14.5, 32.0, 426.0),
        (19, 398.0, 15.0, 20.0, 43.0, 469.0),
        (17, 442.0, 22.0, 29.0, 62.0, 528.0),
    )
    total = sum(spec[0] for spec in row_specs)
    arm_indices = set(rng.choice(total, size=max(1, round(total * 0.10)), replace=False))
    person_index = 0

    for row_index, (count, base_y, base_rx, base_ry, base_shoulder, bottom) in enumerate(
        row_specs
    ):
        # Normalised random gaps cover the width without betraying a regular
        # grid.  A second jitter breaks any rhythm left by the normalisation.
        gap_weights = rng.uniform(0.38, 1.70, size=count)
        centres = (np.cumsum(gap_weights) - gap_weights * 0.5)
        centres = centres / centres[-1] * (width + 95.0) - 47.5
        mean_gap = width / count
        centres += rng.uniform(-mean_gap * 0.18, mean_gap * 0.18, size=count)
        # Shift very distant figures slightly toward the shared VP.
        convergence = 0.06 * (3 - row_index)
        centres = centres * (1.0 - convergence) + vp[0] * convergence
        centres = np.clip(centres, -18, width + 18)

        for cx in centres:
            scale = rng.uniform(0.70, 1.31)
            rx = base_rx * scale * rng.uniform(0.82, 1.18)
            ry = base_ry * scale * rng.uniform(0.86, 1.15)
            shoulder = base_shoulder * scale * rng.uniform(0.79, 1.22)
            head_y = base_y + rng.uniform(-17.0, 17.0) * (0.62 + row_index * 0.15)
            person_bottom = bottom + rng.uniform(-16.0, 20.0)
            raised = 0
            if person_index in arm_indices:
                raised = int(rng.choice((-2, -1, 1, 2)))

            person_geometry(
                crowd_draw,
                float(cx),
                float(head_y),
                float(rx),
                float(ry),
                float(shoulder),
                float(person_bottom),
                raised,
                255,
            )
            rim_width = 1 if row_index < 2 else 2
            person_rim(
                rim_draw,
                float(cx),
                float(head_y),
                float(rx),
                float(ry),
                float(shoulder),
                raised,
                rim_width,
                int(rng.integers(130, 211)),
            )
            person_index += 1

    crowd_array = np.asarray(crowd, dtype=np.float32) / 255.0
    # A tiny blur affects only the rim, keeping the silhouettes completely black.
    rim = rim.filter(ImageFilter.GaussianBlur(0.32))
    rim_array = np.asarray(rim, dtype=np.float32) / 255.0
    return crowd_array, rim_array, total, len(arm_indices)


def mean_luminance(rgb: np.ndarray) -> float:
    values = np.asarray(rgb, dtype=np.float64)
    luminance = (
        values[..., 0] * float(LUMA_WEIGHTS[0])
        + values[..., 1] * float(LUMA_WEIGHTS[1])
        + values[..., 2] * float(LUMA_WEIGHTS[2])
    )
    return float(np.mean(luminance))


def composite_exposed(
    scene: np.ndarray,
    crowd: np.ndarray,
    rim: np.ndarray,
    foreground_light: np.ndarray,
    exposure: float,
) -> np.ndarray:
    """Expose emitted light, then apply the scene's deliberate occlusion order."""
    emitted = np.maximum(scene - ROOM_BLACK[None, None, :], 0.0)
    exposed = ROOM_BLACK[None, None, :] + 247.0 * (
        1.0 - np.exp(-emitted * exposure / 247.0)
    )

    # The audience is truly black.  The rim is laid on top but restricted to
    # upward contours by construction; no face data is ever generated.
    exposed = exposed * (1.0 - crowd[..., None]) + SILHOUETTE * crowd[..., None]
    rim_alpha = np.clip(rim * 0.92, 0.0, 1.0)[..., None]
    rim_colour = MID_CRIMSON * 0.66 + HIGHLIGHT * 0.34
    exposed = exposed * (1.0 - rim_alpha) + rim_colour * rim_alpha

    # Foreground cones are composited after the silhouettes, which makes their
    # crossings unambiguously nearer to the camera than the audience.
    front = 255.0 * (1.0 - np.exp(-foreground_light * exposure / 255.0))
    exposed += front
    return np.clip(exposed, 0.0, 255.0)


def finish_image(
    scene: np.ndarray,
    crowd: np.ndarray,
    rim: np.ndarray,
    foreground_light: np.ndarray,
    target_luminance: float,
) -> Image.Image:
    low, high = 0.04, 18.0
    for _ in range(38):
        middle = (low + high) * 0.5
        candidate = composite_exposed(scene, crowd, rim, foreground_light, middle)
        if mean_luminance(candidate) < target_luminance:
            low = middle
        else:
            high = middle
    final = composite_exposed(scene, crowd, rim, foreground_light, (low + high) * 0.5)
    return Image.fromarray(np.uint8(np.rint(final)))


def generate_variant(
    seed: int, target_luminance: float
) -> tuple[Image.Image, tuple[float, float], int, int, int]:
    rng = np.random.default_rng(seed)
    width, height = OUTPUT_SIZE
    canvas = np.broadcast_to(ROOM_BLACK, (height, width, 3)).copy()
    vp = choose_vanishing_point(rng)
    room_noise = draw_room(canvas, vp, rng)
    stage_y, stage_bounds = render_stage_and_floor(canvas, vp, room_noise, rng)
    beams, sources = make_beams(vp, rng)
    back_beams = [beam for beam in beams if not beam.foreground]
    front_beams = [beam for beam in beams if beam.foreground]
    canvas += render_beam_volume(back_beams, sources, include_sources=True)
    add_stage_haze(canvas, stage_y, stage_bounds, room_noise, rng)
    crowd, rim, people, raised_arms = make_crowd(vp, rng)
    foreground_light = render_beam_volume(front_beams, [], include_sources=False)
    image = finish_image(canvas, crowd, rim, foreground_light, target_luminance)
    return image, vp, people, raised_arms, len(front_beams)


def main() -> None:
    for index, (seed, target) in enumerate(
        zip(SEEDS, TARGET_MEAN_LUMINANCE), start=1
    ):
        output = HERE / f"laser_gen_{index}.jpg"
        generated, vp, people, raised_arms, foreground_beams = generate_variant(
            seed, target
        )
        generated.save(
            output,
            "JPEG",
            quality=JPEG_QUALITY,
            subsampling=0,
            optimize=True,
        )
        with Image.open(output) as saved:
            saved_rgb = np.asarray(saved.convert("RGB"), dtype=np.float32)
            measured = mean_luminance(saved_rgb)
            saved_size = saved.size
        print(
            f"{output.name}: seed={seed}, size={saved_size}, quality={JPEG_QUALITY}, "
            f"mean_luminance={measured:.2f}, vp=({vp[0]:.1f},{vp[1]:.1f}), "
            f"people={people}, raised_arms={raised_arms}, "
            f"foreground_beams={foreground_beams}"
        )


if __name__ == "__main__":
    main()
