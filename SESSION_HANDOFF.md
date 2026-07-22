# Session handoff

Saved: 2026-07-21 (America/Los_Angeles)

## Repository state

- Repository: `keuller-clone/pizza-io`
- Local checkout: `/home/esteban/pizza-io`
- Active branch: `visual-overhaul`
- Last implementation commit: `0e296c6 Build normalized pixel-art atlas renderer`
- Branch tracks `origin/visual-overhaul`.

## Product direction

Completely overhaul Pizza IO into an original, cozy pixel-art farming and restaurant simulation.
Stardew Valley is a genre and atmosphere reference only; do not copy its sprites, characters,
maps, interface, or exact visual designs.

The project is moving from procedural canvas illustrations to normalized bitmap atlases and a
tile-based renderer while preserving the existing farming, baking, serving, hiring, upgrade, and
customer simulation.

## Work completed

- Created and published the `visual-overhaul` branch.
- Reviewed the complete README and original single-file implementation.
- Generated an original 6×6 environment source atlas.
- Generated a four-direction, four-frame player walk sheet.
- Generated walk sheets for the harvester, baker, counter attendant, and customer.
- Preserved original generation output under `assets/source/`.
- Added `tools/build_assets.py` to recover cells, remove frame drift, apply a shared scale, anchor
  feet consistently, harden alpha edges, quantize palettes, and emit normalized atlases.
- Added exact runtime contracts in `assets/generated/atlas-manifest.json`.
- Added explicit atlas loading and error handling to `pizza-io.html`.
- Rebuilt terrain, paths, structures, characters, start screen, HUD, and menus around the new art.
- Documented the recovery-first pixel-art workflow in `README.md` and `assets/README.md`.

## Referenced workflow

The asset process incorporates the video:

`https://www.youtube.com/watch?v=nIAIxvNUrdU`

Key workflow: reference image → pixel-snap anchor → directional anchor → animation generation →
recover frames → curate → snap each frame → apply a consistent ground anchor → normalize and
combine. Generated sheets are source material, never direct runtime assets.

## Validation completed

- Extracted inline JavaScript and passed `node --check`.
- Passed `python3 -m py_compile tools/build_assets.py`.
- Rebuilt all generated assets successfully with `python3 tools/build_assets.py`.
- Passed `git diff --check`.
- Rendered the game in headless Chrome at 1440×900.
- Visually inspected the play-state screenshot.
- Fixed an atlas load-timing defect found during browser validation.

## How to run

```bash
cd /home/esteban/pizza-io
google-chrome pizza-io.html
```

Controls: WASD or arrows to move, E to interact, mouse clicks for hiring and upgrades.

## Recommended next milestone

1. Replace the responsive fraction-based layout with a real logical tile map and collision grid.
2. Add a camera and a larger explorable farm/pizzeria property.
3. Create directional animations for helpers and multiple visually distinct customers.
4. Replace remaining procedural crop icons, effects, and upgrade decorations with curated sprites.
5. Add day/night lighting, ambient animation, weather, and seasonal palette support.
6. Redesign interaction and management UI for smaller screens and controller navigation.
7. Add automated gameplay regression coverage through Chrome DevTools Protocol.

Keep gameplay logic and rendering concerns separate. Continue editing on `visual-overhaul`; do not
merge to `main` until the overhaul is playable and reviewed.
