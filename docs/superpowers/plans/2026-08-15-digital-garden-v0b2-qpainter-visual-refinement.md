# Digital Garden V0-B.2 QPainter Visual Refinement Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Raise the current procedural Digital Garden renderer to a polished, dimensional, coherent QPainter illustration while preserving authoritative Garden state, deterministic identity, interaction masks, and the 97-test baseline.

**Architecture:** Keep `GardenRenderState` and the existing scene-model boundary unchanged. Add a small illustration-layer vocabulary around the current scene modules: directional lighting/depth, deterministic material breakup, richer bonsai and vine paint passes, and renderer-owned HUD treatment. Visual state remains derived from existing authoritative values through `scene_style`; no new Garden World state is introduced.

**Tech Stack:** Python 3.12, PySide6 / Qt 6, QWidget, QPainter, QImage/QRegion/QPainterPath, pytest 9, Ruff.

## Global Constraints

- Renderer remains PySide6 / QWidget / QPainter for this campaign.
- Garden World remains authoritative; rendering changes only presentation.
- No raster asset collage or generated art packs.
- No Qt Quick/QML, OpenGL/RHI, shader infrastructure, or new graphics engine.
- No new Garden World physics or unsupported weather/environment facts.
- No B.3 interaction actions and no B.4 animation campaign.
- No per-frame randomness; all decorative variation must remain deterministic and seed-stable.
- Geometry-derived window masks must continue to match prepared scene geometry.
- Canonical V0-A 240-tick output must remain unchanged.
- Every task uses TDD: RED first, focused GREEN, then broader regression checks.
- Final required automated gates: `uv run pytest -q`, `uv run ruff check .`, `uv run ruff format --check .`, `git diff --check`.

---

## File Map

### New focused module

- `src/digital_garden/desktop/scene/lighting.py` — pure directional-light/depth values shared by ground, bonsai, vines, and HUD paint passes.
- `tests/test_scene_lighting.py` — semantic tests for the light/depth contract.

### Existing scene modules to extend

- `src/digital_garden/desktop/scene/style.py` — expose the current authoritative style inputs needed by the visual passes without duplicating Garden rules.
- `src/digital_garden/desktop/scene/ground.py` — contact shadow, material mottling, edge depth, richer botanical layering.
- `src/digital_garden/desktop/scene/bonsai.py` — irregular canopy sub-lobes, trunk/branch depth, root grounding, layered highlights.
- `src/digital_garden/desktop/scene/vines.py` — layered stem/leaf values and visible leaves on edge vines while preserving exact mask derivation.
- `src/digital_garden/desktop/scene/renderer.py` — coherent pass ordering, static atmosphere, integrated HUD/collapse painting.
- `src/digital_garden/desktop/windows.py` — make the existing `QPushButton` an invisible hit target so the renderer owns the collapse visual.

### Existing/new tests to extend

- `tests/test_scene_ground.py`
- `tests/test_scene_bonsai.py`
- `tests/test_scene_vines.py`
- `tests/test_scene_renderer.py`
- `tests/test_scene_weather.py`
- `tests/test_desktop_windows.py`

---

### Task 1: Directional Light and Contact-Depth Foundation

**Files:**
- Create: `src/digital_garden/desktop/scene/lighting.py`
- Create: `tests/test_scene_lighting.py`
- Modify: `src/digital_garden/desktop/scene/ground.py`
- Modify: `src/digital_garden/desktop/scene/renderer.py`
- Test: `tests/test_scene_renderer.py`

**Interfaces:**
- Consumes: `SceneStyle` from `scene_style(state)`.
- Produces: `SceneLighting`, `scene_lighting(style) -> SceneLighting`, `paint_ground_shadow(painter, scene, lighting) -> None`.

- [ ] **Step 1: Write the failing light-contract test**

Create `tests/test_scene_lighting.py` with a representative `GardenRenderState` helper and assert that the light direction is stable while weather-derived style changes intensity rather than direction:

