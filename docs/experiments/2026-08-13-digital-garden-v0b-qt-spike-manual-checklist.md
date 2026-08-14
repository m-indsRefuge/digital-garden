# Digital Garden V0-B-0 Qt Spike: Manual Windows Checklist

This checklist is the human acceptance gate for the PySide6 desktop artifact.
Automated checks provide supporting evidence only; Nolan's Windows observations
determine Gates A-I and must not be inferred from tests.

## Run

In PowerShell, from the repository root:

```powershell
uv sync
uv run digital-garden-ui-spike
```

For every gate, record `PASS`, `FAIL`, or `NOT TESTED`, followed by one concrete
observation. Record `DIGITAL_GARDEN_SPIKE_DISPLAY` exactly as printed by the
application for Gate H.

| Gate | Manual Windows check | Status | Observation |
| --- | --- | --- | --- |
| A Transparency | No opaque rectangle; desktop/app visible through transparent region. | NOT TESTED | Awaiting manual Windows run. |
| B Frameless | No title bar or normal border. | NOT TESTED | Awaiting manual Windows run. |
| C Persistent anchor | Stays above ordinary apps and remains compact. | NOT TESTED | Awaiting manual Windows run. |
| D Expansion | Single click expands adjacent patch; `COLLAPSE` returns to vine. | NOT TESTED | Awaiting manual Windows run. |
| E Input integrity | Transparent/non-artifact area lets underlying app receive click; visible control receives artifact click. | NOT TESTED | Awaiting manual Windows run. |
| F Outside dismissal | Clicking another ordinary app dismisses expanded patch without breaking that app interaction. | NOT TESTED | Awaiting manual Windows run. |
| G Focus | Collapsed vine does not retain keyboard focus; expanded interaction is predictable; collapse returns to unobtrusive behavior. | NOT TESTED | Awaiting manual Windows run. |
| H DPI/display | Record `DIGITAL_GARDEN_SPIKE_DISPLAY` output; artifact remains visible/usable at current scaling; second-monitor movement is tested when available, otherwise `NOT TESTED`. | NOT TESTED | Awaiting manual Windows run. |
| I GardenService | Real `anchor_state`/`condition` visible; `WATER` routes through `GardenService` and refreshes without direct state mutation. | NOT TESTED | Awaiting manual Windows run. |

Do not approve or reject Qt from automated evidence. If a load-bearing behavior
fails, preserve the branch and observations, then stop; any fallback experiment
requires a separate explicit human decision.
