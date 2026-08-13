from digital_garden.domain import Weather, make_initial_state


def test_initial_state_is_normalized_and_repeatable() -> None:
    first = make_initial_state(seed=7)
    second = make_initial_state(seed=7)

    assert first == second
    assert first.seed == 7
    assert first.tick == 0
    assert first.day_index == 0
    assert first.hour_of_day == 0
    assert first.weather is Weather.CLOUDY
    assert first.soil.moisture == 0.55
    assert first.bonsai.health == 0.85
    assert first.bonsai.stress == 0.10
    assert first.bonsai.growth == 0.20
    assert first.bonsai.canopy_density == 0.50
    assert first.ground.density == 0.35
    assert first.vine.extent == 0.20
