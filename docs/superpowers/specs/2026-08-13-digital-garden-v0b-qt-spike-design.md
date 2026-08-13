# Digital Garden V0-B-0 — PySide6 Desktop Artifact Technology Spike

**Status:** Approved direction; written spike specification pending user review  
**Date:** 2026-08-13  
**Base:** `main` at the preserved V0-A Garden World baseline  
**Target platform:** Windows 11 desktop  
**Purpose:** Determine whether PySide6/Qt can reliably produce the unusual desktop-artifact behavior required by Digital Garden before committing the full V0-B implementation to Qt.

## 1. Decision being made

This is a technology-feasibility experiment, not the V0-B implementation.

The spike answers one question:

> Can PySide6/Qt produce a transparent, frameless, organic Windows desktop artifact with a persistent vine anchor, an attached expandable garden surface, acceptable input behavior, and direct access to the existing Python `GardenService`?

If the answer is yes, PySide6/Qt becomes the approved V0-B desktop technology and a separate V0-B implementation plan is written.

If a fundamental Windows behavior cannot be achieved cleanly, the spike is preserved as evidence and V0-B evaluates WPF next. The spike must not force Qt into production merely because some parts work.

## 2. Existing architectural boundary

V0-A on `main` remains authoritative.

```text
Desktop Artifact
      |
      | snapshot / action request
      v
 GardenService
      |
      v
 Garden World
```

The spike may read Garden World state and request legitimate actions through `GardenService`.

The spike must not:

- duplicate garden simulation logic;
- mutate `GardenState` directly;
- move weather, moisture, health, growth, condition, or reward authority into the UI;
- change V0-A constants or physics;
- alter the deterministic 52-test V0-A baseline.

## 3. Why PySide6 is first

PySide6 is tested first because the existing Garden World is Python, allowing the desktop artifact to consume `GardenService` directly without adding a C#/Python process or IPC boundary.

Qt documentation establishes that top-level translucent widgets are supported and that, on Windows, translucency requires a frameless window. Qt also exposes always-on-top, no-focus, and input-transparency window flags. These capabilities make PySide6 a plausible fit, but the actual combination must be proven on the target Windows 11 machine rather than assumed from documentation.

Primary references:

- Qt for Python `QWidget` translucent-window documentation: https://doc.qt.io/qtforpython-6/PySide6/QtWidgets/QWidget.html
- Qt for Python `Qt.WindowType` / widget attributes: https://doc.qt.io/qtforpython-6/PySide6/QtCore/Qt.html

## 4. Spike scope

The spike creates the smallest runnable visual shell capable of exercising the required window behavior.

It contains only:

1. one compact vine-anchor surface;
2. one attached expanded garden surface;
3. simple procedural placeholder artwork;
4. expand/collapse behavior;
5. minimal GardenService binding;
6. diagnostic output needed to judge DPI, monitor, focus, z-order, and input behavior.

It does not contain the final bonsai artwork, animations, production persistence orchestration, startup-at-login behavior, settings UI, tray UI, installer, neural intelligence, LLMs, or V0-B polish.

The spike has a hard scope cap: one Qt implementation path plus, only if needed for transparent-region hit testing, one small isolated Windows-native hit-test experiment. Do not add a second GUI framework or a general native-window abstraction inside this spike.

## 5. Visual shell

### Collapsed state

The initial process displays only a compact organic anchor near a desktop edge or corner.

The visible placeholder should suggest a vine using simple Qt-painted shapes. It need not be beautiful; its purpose is to reveal whether an irregular transparent artifact behaves correctly.

Requirements:

- no conventional title bar;
- no standard window border;
- desktop/applications remain visibly present through transparent regions;
- compact footprint;
- always-on-top over ordinary application windows;
- anchor remains clickable;
- ordinary keyboard focus should not be captured unnecessarily.

### Expanded state

Clicking the anchor reveals a medium transparent/organic garden surface immediately adjacent to and visually connected with the anchor.

The expanded surface contains only enough placeholder content to make its bounds and interaction region obvious, such as:

- a stylised placeholder bonsai silhouette;
- a ground/moss patch;
- a small diagnostic label showing the current Garden World condition.

The expanded surface must still avoid conventional app chrome.

## 6. Required interaction experiment

The spike must prove or explicitly fail each of these behaviors on Windows 11:

```text
single click anchor -> expand
explicit collapse control -> collapse
outside interaction -> expanded artifact dismisses without remaining over work
```

No hover interaction is introduced.

No right-click action menu is introduced.

The outside-interaction experiment must first attempt a Qt-native/non-invasive mechanism such as window deactivation/focus transition. A global mouse hook is not permitted merely to make the spike pass.

If Qt cannot meet the dismissal contract without invasive global input interception, record that as a technology risk/failure rather than hiding it.

## 7. Transparent-region input test

This is a load-bearing feasibility gate.

The organic artifact must not create a large invisible rectangle that blocks ordinary desktop/application clicks in visually transparent areas.

The spike must test the smallest reasonable Qt-native technique first, including shaped/masked regions where suitable.

If per-region click behavior requires a small Windows-specific native hit-test shim, Forge may prototype that only as a clearly isolated spike experiment. It must not become an unreviewed production abstraction.

The report must distinguish:

- pure-Qt behavior;
- any Windows-specific workaround tested;
- whether the workaround is small and deterministic enough to be acceptable for V0-B.

## 8. Always-on-top and focus behavior

The collapsed vine anchor should remain above ordinary windows while remaining unobtrusive.

The spike must inspect:

- z-order after switching among ordinary applications;
- whether clicking the anchor unexpectedly activates or steals focus beyond what is required;
- whether expanded interaction can temporarily receive input;
- whether collapse returns the artifact to its compact ambient state.

The spike does not need to defeat exclusive full-screen applications, secure desktop surfaces, UAC prompts, or other system-owned topmost surfaces.

## 9. DPI and multi-monitor test

The spike must expose enough diagnostics to manually verify:

- current screen name;
- logical DPI or device-pixel ratio;
- window geometry;
- active screen changes when moved between monitors.

Acceptance does not require an automated multi-monitor laboratory. It requires the prototype to remain correctly visible and usable when manually moved between available monitors and under the current Windows display scaling.

If only one monitor is available during the run, record multi-monitor movement as `NOT TESTED`, not `PASS`.

## 10. Garden World binding

The prototype must import the existing Garden World package directly and create or receive a `GardenService` instance through the existing public Python boundary.

At minimum, the expanded artifact displays two labelled values from a real `GardenService.snapshot()` result:

```text
anchor_state      <- snapshot["derived"]["anchor_state"]
garden_condition  <- snapshot["derived"]["condition"]
```

The spike must expose exactly one diagnostic Garden action control: `WATER`. It must call `GardenService.apply(GardenAction.WATER)` and then refresh the displayed Garden World snapshot. This proves the action path without building the production Water/Trim/Prune/Inspect control surface.

No Garden World state may be manually assigned by the UI.

## 11. Dependency boundary

The spike may add PySide6 on its isolated branch/worktree.

No other GUI framework may be added during the PySide6 experiment.

Avoid third-party helper libraries for transparency, global hooks, theming, animation, window management, or IPC unless PySide6 itself cannot exercise a load-bearing requirement and the failure is being explicitly investigated.

The purpose is to evaluate Qt, not a stack of compensating packages.

## 12. Evidence and observability

The spike must produce:

1. a runnable command for Nolan's Windows machine;
2. automated tests for non-visual deterministic behavior that can reasonably be tested without a desktop session;
3. a manual acceptance checklist for the actual window behavior;
4. a short technology decision report.

The report must classify every gate as:

```text
PASS
FAIL
NOT TESTED
```

and include a short observation/evidence note.

The report must not convert an untested desktop behavior into a pass based on code inspection alone. Forge may prepare the checklist and automated evidence, but the load-bearing visual/input gates are not `PASS` until Nolan exercises the runnable prototype on the target Windows desktop and supplies the observations.

## 13. Feasibility gates

PySide6 is approved for V0-B only if all load-bearing gates pass on Nolan's Windows 11 desktop.

### Gate A — Transparency

- desktop/other applications visibly show through transparent regions;
- no opaque rectangular background surrounds the artifact.

### Gate B — Frameless artifact

- no normal Windows title bar or border appears during normal use.

### Gate C — Persistent anchor

- collapsed vine anchor stays above ordinary application windows;
- its footprint remains compact.

### Gate D — Expansion

- single click on anchor reveals the attached medium garden surface;
- collapse returns to the compact anchor.

### Gate E — Input integrity

- visible interactive regions receive intended clicks;
- visually transparent/non-artifact regions do not materially block ordinary desktop/application input.

### Gate F — Dismissal

- interacting outside the expanded garden dismisses it through a non-invasive mechanism;
- no global mouse hook is required for the approved path.

### Gate G — Focus behavior

- the anchor does not unnecessarily steal keyboard focus;
- expanded interaction behaves predictably;
- collapse restores unobtrusive ambient behavior.

### Gate H — DPI/display behavior

- artifact remains correctly visible and usable at the current Windows scaling;
- multi-monitor movement passes when more than one display is available, otherwise this sub-check is `NOT TESTED` and does not by itself reject Qt.

### Gate I — GardenService compatibility

- the UI reads real `anchor_state` and `garden_condition` from `GardenService`;
- the diagnostic `WATER` control passes through `GardenService.apply()` and the refreshed snapshot reflects the legitimate Garden World outcome;
- no direct GardenState mutation occurs in the UI.

## 14. Decision rule

### APPROVE QT

Approve PySide6/Qt for V0-B when Gates A–G and I pass, the current-display portion of H passes, and any Windows-specific shim required for transparent hit testing is small, isolated, deterministic, and reviewable.

### REJECT QT

Reject PySide6/Qt for V0-B if any of these are true:

- reliable translucent frameless behavior cannot be achieved;
- the anchor cannot remain topmost without unacceptable focus/input side effects;
- transparent regions materially block normal work and only invasive interception fixes it;
- outside dismissal requires a global input hook;
- direct GardenService binding proves unstable or forces architectural coupling that violates V0-A authority.

### INCONCLUSIVE

Use `INCONCLUSIVE` only when a gate genuinely cannot be exercised on the available machine. Do not use it to avoid recording a failure.

## 15. Spike preservation rule

The spike is evidence, not automatically production code.

If Qt is approved, the subsequent V0-B implementation plan may reuse small proven pieces, but it must deliberately decide what graduates from the spike.

If Qt is rejected, preserve the spike branch/report long enough to document why, then begin a separate WPF feasibility decision rather than layering multiple frameworks into the same experiment.

## 16. Success outcome

A successful spike ends with Nolan being able to run a command on Windows 11 and see the first genuine Digital Garden desktop artifact:

```text
compact vine anchor
       |
      click
       v
transparent attached garden surface
       |
       +-- placeholder bonsai
       +-- real Garden World condition
       +-- one diagnostic WATER action
```

The visual quality is intentionally primitive. The milestone is proving that the physical desktop interaction model works and that Qt is a sound foundation for the real V0-B artifact.
