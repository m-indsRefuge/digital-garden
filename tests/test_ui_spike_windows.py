import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QEvent, QPoint, QPointF, Qt
from PySide6.QtGui import QMouseEvent, QRegion
from PySide6.QtWidgets import QApplication, QWidget

from digital_garden.domain import GardenAction, make_initial_state
from digital_garden.service import GardenService
from digital_garden.ui_spike.presentation import GardenSpikeController
from digital_garden.ui_spike.windows import (
    GardenPatchWindow,
    VineAnchorWindow,
    build_patch_mask,
    window_diagnostics,
)


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
    assert window.mask() != QRegion(window.rect())
    window.close()
    app.processEvents()


def test_window_diagnostics_has_required_fields() -> None:
    app = QApplication.instance() or QApplication([])
    controller = GardenSpikeController(GardenService(make_initial_state(seed=7)))
    anchor = VineAnchorWindow(controller)
    result = window_diagnostics(anchor)
    assert set(result) == {
        "screen_name",
        "device_pixel_ratio",
        "logical_dpi_x",
        "logical_dpi_y",
        "geometry",
    }
    assert len(result["geometry"]) == 4
    anchor.close()
    app.processEvents()


def test_anchor_emits_display_diagnostic_only_on_first_show(capsys: object) -> None:
    app = QApplication.instance() or QApplication([])
    controller = GardenSpikeController(GardenService(make_initial_state(seed=7)))
    anchor = VineAnchorWindow(controller)
    anchor.show()
    app.processEvents()
    anchor.hide()
    app.processEvents()
    anchor.show()
    app.processEvents()

    output = capsys.readouterr().out
    assert output.count("DIGITAL_GARDEN_SPIKE_DISPLAY") == 1
    anchor.close()
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
    assert not patch.mask().isEmpty()
    assert patch.mask() != QRegion(patch.rect())
    assert patch.anchor_state_text == "CALM"
    assert patch.condition_text == "HEALTHY"
    patch.close()
    app.processEvents()


def test_patch_mask_leaves_known_empty_spaces_transparent() -> None:
    mask = build_patch_mask()
    assert not mask.contains(QPoint(100, 180))
    assert not mask.contains(QPoint(270, 174))
    assert not mask.contains(QPoint(19, 17))


def test_patch_mask_contains_painted_branch_strokes() -> None:
    mask = build_patch_mask()
    assert mask.contains(QPoint(250, 200))
    assert mask.contains(QPoint(220, 152))
    assert mask.contains(QPoint(280, 131))


def test_visible_patch_collapses_when_other_window_activates() -> None:
    app = QApplication.instance() or QApplication([])
    controller = GardenSpikeController(GardenService(make_initial_state(seed=7)))
    anchor = VineAnchorWindow(controller)
    patch = GardenPatchWindow(controller)
    anchor.attach_patch(patch)
    collapse_requests: list[bool] = []
    patch.collapse_requested.connect(lambda: collapse_requests.append(True))
    patch.show()
    app.processEvents()
    assert patch.isActiveWindow()
    other_window = QWidget()
    other_window.show()
    other_window.activateWindow()
    app.processEvents()

    assert collapse_requests == [True]
    assert not patch.isVisible()
    anchor.close()
    patch.close()
    other_window.close()
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


def test_diagnostic_water_refreshes_soil_presentation_from_service_snapshot() -> None:
    app = QApplication.instance() or QApplication([])
    service = GardenService(make_initial_state(seed=7))
    patch = GardenPatchWindow(GardenSpikeController(service))

    assert patch.soil_moisture_text == "0.55"
    patch.perform_diagnostic_water()
    assert patch.soil_moisture_text == "0.80"

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