```python
from dataclasses import replace

from digital_garden.desktop.presentation import GardenRenderState
from digital_garden.desktop.scene.lighting import scene_lighting
from digital_garden.desktop.scene.style import scene_style


def _state() -> GardenRenderState:
    return GardenRenderState(
        seed=7,
        tick=12,
        weather="CLOUDY",
        light_level=0.55,
        humidity=0.60,
        soil_moisture=0.50,
        bonsai_health=0.50,
        bonsai_stress=0.20,
        bonsai_growth=0.40,
        canopy_density=0.60,
        ground_density=0.50,
        vine_extent=0.40,
        condition="HEALTHY",
        anchor_state="CALM",
    )


def test_scene_lighting_keeps_one_direction_but_weather_changes_strength() -> None:
    state = _state()
    sunny = scene_lighting(scene_style(replace(state, weather="SUNNY")))
    rainy = scene_lighting(scene_style(replace(state, weather="RAINY")))

    assert sunny.shadow_offset == rainy.shadow_offset
    assert sunny.highlight_offset == rainy.highlight_offset
    assert sunny.highlight_alpha > rainy.highlight_alpha
    assert rainy.shadow_alpha > sunny.shadow_alpha
```

- [ ] **Step 2: Run the test and verify RED**

Run:

```powershell
uv run pytest -q tests/test_scene_lighting.py
```

Expected: import failure because `scene.lighting` does not yet exist.

- [ ] **Step 3: Implement the minimal pure lighting contract**

Create `src/digital_garden/desktop/scene/lighting.py`:

```python
from dataclasses import dataclass

from PySide6.QtCore import QPointF

from digital_garden.desktop.scene.style import SceneStyle


@dataclass(frozen=True)
class SceneLighting:
    shadow_offset: QPointF
    highlight_offset: QPointF
    shadow_alpha: int
    highlight_alpha: int


def scene_lighting(style: SceneStyle) -> SceneLighting:
    brightness = max(0.0, min(1.0, style.ambient_brightness))
    coolness = max(0.0, min(1.0, style.atmosphere_coolness))
    return SceneLighting(
        shadow_offset=QPointF(7.0, 8.0),
        highlight_offset=QPointF(-3.0, -4.0),
        shadow_alpha=round(44 + coolness * 36 - brightness * 12),
        highlight_alpha=round(42 + brightness * 58 - coolness * 18),
    )
```

- [ ] **Step 4: Verify the pure contract is GREEN**

Run:

```powershell
uv run pytest -q tests/test_scene_lighting.py
```

Expected: PASS.

- [ ] **Step 5: Add a rendered-pixel RED for the ground contact shadow**

Extend `tests/test_scene_renderer.py` with an offscreen `QApplication`/`QImage` helper if one is not already present, then add:

```python
def test_patch_paints_contact_depth_below_ground() -> None:
    image = _paint_patch(_render_state())

    assert image.pixelColor(260, 403).alpha() > 0
```

The point is intentionally just below the current organic ground body but inside the future contact-shadow footprint.

- [ ] **Step 6: Run the focused renderer test and verify RED**

Run:

```powershell
uv run pytest -q tests/test_scene_renderer.py -k contact_depth
```

Expected: FAIL because the pixel remains transparent.

- [ ] **Step 7: Implement a soft deterministic contact shadow**

In `ground.py`, add:

```python
from digital_garden.desktop.scene.lighting import SceneLighting


def paint_ground_shadow(
    painter: QPainter,
    scene: GroundScene,
    lighting: SceneLighting,
) -> None:
    path = _outline_path(scene)
    painter.save()
    painter.translate(lighting.shadow_offset)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor(18, 25, 20, lighting.shadow_alpha))
    painter.drawPath(path)
    painter.restore()
```

In `renderer.paint_patch`, compute `lighting = scene_lighting(style)` once and call `paint_ground_shadow(...)` before `paint_ground(...)`.

- [ ] **Step 8: Verify Task 1**

Run:

```powershell
uv run pytest -q tests/test_scene_lighting.py tests/test_scene_renderer.py
uv run ruff check src/digital_garden/desktop/scene/lighting.py src/digital_garden/desktop/scene/ground.py src/digital_garden/desktop/scene/renderer.py tests/test_scene_lighting.py tests/test_scene_renderer.py
uv run ruff format --check src/digital_garden/desktop/scene/lighting.py src/digital_garden/desktop/scene/ground.py src/digital_garden/desktop/scene/renderer.py tests/test_scene_lighting.py tests/test_scene_renderer.py
git diff --check
```

Expected: all pass.

- [ ] **Step 9: Commit Task 1**

```powershell
git add src/digital_garden/desktop/scene/lighting.py src/digital_garden/desktop/scene/ground.py src/digital_garden/desktop/scene/renderer.py tests/test_scene_lighting.py tests/test_scene_renderer.py
git commit -m "feat(renderer): add directional light foundation"
```

---

### Task 2: Deterministic Ground Material and Edge Depth

