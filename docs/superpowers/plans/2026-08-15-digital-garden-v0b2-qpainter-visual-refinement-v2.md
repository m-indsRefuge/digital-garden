# Digital Garden V0-B.2 QPainter Visual Refinement Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Raise the current procedural Digital Garden renderer to a polished, dimensional, coherent QPainter illustration while preserving authoritative Garden state, deterministic identity, interaction masks, and the 97-test baseline.

**Architecture:** Keep `GardenRenderState` and the current scene-model boundary unchanged. Add one shared directional-light contract, then refine ground, bonsai, vines, HUD, and static atmosphere as independent deterministic passes. Any newly visible geometry outside an existing mask must add its own mask region and be unioned into the production window mask.

**Tech Stack:** Python 3.12, PySide6 / Qt 6, QWidget, QPainter, QImage, QPainterPath, QRegion, pytest 9, Ruff.

## Global Constraints

- Renderer remains PySide6 / QWidget / QPainter.
- Garden World remains authoritative; renderer changes presentation only.
- No raster asset collage, generated art packs, Qt Quick/QML, OpenGL/RHI, shaders, or new graphics engine.
- No new Garden World physics or unsupported temperature/wind/environment values.
- No B.3 interaction actions and no B.4 animation campaign.
- No per-frame randomness; decorative variation stays seed-stable.
- Geometry-derived window masks must include every visible geometry pass that extends beyond the previous shape.
- Canonical V0-A 240-tick output must remain unchanged.
- Every behavior follows RED -> minimal GREEN -> focused regression -> commit.

## File Map

- Create `src/digital_garden/desktop/scene/lighting.py`: shared pure light/depth values.
- Create `tests/test_scene_lighting.py`: semantic lighting tests.
- Extend `scene/ground.py`: contact shadow, shadow mask, material breakup, edge depth.
- Extend `scene/bonsai.py`: irregular foliage lobes and structural depth.
- Extend `scene/vines.py`: edge leaves and layered value treatment.
- Extend `scene/renderer.py`: pass ordering, mask unions, HUD/collapse visuals, whole-scene atmosphere.
- Extend `scene/style.py`: only palette/alpha values already derived from authoritative state.
- Extend `desktop/windows.py`: keep collapse `QPushButton` as an invisible hit target.
- Extend `tests/test_scene_ground.py`, `test_scene_bonsai.py`, `test_scene_vines.py`, `test_scene_renderer.py`, `test_scene_weather.py`, `test_desktop_windows.py`.

---

### Task 1: Directional Light and Mask-Safe Contact Depth

**Files:**
- Create: `src/digital_garden/desktop/scene/lighting.py`
- Create: `tests/test_scene_lighting.py`
- Modify: `src/digital_garden/desktop/scene/ground.py`
- Modify: `src/digital_garden/desktop/scene/renderer.py`
- Test: `tests/test_scene_renderer.py`

**Interfaces:**
- Produces `SceneLighting` and `scene_lighting(style: SceneStyle) -> SceneLighting`.
- Produces `paint_ground_shadow(painter, scene, lighting) -> None`.
- Produces `ground_shadow_mask_region(scene, lighting) -> QRegion` from exactly the same translated path used for painting.

- [ ] **Step 1: Write RED for the pure light contract**

Create `tests/test_scene_lighting.py`:

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

Run:

```powershell
uv run pytest -q tests/test_scene_lighting.py
```

Expected: import failure because `scene.lighting` does not exist.

- [ ] **Step 2: Implement minimal lighting contract**

Create `scene/lighting.py`:

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

Run `uv run pytest -q tests/test_scene_lighting.py`; expected PASS.

- [ ] **Step 3: Write RED for contact shadow and mask coupling**

In `tests/test_scene_renderer.py`, add a local `_paint_patch` helper using `QApplication`, `QImage(520, 420, Format_ARGB32_Premultiplied)`, and `QPainterShellRenderer().paint_patch(...)`, then add:

