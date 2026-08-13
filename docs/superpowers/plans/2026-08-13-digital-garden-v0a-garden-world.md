# Digital Garden V0-A Garden World Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the deterministic, persistent, fully headless Garden World that owns time, weather, soil, bonsai condition, surrounding growth, user actions, derived health, persistence, observability, and an append-only experience ledger.

**Architecture:** V0-A is a pure Python domain engine with immutable state transitions. The engine receives an authoritative `GardenState` plus a tick or legitimate action and returns a new `GardenState`; rendering is absent and cannot mutate world truth. Persistence, the experience ledger, and the future neural observation vector sit at the boundary of the engine rather than inside its biological rules.

**Tech Stack:** Python 3.12+, standard library only at runtime, `uv` for environment/project management, `pytest` for tests, `ruff` for lint/format, Windows 11 as the target product platform.

## Global Constraints

- Target platform: Windows 11 desktop.
- `24` logical ticks equal `1` garden day.
- Production mapping: `1` logical garden-hour tick equals `1` elapsed real hour.
- Weather states are exactly `SUNNY`, `CLOUDY`, and `RAINY`.
- Healthy soil-moisture band is exactly `0.40–0.70` inclusive.
- Biological/environmental values are normalized to `0.0–1.0`.
- The bonsai has no terminal death state and must remain recoverable.
- V0 user-facing actions are `WATER`, `TRIM`, `PRUNE`, and `INSPECT`.
- The future controller action surface also reserves `LEAVE_ALONE`.
- No neural network, reinforcement-learning, LLM, real-weather API, GUI, notification, currency, inventory, achievement, social, arbitrary-planting, or procedural-3D dependency enters V0-A.
- Same initial state + seed + ordered actions + elapsed ticks must produce exactly the same final state.
- Accelerated simulation must call the same one-tick world transition used by real-time execution.
- The Garden World is authoritative; future intelligence may request actions but may not directly set weather, moisture, health, stress, growth, or derived reward/health values.

## Plan Boundary

This plan implements **V0-A only**. The transparent vine anchor, expandable garden patch, bonsai artwork, animation, Windows window behavior, and input surface are intentionally deferred to a separate **V0-B Desktop Artifact implementation plan** after V0-A has a preserved acceptance baseline.

## File Structure

```text
pyproject.toml
README.md
src/digital_garden/
    __init__.py
    config.py          # Explicit V0 simulation constants
    domain.py          # Enums and immutable authoritative state types
    weather.py         # Deterministic weather transition and environment mapping
    derived.py         # Moisture fitness, overgrowth, garden condition, anchor state
    engine.py          # One-tick and multi-tick authoritative world transitions
    actions.py         # Legitimate user/controller action transitions
    observation.py     # Full snapshot serialization and fixed 12-value brain vector
    persistence.py     # Versioned JSON save/load and elapsed-time replay
    ledger.py          # Append-only JSONL experience ledger
    service.py         # Stable orchestration boundary for UI/CLI/future controllers
    cli.py             # Headless accelerated simulation entry point
tests/
    test_domain.py
    test_weather.py
    test_engine.py
    test_derived.py
    test_actions.py
    test_observation.py
    test_persistence.py
    test_ledger.py
    test_service.py
    test_cli.py
    test_acceptance.py
```

## Locked V0-A Constants

These values are the initial deterministic simulation contract. They are deliberately simple and may be tuned only through a later explicit experiment/change, not silently during implementation.

```python
# Initial state
INITIAL_SOIL_MOISTURE = 0.55
INITIAL_BONSAI_HEALTH = 0.85
INITIAL_BONSAI_STRESS = 0.10
INITIAL_BONSAI_GROWTH = 0.20
INITIAL_CANOPY_DENSITY = 0.50
INITIAL_GROUND_DENSITY = 0.35
INITIAL_VINE_EXTENT = 0.20
INITIAL_WEATHER = "CLOUDY"

# Weather -> (light, humidity, soil delta per tick)
SUNNY_ENV = (0.90, 0.30, -0.008)
CLOUDY_ENV = (0.55, 0.55, -0.004)
RAINY_ENV = (0.25, 0.90, +0.014)

# Daily Markov transition probabilities
SUNNY_TRANSITIONS = {"SUNNY": 0.60, "CLOUDY": 0.30, "RAINY": 0.10}
CLOUDY_TRANSITIONS = {"SUNNY": 0.30, "CLOUDY": 0.45, "RAINY": 0.25}
RAINY_TRANSITIONS = {"SUNNY": 0.10, "CLOUDY": 0.55, "RAINY": 0.35}

# Actions
WATER_AMOUNT = 0.25
TRIM_GROUND_AMOUNT = 0.20
TRIM_VINE_AMOUNT = 0.15
PRUNE_CANOPY_AMOUNT = 0.18
PRUNE_STRESS_COST = 0.08

# Biological rules
BONSAI_HEALTH_FLOOR = 0.15
DRY_STRESS_BASE = 0.012
WET_STRESS_BASE = 0.012
MOISTURE_STRESS_SCALE = 0.040
CANOPY_STRESS_DELTA = 0.006
HEALTHY_STRESS_RECOVERY = 0.008
HEALTH_GAIN_PER_TICK = 0.0015
HEALTH_LOSS_STRESSED = 0.0020
HEALTH_LOSS_SEVERE = 0.0040
BONSAI_GROWTH_PER_TICK = 0.0004
CANOPY_GROWTH_PER_TICK = 0.0006
GROUND_GROWTH_PER_TICK = 0.0007
VINE_GROWTH_PER_TICK = 0.0005
```

