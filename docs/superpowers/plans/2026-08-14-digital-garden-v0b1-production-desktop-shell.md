# Digital Garden V0-B.1 Production Desktop Shell Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Graduate the Windows/Qt mechanisms proven by the V0-B-0 spike into a clean production desktop shell with an immutable GardenService presentation boundary, production anchor/patch lifecycle, monitor-aware placement, and desktop-only position persistence.

**Architecture:** V0-B.1 adds a focused `digital_garden.desktop` package above the unchanged V0-A `GardenService`. `DesktopController` converts authoritative snapshots into an immutable `GardenRenderState`; production Qt windows consume that render state through a small QPainter shell renderer, while a separate desktop-preferences store owns only screen/anchor placement. This slice deliberately does not implement the living garden artwork, Garden actions, elapsed-time desktop lifecycle, or animation.

**Tech Stack:** Python 3.12+, PySide6/Qt 6 (`PySide6>=6.11,<7`), QWidget/QPainter, standard-library JSON persistence, existing `GardenService`, pytest, Ruff, Windows 11.

## Global Constraints

- Target platform: Windows 11 desktop.
- Approved desktop technology: PySide6 / Qt 6.
- Initial renderer: QWidget + QPainter.
- The Garden World remains authoritative; the desktop shell may read `GardenService.snapshot()` but may not assign Garden World values directly.
- Do not change V0-A weather, moisture, health, stress, growth, overgrowth, action, persistence, or timing rules.
- Do not introduce a second simulation clock.
- No Garden action controls are implemented in V0-B.1; `WATER`, `TRIM`, `PRUNE`, and `INSPECT` belong to V0-B.3.
- No elapsed-time Garden lifecycle integration is implemented in V0-B.1; that belongs to V0-B.4.
- No animation, rain motion, living ground-cover system, final bonsai artwork, fauna, neural network, LLM, reinforcement learning, real-weather API, Qt Quick/QML, native Windows hook, or second GUI framework.
- The collapsed anchor starts as the ambient default; expanded state is not persisted in V0-B.1.
- Desktop persistence stores only desktop-artifact preferences. It must never serialize or mutate Garden physics.
- Preserve the V0-A deterministic baseline, including all existing tests and the canonical seed-7 240-tick simulation.
- Manual Windows behavior cannot be marked PASS from offscreen tests alone.

## Plan Boundary

This plan implements **V0-B.1 only**. It establishes production package boundaries and a reliable shell. It intentionally leaves the rich bonsai/ground/vine/weather renderer to V0-B.2, the four Garden interactions to V0-B.3, and Garden resume/ambient animation/performance work to V0-B.4.

## Production File Structure

```text
pyproject.toml
uv.lock
src/digital_garden/desktop/
    __init__.py
    app.py
    controller.py
    presentation.py
    placement.py
    persistence.py
    windows.py
    scene/
        __init__.py
        renderer.py
tests/
    test_desktop_presentation.py
    test_desktop_persistence.py
    test_desktop_placement.py
    test_desktop_windows.py
    test_desktop_app.py
docs/experiments/
    2026-08-14-digital-garden-v0b1-production-shell-checklist.md
```

`interaction.py` and the richer scene modules (`bonsai.py`, `ground.py`, `vines.py`, `weather.py`, `ambience.py`) are deliberately not created in this slice.

---

### Task 1: Production dependency, immutable presentation model, and GardenService controller

**Files:**
- Modify: `pyproject.toml`
- Modify: `uv.lock` via `uv sync`
- Create: `src/digital_garden/desktop/__init__.py`
- Create: `src/digital_garden/desktop/presentation.py`
- Create: `src/digital_garden/desktop/controller.py`
- Create: `tests/test_desktop_presentation.py`

**Interfaces:**
- Consumes: existing `GardenService.snapshot() -> dict[str, object]`.
- Produces: `GardenRenderState`, `render_state_from_snapshot(snapshot)`, `DesktopController.render_state()`.
- Later tasks must consume `GardenRenderState`; they must not parse `GardenService.snapshot()` themselves.

- [ ] **Step 1: Add the production Qt dependency and desktop command declaration**

Modify `pyproject.toml` so the relevant entries are exactly:

```toml
[project]
name = "digital-garden"
version = "0.1.0"
description = "A living desktop garden artifact and deterministic learning environment."
requires-python = ">=3.12"
dependencies = [
  "PySide6>=6.11,<7",
]

[project.scripts]
digital-garden = "digital_garden.cli:main"
digital-garden-desktop = "digital_garden.desktop.app:main"
```

Do not remove or weaken the existing development dependencies or quality configuration.