**Files:**
- Modify: `src/digital_garden/desktop/scene/ground.py`
- Test: `tests/test_scene_ground.py`

**Interfaces:**
- Consumes: existing `candidate_pool`, `visible_candidates`, `stable_unit`, `SceneLighting`.
- Produces: `GroundMaterialMark` entries stored in `GroundScene.material_marks`; richer `paint_ground(...)` with seed-stable material breakup.

- [ ] **Step 1: Write the failing deterministic-material test**

Extend `tests/test_scene_ground.py`:

```python
def test_ground_material_marks_are_seed_stable_and_seed_specific() -> None:
    state = _render_state()
    style = scene_style(state)

    first = build_ground_scene(state, style)
    again = build_ground_scene(state, style)
    other = build_ground_scene(replace(state, seed=8), scene_style(replace(state, seed=8)))

    assert first.material_marks == again.material_marks
    assert first.material_marks != other.material_marks
    assert len(first.material_marks) >= 18
```

- [ ] **Step 2: Run RED**

```powershell
uv run pytest -q tests/test_scene_ground.py -k material_marks
```

Expected: FAIL because `GroundScene` has no `material_marks`.

- [ ] **Step 3: Add the prepared material-mark model**

In `ground.py` add:

```python
@dataclass(frozen=True)
class GroundMaterialMark:
    center_x: float
    center_y: float
    radius_x: float
    radius_y: float
    opacity: float


@dataclass(frozen=True)
class GroundScene:
    outline: tuple[GroundPoint, ...]
    material_marks: tuple[GroundMaterialMark, ...]
    clover: tuple[GroundDetail, ...]
    flowers: tuple[GroundDetail, ...]
    grass: tuple[GroundDetail, ...]
    moss: tuple[GroundDetail, ...]
    stones: tuple[GroundDetail, ...]
```

Build `material_marks` from a stable pool of 32 sites mapped through `_ground_detail(...)`. Keep their visibility independent of state so the material identity does not pop in/out; use `stable_unit` for radius and opacity.

Example builder:

```python
def _material_marks(state: GardenRenderState) -> tuple[GroundMaterialMark, ...]:
    candidates = candidate_pool(state.seed, "ground-material", 32)
    return tuple(
        GroundMaterialMark(
            center_x=_ground_detail(candidate.x, candidate.y, candidate.scale).center_x,
            center_y=_ground_detail(candidate.x, candidate.y, candidate.scale).center_y,
            radius_x=6.0 + candidate.scale * 10.0,
            radius_y=2.5 + candidate.scale * 5.0,
            opacity=0.08 + stable_unit(state.seed, "ground-material-alpha", index) * 0.12,
        )
        for index, candidate in enumerate(candidates)
    )
```

- [ ] **Step 4: Verify model GREEN**

```powershell
uv run pytest -q tests/test_scene_ground.py -k material_marks
```

Expected: PASS.

- [ ] **Step 5: Add a rendered RED for tonal breakup**

Add a ground-painter test using `QImage` and assert two known interior points no longer collapse to the same flat tone under a fixed state:

```python
def test_ground_material_breakup_produces_more_than_one_interior_tone() -> None:
    image = _paint_ground(_render_state())

    assert image.pixelColor(220, 345) != image.pixelColor(300, 345)
```

- [ ] **Step 6: Run RED**

```powershell
uv run pytest -q tests/test_scene_ground.py -k interior_tone
```

Expected: FAIL while the surface remains effectively uniform at those points.

- [ ] **Step 7: Paint material marks and edge depth inside the existing clip**

Inside `paint_ground(...)`, after the base soil/moss layers and before botanical details:

```python
for index, mark in enumerate(scene.material_marks):
    painter.setOpacity(mark.opacity)
    painter.setBrush(
        _darkened(style.palette.moss, 0.18)
        if index % 2
        else _darkened(style.palette.soil, 0.10)
    )
    painter.drawEllipse(
        QRectF(
            mark.center_x - mark.radius_x,
            mark.center_y - mark.radius_y,
            mark.radius_x * 2.0,
            mark.radius_y * 2.0,
        )
    )

painter.setOpacity(1.0)
```

Add one restrained lower-edge depth pass by drawing the same ground path translated down 2–3 px with low alpha before restoring the clip, ensuring the visual remains inside the existing mask envelope.

- [ ] **Step 8: Verify Task 2**

