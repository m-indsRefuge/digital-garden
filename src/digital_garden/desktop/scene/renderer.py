from PySide6.QtCore import QRect, QSize, Qt
from PySide6.QtGui import (
    QColor,
    QPainter,
    QPainterPath,
    QPen,
    QRegion,
)

from digital_garden.desktop.presentation import GardenRenderState
from digital_garden.desktop.scene.bonsai import (
    bonsai_mask_region,
    build_bonsai_scene,
    paint_bonsai,
)
from digital_garden.desktop.scene.style import scene_style

ANCHOR_SIZE = QSize(96, 180)
PATCH_SIZE = QSize(520, 420)

PATCH_LABEL_RECT = QRect(18, 16, 238, 86)
PATCH_GROUND_RECT = QRect(24, 236, 472, 156)
PATCH_COLLAPSE_RECT = QRect(414, 352, 82, 40)

ANCHOR_LEAF_RECTS = (
    QRect(20, 28, 42, 28),
    QRect(39, 58, 42, 28),
    QRect(14, 91, 42, 28),
    QRect(38, 124, 42, 28),
)

ANCHOR_COLORS = {
    "CALM": QColor("#5E9B68"),
    "DRY": QColor("#9A8052"),
    "WILD": QColor("#4E8D4A"),
    "THRIVING": QColor("#78B86A"),
    "STRESSED": QColor("#7A6956"),
}


def _rounded_region(rect: QRect, radius: int) -> QRegion:
    path = QPainterPath()
    path.addRoundedRect(rect, radius, radius)
    return QRegion(path.toFillPolygon().toPolygon())


class QPainterShellRenderer:
    def anchor_mask(self) -> QRegion:
        region = QRegion(43, 12, 10, 156)

        for rect in ANCHOR_LEAF_RECTS:
            region = region.united(QRegion(rect, QRegion.RegionType.Ellipse))

        return region

    def patch_mask(self, state: GardenRenderState) -> QRegion:
        style = scene_style(state)
        bonsai = build_bonsai_scene(state, style)

        region = _rounded_region(PATCH_LABEL_RECT, 12)
        region = region.united(
            QRegion(
                PATCH_GROUND_RECT,
                QRegion.RegionType.Ellipse,
            )
        )

        region = region.united(bonsai_mask_region(bonsai))

        return region.united(QRegion(PATCH_COLLAPSE_RECT))

    def paint_anchor(
        self,
        painter: QPainter,
        state: GardenRenderState,
    ) -> None:
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        painter.setPen(
            QPen(
                QColor("#31533B"),
                7,
                Qt.PenStyle.SolidLine,
                Qt.PenCapStyle.RoundCap,
            )
        )
        painter.drawLine(48, 15, 48, 165)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(
            ANCHOR_COLORS.get(
                state.anchor_state,
                ANCHOR_COLORS["CALM"],
            )
        )

        for rect in ANCHOR_LEAF_RECTS:
            painter.drawEllipse(rect)

    def paint_patch(
        self,
        painter: QPainter,
        state: GardenRenderState,
    ) -> None:
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        style = scene_style(state)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(23, 52, 33, 220))
        painter.drawRoundedRect(PATCH_LABEL_RECT, 12, 12)

        painter.setBrush(QColor("#416E43"))
        painter.drawEllipse(PATCH_GROUND_RECT)

        paint_bonsai(painter, build_bonsai_scene(state, style), style)

        painter.setPen(QColor("#E7F2DB"))
        painter.drawText(
            30,
            48,
            f"CONDITION: {state.condition}",
        )
        painter.drawText(
            30,
            72,
            f"WEATHER: {state.weather}",
        )
