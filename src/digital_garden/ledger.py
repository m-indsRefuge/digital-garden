import json
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from digital_garden.domain import ActionSource, GardenState
from digital_garden.observation import state_from_dict, state_to_dict


class LedgerAction(StrEnum):
    LEAVE_ALONE = "LEAVE_ALONE"
    WATER = "WATER"
    TRIM = "TRIM"
    PRUNE = "PRUNE"
    INSPECT = "INSPECT"
    WEATHER_CHANGE = "WEATHER_CHANGE"


@dataclass(frozen=True)
class LedgerEvent:
    schema_version: int
    tick: int
    source: ActionSource
    action: LedgerAction
    pre_state: GardenState
    post_state: GardenState


def append_event(path: Path, event: LedgerEvent) -> None:
    payload = {
        "schema_version": event.schema_version,
        "tick": event.tick,
        "source": event.source.value,
        "action": event.action.value,
        "pre_state": state_to_dict(event.pre_state),
        "post_state": state_to_dict(event.post_state),
    }
    with path.open("a", encoding="utf-8") as ledger_file:
        ledger_file.write(json.dumps(payload))
        ledger_file.write("\n")


def read_events(path: Path) -> list[LedgerEvent]:
    with path.open(encoding="utf-8") as ledger_file:
        return [_event_from_payload(json.loads(line)) for line in ledger_file]


def _event_from_payload(payload: dict[str, object]) -> LedgerEvent:
    return LedgerEvent(
        schema_version=payload["schema_version"],
        tick=payload["tick"],
        source=ActionSource(payload["source"]),
        action=LedgerAction(payload["action"]),
        pre_state=state_from_dict(payload["pre_state"]),
        post_state=state_from_dict(payload["post_state"]),
    )