```python
def test_patch_contact_shadow_is_visible_and_inside_window_mask() -> None:
    state = _render_state()
    image = _paint_patch(state)
    mask = QPainterShellRenderer().patch_mask(state)
    point = QPoint(260, 403)

    assert image.pixelColor(point).alpha() > 0
    assert mask.contains(point)
```

Run:

```powershell
uv run pytest -q tests/test_scene_renderer.py -k contact_shadow
```

Expected: FAIL because no translated ground shadow exists.

- [ ] **Step 4: Implement painted shadow and exact shadow region**

In `ground.py`:

```python
from digital_garden.desktop.scene.lighting import SceneLighting


def _translated_outline_path(scene: GroundScene, lighting: SceneLighting) -> QPainterPath:
    path = _outline_path(scene)
    translated = QPainterPath(path)
    translated.translate(lighting.shadow_offset.x(), lighting.shadow_offset.y())
    return translated


def ground_shadow_mask_region(scene: GroundScene, lighting: SceneLighting) -> QRegion:
    return QRegion(_translated_outline_path(scene, lighting).toFillPolygon().toPolygon())


def paint_ground_shadow(
    painter: QPainter,
    scene: GroundScene,
    lighting: SceneLighting,
) -> None:
    painter.save()
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QColor(18, 25, 20, lighting.shadow_alpha))
    painter.drawPath(_translated_outline_path(scene, lighting))
    painter.restore()
```

In `renderer.patch_mask`, compute `lighting = scene_lighting(style)` and union `ground_shadow_mask_region(ground, lighting)`. In `paint_patch`, compute the same lighting and call `paint_ground_shadow` before `paint_ground`.

- [ ] **Step 5: Verify and commit Task 1**

```powershell
uv run pytest -q tests/test_scene_lighting.py tests/test_scene_renderer.py
uv run ruff check src/digital_garden/desktop/scene/lighting.py src/digital_garden/desktop/scene/ground.py src/digital_garden/desktop/scene/renderer.py tests/test_scene_lighting.py tests/test_scene_renderer.py
uv run ruff format --check src/digital_garden/desktop/scene/lighting.py src/digital_garden/desktop/scene/ground.py src/digital_garden/desktop/scene/renderer.py tests/test_scene_lighting.py tests/test_scene_renderer.py
git diff --check
git add src/digital_garden/desktop/scene/lighting.py src/digital_garden/desktop/scene/ground.py src/digital_garden/desktop/scene/renderer.py tests/test_scene_lighting.py tests/test_scene_renderer.py
git commit -m "feat(renderer): add directional light foundation"
```

---

### Task 2: Deterministic Ground Material Breakup

**Files:**
- Modify: `src/digital_garden/desktop/scene/ground.py`
- Test: `tests/test_scene_ground.py`

**Interfaces:**
- Adds `GroundMaterialMark` and `GroundScene.material_marks`.
- Reuses `candidate_pool`, `stable_unit`, current ground clip, current state-derived palette.

- [ ] **Step 1: Write model RED**

```python
def test_ground_material_marks_are_seed_stable_and_seed_specific() -> None:
    state = _render_state()
    first = build_ground_scene(state, scene_style(state))
    again = build_ground_scene(state, scene_style(state))
    other_state = replace(state, seed=8)
    other = build_ground_scene(other_state, scene_style(other_state))

    assert first.material_marks == again.material_marks
    assert first.material_marks != other.material_marks
    assert len(first.material_marks) == 32
```

Run `uv run pytest -q tests/test_scene_ground.py -k material_marks`; expected attribute failure.

- [ ] **Step 2: Implement stable material sites**

```python
@dataclass(frozen=True)
class GroundMaterialMark:
    center_x: float
    center_y: float
    radius_x: float
    radius_y: float
    opacity: float
```

Add `material_marks: tuple[GroundMaterialMark, ...]` to `GroundScene` and build exactly 32 marks from `candidate_pool(state.seed, "ground-material", 32)`. Map each candidate through `_ground_detail`; derive opacity from `stable_unit(state.seed, "ground-material-alpha", index)`.

