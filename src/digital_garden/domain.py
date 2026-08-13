from dataclasses import dataclass
from enum import StrEnum

from digital_garden import config


class Weather(StrEnum):
    SUNNY = "SUNNY"
    CLOUDY = "CLOUDY"
    RAINY = "RAINY"


class GardenCondition(StrEnum):
    THRIVING = "THRIVING"
    HEALTHY = "HEALTHY"
    WILD = "WILD"
    STRESSED = "STRESSED"
    STRUGGLING = "STRUGGLING"


class AnchorState(StrEnum):
    CALM = "CALM"
    DRY = "DRY"
    WILD = "WILD"
    THRIVING = "THRIVING"
    STRESSED = "STRESSED"


class GardenAction(StrEnum):
    LEAVE_ALONE = "LEAVE_ALONE"
    WATER = "WATER"
    TRIM = "TRIM"
    PRUNE = "PRUNE"
    INSPECT = "INSPECT"


class ActionSource(StrEnum):
    USER = "USER"
    SYSTEM = "SYSTEM"
    EXPERT = "EXPERT"
    BRAIN = "BRAIN"


@dataclass(frozen=True)
class SoilState:
    moisture: float


@dataclass(frozen=True)
class BonsaiState:
    health: float
    stress: float
    growth: float
    canopy_density: float


@dataclass(frozen=True)
class GroundState:
    density: float


@dataclass(frozen=True)
class VineState:
    extent: float


@dataclass(frozen=True)
class GardenState:
    seed: int
    tick: int
    day_index: int
    hour_of_day: int
    weather: Weather
    light_level: float
    humidity: float
    soil: SoilState
    bonsai: BonsaiState
    ground: GroundState
    vine: VineState


def clamp01(value: float) -> float:
    return min(1.0, max(0.0, value))


def make_initial_state(seed: int) -> GardenState:
    return GardenState(
        seed=seed,
        tick=0,
        day_index=0,
        hour_of_day=0,
        weather=Weather.CLOUDY,
        light_level=0.55,
        humidity=0.55,
        soil=SoilState(config.INITIAL_SOIL_MOISTURE),
        bonsai=BonsaiState(
            health=config.INITIAL_BONSAI_HEALTH,
            stress=config.INITIAL_BONSAI_STRESS,
            growth=config.INITIAL_BONSAI_GROWTH,
            canopy_density=config.INITIAL_CANOPY_DENSITY,
        ),
        ground=GroundState(config.INITIAL_GROUND_DENSITY),
        vine=VineState(config.INITIAL_VINE_EXTENT),
    )
