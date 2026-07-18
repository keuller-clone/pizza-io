# pizza io

**Dev notes** — created 2026-07-18 (Claude Code session, Linux).

## Where the game lives

- **The entire game is ONE file:** `PizzaIO.html`, at
  `/home/esteban/Documents/pizza io/PizzaIO.html`.
- Zero dependencies, no build step, no server. Open the file in any modern browser —
  `xdg-open "PizzaIO.html"` from inside the project folder.

## Game summary

Top-down 2D canvas restaurant-sim. No camera scroll — the whole shop (garden/kitchen up top,
plaza/stand below) fits on one screen, laid out as fractions of the current window size
(`computeLayout()`, recomputed on resize).

**The loop:** walk to a crate or the cheese plant and press **E** to harvest → once you're
holding at least 1 wheat, 1 tomato, 1 herb and 1 cheese, press **E** at the oven to load a slot →
watch the circular progress ring fill → press **E** again to pull the finished pizza out onto its
tray → carry it (you can hold up to 2) to the stand and press **E** to deposit it on the display →
press **E** at the stand again to serve the customer waiting at the front of the line for gold.

**Ingredients:** wheat / tomato / herb crates hold up to 5 each and regenerate 1 every 4s once
below max. The **cheese plant** is a single always-there source: it glows when ripe, harvest it
for 1 cheese, then it needs ~10s to regrow (shown as a small growth ring) before it's harvestable
again.

**Customers:** spawn every 4–7s (capped at 6 in line), queue up on a diagonal line off the stand,
and have 24s of patience (shown as a bar over their head) before they give up and storm off with
no sale.

**Hire help** (click the panel, bottom-right of the HUD):
- **Harvester** ($40) — a farmhand who continuously walks to whichever ingredient source has
  stock (or a ripe cheese plant), harvests it, and repeats.
- **Counter** ($70) — stands at the stand and serves the front customer the instant there's stock
  and someone waiting, faster/more reliably than the player remembering to walk over.
- **Baker** ($110) — tends the oven: loads a free slot whenever there's a full set of ingredients,
  waits for it to finish, carries the pizza to the stand, and repeats. Also cuts cook time from
  9s to 6s (applies globally, not just to bakes the Baker personally loads).

All three roles remain manually doable by the player via the same **E**-interact even after
hiring the corresponding helper — hiring just adds an NPC doing the job in parallel, it doesn't
take the job away from you.

There's no win/lose state — it's an open-ended tycoon loop, start screen only.

## Tuning

| constant | value | where |
|---|---|---|
| Oven cook time | 9s (6s once Baker hired) | `cookDuration()` |
| Max pizzas player can carry | 2 | `MAX_CARRY` |
| Max pizzas on the stand | 6 | `MAX_STAND` |
| Max customers in line | 6 | `MAX_QUEUE` |
| Box regen | +1 per 4s, up to 5 | `BOX_REGEN`, `boxes.*.max` |
| Customer patience | 24s | `CUSTOMER_PATIENCE` |
| Sale price | random $8–11 per pizza | `salePrice()` |
| Hire costs | Harvester $40 / Counter $70 / Baker $110 | `HIRE_COST` |
| Oven slots | 2 (fixed, not currently purchasable) | `layout.ovenSlots` |

## Code map (all inline in PizzaIO.html)

| section | key functions |
|---|---|
| setup/input | `resize()` → `computeLayout()` (fraction-of-window station placement), keydown/keyup (`ePressed` edge trigger), canvas `click` → `handleClick()` for the hire panel |
| audio | `tone()` WebAudio synth, `sfx.{harvest,step,ovenStart,ovenDone,pickup,deposit,cash,sad,hire,deny}` |
| state | `newGame()`, globals: `player`, `boxes.{wheat,tomato,herb}`, `cheesePlant`, `ovenSlots[2]`, `standStock`, `queue`/`leavers`, `helpers`, `npcs.{harvester,baker,counter}` |
| shared actions | `harvestBox()`, `harvestCheese()`, `canAssemble()`, `loadOven()`, `collectOven()`, `depositPizza()`, `serveFrontCustomer()` — used identically by the player's E-interact **and** the helper AIs, so there's exactly one code path per action regardless of who triggers it |
| interact | `nearestInteract()` — proximity-sorted list of available actions near the player, drives both the E-key dispatch and the on-screen prompt text |
| update | `update()` → `updatePlayer()`, `updateOven()`, `updateCustomers()` (spawn/walk/patience/leave), `updateHelperNPCs()` → `updateHarvesterNPC()`/`updateBakerNPC()`/`updateCounterNPC()` (small per-role state machines) |
| draw | `draw()` → zones/boxes/cheese-plant/oven (`drawRadialProgress()` reused for both cook progress and cheese regrowth), counter, queue/leavers, player + all 3 helper NPCs (`drawFigure()` shared body, per-role palette), particles/floaters, `drawInteractPrompt()`, `drawHUD()` → `drawHireMenu()` (also populates `buttons[]` for click hit-testing) |
| loop | `frame()` rAF, dt clamped to 0.05s |

## Design notes

- Money/ingredients/oven/queue are one global source of truth; helper NPCs call the *exact same*
  functions the player's E-interact calls (`harvestBox`, `loadOven`, `collectOven`,
  `depositPizza`, `serveFrontCustomer`) — no duplicated logic between manual and automated paths.
- The hire-menu buttons are recomputed into a `buttons[]` array every `drawHireMenu()` call and
  hit-tested on canvas `click`, rather than being real DOM elements — keeps everything on one
  canvas/one coordinate system, same pattern as the interact-prompt text.
- Visual style is deliberately flatter and more heavily outlined than a softer painterly look
  (`ctx.imageSmoothingEnabled = false`, 2–3px dark outlines, flat 1–2 tone shading) to read more
  like a 16-bit top-down sim (Stardew Valley / A Link to the Past) rather than blended gradients.

## Ideas / next steps (never started)

- Purchasable oven slot(s) beyond the fixed 2.
- Multiple hires per role (a second Harvester, etc.) instead of one each.
- Upgrades: bigger crates, faster player walk speed, higher sale price.
- Recipe variety (different toppings unlocked by new ingredients) instead of one fixed pizza.
- Persistent save (localStorage) — currently everything resets on reload.
- Day/shift structure with a closing time and a daily summary instead of endless open shop.

## Testing recipe

Same headless-Chrome CDP-driver approach used for prior projects — no visual browser needed to
verify game logic. Open dev console and poke globals directly, e.g.:
```js
state; money; stock;                             // where am I
player.x = layout.ovenBase.x; player.y = layout.ovenBase.y; ePressed = true;  // interact next tick
ovenSlots[0].t = ovenSlots[0].dur;                // force the current bake to finish instantly
money = 500;                                      // cheat for testing hires
queue.push({ x: 0, y: 0, homeX: 0, homeY: 0, state: 'waiting', patience: 24, maxPatience: 24, hue: 0 });
```
Verified end-to-end via a headless-Chrome CDP driver with zero console exceptions: full manual
loop (harvest all 4 → load oven → force-finish cook → collect → deposit → serve for gold),
customer-patience timeout (leaves unhappy, removed from queue), hire-menu click using the real
computed button rect (not a hardcoded coordinate), 20 simulated seconds of unattended Harvester
AI (gathers a mix of all ingredient types on its own), and ~50 simulated seconds of combined
Baker + Counter automation (bakes, runs pizzas to the stand, and serves customers with zero
player input, net positive gold). Also screenshotted to check the visual layout — caught and
fixed one bug this way (the Counter helper's idle spot originally overlapped the stand's stock
count label).