- [ ] **Step 3: Write painter RED and implement tonal breakup**

Add a helper that paints only the prepared ground to a transparent QImage. Add:

```python
def test_ground_material_breakup_produces_multiple_interior_values() -> None:
    image = _paint_ground(_render_state())
    colors = {
        image.pixelColor(220, 345).rgba(),
        image.pixelColor(260, 345).rgba(),
        image.pixelColor(300, 345).rgba(),
    }
    assert len(colors) >= 2
```

Run RED. Then, inside the existing ground clip, paint alternating low-opacity darkened moss/soil ellipses for `scene.material_marks` before botanical details. Reset opacity to `1.0` before drawing grass/clover/flowers.

- [ ] **Step 4: Verify and commit Task 2**

```powershell
uv run pytest -q tests/test_scene_ground.py tests/test_scene_renderer.py
uv run ruff check src/digital_garden/desktop/scene/ground.py tests/test_scene_ground.py
uv run ruff format --check src/digital_garden/desktop/scene/ground.py tests/test_scene_ground.py
git diff --check
git add src/digital_garden/desktop/scene/ground.py tests/test_scene_ground.py
git commit -m "feat(renderer): refine ground material depth"
```

---

### Task 3: Irregular Bonsai Canopy and Structural Depth

**Files:**
- Modify: `src/digital_garden/desktop/scene/bonsai.py`
- Modify: `src/digital_garden/desktop/scene/renderer.py`
- Test: `tests/test_scene_bonsai.py`

**Interfaces:**
- Adds `CanopyLobe` and `CanopyCluster.lobes`.
- Changes painter signature to `paint_bonsai(painter, scene, style, lighting)`.

- [ ] **Step 1: Write canopy RED**

```python
def test_canopy_clusters_have_seed_stable_irregular_lobes() -> None:
    state = _render_state()
    scene = build_bonsai_scene(state, scene_style(state))
    again = build_bonsai_scene(state, scene_style(state))

    assert scene.canopy == again.canopy
    assert all(len(cluster.lobes) == 5 for cluster in scene.canopy)
    assert any(
        lobe.offset_x != 0.0 or lobe.offset_y != 0.0
        for cluster in scene.canopy
        for lobe in cluster.lobes
    )
```

Run `uv run pytest -q tests/test_scene_bonsai.py -k irregular_lobes`; expected attribute failure.

- [ ] **Step 2: Implement deterministic lobe geometry**

```python
@dataclass(frozen=True)
class CanopyLobe:
    offset_x: float
    offset_y: float
    scale_x: float
    scale_y: float
```

Add `lobes` to `CanopyCluster`. Build five lobes per cluster from stable IDs such as `canopy-lobe-x-{cluster_index}`. Constrain offsets/scales so every lobe remains inside the parent cluster envelope; keep `_cluster_region` as the conservative mask.

- [ ] **Step 3: Write painter RED and implement layered depth**

Add an offscreen bonsai helper and a semantic test comparing two interior canopy values under the same state. Then change `paint_bonsai` to accept `SceneLighting` and paint in this order: translated low-alpha root/trunk shadow; structural root/branch strokes; trunk base; offset thin trunk highlight; parent foliage shadow mass; five main foliage lobes; restrained upper-left highlight lobes using `lighting.highlight_alpha`.

Update `renderer.paint_patch` to pass the shared lighting value.

- [ ] **Step 4: Verify and commit Task 3**

```powershell
uv run pytest -q tests/test_scene_bonsai.py tests/test_scene_renderer.py
uv run ruff check src/digital_garden/desktop/scene/bonsai.py src/digital_garden/desktop/scene/renderer.py tests/test_scene_bonsai.py
uv run ruff format --check src/digital_garden/desktop/scene/bonsai.py src/digital_garden/desktop/scene/renderer.py tests/test_scene_bonsai.py
git diff --check
git add src/digital_garden/desktop/scene/bonsai.py src/digital_garden/desktop/scene/renderer.py tests/test_scene_bonsai.py
git commit -m "feat(renderer): deepen procedural bonsai"
```

