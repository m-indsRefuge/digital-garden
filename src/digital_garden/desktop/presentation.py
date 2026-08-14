from collections.abc import Mapping
from dataclasses import dataclass


@dataclass(frozen=True)
class GardenRenderState:
    seed: int
    tick: int
    weather: str
    light_level: float
    humidity: float
    soil_moisture: float
    bonsai_health: float
    bonsai_stress: float
    bonsai_growth: float
    canopy_density: float
    ground_density: float
    vine_extent: float
    condition: str
    anchor_state: str


def _mapping(value: object, name: str) -> Mapping[str, object]:
    if not isinstance(value, Mapping):
        raise TypeError(f"{name} must be a mapping")
    return value


def _number(value: object, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{name} must be numeric")
    return float(value)


def _integer(value: object, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} must be an integer")
    return value


def _string(value: object, name: str) -> str:
    if not isinstance(value, str):
        raise TypeError(f"{name} must be a string")
    return value


def render_state_from_snapshot(snapshot: dict[str, object]) -> GardenRenderState:
    state = _mapping(snapshot.get("state"), "snapshot state")
    derived = _mapping(snapshot.get("derived"), "snapshot derived")
    soil = _mapping(state.get("soil"), "snapshot soil")
    bonsai = _mapping(state.get("bonsai"), "snapshot bonsai")
    ground = _mapping(state.get("ground"), "snapshot ground")
    vine = _mapping(state.get("vine"), "snapshot vine")

    return GardenRenderState(
        seed=_integer(state.get("seed"), "seed"),
        tick=_integer(state.get("tick"), "tick"),
        weather=_string(state.get("weather"), "weather"),
        light_level=_number(state.get("light_level"), "light_level"),
        humidity=_number(state.get("humidity"), "humidity"),
        soil_moisture=_number(soil.get("moisture"), "soil moisture"),
        bonsai_health=_number(bonsai.get("health"), "bonsai health"),
        bonsai_stress=_number(bonsai.get("stress"), "bonsai stress"),
        bonsai_growth=_number(bonsai.get("growth"), "bonsai growth"),
        canopy_density=_number(bonsai.get("canopy_density"), "canopy density"),
        ground_density=_number(ground.get("density"), "ground density"),
        vine_extent=_number(vine.get("extent"), "vine extent"),
        condition=_string(derived.get("condition"), "condition"),
        anchor_state=_string(derived.get("anchor_state"), "anchor state"),
    )