---

### Task 1: Repository scaffold and authoritative state contracts

**Files:**
- Create: `pyproject.toml`
- Create: `src/digital_garden/__init__.py`
- Create: `src/digital_garden/config.py`
- Create: `src/digital_garden/domain.py`
- Create: `tests/test_domain.py`

**Interfaces:**
- Produces: `Weather`, `GardenCondition`, `AnchorState`, `GardenAction`, `ActionSource` enums.
- Produces: frozen dataclasses `SoilState`, `BonsaiState`, `GroundState`, `VineState`, `GardenState`.
- Produces: `make_initial_state(seed: int) -> GardenState`.
- Produces: `clamp01(value: float) -> float`.

- [ ] **Step 1: Create the failing domain test**

```python
# tests/test_domain.py
from digital_garden.domain import Weather, make_initial_state


def test_initial_state_is_normalized_and_repeatable() -> None:
    first = make_initial_state(seed=7)
    second = make_initial_state(seed=7)

    assert first == second
    assert first.seed == 7
    assert first.tick == 0
    assert first.day_index == 0
    assert first.hour_of_day == 0
    assert first.weather is Weather.CLOUDY
    assert first.soil.moisture == 0.55
    assert first.bonsai.health == 0.85
    assert first.bonsai.stress == 0.10
    assert first.bonsai.growth == 0.20
    assert first.bonsai.canopy_density == 0.50
    assert first.ground.density == 0.35
    assert first.vine.extent == 0.20
```

- [ ] **Step 2: Run the test and verify RED**

Run:

```powershell
uv run pytest tests/test_domain.py -q
```

Expected: collection/import failure because `digital_garden.domain` does not exist yet.

- [ ] **Step 3: Add the minimal Python project scaffold**

`pyproject.toml`:

```toml
[project]
name = "digital-garden"
version = "0.1.0"
description = "A living desktop garden artifact and deterministic learning environment."
requires-python = ">=3.12"
dependencies = []

[dependency-groups]
dev = [
  "pytest>=9.0",
  "ruff>=0.16",
]

[project.scripts]
digital-garden = "digital_garden.cli:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/digital_garden"]

[tool.pytest.ini_options]
pythonpath = ["src"]
testpaths = ["tests"]

[tool.ruff]
target-version = "py312"
line-length = 100
```

- [ ] **Step 4: Implement the locked constants and immutable state types**

`src/digital_garden/config.py` must define the constants from **Locked V0-A Constants** plus:

```python
MOISTURE_HEALTHY_MIN = 0.40
MOISTURE_HEALTHY_MAX = 0.70
TICKS_PER_DAY = 24
SECONDS_PER_REAL_TICK = 3600
SCHEMA_VERSION = 1
```

`src/digital_garden/domain.py` must define:

```python
from dataclasses import dataclass
from enum import StrEnum

from digital_garden import config


class Weather(StrEnum):
    SUNNY = "SUNNY"
    CLOUDY = "CLOUDY"
    RAINY = "RAINY"


class GardenCondition(StrEnum):
    THRIVING = "THRIVING"
    HEALTHY = "HEALTHY"
    WILD = "WILD"
    STRESSED = "STRESSED"
    STRUGGLING = "STRUGGLING"


class AnchorState(StrEnum):
    CALM = "CALM"
    DRY = "DRY"
    WILD = "WILD"
    THRIVING = "THRIVING"
    STRESSED = "STRESSED"


class GardenAction(StrEnum):
    LEAVE_ALONE = "LEAVE_ALONE"
    WATER = "WATER"
    TRIM = "TRIM"
    PRUNE = "PRUNE"
    INSPECT = "INSPECT"


class ActionSource(StrEnum):
    USER = "USER"
    SYSTEM = "SYSTEM"
    EXPERT = "EXPERT"
    BRAIN = "BRAIN"


@dataclass(frozen=True)
class SoilState:
    moisture: float


@dataclass(frozen=True)
class BonsaiState:
    health: float
    stress: float
    growth: float
    canopy_density: float


@dataclass(frozen=True)
class GroundState:
    density: float


@dataclass(frozen=True)
class VineState:
    extent: float


@dataclass(frozen=True)
class GardenState:
    seed: int
    tick: int
    day_index: int
    hour_of_day: int
    weather: Weather
    light_level: float
    humidity: float
    soil: SoilState
    bonsai: BonsaiState
    ground: GroundState
    vine: VineState


def clamp01(value: float) -> float:
    return min(1.0, max(0.0, value))


def make_initial_state(seed: int) -> GardenState:
    return GardenState(
        seed=seed,
        tick=0,
        day_index=0,
        hour_of_day=0,
        weather=Weather.CLOUDY,
        light_level=0.55,
        humidity=0.55,
        soil=SoilState(config.INITIAL_SOIL_MOISTURE),
        bonsai=BonsaiState(
            health=config.INITIAL_BONSAI_HEALTH,
            stress=config.INITIAL_BONSAI_STRESS,
            growth=config.INITIAL_BONSAI_GROWTH,
            canopy_density=config.INITIAL_CANOPY_DENSITY,
        ),
        ground=GroundState(config.INITIAL_GROUND_DENSITY),
        vine=VineState(config.INITIAL_VINE_EXTENT),
    )
```

- [ ] **Step 5: Run domain tests and quality gates**

```powershell
uv sync
uv run pytest tests/test_domain.py -q
uv run ruff check .
uv run ruff format --check .
```

Expected: all commands exit `0`.