- [ ] **Step 2: Synchronize dependencies and prove the approved Qt major version**

Run:

```powershell
uv sync
uv run python -c "import PySide6; print(PySide6.__version__)"
```

Expected: a PySide6 `6.x` version satisfying `>=6.11,<7` prints and `uv.lock` changes only as required by the dependency addition.

- [ ] **Step 3: Write the failing presentation tests**

Create `tests/test_desktop_presentation.py`:

```python
from dataclasses import replace

import pytest

from digital_garden.desktop.controller import DesktopController
from digital_garden.desktop.presentation import GardenRenderState, render_state_from_snapshot
from digital_garden.domain import BonsaiState, GroundState, SoilState, VineState, Weather, make_initial_state
from digital_garden.observation import inspection_snapshot
from digital_garden.service import GardenService


def test_snapshot_maps_to_complete_immutable_render_state() -> None:
    state = replace(
        make_initial_state(seed=7),
        tick=12,
        weather=Weather.RAINY,
        light_level=0.25,
        humidity=0.90,
        soil=SoilState(0.67),
        bonsai=BonsaiState(0.81, 0.22, 0.31, 0.64),
        ground=GroundState(0.48),
        vine=VineState(0.39),
    )
    render_state = render_state_from_snapshot(inspection_snapshot(state))

    assert render_state == GardenRenderState(
        seed=7,
        tick=12,
        weather="RAINY",
        light_level=0.25,
        humidity=0.90,
        soil_moisture=0.67,
        bonsai_health=0.81,
        bonsai_stress=0.22,
        bonsai_growth=0.31,
        canopy_density=0.64,
        ground_density=0.48,
        vine_extent=0.39,
        condition="HEALTHY",
        anchor_state="CALM",
    )


def test_controller_delegates_only_to_service_snapshot() -> None:
    service = GardenService(make_initial_state(seed=7))
    controller = DesktopController(service)
    assert controller.render_state() == render_state_from_snapshot(service.snapshot())
    assert service.state == make_initial_state(seed=7)


def test_presentation_rejects_malformed_snapshot() -> None:
    with pytest.raises(TypeError, match="snapshot state"):
        render_state_from_snapshot({"state": "bad", "derived": {}})
```

- [ ] **Step 4: Verify the presentation tests fail**

Run:

```powershell
uv run pytest tests/test_desktop_presentation.py -q
```

Expected: FAIL because the production desktop package does not exist.

- [ ] **Step 5: Implement the immutable presentation contract**

Create `src/digital_garden/desktop/__init__.py` containing:

```python
"""Production Windows desktop artifact for Digital Garden."""
```

Create `src/digital_garden/desktop/presentation.py` with this contract:

```python
from collections.abc import Mapping
from dataclasses import dataclass


@dataclass(frozen=True)
class GardenRenderState:
    seed: int
    tick: int
    weather: str
    light_level: float
    humidity: float
    soil_moisture: float
    bonsai_health: float
    bonsai_stress: float
    bonsai_growth: float
    canopy_density: float
    ground_density: float
    vine_extent: float
    condition: str
    anchor_state: str


def _mapping(value: object, name: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise TypeError(f"{name} must be a mapping")
    return value


def _number(value: object, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{name} must be numeric")
    return float(value)


def _integer(value: object, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} must be an integer")
    return value


def render_state_from_snapshot(snapshot: dict[str, object]) -> GardenRenderState:
    state = _mapping(snapshot.get("state"), "snapshot state")
    derived = _mapping(snapshot.get("derived"), "snapshot derived")
    soil = _mapping(state.get("soil"), "snapshot soil")
    bonsai = _mapping(state.get("bonsai"), "snapshot bonsai")
    ground = _mapping(state.get("ground"), "snapshot ground")
    vine = _mapping(state.get("vine"), "snapshot vine")

    return GardenRenderState(
        seed=_integer(state.get("seed"), "seed"),
        tick=_integer(state.get("tick"), "tick"),
        weather=str(state.get("weather")),
        light_level=_number(state.get("light_level"), "light_level"),
        humidity=_number(state.get("humidity"), "humidity"),
        soil_moisture=_number(soil.get("moisture"), "soil moisture"),
        bonsai_health=_number(bonsai.get("health"), "bonsai health"),
        bonsai_stress=_number(bonsai.get("stress"), "bonsai stress"),
        bonsai_growth=_number(bonsai.get("growth"), "bonsai growth"),
        canopy_density=_number(bonsai.get("canopy_density"), "canopy density"),
        ground_density=_number(ground.get("density"), "ground density"),
        vine_extent=_number(vine.get("extent"), "vine extent"),
        condition=str(derived.get("condition")),
        anchor_state=str(derived.get("anchor_state")),
    )
```

