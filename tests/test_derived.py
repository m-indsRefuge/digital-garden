from dataclasses import replace

from digital_garden.derived import derive_garden_state, moisture_fitness
from digital_garden.domain import (
    AnchorState,
    GardenCondition,
    GroundState,
    VineState,
    make_initial_state,
)


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