```powershell
uv run pytest -q tests/test_scene_ground.py tests/test_scene_renderer.py
uv run ruff check src/digital_garden/desktop/scene/ground.py tests/test_scene_ground.py
uv run ruff format --check src/digital_garden/desktop/scene/ground.py tests/test_scene_ground.py
git diff --check
```

Expected: all pass.

- [ ] **Step 9: Commit Task 2**

```powershell
git add src/digital_garden/desktop/scene/ground.py tests/test_scene_ground.py
git commit -m "feat(renderer): refine ground material depth"
```

---

### Task 3: Bonsai Canopy, Trunk, and Root Depth

**Files:**
- Modify: `src/digital_garden/desktop/scene/bonsai.py`
- Modify: `src/digital_garden/desktop/scene/renderer.py`
- Test: `tests/test_scene_bonsai.py`

**Interfaces:**
- Consumes: `SceneLighting`, `stable_unit`, existing `BonsaiScene`/`CanopyCluster`.
- Produces: `CanopyLobe`, `CanopyCluster.lobes`, enhanced `paint_bonsai(painter, scene, style, lighting)`.

- [ ] **Step 1: Write the failing canopy-lobe model test**

Extend `tests/test_scene_bonsai.py`:

```python
def test_canopy_clusters_have_seed_stable_irregular_lobes() -> None:
    state = _render_state()
    style = scene_style(state)

    scene = build_bonsai_scene(state, style)
    again = build_bonsai_scene(state, style)

    assert scene.canopy == again.canopy
    assert all(len(cluster.lobes) >= 4 for cluster in scene.canopy)
    assert any(
        lobe.offset_x != 0.0 or lobe.offset_y != 0.0
        for cluster in scene.canopy
        for lobe in cluster.lobes
    )
```

- [ ] **Step 2: Run RED**

```powershell
uv run pytest -q tests/test_scene_bonsai.py -k irregular_lobes
```

Expected: FAIL because `CanopyCluster` has no `lobes`.

- [ ] **Step 3: Add deterministic lobe geometry**

In `bonsai.py`:

```python
@dataclass(frozen=True)
class CanopyLobe:
    offset_x: float
    offset_y: float
    scale_x: float
    scale_y: float


@dataclass(frozen=True)
class CanopyCluster:
    center_x: float
    center_y: float
    radius_x: float
    radius_y: float
    rotation: float
    lobes: tuple[CanopyLobe, ...]
```

Create 5 lobes per visible cluster from stable seed/object IDs. Keep every lobe inside the parent ellipse envelope closely enough that `_cluster_region` remains a conservative valid interaction mask.

Example:

```python
def _cluster_lobes(seed: int, index: int) -> tuple[CanopyLobe, ...]:
    return tuple(
        CanopyLobe(
            offset_x=(stable_unit(seed, f"canopy-lobe-x-{index}", lobe) - 0.5) * 0.52,
            offset_y=(stable_unit(seed, f"canopy-lobe-y-{index}", lobe) - 0.5) * 0.44,
            scale_x=0.42 + stable_unit(seed, f"canopy-lobe-sx-{index}", lobe) * 0.22,
            scale_y=0.40 + stable_unit(seed, f"canopy-lobe-sy-{index}", lobe) * 0.20,
        )
        for lobe in range(5)
    )
```

- [ ] **Step 4: Verify lobe model GREEN**

```powershell
uv run pytest -q tests/test_scene_bonsai.py -k irregular_lobes
```

Expected: PASS.

- [ ] **Step 5: Add a painter RED proving directional depth exists**

Add an offscreen painter test that compares a shadow-side canopy pixel with a highlight-side canopy pixel under the same fixed state:

```python
def test_bonsai_canopy_has_directional_value_separation() -> None:
    image = _paint_bonsai(_render_state())

    assert image.pixelColor(248, 160) != image.pixelColor(270, 145)
```

- [ ] **Step 6: Run RED**

```powershell
uv run pytest -q tests/test_scene_bonsai.py -k directional_value
```

Expected: FAIL or demonstrate insufficient separation before the new lobe/depth pass.

- [ ] **Step 7: Refine `paint_bonsai` into layered passes**

Change signature:

```python
def paint_bonsai(
    painter: QPainter,
    scene: BonsaiScene,
    style: SceneStyle,
    lighting: SceneLighting,
) -> None:
```

Implement in this order:

1. low-alpha root/trunk contact shadow translated by `lighting.shadow_offset * 0.35`;
2. root and branch dark structural strokes;
3. trunk base stroke;
4. thinner trunk highlight stroke translated toward `lighting.highlight_offset` rather than centered on the trunk;
5. each canopy parent shadow mass;
6. each deterministic lobe in main foliage color;
7. 2–3 upper-left lobes per cluster in highlight color at `lighting.highlight_alpha`.

Do not change branch geometry or authoritative state mapping in this task.

- [ ] **Step 8: Update renderer call and verify Task 3**

In `renderer.paint_patch`, pass the shared `lighting` value into `paint_bonsai`.

Run:

```powershell
uv run pytest -q tests/test_scene_bonsai.py tests/test_scene_renderer.py
uv run ruff check src/digital_garden/desktop/scene/bonsai.py src/digital_garden/desktop/scene/renderer.py tests/test_scene_bonsai.py
uv run ruff format --check src/digital_garden/desktop/scene/bonsai.py src/digital_garden/desktop/scene/renderer.py tests/test_scene_bonsai.py
git diff --check
```

Expected: all pass.

- [ ] **Step 9: Commit Task 3**

```powershell
git add src/digital_garden/desktop/scene/bonsai.py src/digital_garden/desktop/scene/renderer.py tests/test_scene_bonsai.py
git commit -m "feat(renderer): deepen procedural bonsai"
```

---

### Task 4: Edge Vine and Anchor Value Refinement

**Files:**
- Modify: `src/digital_garden/desktop/scene/vines.py`
- Modify: `src/digital_garden/desktop/scene/renderer.py`
- Test: `tests/test_scene_vines.py`

**Interfaces:**
- Consumes: `SceneLighting`, existing `VineStem`, `VineLeaf`, `EdgeVineScene`, `AnchorVineScene`.
- Produces: `EdgeVineScene.leaves`; enhanced `paint_edge_vines(..., lighting)` and `paint_anchor_vine(..., lighting)`.

- [ ] **Step 1: Write a failing edge-leaf contract test**

Extend `tests/test_scene_vines.py`:

```python
def test_edge_vines_gain_seed_stable_leaves_as_extent_grows() -> None:
    state = _render_state()
    style = scene_style(state)

    low = build_edge_vine_scene(replace(state, vine_extent=0.15), style)
    high = build_edge_vine_scene(replace(state, vine_extent=0.90), style)
    high_again = build_edge_vine_scene(replace(state, vine_extent=0.90), style)

    assert high == high_again
    assert len(high.leaves) > len(low.leaves)
```

- [ ] **Step 2: Run RED**

```powershell
uv run pytest -q tests/test_scene_vines.py -k edge_vines_gain
```

Expected: FAIL because `EdgeVineScene` has no `leaves`.

- [ ] **Step 3: Add deterministic edge leaves and include them in masks**

Update:

```python
@dataclass(frozen=True)
class EdgeVineScene:
    stems: tuple[VineStem, ...]
    leaves: tuple[VineLeaf, ...]
```

Generate 1–2 leaves per visible stem using stable unit values and `vine_extent` visibility thresholds. Then update `edge_vine_mask_region`:

```python
for leaf in scene.leaves:
    region = region.united(_leaf_region(leaf))
```

This keeps visible geometry and interaction geometry aligned.

- [ ] **Step 4: Verify geometry/mask GREEN**

```powershell
uv run pytest -q tests/test_scene_vines.py -k "edge_vines_gain or masks"
```

Expected: PASS.

- [ ] **Step 5: Add a visual RED for layered anchor leaves**

Add an offscreen anchor paint test asserting that an upper-left portion of a known leaf differs from its lower-right portion under a healthy/calm state.

- [ ] **Step 6: Run RED**

```powershell
uv run pytest -q tests/test_scene_vines.py -k layered_anchor
```

Expected: FAIL while each leaf is a single flat fill.

- [ ] **Step 7: Add stem shadow/highlight and leaf value passes**

Change painter signatures to accept `SceneLighting`. For each stem, draw a slightly wider low-alpha shadow stroke first, then the main vine stroke. For leaves, draw the base leaf then a clipped/translated smaller highlight path using `style.palette.foliage_highlight` and `lighting.highlight_alpha`.

Do not add animation or per-frame variation.

- [ ] **Step 8: Verify Task 4**

```powershell
uv run pytest -q tests/test_scene_vines.py tests/test_scene_renderer.py tests/test_desktop_windows.py
uv run ruff check src/digital_garden/desktop/scene/vines.py src/digital_garden/desktop/scene/renderer.py tests/test_scene_vines.py
uv run ruff format --check src/digital_garden/desktop/scene/vines.py src/digital_garden/desktop/scene/renderer.py tests/test_scene_vines.py
git diff --check
```