- [ ] **Step 6: Commit the scaffold/state contract**

```powershell
git add pyproject.toml src tests/test_domain.py
git commit -m "feat: define Digital Garden world state"
```

---

### Task 2: Deterministic weather and logical clock

**Files:**
- Create: `src/digital_garden/weather.py`
- Create: `tests/test_weather.py`

**Interfaces:**
- Consumes: `Weather`, `GardenState`, `clamp01`, config constants.
- Produces: `environment_for(weather: Weather) -> tuple[float, float, float]` returning `(light, humidity, soil_delta)`.
- Produces: `next_weather(seed: int, day_index: int, previous: Weather) -> Weather`.
- Produces: `advance_clock_and_weather(state: GardenState) -> GardenState`.

- [ ] **Step 1: Write deterministic weather tests**

```python
# tests/test_weather.py
from digital_garden.domain import Weather, make_initial_state
from digital_garden.weather import advance_clock_and_weather, next_weather


def test_seed_7_weather_sequence_is_stable() -> None:
    weather = Weather.CLOUDY
    observed = []
    for day in range(1, 11):
        weather = next_weather(7, day, weather)
        observed.append(weather)

    assert observed == [
        Weather.CLOUDY,
        Weather.RAINY,
        Weather.RAINY,
        Weather.CLOUDY,
        Weather.SUNNY,
        Weather.SUNNY,
        Weather.CLOUDY,
        Weather.SUNNY,
        Weather.CLOUDY,
        Weather.CLOUDY,
    ]


def test_weather_changes_only_at_day_boundary() -> None:
    state = make_initial_state(seed=7)
    for _ in range(23):
        state = advance_clock_and_weather(state)
        assert state.weather is Weather.CLOUDY

    state = advance_clock_and_weather(state)
    assert state.tick == 24
    assert state.day_index == 1
    assert state.hour_of_day == 0
    assert state.weather is Weather.CLOUDY
```

- [ ] **Step 2: Run and verify RED**

```powershell
uv run pytest tests/test_weather.py -q
```

Expected: import failure for `digital_garden.weather`.

- [ ] **Step 3: Implement stable hash-based weather selection**

`src/digital_garden/weather.py`:

```python
import hashlib
from dataclasses import replace

from digital_garden.domain import GardenState, Weather

_TRANSITIONS = {
    Weather.SUNNY: ((Weather.SUNNY, 0.60), (Weather.CLOUDY, 0.30), (Weather.RAINY, 0.10)),
    Weather.CLOUDY: ((Weather.SUNNY, 0.30), (Weather.CLOUDY, 0.45), (Weather.RAINY, 0.25)),
    Weather.RAINY: ((Weather.SUNNY, 0.10), (Weather.CLOUDY, 0.55), (Weather.RAINY, 0.35)),
}

_ENVIRONMENT = {
    Weather.SUNNY: (0.90, 0.30, -0.008),
    Weather.CLOUDY: (0.55, 0.55, -0.004),
    Weather.RAINY: (0.25, 0.90, 0.014),
}


def environment_for(weather: Weather) -> tuple[float, float, float]:
    return _ENVIRONMENT[weather]


def _roll(seed: int, day_index: int, previous: Weather) -> float:
    payload = f"{seed}:{day_index}:{previous.value}".encode()
    integer = int.from_bytes(hashlib.blake2b(payload, digest_size=8).digest(), "big")
    return integer / ((1 << 64) - 1)


def next_weather(seed: int, day_index: int, previous: Weather) -> Weather:
    roll = _roll(seed, day_index, previous)
    cumulative = 0.0
    for weather, probability in _TRANSITIONS[previous]:
        cumulative += probability
        if roll < cumulative:
            return weather
    return _TRANSITIONS[previous][-1][0]


def advance_clock_and_weather(state: GardenState) -> GardenState:
    tick = state.tick + 1
    hour = (state.hour_of_day + 1) % 24
    day = state.day_index + (1 if hour == 0 else 0)
    weather = next_weather(state.seed, day, state.weather) if hour == 0 else state.weather
    light, humidity, _ = environment_for(weather)
    return replace(
        state,
        tick=tick,
        day_index=day,
        hour_of_day=hour,
        weather=weather,
        light_level=light,
        humidity=humidity,
    )
```

- [ ] **Step 4: Run tests and quality gates**

```powershell
uv run pytest tests/test_weather.py -q
uv run ruff check .
uv run ruff format --check .
```

Expected: all commands exit `0`.

- [ ] **Step 5: Commit**

```powershell
git add src/digital_garden/weather.py tests/test_weather.py
git commit -m "feat: add deterministic garden weather"
```

---

### Task 3: Soil and bonsai one-tick dynamics

**Files:**
- Create: `src/digital_garden/engine.py`
- Create: `tests/test_engine.py`

**Interfaces:**
- Consumes: authoritative state and weather environment mapping.
- Produces: `advance_one_tick(state: GardenState) -> GardenState`.
- Produces: `advance_ticks(state: GardenState, count: int) -> GardenState`.

- [ ] **Step 1: Write failing dynamics tests**

