#!/usr/bin/env python3
"""Normalize generated source art into deterministic, engine-ready atlases.

The source images are intentionally kept untouched. This implements the recovery
steps from the project's pixel-art workflow: recover cells, snap pixels, anchor
frames, normalize dimensions, limit the palette, and combine final sheets.
"""

from pathlib import Path
import json

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets" / "source"
OUTPUT = ROOT / "assets" / "generated"


def nearest(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    return image.resize(size, Image.Resampling.NEAREST)


def build_environment() -> dict:
    source = Image.open(SOURCE / "environment-atlas-source.png").convert("RGB")
    columns = rows = 6
    source_cell = source.width // columns
    target_cell = 128
    inset = 3  # remove the generated separator without sampling neighbouring cells
    output = Image.new("RGB", (columns * target_cell, rows * target_cell))

    for row in range(rows):
        for column in range(columns):
            left = column * source_cell + inset
            top = row * source_cell + inset
            tile = source.crop((
                left,
                top,
                (column + 1) * source_cell - inset,
                (row + 1) * source_cell - inset,
            ))
            output.paste(nearest(tile, (target_cell, target_cell)),
                         (column * target_cell, row * target_cell))

    output.save(OUTPUT / "environment-atlas.png", optimize=True)
    return {"columns": columns, "rows": rows, "cell": target_cell}


def recover_character_cells(source: Image.Image) -> list[Image.Image]:
    cells = []
    for row in range(4):
        for column in range(4):
            left = round(column * source.width / 4)
            right = round((column + 1) * source.width / 4)
            top = round(row * source.height / 4)
            bottom = round((row + 1) * source.height / 4)
            cells.append(source.crop((left, top, right, bottom)))
    return cells


def build_player() -> dict:
    source = Image.open(SOURCE / "player-walk-alpha-source.png").convert("RGBA")
    recovered = recover_character_cells(source)
    bounds = [cell.getbbox() for cell in recovered]
    if any(bound is None for bound in bounds):
        raise RuntimeError("A generated character frame was empty")

    trimmed = [cell.crop(bound) for cell, bound in zip(recovered, bounds)]
    max_height = max(frame.height for frame in trimmed)
    scale = 76 / max_height
    cell_size = 96
    foot_anchor_y = 88
    sheet = Image.new("RGBA", (cell_size * 4, cell_size * 4), (0, 0, 0, 0))

    for index, frame in enumerate(trimmed):
        # One shared scale avoids the size drift caused by normalizing frames alone.
        width = max(1, round(frame.width * scale))
        height = max(1, round(frame.height * scale))
        snapped = nearest(frame, (width, height))
        alpha = snapped.getchannel("A").point(lambda value: 255 if value >= 96 else 0)
        snapped.putalpha(alpha)

        column = index % 4
        row = index // 4
        x = column * cell_size + (cell_size - width) // 2
        y = row * cell_size + foot_anchor_y - height
        sheet.alpha_composite(snapped, (x, y))

    # Quantize the whole sheet together so every direction shares one small palette.
    alpha = sheet.getchannel("A")
    rgb = Image.new("RGB", sheet.size, (255, 0, 255))
    rgb.paste(sheet.convert("RGB"), mask=alpha)
    quantized = rgb.quantize(colors=32, method=Image.Quantize.FASTOCTREE).convert("RGBA")
    quantized.putalpha(alpha)
    quantized.save(OUTPUT / "player-walk.png", optimize=True)
    return {
        "columns": 4,
        "rows": 4,
        "cell": cell_size,
        "anchor": {"x": cell_size // 2, "y": foot_anchor_y},
        "directions": ["south", "west", "east", "north"],
        "framesPerDirection": 4,
    }


def build_supporting_cast() -> dict:
    source = Image.open(SOURCE / "supporting-cast-alpha-source.png").convert("RGBA")
    recovered = recover_character_cells(source)
    bounds = [cell.getbbox() for cell in recovered]
    if any(bound is None for bound in bounds):
        raise RuntimeError("A generated supporting-cast frame was empty")

    trimmed = [cell.crop(bound) for cell, bound in zip(recovered, bounds)]
    max_height = max(frame.height for frame in trimmed)
    scale = 76 / max_height
    cell_size = 96
    foot_anchor_y = 88
    sheet = Image.new("RGBA", (cell_size * 4, cell_size * 4), (0, 0, 0, 0))

    for index, frame in enumerate(trimmed):
        width = max(1, round(frame.width * scale))
        height = max(1, round(frame.height * scale))
        snapped = nearest(frame, (width, height))
        alpha = snapped.getchannel("A").point(lambda value: 255 if value >= 96 else 0)
        snapped.putalpha(alpha)
        column = index % 4
        row = index // 4
        x = column * cell_size + (cell_size - width) // 2
        y = row * cell_size + foot_anchor_y - height
        sheet.alpha_composite(snapped, (x, y))

    alpha = sheet.getchannel("A")
    rgb = Image.new("RGB", sheet.size, (255, 0, 255))
    rgb.paste(sheet.convert("RGB"), mask=alpha)
    quantized = rgb.quantize(colors=40, method=Image.Quantize.FASTOCTREE).convert("RGBA")
    quantized.putalpha(alpha)
    quantized.save(OUTPUT / "supporting-cast.png", optimize=True)
    return {
        "columns": 4,
        "rows": 4,
        "cell": cell_size,
        "anchor": {"x": cell_size // 2, "y": foot_anchor_y},
        "roles": ["harvester", "baker", "counter", "customer"],
        "framesPerRole": 4,
    }


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    manifest = {
        "environment": build_environment(),
        "player": build_player(),
        "supportingCast": build_supporting_cast(),
    }
    (OUTPUT / "atlas-manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    print("Built environment, player, supporting-cast, and manifest assets")


if __name__ == "__main__":
    main()
