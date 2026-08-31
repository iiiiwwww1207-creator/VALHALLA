#!/usr/bin/env python3
"""Deterministically upscale and gently restore celavi_red.jpg."""

from pathlib import Path

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter


INPUT_PATH = Path("in/celavi_red.jpg")
OUTPUT_PATH = Path("out/celavi_red_hq.jpg")
OUTPUT_SIZE = (2560, 1708)


def reduce_flat_dark_noise(image: Image.Image) -> Image.Image:
    """Blend a light blur only into locally flat areas, favoring shadows."""
    source = np.asarray(image, dtype=np.float32)
    luminance = np.asarray(image.convert("L"), dtype=np.float32)

    # A local min/max range is robust around strong red lighting: detailed and
    # edged areas have a wide range, while noisy flat areas remain relatively low.
    lum_image = Image.fromarray(luminance.astype(np.uint8))
    local_max = np.asarray(lum_image.filter(ImageFilter.MaxFilter(5)), dtype=np.float32)
    local_min = np.asarray(lum_image.filter(ImageFilter.MinFilter(5)), dtype=np.float32)
    local_range = local_max - local_min

    # Smooth transitions prevent visible denoising boundaries. At most 38% of a
    # 0.65 px Gaussian blur is used, so texture and architectural detail survive.
    flatness = np.clip((16.0 - local_range) / 12.0, 0.0, 1.0)
    shadow_weight = 0.45 + 0.55 * np.clip((150.0 - luminance) / 120.0, 0.0, 1.0)
    blend = (0.38 * flatness * shadow_weight)[..., None]

    blurred = np.asarray(image.filter(ImageFilter.GaussianBlur(radius=0.65)), dtype=np.float32)
    restored = source * (1.0 - blend) + blurred * blend
    return Image.fromarray(np.clip(restored + 0.5, 0, 255).astype(np.uint8))


def main() -> None:
    with Image.open(INPUT_PATH) as input_image:
        image = input_image.convert("RGB")

    image = image.resize(OUTPUT_SIZE, Image.Resampling.LANCZOS)
    image = image.filter(ImageFilter.UnsharpMask(radius=1.2, percent=55, threshold=4))
    image = reduce_flat_dark_noise(image)
    image = ImageEnhance.Contrast(image).enhance(1.04)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    image.save(OUTPUT_PATH, "JPEG", quality=95, subsampling=0, optimize=True)


if __name__ == "__main__":
    main()