```python
# tests/test_engine.py
from dataclasses import replace

from digital_garden.domain import BonsaiState, SoilState, make_initial_state
from digital_garden.engine import advance_one_tick, advance_ticks


def test_sunny_or_cloudy_time_dries_soil() -> None:
    state = make_initial_state(seed=7)
    later = advance_one_tick(state)
    assert later.soil.moisture < state.soil.moisture


def test_dryness_increases_stress() -> None:
    state = make_initial_state(seed=7)
    state = replace(state, soil=SoilState(0.10))
    later = advance_one_tick(state)
    assert later.bonsai.stress > state.bonsai.stress


def test_excess_water_increases_stress() -> None:
    state = make_initial_state(seed=7)
    state = replace(state, soil=SoilState(0.95))
    later = advance_one_tick(state)
    assert later.bonsai.stress > state.bonsai.stress


def test_healthy_moisture_recovers_stress() -> None:
    state = make_initial_state(seed=7)
    state = replace(
        state,
        bonsai=BonsaiState(
            health=0.80,
            stress=0.30,
            growth=0.20,
            canopy_density=0.50,
        ),
    )
    later = advance_one_tick(state)
    assert later.bonsai.stress < state.bonsai.stress


def test_bonsai_never_crosses_health_floor() -> None:
    state = make_initial_state(seed=7)
    state = replace(
        state,
        soil=SoilState(0.0),
        bonsai=replace(state.bonsai, health=0.151, stress=1.0),
    )
    later = advance_ticks(state, 1000)
    assert later.bonsai.health >= 0.15
```

- [ ] **Step 2: Run and verify RED**

```powershell
uv run pytest tests/test_engine.py -q
```

Expected: import failure for `digital_garden.engine`.

- [ ] **Step 3: Implement the minimal biological transition**

`advance_one_tick()` must execute in this order:

```text
1. advance logical clock/weather
2. apply weather soil delta and clamp moisture
3. calculate moisture stress
4. add canopy stress when canopy < 0.25 or > 0.80
5. recover stress by 0.008 only when moisture is inside 0.40–0.70 and canopy is 0.25–0.80
6. update health with floor 0.15
7. update long-term bonsai growth only when health > 0.60, stress < 0.35, and moisture is healthy
8. update canopy, ground, and vine growth
9. return a new immutable GardenState
```

Use these exact stress/health rules:

```python
if moisture < 0.40:
    stress_delta = 0.012 + (0.40 - moisture) * 0.040
elif moisture > 0.70:
    stress_delta = 0.012 + (moisture - 0.70) * 0.040
else:
    stress_delta = -0.008

if canopy < 0.25 or canopy > 0.80:
    stress_delta += 0.006

if stress >= 0.75:
    health_delta = -0.004
elif stress >= 0.50:
    health_delta = -0.002
elif stress <= 0.20 and 0.40 <= moisture <= 0.70:
    health_delta = 0.0015
else:
    health_delta = 0.0
```

Growth rules:

```python
favorable = health > 0.60 and stress < 0.35 and 0.40 <= moisture <= 0.70
bonsai_growth_delta = 0.0004 if favorable else 0.0
canopy_delta = 0.0006 if health > 0.50 else 0.0
ground_delta = 0.0007 * (0.5 + humidity)
vine_delta = 0.0005 * (0.5 + humidity)
```

`advance_ticks()` must reject negative counts with `ValueError` and implement acceleration only as repeated calls to `advance_one_tick()`.

- [ ] **Step 4: Run engine tests and full suite**

```powershell
uv run pytest tests/test_engine.py -q
uv run pytest -q
uv run ruff check .
uv run ruff format --check .
```

Expected: all commands exit `0`.

- [ ] **Step 5: Commit**

```powershell
git add src/digital_garden/engine.py tests/test_engine.py
git commit -m "feat: add deterministic garden dynamics"
```

---

### Task 4: Derived garden health, wildness, condition, and anchor state

**Files:**
- Create: `src/digital_garden/derived.py`
- Create: `tests/test_derived.py`

**Interfaces:**
- Produces: frozen `DerivedGardenState(garden_health, overgrowth, condition, anchor_state)`.
- Produces: `moisture_fitness(moisture: float) -> float`.
- Produces: `derive_garden_state(state: GardenState) -> DerivedGardenState`.

- [ ] **Step 1: Write failing derived-state tests**

```python
# tests/test_derived.py
from dataclasses import replace

from digital_garden.derived import derive_garden_state, moisture_fitness
from digital_garden.domain import AnchorState, GardenCondition, GroundState, VineState, make_initial_state


def test_moisture_fitness_is_one_inside_healthy_band() -> None:
    assert moisture_fitness(0.40) == 1.0
    assert moisture_fitness(0.55) == 1.0
    assert moisture_fitness(0.70) == 1.0


def test_wild_garden_can_still_be_healthy() -> None:
    state = make_initial_state(seed=7)
    state = replace(state, ground=GroundState(1.0), vine=VineState(1.0))
    derived = derive_garden_state(state)
    assert derived.condition is GardenCondition.WILD
    assert derived.garden_health >= 0.65
    assert derived.anchor_state is AnchorState.WILD


def test_dry_anchor_has_priority_for_dry_garden() -> None:
    state = make_initial_state(seed=7)
    state = replace(state, soil=replace(state.soil, moisture=0.20))
    assert derive_garden_state(state).anchor_state is AnchorState.DRY
```

- [ ] **Step 2: Run and verify RED**

```powershell
uv run pytest tests/test_derived.py -q
```

- [ ] **Step 3: Implement the exact derived formulas**

Use:

```python
canopy_pressure = clamp01((canopy_density - 0.60) / 0.40)
overgrowth = clamp01(
    0.40 * canopy_pressure
    + 0.30 * ground_density
    + 0.30 * vine_extent
)

if moisture < 0.40:
    moisture_fitness = moisture / 0.40
elif moisture <= 0.70:
    moisture_fitness = 1.0
else:
    moisture_fitness = (1.0 - moisture) / 0.30

manageable_growth = 1.0 if overgrowth <= 0.60 else 1.0 - ((overgrowth - 0.60) / 0.40)
garden_health = clamp01(
    0.65 * bonsai_health
    + 0.20 * clamp01(moisture_fitness)
    + 0.15 * clamp01(manageable_growth)
)
```

