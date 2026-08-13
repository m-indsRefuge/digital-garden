import json
import os
import tempfile
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path

from digital_garden.domain import GardenState
from digital_garden.engine import advance_ticks
from digital_garden.observation import state_from_dict, state_to_dict

SCHEMA_VERSION = 1


@dataclass(frozen=True)
class PersistedGarden:
    schema_version: int
    last_processed_time: datetime
    state: GardenState


def save_garden(path: Path, persisted: PersistedGarden) -> None:
    _require_timezone_aware(persisted.last_processed_time)
    payload = {
        "schema_version": persisted.schema_version,
        "last_processed_time": persisted.last_processed_time.isoformat(),
        "state": state_to_dict(persisted.state),
    }
    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        dir=path.parent,
        prefix=f".{path.name}.",
        suffix=".tmp",
        delete=False,
    ) as temporary:
        json.dump(payload, temporary)
        temporary_path = Path(temporary.name)

    try:
        os.replace(temporary_path, path)
    except BaseException:
        temporary_path.unlink(missing_ok=True)
        raise


def load_garden(path: Path) -> PersistedGarden:
    with path.open(encoding="utf-8") as source:
        payload = json.load(source)

    if payload["schema_version"] != SCHEMA_VERSION:
        raise ValueError("unsupported schema_version")

    last_processed_time = datetime.fromisoformat(payload["last_processed_time"])
    _require_timezone_aware(last_processed_time)
    return PersistedGarden(
        schema_version=payload["schema_version"],
        last_processed_time=last_processed_time,
        state=state_from_dict(payload["state"]),
    )


def advance_elapsed(persisted: PersistedGarden, now: datetime) -> tuple[PersistedGarden, int]:
    _require_timezone_aware(persisted.last_processed_time)
    _require_timezone_aware(now)
    elapsed_seconds = (now - persisted.last_processed_time).total_seconds()
    if elapsed_seconds < 0:
        raise ValueError("now must not be before last_processed_time")

    processed_ticks = int(elapsed_seconds // 3600)
    new_state = advance_ticks(persisted.state, processed_ticks)
    new_last_processed = persisted.last_processed_time + timedelta(hours=processed_ticks)
    return (
        PersistedGarden(persisted.schema_version, new_last_processed, new_state),
        processed_ticks,
    )


def _require_timezone_aware(value: datetime) -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("datetime must be timezone-aware")
