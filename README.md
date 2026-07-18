# pizza io

**Dev notes** — created 2026-07-18 (Claude Code session, Linux). v2 pass same day: longer customer
patience, a full visual overhaul (growing garden beds, domed oven, decorated farmstand), helper
speed upgrades, and stand decorations.

## Where the game lives

- **The entire game is ONE file:** `pizza-io.html`, at
  `/home/esteban/Documents/pizza io/pizza-io.html`.
- Zero dependencies, no build step, no server. Open the file in any modern browser —
  `xdg-open "pizza-io.html"` from inside the project folder.

## Game summary

Top-down 2D canvas restaurant-sim, farm-themed (Stardew Valley / A Link to the Past inspired — see
the reference screenshot the visual pass was built against). No camera scroll — the whole shop
(garden up top, dirt-path plaza with the farmstand below) fits on one screen, laid out as
fractions of the current window size (`computeLayout()`, recomputed on resize).

**The loop:** walk to a garden bed or the cheese plant and press **E** to harvest → once you're
holding at least 1 wheat, 1 tomato, 1 herb and 1 cheese, press **E** at the domed oven to load a
slot → watch the circular progress ring fill → press **E** again to pull the finished pizza out
onto its tray → carry it (you can hold up to 2) to the farmstand and press **E** to deposit it on
the display → press **E** at the stand again to serve the customer waiting at the front of the
line for gold.

**Ingredients grow, they don't sit in boxes.** Wheat, tomato and herb each have their own tilled
garden bed with 5 individual plant slots (`makePatch()`, `PATCH_OFFSETS`); harvesting a grown
plant knocks it back to a sprout that regrows over 4s. The **cheese plant** is a single
always-there source in its own round bed: it glows when ripe, harvest it for 1 cheese, then it
needs ~10s to regrow (shown as a small growth ring) before it's harvestable again.

**Customers:** spawn every 8–13s (capped at 6 in line, +2 with Patio Tables), queue up on a
diagonal line off the stand, and have 55s of patience (+12s with Planters) shown as a bar over
their head before they give up and storm off with no sale. (v1 shipped with 24s patience / 4–7s
spawns, which wasn't enough time to harvest-bake-serve even one order from scratch — bumped
significantly after that feedback.)

**Hire help** (bottom-right HIRE HELP panel) — each helper, once hired, can also be **upgraded for
more speed** up to 3 levels from the same panel button (cost scales per level):
- **Harvester** ($40) — a farmhand who continuously walks to whichever ingredient bed has a ready
  plant (or a ripe cheese plant), harvests it, and repeats. Each speed level (+40%/level) makes it
  walk and act faster.
- **Counter** ($70) — stands at the stand and serves the front customer the instant there's stock
  and someone waiting. Speed levels shorten its reaction cooldown.
- **Baker** ($110) — tends the oven: loads a free slot whenever there's a full set of ingredients,
  waits for it to finish, carries the pizza to the stand, and repeats. Also cuts cook time by 1s
  per speed level (9s base, 6s once hired, down to a 3s floor at max level) — applies globally,
  not just to bakes the Baker personally loads.

All three roles remain manually doable by the player via the same **E**-interact even after
hiring the corresponding helper — hiring just adds an NPC doing the job in parallel, it doesn't
take the job away from you.

**Upgrade the stand** (bottom-left UPGRADE STAND panel) — one-time cosmetic-plus-perk purchases:
- **Planters** ($45) — flower boxes flanking the counter, +12s customer patience.
- **Patio Tables** ($65) — two little tables with umbrellas beside the stand, +2 max queue length.
- **Lanterns** ($85) — a glowing string of lanterns along the stand roof, +$1 per sale.

There's no win/lose state — it's an open-ended tycoon loop, start screen only.

## Tuning

| constant | value | where |
|---|---|---|
| Oven cook time | 9s (6s once Baker hired, −1s per Baker speed level, floor 3s) | `cookDuration()` |
| Max pizzas player can carry | 2 | `MAX_CARRY` |
| Max pizzas on the stand | 6 | `MAX_STAND` |
| Max customers in line | 6 (+2 with Patio Tables) | `MAX_QUEUE`, `maxQueueEff()` |
| Garden bed regrow | +1 plant ready per 4s per slot, 5 slots per bed | `PATCH_GROW`, `PATCH_OFFSETS` |
| Cheese plant regrow | 10s, single source | `cheesePlant.regrowMax` |
| Customer patience | 55s base (+12s with Planters) | `CUSTOMER_PATIENCE`, `patienceBonus()` |
| Customer spawn interval | random 8–13s | `updateCustomers()` |
| Sale price | random $8–11 per pizza (+$1 with Lanterns) | `salePrice()` |
| Hire costs | Harvester $40 / Counter $70 / Baker $110 | `HIRE_COST` |
| Helper speed upgrade | up to 3 levels, +40% speed/level, cost `base × (level+1)` | `helperSpeedMult()`, `upgradeCost()`, `UPGRADE_BASE_COST` |
| Decoration costs | Planters $45 / Tables $65 / Lanterns $85 | `DECOR_COST` |
| Oven slots | 2 (fixed, not currently purchasable) | `layout.ovenSlots` |

## Code map (all inline in pizza-io.html)

