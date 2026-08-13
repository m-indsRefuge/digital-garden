import pytest

from digital_garden.domain import make_initial_state
from digital_garden.observation import (
    inspection_snapshot,
    observation_vector,
    state_from_dict,
    state_to_dict,
)


def test_brain_observation_has_fixed_order_and_length() -> None:
    state = make_initial_state(seed=7)
    vector = observation_vector(state)
    assert vector == (
        0.55,
        0.85,
        0.10,
        0.20,
        0.50,
        0.35,
        0.20,
        0.55,
        0.55,
        0.0,
        1.0,
        0.0,
    )
    assert len(vector) == 12


def test_state_serialization_round_trips_exactly() -> None:
    state = make_initial_state(seed=7)
    payload = state_to_dict(state)
    assert payload["weather"] == "CLOUDY"
    assert payload["soil"] == {"moisture": 0.55}
    assert state_from_dict(payload) == state


def test_state_deserialization_rejects_unknown_weather() -> None:
    payload = state_to_dict(make_initial_state(seed=7))
    payload["weather"] = "WINDY"
    with pytest.raises(ValueError, match="WINDY"):
        state_from_dict(payload)


def test_inspection_snapshot_includes_derived_human_facing_state() -> None:
    snapshot = inspection_snapshot(make_initial_state(seed=7))
    assert snapshot["derived"] == {
        "garden_health": 0.9025,
        "overgrowth": 0.16499999999999998,
        "condition": "HEALTHY",
        "anchor_state": "CALM",
    }
