from datetime import UTC, datetime, timedelta, tzinfo

import pytest

from digital_garden.domain import make_initial_state
from digital_garden.persistence import PersistedGarden, advance_elapsed, load_garden, save_garden


class FallBackTimeZone(tzinfo):
    def utcoffset(self, value: datetime | None) -> timedelta | None:
        if value is None:
            return None
        return timedelta(hours=-4 if value.hour < 2 else -5)

    def dst(self, value: datetime | None) -> timedelta:
        return timedelta(0)

    def fromutc(self, value: datetime) -> datetime:
        return value + timedelta(hours=-4 if value.hour < 6 else -5)


def test_persisted_state_round_trips(tmp_path) -> None:
    path = tmp_path / "garden-state.json"
    persisted = PersistedGarden(
        schema_version=1,
        last_processed_time=datetime(2026, 8, 13, 10, 0, tzinfo=UTC),
        state=make_initial_state(seed=7),
    )
    save_garden(path, persisted)
    assert load_garden(path) == persisted


def test_load_rejects_unsupported_schema_version(tmp_path) -> None:
    path = tmp_path / "garden-state.json"
    path.write_text('{"schema_version": 2}', encoding="utf-8")

    with pytest.raises(ValueError, match="schema_version"):
        load_garden(path)


def test_save_rejects_unsupported_schema_version_before_replacing_file(tmp_path) -> None:
    path = tmp_path / "garden-state.json"
    valid = PersistedGarden(
        1,
        datetime(2026, 8, 13, 10, 0, tzinfo=UTC),
        make_initial_state(seed=7),
    )
    save_garden(path, valid)
    original_contents = path.read_text(encoding="utf-8")

    invalid = PersistedGarden(
        2,
        datetime(2026, 8, 13, 11, 0, tzinfo=UTC),
        make_initial_state(seed=7),
    )
    with pytest.raises(ValueError, match="schema_version"):
        save_garden(path, invalid)

    assert path.read_text(encoding="utf-8") == original_contents


def test_elapsed_time_uses_whole_real_hours_and_preserves_remainder() -> None:
    start = datetime(2026, 8, 13, 10, 0, tzinfo=UTC)
    persisted = PersistedGarden(1, start, make_initial_state(seed=7))
    resumed, processed = advance_elapsed(persisted, start + timedelta(hours=2, minutes=30))

    assert processed == 2
    assert resumed.state.tick == 2
    assert resumed.last_processed_time == start + timedelta(hours=2)


def test_elapsed_time_uses_real_hours_across_a_dst_fall_back() -> None:
    timezone = FallBackTimeZone()
    start = datetime(2026, 11, 1, 0, 30, tzinfo=timezone)
    now = datetime(2026, 11, 1, 2, 30, tzinfo=timezone)
    persisted = PersistedGarden(1, start, make_initial_state(seed=7))

    resumed, processed = advance_elapsed(persisted, now)

    assert processed == 3
    assert resumed.state.tick == 3
    assert resumed.last_processed_time == now


def test_clock_rollback_is_rejected() -> None:
    start = datetime(2026, 8, 13, 10, 0, tzinfo=UTC)
    persisted = PersistedGarden(1, start, make_initial_state(seed=7))
    try:
        advance_elapsed(persisted, start - timedelta(seconds=1))
    except ValueError as exc:
        assert "before last_processed_time" in str(exc)
    else:
        raise AssertionError("expected ValueError")


def test_elapsed_time_rejects_naive_datetimes() -> None:
    aware_start = datetime(2026, 8, 13, 10, 0, tzinfo=UTC)
    persisted = PersistedGarden(1, aware_start, make_initial_state(seed=7))

    with pytest.raises(ValueError, match="timezone-aware"):
        advance_elapsed(persisted, datetime.fromisoformat("2026-08-13T11:00:00"))

    naive_persisted = PersistedGarden(
        1,
        datetime.fromisoformat("2026-08-13T10:00:00"),
        make_initial_state(seed=7),
    )
    with pytest.raises(ValueError, match="timezone-aware"):
        advance_elapsed(naive_persisted, aware_start)
