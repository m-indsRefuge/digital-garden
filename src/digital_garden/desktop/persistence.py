import json
import os
import tempfile
from dataclasses import dataclass
from pathlib import Path

DESKTOP_PREFERENCES_SCHEMA_VERSION = 1


@dataclass(frozen=True)
class DesktopPreferences:
    screen_name: str | None = None
    anchor_x: int | None = None
    anchor_y: int | None = None


def default_preferences_path() -> Path:
    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        return Path(local_app_data) / "DigitalGarden" / "desktop.json"
    return Path.home() / ".digital-garden" / "desktop.json"


class DesktopPreferencesStore:
    def __init__(self, path: Path) -> None:
        self.path = path

    def load(self) -> DesktopPreferences:
        try:
            payload = json.loads(self.path.read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError, OSError, UnicodeError):
            return DesktopPreferences()

        if not isinstance(payload, dict):
            return DesktopPreferences()

        if payload.get("schema_version") != DESKTOP_PREFERENCES_SCHEMA_VERSION:
            return DesktopPreferences()

        screen_name = payload.get("screen_name")
        anchor_x = payload.get("anchor_x")
        anchor_y = payload.get("anchor_y")

        if screen_name is not None and not isinstance(screen_name, str):
            return DesktopPreferences()

        if anchor_x is not None and (isinstance(anchor_x, bool) or not isinstance(anchor_x, int)):
            return DesktopPreferences()

        if anchor_y is not None and (isinstance(anchor_y, bool) or not isinstance(anchor_y, int)):
            return DesktopPreferences()

        return DesktopPreferences(
            screen_name=screen_name,
            anchor_x=anchor_x,
            anchor_y=anchor_y,
        )

    def save(self, preferences: DesktopPreferences) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)

        payload = {
            "schema_version": DESKTOP_PREFERENCES_SCHEMA_VERSION,
            "screen_name": preferences.screen_name,
            "anchor_x": preferences.anchor_x,
            "anchor_y": preferences.anchor_y,
        }

        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=self.path.parent,
            prefix=f".{self.path.name}.",
            suffix=".tmp",
            delete=False,
        ) as temporary:
            json.dump(payload, temporary, sort_keys=True)
            temporary_path = Path(temporary.name)

        try:
            os.replace(temporary_path, self.path)
        except BaseException:
            temporary_path.unlink(missing_ok=True)
            raise
