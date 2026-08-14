import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication

from digital_garden.domain import GardenAction, make_initial_state
from digital_garden.service import GardenService
from digital_garden.ui_spike.presentation import GardenSpikeController
from digital_garden.ui_spike.windows import GardenPatchWindow, VineAnchorWindow


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


def test_patch_declares_spike_window_contract_and_real_state() -> None:
    app = QApplication.instance() or QApplication([])
    controller = GardenSpikeController(GardenService(make_initial_state(seed=7)))
    patch = GardenPatchWindow(controller)
    flags = patch.windowFlags()
    assert flags & Qt.WindowType.FramelessWindowHint
    assert flags & Qt.WindowType.WindowStaysOnTopHint
    assert flags & Qt.WindowType.Tool
    assert patch.testAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
    assert patch.anchor_state_text == "CALM"
    assert patch.condition_text == "HEALTHY"
    patch.close()
    app.processEvents()


def test_patch_diagnostic_water_routes_through_controller() -> None:
    app = QApplication.instance() or QApplication([])
    service = GardenService(make_initial_state(seed=7))
    controller = GardenSpikeController(service)
    patch = GardenPatchWindow(controller)
    before = service.state.soil.moisture
    patch.perform_diagnostic_water()
    assert service.state.soil.moisture > before
    assert controller.last_action is GardenAction.WATER
    patch.close()
    app.processEvents()