Expected: all pass, including geometry-mask/window contract tests.

- [ ] **Step 9: Commit Task 4**

```powershell
git add src/digital_garden/desktop/scene/vines.py src/digital_garden/desktop/scene/renderer.py tests/test_scene_vines.py
git commit -m "feat(renderer): refine living vines"
```

---

### Task 5: Integrated HUD and Renderer-Owned Collapse Affordance

**Files:**
- Modify: `src/digital_garden/desktop/scene/renderer.py`
- Modify: `src/digital_garden/desktop/windows.py`
- Modify: `src/digital_garden/desktop/scene/style.py`
- Test: `tests/test_scene_renderer.py`
- Test: `tests/test_desktop_windows.py`

**Interfaces:**
- Consumes: `PATCH_LABEL_RECT`, `PATCH_COLLAPSE_RECT`, authoritative `condition` and `weather`, `SceneStyle` palette.
- Produces: renderer-painted HUD and collapse affordance; transparent `QPushButton` retained only as an interaction hit target.

- [ ] **Step 1: Write a failing window-contract test for the invisible collapse hit target**

Extend `tests/test_desktop_windows.py`:

```python
def test_collapse_button_is_only_an_invisible_hit_target() -> None:
    app = QApplication.instance() or QApplication([])
    patch = GardenPatchWindow(_controller(), QPainterShellRenderer())

    button = patch._collapse_button
    assert button.text() == ""
    assert button.isFlat()
    assert "background: transparent" in button.styleSheet()

    patch.close()
    app.processEvents()
```

- [ ] **Step 2: Run RED**

```powershell
uv run pytest -q tests/test_desktop_windows.py -k invisible_hit_target
```

Expected: FAIL because the button currently paints the stock `COLLAPSE` widget.

- [ ] **Step 3: Convert the button to a transparent hit target**

In `windows.py`:

```python
self._collapse_button = QPushButton("", self)
self._collapse_button.setFlat(True)
self._collapse_button.setStyleSheet("background: transparent; border: none;")
self._collapse_button.setGeometry(PATCH_COLLAPSE_RECT)
self._collapse_button.clicked.connect(self.collapse_requested.emit)
```

- [ ] **Step 4: Verify hit-target GREEN and preserved interaction**

```powershell
uv run pytest -q tests/test_desktop_windows.py
```

Expected: PASS.

- [ ] **Step 5: Add a rendered RED for integrated HUD backing**

Extend `tests/test_scene_renderer.py` to assert that the label backing has transparency and that the collapse rectangle is now visibly painted by the renderer:

```python
def test_renderer_owns_soft_hud_and_collapse_visuals() -> None:
    image = _paint_patch(_render_state())

    hud = image.pixelColor(24, 24)
    collapse = image.pixelColor(PATCH_COLLAPSE_RECT.center())

    assert 0 < hud.alpha() < 255
    assert collapse.alpha() > 0
```

- [ ] **Step 6: Run RED**

```powershell
uv run pytest -q tests/test_scene_renderer.py -k soft_hud
```

Expected: FAIL for the collapse pixel and/or current opaque-looking rectangular treatment.

- [ ] **Step 7: Paint a softer HUD and botanical collapse affordance**

In `style.py`, retain `overlay_backing`/`overlay_text` but reduce rectangular dominance through alpha only; do not invent state fields.

In `renderer.paint_patch`:

1. replace the hard-coded `QColor(23, 52, 33, 220)` with `style.palette.overlay_backing`;
2. use two overlapping rounded translucent shapes or a slightly inset secondary shape so the panel edge is softer without textures;
3. keep Qt text crisp and authoritative: only `CONDITION: {state.condition}` and `WEATHER: {state.weather}`;
4. paint `PATCH_COLLAPSE_RECT` as a small moss/soil-toned rounded tab with real Qt text `COLLAPSE` centered inside it;
5. optionally add one deterministic short vine stroke toward the tab only if it reuses existing prepared edge-vine geometry rather than inventing a new stateful object.

- [ ] **Step 8: Verify Task 5**

