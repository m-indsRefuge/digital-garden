from digital_garden.desktop.presentation import (
    GardenRenderState,
    render_state_from_snapshot,
)
from digital_garden.service import GardenService


class DesktopController:
    def __init__(self, service: GardenService) -> None:
        self._service = service

    def render_state(self) -> GardenRenderState:
        return render_state_from_snapshot(self._service.snapshot())
