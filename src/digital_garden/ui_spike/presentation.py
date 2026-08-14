from dataclasses import dataclass

from digital_garden.domain import GardenAction
from digital_garden.service import GardenService


@dataclass(frozen=True)
class GardenSnapshotView:
    anchor_state: str
    condition: str


class GardenSpikeController:
    def __init__(self, service: GardenService) -> None:
        self._service = service
        self.last_action: GardenAction | None = None

    def view(self) -> GardenSnapshotView:
        snapshot = self._service.snapshot()
        derived = snapshot["derived"]
        if not isinstance(derived, dict):
            raise TypeError("snapshot derived state must be a dictionary")
        return GardenSnapshotView(
            anchor_state=str(derived["anchor_state"]),
            condition=str(derived["condition"]),
        )

    def water(self) -> GardenSnapshotView:
        self._service.apply(GardenAction.WATER)
        self.last_action = GardenAction.WATER
        return self.view()
