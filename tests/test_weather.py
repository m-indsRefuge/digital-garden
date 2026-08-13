from digital_garden.domain import Weather, make_initial_state
from digital_garden.weather import advance_clock_and_weather, next_weather


def test_seed_7_weather_sequence_is_stable() -> None:
    weather = Weather.CLOUDY
    observed = []
    for day in range(1, 11):
        weather = next_weather(7, day, weather)
        observed.append(weather)

    assert observed == [
        Weather.CLOUDY,
        Weather.RAINY,
        Weather.RAINY,
        Weather.CLOUDY,
        Weather.SUNNY,
        Weather.SUNNY,
        Weather.CLOUDY,
        Weather.SUNNY,
        Weather.CLOUDY,
        Weather.CLOUDY,
    ]


def test_weather_changes_only_at_day_boundary() -> None:
    state = make_initial_state(seed=7)
    for _ in range(23):
        state = advance_clock_and_weather(state)
        assert state.weather is Weather.CLOUDY

    state = advance_clock_and_weather(state)
    assert state.tick == 24
    assert state.day_index == 1
    assert state.hour_of_day == 0
    assert state.weather is Weather.CLOUDY