| section | key functions |
|---|---|
| setup/input | `resize()` → `computeLayout()` (fraction-of-window station placement), keydown/keyup (`ePressed` edge trigger), canvas `click` → `handleClick()` for both HUD panels |
| audio | `tone()` WebAudio synth, `sfx.{harvest,step,ovenStart,ovenDone,pickup,deposit,cash,sad,hire,deny}` |
| state | `newGame()`, globals: `player`, `patches.{wheat,tomato,herb}` (each a 5-plant bed), `cheesePlant`, `ovenSlots[2]`, `standStock`, `queue`/`leavers`, `helpers`/`helperLevel`, `decorations`, `npcs.{harvester,baker,counter}` |
| shared actions | `harvestPatch()`, `harvestCheese()`, `canAssemble()`, `loadOven()`, `collectOven()`, `depositPizza()`, `serveFrontCustomer()` — used identically by the player's E-interact **and** the helper AIs, so there's exactly one code path per action regardless of who triggers it |
| interact | `nearestInteract()` — proximity-sorted list of available actions near the player, drives both the E-key dispatch and the on-screen prompt text |
| update | `update()` → `updatePlayer()`, `updateOven()`, `updateCustomers()` (spawn/walk/patience/leave), `updateHelperNPCs()` → `updateHarvesterNPC()`/`updateBakerNPC()`/`updateCounterNPC()` (small per-role state machines, each applying `helperSpeedMult(role)`) |
| draw | `draw()` → `drawBackground()` (grass/dirt zones, fence, trees) → `drawTilledPlot()` + `drawPatch()`×3 (growing crops) → `drawCheesePlant()` → `drawOven()` (domed, chimney/smoke, 2 cook slots) → `drawTables()` → `drawCounter()` (roofed stand + planters/lanterns) → queue/leavers → player + all 3 helper NPCs (`drawFigure()` shared body, per-role palette) → particles/floaters → `drawInteractPrompt()` → `drawHUD()` → `drawHireMenu()` + `drawDecorMenu()` (both populate `buttons[]` for click hit-testing) |
| loop | `frame()` rAF, dt clamped to 0.05s |

## Design notes

- Money/ingredients/oven/queue are one global source of truth; helper NPCs call the *exact same*
  functions the player's E-interact calls (`harvestPatch`, `loadOven`, `collectOven`,
  `depositPizza`, `serveFrontCustomer`) — no duplicated logic between manual and automated paths.
- Both HUD panels' buttons are recomputed into a single `buttons[]` array every `drawHUD()` call
  and hit-tested on canvas `click` via a generic `{x,y,w,h,act}` shape (`act` is a closure) —
  keeps everything on one canvas/one coordinate system rather than real DOM elements, same pattern
  as the interact-prompt text.
- Ingredient beds are literal plant-slot arrays (`patch.plants[i].ready/t`), not a numeric
  "stock/max" counter on a box — the visual (grown vs. sprouting per slot) *is* the state, no
  separate UI needed to know what's harvestable at a glance.
- Visual style is deliberately flat-shaded with bold dark outlines (`ctx.imageSmoothingEnabled =
  false`, 2–3px outlines, 2–3 tone shading with a highlight + shadow pass on character bodies) to
  read like a 16-bit top-down sim rather than blended gradients — most structures (oven, stand,
  huts-equivalent) are drawn "front-elevation" style even though movement is top-down, matching
  how the reference art (and the prior TridentTides project) handles buildings.

## Ideas / next steps (never started)

- Purchasable oven slot(s) beyond the fixed 2.
- Multiple hires per role (a second Harvester, etc.) instead of one each.
- Recipe variety (different toppings unlocked by new ingredients) instead of one fixed pizza.
- Persistent save (localStorage) — currently everything resets on reload.
- Day/shift structure with a closing time and a daily summary instead of endless open shop.
- More decorations (fencing styles, a scarecrow, seasonal skins).

## Testing recipe

Same headless-Chrome CDP-driver approach used for prior projects — no visual browser needed to
verify game logic. Open dev console and poke globals directly, e.g.:
```js
state; money; stock;                             // where am I
patches.wheat.plants;                             // inspect a garden bed's 5 plant slots
player.x = layout.ovenBase.x; player.y = layout.ovenBase.y; ePressed = true;  // interact next tick
ovenSlots[0].t = ovenSlots[0].dur;                // force the current bake to finish instantly
money = 1000;                                     // cheat for testing hires/upgrades/decor
helperLevel.baker = 3;                            // max out a helper's speed without paying
queue.push({ x: 0, y: 0, homeX: 0, homeY: 0, state: 'waiting', patience: 55, maxPatience: 55, hue: 0 });
```
Verified end-to-end via a headless-Chrome CDP driver with zero console exceptions: full manual
loop on the new patch model (harvest all 4 → load oven → force-finish cook → collect → deposit →
serve for gold), garden-bed regrowth (harvested plant becomes ready again after `PATCH_GROW`
seconds), customer-patience timeout at the new 55s default, hire → upgrade-speed → decoration
purchase all via real computed button rects clicked through `handleClick()` (not hardcoded
coordinates), cost scaling and max-level capping on helper upgrades, and a 90-second fully
automated run (all three helpers hired and speed-upgraded) ending with positive gold, healthy
stock flow, and zero customers lost to impatience.

**Bug found and fixed during this pass:** `moveToward()` didn't clamp its per-frame step to the
remaining distance, so a helper moving fast enough to overshoot its target's ~4px arrival radius
in one frame would perpetually oscillate back and forth across the destination and never register
as "arrived" — silently soft-locking that helper (visible as it forever `walk`ing toward its
target, never receiving anything). This got more likely at exactly the moment a player would upgrade
a helper's speed, since a faster helper takes bigger per-frame steps. Caught via a 90-second
automated-helper simulation showing stock/money frozen at zero; fixed by snapping directly to the
target whenever the frame's step would reach or pass it.