```powershell
uv run pytest -q tests/test_scene_renderer.py tests/test_desktop_windows.py
uv run ruff check src/digital_garden/desktop/scene/renderer.py src/digital_garden/desktop/windows.py src/digital_garden/desktop/scene/style.py tests/test_scene_renderer.py tests/test_desktop_windows.py
uv run ruff format --check src/digital_garden/desktop/scene/renderer.py src/digital_garden/desktop/windows.py src/digital_garden/desktop/scene/style.py tests/test_scene_renderer.py tests/test_desktop_windows.py
git diff --check
```

Expected: all pass.

- [ ] **Step 9: Commit Task 5**

```powershell
git add src/digital_garden/desktop/scene/renderer.py src/digital_garden/desktop/windows.py src/digital_garden/desktop/scene/style.py tests/test_scene_renderer.py tests/test_desktop_windows.py
git commit -m "feat(renderer): integrate garden HUD controls"
```

---

### Task 6: Whole-Scene Static Weather Polish

**Files:**
- Modify: `src/digital_garden/desktop/scene/renderer.py`
- Modify: `src/digital_garden/desktop/scene/style.py`
- Test: `tests/test_scene_weather.py`

**Interfaces:**
- Consumes: existing authoritative `weather`, `light_level`, `humidity`, `soil_moisture`; `SceneStyle.palette.ambient`; `SceneLighting`.
- Produces: a restrained whole-scene atmosphere pass applied after botanical paint but before HUD text.

- [ ] **Step 1: Add a RED proving weather changes the composition above the ground**

Extend `tests/test_scene_weather.py`:

```python
def test_weather_changes_static_canopy_atmosphere() -> None:
    state = _render_state()
    sunny = _paint_patch(replace(state, weather="SUNNY"))
    rainy = _paint_patch(replace(state, weather="RAINY"))

    assert sunny.pixelColor(280, 150) != rainy.pixelColor(280, 150)
```

The point is within the bonsai canopy, so this test proves weather treatment is no longer ground-only.

- [ ] **Step 2: Run RED**

```powershell
uv run pytest -q tests/test_scene_weather.py -k canopy_atmosphere
```

Expected: FAIL if weather currently affects only ground/static palette insufficiently at that point.

- [ ] **Step 3: Implement a clipped whole-scene atmosphere pass**

In `renderer.paint_patch`, after ground/vines/bonsai and before HUD, draw one low-alpha translucent wash over the union of `ground_mask_region`, `edge_vine_mask_region`, and `bonsai_mask_region` rather than the full 520x420 rectangle.

Use only `style.palette.ambient`; do not add temperature/wind labels or new simulation state.

Concept:

```python
scene_region = ground_mask_region(ground)
scene_region = scene_region.united(edge_vine_mask_region(edge_vines))
scene_region = scene_region.united(bonsai_mask_region(bonsai))

painter.save()
painter.setClipRegion(scene_region)
painter.setPen(Qt.PenStyle.NoPen)
painter.setBrush(_qcolor(style.palette.ambient))
painter.drawRect(QRect(0, 0, PATCH_SIZE.width(), PATCH_SIZE.height()))
painter.restore()
```

If renderer cannot use ground's private `_qcolor`, add a tiny renderer-local `QColor` conversion instead of exporting unrelated helpers.

- [ ] **Step 4: Verify Task 6**

```powershell
uv run pytest -q tests/test_scene_weather.py tests/test_scene_renderer.py tests/test_scene_ground.py tests/test_scene_bonsai.py tests/test_scene_vines.py
uv run ruff check src/digital_garden/desktop/scene/renderer.py src/digital_garden/desktop/scene/style.py tests/test_scene_weather.py
uv run ruff format --check src/digital_garden/desktop/scene/renderer.py src/digital_garden/desktop/scene/style.py tests/test_scene_weather.py
git diff --check
```

Expected: all pass.

- [ ] **Step 5: Commit Task 6**

```powershell
git add src/digital_garden/desktop/scene/renderer.py src/digital_garden/desktop/scene/style.py tests/test_scene_weather.py
git commit -m "feat(renderer): polish static weather atmosphere"
```

---

### Task 7: Visual-Quality Regression Gate and Supersampling Decision

**Files:**
- Modify only if evidence justifies it: `src/digital_garden/desktop/scene/renderer.py`
- Test only if implemented: `tests/test_scene_renderer.py`

**Interfaces:**
- Consumes: complete refined scene from Tasks 1–6.
- Produces: either a documented decision to keep direct rendering, or a bounded 2x offscreen render/downsample path if aliasing is visibly unacceptable and performance remains acceptable.

- [ ] **Step 1: Run the production renderer manually before adding any supersampling code**

