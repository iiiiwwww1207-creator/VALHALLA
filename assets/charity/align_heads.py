#!/usr/bin/env python3
"""Align the three people's topmost alpha pixels without scaling or x movement."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image
from scipy import ndimage


SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_INPUT = SCRIPT_DIR / "group_flat_cut.png"
DEFAULT_OUTPUT = SCRIPT_DIR / "group_flat_aligned.png"
DEFAULT_PREVIEW = SCRIPT_DIR / "group_flat_aligned_preview.jpg"
PREVIEW_BACKGROUND = (10, 8, 6, 255)


@dataclass(frozen=True)
class PersonComponent:
    label: int
    x_min: int
    top_y: int


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Align three alpha-connected people to the highest head top."
    )
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--preview", type=Path, default=DEFAULT_PREVIEW)
    return parser.parse_args()


def find_people(alpha: np.ndarray) -> tuple[np.ndarray, list[PersonComponent]]:
    # Eight-neighbour connectivity keeps diagonally touching antialiased pixels together.
    component_labels, component_count = ndimage.label(
        alpha > 0, structure=np.ones((3, 3), dtype=np.uint8)
    )
    if component_count < 3:
        raise ValueError(
            f"Expected at least 3 alpha-connected components, found {component_count}."
        )

    # A few isolated antialias pixels can form tiny extra components. The three
    # largest components are the people; assign every smaller component to the
    # horizontally nearest person so no nonzero-alpha source pixel is discarded.
    areas = np.bincount(component_labels.ravel())[1:]
    anchor_labels = np.argsort(areas)[-3:] + 1
    anchor_centers_x: list[float] = []
    for label_id in anchor_labels:
        _, xs = np.nonzero(component_labels == label_id)
        anchor_centers_x.append(float(xs.mean()))

    horizontal_order = np.argsort(anchor_centers_x)
    anchor_centers_x = [anchor_centers_x[index] for index in horizontal_order]
    people_labels = np.zeros_like(component_labels)
    for component_id in range(1, component_count + 1):
        _, xs = np.nonzero(component_labels == component_id)
        nearest_person = int(np.argmin(np.abs(np.asarray(anchor_centers_x) - xs.mean())))
        people_labels[component_labels == component_id] = nearest_person + 1

    people: list[PersonComponent] = []
    for person_id in range(1, 4):
        ys, xs = np.nonzero(people_labels == person_id)
        people.append(
            PersonComponent(
                label=person_id,
                x_min=int(xs.min()),
                top_y=int(ys.min()),
            )
        )

    # The source composition is left, centre, right; horizontal position identifies each.
    people.sort(key=lambda person: person.x_min)
    return people_labels, people


def align_people(source: np.ndarray) -> tuple[np.ndarray, list[tuple[int, int]]]:
    labels, people = find_people(source[:, :, 3])
    target_y = min(person.top_y for person in people)
    result = np.zeros_like(source)
    movements: list[tuple[int, int]] = []
    height = source.shape[0]

    for person in people:
        dy = target_y - person.top_y
        ys, xs = np.nonzero(labels == person.label)
        destination_ys = ys + dy
        in_frame = (destination_ys >= 0) & (destination_ys < height)
        result[destination_ys[in_frame], xs[in_frame]] = source[ys[in_frame], xs[in_frame]]
        movements.append((person.top_y, dy))

    return result, movements


def main() -> None:
    args = parse_args()
    source_image = Image.open(args.input).convert("RGBA")
    source = np.asarray(source_image)
    aligned, movements = align_people(source)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    aligned_image = Image.fromarray(aligned)
    aligned_image.save(args.output)

    preview_background = Image.new("RGBA", aligned_image.size, PREVIEW_BACKGROUND)
    preview = Image.alpha_composite(preview_background, aligned_image).convert("RGB")
    args.preview.parent.mkdir(parents=True, exist_ok=True)
    preview.save(args.preview, quality=95, subsampling=0)

    for position, (top_y, dy) in zip(("left", "center", "right"), movements):
        print(f"{position}: original top Y={top_y}, vertical movement={dy:+d}px")
    print(f"saved RGBA: {args.output}")
    print(f"saved preview: {args.preview}")


if __name__ == "__main__":
    main()
