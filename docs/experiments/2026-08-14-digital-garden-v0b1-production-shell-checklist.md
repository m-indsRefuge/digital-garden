# Digital Garden V0-B.1 Production Shell - Manual Acceptance

**Status:** NOT TESTED

## Run command

uv run digital-garden-desktop

## Manual acceptance gates

| Gate | Requirement | Status |
|---|---|---|
| S1 | Frameless/transparency - anchor and patch have no standard window chrome; transparent gaps remain transparent. | NOT TESTED |
| S2 | Persistent anchor - anchor remains above ordinary applications without taking unnecessary keyboard focus. | NOT TESTED |
| S3 | Expansion/collapse - one click on the anchor expands the patch; explicit COLLAPSE returns to the anchor. | NOT TESTED |
| S4 | Input integrity - transparent and non-artifact areas do not materially block input to underlying applications. | NOT TESTED |
| S5 | Outside dismissal - activating another application collapses the expanded patch back to the anchor. | NOT TESTED |
| S6 | Multi-screen placement - anchor and expanded patch remain inside usable screen geometry; the patch changes side when required. | NOT TESTED |
| S7 | Position persistence - after dragging the anchor, closing and relaunching restores its saved screen and position, clamped safely if display geometry changed. | NOT TESTED |
| S8 | Garden boundary/state display - CONDITION and WEATHER reflect GardenService state, and shell interaction does not mutate Garden state. | NOT TESTED |

## Acceptance rule

Do not mark V0-B.1 manually accepted until S1 through S8 have been directly
observed on Windows. Automated Qt tests supplement these gates but do not
replace manual desktop observation.
