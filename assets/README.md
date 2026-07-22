# Pixel-art asset pipeline

Generated images are source material, not engine-ready sprites. The project follows the recovery
workflow demonstrated in the linked pixel-art production video:

1. Generate a coherent reference image.
2. Recover individual frames or tiles from the generated sheet.
3. Curate usable frames and discard malformed output.
4. Pixel-snap with nearest-neighbour resampling and hard alpha edges.
5. Apply one shared character scale instead of resizing each pose independently.
6. Anchor every animation frame to the same ground contact point.
7. Normalize cells and combine them into a deterministic atlas.
8. Validate the atlas in the actual renderer at integer scale.

`source/` preserves untouched generation output. `generated/` contains files consumed by the game.
Run `python3 tools/build_assets.py` after replacing or adding source art. The current manifest
contains the 6×6 environment atlas, the four-direction player walk cycle, and four supporting-cast
walk cycles (harvester, baker, counter attendant, and customer).

The original generated art uses a warm countryside palette and an original character design. It
must not reproduce sprites, maps, characters, or other protected assets from an existing game.