- [ ] **Step 6: Implement the GardenService-facing controller**

Create `src/digital_garden/desktop/controller.py`:

```python
from digital_garden.desktop.presentation import GardenRenderState, render_state_from_snapshot
from digital_garden.service import GardenService


class DesktopController:
    def __init__(self, service: GardenService) -> None:
        self._service = service

    def render_state(self) -> GardenRenderState:
        return render_state_from_snapshot(self._service.snapshot())
```

No mutating Garden methods belong in this controller during V0-B.1.

- [ ] **Step 7: Run Task 1 verification**

Run:

```powershell
uv run pytest tests/test_desktop_presentation.py -q
uv run ruff check src/digital_garden/desktop tests/test_desktop_presentation.py
uv run ruff format --check src/digital_garden/desktop tests/test_desktop_presentation.py
git diff --check
```

Expected: all pass.

- [ ] **Step 8: Commit Task 1**

```powershell
git add pyproject.toml uv.lock src/digital_garden/desktop tests/test_desktop_presentation.py
git commit -m "feat: add production desktop presentation boundary"
```

---

### Task 2: Desktop-only preferences and deterministic monitor-aware placement

**Files:**
- Create: `src/digital_garden/desktop/persistence.py`
- Create: `src/digital_garden/desktop/placement.py`
- Create: `tests/test_desktop_persistence.py`
- Create: `tests/test_desktop_placement.py`

**Interfaces:**
- Produces: `DesktopPreferences`, `DesktopPreferencesStore`, `default_preferences_path()`, `ScreenGeometry`, `choose_screen()`, `default_anchor_origin()`, `clamp_anchor_origin()`, and `adjacent_patch_origin()`.
- Desktop preferences must not import `GardenState`, `GardenService`, `digital_garden.persistence`, or Garden config constants.

- [ ] **Step 1: Write failing desktop-preferences tests**

Create `tests/test_desktop_persistence.py`:

```python
import json

from digital_garden.desktop.persistence import (
    DESKTOP_PREFERENCES_SCHEMA_VERSION,
    DesktopPreferences,
    DesktopPreferencesStore,
)


def test_desktop_preferences_round_trip(tmp_path) -> None:
    path = tmp_path / "desktop.json"
    store = DesktopPreferencesStore(path)
    preferences = DesktopPreferences(screen_name="DISPLAY2", anchor_x=1710, anchor_y=760)

    store.save(preferences)

    assert store.load() == preferences
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["schema_version"] == DESKTOP_PREFERENCES_SCHEMA_VERSION
    assert "state" not in payload
    assert "soil" not in payload


def test_missing_or_invalid_desktop_preferences_fall_back_safely(tmp_path) -> None:
    path = tmp_path / "desktop.json"
    store = DesktopPreferencesStore(path)
    assert store.load() == DesktopPreferences()

    path.write_text("not-json", encoding="utf-8")
    assert store.load() == DesktopPreferences()
```

- [ ] **Step 2: Verify the preferences tests fail**

```powershell
uv run pytest tests/test_desktop_persistence.py -q
```

- [ ] **Step 3: Implement desktop-only preferences**

Create `src/digital_garden/desktop/persistence.py` with exactly one schema and no Garden imports:

```python
import json
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path

DESKTOP_PREFERENCES_SCHEMA_VERSION = 1


@dataclass(frozen=True)
class DesktopPreferences:
    screen_name: str | None = None
    anchor_x: int | None = None
    anchor_y: int | None = None


def default_preferences_path() -> Path:
    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        return Path(local_app_data) / "DigitalGarden" / "desktop.json"
    return Path.home() / ".digital-garden" / "desktop.json"


class DesktopPreferencesStore:
    def __init__(self, path: Path) -> None:
        self.path = path

    def load(self) -> DesktopPreferences:
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
            if payload.get("schema_version") != DESKTOP_PREFERENCES_SCHEMA_VERSION:
                return DesktopPreferences()
            screen_name = payload.get("screen_name")
            anchor_x = payload.get("anchor_x")
            anchor_y = payload.get("anchor_y")
            if screen_name is not None and not isinstance(screen_name, str):
                return DesktopPreferences()
            if anchor_x is not None and not isinstance(anchor_x, int):
                return DesktopPreferences()
            if anchor_y is not None and not isinstance(anchor_y, int):
                return DesktopPreferences()
            return DesktopPreferences(screen_name, anchor_x, anchor_y)
        except (FileNotFoundError, json.JSONDecodeError, OSError, TypeError):
            return DesktopPreferences()

    def save(self, preferences: DesktopPreferences) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "schema_version": DESKTOP_PREFERENCES_SCHEMA_VERSION,
            "screen_name": preferences.screen_name,
            "anchor_x": preferences.anchor_x,
            "anchor_y": preferences.anchor_y,
        }
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=self.path.parent,
            prefix=f".{self.path.name}.",
            suffix=".tmp",
            delete=False,
        ) as temporary:
            json.dump(payload, temporary, sort_keys=True)
            temporary_path = Path(temporary.name)
        try:
            os.replace(temporary_path, self.path)
        except BaseException:
            temporary_path.unlink(missing_ok=True)
            raise
```

