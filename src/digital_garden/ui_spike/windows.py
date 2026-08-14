import json

from PySide6.QtCore import QEvent, QRect, Qt, Signal
from PySide6.QtGui import (
    QColor,
    QGuiApplication,
    QMouseEvent,
    QPainter,
    QPainterPath,
    QPainterPathStroker,
    QPen,
    QRegion,
)
from PySide6.QtWidgets import QPushButton, QWidget

from digital_garden.ui_spike.geometry import adjacent_patch_origin
from digital_garden.ui_spike.presentation import GardenSpikeController

DRAG_THRESHOLD = 6
PATCH_LABEL_RECT = QRect(18, 16, 238, 86)
PATCH_GROUND_RECT = QRect(24, 236, 472, 156)
PATCH_BRANCH_WIDTH = 18
PATCH_BRANCH_LINES = (
    (250, 256, 250, 125),
    (250, 176, 190, 128),
    (250, 156, 310, 106),
)
PATCH_CANOPY_RECTS = (
    QRect(158, 78, 100, 86),
    QRect(220, 48, 112, 96),
    QRect(286, 74, 92, 82),
)
PATCH_WATER_BUTTON_RECT = QRect(326, 352, 82, 40)
PATCH_COLLAPSE_BUTTON_RECT = QRect(414, 352, 82, 40)


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


def _rounded_region(rect: QRect, radius: int) -> QRegion:
    path = QPainterPath()
    path.addRoundedRect(rect, radius, radius)
    return QRegion(path.toFillPolygon().toPolygon())


def _stroked_line_region(x1: int, y1: int, x2: int, y2: int) -> QRegion:
    path = QPainterPath()
    path.moveTo(x1, y1)
    path.lineTo(x2, y2)
    stroker = QPainterPathStroker()
    stroker.setWidth(PATCH_BRANCH_WIDTH)
    stroker.setCapStyle(Qt.PenCapStyle.RoundCap)
    return QRegion(stroker.createStroke(path).toFillPolygon().toPolygon())


def build_patch_mask() -> QRegion:
    region = _rounded_region(PATCH_LABEL_RECT, 12)
    region = region.united(QRegion(PATCH_GROUND_RECT, QRegion.RegionType.Ellipse))
    for line in PATCH_BRANCH_LINES:
        region = region.united(_stroked_line_region(*line))
    for rect in PATCH_CANOPY_RECTS:
        region = region.united(QRegion(rect, QRegion.RegionType.Ellipse))
    region = region.united(QRegion(PATCH_WATER_BUTTON_RECT))
    return region.united(QRegion(PATCH_COLLAPSE_BUTTON_RECT))


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
        self._soil_moisture_text = ""
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(520, 420)
        self.setMask(build_patch_mask())

        self._water_button = QPushButton("WATER", self)
        self._water_button.setGeometry(PATCH_WATER_BUTTON_RECT)
        self._water_button.clicked.connect(self.perform_diagnostic_water)
        self._collapse_button = QPushButton("COLLAPSE", self)
        self._collapse_button.setGeometry(PATCH_COLLAPSE_BUTTON_RECT)
        self._collapse_button.clicked.connect(self.collapse_requested.emit)
        self.refresh_view()

    @property
    def anchor_state_text(self) -> str:
        return self._anchor_state_text

    @property
    def condition_text(self) -> str:
        return self._condition_text

    @property
    def soil_moisture_text(self) -> str:
        return self._soil_moisture_text

    def refresh_view(self) -> None:
        view = self._controller.view()
        self._anchor_state_text = view.anchor_state
        self._condition_text = view.condition
        self._soil_moisture_text = f"{view.soil_moisture:.2f}"
        self.update()

    def perform_diagnostic_water(self) -> None:
        self._controller.water()
        self.refresh_view()

    def changeEvent(self, event: QEvent) -> None:
        super().changeEvent(event)
        if (
            event.type() == QEvent.Type.ActivationChange
            and self.isVisible()
            and not self.isActiveWindow()
        ):
            self.collapse_requested.emit()

    def paintEvent(self, _event: object) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#173421"))
        painter.drawRoundedRect(PATCH_LABEL_RECT, 12, 12)
        painter.setBrush(QColor("#416E43"))
        painter.drawEllipse(PATCH_GROUND_RECT)
        painter.setPen(
            QPen(
                QColor("#7A5537"),
                PATCH_BRANCH_WIDTH,
                Qt.PenStyle.SolidLine,
                Qt.PenCapStyle.RoundCap,
            )
        )
        for line in PATCH_BRANCH_LINES:
            painter.drawLine(*line)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#6FA65D"))
        for rect in PATCH_CANOPY_RECTS:
            painter.drawEllipse(rect)
        painter.setPen(QColor("#E7F2DB"))
        painter.drawText(28, 44, f"ANCHOR: {self.anchor_state_text}")
        painter.drawText(28, 68, f"CONDITION: {self.condition_text}")
        painter.drawText(28, 92, f"SOIL: {self.soil_moisture_text}")


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
        self._first_display_diagnostic_emitted = False
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(96, 180)
        self.setMask(build_anchor_mask())

    def showEvent(self, event: object) -> None:
        super().showEvent(event)
        if not self._screen_changes_connected and self.windowHandle() is not None:
            self.windowHandle().screenChanged.connect(self._print_display_diagnostics)
            self._screen_changes_connected = True
        if not self._first_display_diagnostic_emitted:
            self._print_display_diagnostics()
            self._first_display_diagnostic_emitted = True

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
