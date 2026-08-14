import json

from digital_garden.desktop.persistence import (
    DESKTOP_PREFERENCES_SCHEMA_VERSION,
    DesktopPreferences,
    DesktopPreferencesStore,
)


def test_desktop_preferences_round_trip(tmp_path) -> None:
    path = tmp_path / "desktop.json"
    store = DesktopPreferencesStore(path)
    preferences = DesktopPreferences(
        screen_name="DISPLAY2",
        anchor_x=1710,
        anchor_y=760,
    )

    store.save(preferences)

    assert store.load() == preferences

    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["schema_version"] == DESKTOP_PREFERENCES_SCHEMA_VERSION
    assert "state" not in payload
    assert "soil" not in payload


def test_missing_invalid_or_non_object_preferences_fall_back_safely(tmp_path) -> None:
    path = tmp_path / "desktop.json"
    store = DesktopPreferencesStore(path)

    assert store.load() == DesktopPreferences()

    path.write_text("not-json", encoding="utf-8")
    assert store.load() == DesktopPreferences()

    path.write_text("[]", encoding="utf-8")
    assert store.load() == DesktopPreferences()
