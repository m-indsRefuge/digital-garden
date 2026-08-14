# Digital Garden V0-B-0 Qt Spike: Decision Report

Implementation status: READY_FOR_MANUAL_RETEST

Technology decision: INCONCLUSIVE — REMEDIATION REQUIRED

## Evidence boundary

The automated suite is supporting implementation evidence. It does not replace
Nolan's human Windows observations, which alone determine the manual acceptance
gates below. No manual success, Qt approval, or Qt rejection is claimed here.

## Manual gates: preserved pre-remediation evidence

| Gate | Status | Observation |
| --- | --- | --- |
| A Transparency | FAIL | Transparency itself works, but a large opaque/dark rounded background encloses the expanded garden instead of leaving an organic transparent desktop artifact. |
| B Frameless | PASS | Frameless; no standard Windows chrome observed. |
| C Persistent anchor | PASS | Persistent compact anchor behaved correctly above ordinary applications. |
| D Expansion | PASS | Single-click expansion and explicit `COLLAPSE` worked. |
| E Input integrity | NOT TESTED | Previous observation concerned visual transparency, not the required underlying-application click-through test. Re-evaluate after Gate A repair. |
| F Outside dismissal | FAIL | Interacting with another application did not automatically dismiss the expanded garden; explicit `COLLAPSE` was required. |
| G Focus | PASS | Focus behavior was acceptable. |
| H DPI/display | PASS | Provisional: artifact worked on all available screens. Capture `DIGITAL_GARDEN_SPIKE_DISPLAY` again during the next manual run. |
| I GardenService | NOT TESTED | Real anchor/condition state was visible and `WATER` could be clicked, but its effect was not visible enough to determine manually whether it worked. |

These are Nolan's recorded pre-remediation results. They remain evidence and
must not be upgraded from automated checks or code inspection. The next manual
run supplies the replacement Gate A-I observations.

## Remediation implemented

- Gate A: the patch no longer paints a full-window dark rounded rectangle.
  Its Qt mask now covers only the diagnostic label plaque, bonsai silhouette,
  ground, and visible controls, leaving the gaps between those elements
  transparent.
- Gate F: the patch now handles `QEvent.ActivationChange` only while it is
  visible and inactive, then emits its existing `collapse_requested` signal.
  This is pure Qt; it adds no global mouse hook, native Windows hook, or
  application-wide input interception.
- Gate I: `SOIL: <moisture>` is read from the authoritative
  `GardenService.snapshot()` state and refreshed after the existing
  `GardenService.apply(GardenAction.WATER)` path.

## Gate F investigation and hypothesis test

Temporary Qt diagnostics on Windows observed `ApplicationDeactivate`, raw
`WindowDeactivate`, and a patch `changeEvent()` value of `ActivationChange`
when the expanded patch lost interaction to another application. The previous
handler checked `WindowDeactivate` inside `changeEvent()`, so it never emitted
`collapse_requested` during that live path.

The focused regression uses a real second Qt window to make the patch inactive,
then verifies that the real activation transition emits the existing collapse
signal and hides the attached patch. The live Windows observation remains
authoritative for the final gate result.

## Exact Windows run command

Run `uv sync` first when dependencies need to be synchronized. The exact
artifact command is:

```powershell
uv run digital-garden-ui-spike
```

## Implemented pure-Qt approach

The spike uses frameless/translucent Tool windows, `QRegion` masks, Qt
deactivation dismissal, and direct `GardenService` binding. No non-Qt fallback
is part of this acceptance package.

## Stop gate

Record the Gate A-I observations in the manual checklist before making a
technology decision. A load-bearing Windows failure preserves the branch and
evidence, then stops; a separate fallback experiment requires an explicit human
decision.
