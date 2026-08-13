from dataclasses import replace

from digital_garden import config
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
    if moisture < config.MOISTURE_HEALTHY_MIN:
        stress_delta = (
            config.DRY_STRESS_BASE
            + (config.MOISTURE_HEALTHY_MIN - moisture) * config.MOISTURE_STRESS_SCALE
        )
    elif moisture > config.MOISTURE_HEALTHY_MAX:
        stress_delta = (
            config.WET_STRESS_BASE
            + (moisture - config.MOISTURE_HEALTHY_MAX) * config.MOISTURE_STRESS_SCALE
        )
    else:
        stress_delta = -config.HEALTHY_STRESS_RECOVERY

    if bonsai.canopy_density < 0.25 or bonsai.canopy_density > 0.80:
        stress_delta += config.CANOPY_STRESS_DELTA
    stress = clamp01(bonsai.stress + stress_delta)

    if stress >= 0.75:
        health_delta = -config.HEALTH_LOSS_SEVERE
    elif stress >= 0.50:
        health_delta = -config.HEALTH_LOSS_STRESSED
    elif stress <= 0.20 and config.MOISTURE_HEALTHY_MIN <= moisture <= config.MOISTURE_HEALTHY_MAX:
        health_delta = config.HEALTH_GAIN_PER_TICK
    else:
        health_delta = 0.0
    health = max(config.BONSAI_HEALTH_FLOOR, clamp01(bonsai.health + health_delta))

    favorable = (
        health > 0.60
        and stress < 0.35
        and config.MOISTURE_HEALTHY_MIN <= moisture <= config.MOISTURE_HEALTHY_MAX
    )
    growth = clamp01(bonsai.growth + (config.BONSAI_GROWTH_PER_TICK if favorable else 0.0))
    canopy_density = clamp01(
        bonsai.canopy_density + (config.CANOPY_GROWTH_PER_TICK if health > 0.50 else 0.0)
    )
    ground_density = clamp01(
        advanced.ground.density + config.GROUND_GROWTH_PER_TICK * (0.5 + humidity)
    )
    vine_extent = clamp01(advanced.vine.extent + config.VINE_GROWTH_PER_TICK * (0.5 + humidity))

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
