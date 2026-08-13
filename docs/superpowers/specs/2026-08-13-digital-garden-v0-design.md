# Digital Garden V0 — Design Specification

**Status:** Approved design contract; written spec pending user review  
**Date:** 2026-08-13  
**Target platform:** Windows 11 desktop  
**Purpose:** Define the smallest deterministic living world that can support the future Digital Garden desktop artifact and later become a controlled learning environment for a neural Garden Brain.

## 1. Product intent

Digital Garden is an ambient living desktop artifact, not a conventional application and not a game.

Its primary visual form is a medium-sized patch of living garden embedded into the desktop. When collapsed, a small organic vine anchor remains persistently visible in a compact always-on-top region. Interacting with that vine unfolds the full garden rather than opening a normal bordered window.

The Garden should feel:

- calm rather than demanding;
- alive rather than animated for decoration;
- persistent rather than session-based;
- organic rather than window/chrome based;
- interesting under both care and neglect.

Neglect must produce wildness, not punishment. V0 has no scores, streaks, XP, energy systems, death screens, or nagging notifications.

The focal object is a stylised classic bonsai. It is the persistent heart of the garden and is not replaceable during V0.

## 2. V0 scope

V0 contains two tightly separated layers.

### V0-A — Garden World

A deterministic, persistent simulation that can run completely headlessly.

It owns:

- time;
- weather;
- soil;
- bonsai condition;
- ground growth;
- vine growth;
- user actions;
- state transitions;
- persistence;
- observability.

### V0-B — Desktop Artifact

A visual representation of that world.

It owns:

- persistent vine anchor;
- collapsed/expanded state;
- medium garden patch;
- visual state rendering;
- interaction controls;
- inspection surface.

The desktop layer never decides what happens to the garden. It requests actions from the Garden World and renders the resulting authoritative state.

## 3. Explicit V0 exclusions

V0 will not contain:

- neural-network decision making;
- reinforcement learning;
- LLMs;
- real-world weather APIs;
- autonomous gardening actions;
- plant death;
- multiple gardens;
- inventory;
- currencies;
- achievements;
- social systems;
- notifications;
- complex botanical simulation;
- arbitrary planting;
- procedural 3D world generation;
- hover-triggered interaction;
- right-click action menus.

The purpose of V0 is to establish a small world trustworthy enough to learn inside later.

## 4. Visual composition

The expanded artifact is a medium living desktop patch divided conceptually into three ecological regions.

### Ground layer

Contains visual elements such as moss, grass, clover, tiny flowers, exposed soil, and occasional mushrooms after wet conditions. This layer is the clearest visual expression of moisture and neglect.

### Focal layer — Stylised Bonsai

The bonsai has:

- a gently twisted trunk;
- visible root flare;
- a layered asymmetrical canopy;
- moss around its base;
- expressive but non-photorealistic foliage.

It must remain recognisable at widget scale.

### Edge layer

Contains ivy, creeping vines, wild grass, and other edge growth. This is where uncontrolled growth becomes visually obvious.

The persistent vine anchor is understood visually as an outgrowth of this same garden.

## 5. Core simulation entities

V0 contains five conceptual entities:

```text
GardenWorld
    |
    +-- Weather
    |
    +-- GardenPatch
            |
            +-- Soil
            +-- Bonsai
            +-- GroundCover
            +-- EdgeVine
```

Each unit has one responsibility.

### GardenWorld

Owns logical time, deterministic random seed, and weather progression.

### Soil

Owns available moisture.

### Bonsai

Owns the focal tree's growth and condition.

### GroundCover

Owns moss/grass/small-growth density.

### EdgeVine

Owns vine extent and the state that eventually drives the persistent desktop anchor.

## 6. State model

Most biological and environmental values use a normalized range:

```text
0.0 = minimum
1.0 = maximum
```

This keeps V0 simple and gives the future neural network a clean numerical observation space.

### World state

```text
seed
tick
day_index
hour_of_day
weather
light_level
humidity
```

Weather is an enum:

```text
SUNNY
CLOUDY
RAINY
```

