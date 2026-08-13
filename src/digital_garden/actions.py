from dataclasses import replace

from digital_garden import config
from digital_garden.domain import GardenAction, GardenState, clamp01


def apply_action(state: GardenState, action: GardenAction) -> GardenState:
    if action is GardenAction.WATER:
        return replace(
            state,
            soil=replace(state.soil, moisture=_adjust(state.soil.moisture, config.WATER_AMOUNT)),
        )
    if action is GardenAction.TRIM:
        return replace(
            state,
            ground=replace(
                state.ground,
                density=_adjust(state.ground.density, -config.TRIM_GROUND_AMOUNT),
            ),
            vine=replace(state.vine, extent=_adjust(state.vine.extent, -config.TRIM_VINE_AMOUNT)),
        )
    if action is GardenAction.PRUNE:
        return replace(
            state,
            bonsai=replace(
                state.bonsai,
                canopy_density=_adjust(state.bonsai.canopy_density, -config.PRUNE_CANOPY_AMOUNT),
                stress=_adjust(state.bonsai.stress, config.PRUNE_STRESS_COST),
            ),
        )
    return state


def _adjust(value: float, delta: float) -> float:
    return clamp01(value + delta)
