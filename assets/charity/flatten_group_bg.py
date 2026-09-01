#!/usr/bin/python3
"""Flatten the studio background in in/group.jpg using Pillow and NumPy only."""

from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter


INPUT = Path("in/group.jpg")
OUTPUT = Path("out/group_flat.jpg")
TARGET = np.array([238.0, 246.0, 253.0], dtype=np.float32)


def design_matrix(x, y):
    """Cubic 2-D polynomial basis for the low-frequency illumination field."""
    return np.column_stack(
        (np.ones_like(x), x, y, x*x, x*y, y*y,
         x*x*x, x*x*y, x*y*y, y*y*y)
    )


def estimate_background(rgb):
    h, w, _ = rgb.shape
    yy, xx = np.mgrid[0:h, 0:w]
    xn = (xx - (w - 1) / 2) / ((w - 1) / 2)
    yn = (yy - (h - 1) / 2) / ((h - 1) / 2)

    # Only bright, low-saturation blue-white pixels can teach the model.  Broad
    # person boxes are removed so that white clothing never biases the fit.
    lum = 0.2126*rgb[..., 0] + 0.7152*rgb[..., 1] + 0.0722*rgb[..., 2]
    chroma = rgb.max(axis=2) - rgb.min(axis=2)
    safe = (lum > 211) & (chroma < 38)
    safe[270:, 115:515] = False
    safe[245:, 555:1010] = False
    safe[285:, 1010:1485] = False

    # Subsample regularly; iteratively reject residual outliers (hair wisps,
    # shadows, JPEG defects).  The resulting field contains no person pixels.
    sample = safe & ((xx % 5) == 0) & ((yy % 5) == 0)
    sx, sy = xn[sample], yn[sample]
    values = rgb[sample]
    A = design_matrix(sx, sy)
    keep = np.ones(len(values), dtype=bool)
    coef = None
    for _ in range(4):
        with np.errstate(all="ignore"):
            coef = np.linalg.lstsq(A[keep], values[keep], rcond=None)[0]
            residual = np.linalg.norm(values - A @ coef, axis=1)
        med = np.median(residual[keep])
        mad = np.median(np.abs(residual[keep] - med)) + 1e-6
        keep = residual < med + 3.5 * 1.4826 * mad

    full_A = design_matrix(xn.ravel(), yn.ravel())
    with np.errstate(all="ignore"):
        field = full_A @ coef
    return field.reshape(h, w, 3).astype(np.float32)


def smoothstep(edge0, edge1, x):
    t = np.clip((x - edge0) / (edge1 - edge0), 0.0, 1.0)
    return t*t*(3.0 - 2.0*t)


def make_background_weight(rgb, field):
    h, w, _ = rgb.shape
    yy, xx = np.mgrid[0:h, 0:w]

    # Away from the three people everything is known background.  Within the
    # generous person zones, color distance from the fitted background protects
    # hair, skin, black clothes and the warmer/shadowed detail of the white suit.
    person_zone = (
        ((xx > 110) & (xx < 520) & (yy > 270)) |
        ((xx > 550) & (xx < 1015) & (yy > 235)) |
        ((xx > 1000) & (xx < 1490) & (yy > 275))
    )
    delta = rgb - field
    distance = np.sqrt(np.sum(delta*delta, axis=2))
    # Full background below 5 RGB-distance units; full foreground above 18.
    foreground = smoothstep(5.0, 18.0, distance) * person_zone

    # The right-hand white suit has highlights almost as bright as the studio.
    # Protect warm-neutral whites inside its actual silhouette; the background
    # is cooler, while darker folds were already protected by color distance.
    silhouette_image = Image.new("L", (w, h), 0)
    ImageDraw.Draw(silhouette_image).polygon(
        [(1170, 535), (1210, 515), (1290, 510), (1345, 540),
         (1370, 650), (1400, 810), (1415, 850), (1390, 875),
         (1360, 855), (1425, 1065), (1170, 1065), (1190, 920),
         (1150, 890), (1120, 810), (1110, 650), (1130, 570)],
        fill=255,
    )
    silhouette = np.asarray(silhouette_image, dtype=np.float32) / 255.0
    blue_minus_red = rgb[..., 2] - rgb[..., 0]
    warm_white = (1.0 - smoothstep(6.0, 11.0, blue_minus_red))
    warm_white *= smoothstep(180.0, 225.0, rgb.mean(axis=2))
    foreground = np.maximum(foreground, silhouette * warm_white)
    weight = 1.0 - foreground

    # Feather only the matte (not the image) to avoid a cut-out edge.
    matte = Image.fromarray(np.uint8(np.clip(weight, 0, 1) * 255))
    matte = matte.filter(ImageFilter.GaussianBlur(radius=1.2))
    return np.asarray(matte, dtype=np.float32) / 255.0


def main():
    image = Image.open(INPUT).convert("RGB")
    rgb = np.asarray(image, dtype=np.float32)
    field = estimate_background(rgb)
    bg_weight = make_background_weight(rgb, field)[..., None]

    # Flat-field subtraction. Retaining 12% of high-frequency residual keeps
    # natural JPEG/grain texture without retaining visible studio falloff.
    flattened_background = TARGET + 0.12 * (rgb - field)
    result = rgb * (1.0 - bg_weight) + flattened_background * bg_weight
    result = np.uint8(np.clip(np.rint(result), 0, 255))

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(result).save(
        OUTPUT, "JPEG", quality=95, subsampling=0, optimize=True
    )


if __name__ == "__main__":
    main()
