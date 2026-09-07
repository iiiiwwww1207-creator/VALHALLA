#!/usr/bin/env python3
"""Generate three wide crimson laser-and-smoke bands for the charity flyer.

Everything is rendered procedurally from fixed seeds.  Beams are tapered light
volumes rather than stroked lines: each has a narrow origin, a wider far end,
a bright inner volume, feathered edges, and two additive scattering halos.
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
TARGET_MEAN_LUMINANCE = (30.0, 34.0, 37.0)

# Project crimson palette.  Deliberately no orange/yellow laser colors.
NEAR_BLACK = np.array((8, 5, 6), dtype=np.float32)
MID_CRIMSON = np.array((193, 18, 31), dtype=np.float32)
BRIGHT_CRIMSON = np.array((224, 48, 60), dtype=np.float32)
HOT_CORE = np.array((255, 238, 235), dtype=np.float32)
LUMA_WEIGHTS = np.array((0.2126, 0.7152, 0.0722), dtype=np.float32)


@dataclass(frozen=True)
class Beam:
    """Geometry and depth for one tapered beam."""

    start: tuple[float, float]
    end: tuple[float, float]
    root_width: float
    tip_width: float
    depth: float
    strength: float


def add_colored_mask(
    canvas: np.ndarray,
    mask: Image.Image,
    color: np.ndarray,
    strength: float,
) -> None:
    """Add a colored grayscale mask to the floating-point RGB canvas."""
    alpha = np.asarray(mask, dtype=np.float32)[..., None] / 255.0
    canvas += alpha * color[None, None, :] * strength


def fractal_noise(
    width: int,
    height: int,
    rng: np.random.Generator,
    octaves: tuple[tuple[int, int, float], ...],
) -> np.ndarray:
    """Return smooth, low-frequency value noise assembled like Perlin octaves."""
    noise = np.zeros((height, width), dtype=np.float32)
    total_weight = 0.0
    for cells_x, cells_y, weight in octaves:
        # An extra cell around the field keeps interpolation from flattening the
        # outside edge, which matters when the banner is cropped horizontally.
        grid = rng.random((cells_y + 2, cells_x + 2), dtype=np.float32)
        small = Image.fromarray(np.uint8(np.rint(grid * 255.0)))
        smooth = small.resize((width, height), Image.Resampling.BICUBIC)
        octave = np.asarray(smooth, dtype=np.float32) / 255.0
        noise += octave * weight
        total_weight += weight
    noise /= total_weight
    low, high = np.percentile(noise, (2.0, 98.0))
    return np.clip((noise - low) / max(high - low, 1e-6), 0.0, 1.0)


def make_smoke(
    width: int, height: int, rng: np.random.Generator
) -> tuple[np.ndarray, np.ndarray]:
    """Create a near-black base with only a trace of full-frame smoke."""
    yy, xx = np.mgrid[0:height, 0:width].astype(np.float32)
    x = xx / (width - 1)
    y = yy / (height - 1)

    broad = fractal_noise(
        width,
        height,
        rng,
        ((5, 2, 1.0), (10, 4, 0.52), (21, 7, 0.24), (43, 13, 0.10)),
    )
    wisps = fractal_noise(
        width,
        height,
        rng,
        ((8, 3, 1.0), (17, 6, 0.46), (35, 11, 0.18)),
    )
    # Wide sinusoidal density folds prevent the texture from reading as a flat
    # cloud while remaining present at every horizontal position.
    phase = rng.uniform(0.0, np.pi * 2.0)
    fold = 0.5 + 0.5 * np.sin(
        x * rng.uniform(3.1, 5.2) * np.pi
        + y * rng.uniform(1.0, 2.1) * np.pi
        + phase
        + broad * 2.2
    )
    ceiling_haze = np.exp(-((y - rng.uniform(0.24, 0.40)) / 0.44) ** 2)
    smoke = np.clip(0.13 + 0.53 * broad + 0.20 * wisps + 0.14 * fold, 0.0, 1.0)
    smoke *= 0.76 + 0.24 * ceiling_haze

    # Keep the unlit room genuinely black.  The global smoke contribution is
    # one fifth of the previous version; most visible haze is added later from
    # blurred beam masks, so areas away from beams fall back to (8, 5, 6).
    canvas = np.broadcast_to(NEAR_BLACK, (height, width, 3)).copy()
    canvas += (smoke**1.65)[..., None] * MID_CRIMSON[None, None, :] * 0.040

    # A second, blurrier emissive layer creates air volume across the full band.
    smoke_mask = Image.fromarray(np.uint8(np.rint(smoke * 255.0)))
    smoke_glow = smoke_mask.filter(ImageFilter.GaussianBlur(radius=22.0))
    add_colored_mask(canvas, smoke_glow, BRIGHT_CRIMSON, 0.015)
    return canvas, smoke


def distribute_sources(
    width: int, height: int, rng: np.random.Generator
) -> list[tuple[float, float]]:
    """Place 7--10 sources irregularly while keeping the entire width covered."""
    count = int(rng.integers(8, 11))

    # Start with full-width strata for coverage, then warp and jitter them.  The
    # sinusoidal warp plus one deliberate close pair gives visible coarse/dense
    # grouping without allowing a large dead interval.
    positions = (np.arange(count, dtype=np.float32) + 0.5) / count
    positions += 0.032 * np.sin(
        positions * np.pi * rng.uniform(2.5, 4.8) + rng.uniform(0, 2 * np.pi)
    )
    positions += rng.uniform(-0.026, 0.026, size=count)
    pair = int(rng.integers(1, count - 1))
    positions[pair] = positions[pair - 1] + rng.uniform(0.030, 0.050)
    positions = np.sort(np.clip(positions, 0.018, 0.982))

    # Pin the outer sources close enough to each edge that even aggressive flyer
    # crops retain both haze and at least part of a beam fan.
    positions[0] = rng.uniform(0.018, 0.038)
    positions[-1] = rng.uniform(0.962, 0.982)
    sources: list[tuple[float, float]] = []
    for index, position in enumerate(positions):
        y_band = 0 if index % 3 else 1
        y = rng.uniform(18, 72) + y_band * rng.uniform(24, 55)
        sources.append((float(position * width), float(min(y, height * 0.27))))
    return sources


def make_beams(
    sources: list[tuple[float, float]], rng: np.random.Generator
) -> list[Beam]:
    """Create depth-sorted tapered beams from every source."""
    width, height = OUTPUT_SIZE
    beams: list[Beam] = []
    geometries: list[tuple[tuple[float, float], tuple[float, float], float]] = []
    for source_index, (sx, sy) in enumerate(sources):
        count = int(rng.integers(4, 7))
        # Alternate fan bias so neighboring sources cross and fill gaps.
        fan_bias = -1.0 if source_index % 2 else 1.0
        for beam_index in range(count):
            depth = float(rng.beta(1.35, 1.35))
            local = (beam_index - (count - 1) / 2.0) / max(count - 1, 1)
            horizontal = (
                local * rng.uniform(280.0, 610.0)
                + fan_bias * rng.uniform(30.0, 170.0)
                + rng.normal(0.0, 85.0)
            )
            # Keep the nominal wide end close to the lower edge.  If it were
            # hundreds of pixels beyond the crop, only the narrow middle of the
            # cone would be visible and it would read as a CG line again.
            end_y = height + rng.uniform(-12.0, 58.0)
            end_x = sx + horizontal * (0.75 + 0.48 * depth)
            # Some rays are long diagonals.  Drawing beyond the canvas produces
            # naturally clipped cones without endpoints inside the artwork.
            if rng.random() < 0.24:
                end_x += rng.choice((-1.0, 1.0)) * rng.uniform(350.0, 900.0)
                end_y += rng.uniform(20.0, 90.0)

            geometries.append(
                (
                    (sx + rng.normal(0.0, 3.0), sy + rng.normal(0.0, 2.2)),
                    (float(end_x), float(end_y)),
                    depth,
                )
            )

    # Assign width classes across the complete set, rather than sampling each
    # beam independently, so every image has the requested 60/30/10 split.
    beam_count = len(geometries)
    width_classes = np.full(beam_count, 2, dtype=np.int8)
    shuffled = rng.permutation(beam_count)
    thin_count = int(round(beam_count * 0.60))
    medium_count = int(round(beam_count * 0.30))
    width_classes[shuffled[:thin_count]] = 0
    width_classes[shuffled[thin_count : thin_count + medium_count]] = 1

    # Brightness deliberately ranges from almost lost in haze to clipped white.
    brightness_roll = rng.random(beam_count)
    for index, (start, end, depth) in enumerate(geometries):
        width_class = int(width_classes[index])
        if width_class == 0:
            root_width = float(rng.uniform(1.0, 2.0))
            tip_width = float(rng.uniform(6.0, 13.0))
        elif width_class == 1:
            root_width = float(rng.uniform(3.0, 5.0))
            tip_width = float(rng.uniform(16.0, 29.0))
        else:
            root_width = float(rng.uniform(6.0, 10.0))
            tip_width = float(rng.uniform(32.0, 52.0))

        roll = float(brightness_roll[index])
        if roll < 0.34:
            strength = float(rng.uniform(0.10, 0.28))
        elif roll < 0.82:
            strength = float(rng.uniform(0.38, 0.78))
        else:
            strength = float(rng.uniform(1.00, 1.42))
        beams.append(
            Beam(
                start=start,
                end=end,
                root_width=root_width,
                tip_width=tip_width,
                depth=depth,
                strength=strength,
            )
        )
    return sorted(beams, key=lambda beam: beam.depth)


def cone_polygon(beam: Beam, width_scale: float) -> list[tuple[float, float]]:
    """Return the four corners of a tapered beam volume."""
    sx, sy = beam.start
    ex, ey = beam.end
    dx, dy = ex - sx, ey - sy
    length = max(float(np.hypot(dx, dy)), 1.0)
    nx, ny = -dy / length, dx / length
    root = beam.root_width * width_scale * 0.5
    tip = beam.tip_width * width_scale * 0.5
    return [
        (sx + nx * root, sy + ny * root),
        (ex + nx * tip, ey + ny * tip),
        (ex - nx * tip, ey - ny * tip),
        (sx - nx * root, sy - ny * root),
    ]


def draw_beam_layer(
    beams: list[Beam],
    width_scale: float,
    alpha_scale: float,
) -> Image.Image:
    """Draw additive beam cones into a grayscale light-volume layer."""
    layer = Image.new("L", OUTPUT_SIZE, 0)
    draw = ImageDraw.Draw(layer, "L")
    # Paint stronger beams last so a crossing dim ray cannot erase their core.
    for beam in sorted(beams, key=lambda item: item.strength):
        value = int(np.clip(255.0 * beam.strength * alpha_scale, 1.0, 255.0))
        draw.polygon(cone_polygon(beam, width_scale), fill=value)
    return layer


def render_beams(
    canvas: np.ndarray,
    beams: list[Beam],
    sources: list[tuple[float, float]],
    rng: np.random.Generator,
) -> None:
    """Render cone bodies, soft edges, and two additive scattering passes."""
    # A nested cone fill forms a transverse gradient: dim feathered boundary,
    # saturated crimson body, and a pale narrow core only at the very center.
    outer = draw_beam_layer(beams, width_scale=1.00, alpha_scale=0.58)
    middle = draw_beam_layer(beams, width_scale=0.52, alpha_scale=0.68)
    inner = draw_beam_layer(beams, width_scale=0.16, alpha_scale=0.95)

    edge_soft = outer.filter(ImageFilter.GaussianBlur(radius=3.2))
    inner_soft = inner.filter(ImageFilter.GaussianBlur(radius=0.65))
    add_colored_mask(canvas, edge_soft, MID_CRIMSON, 0.28)
    add_colored_mask(canvas, outer, BRIGHT_CRIMSON, 0.42)
    add_colored_mask(canvas, middle, BRIGHT_CRIMSON, 0.34)
    add_colored_mask(canvas, inner_soft, HOT_CORE, 0.82)

    # Required two-stage additive scattering: wide/weak and narrow/strong.  Both
    # originate from the actual cone layer, so the haze follows the beam volume.
    wide_radius = float(rng.uniform(20.0, 25.0))
    narrow_radius = float(rng.uniform(8.0, 12.0))
    wide_scatter = outer.filter(ImageFilter.GaussianBlur(radius=wide_radius))
    narrow_scatter = outer.filter(ImageFilter.GaussianBlur(radius=narrow_radius))
    add_colored_mask(canvas, wide_scatter, MID_CRIMSON, 0.16)
    add_colored_mask(canvas, narrow_scatter, BRIGHT_CRIMSON, 0.25)

    # Diffuse source pools connect each fan to the smoky atmosphere.  They are
    # glows, not fixtures, and are present from the left edge to the right edge.
    source_layer = Image.new("L", OUTPUT_SIZE, 0)
    source_draw = ImageDraw.Draw(source_layer, "L")
    for sx, sy in sources:
        radius = rng.uniform(3.5, 6.5)
        source_draw.ellipse(
            (sx - radius, sy - radius, sx + radius, sy + radius),
            fill=int(rng.uniform(165, 235)),
        )
    source_halo = source_layer.filter(ImageFilter.GaussianBlur(radius=10.5))
    source_soft = source_layer.filter(ImageFilter.GaussianBlur(radius=2.5))
    add_colored_mask(canvas, source_halo, BRIGHT_CRIMSON, 0.28)
    add_colored_mask(canvas, source_soft, HOT_CORE, 0.24)


def add_smoke_ribbons(
    canvas: np.ndarray, smoke: np.ndarray, rng: np.random.Generator
) -> None:
    """Add uneven illuminated wisps over the beam field for atmospheric depth."""
    width, height = OUTPUT_SIZE
    ribbon_mask = Image.new("L", OUTPUT_SIZE, 0)
    draw = ImageDraw.Draw(ribbon_mask, "L")
    for _ in range(int(rng.integers(9, 15))):
        y = rng.uniform(70.0, height - 35.0)
        amplitude = rng.uniform(10.0, 44.0)
        wavelength = rng.uniform(330.0, 900.0)
        phase = rng.uniform(0.0, np.pi * 2.0)
        points = []
        for x in range(-80, width + 81, 40):
            py = y + amplitude * np.sin(x / wavelength * 2 * np.pi + phase)
            points.append((x, py))
        draw.line(points, fill=int(rng.uniform(16, 42)), width=int(rng.integers(10, 28)))
    ribbon_mask = ribbon_mask.filter(ImageFilter.GaussianBlur(radius=rng.uniform(16, 28)))
    # Modulate ribbons by the low-frequency smoke so they appear and disappear.
    ribbon = np.asarray(ribbon_mask, dtype=np.float32) / 255.0
    ribbon *= 0.35 + 0.65 * smoke
    modulated = Image.fromarray(np.uint8(np.rint(np.clip(ribbon, 0, 1) * 255)))
    add_colored_mask(canvas, modulated, BRIGHT_CRIMSON, 0.035)


def add_particles(canvas: np.ndarray, rng: np.random.Generator) -> None:
    """Scatter restrained crimson dust motes through the lit smoke."""
    width, height = OUTPUT_SIZE
    dust = Image.new("L", OUTPUT_SIZE, 0)
    draw = ImageDraw.Draw(dust, "L")
    for _ in range(int(rng.integers(420, 650))):
        x = int(rng.integers(4, width - 4))
        y = int(np.clip(rng.beta(1.45, 1.8) * height, 4, height - 5))
        value = int(np.clip(rng.lognormal(3.0, 0.48), 8, 105))
        radius = 1 if rng.random() < 0.16 else 0
        if radius:
            draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=value)
        else:
            draw.point((x, y), fill=value)
    dust = dust.filter(ImageFilter.GaussianBlur(radius=0.55))
    add_colored_mask(canvas, dust, HOT_CORE, 0.45)


def mean_luminance(rgb: np.ndarray) -> float:
    """Return Rec. 709 mean luminance on the conventional 0--255 scale."""
    values = np.asarray(rgb, dtype=np.float64)
    luminance = (
        values[..., 0] * float(LUMA_WEIGHTS[0])
        + values[..., 1] * float(LUMA_WEIGHTS[1])
        + values[..., 2] * float(LUMA_WEIGHTS[2])
    )
    return float(np.mean(luminance))


def match_mean_luminance(canvas: np.ndarray, target: float) -> np.ndarray:
    """Expose only emitted light while preserving the near-black room floor."""
    # Separating the light from the floor is crucial: multiplying the complete
    # image to reach a target mean would turn the whole frame crimson again.
    source = np.maximum(canvas - NEAR_BLACK[None, None, :], 0.0)

    def expose(value: float) -> np.ndarray:
        emitted = 247.0 * (1.0 - np.exp(-source * value / 247.0))
        return NEAR_BLACK[None, None, :] + emitted

    low, high = 0.05, 16.0
    for _ in range(36):
        middle = (low + high) * 0.5
        if mean_luminance(expose(middle)) < target:
            low = middle
        else:
            high = middle
    return expose((low + high) * 0.5)


def finish_image(canvas: np.ndarray, target_luminance: float) -> Image.Image:
    """Shape the frame and automatically hit the requested luminance range."""
    height, width = canvas.shape[:2]
    yy = np.mgrid[0:height, 0:width][0].astype(np.float32)
    y = yy / (height - 1)

    # Gentle top/bottom shaping only.  No side vignette: horizontal crops must
    # retain usable light at both extremes.
    vertical = 0.93 + 0.07 * np.exp(-((y - 0.43) / 0.50) ** 2)
    canvas *= vertical[..., None]
    canvas = match_mean_luminance(canvas, target_luminance)
    canvas = np.clip(canvas, 0.0, 255.0)
    return Image.fromarray(np.uint8(np.rint(canvas)))


def vertical_slice_maxima(rgb: np.ndarray, slice_count: int = 20) -> list[float]:
    """Return the maximum luminance found in each equal vertical slice."""
    values = np.asarray(rgb, dtype=np.float32)
    luminance = (
        values[..., 0] * LUMA_WEIGHTS[0]
        + values[..., 1] * LUMA_WEIGHTS[1]
        + values[..., 2] * LUMA_WEIGHTS[2]
    )
    sections = np.array_split(luminance, slice_count, axis=1)
    return [float(section.max()) for section in sections]


def generate_variant(seed: int, target_luminance: float) -> Image.Image:
    rng = np.random.default_rng(seed)
    width, height = OUTPUT_SIZE
    canvas, smoke = make_smoke(width, height, rng)
    sources = distribute_sources(width, height, rng)
    beams = make_beams(sources, rng)
    render_beams(canvas, beams, sources, rng)
    add_smoke_ribbons(canvas, smoke, rng)
    add_particles(canvas, rng)
    return finish_image(canvas, target_luminance)


def main() -> None:
    for index, (seed, target) in enumerate(
        zip(SEEDS, TARGET_MEAN_LUMINANCE), start=1
    ):
        output = HERE / f"laser_gen_{index}.jpg"
        generated = generate_variant(seed, target)
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
            slice_maxima = vertical_slice_maxima(saved_rgb)
        coverage_ok = all(value >= 120.0 for value in slice_maxima)
        print(
            f"{output.name}: seed={seed}, size={generated.size}, "
            f"mean_luminance={measured:.2f}, "
            f"20_slice_max_min={min(slice_maxima):.2f}, "
            f"all_slices_ge_120={coverage_ok}"
        )


if __name__ == "__main__":
    main()