### Soil state

```text
soil_moisture: 0.0–1.0
```

### Bonsai state

```text
health:          0.0–1.0
stress:          0.0–1.0
growth:          0.0–1.0
canopy_density:  0.0–1.0
```

`growth` represents long-term development. `canopy_density` represents how full or unmanaged the foliage currently is. These are intentionally separate: a mature bonsai can be beautifully maintained or heavily overgrown.

### Ground-cover state

```text
ground_density: 0.0–1.0
```

### Edge-vine state

```text
vine_extent: 0.0–1.0
```

### Derived garden state

```text
garden_health
overgrowth
anchor_state
garden_condition
```

These are derived values, not independently mutable state. This prevents contradictory conditions without an explicit mathematical reason.

## 7. Time model

The simulation uses a logical garden-hour as its atomic time step.

```text
24 ticks = 1 garden day
```

Production mode maps those ticks to elapsed real time. Testing and experimentation may advance ticks instantly.

The same simulation logic is used in both modes:

```text
Desktop mode:
real time -> elapsed garden hours -> state update

Experiment mode:
advance(10_000 ticks)
```

There must be no separate fast-simulation physics.

## 8. Determinism requirement

Given:

```text
initial state
+ seed
+ elapsed ticks
+ ordered user-action sequence
```

the resulting garden state must be exactly reproducible.

This is a hard architectural requirement. It allows later learning experiments to distinguish controller improvement from uncontrolled simulation differences.

## 9. Weather model

V0 weather is internally generated and selected once per garden day. The generator is seeded and therefore replayable.

Weather should exhibit persistence rather than completely independent daily rolls. A simple transition model is sufficient:

```text
SUNNY
  -> usually SUNNY/CLOUDY
  -> occasionally RAINY

CLOUDY
  -> may become SUNNY
  -> may remain CLOUDY
  -> may become RAINY

RAINY
  -> commonly becomes CLOUDY
  -> sometimes continues
  -> occasionally clears
```

Exact transition probabilities are implementation constants and must be explicit and tested.

### Weather effects

**Sunny**

- soil moisture decreases faster;
- light increases;
- humidity decreases;
- healthy growth continues.

**Cloudy**

- soil dries slowly;
- light is moderate;
- humidity is moderate;
- growth is slow and steady.

**Rainy**

- soil moisture rises;
- humidity rises;
- growth potential rises;
- overgrowth potential rises.

Rain is not universally beneficial. A garden that is already extremely wet can become stressed.

## 10. Bonsai health model

Bonsai health is primarily influenced by:

- soil-moisture fitness;
- current stress;
- canopy condition;
- recent environmental conditions.

There is a preferred moisture band rather than a single ideal number.

The V0 moisture-health constants are:

```text
healthy moisture band: 0.40–0.70
```

Below this band, dryness stress increases and health gradually declines. Above this band, overwatering stress increases and health gradually declines.

Health changes slowly. One bad hour cannot destroy the bonsai.

## 11. No-death rule

The V0 bonsai cannot die.

Its condition may become:

```text
THRIVING
HEALTHY
WILD
STRESSED
STRUGGLING
```

but there is no terminal death state. Even a heavily neglected garden remains recoverable.

This is both a product decision and a useful learning-system property: the simulation does not terminate because an early controller makes poor decisions.

## 12. Growth and overgrowth

Growth and overgrowth are intentionally different.

### Healthy growth

The bonsai gradually matures when moisture is suitable, stress is low, and environmental conditions are reasonable. Long-term `growth` generally moves upward and is not removed by ordinary trimming.

### Canopy density

The bonsai canopy naturally thickens. Too little density may indicate over-pruning. Too much density represents an unmanaged tree.

### Ground density

Ground cover slowly grows under suitable conditions. Wet conditions accelerate it.

### Vine extent

Edge vines slowly spread. Rain and high humidity accelerate them.

The derived `overgrowth` score is calculated primarily from:

```text
canopy_density
ground_density
vine_extent
```

This allows a healthy but increasingly wild garden to exist.

## 13. User actions

