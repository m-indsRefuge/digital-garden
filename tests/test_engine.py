from dataclasses import replace

import pytest

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


def test_advance_ticks_rejects_negative_counts() -> None:
    with pytest.raises(ValueError):
        advance_ticks(make_initial_state(seed=7), -1)


def test_advance_ticks_repeats_the_one_tick_transition() -> None:
    state = make_initial_state(seed=11)
    assert advance_ticks(state, 3) == advance_one_tick(advance_one_tick(advance_one_tick(state)))