- [ ] **Step 4: Write failing placement tests**

Create `tests/test_desktop_placement.py`:

```python
from PySide6.QtCore import QPoint, QRect, QSize

from digital_garden.desktop.persistence import DesktopPreferences
from digital_garden.desktop.placement import (
    ScreenGeometry,
    adjacent_patch_origin,
    choose_screen,
    restore_anchor_origin,
)


def test_choose_screen_prefers_saved_name_and_falls_back_to_primary() -> None:
    screens = (
        ScreenGeometry("PRIMARY", QRect(0, 0, 1920, 1080)),
        ScreenGeometry("SECONDARY", QRect(1920, 0, 1920, 1080)),
    )
    assert choose_screen(screens, "SECONDARY").name == "SECONDARY"
    assert choose_screen(screens, "MISSING").name == "PRIMARY"


def test_restore_anchor_clamps_saved_position_to_available_geometry() -> None:
    screen = ScreenGeometry("PRIMARY", QRect(0, 0, 1920, 1080))
    preferences = DesktopPreferences("PRIMARY", 5000, 5000)
    assert restore_anchor_origin(preferences, screen, QSize(96, 180)) == QPoint(1824, 900)


def test_patch_prefers_left_and_flips_right_when_required() -> None:
    available = QRect(0, 0, 1920, 1080)
    patch_size = QSize(520, 420)
    assert adjacent_patch_origin(QRect(1800, 700, 96, 180), patch_size, available) == QPoint(
        1272, 580
    )
    assert adjacent_patch_origin(QRect(10, 500, 96, 180), patch_size, available) == QPoint(
        114, 380
    )
```

- [ ] **Step 5: Verify placement tests fail**

```powershell
uv run pytest tests/test_desktop_placement.py -q
```

- [ ] **Step 6: Implement deterministic placement**

Create `src/digital_garden/desktop/placement.py`:

```python
from dataclasses import dataclass

from PySide6.QtCore import QPoint, QRect, QSize

from digital_garden.desktop.persistence import DesktopPreferences

ANCHOR_MARGIN = 32
PATCH_GAP = 8


@dataclass(frozen=True)
class ScreenGeometry:
    name: str
    available: QRect


def choose_screen(screens: tuple[ScreenGeometry, ...], preferred_name: str | None) -> ScreenGeometry:
    if not screens:
        raise RuntimeError("no desktop screens are available")
    if preferred_name is not None:
        for screen in screens:
            if screen.name == preferred_name:
                return screen
    return screens[0]


def clamp_anchor_origin(origin: QPoint, anchor_size: QSize, available: QRect) -> QPoint:
    max_x = available.x() + available.width() - anchor_size.width()
    max_y = available.y() + available.height() - anchor_size.height()
    return QPoint(
        min(max(origin.x(), available.x()), max_x),
        min(max(origin.y(), available.y()), max_y),
    )


def default_anchor_origin(anchor_size: QSize, available: QRect) -> QPoint:
    return clamp_anchor_origin(
        QPoint(
            available.x() + available.width() - anchor_size.width() - ANCHOR_MARGIN,
            available.y() + available.height() - anchor_size.height() - ANCHOR_MARGIN,
        ),
        anchor_size,
        available,
    )


def restore_anchor_origin(
    preferences: DesktopPreferences,
    screen: ScreenGeometry,
    anchor_size: QSize,
) -> QPoint:
    if preferences.anchor_x is None or preferences.anchor_y is None:
        return default_anchor_origin(anchor_size, screen.available)
    return clamp_anchor_origin(
        QPoint(preferences.anchor_x, preferences.anchor_y), anchor_size, screen.available
    )


def adjacent_patch_origin(
    anchor_geometry: QRect,
    patch_size: QSize,
    available: QRect,
) -> QPoint:
    centered_y = anchor_geometry.y() + (anchor_geometry.height() - patch_size.height()) // 2
    max_y = available.y() + available.height() - patch_size.height()
    y = min(max(centered_y, available.y()), max_y)

    left_x = anchor_geometry.x() - PATCH_GAP - patch_size.width()
    if left_x >= available.x():
        x = left_x
    else:
        x = anchor_geometry.x() + anchor_geometry.width() + PATCH_GAP

    max_x = available.x() + available.width() - patch_size.width()
    return QPoint(min(max(x, available.x()), max_x), y)
```

