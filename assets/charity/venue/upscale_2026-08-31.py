#!/usr/bin/env /usr/bin/python3
"""Conservative, non-generative upscaling for the three supplied JPEGs."""

from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter


JOBS = (
    ("todai_avenue.jpg", "todai_avenue_hq.jpg", (2700, 1527)),
    ("yasuda_hall.jpg", "yasuda_hall_hq.jpg", (2560, 1708)),
    ("celavi_blue.jpg", "celavi_blue_hq.jpg", (2128, 1416)),
)

INPUT_DIR = Path("in")
OUTPUT_DIR = Path("out")


def selective_denoise(image: Image.Image) -> Image.Image:
    """Blend a tiny blur into flat areas, with slightly more weight in shadows."""
    source = np.asarray(image, dtype=np.float32)
    local_mean = np.asarray(image.filter(ImageFilter.GaussianBlur(1.15)), dtype=np.float32)
    gentle_blur = np.asarray(image.filter(ImageFilter.GaussianBlur(0.55)), dtype=np.float32)

    luma = source[..., 0] * 0.2126 + source[..., 1] * 0.7152 + source[..., 2] * 0.0722
    detail = np.mean(np.abs(source - local_mean), axis=2)

    # The mask quickly falls to zero at edges/textures. Shadows receive at most
    # a small additional blend, which suppresses noise without waxy detail loss.
    flatness = np.clip((8.0 - detail) / 8.0, 0.0, 1.0)
    darkness = np.clip((105.0 - luma) / 105.0, 0.0, 1.0)
    amount = flatness * (0.08 + 0.10 * darkness)
    result = source * (1.0 - amount[..., None]) + gentle_blur * amount[..., None]
    return Image.fromarray(np.clip(np.rint(result), 0, 255).astype(np.uint8))


def luma_contrast(image: Image.Image, factor: float = 1.04) -> Image.Image:
    """Raise luminance contrast without directly scaling color saturation."""
    rgb = np.asarray(image, dtype=np.float32)
    luma = rgb[..., 0] * 0.2126 + rgb[..., 1] * 0.7152 + rgb[..., 2] * 0.0722
    adjusted_luma = (luma - 127.5) * factor + 127.5
    result = rgb + (adjusted_luma - luma)[..., None]
    return Image.fromarray(np.clip(np.rint(result), 0, 255).astype(np.uint8))


def process(source_path: Path, output_path: Path, target_size: tuple[int, int]) -> None:
    with Image.open(source_path) as opened:
        image = opened.convert("RGB")
        image = image.resize(target_size, Image.Resampling.LANCZOS)

    # Low amount and a small radius recover interpolation softness while keeping
    # bright/dark edge overshoot (visible halos) restrained.
    image = image.filter(ImageFilter.UnsharpMask(radius=1.25, percent=55, threshold=3))
    image = selective_denoise(image)
    image = luma_contrast(image, factor=1.04)
    image.save(output_path, "JPEG", quality=95, subsampling=0, optimize=True)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for source_name, output_name, target_size in JOBS:
        source_path = INPUT_DIR / source_name
        output_path = OUTPUT_DIR / output_name
        process(source_path, output_path, target_size)
        print(f"{source_path} -> {output_path} {target_size[0]}x{target_size[1]}")


if __name__ == "__main__":
    main()
