from dataclasses import dataclass

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPainterPathStroker, QPen, QRegion

from digital_garden.desktop.presentation import GardenRenderState
from digital_garden.desktop.scene.style import Color, SceneStyle
from digital_garden.desktop.scene.variation import (
    candidate_pool,
    stable_unit,
    visible_candidates,
)


@dataclass(frozen=True)
class GroundPoint:
    x: float
    y: float


@dataclass(frozen=True)
class GroundDetail:
    center_x: float
    center_y: float
    scale: float
    rotation: float


@dataclass(frozen=True)
class GroundScene:
    outline: tuple[GroundPoint, ...]
    clover: tuple[GroundDetail, ...]
    flowers: tuple[GroundDetail, ...]
    grass: tuple[GroundDetail, ...]
    moss: tuple[GroundDetail, ...]
    stones: tuple[GroundDetail, ...]


_GROUND_OUTLINE = (
    (30.0, 344.0),
    (40.0, 316.0),
    (78.0, 296.0),
    (122.0, 282.0),
    (174.0, 274.0),
    (224.0, 266.0),
    (276.0, 263.0),
    (328.0, 267.0),
    (376.0, 278.0),
    (428.0, 294.0),
    (476.0, 316.0),
    (492.0, 341.0),
    (483.0, 361.0),
    (449.0, 377.0),
    (400.0, 388.0),
    (344.0, 396.0),
    (284.0, 399.0),
    (227.0, 397.0),
    (169.0, 391.0),
    (112.0, 382.0),
    (62.0, 370.0),
    (33.0, 355.0),
)


def _detail_sites(
    state: GardenRenderState,
    object_id: str,
    count: int,
    visibility: float,
) -> tuple[GroundDetail, ...]:
    candidates = candidate_pool(state.seed, object_id, count)
    visible = visible_candidates(candidates, visibility)

    return tuple(_ground_detail(candidate.x, candidate.y, candidate.scale) for candidate in visible)


def _ground_detail(x: float, y: float, scale: float) -> GroundDetail:
    center_x = 68.0 + x * 384.0
    edge_distance = abs(x - 0.5) * 2.0
    half_height = 31.0 + (1.0 - edge_distance) * 31.0
    return GroundDetail(
        center_x=center_x,
        center_y=331.0 + (y - 0.5) * 2.0 * half_height,
        scale=scale,
        rotation=(x - 0.5) * 24.0,
    )


def _ground_outline(state: GardenRenderState) -> tuple[GroundPoint, ...]:
    return tuple(
        GroundPoint(
            x=x + (stable_unit(state.seed, "ground-edge-x", index) - 0.5) * 8.0,
            y=y + (stable_unit(state.seed, "ground-edge-y", index) - 0.5) * 6.0,
        )
        for index, (x, y) in enumerate(_GROUND_OUTLINE)
    )


def build_ground_scene(
    state: GardenRenderState,
    _style: SceneStyle,
) -> GroundScene:
    density = max(0.0, min(1.0, state.ground_density))
    return GroundScene(
        outline=_ground_outline(state),
        clover=_detail_sites(state, "ground-clover", 24, density),
        flowers=_detail_sites(state, "ground-flowers", 8, max(0.0, (density - 0.35) / 0.65)),
        grass=_detail_sites(state, "ground-grass", 22, density),
        moss=_detail_sites(state, "ground-moss", 14, 0.35 + density * 0.65),
        stones=_detail_sites(state, "ground-stones", 7, 0.30 + density * 0.55),
    )


def _qcolor(color: Color, alpha: int | None = None) -> QColor:
    return QColor(color.red, color.green, color.blue, color.alpha if alpha is None else alpha)


def _outline_path(scene: GroundScene) -> QPainterPath:
    first, *rest = scene.outline
    path = QPainterPath(QPointF(first.x, first.y))

    for point in rest:
        path.lineTo(point.x, point.y)

    path.closeSubpath()
    return path


def ground_mask_region(scene: GroundScene) -> QRegion:
    """Return the clickable opaque ground footprint for a prepared scene."""
    path = _outline_path(scene)
    stroker = QPainterPathStroker()
    stroker.setWidth(6.0)
    mask_path = path.united(stroker.createStroke(path))
    return QRegion(mask_path.toFillPolygon().toPolygon())


def _darkened(color: Color, amount: float) -> QColor:
    factor = 1.0 - amount
    return QColor(
        round(color.red * factor),
        round(color.green * factor),
        round(color.blue * factor),
        color.alpha,
    )


