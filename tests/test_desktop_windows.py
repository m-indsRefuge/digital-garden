import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import Qt
from PySide6.QtGui import QRegion
from PySide6.QtWidgets import QApplication, QWidget

from digital_garden.desktop.controller import DesktopController
from digital_garden.desktop.scene.renderer import QPainterShellRenderer
from digital_garden.desktop.windows import GardenPatchWindow, VineAnchorWindow
from digital_garden.domain import make_initial_state
from digital_garden.service import GardenService


def _controller() -> DesktopController:
    return DesktopController(GardenService(make_initial_state(seed=7)))


def test_anchor_and_patch_keep_the_proven_window_contract() -> None:
    app = QApplication.instance() or QApplication([])
    renderer = QPainterShellRenderer()
    anchor = VineAnchorWindow(_controller(), renderer)
    patch = GardenPatchWindow(_controller(), renderer)

    anchor_flags = anchor.windowFlags()
    patch_flags = patch.windowFlags()

    assert anchor_flags & Qt.WindowType.FramelessWindowHint
    assert anchor_flags & Qt.WindowType.WindowStaysOnTopHint
    assert anchor_flags & Qt.WindowType.Tool
    assert anchor_flags & Qt.WindowType.WindowDoesNotAcceptFocus

    assert patch_flags & Qt.WindowType.FramelessWindowHint
    assert patch_flags & Qt.WindowType.WindowStaysOnTopHint
    assert patch_flags & Qt.WindowType.Tool

    assert anchor.testAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
    assert patch.testAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

    assert not anchor.mask().isEmpty()
    assert not patch.mask().isEmpty()
    assert anchor.mask() != QRegion(anchor.rect())
    assert patch.mask() != QRegion(patch.rect())

    anchor.close()
    patch.close()
    app.processEvents()


def test_collapse_button_is_only_an_invisible_hit_target() -> None:
    app = QApplication.instance() or QApplication([])
    patch = GardenPatchWindow(_controller(), QPainterShellRenderer())
    button = patch._collapse_button

    assert button.text() == ""
    assert button.isFlat()
    assert "background: transparent" in button.styleSheet()

    patch.close()
    app.processEvents()


def test_activation_change_collapses_attached_patch() -> None:
    app = QApplication.instance() or QApplication([])
    renderer = QPainterShellRenderer()
    controller = _controller()

    anchor = VineAnchorWindow(controller, renderer)
    patch = GardenPatchWindow(controller, renderer)
    other = QWidget()

    anchor.attach_patch(patch)

    anchor.show()
    anchor.expand_patch()
    app.processEvents()

    assert patch.isVisible()

    other.show()
    other.activateWindow()
    app.processEvents()

    assert not patch.isVisible()

    other.close()
    anchor.close()
    patch.close()
    app.processEvents()
