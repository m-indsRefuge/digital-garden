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