def _paint_moss_patch(
    painter: QPainter,
    detail: GroundDetail,
    style: SceneStyle,
) -> None:
    painter.setBrush(_qcolor(style.palette.moss, 160))
    painter.drawEllipse(
        QRectF(
            detail.center_x - 14.0 * detail.scale,
            detail.center_y - 6.0 * detail.scale,
            28.0 * detail.scale,
            12.0 * detail.scale,
        )
    )


def _paint_stone(
    painter: QPainter,
    detail: GroundDetail,
    style: SceneStyle,
) -> None:
    painter.setBrush(_darkened(style.palette.trunk, 0.22))
    painter.drawEllipse(
        QRectF(
            detail.center_x - 7.0 * detail.scale,
            detail.center_y - 4.0 * detail.scale,
            14.0 * detail.scale,
            8.0 * detail.scale,
        )
    )


def _paint_grass(
    painter: QPainter,
    detail: GroundDetail,
    style: SceneStyle,
) -> None:
    pen = QPen(_qcolor(style.palette.vine, 186))
    pen.setWidthF(1.1 + detail.scale * 0.8)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    painter.setPen(pen)

    blade = QPainterPath(QPointF(detail.center_x, detail.center_y + 4.0 * detail.scale))
    blade.cubicTo(
        detail.center_x + 2.0 * detail.rotation / 24.0,
        detail.center_y - 7.0 * detail.scale,
        detail.center_x + 6.0 * detail.rotation / 24.0,
        detail.center_y - 13.0 * detail.scale,
        detail.center_x + 9.0 * detail.rotation / 24.0,
        detail.center_y - 20.0 * detail.scale,
    )
    painter.drawPath(blade)


def _paint_clover(
    painter: QPainter,
    detail: GroundDetail,
    style: SceneStyle,
) -> None:
    painter.save()
    painter.translate(detail.center_x, detail.center_y)
    painter.rotate(detail.rotation)
    painter.setBrush(_qcolor(style.palette.foliage, 204))

    leaf_size = 6.0 * detail.scale
    for x_offset, y_offset in ((-leaf_size, 0.0), (leaf_size, 0.0), (0.0, -leaf_size)):
        painter.drawEllipse(
            QRectF(x_offset - leaf_size, y_offset - leaf_size, leaf_size * 2.0, leaf_size * 2.0)
        )

    painter.restore()


def _paint_flower(
    painter: QPainter,
    detail: GroundDetail,
    style: SceneStyle,
) -> None:
    painter.setBrush(_qcolor(style.palette.foliage_highlight, 210))
    petal_size = 2.4 * detail.scale
    for x_offset, y_offset in (
        (-petal_size, 0.0),
        (petal_size, 0.0),
        (0.0, -petal_size),
        (0.0, petal_size),
    ):
        painter.drawEllipse(
            QRectF(
                detail.center_x + x_offset - petal_size,
                detail.center_y + y_offset - petal_size,
                petal_size * 2.0,
                petal_size * 2.0,
            )
        )

    painter.setBrush(_qcolor(style.palette.trunk, 220))
    painter.drawEllipse(
        QRectF(
            detail.center_x - petal_size * 0.65,
            detail.center_y - petal_size * 0.65,
            petal_size * 1.3,
            petal_size * 1.3,
        )
    )


def paint_ground(
    painter: QPainter,
    scene: GroundScene,
    style: SceneStyle,
) -> None:
    painter.save()
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setPen(Qt.PenStyle.NoPen)
    path = _outline_path(scene)
    painter.setClipPath(path, Qt.ClipOperation.IntersectClip)

    painter.setBrush(_qcolor(style.palette.soil))
    painter.drawPath(path)
    painter.setOpacity(0.24 + style.ground_lushness * 0.48)
    painter.setBrush(_qcolor(style.palette.moss))
    painter.drawPath(path)
    painter.setOpacity(1.0)

    for detail in scene.moss:
        _paint_moss_patch(painter, detail, style)

    for detail in scene.stones:
        _paint_stone(painter, detail, style)

    for detail in scene.grass:
        _paint_grass(painter, detail, style)

    painter.setPen(Qt.PenStyle.NoPen)
    for detail in scene.clover:
        _paint_clover(painter, detail, style)

    for detail in scene.flowers:
        _paint_flower(painter, detail, style)

    wet_alpha = round(style.wet_highlight_opacity * 255.0)
    if wet_alpha:
        painter.setBrush(_qcolor(style.palette.wet_highlight, wet_alpha))
        for detail in scene.moss[::3]:
            painter.drawEllipse(
                QRectF(
                    detail.center_x - 4.0 * detail.scale,
                    detail.center_y - 1.5 * detail.scale,
                    8.0 * detail.scale,
                    3.0 * detail.scale,
                )
            )

    painter.restore()
