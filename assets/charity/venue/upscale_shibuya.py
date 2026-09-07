#!/usr/bin/env python3
"""Conservatively clean and upscale the compressed Shibuya night photograph."""

from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageFilter


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "shibuya_src.jpg"
OUTPUT = HERE / "shibuya_night.jpg"
TARGET_SIZE = (2485, 3731)


def edge_aware_denoise(image: Image.Image) -> Image.Image:
    """Reduce JPEG/night noise while protecting signs and building edges."""
    rgb = np.asarray(image, dtype=np.uint8)
    filtered = cv2.bilateralFilter(rgb, d=5, sigmaColor=20, sigmaSpace=3)

    source = rgb.astype(np.float32)
    smoothed = filtered.astype(np.float32)
    luma = (
        source[..., 0] * 0.2126
        + source[..., 1] * 0.7152
        + source[..., 2] * 0.0722
    )

    # Use more of the bilateral result in dark, flat areas. High-gradient areas
    # (small sign lettering, window lines, roof edges) retain almost all source detail.
    gx = cv2.Sobel(luma, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(luma, cv2.CV_32F, 0, 1, ksize=3)
    gradient = cv2.magnitude(gx, gy)
    edge_protection = np.clip(1.0 - gradient / 38.0, 0.10, 1.0)
    darkness = np.clip((125.0 - luma) / 125.0, 0.0, 1.0)
    amount = (0.32 + 0.24 * darkness) * edge_protection

    result = source * (1.0 - amount[..., None]) + smoothed * amount[..., None]
    return Image.fromarray(np.clip(np.rint(result), 0, 255).astype(np.uint8))


def lift_shadows(image: Image.Image, gamma: float = 1.06) -> Image.Image:
    """Apply a slight gamma lift to luminance while leaving chroma unchanged."""
    rgb = np.asarray(image, dtype=np.float32)
    luma = rgb[..., 0] * 0.2126 + rgb[..., 1] * 0.7152 + rgb[..., 2] * 0.0722
    lifted = 255.0 * np.power(luma / 255.0, 1.0 / gamma)
    result = rgb + (lifted - luma)[..., None]
    return Image.fromarray(np.clip(np.rint(result), 0, 255).astype(np.uint8))


def laplacian_variance(image: Image.Image) -> float:
    """Return the conventional OpenCV Laplacian variance on grayscale pixels."""
    gray = cv2.cvtColor(np.asarray(image.convert("RGB")), cv2.COLOR_RGB2GRAY)
    return float(cv2.Laplacian(gray, cv2.CV_64F).var())


def process() -> None:
    with Image.open(SOURCE) as opened:
        source = opened.convert("RGB")

    source_sharpness = laplacian_variance(source)
    cleaned = edge_aware_denoise(source)
    enlarged = cleaned.resize(TARGET_SIZE, Image.Resampling.LANCZOS)
    sharpened = enlarged.filter(
        ImageFilter.UnsharpMask(radius=2.0, percent=80, threshold=3)
    )
    result = lift_shadows(sharpened, gamma=1.06)
    result.save(
        OUTPUT,
        "JPEG",
        quality=94,
        subsampling=0,
        optimize=True,
        dpi=(300, 300),
    )

    # Re-open the actual JPEG so the reported metric includes final compression.
    with Image.open(OUTPUT) as saved:
        saved_rgb = saved.convert("RGB")
        output_sharpness = laplacian_variance(saved_rgb)
        normalized = saved_rgb.resize(source.size, Image.Resampling.LANCZOS)
        normalized_sharpness = laplacian_variance(normalized)

    print(f"Source: {source.size[0]}x{source.size[1]}")
    print(f"Output: {TARGET_SIZE[0]}x{TARGET_SIZE[1]}")
    print(f"Laplacian variance (source, native): {source_sharpness:.2f}")
    print(f"Laplacian variance (output, native): {output_sharpness:.2f}")
    print(
        "Laplacian variance (output resized to source dimensions): "
        f"{normalized_sharpness:.2f}"
    )
    print(f"Saved: {OUTPUT} ({OUTPUT.stat().st_size / (1024 * 1024):.2f} MiB)")


if __name__ == "__main__":
    process()
