from PySide6.QtCore import QEvent, Qt, Signal
from PySide6.QtGui import QGuiApplication, QMouseEvent, QPainter
from PySide6.QtWidgets import QPushButton, QWidget

from digital_garden.desktop.controller import DesktopController
from digital_garden.desktop.placement import adjacent_patch_origin
from digital_garden.desktop.scene.renderer import (
    ANCHOR_SIZE,
    PATCH_COLLAPSE_RECT,
    PATCH_SIZE,
    QPainterShellRenderer,
)

DRAG_THRESHOLD = 6


class GardenPatchWindow(QWidget):
    collapse_requested = Signal()

    def __init__(
        self,
        controller: DesktopController,
        renderer: QPainterShellRenderer,
    ) -> None:
        flags = (
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )

        super().__init__(None, flags)

        self._controller = controller
        self._renderer = renderer
        self._render_state = controller.render_state()

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(PATCH_SIZE)
        self.setMask(renderer.patch_mask())

        self._collapse_button = QPushButton("COLLAPSE", self)
        self._collapse_button.setGeometry(PATCH_COLLAPSE_RECT)
        self._collapse_button.clicked.connect(self.collapse_requested.emit)

    def refresh_state(self) -> None:
        self._render_state = self._controller.render_state()
        self.update()

    def changeEvent(self, event: QEvent) -> None:
        super().changeEvent(event)

        if (
            event.type() is QEvent.Type.ActivationChange
            and self.isVisible()
            and not self.isActiveWindow()
        ):
            self.collapse_requested.emit()

    def paintEvent(self, _event: object) -> None:
        painter = QPainter(self)
        self._renderer.paint_patch(
            painter,
            self._render_state,
        )


class VineAnchorWindow(QWidget):
    clicked = Signal()
    position_committed = Signal(str, int, int)

    def __init__(
        self,
        controller: DesktopController,
        renderer: QPainterShellRenderer,
    ) -> None:
        flags = (
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
            | Qt.WindowType.WindowDoesNotAcceptFocus
        )

        super().__init__(None, flags)

        self._controller = controller
        self._renderer = renderer
        self._patch: GardenPatchWindow | None = None

        self._drag_origin = None
        self._window_origin = None
        self._is_dragging = False

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(ANCHOR_SIZE)
        self.setMask(renderer.anchor_mask())

        self.clicked.connect(self.expand_patch)

    def attach_patch(
        self,
        patch: GardenPatchWindow,
    ) -> None:
        self._patch = patch
        patch.collapse_requested.connect(self.collapse_patch)

    def expand_patch(self) -> None:
        if self._patch is None:
            return

        screen = self.screen() or QGuiApplication.primaryScreen()

        if screen is None:
            return

        self._patch.refresh_state()

        self._patch.move(
            adjacent_patch_origin(
                self.frameGeometry(),
                self._patch.size(),
                screen.availableGeometry(),
            )
        )

        self._patch.show()
        self._patch.raise_()
        self._patch.activateWindow()

    def collapse_patch(self) -> None:
        if self._patch is not None:
            self._patch.hide()

    def paintEvent(self, _event: object) -> None:
        painter = QPainter(self)
        self._renderer.paint_anchor(
            painter,
            self._controller.render_state(),
        )

    def mousePressEvent(
        self,
        event: QMouseEvent,
    ) -> None:
        if event.button() is Qt.MouseButton.LeftButton:
            self._drag_origin = event.globalPosition()
            self._window_origin = self.pos()
            self._is_dragging = False

        super().mousePressEvent(event)

    def mouseMoveEvent(
        self,
        event: QMouseEvent,
    ) -> None:
        if self._drag_origin is not None and self._window_origin is not None:
            offset = event.globalPosition() - self._drag_origin

            if offset.manhattanLength() > DRAG_THRESHOLD:
                self._is_dragging = True
                self.move(self._window_origin + offset.toPoint())

                if self._patch is not None and self._patch.isVisible():
                    self.expand_patch()

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(
        self,
        event: QMouseEvent,
    ) -> None:
        if event.button() is Qt.MouseButton.LeftButton:
            if self._is_dragging:
                screen = self.screen() or QGuiApplication.primaryScreen()

                screen_name = "" if screen is None else screen.name()

                self.position_committed.emit(
                    screen_name,
                    self.x(),
                    self.y(),
                )
            else:
                self.clicked.emit()

        self._drag_origin = None
        self._window_origin = None
        self._is_dragging = False

        super().mouseReleaseEvent(event)