---

### Task 4: Edge Leaves and Layered Vine Values

**Files:**
- Modify: `src/digital_garden/desktop/scene/vines.py`
- Modify: `src/digital_garden/desktop/scene/renderer.py`
- Test: `tests/test_scene_vines.py`

**Interfaces:**
- Adds `EdgeVineScene.leaves`.
- Edge-vine mask unions the exact prepared leaf paths.
- Changes both vine painters to accept `SceneLighting`.

- [ ] **Step 1: Write edge-leaf RED**

```python
def test_edge_vines_gain_seed_stable_leaves_as_extent_grows() -> None:
    state = _render_state()
    low_state = replace(state, vine_extent=0.15)
    high_state = replace(state, vine_extent=0.90)

    low = build_edge_vine_scene(low_state, scene_style(low_state))
    high = build_edge_vine_scene(high_state, scene_style(high_state))
    high_again = build_edge_vine_scene(high_state, scene_style(high_state))

    assert high == high_again
    assert len(high.leaves) > len(low.leaves)
```

Run `uv run pytest -q tests/test_scene_vines.py -k edge_vines_gain`; expected attribute failure.

- [ ] **Step 2: Implement deterministic edge leaves and exact mask union**

Add `leaves: tuple[VineLeaf, ...]` to `EdgeVineScene`. Generate leaf sites from visible stems and stable seed IDs; gate additional leaves by `vine_extent`. Update `edge_vine_mask_region` to union `_leaf_region(leaf)` for every visible edge leaf.

- [ ] **Step 3: Layer vine paint values**

Change signatures to:

```python
def paint_edge_vines(painter, scene, style, lighting) -> None: ...
def paint_anchor_vine(painter, scene, style, lighting) -> None: ...
```

For stems: low-alpha slightly wider shadow stroke, then main stroke. For leaves: base leaf fill plus a smaller upper-left highlight path using `style.palette.foliage_highlight` and `lighting.highlight_alpha`. Keep prepared geometry deterministic and animation-free.

- [ ] **Step 4: Verify and commit Task 4**

```powershell
uv run pytest -q tests/test_scene_vines.py tests/test_scene_renderer.py tests/test_desktop_windows.py
uv run ruff check src/digital_garden/desktop/scene/vines.py src/digital_garden/desktop/scene/renderer.py tests/test_scene_vines.py
uv run ruff format --check src/digital_garden/desktop/scene/vines.py src/digital_garden/desktop/scene/renderer.py tests/test_scene_vines.py
git diff --check
git add src/digital_garden/desktop/scene/vines.py src/digital_garden/desktop/scene/renderer.py tests/test_scene_vines.py
git commit -m "feat(renderer): refine living vines"
```

---

### Task 5: Integrated HUD and Renderer-Owned Collapse Visual

**Files:**
- Modify: `src/digital_garden/desktop/scene/renderer.py`
- Modify: `src/digital_garden/desktop/scene/style.py`
- Modify: `src/digital_garden/desktop/windows.py`
- Test: `tests/test_scene_renderer.py`
- Test: `tests/test_desktop_windows.py`

**Interfaces:**
- Keeps `PATCH_LABEL_RECT` and `PATCH_COLLAPSE_RECT` interaction geometry.
- Renderer paints both visuals; `QPushButton` remains only the click target.

- [ ] **Step 1: Write invisible-hit-target RED**

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

Run `uv run pytest -q tests/test_desktop_windows.py -k invisible_hit_target`; expected FAIL.

- [ ] **Step 2: Convert stock button to transparent interaction surface**

```python
self._collapse_button = QPushButton("", self)
self._collapse_button.setFlat(True)
self._collapse_button.setStyleSheet("background: transparent; border: none;")
self._collapse_button.setGeometry(PATCH_COLLAPSE_RECT)
self._collapse_button.clicked.connect(self.collapse_requested.emit)
```

