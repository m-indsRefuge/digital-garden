# Digital Garden V0-B-0 Qt Spike: Decision Report

Implementation status: READY_FOR_MANUAL_ACCEPTANCE

Technology decision: INCONCLUSIVE — manual Windows gates not yet executed

## Evidence boundary

The automated suite is supporting implementation evidence. It does not replace
Nolan's human Windows observations, which alone determine the manual acceptance
gates below. No manual success, Qt approval, or Qt rejection is claimed here.

## Manual gates

| Gate | Status | Observation |
| --- | --- | --- |
| A Transparency | NOT TESTED | Awaiting manual Windows run. |
| B Frameless | NOT TESTED | Awaiting manual Windows run. |
| C Persistent anchor | NOT TESTED | Awaiting manual Windows run. |
| D Expansion | NOT TESTED | Awaiting manual Windows run. |
| E Input integrity | NOT TESTED | Awaiting manual Windows run. |
| F Outside dismissal | NOT TESTED | Awaiting manual Windows run. |
| G Focus | NOT TESTED | Awaiting manual Windows run. |
| H DPI/display | NOT TESTED | Awaiting manual Windows run. |
| I GardenService | NOT TESTED | Awaiting manual Windows run. |

## Exact Windows run command

```powershell
uv sync
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
