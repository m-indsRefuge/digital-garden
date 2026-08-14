# Digital Garden V0-B-0 Qt Spike: Decision Report

Implementation status: COMPLETE

Technology decision: APPROVE QT

Approved desktop technology: PySide6 / Qt 6

## Evidence boundary

The technology decision combines the completed automated spike verification with
Nolan's manual Windows acceptance observations. Automated checks support the
implementation evidence; the real desktop gates below were accepted only after
manual execution on the target Windows environment.

## Final manual gates

| Gate | Status | Observation |
| --- | --- | --- |
| A Transparency | PASS | Remediated organic patch is transparent between its actual visual elements; the previous full dark background is gone. |
| B Frameless | PASS | No title bar, border, or conventional Windows chrome observed. |
| C Persistent anchor | PASS | Compact vine anchor remained above ordinary applications. |
| D Expansion | PASS | Single-click expansion and explicit collapse worked. |
| E Input integrity | PASS | Transparent/non-artifact regions allowed underlying application interaction while visible controls remained interactive. |
| F Outside dismissal | PASS | Clicking another ordinary application dismissed the expanded patch after the pure-Qt activation-change remediation. |
| G Focus | PASS | Collapsed and expanded focus behavior remained unobtrusive and predictable. |
| H DPI/display | PASS | Artifact remained visible and usable across all available screens during manual retest. |
| I GardenService | PASS | Real Garden World state was shown; `SOIL` visibly changed from `0.55` to `0.80` after `WATER` through the service-backed action path. |

## Automated baseline

The final remediation campaign reported:

```text
PySide6: 6.11.1
67 tests passed
Ruff check passed
Ruff format check passed
git diff --check passed
canonical 240-tick V0-A simulation unchanged
```

Canonical V0-A output remained:

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

## Remediation evidence

The first manual run found three issues requiring remediation:

- the expanded garden was visually enclosed by a large dark background;
- outside interaction did not dismiss the patch;
- the `WATER` action lacked enough visible feedback for manual confirmation.

The scoped remediation resolved them without changing the Garden World:

- the patch mask now follows only the diagnostic plaque, bonsai silhouette,
  ground, and controls, leaving intervening regions transparent;
- root-cause investigation showed that the live Qt `changeEvent()` path exposes
  focus-loss through `ActivationChange`; the patch now collapses when it becomes
  inactive through that pure-Qt path;
- `SOIL: <moisture>` is read from the authoritative `GardenService.snapshot()`
  result and refreshed after the existing `GardenService.apply(GardenAction.WATER)`
  action path.

No native Windows hook, global mouse hook, application-wide input interception,
or second GUI framework was required.

## Approved architecture result

The spike proves the following production-relevant mechanisms on Windows 11:

```text
PySide6 / Qt
    |
    +-- frameless translucent Tool windows
    +-- shaped QRegion desktop artifacts
    +-- always-on-top compact anchor
    +-- click-to-expand attached patch
    +-- pure-Qt ActivationChange outside dismissal
    +-- multi-screen positioning
    +-- transparent-region input integrity
    +-- direct GardenService snapshot/action boundary
```

The Garden World remains authoritative. The successful spike does not authorize
direct UI mutation of Garden state or promotion of every prototype implementation
detail into production.

## Production graduation rule

V0-B should deliberately graduate the proven mechanisms above into a clean
production desktop package. Prototype artwork, diagnostic controls, temporary
layout choices, and spike-specific structure should be redesigned rather than
blindly merged as the final artifact.

## Final decision

```text
APPROVE QT
```

PySide6 / Qt 6 is approved as the Digital Garden V0-B desktop technology.
The V0-B-0 spike is complete and preserved as engineering evidence.