Run full `tests/test_desktop_windows.py`; expected PASS.

- [ ] **Step 3: Write renderer-owned HUD RED**

Add `_paint_patch` usage and:

```python
def test_renderer_owns_soft_hud_and_collapse_visuals() -> None:
    image = _paint_patch(_render_state())
    hud = image.pixelColor(QPoint(24, 24))
    collapse = image.pixelColor(PATCH_COLLAPSE_RECT.center())

    assert 0 < hud.alpha() < 255
    assert collapse.alpha() > 0
```

Run `uv run pytest -q tests/test_scene_renderer.py -k soft_hud`; expected FAIL before the collapse affordance is painted by the renderer.

- [ ] **Step 4: Implement integrated HUD/collapse paint**

Use `style.palette.overlay_backing` instead of the hard-coded green rectangle. Paint a restrained two-layer rounded translucent backing; keep real Qt text limited to `CONDITION` and `WEATHER`. Paint `PATCH_COLLAPSE_RECT` as a small moss/soil-toned rounded tab and draw real Qt `COLLAPSE` text centered inside it. Do not add unsupported telemetry.

- [ ] **Step 5: Verify and commit Task 5**

```powershell
uv run pytest -q tests/test_scene_renderer.py tests/test_desktop_windows.py
uv run ruff check src/digital_garden/desktop/scene/renderer.py src/digital_garden/desktop/scene/style.py src/digital_garden/desktop/windows.py tests/test_scene_renderer.py tests/test_desktop_windows.py
uv run ruff format --check src/digital_garden/desktop/scene/renderer.py src/digital_garden/desktop/scene/style.py src/digital_garden/desktop/windows.py tests/test_scene_renderer.py tests/test_desktop_windows.py
git diff --check
git add src/digital_garden/desktop/scene/renderer.py src/digital_garden/desktop/scene/style.py src/digital_garden/desktop/windows.py tests/test_scene_renderer.py tests/test_desktop_windows.py
git commit -m "feat(renderer): integrate garden HUD controls"
```

---

### Task 6: Whole-Scene Static Weather Polish

**Files:**
- Modify: `src/digital_garden/desktop/scene/renderer.py`
- Test: `tests/test_scene_weather.py`

**Interfaces:**
- Reuses only `SceneStyle.palette.ambient` and the prepared geometry regions.
- Adds no new state fields.

- [ ] **Step 1: Write RED above the ground layer**

```python
def test_weather_changes_static_canopy_atmosphere() -> None:
    state = _render_state()
    sunny = _paint_patch(replace(state, weather="SUNNY"))
    rainy = _paint_patch(replace(state, weather="RAINY"))

    assert sunny.pixelColor(280, 150) != rainy.pixelColor(280, 150)
```

Run `uv run pytest -q tests/test_scene_weather.py -k canopy_atmosphere`; expected FAIL if weather remains ground-only at that point.

- [ ] **Step 2: Implement clipped whole-scene atmosphere**

In `renderer.paint_patch`, after botanical paint and before HUD text, construct:

```python
scene_region = ground_mask_region(ground)
scene_region = scene_region.united(edge_vine_mask_region(edge_vines))
scene_region = scene_region.united(bonsai_mask_region(bonsai))
```

Clip the painter to `scene_region`, fill the patch bounds with `style.palette.ambient`, restore, then paint HUD/collapse so text remains crisp. Do not include the contact shadow in the atmosphere clip.

- [ ] **Step 3: Verify and commit Task 6**

```powershell
uv run pytest -q tests/test_scene_weather.py tests/test_scene_renderer.py tests/test_scene_ground.py tests/test_scene_bonsai.py tests/test_scene_vines.py
uv run ruff check src/digital_garden/desktop/scene/renderer.py tests/test_scene_weather.py
uv run ruff format --check src/digital_garden/desktop/scene/renderer.py tests/test_scene_weather.py
git diff --check
git add src/digital_garden/desktop/scene/renderer.py tests/test_scene_weather.py
git commit -m "feat(renderer): polish static weather atmosphere"
```

