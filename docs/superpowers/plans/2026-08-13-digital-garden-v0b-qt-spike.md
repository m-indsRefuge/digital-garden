# Digital Garden V0-B-0 PySide6 Desktop Artifact Spike Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the smallest runnable PySide6/Qt prototype that proves or disproves Digital Garden's transparent, frameless, always-on-top, expandable desktop-artifact interaction model on Windows 11.

**Architecture:** The spike adds a thin Qt Widgets shell above the existing `GardenService`; the Garden World remains authoritative and unchanged. A compact shaped `VineAnchorWindow` owns the collapsed surface, an adjacent shaped `GardenPatchWindow` owns the temporary expanded surface, and a tiny controller translates `GardenService.snapshot()` into display values and routes one diagnostic `WATER` action through `GardenService.apply()`.

**Tech Stack:** Python 3.12+, existing Digital Garden V0-A runtime, PySide6/Qt 6 (`PySide6>=6.10,<7`), Qt Widgets, pytest, Ruff, Windows 11.

## Global Constraints

- This is a technology-feasibility experiment, not the full V0-B implementation.
- V0-A remains authoritative for all Garden World state and rules.
- The UI may read `GardenService.snapshot()` and request legitimate actions through `GardenService.apply()` only.
- No direct `GardenState` mutation from the UI.
- No V0-A constant or physics changes.
- Preserve the 52-test deterministic V0-A baseline and canonical 240-tick result.
- PySide6 is the only GUI framework in this spike.
- No final artwork, production animation, installer, tray UI, startup-at-login, neural network, LLM, reinforcement learning, or weather API.
- This implementation plan tests the pure-Qt shaped-window path only. If transparent-region input or outside dismissal fails on the real desktop, STOP and report the failure; do not add a native fallback in this plan.
- Manual window behavior is never marked PASS from code inspection alone.
- Target outcome: a real compact vine anchor that expands into a transparent attached garden patch and displays real Garden World state.

## Existing Interfaces

```python
from digital_garden.domain import GardenAction, make_initial_state
from digital_garden.service import GardenService

service = GardenService(make_initial_state(seed=7))
snapshot = service.snapshot()
# snapshot["derived"]["anchor_state"]
# snapshot["derived"]["condition"]
service.apply(GardenAction.WATER)
```

## File Structure

```text
pyproject.toml
src/digital_garden/ui_spike/
    __init__.py
    presentation.py
    geometry.py
    windows.py
    app.py
tests/
    test_ui_spike_presentation.py
    test_ui_spike_geometry.py
    test_ui_spike_windows.py
docs/experiments/
    2026-08-13-digital-garden-v0b-qt-spike-manual-checklist.md
    2026-08-13-digital-garden-v0b-qt-spike-report.md
```

---

### Task 1: PySide6 bootstrap, GardenService controller, and first visible vine anchor

**Files:**
- Modify: `pyproject.toml`
- Create: `src/digital_garden/ui_spike/__init__.py`
- Create: `src/digital_garden/ui_spike/presentation.py`
- Create: `src/digital_garden/ui_spike/windows.py`
- Create: `src/digital_garden/ui_spike/app.py`
- Create: `tests/test_ui_spike_presentation.py`
- Create: `tests/test_ui_spike_windows.py`

**Interfaces:**
- Consumes: `GardenService.snapshot()`, `GardenService.apply()`, `make_initial_state()`.
- Produces: `GardenSnapshotView`, `GardenSpikeController`, `VineAnchorWindow`, `digital-garden-ui-spike` command.

- [ ] **Step 1: Add PySide6 and the spike command**

Set the project dependency and script entries to include:

```toml
dependencies = [
  "PySide6>=6.10,<7",
]

[project.scripts]
digital-garden = "digital_garden.cli:main"
digital-garden-ui-spike = "digital_garden.ui_spike.app:main"
```

Keep all existing project metadata and quality-tool settings.

- [ ] **Step 2: Sync and prove PySide6 imports**

```powershell
uv sync
uv run python -c "import PySide6; print(PySide6.__version__)"
```

Expected: PySide6 6.x prints.

- [ ] **Step 3: Write failing controller tests**

Create `tests/test_ui_spike_presentation.py`:

```python
from digital_garden.domain import GardenAction, make_initial_state
from digital_garden.service import GardenService
from digital_garden.ui_spike.presentation import GardenSnapshotView, GardenSpikeController


def test_controller_reads_real_derived_state() -> None:
    controller = GardenSpikeController(GardenService(make_initial_state(seed=7)))
    assert controller.view() == GardenSnapshotView(anchor_state="CALM", condition="HEALTHY")


def test_water_routes_through_garden_service() -> None:
    service = GardenService(make_initial_state(seed=7))
    controller = GardenSpikeController(service)
    before = service.state.soil.moisture
    controller.water()
    assert service.state.soil.moisture > before
    assert controller.last_action is GardenAction.WATER
```

- [ ] **Step 4: Verify the tests fail**

```powershell
uv run pytest tests/test_ui_spike_presentation.py -q
```

Expected: import failure because `ui_spike.presentation` does not exist.

- [ ] **Step 5: Implement the controller boundary**

Create `presentation.py` with:

```python
from dataclasses import dataclass

from digital_garden.domain import GardenAction
from digital_garden.service import GardenService


@dataclass(frozen=True)
class GardenSnapshotView:
    anchor_state: str
    condition: str


class GardenSpikeController:
    def __init__(self, service: GardenService) -> None:
        self._service = service
        self.last_action: GardenAction | None = None

    def view(self) -> GardenSnapshotView:
        snapshot = self._service.snapshot()
        derived = snapshot["derived"]
        if not isinstance(derived, dict):
            raise TypeError("snapshot derived state must be a dictionary")
        return GardenSnapshotView(
            anchor_state=str(derived["anchor_state"]),
            condition=str(derived["condition"]),
        )

    def water(self) -> GardenSnapshotView:
        self._service.apply(GardenAction.WATER)
        self.last_action = GardenAction.WATER
        return self.view()
```

Create `__init__.py` containing only a package docstring.

- [ ] **Step 6: Verify the controller tests pass**

```powershell
uv run pytest tests/test_ui_spike_presentation.py -q
```

Expected: `2 passed`.

- [ ] **Step 7: Write a failing Qt flag test**

Create `tests/test_ui_spike_windows.py`:

```python
import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from digital_garden.domain import make_initial_state
from digital_garden.service import GardenService
from digital_garden.ui_spike.presentation import GardenSpikeController
from digital_garden.ui_spike.windows import VineAnchorWindow


def test_anchor_declares_spike_window_contract() -> None:
    app = QApplication.instance() or QApplication([])
    controller = GardenSpikeController(GardenService(make_initial_state(seed=7)))
    window = VineAnchorWindow(controller)
    flags = window.windowFlags()
    assert flags & Qt.WindowType.FramelessWindowHint
    assert flags & Qt.WindowType.WindowStaysOnTopHint
    assert flags & Qt.WindowType.Tool
    assert flags & Qt.WindowType.WindowDoesNotAcceptFocus
    assert window.testAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
    assert not window.mask().isEmpty()
    window.close()
    app.processEvents()
```

- [ ] **Step 8: Verify the Qt test fails**

```powershell
uv run pytest tests/test_ui_spike_windows.py -q
```

Expected: import failure because `VineAnchorWindow` does not exist.

- [ ] **Step 9: Implement the shaped vine anchor**

Create `windows.py` with `VineAnchorWindow(QWidget)` using:

```python
Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool | Qt.WindowDoesNotAcceptFocus
```

and `WA_TranslucentBackground`. Use logical size `96 x 180`. Build a non-rectangular `QRegion` mask from a narrow stem plus ellipse/leaf regions, draw simple antialiased procedural vine shapes with `QPainter`, emit `clicked` on a click, and support dragging when movement exceeds a `DRAG_THRESHOLD = 6` pixel threshold. No Garden World logic belongs in this class.

Expose:

```python
def build_anchor_mask() -> QRegion:
    ...
```

where the implementation returns the union of the actual stem/leaf regions used by the window.

- [ ] **Step 10: Implement the application bootstrap**

Create `app.py`:

```python
import sys

from PySide6.QtWidgets import QApplication

from digital_garden.domain import make_initial_state
from digital_garden.service import GardenService
from digital_garden.ui_spike.presentation import GardenSpikeController
from digital_garden.ui_spike.windows import VineAnchorWindow


def main() -> None:
    app = QApplication.instance() or QApplication(sys.argv)
    controller = GardenSpikeController(GardenService(make_initial_state(seed=7)))
    anchor = VineAnchorWindow(controller)
    anchor.show()
    raise SystemExit(app.exec())
```

- [ ] **Step 11: Run Task 1 gates**

```powershell
uv run pytest tests/test_ui_spike_presentation.py tests/test_ui_spike_windows.py -q
uv run ruff check src/digital_garden/ui_spike tests/test_ui_spike_presentation.py tests/test_ui_spike_windows.py
uv run ruff format --check src/digital_garden/ui_spike tests/test_ui_spike_presentation.py tests/test_ui_spike_windows.py
git diff --check
```

Expected: all pass.

- [ ] **Step 12: Smoke-launch without claiming manual gates**

```powershell
uv run digital-garden-ui-spike
```

Expected: a compact frameless vine-like placeholder appears. Close it normally. Do not mark transparency/input/focus/z-order/DPI gates PASS yet.

- [ ] **Step 13: Commit Task 1**

```powershell
git add pyproject.toml uv.lock src/digital_garden/ui_spike tests/test_ui_spike_presentation.py tests/test_ui_spike_windows.py
git commit -m "feat: add PySide6 desktop artifact spike anchor"
```

---

### Task 2: Expandable garden patch and diagnostic WATER interaction

**Files:**
- Create: `src/digital_garden/ui_spike/geometry.py`
- Modify: `src/digital_garden/ui_spike/windows.py`
- Modify: `src/digital_garden/ui_spike/app.py`
- Create: `tests/test_ui_spike_geometry.py`
- Modify: `tests/test_ui_spike_windows.py`

**Interfaces:**
- Produces: `adjacent_patch_origin(...)`, `GardenPatchWindow`, `VineAnchorWindow.attach_patch()`, `expand_patch()`, `collapse_patch()`.

- [ ] **Step 1: Write failing placement tests**

Create `tests/test_ui_spike_geometry.py`:

```python
from PySide6.QtCore import QPoint, QRect, QSize

from digital_garden.ui_spike.geometry import adjacent_patch_origin


def test_patch_prefers_left_when_space_exists() -> None:
    assert adjacent_patch_origin(
        QRect(1800, 700, 96, 180), QSize(520, 420), QRect(0, 0, 1920, 1080)
    ) == QPoint(1272, 460)


def test_patch_flips_right_near_left_edge() -> None:
    assert adjacent_patch_origin(
        QRect(10, 500, 96, 180), QSize(520, 420), QRect(0, 0, 1920, 1080)
    ) == QPoint(114, 380)
```

- [ ] **Step 2: Verify placement tests fail**

```powershell
uv run pytest tests/test_ui_spike_geometry.py -q
```

- [ ] **Step 3: Implement placement**

Create `geometry.py` with `PATCH_GAP = 8` and a deterministic `adjacent_patch_origin(anchor_geometry, patch_size, available_geometry)` that vertically centers/clamps the patch, prefers the left side, and flips right when left placement would leave the available screen geometry.

- [ ] **Step 4: Verify placement tests pass**

```powershell
uv run pytest tests/test_ui_spike_geometry.py -q
```

Expected: `2 passed`.

- [ ] **Step 5: Add failing patch tests**

Extend `test_ui_spike_windows.py` to construct `GardenPatchWindow` and assert:

```python
assert patch.windowFlags() & Qt.WindowType.FramelessWindowHint
assert patch.windowFlags() & Qt.WindowType.Tool
assert patch.testAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
assert patch.anchor_state_text == "CALM"
assert patch.condition_text == "HEALTHY"
```

Add a second test that calls `patch.perform_diagnostic_water()` and verifies the underlying `GardenService.state.soil.moisture` increases and `controller.last_action is GardenAction.WATER`.

- [ ] **Step 6: Verify the patch tests fail**

Run the two new test nodes. Expected: FAIL because `GardenPatchWindow` does not exist.

- [ ] **Step 7: Implement `GardenPatchWindow`**

Requirements:

- logical size `520 x 420`;
- frameless, translucent, always-on-top Qt Tool window;
- rounded/organic `QRegion` mask removing rectangular corners;
- procedural placeholder art only: moss/ground ellipse, simple trunk/branches, simple canopy circles;
- visible real `anchor_state` and `condition` from `GardenSpikeController.view()`;
- one diagnostic `WATER` control that calls `controller.water()` and refreshes the displayed state;
- one `COLLAPSE` control emitting `collapse_requested`;
- read-only `anchor_state_text` and `condition_text` properties;
- `perform_diagnostic_water()` public method.

Do not add TRIM, PRUNE, or INSPECT controls.

- [ ] **Step 8: Connect expand/collapse**

Extend `VineAnchorWindow` so `clicked` shows the attached patch adjacent to the anchor on the anchor's current screen, raises/activates the patch, and `collapse_requested` hides it. Dragging the anchor while expanded must keep the patch adjacent.

Update `app.py` to construct both windows, attach them, and show only the anchor at startup.

- [ ] **Step 9: Run Task 2 gates**

```powershell
uv run pytest tests/test_ui_spike_presentation.py tests/test_ui_spike_geometry.py tests/test_ui_spike_windows.py -q
uv run ruff check .
uv run ruff format --check .
git diff --check
```

Expected: all pass.

- [ ] **Step 10: Interactive smoke run**

```powershell
uv run digital-garden-ui-spike
```

Confirm only that click expands, COLLAPSE hides the patch, and WATER routes through the real service without crashing. Formal visual gates remain unclassified.

- [ ] **Step 11: Commit Task 2**

```powershell
git add src/digital_garden/ui_spike tests/test_ui_spike_geometry.py tests/test_ui_spike_windows.py
git commit -m "feat: add expandable Digital Garden spike patch"
```

---

### Task 3: Pure-Qt outside dismissal, focus contract, and display diagnostics

**Files:**
- Modify: `src/digital_garden/ui_spike/windows.py`
- Modify: `tests/test_ui_spike_windows.py`

**Interfaces:**
- Produces: `window_diagnostics(widget: QWidget) -> dict[str, object]` and collapse-on-window-deactivation behavior.

- [ ] **Step 1: Add failing diagnostics tests**

Add:

```python
from digital_garden.ui_spike.windows import window_diagnostics


def test_window_diagnostics_has_required_fields() -> None:
    app = QApplication.instance() or QApplication([])
    controller = GardenSpikeController(GardenService(make_initial_state(seed=7)))
    anchor = VineAnchorWindow(controller)
    result = window_diagnostics(anchor)
    assert set(result) == {
        "screen_name",
        "device_pixel_ratio",
        "logical_dpi_x",
        "logical_dpi_y",
        "geometry",
    }
    assert len(result["geometry"]) == 4
    anchor.close()
    app.processEvents()
```

- [ ] **Step 2: Verify the test fails**

```powershell
uv run pytest tests/test_ui_spike_windows.py::test_window_diagnostics_has_required_fields -q
```

- [ ] **Step 3: Implement diagnostics**

Implement `window_diagnostics()` to return screen name, device pixel ratio, logical DPI X/Y, and `(x, y, width, height)`. Print one concise JSON diagnostic line prefixed `DIGITAL_GARDEN_SPIKE_DISPLAY` when the anchor is first shown and when its screen changes.

- [ ] **Step 4: Implement outside dismissal using Qt window deactivation**

In `GardenPatchWindow.changeEvent`, on `QEvent.Type.WindowDeactivate`, emit `collapse_requested` when the patch is visible. Keep the explicit COLLAPSE control. Do not add application-wide input monitoring.

- [ ] **Step 5: Prove masks are installed**

Extend the Qt tests to assert both anchor and patch have non-empty masks whose bounding rectangle matches the widget rectangle while the actual mask is non-rectangular/multi-region.

- [ ] **Step 6: Run all automated gates and preserved V0-A baseline**

```powershell
uv run pytest -q
uv run ruff check .
uv run ruff format --check .
git diff --check
uv run digital-garden simulate --seed 7 --ticks 240
```

Required:

```text
all original 52 V0-A tests plus new spike tests pass
tick = 240
day_index = 10
observation_length = 12
all other canonical V0-A simulation values unchanged
```