```powershell
uv run digital-garden-desktop
```

Capture/inspect both collapsed anchor and expanded patch at native Windows scaling.

- [ ] **Step 2: Apply the evidence gate**

Choose **direct rendering** if curves, small leaves, grass, and text edges are already acceptably smooth at production size. Choose **2x supersampling experiment** only if visible aliasing materially harms the result.

Do not implement supersampling merely because it was listed in the design.

- [ ] **Step 3A: If direct rendering is accepted, make no renderer change**

Record the decision in the final task/closeout notes and proceed to Task 8.

- [ ] **Step 3B: If supersampling is justified, first add a failing semantic test**

Add a test around a small pure helper rather than snapshotting an entire image:

```python
def test_supersampled_size_is_exactly_double_patch_size() -> None:
    renderer = QPainterShellRenderer()
    assert renderer.supersampled_patch_size() == QSize(PATCH_SIZE.width() * 2, PATCH_SIZE.height() * 2)
```

- [ ] **Step 4B: Implement only a 2x offscreen path**

Render botanical layers to `QImage(PATCH_SIZE * 2, Format_ARGB32_Premultiplied)`, scale the painter by `2.0`, then draw the image back to the window using `Qt.TransformationMode.SmoothTransformation`. Keep UI text at native resolution if 2x text downsampling reduces clarity.

Do not generalize to arbitrary scales or caching in V0-B.2.

- [ ] **Step 5: Verify Task 7 if code changed**

```powershell
uv run pytest -q tests/test_scene_renderer.py
uv run ruff check src/digital_garden/desktop/scene/renderer.py tests/test_scene_renderer.py
uv run ruff format --check src/digital_garden/desktop/scene/renderer.py tests/test_scene_renderer.py
git diff --check
```

- [ ] **Step 6: Commit only if Task 7 changed code**

```powershell
git add src/digital_garden/desktop/scene/renderer.py tests/test_scene_renderer.py
git commit -m "perf(renderer): add bounded supersampling"
```

---

### Task 8: Full Acceptance, Canonical Baseline, and V0-B.2 Visual Seal

**Files:**
- No production code unless a failure is discovered.
- Update project closeout/plan notes only after all gates pass if the repository already maintains such a record for V0-B.2.

**Interfaces:**
- Consumes: final refined continuation branch.
- Produces: verified V0-B.2 QPainter visual baseline ready for integration/review.

- [ ] **Step 1: Run full automated tests**

```powershell
uv run pytest -q
```

Expected: all tests pass; baseline count must be at least 97 plus tests added by this campaign.

- [ ] **Step 2: Run lint/format/whitespace gates**

```powershell
uv run ruff check .
uv run ruff format --check .
git diff --check
```

Expected: all clean.

- [ ] **Step 3: Re-run the canonical V0-A 240-tick acceptance command already used by the repository**

Expected exact authoritative values remain:

```json
{"anchor_state":"DRY","bonsai_health":0.44449999999999634,"bonsai_stress":1.0,"condition":"STRUGGLING","day_index":10,"hour_of_day":0,"observation_length":12,"overgrowth":0.29088800000001,"seed":7,"soil_moisture":0.13199999999999923,"tick":240,"weather":"CLOUDY"}
```

Whitespace in JSON output may differ; values must not.

- [ ] **Step 4: Verify repository state**

```powershell
git branch --show-current
git rev-parse HEAD
git status --short
```

Expected branch: `build/digital-garden-v0b2-byte-continuation`; status clean after all intended commits.

- [ ] **Step 5: Run Windows manual visual acceptance**

```powershell
uv run digital-garden-desktop
```

Accept only if all are true:

- ground visibly has contact depth and tonal material breakup;
- bonsai canopy is irregular and richer without visual noise;
- trunk/root/foliage share one implied light direction;
- anchor and edge vines remain coherent with the patch;
- HUD reads as integrated rather than a stock green panel;
- collapse interaction still works while the stock button is no longer visually dominant;
- SUNNY/CLOUDY/RAINY visual moods are distinguishable but restrained;
- interaction masks still feel correct on transparent regions;
- dragging, expansion, collapse, and outside dismissal remain correct;
- no unsupported temperature/wind/environment claims appear;
- performance remains smooth at production size.

- [ ] **Step 6: Final commit only if closeout documentation changed**

```powershell
git add docs/
git commit -m "docs(renderer): seal V0-B.2 visual refinement"
```

Do not create an empty commit.