- [ ] **Step 7: Run Task 2 verification**

```powershell
uv run pytest tests/test_desktop_persistence.py tests/test_desktop_placement.py -q
uv run ruff check src/digital_garden/desktop tests/test_desktop_persistence.py tests/test_desktop_placement.py
uv run ruff format --check src/digital_garden/desktop tests/test_desktop_persistence.py tests/test_desktop_placement.py
git diff --check
```

- [ ] **Step 8: Commit Task 2**

```powershell
git add src/digital_garden/desktop/persistence.py src/digital_garden/desktop/placement.py tests/test_desktop_persistence.py tests/test_desktop_placement.py
git commit -m "feat: add desktop placement persistence boundary"
```

---

### Task 3: Production QPainter shell renderer and proven window lifecycle

**Files:**
- Create: `src/digital_garden/desktop/scene/__init__.py`
- Create: `src/digital_garden/desktop/scene/renderer.py`
- Create: `src/digital_garden/desktop/windows.py`
- Create: `tests/test_desktop_windows.py`

**Interfaces:**
- Consumes: `GardenRenderState`, placement functions.
- Produces: `QPainterShellRenderer`, `VineAnchorWindow`, `GardenPatchWindow`.
- The windows may ask `DesktopController` for a render state, but must never parse snapshots or mutate Garden state.
- This task graduates only proven spike mechanics; it does not copy the spike package wholesale.

- [ ] **Step 1: Write failing Qt contract tests**

Create `tests/test_desktop_windows.py` beginning with:

```python
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import Qt
from PySide6.QtGui import QRegion
from PySide6.QtWidgets import QApplication, QWidget

from digital_garden.desktop.controller import DesktopController
from digital_garden.desktop.scene.renderer import QPainterShellRenderer
from digital_garden.desktop.windows import GardenPatchWindow, VineAnchorWindow
from digital_garden.domain import make_initial_state
from digital_garden.service import GardenService


def _controller() -> DesktopController:
    return DesktopController(GardenService(make_initial_state(seed=7)))


def test_anchor_and_patch_keep_the_proven_window_contract() -> None:
    app = QApplication.instance() or QApplication([])
    renderer = QPainterShellRenderer()
    anchor = VineAnchorWindow(_controller(), renderer)
    patch = GardenPatchWindow(_controller(), renderer)

    anchor_flags = anchor.windowFlags()
    patch_flags = patch.windowFlags()
    assert anchor_flags & Qt.WindowType.FramelessWindowHint
    assert anchor_flags & Qt.WindowType.WindowStaysOnTopHint
    assert anchor_flags & Qt.WindowType.Tool
    assert anchor_flags & Qt.WindowType.WindowDoesNotAcceptFocus
    assert patch_flags & Qt.WindowType.FramelessWindowHint
    assert patch_flags & Qt.WindowType.WindowStaysOnTopHint
    assert patch_flags & Qt.WindowType.Tool
    assert anchor.testAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
    assert patch.testAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
    assert not anchor.mask().isEmpty()
    assert not patch.mask().isEmpty()
    assert anchor.mask() != QRegion(anchor.rect())
    assert patch.mask() != QRegion(patch.rect())

    anchor.close()
    patch.close()
    app.processEvents()
```

Add a second test that attaches the patch, shows both through `anchor.expand_patch()`, activates a separate plain `QWidget`, processes events, and asserts the patch becomes hidden after its real `ActivationChange` transition. Do not call `collapse_patch()` directly in that regression.

- [ ] **Step 2: Verify the Qt tests fail**

```powershell
uv run pytest tests/test_desktop_windows.py -q
```

Expected: FAIL because the production renderer/windows do not exist.

- [ ] **Step 3: Implement the minimal production renderer boundary**

Create `src/digital_garden/desktop/scene/__init__.py`:

```python
"""Desktop scene rendering components."""
```

Create `renderer.py` with fixed shell dimensions and the proven organic-region strategy. Use:

```python
ANCHOR_SIZE = QSize(96, 180)
PATCH_SIZE = QSize(520, 420)
PATCH_LABEL_RECT = QRect(18, 16, 238, 86)
PATCH_GROUND_RECT = QRect(24, 236, 472, 156)
PATCH_COLLAPSE_RECT = QRect(414, 352, 82, 40)
```