If the Garden World output changes, STOP.

- [ ] **Step 7: Commit Task 3**

```powershell
git add src/digital_garden/ui_spike tests/test_ui_spike_windows.py
git commit -m "feat: harden Qt spike window behavior"
```

---

### Task 4: Manual acceptance package and stop gate

**Files:**
- Create: `docs/experiments/2026-08-13-digital-garden-v0b-qt-spike-manual-checklist.md`
- Create: `docs/experiments/2026-08-13-digital-garden-v0b-qt-spike-report.md`

**Interfaces:**
- Produces: human-executable Gate A-I checklist and `READY_FOR_MANUAL_ACCEPTANCE` report. It does not approve Qt before Nolan's observations.

- [ ] **Step 1: Write the manual checklist**

The checklist must instruct Nolan to run:

```powershell
uv sync
uv run digital-garden-ui-spike
```

and record `PASS`, `FAIL`, or `NOT TESTED` plus one observation for each:

```text
A Transparency — no opaque rectangle; desktop/app visible through transparent region.
B Frameless — no title bar or normal border.
C Persistent anchor — stays above ordinary apps and remains compact.
D Expansion — single click expands adjacent patch; COLLAPSE returns to vine.
E Input integrity — transparent/non-artifact area lets underlying app receive click; visible control receives artifact click.
F Outside dismissal — clicking another ordinary app dismisses expanded patch without breaking that app interaction.
G Focus — collapsed vine does not retain keyboard focus; expanded interaction is predictable; collapse returns to unobtrusive behavior.
H DPI/display — record DIGITAL_GARDEN_SPIKE_DISPLAY output; artifact remains visible/usable at current scaling; second-monitor movement is tested when available, otherwise NOT TESTED.
I GardenService — real anchor_state/condition visible; WATER routes through GardenService and refreshes without direct state mutation.
```

- [ ] **Step 2: Write the initial decision report**

Create the report with:

```text
Implementation status: READY_FOR_MANUAL_ACCEPTANCE
Technology decision: INCONCLUSIVE — manual Windows gates not yet executed
```

Include a Gate A-I table with every status initially `NOT TESTED` and observation `Awaiting manual Windows run.` Also record the exact pure-Qt techniques used by the branch: frameless/translucent Tool windows, QRegion masks, Qt deactivation dismissal, and direct `GardenService` binding. Do not claim manual success.

- [ ] **Step 3: Run the complete pre-manual gate**

```powershell
uv sync
uv run pytest -q
uv run ruff check .
uv run ruff format --check .
git diff --check
uv run digital-garden simulate --seed 7 --ticks 240
```

Required: all checks pass and canonical V0-A values remain unchanged.

- [ ] **Step 4: Commit the acceptance package**

```powershell
git add docs/experiments
git commit -m "docs: add Qt spike manual acceptance gate"
```

- [ ] **Step 5: Perform final independent whole-spike review**

Review the complete spike diff from its merge-base. Require:

- spec compliance;
- no Garden World authority leakage;
- no second GUI framework;
- correct `GardenService` boundary;
- pure-Qt shaped-window/input strategy only;
- manual gates remain unclaimed;
- automated tests and YAGNI quality.

Repair Critical/Important findings and re-review before handoff.

- [ ] **Step 6: Push and stop for the real desktop run**

Push the implementation branch. Do not merge it and do not open a production V0-B PR.

Return:

```text
READY_FOR_MANUAL_ACCEPTANCE
```

plus branch/worktree, final HEAD, PySide6 version, test count/result, Ruff/whitespace results, unchanged 240-tick output, independent reviewer verdict, exact run command, manual checklist path, report path, and confirmation that no non-Qt fallback was added.

## Failure Boundary

If the pure-Qt artifact cannot satisfy a load-bearing Windows behavior during Nolan's manual run, preserve the branch/evidence and stop. Any separate fallback experiment requires a new explicit human decision and is outside this implementation plan.

## Completion Boundary

This implementation plan ends at `READY_FOR_MANUAL_ACCEPTANCE`. The technology decision occurs only after Nolan supplies the Gate A-I observations. `APPROVE QT` triggers the separate full V0-B planning cycle; a fundamental failure follows the approved spike spec's reject/escalation rules.