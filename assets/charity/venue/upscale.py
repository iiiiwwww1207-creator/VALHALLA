#!/usr/bin/env python3
"""Non-generative JPEG upscaling with restrained detail restoration."""

from pathlib import Path

from PIL import Image, ImageChops, ImageEnhance, ImageFilter


ROOT = Path(__file__).resolve().parent
IN_DIR = ROOT / "in"
OUT_DIR = ROOT / "out"

JOBS = {
    "yasuda_hall_interior.jpg": ((3130, 2090), "yasuda_hall_interior_hq.jpg"),
    "yasuda_exterior.jpg": ((3150, 4200), "yasuda_exterior_hq.jpg"),
}


def flat_area_denoise(image: Image.Image) -> Image.Image:
    """Blend a very light blur only where local detail and edges are weak."""
    softened = image.filter(ImageFilter.GaussianBlur(radius=0.55))

    # Two complementary signals keep both fine texture and strong contours out
    # of the denoise mask. The mask never exceeds 42/255 (~16.5% blending).
    local_detail = ImageChops.difference(image, softened).convert("L")
    edge_signal = image.convert("L").filter(ImageFilter.GaussianBlur(0.6))
    edge_signal = edge_signal.filter(ImageFilter.FIND_EDGES)
    detail_signal = ImageChops.lighter(local_detail, edge_signal)

    mask_lut = []
    for value in range(256):
        if value <= 4:
            weight = 42
        elif value >= 16:
            weight = 0
        else:
            weight = round(42 * (16 - value) / 12)
        mask_lut.append(weight)
    flat_mask = detail_signal.point(mask_lut)
    return Image.composite(softened, image, flat_mask)


def process(source: Path, target: Path, target_size: tuple[int, int]) -> None:
    with Image.open(source) as opened:
        icc_profile = opened.info.get("icc_profile")
        dpi = opened.info.get("dpi")
        image = opened.convert("RGB")

    image = image.resize(target_size, Image.Resampling.LANCZOS)
    image = image.filter(
        ImageFilter.UnsharpMask(radius=1.15, percent=62, threshold=4)
    )
    image = flat_area_denoise(image)
    image = ImageEnhance.Contrast(image).enhance(1.05)

    save_args = {
        "format": "JPEG",
        "quality": 95,
        "subsampling": 0,
        "optimize": True,
    }
    if icc_profile:
        save_args["icc_profile"] = icc_profile
    if dpi:
        save_args["dpi"] = dpi
    image.save(target, **save_args)


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for input_name, (target_size, output_name) in JOBS.items():
        source = IN_DIR / input_name
        if not source.is_file():
            raise FileNotFoundError(f"Missing input: {source}")
        process(source, OUT_DIR / output_name, target_size)


if __name__ == "__main__":
    main()
