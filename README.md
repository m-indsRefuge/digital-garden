# Digital Garden

Digital Garden is a local, deterministic garden world: a small bonsai, soil,
ground cover, vines, and weather evolve over discrete ticks. V0-A establishes
the authoritative headless Garden World and its testable operating contract.

## V0-A boundary

V0-A is the deterministic, standard-library Python runtime. It has no GUI,
learned intelligence, neural network, LLM, reinforcement learning, or network
dependency. It is deliberately headless so state transitions, persistence, and
future observations remain inspectable and reproducible.

V0-B is a separate future desktop-artifact phase. Its visual shell may render
Garden World state, but it must not move simulation authority out of the Garden
World.

## Operating contract

- Python 3.12+ with a standard-library runtime (development uses pytest and
  Ruff).
- 24 simulation ticks are one garden day; one real hour is one production tick.
- Weather is seeded and deterministic for a given state and seed.
- The healthy soil-moisture band is inclusive: 0.40–0.70.
- Available garden actions are `WATER`, `TRIM`, `PRUNE`, and `INSPECT`.
- The bonsai has a no-death rule: health is clamped to a non-terminal floor.
- A future Garden Brain observes exactly 12 numeric values; V0-A does not
  include that brain.

## Run it

Create the local development environment and run the tests:

```powershell
uv sync
uv run pytest -q
```

Run a deterministic 10-day headless simulation:

```powershell
uv run digital-garden simulate --seed 7 --ticks 240
```

The command prints a JSON summary, including the final tick, day index, and
12-value observation length.

## V0-B.1 production shell

PySide6/Qt 6 is the approved Windows desktop technology. V0-B.1 provides the
production desktop shell only; living garden rendering, Garden actions,
persisted Garden resume, and ambient animation remain later V0-B slices.

```powershell
uv run digital-garden-desktop
```