---

### Task 7: Evidence Gate for Optional 2x Supersampling

**Files:**
- Modify only if justified: `src/digital_garden/desktop/scene/renderer.py`
- Test only if justified: `tests/test_scene_renderer.py`

**Interfaces:**
- No code is required if native QPainter output is already acceptably smooth.

- [ ] **Step 1: Run native renderer manually**

```powershell
uv run digital-garden-desktop
```

Inspect small leaves, branch edges, grass, rounded ground edge, and HUD text at native Windows scaling.

- [ ] **Step 2: Apply the gate**

If aliasing is not visually material, make no code change and record direct rendering as accepted. If aliasing is materially harming the garden, proceed with exactly a 2x botanical-layer experiment; do not generalize to arbitrary scales or caching.

- [ ] **Step 3: If justified, write RED for fixed 2x size helper**

```python
def test_supersampled_patch_size_is_exactly_double_native_size() -> None:
    assert QPainterShellRenderer().supersampled_patch_size() == QSize(1040, 840)
```

- [ ] **Step 4: If justified, implement fixed 2x botanical offscreen render**

Render botanical layers to `QImage(1040, 840, Format_ARGB32_Premultiplied)`, scale the offscreen painter by `2.0`, then composite back to 520x420 with smooth transformation. Paint Qt HUD text at native resolution after downsampling. No other scale/caching API is added.

- [ ] **Step 5: Verify/commit only if code changed**

```powershell
uv run pytest -q tests/test_scene_renderer.py
uv run ruff check src/digital_garden/desktop/scene/renderer.py tests/test_scene_renderer.py
uv run ruff format --check src/digital_garden/desktop/scene/renderer.py tests/test_scene_renderer.py
git diff --check
git add src/digital_garden/desktop/scene/renderer.py tests/test_scene_renderer.py
git commit -m "perf(renderer): add bounded supersampling"
```

Skip `git add`/commit if the evidence gate rejects supersampling.

---

### Task 8: Final Regression and Windows Visual Acceptance

**Files:**
- No production change unless a gate exposes a defect.

**Interfaces:**
- Produces the sealed V0-B.2 QPainter visual baseline.

- [ ] **Step 1: Run complete automated gates**

```powershell
uv run pytest -q
uv run ruff check .
uv run ruff format --check .
git diff --check
```

Expected: all pass; test count is at least 97 plus this campaign's added tests.

- [ ] **Step 2: Verify canonical V0-A output**

```powershell
uv run digital-garden simulate --seed 7 --ticks 240
```

Expected values:

```json
{"anchor_state":"DRY","bonsai_health":0.44449999999999634,"bonsai_stress":1.0,"condition":"STRUGGLING","day_index":10,"hour_of_day":0,"observation_length":12,"overgrowth":0.29088800000001,"seed":7,"soil_moisture":0.13199999999999923,"tick":240,"weather":"CLOUDY"}
```

JSON spacing/order is not an acceptance issue because the CLI sorts keys; values must match.

- [ ] **Step 3: Verify branch and cleanliness**

```powershell
git branch --show-current
git rev-parse HEAD
git status --short
```

Expected branch: `build/digital-garden-v0b2-byte-continuation`; status clean after intended commits.

- [ ] **Step 4: Run Windows manual visual acceptance**

```powershell
uv run digital-garden-desktop
```

Accept only if: contact shadow is visible and not clipped; ground has subtle tonal breakup; bonsai canopy is richer but coherent; tree/ground/vines share one light direction; anchor still matches the garden; HUD is integrated; collapse remains clickable; SUNNY/CLOUDY/RAINY are visually distinct but calm; transparent-region masks still feel correct; drag/expand/collapse/outside-dismissal remain correct; no unsupported environment claims appear; performance remains smooth.