Condition precedence must be exactly:

```python
if bonsai_health <= 0.35 or bonsai_stress >= 0.80:
    STRUGGLING
elif bonsai_health < 0.65 or bonsai_stress >= 0.50 or moisture < 0.25 or moisture > 0.85:
    STRESSED
elif bonsai_health >= 0.90 and bonsai_stress <= 0.15 and moisture_fitness >= 0.90 and overgrowth <= 0.45:
    THRIVING
elif overgrowth >= 0.60 and garden_health >= 0.65:
    WILD
else:
    HEALTHY
```

Anchor precedence must be exactly:

```python
if moisture < 0.30:
    DRY
elif condition in {STRESSED, STRUGGLING}:
    STRESSED
elif condition is THRIVING:
    THRIVING
elif condition is WILD:
    WILD
else:
    CALM
```

- [ ] **Step 4: Verify**

```powershell
uv run pytest tests/test_derived.py -q
uv run pytest -q
uv run ruff check .
uv run ruff format --check .
```

- [ ] **Step 5: Commit**

```powershell
git add src/digital_garden/derived.py tests/test_derived.py
git commit -m "feat: derive garden health and wildness"
```

---

### Task 5: Legitimate garden actions

**Files:**
- Create: `src/digital_garden/actions.py`
- Create: `tests/test_actions.py`

**Interfaces:**
- Produces: `apply_action(state: GardenState, action: GardenAction) -> GardenState`.

- [ ] **Step 1: Write failing action tests**

```python
# tests/test_actions.py
from digital_garden.actions import apply_action
from digital_garden.domain import GardenAction, make_initial_state


def test_water_only_raises_soil_moisture() -> None:
    state = make_initial_state(seed=7)
    changed = apply_action(state, GardenAction.WATER)
    assert changed.soil.moisture == 0.80
    assert changed.bonsai == state.bonsai
    assert changed.ground == state.ground
    assert changed.vine == state.vine


def test_trim_does_not_touch_bonsai_canopy() -> None:
    state = make_initial_state(seed=7)
    changed = apply_action(state, GardenAction.TRIM)
    assert changed.ground.density == 0.15
    assert changed.vine.extent == 0.05
    assert changed.bonsai.canopy_density == state.bonsai.canopy_density


def test_prune_reduces_canopy_and_costs_stress() -> None:
    state = make_initial_state(seed=7)
    changed = apply_action(state, GardenAction.PRUNE)
    assert changed.bonsai.canopy_density == 0.32
    assert changed.bonsai.stress == 0.18


def test_inspect_and_leave_alone_do_not_mutate_world() -> None:
    state = make_initial_state(seed=7)
    assert apply_action(state, GardenAction.INSPECT) == state
    assert apply_action(state, GardenAction.LEAVE_ALONE) == state
```

- [ ] **Step 2: Run and verify RED**

```powershell
uv run pytest tests/test_actions.py -q
```

- [ ] **Step 3: Implement action transitions**

`apply_action()` must use `dataclasses.replace`, `clamp01`, and only these effects:

```text
WATER       soil.moisture += 0.25
TRIM        ground.density -= 0.20; vine.extent -= 0.15
PRUNE       canopy_density -= 0.18; bonsai.stress += 0.08
INSPECT     no mutation
LEAVE_ALONE no mutation
```

All resulting normalized values must be clamped to `0.0–1.0`.

- [ ] **Step 4: Verify and commit**

```powershell
uv run pytest tests/test_actions.py -q
uv run pytest -q
uv run ruff check .
uv run ruff format --check .
git add src/digital_garden/actions.py tests/test_actions.py
git commit -m "feat: add controlled garden actions"
```

---

### Task 6: Stable machine observation and full snapshot serialization

**Files:**
- Create: `src/digital_garden/observation.py`
- Create: `tests/test_observation.py`

**Interfaces:**
- Produces: `observation_vector(state: GardenState) -> tuple[float, ...]` with exactly 12 values.
- Produces: `state_to_dict(state: GardenState) -> dict[str, object]`.
- Produces: `state_from_dict(payload: dict[str, object]) -> GardenState`.
- Produces: `inspection_snapshot(state: GardenState) -> dict[str, object]` including derived human-facing state.

- [ ] **Step 1: Write failing observation tests**

```python
# tests/test_observation.py
from digital_garden.domain import make_initial_state
from digital_garden.observation import observation_vector, state_from_dict, state_to_dict


def test_brain_observation_has_fixed_order_and_length() -> None:
    state = make_initial_state(seed=7)
    vector = observation_vector(state)
    assert vector == (
        0.55,
        0.85,
        0.10,
        0.20,
        0.50,
        0.35,
        0.20,
        0.55,
        0.55,
        0.0,
        1.0,
        0.0,
    )
    assert len(vector) == 12


def test_state_serialization_round_trips_exactly() -> None:
    state = make_initial_state(seed=7)
    assert state_from_dict(state_to_dict(state)) == state
```

- [ ] **Step 2: Run and verify RED**

```powershell
uv run pytest tests/test_observation.py -q
```

- [ ] **Step 3: Implement the exact 12-value observation order**

The order is immutable for V0:

```text
0  soil_moisture
1  bonsai_health
2  bonsai_stress
3  bonsai_growth
4  canopy_density
5  ground_density
6  vine_extent
7  light_level
8  humidity
9  weather_sunny
10 weather_cloudy
11 weather_rainy
```

`state_to_dict()` must emit enum values as strings and nested state as ordinary JSON-compatible dictionaries. `state_from_dict()` must reconstruct the exact frozen dataclasses and reject unknown weather values through the `Weather(...)` enum constructor.

- [ ] **Step 4: Verify and commit**

```powershell
uv run pytest tests/test_observation.py -q
uv run pytest -q
uv run ruff check .
uv run ruff format --check .
git add src/digital_garden/observation.py tests/test_observation.py
git commit -m "feat: expose garden observations"
```

---

### Task 7: Versioned persistence and elapsed-time replay

**Files:**
- Create: `src/digital_garden/persistence.py`
- Create: `tests/test_persistence.py`

**Interfaces:**
- Produces: frozen `PersistedGarden(schema_version: int, last_processed_time: datetime, state: GardenState)`.
- Produces: `save_garden(path: Path, persisted: PersistedGarden) -> None`.
- Produces: `load_garden(path: Path) -> PersistedGarden`.
- Produces: `advance_elapsed(persisted: PersistedGarden, now: datetime) -> tuple[PersistedGarden, int]`.

- [ ] **Step 1: Write failing persistence tests**

```python
# tests/test_persistence.py
from datetime import UTC, datetime, timedelta

from digital_garden.domain import make_initial_state
from digital_garden.persistence import PersistedGarden, advance_elapsed, load_garden, save_garden


def test_persisted_state_round_trips(tmp_path) -> None:
    path = tmp_path / "garden-state.json"
    persisted = PersistedGarden(
        schema_version=1,
        last_processed_time=datetime(2026, 8, 13, 10, 0, tzinfo=UTC),
        state=make_initial_state(seed=7),
    )
    save_garden(path, persisted)
    assert load_garden(path) == persisted


def test_elapsed_time_uses_whole_real_hours_and_preserves_remainder() -> None:
    start = datetime(2026, 8, 13, 10, 0, tzinfo=UTC)
    persisted = PersistedGarden(1, start, make_initial_state(seed=7))
    resumed, processed = advance_elapsed(persisted, start + timedelta(hours=2, minutes=30))

    assert processed == 2
    assert resumed.state.tick == 2
    assert resumed.last_processed_time == start + timedelta(hours=2)


def test_clock_rollback_is_rejected() -> None:
    start = datetime(2026, 8, 13, 10, 0, tzinfo=UTC)
    persisted = PersistedGarden(1, start, make_initial_state(seed=7))
    try:
        advance_elapsed(persisted, start - timedelta(seconds=1))
    except ValueError as exc:
        assert "before last_processed_time" in str(exc)
    else:
        raise AssertionError("expected ValueError")
```

- [ ] **Step 2: Run and verify RED**

```powershell
uv run pytest tests/test_persistence.py -q
```

- [ ] **Step 3: Implement versioned JSON persistence**

Persist exactly this envelope shape:

```json
{
  "schema_version": 1,
  "last_processed_time": "2026-08-13T10:00:00+00:00",
  "state": {}
}
```

`save_garden()` must write UTF-8 JSON to a temporary sibling file and use `os.replace()` for atomic replacement. `load_garden()` must reject any `schema_version` other than `1` with `ValueError`.

`advance_elapsed()` must:

```python
elapsed_seconds = (now - persisted.last_processed_time).total_seconds()
processed_ticks = int(elapsed_seconds // 3600)
new_state = advance_ticks(persisted.state, processed_ticks)
new_last_processed = persisted.last_processed_time + timedelta(hours=processed_ticks)
```

Both datetimes must be timezone-aware. Naive datetimes are rejected with `ValueError`.

- [ ] **Step 4: Verify and commit**

```powershell
uv run pytest tests/test_persistence.py -q
uv run pytest -q
uv run ruff check .
uv run ruff format --check .
git add src/digital_garden/persistence.py tests/test_persistence.py
git commit -m "feat: persist and resume garden state"
```

---

### Task 8: Append-only experience ledger

**Files:**
- Create: `src/digital_garden/ledger.py`
- Create: `tests/test_ledger.py`

**Interfaces:**
- Produces: `LedgerAction` enum containing `LEAVE_ALONE`, `WATER`, `TRIM`, `PRUNE`, `INSPECT`, `WEATHER_CHANGE`.
- Produces: frozen `LedgerEvent(schema_version, tick, source, action, pre_state, post_state)`.
- Produces: `append_event(path: Path, event: LedgerEvent) -> None`.
- Produces: `read_events(path: Path) -> list[LedgerEvent]`.

- [ ] **Step 1: Write failing ledger test**

```python
# tests/test_ledger.py
from digital_garden.domain import ActionSource, make_initial_state
from digital_garden.ledger import LedgerAction, LedgerEvent, append_event, read_events


def test_jsonl_ledger_is_append_only_and_round_trips(tmp_path) -> None:
    path = tmp_path / "experience.jsonl"
    state = make_initial_state(seed=7)
    event = LedgerEvent(
        schema_version=1,
        tick=0,
        source=ActionSource.USER,
        action=LedgerAction.INSPECT,
        pre_state=state,
        post_state=state,
    )

    append_event(path, event)
    append_event(path, event)

    assert read_events(path) == [event, event]
    assert len(path.read_text(encoding="utf-8").splitlines()) == 2
```

- [ ] **Step 2: Run and verify RED**

