#!/usr/bin/env python3
"""Cut the flat pale-blue background out of group_flat.jpg.

The matte is primarily a soft colour-distance key.  A filled mask made from
large connected foreground components protects pale clothes inside each
person's silhouette, while the original soft key remains at the outer edge.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import cv2
import numpy as np


DEFAULT_BG = np.array([237.0, 246.0, 253.0], dtype=np.float32)


def smoothstep(edge0: float, edge1: float, value: np.ndarray) -> np.ndarray:
    value = np.clip((value - edge0) / (edge1 - edge0), 0.0, 1.0)
    return value * value * (3.0 - 2.0 * value)


def estimate_background(rgb: np.ndarray) -> np.ndarray:
    """Robustly estimate the flat background from clearly empty border areas."""
    h, w = rgb.shape[:2]
    strips = np.concatenate(
        (
            rgb[: max(32, h // 8)].reshape(-1, 3),
            rgb[:, : max(16, w // 50)].reshape(-1, 3),
            rgb[:, -max(16, w // 50) :].reshape(-1, 3),
        ),
        axis=0,
    )
    estimate = np.median(strips, axis=0).astype(np.float32)
    # Guard against an unexpectedly occupied border.  The known flattened
    # source colour is also useful for byte-for-byte reproducibility.
    if np.linalg.norm(estimate - DEFAULT_BG) > 12.0:
        return DEFAULT_BG.copy()
    return estimate


def colour_key_score(rgb: np.ndarray, background: np.ndarray) -> np.ndarray:
    """Perceptual distance using luminance, chroma, saturation and hue."""
    bg_pixel = np.uint8([[np.clip(background, 0, 255)]])
    lab = cv2.cvtColor(rgb, cv2.COLOR_RGB2LAB).astype(np.float32)
    bg_lab = cv2.cvtColor(bg_pixel, cv2.COLOR_RGB2LAB)[0, 0].astype(np.float32)
    hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV).astype(np.float32)
    bg_hsv = cv2.cvtColor(bg_pixel, cv2.COLOR_RGB2HSV)[0, 0].astype(np.float32)

    # A cast shadow is mostly a darker copy of the backdrop, whereas the white
    # suit is brighter and less blue.  Treat those two luminance directions
    # asymmetrically so the shadow is discarded without erasing the suit.
    dl_light = np.maximum(lab[..., 0] - bg_lab[0], 0.0)
    dl_dark = np.maximum(bg_lab[0] - lab[..., 0] - 22.0, 0.0)
    dc = np.linalg.norm(lab[..., 1:3] - bg_lab[1:3], axis=2)
    ds = np.abs(hsv[..., 1] - bg_hsv[1])

    # OpenCV hue is circular in [0, 180).  Hue is unreliable near grey, so
    # weight it by the smaller saturation of the two colours.
    dh = np.abs(hsv[..., 0] - bg_hsv[0])
    dh = np.minimum(dh, 180.0 - dh)
    hue_weight = np.minimum(hsv[..., 1], bg_hsv[1]) / 32.0

    return np.sqrt(
        (0.70 * dl_light) ** 2
        + (0.48 * dl_dark) ** 2
        + (1.12 * dc) ** 2
        + (0.20 * ds) ** 2
        + (0.18 * dh * hue_weight) ** 2
    )


def person_silhouettes(rgb: np.ndarray, score: np.ndarray) -> np.ndarray:
    """Estimate the three large person components, including pale interiors."""
    h, w = score.shape
    sx, sy = w / 1600.0, h / 1066.0
    canonical_rois = (
        (125, 295, 390, 771),
        (565, 265, 440, 801),
        (1050, 315, 430, 751),
    )
    combined = np.zeros((h, w), np.uint8)
    cv2.setRNGSeed(20260918)

    for cx, cy, cw, ch in canonical_rois:
        x, y = int(cx * sx), int(cy * sy)
        rw, rh = min(int(cw * sx), w - x), min(int(ch * sy), h - y)
        mask = np.full((h, w), cv2.GC_BGD, np.uint8)
        mask[y : y + rh, x : x + rw] = cv2.GC_PR_FGD
        # Exact/near-exact key pixels are certain background.  Strong colour
        # differences seed foreground; white clothing remains probable FG and
        # is learned as part of the connected person model.
        mask[score < 0.8] = cv2.GC_BGD
        roi = np.zeros((h, w), bool)
        roi[y : y + rh, x : x + rw] = True
        mask[roi & (score > 11.0)] = cv2.GC_FGD
        bg_model = np.zeros((1, 65), np.float64)
        fg_model = np.zeros((1, 65), np.float64)
        cv2.grabCut(rgb, mask, None, bg_model, fg_model, 5, cv2.GC_INIT_WITH_MASK)
        component = np.uint8((mask == cv2.GC_FGD) | (mask == cv2.GC_PR_FGD)) * 255

        count, labels, stats, _ = cv2.connectedComponentsWithStats(component, 8)
        for label in range(1, count):
            if stats[label, cv2.CC_STAT_AREA] >= score.size * 0.008:
                combined[labels == label] = 255

    # Remove only small enclosed segmentation pinholes.  Large openings (for
    # example between an arm and torso) are genuine background and stay clear.
    inverse = np.uint8(combined == 0) * 255
    count, labels, stats, _ = cv2.connectedComponentsWithStats(inverse, 8)
    max_hole_area = score.size * 0.001
    for label in range(1, count):
        x = stats[label, cv2.CC_STAT_LEFT]
        y = stats[label, cv2.CC_STAT_TOP]
        ww = stats[label, cv2.CC_STAT_WIDTH]
        hh = stats[label, cv2.CC_STAT_HEIGHT]
        touches_edge = x == 0 or y == 0 or x + ww == w or y + hh == h
        if not touches_edge and stats[label, cv2.CC_STAT_AREA] <= max_hole_area:
            combined[labels == label] = 255

    return combined


def despill(rgb: np.ndarray, alpha: np.ndarray, background: np.ndarray) -> np.ndarray:
    """Remove pale-blue background mixed into antialiased edge pixels."""
    source = rgb.astype(np.float32) / 255.0
    bg = background.astype(np.float32) / 255.0
    a = alpha[..., None]

    # Invert the usual source-over equation.  Very small alphas are clamped to
    # keep JPEG noise from turning into strongly coloured specks.
    safe_a = np.maximum(a, 0.08)
    unmixed = (source - bg * (1.0 - a)) / safe_a
    unmixed = np.clip(unmixed, 0.0, 1.0)
    edge_amount = np.clip((1.0 - a) * (a > 0.015), 0.0, 1.0)
    result = source * (1.0 - edge_amount) + unmixed * edge_amount
    result[a[..., 0] <= 0.005] = 0.0
    return np.uint8(np.clip(result * 255.0 + 0.5, 0, 255))


def cut_out(rgb: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    background = estimate_background(rgb)
    score = colour_key_score(rgb, background)

    # A broad transition retains fine hair and antialiasing without a hard rim.
    alpha = smoothstep(2.25, 8.5, score)
    silhouette = person_silhouettes(rgb, score)
    interior = cv2.erode(
        silhouette, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)), iterations=1
    ) > 0
    support = cv2.dilate(
        silhouette, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7)), iterations=1
    ) > 0
    alpha[~support] = 0.0
    alpha[interior] = 1.0
    alpha = cv2.GaussianBlur(alpha, (0, 0), 0.35)
    alpha[interior] = 1.0
    alpha[alpha < 0.006] = 0.0

    clean_rgb = despill(rgb, alpha, background)
    rgba = np.dstack((clean_rgb, np.uint8(np.clip(alpha * 255.0 + 0.5, 0, 255))))
    return rgba, background


def main() -> None:
    here = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=here / "group_flat.jpg")
    parser.add_argument("--output", type=Path, default=here / "group_flat_cut.png")
    parser.add_argument(
        "--preview", type=Path, default=here / "group_flat_cut_preview.jpg"
    )
    args = parser.parse_args()

    bgr = cv2.imread(str(args.input), cv2.IMREAD_COLOR)
    if bgr is None:
        raise SystemExit(f"Could not read input: {args.input}")
    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    rgba, background = cut_out(rgb)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    if not cv2.imwrite(str(args.output), cv2.cvtColor(rgba, cv2.COLOR_RGBA2BGRA)):
        raise SystemExit(f"Could not write output: {args.output}")

    alpha = rgba[..., 3:4].astype(np.float32) / 255.0
    black = np.array([10.0, 8.0, 6.0], dtype=np.float32)
    preview = rgba[..., :3].astype(np.float32) * alpha + black * (1.0 - alpha)
    preview_bgr = cv2.cvtColor(np.uint8(np.clip(preview + 0.5, 0, 255)), cv2.COLOR_RGB2BGR)
    if not cv2.imwrite(str(args.preview), preview_bgr, [cv2.IMWRITE_JPEG_QUALITY, 95]):
        raise SystemExit(f"Could not write preview: {args.preview}")

    print(f"background RGB: {tuple(int(round(x)) for x in background)}")
    print(f"wrote {args.output} ({rgba.shape[1]}x{rgba.shape[0]}, RGBA)")
    print(f"wrote {args.preview}")


if __name__ == "__main__":
    main()