V0 has exactly four user-facing interactions.

### WATER

Raises `soil_moisture`.

```text
dry garden -> usually beneficial
already wet garden -> risk of additional stress
```

Watering must not be an always-correct action.

### TRIM

Targets ground and edge growth.

Effects:

```text
ground_density decreases
vine_extent decreases modestly
```

It does not directly prune the bonsai. Trim is routine surrounding maintenance.

### PRUNE

Targets the bonsai.

Effects:

```text
canopy_density decreases
temporary stress may increase
```

A correctly timed prune can improve long-term bonsai condition. Repeated or excessive pruning can be harmful.

### INSPECT

Changes no simulation state.

It exposes a compact telemetry view containing at minimum:

```text
weather
soil moisture
bonsai condition
overgrowth
```

More detailed developer/debug telemetry may exist separately.

## 14. Garden health

`garden_health` is a derived summary value. It should be dominated by bonsai condition but incorporate the surrounding ecosystem.

Conceptually:

```text
garden_health =
    bonsai health
    + moisture fitness
    + manageable surrounding growth
```

Exact weighting must remain explicit implementation constants covered by tests.

A garden does not need to be perfectly manicured to be healthy:

```text
wild != unhealthy
```

Overgrowth becomes unhealthy only when it materially stresses the garden.

## 15. Human-facing garden conditions

Continuous values collapse into a few broad presentation states.

### THRIVING

- excellent bonsai condition;
- low stress;
- appropriate moisture;
- balanced growth.

### HEALTHY

- garden is within normal operating range.

### WILD

- garden is healthy enough;
- ground/vine growth is visibly high;
- maintenance would change appearance but is not urgent.

### STRESSED

- moisture or canopy condition is outside the preferred range;
- bonsai stress is elevated.

### STRUGGLING

- poor conditions have been sustained;
- the garden remains recoverable.

These states drive visual treatment rather than exposing raw numbers continuously.

## 16. Persistent vine anchor

Collapsed mode leaves an organic vine visible in a compact always-on-top region near a desktop edge or corner.

The vine is both:

1. the interaction handle that reveals the Garden;
2. a compressed visual indicator of garden state.

Derived anchor states are:

```text
CALM
DRY
WILD
THRIVING
STRESSED
```

Examples:

- **CALM:** green, tidy vine;
- **DRY:** slightly pale or curling foliage;
- **WILD:** thicker, tangled growth;
- **THRIVING:** rich foliage and possibly a small bloom;
- **STRESSED:** visibly less vigorous without becoming alarming.

No numeric badges or notification dots are required.

## 17. Expand and collapse behavior

### Collapsed

Only the compact vine anchor remains always-on-top. Its footprint must be small enough not to interfere materially with normal work.

### Expanded

A single click on the anchor unfolds the medium garden patch adjacent to the vine. The expanded patch may temporarily occupy the foreground while the user interacts with it, but it is not intended to remain floating over active work after dismissal.

The expanded state must not visually resemble opening a conventional application window.

V0 interaction contract:

```text
single click anchor -> expand
single click explicit collapse control -> collapse
single click outside expanded garden -> collapse
Water / Trim / Prune / Inspect -> available inside expanded garden
```

Hover-triggered behavior and right-click action menus are excluded from V0.

## 18. Persistence

Closing the application or restarting Windows must not reset the garden.

Persist at minimum:

```text
schema_version
seed
last_processed_time
world state
soil state
bonsai state
ground state
vine state
```

On resume:

```text
load persisted state
-> calculate elapsed logical ticks
-> advance the same deterministic simulation
-> present current state
```

The state must never depend on the Garden having remained continuously open.

## 19. Experience ledger

V0 records a small append-only interaction history even though there is no AI yet.

Each meaningful event is representable as:

```text
tick
pre_state
action_source
action
post_state
```

Initial `action_source` values are:

```text
USER
SYSTEM
```

Future values may include:

```text
EXPERT
BRAIN
```

A future `reward` field may be introduced when reinforcement learning begins.

The ledger provides raw material for later learning experiments without changing the world engine retrospectively.

