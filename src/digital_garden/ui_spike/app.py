import sys

from PySide6.QtWidgets import QApplication

from digital_garden.domain import make_initial_state
from digital_garden.service import GardenService
from digital_garden.ui_spike.presentation import GardenSpikeController
from digital_garden.ui_spike.windows import GardenPatchWindow, VineAnchorWindow


def main() -> None:
    app = QApplication.instance() or QApplication(sys.argv)
    controller = GardenSpikeController(GardenService(make_initial_state(seed=7)))
    anchor = VineAnchorWindow(controller)
    patch = GardenPatchWindow(controller)
    anchor.attach_patch(patch)
    anchor.show()
    raise SystemExit(app.exec())