```powershell
uv run pytest tests/test_ledger.py -q
```

- [ ] **Step 3: Implement one-JSON-object-per-line ledger storage**

Each line must contain:

```json
{
  "schema_version": 1,
  "tick": 0,
  "source": "USER",
  "action": "INSPECT",
  "pre_state": {},
  "post_state": {}
}
```

Use `state_to_dict()`/`state_from_dict()` rather than a second serialization implementation. Appending must open with `encoding="utf-8"` and mode `"a"`; never rewrite prior lines.

- [ ] **Step 4: Verify and commit**

```powershell
uv run pytest tests/test_ledger.py -q
uv run pytest -q
uv run ruff check .
uv run ruff format --check .
git add src/digital_garden/ledger.py tests/test_ledger.py
git commit -m "feat: record garden experience ledger"
```

---

### Task 9: Stable GardenService boundary for UI, CLI, and future brains

**Files:**
- Create: `src/digital_garden/service.py`
- Create: `tests/test_service.py`

**Interfaces:**
- Consumes: engine, actions, derived state, persistence, observation, ledger.
- Produces: `GardenService(state: GardenState, ledger_path: Path | None = None)`.
- Produces methods:
  - `snapshot() -> dict[str, object]`
  - `observation() -> tuple[float, ...]`
  - `apply(action: GardenAction, source: ActionSource = ActionSource.USER) -> GardenState`
  - `advance(count: int) -> GardenState`

- [ ] **Step 1: Write failing service integration tests**

```python
# tests/test_service.py
from digital_garden.domain import ActionSource, GardenAction, make_initial_state
from digital_garden.ledger import read_events
from digital_garden.service import GardenService


def test_user_action_is_applied_and_logged(tmp_path) -> None:
    ledger_path = tmp_path / "experience.jsonl"
    service = GardenService(make_initial_state(seed=7), ledger_path)

    service.apply(GardenAction.WATER, ActionSource.USER)

    assert service.state.soil.moisture == 0.80
    events = read_events(ledger_path)
    assert len(events) == 1
    assert events[0].action.value == "WATER"
    assert events[0].source is ActionSource.USER


def test_weather_change_is_logged_as_system_event(tmp_path) -> None:
    ledger_path = tmp_path / "experience.jsonl"
    service = GardenService(make_initial_state(seed=7), ledger_path)
    service.advance(48)

    events = read_events(ledger_path)
    weather_events = [event for event in events if event.action.value == "WEATHER_CHANGE"]
    assert len(weather_events) >= 1
    assert all(event.source is ActionSource.SYSTEM for event in weather_events)
```

- [ ] **Step 2: Run and verify RED**

```powershell
uv run pytest tests/test_service.py -q
```

- [ ] **Step 3: Implement the orchestration boundary**

`GardenService.apply()` must capture `pre_state`, call `apply_action()`, set `self.state`, and append exactly one ledger event when a ledger path exists. `INSPECT` is logged even though `pre_state == post_state`.

`GardenService.advance(count)` must loop exactly `count` calls to `advance_one_tick()`. On any tick where `pre_state.weather != post_state.weather`, append one `SYSTEM / WEATHER_CHANGE` event with the pre/post states. It must not log every ordinary tick.

`GardenService.snapshot()` returns `inspection_snapshot(self.state)`. `GardenService.observation()` returns the fixed 12-value tuple.

- [ ] **Step 4: Verify and commit**

```powershell
uv run pytest tests/test_service.py -q
uv run pytest -q
uv run ruff check .
uv run ruff format --check .
git add src/digital_garden/service.py tests/test_service.py
git commit -m "feat: add garden service boundary"
```

---

### Task 10: Headless accelerated simulation CLI

**Files:**
- Create: `src/digital_garden/cli.py`
- Create: `tests/test_cli.py`

**Interfaces:**
- Produces console command: `digital-garden simulate --seed <int> --ticks <int>`.
- Output: deterministic JSON summary to stdout.

- [ ] **Step 1: Write failing CLI test**

```python
# tests/test_cli.py
import json
import subprocess
import sys


def test_simulate_command_produces_machine_readable_summary() -> None:
    completed = subprocess.run(
        [sys.executable, "-m", "digital_garden.cli", "simulate", "--seed", "7", "--ticks", "48"],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(completed.stdout)
    assert payload["seed"] == 7
    assert payload["tick"] == 48
    assert payload["day_index"] == 2
    assert payload["observation_length"] == 12
    assert payload["condition"] in {"THRIVING", "HEALTHY", "WILD", "STRESSED", "STRUGGLING"}
```

- [ ] **Step 2: Run and verify RED**

```powershell
uv run pytest tests/test_cli.py -q
```

- [ ] **Step 3: Implement argparse CLI**

The CLI must use `argparse` only. For `simulate`:

```python
state = make_initial_state(args.seed)
service = GardenService(state)
service.advance(args.ticks)
snapshot = service.snapshot()
summary = {
    "seed": service.state.seed,
    "tick": service.state.tick,
    "day_index": service.state.day_index,
    "hour_of_day": service.state.hour_of_day,
    "weather": service.state.weather.value,
    "soil_moisture": service.state.soil.moisture,
    "bonsai_health": service.state.bonsai.health,
    "bonsai_stress": service.state.bonsai.stress,
    "overgrowth": snapshot["overgrowth"],
    "condition": snapshot["garden_condition"],
    "anchor_state": snapshot["anchor_state"],
    "observation_length": len(service.observation()),
}
print(json.dumps(summary, sort_keys=True))
```

