from dataclasses import replace
from datetime import UTC, datetime, timedelta

import pytest

from digital_garden import config
from digital_garden.actions import apply_action
from digital_garden.derived import moisture_fitness
from digital_garden.domain import GardenAction, Weather, make_initial_state
from digital_garden.engine import advance_one_tick
from digital_garden.ledger import read_events
from digital_garden.persistence import PersistedGarden, advance_elapsed, load_garden, save_garden
from digital_garden.service import GardenService
from digital_garden.weather import advance_clock_and_weather, environment_for, next_weather


def test_water_action_observes_configured_amount(monkeypatch) -> None:
    monkeypatch.setattr(config, "WATER_AMOUNT", 0.10)

    changed = apply_action(make_initial_state(seed=7), GardenAction.WATER)

    assert changed.soil.moisture == pytest.approx(0.65)


def test_trim_action_observes_configured_amounts(monkeypatch) -> None:
    monkeypatch.setattr(config, "TRIM_GROUND_AMOUNT", 0.10)
    monkeypatch.setattr(config, "TRIM_VINE_AMOUNT", 0.05)

    changed = apply_action(make_initial_state(seed=7), GardenAction.TRIM)

    assert changed.ground.density == pytest.approx(0.25)
    assert changed.vine.extent == pytest.approx(0.15)


def test_prune_action_observes_configured_amounts(monkeypatch) -> None:
    monkeypatch.setattr(config, "PRUNE_CANOPY_AMOUNT", 0.10)
    monkeypatch.setattr(config, "PRUNE_STRESS_COST", 0.02)

    changed = apply_action(make_initial_state(seed=7), GardenAction.PRUNE)

    assert changed.bonsai.canopy_density == pytest.approx(0.40)
    assert changed.bonsai.stress == pytest.approx(0.12)


def test_engine_observes_configured_healthy_stress_recovery(monkeypatch) -> None:
    monkeypatch.setattr(config, "HEALTHY_STRESS_RECOVERY", 0.05)
    state = make_initial_state(seed=7)
    state = replace(state, bonsai=replace(state.bonsai, stress=0.30))

    changed = advance_one_tick(state)

    assert changed.bonsai.stress == pytest.approx(0.25)


def test_moisture_fitness_observes_configured_healthy_minimum(monkeypatch) -> None:
    monkeypatch.setattr(config, "MOISTURE_HEALTHY_MIN", 0.60)

    assert moisture_fitness(0.55) == pytest.approx(11 / 12)


def test_weather_environment_observes_configured_values(monkeypatch) -> None:
    monkeypatch.setattr(config, "CLOUDY_ENV", (0.22, 0.44, -0.06))

    assert environment_for(Weather.CLOUDY) == (0.22, 0.44, -0.06)


def test_weather_transition_observes_configured_probabilities(monkeypatch) -> None:
    monkeypatch.setattr(config, "CLOUDY_TRANSITIONS", {"RAINY": 1.0})

    assert next_weather(seed=7, day_index=1, previous=Weather.CLOUDY) is Weather.RAINY


def test_weather_clock_observes_configured_day_length(monkeypatch) -> None:
    monkeypatch.setattr(config, "TICKS_PER_DAY", 1)

    changed = advance_clock_and_weather(make_initial_state(seed=7))

    assert changed.tick == 1
    assert changed.day_index == 1
    assert changed.hour_of_day == 0


def test_initial_state_observes_configured_weather_environment(monkeypatch) -> None:
    monkeypatch.setattr(config, "INITIAL_WEATHER", "SUNNY")
    monkeypatch.setattr(config, "SUNNY_ENV", (0.91, 0.32, -0.01))

    state = make_initial_state(seed=7)

    assert state.weather is Weather.SUNNY
    assert state.light_level == pytest.approx(0.91)
    assert state.humidity == pytest.approx(0.32)


def test_persistence_observes_configured_real_tick_seconds(monkeypatch) -> None:
    start = datetime(2026, 8, 13, 10, 0, tzinfo=UTC)
    persisted = PersistedGarden(config.SCHEMA_VERSION, start, make_initial_state(seed=7))
    monkeypatch.setattr(config, "SECONDS_PER_REAL_TICK", 2)

    resumed, processed = advance_elapsed(persisted, start + timedelta(seconds=5))

    assert processed == 2
    assert resumed.state.tick == 2
    assert resumed.last_processed_time == start + timedelta(seconds=4)


def test_persistence_observes_configured_schema_version(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(config, "SCHEMA_VERSION", 2)
    persisted = PersistedGarden(
        2,
        datetime(2026, 8, 13, 10, 0, tzinfo=UTC),
        make_initial_state(seed=7),
    )
    path = tmp_path / "garden-state.json"

    save_garden(path, persisted)

    assert load_garden(path) == persisted


def test_service_events_observe_configured_schema_version(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(config, "SCHEMA_VERSION", 7)
    path = tmp_path / "experience.jsonl"
    service = GardenService(make_initial_state(seed=7), path)

    service.apply(GardenAction.INSPECT)

    assert read_events(path)[0].schema_version == 7
