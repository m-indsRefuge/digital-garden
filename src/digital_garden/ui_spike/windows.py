from PySide6.QtCore import QRect, Qt, Signal
from PySide6.QtGui import QColor, QMouseEvent, QPainter, QPen, QRegion
from PySide6.QtWidgets import QWidget

from digital_garden.ui_spike.presentation import GardenSpikeController

DRAG_THRESHOLD = 6


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
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(96, 180)
        self.setMask(build_anchor_mask())

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
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() is Qt.MouseButton.LeftButton and not self._is_dragging:
            self.clicked.emit()
        self._drag_origin = None
        self._window_origin = None
        self._is_dragging = False
        super().mouseReleaseEvent(event)
