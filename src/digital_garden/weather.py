import hashlib
from dataclasses import replace

from digital_garden import config
from digital_garden.domain import GardenState, Weather


def environment_for(weather: Weather) -> tuple[float, float, float]:
    if weather is Weather.SUNNY:
        return config.SUNNY_ENV
    if weather is Weather.CLOUDY:
        return config.CLOUDY_ENV
    return config.RAINY_ENV


def _transition_weights(previous: Weather) -> dict[str, float]:
    if previous is Weather.SUNNY:
        return config.SUNNY_TRANSITIONS
    if previous is Weather.CLOUDY:
        return config.CLOUDY_TRANSITIONS
    return config.RAINY_TRANSITIONS


def _roll(seed: int, day_index: int, previous: Weather) -> float:
    payload = f"{seed}:{day_index}:{previous.value}".encode()
    integer = int.from_bytes(hashlib.blake2b(payload, digest_size=8).digest(), "big")
    return integer / ((1 << 64) - 1)


def next_weather(seed: int, day_index: int, previous: Weather) -> Weather:
    roll = _roll(seed, day_index, previous)
    cumulative = 0.0
    transitions = tuple(
        (Weather(weather_name), probability)
        for weather_name, probability in _transition_weights(previous).items()
    )
    for weather, probability in transitions:
        cumulative += probability
        if roll < cumulative:
            return weather
    return transitions[-1][0]


def advance_clock_and_weather(state: GardenState) -> GardenState:
    tick = state.tick + 1
    hour = (state.hour_of_day + 1) % config.TICKS_PER_DAY
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
