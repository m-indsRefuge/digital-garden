# Digital Garden V0-B — Desktop Artifact Design

**Status:** Approved direction; written production specification pending user review  
**Date:** 2026-08-14  
**Base:** clean `main` after the preserved V0-A Garden World baseline  
**Approved desktop technology:** PySide6 / Qt 6  
**Initial renderer:** QWidget + QPainter  
**Target platform:** Windows 11 desktop

## 1. Purpose

V0-B turns the deterministic V0-A Garden World into a persistent, visually appealing desktop artifact without moving simulation authority into the UI.

The user experience is a living desktop patch rather than a conventional application window:

```text
collapsed: compact vine anchor
          |
         click
          v
expanded: organic medium garden patch
          |
          +-- stylised bonsai
          +-- ground/moss/clover/grass
          +-- edge vines
          +-- weather/ambient visuals
          +-- WATER / TRIM / PRUNE / INSPECT
```

The artifact must remain calming, unobtrusive, persistent, and interesting when unattended. No standard window chrome, nagging notifications, streaks, energy systems, death screens, or game-like punishment are introduced.

## 2. Proven technology baseline

The V0-B-0 PySide6 spike proved on the target Windows 11 environment that Qt can provide:

- frameless translucent top-level windows;
- shaped `QRegion` desktop artifacts;
- always-on-top compact anchor behavior;
- single-click expansion into an attached patch;
- pure-Qt `ActivationChange` outside dismissal;
- transparent-region input integrity;
- multi-screen positioning;
- direct `GardenService` snapshot/action integration.

V0-B graduates these proven mechanisms deliberately. Prototype artwork, diagnostic controls, spike-specific class layout, and temporary geometry are not automatically production architecture.

## 3. Architectural rule

The Garden remains authoritative.

```text
Garden World
    |
    v
GardenService
    |
    v
Desktop Presentation Model
    |
    +-- Desktop Window System
    |
    +-- Renderer
    |
    +-- Interaction Surface
```

The desktop layer may:

- read authoritative state through `GardenService`;
- translate that state into presentation-only render state;
- request legitimate actions through `GardenService`;
- retain desktop-only preferences such as window position.

The desktop layer must not:

- assign Garden World values directly;
- duplicate weather, moisture, health, stress, growth, or overgrowth rules;
- introduce a second simulation clock;
- decide biological outcomes;
- approve learned actions or rewards;
- make renderer-local state authoritative.

Guiding rule:

> The Garden determines what is true. The desktop artifact determines how truth is shown.

## 4. Production package boundaries

V0-B should introduce focused production components rather than one large UI file.

Recommended conceptual structure:

```text
src/digital_garden/desktop/
    __init__.py
    app.py
    controller.py
    presentation.py
    placement.py
    windows.py
    interaction.py
    persistence.py
    scene/
        __init__.py
        model.py
        renderer.py
        bonsai.py
        ground.py
        vines.py
        weather.py
        ambience.py
```

Exact filenames may be adjusted during planning, but the responsibilities must remain separated:

- `controller`: owns GardenService-facing UI orchestration;
- `presentation`: converts authoritative snapshots into immutable render state;
- `placement`: monitor-aware geometry and anchor/patch positioning;
- `windows`: proven transparent/frameless/window-lifecycle mechanics;
- `interaction`: maps user UI actions to GardenService requests;
- desktop `persistence`: stores only desktop-artifact preferences, never Garden physics;
- `scene/*`: visual composition and procedural rendering only.

## 5. Renderer strategy and portability

### Initial renderer

V0-B begins with QWidget + QPainter because that technology path has already been proven on the real Windows desktop.

QPainter is expected to support the initial stylised 2D visual language:

- antialiased vector forms;
- transparent layered composition;
- gradients and soft shading;
- transformed raster/vector assets where appropriate;
- rain streaks/drops;
- moss, clover, grass, soil, vines and mushrooms;
- subtle branch/leaf/ground movement;
- weather-dependent light and atmosphere.

### Renderer portability requirement

No GardenService or window-lifecycle code may depend directly on QPainter-specific scene internals.

The renderer consumes a stable presentation contract. The future renderer may be replaced by Qt Quick/QML or another Qt rendering path without redesigning Garden World or GardenService.

Conceptually:

```text
GardenService
     |
     v
PresentationModel
     |
     v
Renderer interface
     |
     +-- V0-B / early V1: QPainter
     |
     +-- future if justified: Qt Quick scene graph
```

A renderer migration is justified by measured visual-complexity/performance evidence, not by speculation.

## 6. Scene composition

The expanded artifact is a scene composed from independent visual systems rather than a monolithic `paintEvent()`.

### 6.1 Focal bonsai

Persistent stylised classic bonsai:

- gently twisted trunk;
- visible root flare;
- layered asymmetrical canopy;
- moss around the base;
- expressive non-photorealistic foliage;
- readable at desktop-artifact scale.

V0-B must map authoritative Garden state into visible variation:

- `health` influences vitality/color/overall visual strength;
- `stress` influences droop/tension/subtle distress cues;
- `growth` influences mature structural fullness;
- `canopy_density` influences foliage density.

Routine TRIM does not visually erase accumulated bonsai growth.

### 6.2 Ground system

Ground scene may include:

- moss;
- grasses;
- clover;
- tiny flowers;
- exposed soil;
- mushrooms under suitable wet conditions.

`ground_density` controls visible ground-cover abundance. Ground evolution must appear persistent rather than randomly replacing the entire patch every frame.

### 6.3 Edge-vine system

`vine_extent` controls how far edge vines and wild grasses spread beyond the core composition and toward the persistent anchor.

The vine anchor remains visually connected to the garden, not a detached launcher icon.

### 6.4 Weather system

Weather is rendered from authoritative V0-A weather/environment state.

Examples:

- `SUNNY`: brighter light, drier atmosphere, warmer highlights;
- `CLOUDY`: softer, flatter light;
- `RAINY`: rain visuals, wet highlights, darker soil/moss treatment, higher visual humidity.

Weather effects never alter Garden World values directly.

## 7. Procedural variation: random-looking but reproducible

Low-level visual variation is not generated by the neural network.

The visual system uses deterministic seeded procedural variation to make the garden feel organic and non-repeating while preserving reproducibility.

The system distinguishes two classes of variability.

### 7.1 Authoritative environmental variability

If a variable can affect the actual Garden World, it belongs in the Garden World and is persisted/replayed there.

Examples may eventually include wind or additional environment values, but V0-B must not invent new authoritative physics unless separately specified.

### 7.2 Decorative micro-variation

Purely visual details belong in the renderer and do not become Garden World state.

Examples:

- which individual leaf sways more strongly;
- exact rain-drop placement;
- small grass-blade phase offsets;
- subtle shimmer/highlight movement;
- future insect decorative motion.

These should be derived deterministically from stable inputs such as:

```text
garden seed + logical time/tick + visual object id
```

Use smooth correlated functions/phase variation rather than frame-by-frame independent random values. Decorative motion must feel continuous, not jittery.

## 8. Persistent procedural identity

The garden should develop visual identity over time.

For systems such as grass, clover, mushrooms or future flowers, the garden seed should define a stable pool of candidate objects/sites. State changes reveal, hide, grow, or modify those candidates instead of generating a completely new layout every refresh.

Example:

```text
seed -> stable candidate ground-cover map

ground_density 0.35 -> subset visible
ground_density 0.55 -> more of the same persistent candidates visible
ground_density 0.80 -> dense persistent scene
```

This principle should make a recognizable clover patch or mushroom site remain part of the same garden history.

## 9. Extensibility beyond V1

The scene architecture must permit future independent visual entity families without rewriting the core renderer.

Potential later systems include:

- insects;
- butterflies/fireflies;
- lizards or other small fauna;
- additional flowers;
- alternate bonsai/tree species;
- user-planted secondary plants;
- decorative stones or natural objects.

V0-B does not implement these features. It only preserves clean scene boundaries so future entity systems can consume presentation/environment state and render independently.

No future decorative entity may silently become authoritative Garden World logic.

## 10. Interaction model

The user-facing Garden actions remain exactly:

```text
WATER
TRIM
PRUNE
INSPECT
```

The production UI should not resemble four ordinary application buttons pasted onto a panel. Controls should be quiet contextual affordances integrated into the artifact while remaining discoverable and accessible.

Every mutating interaction routes through:

```python
GardenService.apply(...)
```

`INSPECT` reads authoritative state and may reveal a lightweight information surface without becoming a conventional dashboard.

No hover-only critical controls. No right-click action menu in V0-B.

## 11. Collapsed anchor

The persistent vine anchor remains the ambient default state.

Requirements:

- compact and organic;
- always above ordinary applications;
- no unnecessary keyboard focus;
- draggable/repositionable;
- visually summarizes the Garden's derived anchor state;
- single click expands the attached garden;
- remains connected visually to the edge-vine system.

Anchor states remain:

```text
CALM
DRY
WILD
THRIVING
STRESSED
```

No badge dots, counters, alerts, or notification chrome.

## 12. Expanded patch

The expanded surface is a medium organic patch attached to the vine anchor.

Requirements:

- transparent between scene elements;
- no opaque rectangular panel surrounding the garden;
- no Windows title bar/border;
- correct placement on the anchor's current screen;
- pure-Qt outside dismissal using the proven activation-change behavior;
- explicit collapse affordance remains available;
- visible/interactable areas receive clicks;
- transparent/non-artifact regions do not materially block underlying desktop interaction.

## 13. Persistence and elapsed-time behavior

Garden World persistence remains authoritative and should continue using the V0-A elapsed-time replay model.

The production artifact should add desktop-only persistence for at least:

- anchor position;
- most recent valid screen/geometry context needed to restore safely;
- collapsed/expanded startup policy if explicitly chosen during planning.

