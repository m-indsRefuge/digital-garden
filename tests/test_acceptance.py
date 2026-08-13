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
