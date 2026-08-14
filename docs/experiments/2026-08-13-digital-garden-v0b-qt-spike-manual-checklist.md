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
observation. Record `DIGITAL_GARDEN_SPIKE_DISPLAY` exactly as printed by the
application for Gate H. The entries below preserve Nolan's pre-remediation
observations; replace them only with a fresh manual retest observation.

| Gate | Manual Windows check | Status | Observation |
| --- | --- | --- | --- |
| A Transparency | No opaque rectangle; desktop/app visible through transparent region. | FAIL | Transparency itself works, but the expanded garden is enclosed by a large opaque/dark rounded background instead of behaving as an organic transparent desktop artifact. |
| B Frameless | No title bar or normal border. | PASS | Frameless; no standard Windows chrome observed. |
| C Persistent anchor | Stays above ordinary apps and remains compact. | PASS | Persistent compact anchor behaved correctly above ordinary applications. |
| D Expansion | Single click expands adjacent patch; `COLLAPSE` returns to vine. | PASS | Single-click expansion and explicit `COLLAPSE` worked. |
| E Input integrity | Transparent/non-artifact area lets underlying app receive click; visible control receives artifact click. | NOT TESTED | The prior observation concerned visual transparency, not the required underlying-application click-through test. Re-evaluate after the Gate A repair. |
| F Outside dismissal | Clicking another ordinary app dismisses expanded patch without breaking that app interaction. | FAIL | Interacting with another application did not automatically dismiss the expanded garden; explicit `COLLAPSE` was required. |
| G Focus | Collapsed vine does not retain keyboard focus; expanded interaction is predictable; collapse returns to unobtrusive behavior. | PASS | Focus behavior was acceptable. |
| H DPI/display | Record `DIGITAL_GARDEN_SPIKE_DISPLAY` output; artifact remains visible/usable at current scaling; second-monitor movement is tested when available, otherwise `NOT TESTED`. | PASS | Provisional: artifact worked on all available screens. Capture `DIGITAL_GARDEN_SPIKE_DISPLAY` again during the next manual run. |
| I GardenService | Real `anchor_state`/`condition` visible; `WATER` routes through `GardenService` and refreshes without direct state mutation. | NOT TESTED | Real anchor/condition state was visible and `WATER` could be clicked, but its effect was not visible enough to determine manually whether it worked. |

## Remediation retest focus

- Gate A: verify that the desktop/application remains visible between the
  label plaque, bonsai, ground, and controls; there must be no full-surface
  dark rounded panel.
- Gate E: perform the deferred transparent-region click-through check after
  the shaped mask repair.
- Gate F: click Chrome, VS Code, or Explorer while the patch is expanded;
  the patch should collapse while the selected application receives that same
  click.
- Gate H: record the fresh `DIGITAL_GARDEN_SPIKE_DISPLAY` line during this
  run, including any available-screen observation.
- Gate I: confirm `SOIL: 0.55` changes to `SOIL: 0.80` after `WATER` for the
  seed-7 initial state.

Do not approve or reject Qt from automated evidence. If a load-bearing behavior
fails, preserve the branch and observations, then stop; any fallback experiment
requires a separate explicit human decision.
