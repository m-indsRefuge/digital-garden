from digital_garden.domain import ActionSource, GardenAction, make_initial_state
from digital_garden.ledger import read_events
from digital_garden.observation import inspection_snapshot, observation_vector
from digital_garden.service import GardenService


def test_user_action_is_applied_and_logged(tmp_path) -> None:
    ledger_path = tmp_path / "experience.jsonl"
    service = GardenService(make_initial_state(seed=7), ledger_path)

    service.apply(GardenAction.WATER, ActionSource.USER)

    assert service.state.soil.moisture == 0.80
    events = read_events(ledger_path)
    assert len(events) == 1
    assert events[0].action.value == "WATER"
    assert events[0].source is ActionSource.USER


def test_weather_change_is_logged_as_system_event(tmp_path) -> None:
    ledger_path = tmp_path / "experience.jsonl"
    service = GardenService(make_initial_state(seed=7), ledger_path)
    service.advance(48)

    events = read_events(ledger_path)
    weather_events = [event for event in events if event.action.value == "WEATHER_CHANGE"]
    assert len(weather_events) >= 1
    assert all(event.source is ActionSource.SYSTEM for event in weather_events)


def test_inspection_is_logged_even_when_it_does_not_change_state(tmp_path) -> None:
    ledger_path = tmp_path / "experience.jsonl"
    service = GardenService(make_initial_state(seed=7), ledger_path)

    state = service.apply(GardenAction.INSPECT)

    events = read_events(ledger_path)
    assert state == make_initial_state(seed=7)
    assert len(events) == 1
    assert events[0].action.value == "INSPECT"
    assert events[0].pre_state == events[0].post_state


def test_advance_processes_exactly_the_requested_number_of_ticks() -> None:
    service = GardenService(make_initial_state(seed=7))

    state = service.advance(3)

    assert state.tick == 3


def test_snapshot_and_observation_delegate_to_existing_views() -> None:
    state = make_initial_state(seed=7)
    service = GardenService(state)

    assert service.snapshot() == inspection_snapshot(state)
    assert service.observation() == observation_vector(state)
