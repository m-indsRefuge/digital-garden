from dataclasses import replace

from digital_garden.domain import (
    BonsaiState,
    GardenState,
    GroundState,
    SoilState,
    VineState,
    clamp01,
)
from digital_garden.weather import advance_clock_and_weather, environment_for


def advance_one_tick(state: GardenState) -> GardenState:
    advanced = advance_clock_and_weather(state)
    _, humidity, soil_delta = environment_for(advanced.weather)
    moisture = clamp01(state.soil.moisture + soil_delta)

    bonsai = state.bonsai
    if moisture < 0.40:
        stress_delta = 0.012 + (0.40 - moisture) * 0.040
    elif moisture > 0.70:
        stress_delta = 0.012 + (moisture - 0.70) * 0.040
    else:
        stress_delta = -0.008

    if bonsai.canopy_density < 0.25 or bonsai.canopy_density > 0.80:
        stress_delta += 0.006
    stress = clamp01(bonsai.stress + stress_delta)

    if stress >= 0.75:
        health_delta = -0.004
    elif stress >= 0.50:
        health_delta = -0.002
    elif stress <= 0.20 and 0.40 <= moisture <= 0.70:
        health_delta = 0.0015
    else:
        health_delta = 0.0
    health = max(0.15, clamp01(bonsai.health + health_delta))

    favorable = health > 0.60 and stress < 0.35 and 0.40 <= moisture <= 0.70
    growth = clamp01(bonsai.growth + (0.0004 if favorable else 0.0))
    canopy_density = clamp01(bonsai.canopy_density + (0.0006 if health > 0.50 else 0.0))
    ground_density = clamp01(advanced.ground.density + 0.0007 * (0.5 + humidity))
    vine_extent = clamp01(advanced.vine.extent + 0.0005 * (0.5 + humidity))

    return replace(
        advanced,
        soil=SoilState(moisture),
        bonsai=BonsaiState(health, stress, growth, canopy_density),
        ground=GroundState(ground_density),
        vine=VineState(vine_extent),
    )


def advance_ticks(state: GardenState, count: int) -> GardenState:
    if count < 0:
        raise ValueError("count must not be negative")

    result = state
    for _ in range(count):
        result = advance_one_tick(result)
    return result
