from digital_garden.derived import derive_garden_state
from digital_garden.domain import (
    BonsaiState,
    GardenState,
    GroundState,
    SoilState,
    VineState,
    Weather,
)


def observation_vector(state: GardenState) -> tuple[float, ...]:
    return (
        state.soil.moisture,
        state.bonsai.health,
        state.bonsai.stress,
        state.bonsai.growth,
        state.bonsai.canopy_density,
        state.ground.density,
        state.vine.extent,
        state.light_level,
        state.humidity,
        float(state.weather is Weather.SUNNY),
        float(state.weather is Weather.CLOUDY),
        float(state.weather is Weather.RAINY),
    )


def state_to_dict(state: GardenState) -> dict[str, object]:
    return {
        "seed": state.seed,
        "tick": state.tick,
        "day_index": state.day_index,
        "hour_of_day": state.hour_of_day,
        "weather": state.weather.value,
        "light_level": state.light_level,
        "humidity": state.humidity,
        "soil": {"moisture": state.soil.moisture},
        "bonsai": {
            "health": state.bonsai.health,
            "stress": state.bonsai.stress,
            "growth": state.bonsai.growth,
            "canopy_density": state.bonsai.canopy_density,
        },
        "ground": {"density": state.ground.density},
        "vine": {"extent": state.vine.extent},
    }


def state_from_dict(payload: dict[str, object]) -> GardenState:
    soil = payload["soil"]
    bonsai = payload["bonsai"]
    ground = payload["ground"]
    vine = payload["vine"]
    if not all(isinstance(value, dict) for value in (soil, bonsai, ground, vine)):
        raise TypeError("nested state must be dictionaries")

    return GardenState(
        seed=payload["seed"],
        tick=payload["tick"],
        day_index=payload["day_index"],
        hour_of_day=payload["hour_of_day"],
        weather=Weather(payload["weather"]),
        light_level=payload["light_level"],
        humidity=payload["humidity"],
        soil=SoilState(moisture=soil["moisture"]),
        bonsai=BonsaiState(
            health=bonsai["health"],
            stress=bonsai["stress"],
            growth=bonsai["growth"],
            canopy_density=bonsai["canopy_density"],
        ),
        ground=GroundState(density=ground["density"]),
        vine=VineState(extent=vine["extent"]),
    )


def inspection_snapshot(state: GardenState) -> dict[str, object]:
    derived = derive_garden_state(state)
    return {
        "state": state_to_dict(state),
        "derived": {
            "garden_health": derived.garden_health,
            "overgrowth": derived.overgrowth,
            "condition": derived.condition.value,
            "anchor_state": derived.anchor_state.value,
        },
    }
