from PySide6.QtCore import QRect, QSize, Qt
from PySide6.QtGui import QColor, QPainter, QPainterPath, QRegion

from digital_garden.desktop.presentation import GardenRenderState
from digital_garden.desktop.scene.bonsai import (
    bonsai_mask_region,
    build_bonsai_scene,
    paint_bonsai,
)
from digital_garden.desktop.scene.ground import (
    build_ground_scene,
    ground_mask_region,
    paint_ground,
)
from digital_garden.desktop.scene.style import scene_style
from digital_garden.desktop.scene.vines import (
    anchor_vine_mask_region,
    build_anchor_vine_scene,
    build_edge_vine_scene,
    edge_vine_mask_region,
    paint_anchor_vine,
    paint_edge_vines,
)

ANCHOR_SIZE = QSize(96, 180)
PATCH_SIZE = QSize(520, 420)

PATCH_LABEL_RECT = QRect(18, 16, 238, 86)
PATCH_COLLAPSE_RECT = QRect(414, 352, 82, 40)


def _rounded_region(rect: QRect, radius: int) -> QRegion:
    path = QPainterPath()
    path.addRoundedRect(rect, radius, radius)
    return QRegion(path.toFillPolygon().toPolygon())


class QPainterShellRenderer:
    def anchor_mask(self, state: GardenRenderState) -> QRegion:
        style = scene_style(state)
        anchor = build_anchor_vine_scene(state, style)
        return anchor_vine_mask_region(anchor)

    def patch_mask(self, state: GardenRenderState) -> QRegion:
        style = scene_style(state)
        bonsai = build_bonsai_scene(state, style)
        ground = build_ground_scene(state, style)
        edge_vines = build_edge_vine_scene(state, style)

        region = _rounded_region(PATCH_LABEL_RECT, 12)
        region = region.united(ground_mask_region(ground))
        region = region.united(edge_vine_mask_region(edge_vines))
        region = region.united(bonsai_mask_region(bonsai))

        return region.united(QRegion(PATCH_COLLAPSE_RECT))

    def paint_anchor(
        self,
        painter: QPainter,
        state: GardenRenderState,
    ) -> None:
        style = scene_style(state)
        paint_anchor_vine(painter, build_anchor_vine_scene(state, style), style)

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

        paint_ground(painter, build_ground_scene(state, style), style)
        paint_edge_vines(painter, build_edge_vine_scene(state, style), style)
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
