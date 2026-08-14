# Digital Garden V0-B-0 Qt Spike: Manual Windows Checklist

This checklist is the human acceptance gate for the PySide6 desktop artifact.
Automated checks provide supporting evidence only; Nolan's Windows observations
determine Gates A-I and must not be inferred from tests.

## Run

In PowerShell, from the repository root:

Run `uv sync` first when dependencies need to be synchronized. The exact
artifact command is:

```powershell
uv run digital-garden-ui-spike
```

For every gate, record `PASS`, `FAIL`, or `NOT TESTED`, followed by one concrete
observation.

## Final manual acceptance result

| Gate | Manual Windows check | Status | Observation |
| --- | --- | --- | --- |
| A Transparency | No opaque rectangle; desktop/app visible through transparent region. | PASS | Remediated organic patch is transparent between the diagnostic plaque, bonsai, ground, and controls; the previous full dark background is gone. |
| B Frameless | No title bar or normal border. | PASS | Frameless; no standard Windows chrome observed. |
| C Persistent anchor | Stays above ordinary apps and remains compact. | PASS | Persistent compact anchor behaved correctly above ordinary applications. |
| D Expansion | Single click expands adjacent patch; `COLLAPSE` returns to vine. | PASS | Single-click expansion and explicit `COLLAPSE` worked. |
| E Input integrity | Transparent/non-artifact area lets underlying app receive click; visible control receives artifact click. | PASS | Transparent gaps passed clicks through to the underlying application while visible artifact controls remained interactive. |
| F Outside dismissal | Clicking another ordinary app dismisses expanded patch without breaking that app interaction. | PASS | Clicking another ordinary application automatically dismissed the expanded patch after the `ActivationChange` remediation. |
| G Focus | Collapsed vine does not retain keyboard focus; expanded interaction is predictable; collapse returns to unobtrusive behavior. | PASS | Focus behavior was acceptable and normal work resumed cleanly after artifact interaction. |
| H DPI/display | Artifact remains visible/usable at current scaling and across available screens. | PASS | Artifact worked correctly across all available screens during the manual retest. The diagnostic output was observed as passing, but the exact `DIGITAL_GARDEN_SPIKE_DISPLAY` line was not retained in the chat record. |
| I GardenService | Real `anchor_state`/`condition` visible; `WATER` routes through `GardenService` and refreshes without direct state mutation. | PASS | Real Garden World state was visible and `SOIL` changed from `0.55` to `0.80` after `WATER`, confirming the visible service-backed action path. |

## Decision

All load-bearing manual Windows gates A-I passed after the scoped remediation.

```text
Technology decision: APPROVE QT
Approved desktop technology: PySide6 / Qt 6
```

The accepted path uses pure Qt: frameless/translucent Tool windows, shaped
`QRegion` masks, `ActivationChange`-based outside dismissal, and direct
`GardenService` binding. No native Windows fallback, global mouse hook, second
GUI framework, or application-wide input interception was required.

This closes the V0-B-0 technology spike. The spike branch remains evidence; the
full V0-B implementation should deliberately graduate only the proven
mechanisms rather than treating all prototype code as production code.
