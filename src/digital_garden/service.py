from pathlib import Path

from digital_garden.actions import apply_action
from digital_garden.domain import ActionSource, GardenAction, GardenState
from digital_garden.engine import advance_one_tick
from digital_garden.ledger import LedgerAction, LedgerEvent, append_event
from digital_garden.observation import inspection_snapshot, observation_vector


class GardenService:
    def __init__(self, state: GardenState, ledger_path: Path | None = None) -> None:
        self.state = state
        self.ledger_path = ledger_path

    def snapshot(self) -> dict[str, object]:
        return inspection_snapshot(self.state)

    def observation(self) -> tuple[float, ...]:
        return observation_vector(self.state)

    def apply(
        self,
        action: GardenAction,
        source: ActionSource = ActionSource.USER,
    ) -> GardenState:
        pre_state = self.state
        self.state = apply_action(pre_state, action)
        self._append_event(
            source=source,
            action=LedgerAction(action.value),
            pre_state=pre_state,
            post_state=self.state,
        )
        return self.state

    def advance(self, count: int) -> GardenState:
        if count < 0:
            raise ValueError("count must not be negative")

        for _ in range(count):
            pre_state = self.state
            self.state = advance_one_tick(pre_state)
            if pre_state.weather is not self.state.weather:
                self._append_event(
                    source=ActionSource.SYSTEM,
                    action=LedgerAction.WEATHER_CHANGE,
                    pre_state=pre_state,
                    post_state=self.state,
                )
        return self.state

    def _append_event(
        self,
        source: ActionSource,
        action: LedgerAction,
        pre_state: GardenState,
        post_state: GardenState,
    ) -> None:
        if self.ledger_path is None:
            return

        append_event(
            self.ledger_path,
            LedgerEvent(
                schema_version=1,
                tick=post_state.tick,
                source=source,
                action=action,
                pre_state=pre_state,
                post_state=post_state,
            ),
        )
