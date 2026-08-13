from digital_garden.domain import ActionSource, make_initial_state
from digital_garden.ledger import LedgerAction, LedgerEvent, append_event, read_events


def test_jsonl_ledger_is_append_only_and_round_trips(tmp_path) -> None:
    path = tmp_path / "experience.jsonl"
    state = make_initial_state(seed=7)
    event = LedgerEvent(
        schema_version=1,
        tick=0,
        source=ActionSource.USER,
        action=LedgerAction.INSPECT,
        pre_state=state,
        post_state=state,
    )

    append_event(path, event)
    append_event(path, event)

    assert read_events(path) == [event, event]
    assert len(path.read_text(encoding="utf-8").splitlines()) == 2
