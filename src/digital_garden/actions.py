from dataclasses import replace

from digital_garden.domain import GardenAction, GardenState, clamp01


def apply_action(state: GardenState, action: GardenAction) -> GardenState:
    if action is GardenAction.WATER:
        return replace(state, soil=replace(state.soil, moisture=_adjust(state.soil.moisture, 0.25)))
    if action is GardenAction.TRIM:
        return replace(
            state,
            ground=replace(state.ground, density=_adjust(state.ground.density, -0.20)),
            vine=replace(state.vine, extent=_adjust(state.vine.extent, -0.15)),
        )
    if action is GardenAction.PRUNE:
        return replace(
            state,
            bonsai=replace(
                state.bonsai,
                canopy_density=_adjust(state.bonsai.canopy_density, -0.18),
                stress=_adjust(state.bonsai.stress, 0.08),
            ),
        )
    return state


def _adjust(value: float, delta: float) -> float:
    return round(clamp01(value + delta), 2)
