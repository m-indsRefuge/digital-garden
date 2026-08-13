import hashlib
from dataclasses import replace

from digital_garden.domain import GardenState, Weather

_TRANSITIONS = {
    Weather.SUNNY: ((Weather.SUNNY, 0.60), (Weather.CLOUDY, 0.30), (Weather.RAINY, 0.10)),
    Weather.CLOUDY: ((Weather.SUNNY, 0.30), (Weather.CLOUDY, 0.45), (Weather.RAINY, 0.25)),
    Weather.RAINY: ((Weather.SUNNY, 0.10), (Weather.CLOUDY, 0.55), (Weather.RAINY, 0.35)),
}

_ENVIRONMENT = {
    Weather.SUNNY: (0.90, 0.30, -0.008),
    Weather.CLOUDY: (0.55, 0.55, -0.004),
    Weather.RAINY: (0.25, 0.90, 0.014),
}


def environment_for(weather: Weather) -> tuple[float, float, float]:
    return _ENVIRONMENT[weather]


def _roll(seed: int, day_index: int, previous: Weather) -> float:
    payload = f"{seed}:{day_index}:{previous.value}".encode()
    integer = int.from_bytes(hashlib.blake2b(payload, digest_size=8).digest(), "big")
    return integer / ((1 << 64) - 1)


def next_weather(seed: int, day_index: int, previous: Weather) -> Weather:
    roll = _roll(seed, day_index, previous)
    cumulative = 0.0
    for weather, probability in _TRANSITIONS[previous]:
        cumulative += probability
        if roll < cumulative:
            return weather
    return _TRANSITIONS[previous][-1][0]


def advance_clock_and_weather(state: GardenState) -> GardenState:
    tick = state.tick + 1
    hour = (state.hour_of_day + 1) % 24
    day = state.day_index + (1 if hour == 0 else 0)
    weather = next_weather(state.seed, day, state.weather) if hour == 0 else state.weather
    light, humidity, _ = environment_for(weather)
    return replace(
        state,
        tick=tick,
        day_index=day,
        hour_of_day=hour,
        weather=weather,
        light_level=light,
        humidity=humidity,
    )