## 20. Future Garden Brain interface

The simulation exposes a machine-readable observation without depending on any neural-network implementation.

The provisional V1 observation vector is:

```text
soil_moisture
bonsai_health
bonsai_stress
bonsai_growth
canopy_density
ground_density
vine_extent
light_level
humidity
weather_sunny
weather_cloudy
weather_rainy
```

This is a 12-value state vector.

A future controller may choose among:

```text
LEAVE_ALONE
WATER
TRIM
PRUNE
```

A possible first Garden Brain architecture is `12 -> 16 -> 16 -> 4`, but this architecture is explicitly outside V0 acceptance.

The world must not know or care whether its eventual controller is deterministic rules, the handwritten neural network, PyTorch, an open-weight model, an LLM teacher, or a human.

## 21. Deterministic expert gardener — future V1

The first intelligence introduced after V0 should probably be an explicit deterministic policy rather than a neural network:

```text
if too dry:
    WATER

if surrounding growth is excessive:
    TRIM

if bonsai canopy is excessive:
    PRUNE

otherwise:
    LEAVE_ALONE
```

The point is not sophistication. The expert provides a known behavioral baseline from which supervised examples can be generated and used to test whether a tiny neural network can learn the policy.

## 22. V0 acceptance criteria

Digital Garden V0 is complete only when all of the following are demonstrated.

### Simulation

- same seed + same initial state + same action sequence + same ticks produce identical state;
- weather progression is deterministic;
- soil moisture responds correctly to weather and watering;
- excessive dryness and wetness increase bonsai stress;
- trim affects surrounding growth but not bonsai canopy;
- prune affects bonsai canopy;
- over-pruning can increase stress;
- neglect produces increasing wildness;
- the bonsai remains recoverable;
- no plant-death terminal state exists.

### Persistence

- state survives restart;
- elapsed closed time advances the same simulation;
- persisted state is versioned.

### Observability

- full garden snapshot can be serialized;
- the 12-value future observation vector can be produced;
- user/system actions are recorded in the experience ledger.

### Desktop artifact

- collapsed state leaves only the compact always-on-top vine anchor;
- expanding reveals a medium garden patch adjacent to the anchor;
- the expanded patch dismisses back to the vine anchor without remaining over active work;
- normal interaction does not require a conventional bordered-window presentation;
- anchor appearance reflects garden condition;
- Water, Trim, Prune, and Inspect are accessible inside the expanded patch.

### Engineering

- world engine runs headlessly;
- visual rendering is not authoritative;
- no neural or LLM dependency exists;
- core simulation rules are deterministic and testable;
- accelerated simulation uses the exact same world logic as real-time execution.

## 23. Guiding architectural rule

The most important contract for the project is:

> **The Garden determines what is true. Intelligence only decides what to do about it.**

The control loop is therefore:

```text
Garden World
    |
    | observation
    v
Garden Brain
    |
    | action request
    v
Garden World
    |
    | outcome
    v
Experience Ledger
```

The brain can never directly alter health, weather, moisture, growth, or reward. It can only request legitimate garden actions.

## 24. V0 build order

The recommended implementation sequence is:

```text
1. State contracts
        |
2. Deterministic clock + seeded weather
        |
3. Soil model
        |
4. Bonsai model
        |
5. Ground + vine growth
        |
6. User actions
        |
7. Derived health / anchor states
        |
8. Persistence + elapsed-time replay
        |
9. Experience ledger
        |
10. Headless accelerated simulation
        |
11. Desktop vine anchor
        |
12. Expanded garden patch
```

The Garden Brain begins only after step 12 has a preserved baseline.

## 25. Design conclusion

V0 creates a very small but meaningful artificial world:

```text
weather
   |
moisture
   |
bonsai / ground / vines
   |
health + wildness
   |
user intervention
   |
new state
```

The first version contains no learned intelligence, yet every part of the cycle becomes observable training evidence.

The central experiment for later phases is therefore:

> **Can a tiny intelligence learn to care for a world better over time?**

V0 exists to make that question measurable, reproducible, and visually meaningful.
