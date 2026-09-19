#!/usr/bin/env python3
"""Extract the old red CAMPFIRE logo from the renewal slide."""

from collections import deque
from pathlib import Path

import numpy as np
from PIL import Image


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "_renewal_slide_src.png"
OUTPUT = HERE / "campfire-logo-old-red.png"
PREVIEW = HERE / "campfire-logo-old-red_preview.jpg"
X_LIMIT = 700
PADDING = 12
OUTPUT_HEIGHT = 300
PREVIEW_BG = (10, 8, 6)


def components(mask: np.ndarray) -> list[np.ndarray]:
    """Return 8-connected components as arrays of (y, x) coordinates."""
    h, w = mask.shape
    seen = np.zeros_like(mask, dtype=bool)
    result = []
    for y, x in np.argwhere(mask):
        if seen[y, x]:
            continue
        queue = deque([(int(y), int(x))])
        seen[y, x] = True
        points = []
        while queue:
            cy, cx = queue.popleft()
            points.append((cy, cx))
            for ny in range(max(0, cy - 1), min(h, cy + 2)):
                for nx in range(max(0, cx - 1), min(w, cx + 2)):
                    if mask[ny, nx] and not seen[ny, nx]:
                        seen[ny, nx] = True
                        queue.append((ny, nx))
        result.append(np.asarray(points, dtype=np.int32))
    return result


def enclosed_background(component: np.ndarray, shape: tuple[int, int]) -> np.ndarray:
    """Find holes enclosed by one component (used for the white c in the flame)."""
    ys, xs = component[:, 0], component[:, 1]
    y0, y1 = max(0, int(ys.min()) - 1), min(shape[0], int(ys.max()) + 2)
    x0, x1 = max(0, int(xs.min()) - 1), min(shape[1], int(xs.max()) + 2)
    wall = np.zeros((y1 - y0, x1 - x0), dtype=bool)
    wall[ys - y0, xs - x0] = True
    outside = np.zeros_like(wall)
    queue = deque()
    for y in range(wall.shape[0]):
        for x in (0, wall.shape[1] - 1):
            if not wall[y, x] and not outside[y, x]:
                outside[y, x] = True
                queue.append((y, x))
    for x in range(wall.shape[1]):
        for y in (0, wall.shape[0] - 1):
            if not wall[y, x] and not outside[y, x]:
                outside[y, x] = True
                queue.append((y, x))
    while queue:
        cy, cx = queue.popleft()
        for ny, nx in ((cy - 1, cx), (cy + 1, cx), (cy, cx - 1), (cy, cx + 1)):
            if 0 <= ny < wall.shape[0] and 0 <= nx < wall.shape[1]:
                if not wall[ny, nx] and not outside[ny, nx]:
                    outside[ny, nx] = True
                    queue.append((ny, nx))
    holes = (~wall) & (~outside)
    full = np.zeros(shape, dtype=bool)
    full[y0:y1, x0:x1] = holes
    return full


def main() -> None:
    source = Image.open(SOURCE).convert("RGBA")
    rgba = np.asarray(source).copy()
    rgb = rgba[..., :3].astype(np.float32)
    source_alpha = rgba[..., 3].astype(np.float32) / 255.0
    r, g, b = np.moveaxis(rgb, -1, 0)

    # A broad red test includes anti-aliased edge pixels. Everything at x >= 700
    # is deliberately excluded before the bounding box is calculated.
    red_strength = r - np.maximum(g, b)
    red = (r > 80) & (red_strength > 12) & (source_alpha > 0)
    red[:, X_LIMIT:] = False
    strong_red = red & (r > 170) & (red_strength > 55)
    yy, xx = np.nonzero(strong_red)
    if not len(xx):
        raise RuntimeError("No red pixels found in the old-logo search area")

    x0 = max(0, int(xx.min()) - PADDING)
    y0 = max(0, int(yy.min()) - PADDING)
    x1 = min(X_LIMIT, int(xx.max()) + PADDING + 1)
    y1 = min(rgba.shape[0], int(yy.max()) + PADDING + 1)

    # The flame is the leftmost substantial red component. Its enclosed light
    # pixels are the white c and must remain opaque.
    substantial = [c for c in components(strong_red) if len(c) >= 20]
    flame = min(substantial, key=lambda c: c[:, 1].min())
    flame_holes = enclosed_background(flame, strong_red.shape)
    # Include the c's gray anti-alias pixels as well as its solid white center.
    light = (rgb.min(axis=2) >= 80) & ((rgb.max(axis=2) - rgb.min(axis=2)) <= 35)
    keep_white_c = flame_holes & light & (source_alpha > 0)

    if np.any(source_alpha == 0):
        # The supplied export is already transparent: retain its clean straight
        # alpha and colors instead of mistakenly treating transparent black as
        # a white-background blend.
        alpha = np.where(red, source_alpha, 0.0)
        out_rgb = rgb.copy()
    else:
        # Recover a soft foreground alpha from white-backed pixels, then reverse
        # the white blend (despill) to prevent pale fringes on dark backgrounds.
        matte_from_white = np.clip((255.0 - np.minimum(g, b)) / 184.0, 0.0, 1.0)
        alpha = np.where(red, matte_from_white, 0.0)
        safe_alpha = np.maximum(alpha, 1.0 / 255.0)[..., None]
        out_rgb = np.clip((rgb - 255.0 * (1.0 - safe_alpha)) / safe_alpha, 0, 255)
    alpha = np.where(keep_white_c, source_alpha, alpha)
    out_rgb[keep_white_c] = rgb[keep_white_c]
    out = np.dstack((out_rgb, alpha[..., None] * 255.0)).astype(np.uint8)
    cropped = Image.fromarray(out[y0:y1, x0:x1])

    width = round(cropped.width * OUTPUT_HEIGHT / cropped.height)
    resized = cropped.resize((width, OUTPUT_HEIGHT), Image.Resampling.LANCZOS)
    resized.save(OUTPUT)

    preview = Image.new("RGB", resized.size, PREVIEW_BG)
    preview.paste(resized, mask=resized.getchannel("A"))
    preview.save(PREVIEW, quality=95, subsampling=0)
    print(f"crop=({x0}, {y0}, {x1}, {y1}) output={resized.size}")


if __name__ == "__main__":
    main()
