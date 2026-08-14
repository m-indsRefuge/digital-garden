import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QEvent, QPoint, QPointF, Qt
from PySide6.QtGui import QMouseEvent
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


def test_anchor_click_expands_patch_and_collapse_signal_hides_it() -> None:
    app = QApplication.instance() or QApplication([])
    controller = GardenSpikeController(GardenService(make_initial_state(seed=7)))
    anchor = VineAnchorWindow(controller)
    patch = GardenPatchWindow(controller)
    anchor.attach_patch(patch)
    anchor.move(250, 200)
    anchor.show()
    app.processEvents()

    anchor.clicked.emit()
    app.processEvents()

    assert patch.isVisible()
    patch.collapse_requested.emit()
    app.processEvents()
    assert not patch.isVisible()

    anchor.close()
    patch.close()
    app.processEvents()


def test_dragging_expanded_anchor_repositions_patch_by_drag_offset() -> None:
    app = QApplication.instance() or QApplication([])
    controller = GardenSpikeController(GardenService(make_initial_state(seed=7)))
    anchor = VineAnchorWindow(controller)
    patch = GardenPatchWindow(controller)
    anchor.attach_patch(patch)
    anchor.move(600, 200)
    anchor.show()
    app.processEvents()
    anchor.expand_patch()
    app.processEvents()
    before_anchor = anchor.pos()
    before_patch = patch.pos()
    local_origin = QPoint(40, 40)
    press_position = before_anchor + local_origin

    anchor.mousePressEvent(
        QMouseEvent(
            QEvent.Type.MouseButtonPress,
            QPointF(local_origin),
            QPointF(local_origin),
            QPointF(press_position),
            Qt.MouseButton.LeftButton,
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier,
        )
    )
    drag_offset = QPoint(40, 0)
    anchor.mouseMoveEvent(
        QMouseEvent(
            QEvent.Type.MouseMove,
            QPointF(local_origin + drag_offset),
            QPointF(local_origin + drag_offset),
            QPointF(press_position + drag_offset),
            Qt.MouseButton.NoButton,
            Qt.MouseButton.LeftButton,
            Qt.KeyboardModifier.NoModifier,
        )
    )
    app.processEvents()

    assert anchor.pos() == before_anchor + drag_offset
    assert patch.pos() == before_patch + drag_offset

    anchor.close()
    patch.close()
    app.processEvents()