`QPainterShellRenderer` must expose exactly:

```python
class QPainterShellRenderer:
    def anchor_mask(self) -> QRegion: ...
    def patch_mask(self) -> QRegion: ...
    def paint_anchor(self, painter: QPainter, state: GardenRenderState) -> None: ...
    def paint_patch(self, painter: QPainter, state: GardenRenderState) -> None: ...
```

Implementation requirements:

- `anchor_mask()` uses the proven narrow stem plus four elliptical leaf regions from the spike rather than a rectangular mask.
- `patch_mask()` unions only the small state plaque, placeholder bonsai trunk/canopy, ground ellipse, and collapse-control rectangle. It must not include a full-window rectangle.
- `paint_anchor()` uses antialiasing and a simple state tint selected from this exact mapping:

```python
ANCHOR_COLORS = {
    "CALM": QColor("#5E9B68"),
    "DRY": QColor("#9A8052"),
    "WILD": QColor("#4E8D4A"),
    "THRIVING": QColor("#78B86A"),
    "STRESSED": QColor("#7A6956"),
}
```

- `paint_patch()` deliberately remains a structural placeholder: draw a small translucent state plaque, one ground ellipse, a simple trunk/three-canopy silhouette, and text for `CONDITION` and `WEATHER`. Do not draw a full panel and do not begin V0-B.2 artwork.
- The renderer reads only `GardenRenderState` and has no `GardenService` import.

- [ ] **Step 4: Implement the production windows using the renderer**

Create `src/digital_garden/desktop/windows.py` with these production contracts:

```python
DRAG_THRESHOLD = 6

class GardenPatchWindow(QWidget):
    collapse_requested = Signal()

class VineAnchorWindow(QWidget):
    clicked = Signal()
    position_committed = Signal(str, int, int)
```

`GardenPatchWindow` requirements:

- flags: `FramelessWindowHint | WindowStaysOnTopHint | Tool`;
- `WA_TranslucentBackground`;
- fixed `PATCH_SIZE` and renderer-supplied mask;
- one small explicit `COLLAPSE` control located at `PATCH_COLLAPSE_RECT`;
- `refresh_state()` stores only the latest immutable `GardenRenderState` from `DesktopController` and calls `update()`;
- `paintEvent()` creates a `QPainter` and delegates to `renderer.paint_patch()`;
- `changeEvent()` must use the proven production rule:

```python
if (
    event.type() is QEvent.Type.ActivationChange
    and self.isVisible()
    and not self.isActiveWindow()
):
    self.collapse_requested.emit()
```

`VineAnchorWindow` requirements:

- flags: `FramelessWindowHint | WindowStaysOnTopHint | Tool | WindowDoesNotAcceptFocus`;
- `WA_TranslucentBackground`;
- fixed `ANCHOR_SIZE` and renderer-supplied mask;
- left click expands attached patch unless a drag occurred;
- drag threshold is exactly `6` logical pixels;
- while dragged with an expanded patch, the patch remains adjacent;
- on completed drag, emit `position_committed(screen_name, x, y)` using the window's current screen name;
- `expand_patch()` refreshes patch state immediately before show, places it with `adjacent_patch_origin()`, then calls `show()`, `raise_()`, and `activateWindow()`;
- `collapse_patch()` hides the patch;
- `paintEvent()` delegates to `renderer.paint_anchor()` with the current render state.

No production window may call `GardenService.apply()` in V0-B.1.

- [ ] **Step 5: Run the window tests**

```powershell
uv run pytest tests/test_desktop_windows.py -q
```

If the offscreen activation test cannot exercise a real activation transition on the execution environment, retain the unit-level event contract and mark the live dismissal behavior for the Task 4 Windows manual gate. Do not weaken or remove the production `ActivationChange` implementation merely to satisfy an offscreen environment.

- [ ] **Step 6: Run Task 3 quality gates**

```powershell
uv run pytest tests/test_desktop_presentation.py tests/test_desktop_persistence.py tests/test_desktop_placement.py tests/test_desktop_windows.py -q
uv run ruff check src/digital_garden/desktop tests/test_desktop_*.py
uv run ruff format --check src/digital_garden/desktop tests/test_desktop_*.py
git diff --check
```

Expected: all executable gates pass.

- [ ] **Step 7: Commit Task 3**

```powershell
git add src/digital_garden/desktop/scene src/digital_garden/desktop/windows.py tests/test_desktop_windows.py
git commit -m "feat: add production Qt desktop shell windows"
```

---

### Task 4: Application orchestration, position restore/save, preserved baseline, and Windows handoff