Desktop persistence must recover safely if a monitor is removed or display geometry changes.

Closing and reopening Digital Garden must not create a separate visual simulation. Garden World computes elapsed logical ticks; the desktop artifact renders the resulting authoritative snapshot.

## 14. Ambient animation policy

Animation is allowed only after static state mapping and production window behavior are correct.

Animations must be:

- subtle;
- state/environment driven where meaningful;
- resource-conscious;
- non-blocking to user desktop work;
- visually smooth;
- disposable/reconstructable rather than authoritative.

Examples:

- leaf/grass sway;
- rain motion;
- soft lighting changes;
- gradual visual reveal of growing ground cover;
- vine-tip movement.

Animation does not advance Garden World time.

## 15. Performance and renderer escalation gate

Because this artifact is intended to live continuously on the desktop, resource efficiency is a product requirement.

V0-B must establish observable baselines for:

- idle CPU usage;
- active-animation CPU usage;
- memory footprint;
- repaint frequency/frame pacing;
- responsiveness while ordinary desktop applications are in use.

Do not migrate to Qt Quick/QML merely because richer visuals are desired.

Evaluate a renderer migration only if measured QPainter behavior becomes a material limitation for:

- frame-rate stability;
- CPU/GPU efficiency;
- number of independently animated elements;
- required visual effects;
- maintainability of scene composition.

If a migration is required, keep the existing presentation contract and replace the renderer behind it.

## 16. Root and Garden Brain boundary

NN-01 is named:

> **Root — Neural Network From Scratch**

Root remains a preserved foundational neural-network learning/reference project. Digital Garden does not import or mutate Root's XOR implementation into production.

A future Garden Brain may descend conceptually from lessons learned in Root, using the already-designed 12-value Garden observation and four actions:

```text
LEAVE_ALONE
WATER
TRIM
PRUNE
```

The Garden Brain chooses actions. It does not generate weather, procedural art, wind micro-motion, rain-drop positions, or other low-level randomness.

Conceptually:

```text
ROOT
  |
  | neural-engineering knowledge
  v
Garden Brain
  |
  | observes authoritative state
  | chooses legitimate actions
  v
GardenService
```

Intelligence remains separable from environmental stochasticity and visual procedural variation.

## 17. V0-B delivery slices

V0-B should be delivered in four production campaigns rather than one large implementation.

### V0-B.1 — Production Desktop Shell

- clean production `desktop` package;
- production anchor/patch lifecycle;
- proven transparency/masks/focus/dismissal/multi-screen behavior;
- immutable presentation adapter from GardenService;
- desktop-position persistence boundary;
- no visual complexity beyond what is needed to validate production structure.

### V0-B.2 — Living Garden Renderer

- stylised bonsai;
- ground-cover system;
- vines;
- weather presentation;
- persistent seeded visual identity;
- authoritative state-to-visual mappings;
- static or minimal motion first.

### V0-B.3 — Production Interaction Layer

- WATER;
- TRIM;
- PRUNE;
- INSPECT;
- contextual artifact-native interaction design;
- action feedback sourced from authoritative state.

### V0-B.4 — Persistence, Ambient Life, and Performance

- elapsed-time resume integrated into desktop lifecycle;
- robust multi-monitor position restore;
- state-driven ambient animation;
- rain and environmental motion;
- resource/performance baseline;
- renderer escalation decision if evidence requires it.

## 18. V0-B exclusions

V0-B does not include:

- Garden Brain / neural decisions;
- LLM integration;
- reinforcement learning;
- real-world weather API;
- autonomous gardening;
- multiple gardens;
- arbitrary planting;
- insects/lizards/fauna;
- inventory/currency/achievements;
- notifications;
- procedural 3D rendering;
- Qt Quick/QML unless a later measured renderer gate explicitly authorizes it.

## 19. Acceptance boundary

V0-B is complete when:

1. the artifact reliably lives on the Windows desktop in collapsed and expanded forms;
2. Garden World state visibly changes the bonsai, ground, vines and weather presentation;
3. WATER/TRIM/PRUNE/INSPECT operate only through GardenService;
4. Garden persistence and elapsed-time resume remain deterministic;
5. desktop position/lifecycle are robust across available displays;
6. the artifact is graphically coherent and pleasant enough to leave running as a desktop object;
7. ambient motion/weather effects are smooth and resource-conscious;
8. renderer performance is measured and either accepted or escalated with evidence;
9. V0-A deterministic behavior remains preserved;
10. no intelligence layer has been introduced prematurely.

## 20. Strategic outcome

V0-B should leave Digital Garden as a complete human-operated living desktop ecosystem with a replaceable renderer and authoritative deterministic world.

That creates the clean foundation for later work:

```text
V0-A Garden World
      +
V0-B Desktop Artifact
      =
V1 Living Garden
      |
      v
future Garden Brain
```

The desktop visual system, deterministic environment, and future neural intelligence remain distinct so later experiments can identify whether behavior came from the world, the renderer, or the agent.
