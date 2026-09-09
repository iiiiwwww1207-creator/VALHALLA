from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw


WIDTH, HEIGHT = 1774, 900
SEED = 240917
OUT = Path(__file__).with_name("ai_tech.jpg")

BG = (10, 7, 9)
RED = (193, 18, 31)
DARK_RED = (142, 16, 25)
IVORY = (245, 239, 228)
CX, CY, HALF = 1200, 450, 200


def rgba() -> Image.Image:
    return Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))


def composite(base: Image.Image, overlay: Image.Image) -> Image.Image:
    return Image.alpha_composite(base, overlay)


def main() -> None:
    rng = np.random.default_rng(SEED)
    image = Image.new("RGBA", (WIDTH, HEIGHT), (*BG, 255))

    traces = rgba()
    tr = ImageDraw.Draw(traces)
    paths: list[list[tuple[int, int]]] = []
    sides = ["left"] * 14 + ["right"] * 12 + ["top"] * 10 + ["bottom"] * 10
    for i, side in enumerate(sides):
        if side == "left":
            y = CY - 165 + (i % 14) * 25
            end_y = int(np.clip(y + rng.integers(-240, 241), 18, HEIGHT - 18))
            pts = [(CX - HALF, y), (900 - (i % 4) * 55, y), (900 - (i % 4) * 55, end_y), (0, end_y)]
        elif side == "right":
            j = i - 14; y = CY - 154 + j * 28
            end_y = int(np.clip(y + rng.integers(-210, 211), 18, HEIGHT - 18))
            pts = [(CX + HALF, y), (1490 + (j % 3) * 55, y), (1490 + (j % 3) * 55, end_y), (WIDTH - 1, end_y)]
        elif side == "top":
            j = i - 26; x = CX - 165 + j * 37
            end_x = int(np.clip(x + rng.integers(-500, 501), 510, WIDTH - 15))
            pts = [(x, CY - HALF), (x, 145 - (j % 3) * 42), (end_x, 145 - (j % 3) * 42), (end_x, 0)]
        else:
            j = i - 36; x = CX - 165 + j * 37
            end_x = int(np.clip(x + rng.integers(-500, 501), 510, WIDTH - 15))
            pts = [(x, CY + HALF), (x, 755 + (j % 3) * 42), (end_x, 755 + (j % 3) * 42), (end_x, HEIGHT - 1)]
        paths.append(pts)
        color = DARK_RED if i % 3 else RED
        tr.line(pts, fill=(*color, 255), width=2 if i % 2 else 3, joint="curve")
        for p in pts[1:-1]:
            r = 5
            tr.ellipse((p[0]-r, p[1]-r, p[0]+r, p[1]+r), outline=(*RED, 255), width=2)
        # One short orthogonal branch per route.
        bx, by = pts[1]
        branch = [(bx, by), (bx + (-55 if i % 2 else 55), by), (bx + (-55 if i % 2 else 55), by + (-45 if i % 3 else 45))]
        tr.line(branch, fill=(*DARK_RED, 255), width=1 if i % 2 else 2)
    image = composite(image, traces)

    # Keep the existing chip geometry; only its former background halo was removed.
    chip = rgba(); cd = ImageDraw.Draw(chip)
    box = (CX-HALF, CY-HALF, CX+HALF, CY+HALF)
    cd.rectangle(box, fill=(10, 7, 9, 218), outline=(*RED, 255), width=7)
    cd.rectangle((CX-174, CY-174, CX+174, CY+174), outline=(*DARK_RED, 245), width=3)
    # Pins on all four sides.
    for o in range(-172, 173, 22):
        cd.line((CX+o, CY-HALF, CX+o, CY-HALF-28), fill=(*RED, 240), width=7)
        cd.line((CX+o, CY+HALF, CX+o, CY+HALF+28), fill=(*RED, 240), width=7)
        cd.line((CX-HALF, CY+o, CX-HALF-28, CY+o), fill=(*RED, 240), width=7)
        cd.line((CX+HALF, CY+o, CX+HALF+28, CY+o), fill=(*RED, 240), width=7)
    # Dense etched routing grid and tiny junctions.
    for o in range(-150, 151, 20):
        cd.line((CX-155, CY+o, CX+155, CY+o), fill=(*DARK_RED, 205), width=2)
        cd.line((CX+o, CY-155, CX+o, CY+155), fill=(*DARK_RED, 205), width=2)
    for _ in range(100):
        x = int(rng.integers(CX-150, CX+151)); y = int(rng.integers(CY-150, CY+151))
        cd.line((x, y, x + int(rng.choice([-18, 18])), y), fill=(*RED, 185), width=2)
    image = composite(image, chip)

    final = image.convert("RGB")
    final.save(OUT, "JPEG", quality=92, subsampling=0, optimize=True)

    check = np.asarray(Image.open(OUT).convert("RGB"), dtype=np.float32)
    luminance = 0.2126*check[..., 0] + 0.7152*check[..., 1] + 0.0722*check[..., 2]
    thirds = np.array_split(luminance, 3, axis=1)
    bright_pct = float((luminance >= 100).mean() * 100)
    dark_pct = float((luminance <= 20).mean() * 100)
    third_means = [float(part.mean()) for part in thirds]
    third_diff = max(third_means) - min(third_means)
    passed = bright_pct < 8 and dark_pct >= 60 and third_diff <= 15

    print(f"Luminance >= 100: {bright_pct:.3f}% (required: < 8%)")
    print(f"Luminance <= 20: {dark_pct:.3f}% (required: >= 60%)")
    print("Third means (left / center / right): " + " / ".join(f"{value:.3f}" for value in third_means))
    print(f"Maximum third mean difference: {third_diff:.3f} (required: <= 15)")
    print(f"PASS: {passed}")


if __name__ == "__main__":
    main()