**Files:**
- Create: `src/digital_garden/desktop/app.py`
- Create: `tests/test_desktop_app.py`
- Modify: `README.md`
- Create: `docs/experiments/2026-08-14-digital-garden-v0b1-production-shell-checklist.md`

**Interfaces:**
- Produces: `DesktopShell`, `build_desktop_shell(service, preferences_store)`, and the `digital-garden-desktop` command.
- Startup is collapsed-only in V0-B.1.
- The app may temporarily create `GardenService(make_initial_state(seed=7))` so the production shell is runnable. This is explicitly replaced by persisted Garden lifecycle orchestration in V0-B.4; do not duplicate elapsed-time logic here.

- [ ] **Step 1: Write failing application-wiring tests**

Create `tests/test_desktop_app.py`:

```python
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from digital_garden.desktop.app import build_desktop_shell
from digital_garden.desktop.persistence import DesktopPreferences, DesktopPreferencesStore
from digital_garden.domain import make_initial_state
from digital_garden.service import GardenService


def test_shell_starts_collapsed_and_does_not_mutate_garden(tmp_path) -> None:
    app = QApplication.instance() or QApplication([])
    service = GardenService(make_initial_state(seed=7))
    store = DesktopPreferencesStore(tmp_path / "desktop.json")
    shell = build_desktop_shell(service, store)

    assert shell.anchor.isVisible() is False
    assert shell.patch.isVisible() is False
    assert service.state == make_initial_state(seed=7)

    shell.anchor.close()
    shell.patch.close()
    app.processEvents()


def test_committed_anchor_position_is_saved_as_desktop_only_preference(tmp_path) -> None:
    app = QApplication.instance() or QApplication([])
    service = GardenService(make_initial_state(seed=7))
    store = DesktopPreferencesStore(tmp_path / "desktop.json")
    shell = build_desktop_shell(service, store)

    shell.anchor.position_committed.emit("SCREEN-X", 120, 240)

    assert store.load() == DesktopPreferences("SCREEN-X", 120, 240)
    assert service.state == make_initial_state(seed=7)
    shell.anchor.close()
    shell.patch.close()
    app.processEvents()
```

- [ ] **Step 2: Verify app tests fail**

```powershell
uv run pytest tests/test_desktop_app.py -q
```

- [ ] **Step 3: Implement the application shell builder**

Create `src/digital_garden/desktop/app.py` with:

```python
import sys
from dataclasses import dataclass

from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QApplication

from digital_garden.desktop.controller import DesktopController
from digital_garden.desktop.persistence import (
    DesktopPreferences,
    DesktopPreferencesStore,
    default_preferences_path,
)
from digital_garden.desktop.placement import ScreenGeometry, choose_screen, restore_anchor_origin
from digital_garden.desktop.scene.renderer import ANCHOR_SIZE, QPainterShellRenderer
from digital_garden.desktop.windows import GardenPatchWindow, VineAnchorWindow
from digital_garden.domain import make_initial_state
from digital_garden.service import GardenService


@dataclass
class DesktopShell:
    anchor: VineAnchorWindow
    patch: GardenPatchWindow


def _screen_geometries() -> tuple[ScreenGeometry, ...]:
    screens = QGuiApplication.screens()
    if not screens:
        raise RuntimeError("no desktop screens are available")
    primary = QGuiApplication.primaryScreen()
    ordered = ([primary] if primary is not None else []) + [screen for screen in screens if screen is not primary]
    return tuple(ScreenGeometry(screen.name(), screen.availableGeometry()) for screen in ordered)


def build_desktop_shell(
    service: GardenService,
    preferences_store: DesktopPreferencesStore,
) -> DesktopShell:
    controller = DesktopController(service)
    renderer = QPainterShellRenderer()
    anchor = VineAnchorWindow(controller, renderer)
    patch = GardenPatchWindow(controller, renderer)
    anchor.attach_patch(patch)

    preferences = preferences_store.load()
    screen = choose_screen(_screen_geometries(), preferences.screen_name)
    anchor.move(restore_anchor_origin(preferences, screen, ANCHOR_SIZE))

    def save_anchor_position(screen_name: str, x: int, y: int) -> None:
        preferences_store.save(DesktopPreferences(screen_name, x, y))

    anchor.position_committed.connect(save_anchor_position)
    return DesktopShell(anchor=anchor, patch=patch)


def main() -> None:
    app = QApplication.instance() or QApplication(sys.argv)
    # V0-B.1 keeps Garden lifecycle deliberately simple. V0-B.4 integrates
    # authoritative persisted Garden resume without adding a second clock.
    service = GardenService(make_initial_state(seed=7))
    store = DesktopPreferencesStore(default_preferences_path())
    shell = build_desktop_shell(service, store)
    shell.anchor.show()
    raise SystemExit(app.exec())
```

