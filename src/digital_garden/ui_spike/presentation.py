from dataclasses import dataclass

from digital_garden.domain import GardenAction
from digital_garden.service import GardenService


@dataclass(frozen=True)
class GardenSnapshotView:
    anchor_state: str
    condition: str
    soil_moisture: float


class GardenSpikeController:
    def __init__(self, service: GardenService) -> None:
        self._service = service
        self.last_action: GardenAction | None = None

    def view(self) -> GardenSnapshotView:
        snapshot = self._service.snapshot()
        derived = snapshot["derived"]
        state = snapshot["state"]
        if not isinstance(derived, dict):
            raise TypeError("snapshot derived state must be a dictionary")
        if not isinstance(state, dict):
            raise TypeError("snapshot state must be a dictionary")
        soil = state["soil"]
        if not isinstance(soil, dict):
            raise TypeError("snapshot soil state must be a dictionary")
        soil_moisture = soil["moisture"]
        if not isinstance(soil_moisture, float):
            raise TypeError("snapshot soil moisture must be a float")
        return GardenSnapshotView(
            anchor_state=str(derived["anchor_state"]),
            condition=str(derived["condition"]),
            soil_moisture=soil_moisture,
        )

    def water(self) -> GardenSnapshotView:
        self._service.apply(GardenAction.WATER)
        self.last_action = GardenAction.WATER
        return self.view()
