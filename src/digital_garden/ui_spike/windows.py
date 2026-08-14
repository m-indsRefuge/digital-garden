import json

from PySide6.QtCore import QEvent, QRect, Qt, Signal
from PySide6.QtGui import QColor, QGuiApplication, QMouseEvent, QPainter, QPen, QRegion
from PySide6.QtWidgets import QPushButton, QWidget

from digital_garden.ui_spike.geometry import adjacent_patch_origin
from digital_garden.ui_spike.presentation import GardenSpikeController

DRAG_THRESHOLD = 6


def window_diagnostics(widget: QWidget) -> dict[str, object]:
    screen = widget.screen() or QGuiApplication.primaryScreen()
    if screen is None:
        raise RuntimeError("No Qt screen is available for window diagnostics")
    geometry = widget.geometry()
    return {
        "screen_name": screen.name(),
        "device_pixel_ratio": screen.devicePixelRatio(),
        "logical_dpi_x": screen.logicalDotsPerInchX(),
        "logical_dpi_y": screen.logicalDotsPerInchY(),
        "geometry": (geometry.x(), geometry.y(), geometry.width(), geometry.height()),
    }


def build_anchor_mask() -> QRegion:
    region = QRegion(43, 12, 10, 156)
    for rect in (
        QRect(20, 28, 42, 28),
        QRect(39, 58, 42, 28),
        QRect(14, 91, 42, 28),
        QRect(38, 124, 42, 28),
    ):
        region = region.united(QRegion(rect, QRegion.RegionType.Ellipse))
    return region


def build_patch_mask() -> QRegion:
    region = QRegion(QRect(24, 0, 472, 420))
    region = region.united(QRegion(QRect(0, 24, 520, 372)))
    for rect in (
        QRect(0, 0, 48, 48),
        QRect(472, 0, 48, 48),
        QRect(0, 372, 48, 48),
        QRect(472, 372, 48, 48),
    ):
        region = region.united(QRegion(rect, QRegion.RegionType.Ellipse))
    return region


class GardenPatchWindow(QWidget):
    collapse_requested = Signal()

    def __init__(self, controller: GardenSpikeController) -> None:
        flags = (
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        super().__init__(None, flags)
        self._controller = controller
        self._anchor_state_text = ""
        self._condition_text = ""
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(520, 420)
        self.setMask(build_patch_mask())

        self._water_button = QPushButton("WATER", self)
        self._water_button.setGeometry(326, 352, 82, 40)
        self._water_button.clicked.connect(self.perform_diagnostic_water)
        self._collapse_button = QPushButton("COLLAPSE", self)
        self._collapse_button.setGeometry(414, 352, 82, 40)
        self._collapse_button.clicked.connect(self.collapse_requested.emit)
        self.refresh_view()

    @property
    def anchor_state_text(self) -> str:
        return self._anchor_state_text

    @property
    def condition_text(self) -> str:
        return self._condition_text

    def refresh_view(self) -> None:
        view = self._controller.view()
        self._anchor_state_text = view.anchor_state
        self._condition_text = view.condition
        self.update()

    def perform_diagnostic_water(self) -> None:
        self._controller.water()
        self.refresh_view()

    def changeEvent(self, event: QEvent) -> None:
        super().changeEvent(event)
        if event.type() is QEvent.Type.WindowDeactivate and self.isVisible():
            self.collapse_requested.emit()

    def paintEvent(self, _event: object) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#173421"))
        painter.drawRoundedRect(self.rect(), 28, 28)
        painter.setBrush(QColor("#416E43"))
        painter.drawEllipse(QRect(24, 236, 472, 156))
        painter.setPen(QPen(QColor("#7A5537"), 18, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawLine(250, 256, 250, 125)
        painter.drawLine(250, 176, 190, 128)
        painter.drawLine(250, 156, 310, 106)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#6FA65D"))
        for rect in (
            QRect(158, 78, 100, 86),
            QRect(220, 48, 112, 96),
            QRect(286, 74, 92, 82),
        ):
            painter.drawEllipse(rect)
        painter.setPen(QColor("#E7F2DB"))
        painter.drawText(28, 44, f"ANCHOR: {self.anchor_state_text}")
        painter.drawText(28, 68, f"CONDITION: {self.condition_text}")


class VineAnchorWindow(QWidget):
    clicked = Signal()

    def __init__(self, controller: GardenSpikeController) -> None:
        flags = (
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
            | Qt.WindowType.WindowDoesNotAcceptFocus
        )
        super().__init__(None, flags)
        self._controller = controller
        self._drag_origin = None
        self._window_origin = None
        self._is_dragging = False
        self._patch: GardenPatchWindow | None = None
        self._screen_changes_connected = False
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(96, 180)
        self.setMask(build_anchor_mask())

    def showEvent(self, event: object) -> None:
        super().showEvent(event)
        if not self._screen_changes_connected and self.windowHandle() is not None:
            self.windowHandle().screenChanged.connect(self._print_display_diagnostics)
            self._screen_changes_connected = True
        self._print_display_diagnostics()

    def _print_display_diagnostics(self, _screen: object = None) -> None:
        print(
            f"DIGITAL_GARDEN_SPIKE_DISPLAY {json.dumps(window_diagnostics(self), sort_keys=True)}"
        )

    def attach_patch(self, patch: GardenPatchWindow) -> None:
        self._patch = patch
        self.clicked.connect(self.expand_patch)
        patch.collapse_requested.connect(self.collapse_patch)

    def expand_patch(self) -> None:
        if self._patch is None:
            return
        screen = self.screen() or QGuiApplication.primaryScreen()
        if screen is None:
            return
        self._patch.move(
            adjacent_patch_origin(
                self.frameGeometry(), self._patch.size(), screen.availableGeometry()
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
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(QPen(QColor("#31533B"), 7, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawLine(48, 15, 48, 165)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#5E9B68"))
        for rect in (
            QRect(20, 28, 42, 28),
            QRect(39, 58, 42, 28),
            QRect(14, 91, 42, 28),
            QRect(38, 124, 42, 28),
        ):
            painter.drawEllipse(rect)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() is Qt.MouseButton.LeftButton:
            self._drag_origin = event.globalPosition()
            self._window_origin = self.pos()
            self._is_dragging = False
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self._drag_origin is not None and self._window_origin is not None:
            offset = event.globalPosition() - self._drag_origin
            if offset.manhattanLength() > DRAG_THRESHOLD:
                self._is_dragging = True
                self.move(self._window_origin + offset.toPoint())
                if self._patch is not None and self._patch.isVisible():
                    self.expand_patch()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() is Qt.MouseButton.LeftButton and not self._is_dragging:
            self.clicked.emit()
        self._drag_origin = None
        self._window_origin = None
        self._is_dragging = False
        super().mouseReleaseEvent(event)