Keep `DesktopShell` alive for the lifetime of the event loop; do not construct temporary windows that can be garbage collected.

- [ ] **Step 4: Verify app tests pass**

```powershell
uv run pytest tests/test_desktop_app.py -q
```

- [ ] **Step 5: Update the README without overstating V0-B completion**

Add a `V0-B.1 production shell` section documenting:

```text
PySide6/Qt 6 is the approved Windows desktop technology.
V0-B.1 provides the production desktop shell only; living garden rendering,
Garden actions, persisted Garden resume, and ambient animation remain later
V0-B slices.
```

Add the exact local command:

```powershell
uv run digital-garden-desktop
```

Do not describe V0-B as complete.

- [ ] **Step 6: Write the Windows manual acceptance checklist**

Create `docs/experiments/2026-08-14-digital-garden-v0b1-production-shell-checklist.md` with the exact run command and these gates, each initially `NOT TESTED`:

```text
S1 Frameless/transparency — anchor and patch have no standard chrome; transparent gaps remain transparent.
S2 Persistent anchor — anchor stays above ordinary apps without unnecessary keyboard focus.
S3 Expansion/collapse — one click expands; explicit COLLAPSE returns to the anchor.
S4 Input integrity — transparent/non-artifact areas do not materially block underlying app input.
S5 Outside dismissal — one click into another ordinary app both dismisses the patch and reaches that app.
S6 Multi-screen placement — anchor can move across available screens and patch opens on the anchor's current screen.
S7 Position persistence — after dragging, closing, and relaunching, the anchor restores to the saved screen/position or safely clamps/falls back when geometry is unavailable.
S8 Garden boundary — displayed condition/weather come from the real GardenService render state; using the shell itself does not mutate Garden state.
```

The checklist must state that final visual quality is not judged in V0-B.1; V0-B.2 owns the living garden renderer.

- [ ] **Step 7: Run the complete automated V0-B.1 gate**

Run:

```powershell
uv sync
uv run pytest -q
uv run ruff check .
uv run ruff format --check .
git diff --check
uv run digital-garden simulate --seed 7 --ticks 240
```

Required canonical output remains exactly:

```text
seed = 7
tick = 240
day_index = 10
hour_of_day = 0
observation_length = 12
weather = CLOUDY
anchor_state = DRY
condition = STRUGGLING
soil_moisture = 0.13199999999999923
bonsai_health = 0.44449999999999634
bonsai_stress = 1.0
overgrowth = 0.29088800000001
```

Any V0-A regression is a blocker.

- [ ] **Step 8: Smoke-launch but do not self-certify Windows gates**

Run:

```powershell
uv run digital-garden-desktop
```

Expected structural result: a compact production vine anchor appears; click expands a transparent organic placeholder patch that displays real condition/weather and offers COLLAPSE. Close the process after the smoke run. Automated or computer-use evidence may support the implementation, but S1–S8 remain for Nolan's real desktop acceptance unless he personally observes them.

- [ ] **Step 9: Commit Task 4**

```powershell
git add src/digital_garden/desktop/app.py tests/test_desktop_app.py README.md docs/experiments/2026-08-14-digital-garden-v0b1-production-shell-checklist.md
git commit -m "feat: complete V0-B.1 production desktop shell"
```

- [ ] **Step 10: Independent whole-slice review and handoff**

Review the complete V0-B.1 diff from its merge-base. Require:

- V0-B.1 spec compliance;
- no Garden World authority leakage;
- no Garden action implementation;
- no elapsed-time duplicate clock;
- desktop preferences contain only desktop state;
- renderer consumes immutable presentation state;
- window code does not parse Garden snapshots;
- no full opaque patch rectangle;
- no native/global hook;
- all automated gates green;
- no Critical or Important review findings.

Repair Critical/Important findings and rerun the complete gate before handoff.

## V0-B.1 Completion Boundary

The implementation campaign ends at:

```text
READY_FOR_V0B1_MANUAL_ACCEPTANCE
```

The implementation branch should be pushed but not merged until Nolan completes S1–S8. V0-B.2 must not begin before the production shell baseline is accepted and preserved.

Required implementation branch:

```text
build/digital-garden-v0b1-production-shell
```

Recommended isolated worktree:

```text
C:\Users\nolan\AIProjects\digital-garden-v0b1-production-shell
```

The branch must be based on the approved `design/digital-garden-v0b-desktop-artifact` branch containing this plan and the V0-B production specification.