Reject negative `--ticks` through `argparse` error handling or a clear `ValueError` converted to non-zero exit.

- [ ] **Step 4: Verify both module and installed command**

```powershell
uv run pytest tests/test_cli.py -q
uv run python -m digital_garden.cli simulate --seed 7 --ticks 240
uv run digital-garden simulate --seed 7 --ticks 240
uv run ruff check .
uv run ruff format --check .
```

The two simulation commands must print equivalent deterministic JSON payloads.

- [ ] **Step 5: Commit**

```powershell
git add src/digital_garden/cli.py tests/test_cli.py
git commit -m "feat: add headless garden simulation"
```

---

### Task 11: V0-A acceptance regression and documentation

**Files:**
- Create: `tests/test_acceptance.py`
- Modify: `README.md`

**Interfaces:**
- Validates the complete V0-A contract without adding new runtime behavior.

- [ ] **Step 1: Write the acceptance regression**

`tests/test_acceptance.py` must contain at minimum these checks:

```python
from dataclasses import replace

from digital_garden.actions import apply_action
from digital_garden.derived import derive_garden_state
from digital_garden.domain import GardenAction, SoilState, make_initial_state
from digital_garden.engine import advance_ticks
from digital_garden.observation import observation_vector


def test_same_seed_actions_and_ticks_reproduce_exact_state() -> None:
    def scenario():
        state = make_initial_state(seed=7)
        state = advance_ticks(state, 36)
        state = apply_action(state, GardenAction.WATER)
        state = advance_ticks(state, 72)
        state = apply_action(state, GardenAction.TRIM)
        state = advance_ticks(state, 120)
        state = apply_action(state, GardenAction.PRUNE)
        return advance_ticks(state, 48)

    assert scenario() == scenario()


def test_neglect_becomes_wilder_without_terminal_death() -> None:
    state = make_initial_state(seed=7)
    initial_overgrowth = derive_garden_state(state).overgrowth
    neglected = advance_ticks(state, 24 * 120)

    assert derive_garden_state(neglected).overgrowth > initial_overgrowth
    assert neglected.bonsai.health >= 0.15


def test_dry_and_wet_states_are_both_harmful() -> None:
    base = make_initial_state(seed=7)
    dry = advance_ticks(replace(base, soil=SoilState(0.05)), 24)
    wet = advance_ticks(replace(base, soil=SoilState(0.95)), 24)

    assert dry.bonsai.stress > base.bonsai.stress
    assert wet.bonsai.stress > base.bonsai.stress


def test_future_brain_surface_is_exactly_twelve_values() -> None:
    assert len(observation_vector(make_initial_state(seed=7))) == 12
```

If the 120-day neglect assertion exposes a legitimate constants issue, adjust only the locked simulation constant responsible for the failed intended behavior, document the numerical change in the commit message/body, and rerun the complete acceptance suite. Do not weaken the acceptance assertion to hide the problem.

- [ ] **Step 2: Run the complete verification gate**

```powershell
uv sync
uv run pytest -q
uv run ruff check .
uv run ruff format --check .
git diff --check
```

Expected: every command exits `0`.

- [ ] **Step 3: Update README with the actual V0-A operating contract**

README must document:

```text
Digital Garden purpose
V0-A vs V0-B boundary
Python 3.12+ / standard-library runtime
24 ticks = one garden day
1 real hour = one production tick
seeded deterministic weather
healthy moisture band 0.40–0.70
WATER / TRIM / PRUNE / INSPECT
no-death rule
12-value future Garden Brain observation
how to run tests
how to run `digital-garden simulate --seed 7 --ticks 240`
explicit statement that there is no GUI or learned intelligence in V0-A
```

- [ ] **Step 4: Re-run verification after documentation**

```powershell
uv run pytest -q
uv run ruff check .
uv run ruff format --check .
git diff --check
```

Expected: every command exits `0`.

- [ ] **Step 5: Commit V0-A acceptance baseline**

```powershell
git add README.md tests/test_acceptance.py
git commit -m "test: lock Digital Garden V0-A baseline"
```

---

## Final V0-A Acceptance Gate

Run from the repository/worktree root:

```powershell
Write-Host "=== DIGITAL GARDEN V0-A ACCEPTANCE ==="
git status --short
git branch --show-current
python --version
uv --version

Write-Host ""
Write-Host "=== SYNC ==="
uv sync

Write-Host ""
Write-Host "=== TESTS ==="
uv run pytest -q

Write-Host ""
Write-Host "=== RUFF CHECK ==="
uv run ruff check .

Write-Host ""
Write-Host "=== RUFF FORMAT ==="
uv run ruff format --check .

Write-Host ""
Write-Host "=== WHITESPACE ==="
git diff --check

Write-Host ""
Write-Host "=== DETERMINISTIC 10-DAY HEADLESS RUN ==="
uv run digital-garden simulate --seed 7 --ticks 240

Write-Host ""
Write-Host "=== FINAL TREE ==="
git status
```

Acceptance requires:

- test suite fully green;
- Ruff check and format green;
- `git diff --check` clean;
- deterministic headless command completes;
- output reports `tick = 240`, `day_index = 10`, and `observation_length = 12`;
- no GUI, neural, LLM, or network dependency has entered the project;
- working tree clean after the acceptance commit.

## Handoff to V0-B

Once this baseline is preserved, write the separate `V0-B Desktop Artifact` implementation plan. That plan begins with a static transparent Windows visual shell so the vine anchor and stylised bonsai become visible early, then binds the rendering layer to `GardenService` without moving authority out of the Garden World.
