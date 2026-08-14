import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from digital_garden.domain import make_initial_state
from digital_garden.service import GardenService
from digital_garden.ui_spike.presentation import GardenSpikeController
from digital_garden.ui_spike.windows import VineAnchorWindow


def test_anchor_declares_spike_window_contract() -> None:
    app = QApplication.instance() or QApplication([])
    controller = GardenSpikeController(GardenService(make_initial_state(seed=7)))
    window = VineAnchorWindow(controller)
    flags = window.windowFlags()
    assert flags & Qt.WindowType.FramelessWindowHint
    assert flags & Qt.WindowType.WindowStaysOnTopHint
    assert flags & Qt.WindowType.Tool
    assert flags & Qt.WindowType.WindowDoesNotAcceptFocus
    assert window.testAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
    assert not window.mask().isEmpty()
    window.close()
    app.processEvents()
