from dataclasses import dataclass

from digital_garden.domain import AnchorState, GardenCondition, GardenState, clamp01


@dataclass(frozen=True)
class DerivedGardenState:
    garden_health: float
    overgrowth: float
    condition: GardenCondition
    anchor_state: AnchorState


def moisture_fitness(moisture: float) -> float:
    if moisture < 0.40:
        return moisture / 0.40
    if moisture <= 0.70:
        return 1.0
    return (1.0 - moisture) / 0.30


def derive_garden_state(state: GardenState) -> DerivedGardenState:
    canopy_pressure = clamp01((state.bonsai.canopy_density - 0.60) / 0.40)
    overgrowth = clamp01(
        0.40 * canopy_pressure + 0.30 * state.ground.density + 0.30 * state.vine.extent
    )
    moisture = state.soil.moisture
    fitness = moisture_fitness(moisture)
    manageable_growth = 1.0 if overgrowth <= 0.60 else 1.0 - ((overgrowth - 0.60) / 0.40)
    garden_health = clamp01(
        0.65 * state.bonsai.health + 0.20 * clamp01(fitness) + 0.15 * clamp01(manageable_growth)
    )

    if state.bonsai.health <= 0.35 or state.bonsai.stress >= 0.80:
        condition = GardenCondition.STRUGGLING
    elif (
        state.bonsai.health < 0.65
        or state.bonsai.stress >= 0.50
        or moisture < 0.25
        or moisture > 0.85
    ):
        condition = GardenCondition.STRESSED
    elif (
        state.bonsai.health >= 0.90
        and state.bonsai.stress <= 0.15
        and fitness >= 0.90
        and overgrowth <= 0.45
    ):
        condition = GardenCondition.THRIVING
    elif overgrowth >= 0.60 and garden_health >= 0.65:
        condition = GardenCondition.WILD
    else:
        condition = GardenCondition.HEALTHY

    if moisture < 0.30:
        anchor_state = AnchorState.DRY
    elif condition in {GardenCondition.STRESSED, GardenCondition.STRUGGLING}:
        anchor_state = AnchorState.STRESSED
    elif condition is GardenCondition.THRIVING:
        anchor_state = AnchorState.THRIVING
    elif condition is GardenCondition.WILD:
        anchor_state = AnchorState.WILD
    else:
        anchor_state = AnchorState.CALM

    return DerivedGardenState(
        garden_health=garden_health,
        overgrowth=overgrowth,
        condition=condition,
        anchor_state=anchor_state,
    )
