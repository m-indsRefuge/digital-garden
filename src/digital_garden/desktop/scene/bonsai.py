from dataclasses import dataclass
from math import cos, radians, sin

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import (
    QColor,
    QPainter,
    QPainterPath,
    QPainterPathStroker,
    QPen,
    QRegion,
    QTransform,
)

from digital_garden.desktop.presentation import GardenRenderState
from digital_garden.desktop.scene.lighting import SceneLighting
from digital_garden.desktop.scene.style import Color, SceneStyle
from digital_garden.desktop.scene.variation import stable_unit


@dataclass(frozen=True)
class ScenePoint:
    x: float
    y: float


@dataclass(frozen=True)
class BezierStroke:
    start: ScenePoint
    control_one: ScenePoint
    control_two: ScenePoint
    end: ScenePoint
    width: float


@dataclass(frozen=True)
class SceneBounds:
    left: float
    top: float
    right: float
    bottom: float


@dataclass(frozen=True)
class CanopyLobe:
    offset_x: float
    offset_y: float
    scale_x: float
    scale_y: float


@dataclass(frozen=True)
class CanopyCluster:
    center_x: float
    center_y: float
    radius_x: float
    radius_y: float
    rotation: float
    lobes: tuple[CanopyLobe, ...]


@dataclass(frozen=True)
class BonsaiScene:
    trunk: BezierStroke
    roots: tuple[BezierStroke, ...]
    branches: tuple[BezierStroke, ...]
    canopy: tuple[CanopyCluster, ...]

    @property
    def bounds(self) -> SceneBounds:
        component_bounds = [
            *(_stroke_bounds(stroke) for stroke in (self.trunk, *self.roots, *self.branches)),
            *(_cluster_bounds(cluster) for cluster in self.canopy),
        ]

        return SceneBounds(
            left=min(bounds.left for bounds in component_bounds),
            top=min(bounds.top for bounds in component_bounds),
            right=max(bounds.right for bounds in component_bounds),
            bottom=max(bounds.bottom for bounds in component_bounds),
        )


_CANOPY_SITES = (
    (258.0, 157.0, 48.0, 28.0, -7.0),
    (303.0, 139.0, 54.0, 30.0, 10.0),
    (214.0, 145.0, 45.0, 26.0, -14.0),
    (276.0, 106.0, 50.0, 28.0, 3.0),
    (337.0, 168.0, 42.0, 24.0, 16.0),
    (180.0, 174.0, 38.0, 23.0, -12.0),
    (316.0, 97.0, 37.0, 22.0, 15.0),
    (236.0, 94.0, 34.0, 21.0, -8.0),
    (365.0, 142.0, 31.0, 19.0, 8.0),
)

_CANOPY_LOBE_TEMPLATES = (
    (-0.30, -0.04, 0.52, 0.52),
    (0.28, -0.08, 0.50, 0.48),
    (-0.08, 0.25, 0.56, 0.44),
    (-0.08, -0.28, 0.46, 0.42),
    (0.25, 0.22, 0.43, 0.40),
)

_TRUNK = BezierStroke(
    start=ScenePoint(270.0, 308.0),
    control_one=ScenePoint(238.0, 264.0),
    control_two=ScenePoint(294.0, 214.0),
    end=ScenePoint(258.0, 146.0),
    width=24.0,
)

_ROOT_TEMPLATES = (
    BezierStroke(
        ScenePoint(270.0, 305.0),
        ScenePoint(244.0, 308.0),
        ScenePoint(216.0, 330.0),
        ScenePoint(180.0, 333.0),
        9.0,
    ),
    BezierStroke(
        ScenePoint(270.0, 306.0),
        ScenePoint(278.0, 320.0),
        ScenePoint(312.0, 331.0),
        ScenePoint(356.0, 328.0),
        8.0,
    ),
    BezierStroke(
        ScenePoint(269.0, 303.0),
        ScenePoint(252.0, 321.0),
        ScenePoint(247.0, 337.0),
        ScenePoint(222.0, 342.0),
        6.0,
    ),
)

_BRANCH_TEMPLATES = (
    BezierStroke(
        ScenePoint(257.0, 225.0),
        ScenePoint(230.0, 202.0),
        ScenePoint(201.0, 180.0),
        ScenePoint(172.0, 170.0),
        12.0,
    ),
    BezierStroke(
        ScenePoint(260.0, 192.0),
        ScenePoint(290.0, 171.0),
        ScenePoint(320.0, 144.0),
        ScenePoint(355.0, 137.0),
        11.0,
    ),
    BezierStroke(
        ScenePoint(267.0, 238.0),
        ScenePoint(294.0, 232.0),
        ScenePoint(326.0, 215.0),
        ScenePoint(372.0, 211.0),
        8.0,
    ),
    BezierStroke(
        ScenePoint(250.0, 181.0),
        ScenePoint(231.0, 163.0),
        ScenePoint(221.0, 139.0),
        ScenePoint(214.0, 118.0),
        8.0,
    ),
    BezierStroke(
        ScenePoint(259.0, 164.0),
        ScenePoint(274.0, 145.0),
        ScenePoint(292.0, 120.0),
        ScenePoint(309.0, 101.0),
        7.0,
    ),
)


def _clamp_unit(value: float) -> float:
    return max(0.0, min(1.0, value))


def _stroke_bounds(stroke: BezierStroke) -> SceneBounds:
    points = (stroke.start, stroke.control_one, stroke.control_two, stroke.end)
    radius = stroke.width / 2.0
    return SceneBounds(
        left=min(point.x for point in points) - radius,
        top=min(point.y for point in points) - radius,
        right=max(point.x for point in points) + radius,
        bottom=max(point.y for point in points) + radius,
    )


def _cluster_bounds(cluster: CanopyCluster) -> SceneBounds:
    angle = radians(cluster.rotation)
    half_width = (cluster.radius_x * cos(angle)) ** 2 + (cluster.radius_y * sin(angle)) ** 2
    half_height = (cluster.radius_x * sin(angle)) ** 2 + (cluster.radius_y * cos(angle)) ** 2
    return SceneBounds(
        left=cluster.center_x - half_width**0.5,
        top=cluster.center_y - half_height**0.5,
        right=cluster.center_x + half_width**0.5,
        bottom=cluster.center_y + half_height**0.5,
    )


def _scale_from_origin(
    point: ScenePoint,
    origin: ScenePoint,
    horizontal_scale: float,
    vertical_scale: float = 1.0,
) -> ScenePoint:
    return ScenePoint(
        x=origin.x + (point.x - origin.x) * horizontal_scale,
        y=origin.y + (point.y - origin.y) * vertical_scale,
    )


def _scaled_branch(branch: BezierStroke, reach: float) -> BezierStroke:
    return BezierStroke(
        start=branch.start,
        control_one=_scale_from_origin(branch.control_one, branch.start, reach, reach),
        control_two=_scale_from_origin(branch.control_two, branch.start, reach, reach),
        end=_scale_from_origin(branch.end, branch.start, reach, reach),
        width=branch.width * (0.78 + reach * 0.22),
    )


def _flared_root(root: BezierStroke, flare: float) -> BezierStroke:
    return BezierStroke(
        start=root.start,
        control_one=_scale_from_origin(root.control_one, root.start, flare),
        control_two=_scale_from_origin(root.control_two, root.start, flare),
        end=_scale_from_origin(root.end, root.start, flare),
        width=root.width * flare,
    )


def _canopy_lobes(seed: int, cluster_index: int) -> tuple[CanopyLobe, ...]:
    return tuple(
        CanopyLobe(
            offset_x=offset_x
            + (stable_unit(seed, f"canopy-lobe-x-{cluster_index}", lobe_index) - 0.5) * 0.06,
            offset_y=offset_y
            + (stable_unit(seed, f"canopy-lobe-y-{cluster_index}", lobe_index) - 0.5) * 0.06,
            scale_x=scale_x
            + (stable_unit(seed, f"canopy-lobe-width-{cluster_index}", lobe_index) - 0.5) * 0.04,
            scale_y=scale_y
            + (stable_unit(seed, f"canopy-lobe-height-{cluster_index}", lobe_index) - 0.5) * 0.04,
        )
        for lobe_index, (offset_x, offset_y, scale_x, scale_y) in enumerate(
            _CANOPY_LOBE_TEMPLATES
        )
    )


def _qcolor(color: Color, alpha: int | None = None) -> QColor:
    return QColor(color.red, color.green, color.blue, color.alpha if alpha is None else alpha)


def _darkened(color: Color, amount: float) -> QColor:
    factor = 1.0 - amount
    return QColor(
        round(color.red * factor),
        round(color.green * factor),
        round(color.blue * factor),
        color.alpha,
    )


def _stroke_path(stroke: BezierStroke) -> QPainterPath:
    path = QPainterPath(QPointF(stroke.start.x, stroke.start.y))
    path.cubicTo(
        QPointF(stroke.control_one.x, stroke.control_one.y),
        QPointF(stroke.control_two.x, stroke.control_two.y),
        QPointF(stroke.end.x, stroke.end.y),
    )
    return path


def _paint_stroke(
    painter: QPainter,
    stroke: BezierStroke,
    color: QColor,
    opacity: float = 1.0,
) -> None:
    pen = QPen(color)
    pen.setWidthF(stroke.width)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)

    painter.save()
    painter.setOpacity(opacity)
    painter.setPen(pen)
    painter.setBrush(Qt.BrushStyle.NoBrush)
    painter.drawPath(_stroke_path(stroke))
    painter.restore()


def _stroke_region(stroke: BezierStroke) -> QRegion:
    stroker = QPainterPathStroker()
    stroker.setWidth(stroke.width + 6.0)
    stroker.setCapStyle(Qt.PenCapStyle.RoundCap)
    stroker.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    path = stroker.createStroke(_stroke_path(stroke))
    return QRegion(path.toFillPolygon().toPolygon())


def _cluster_region(cluster: CanopyCluster) -> QRegion:
    path = QPainterPath()
    path.addEllipse(
        QRectF(
            -cluster.radius_x,
            -cluster.radius_y,
            cluster.radius_x * 2.0,
            cluster.radius_y * 2.0,
        )
    )
    transform = QTransform()
    transform.translate(cluster.center_x, cluster.center_y)
    transform.rotate(cluster.rotation)
    return QRegion(transform.map(path).toFillPolygon().toPolygon())


def bonsai_mask_region(scene: BonsaiScene) -> QRegion:
    region = _stroke_region(scene.trunk)

    for stroke in (*scene.roots, *scene.branches):
        region = region.united(_stroke_region(stroke))

    for cluster in scene.canopy:
        region = region.united(_cluster_region(cluster))

    return region


def paint_bonsai(
    painter: QPainter,
    scene: BonsaiScene,
    style: SceneStyle,
    lighting: SceneLighting,
) -> None:
    painter.save()
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)

    trunk_shadow = _darkened(style.palette.trunk, 0.34)
    for root in scene.roots:
        _paint_stroke(painter, root, trunk_shadow, 0.88)

    branch_opacity = 0.48 + style.exposed_branch_visibility * 0.42
    for branch in scene.branches:
        _paint_stroke(painter, branch, _darkened(style.palette.trunk, 0.20), branch_opacity)

    _paint_stroke(painter, scene.trunk, _qcolor(style.palette.trunk))
    painter.save()
    painter.translate(lighting.highlight_offset.x(), lighting.highlight_offset.y())
    _paint_stroke(
        painter,
        BezierStroke(
            start=scene.trunk.start,
            control_one=scene.trunk.control_one,
            control_two=scene.trunk.control_two,
            end=scene.trunk.end,
            width=scene.trunk.width * 0.24,
        ),
        _qcolor(style.palette.foliage_highlight, lighting.highlight_alpha),
        0.46,
    )
    painter.restore()

    for cluster in scene.canopy:
        painter.save()
        painter.translate(cluster.center_x, cluster.center_y)
        painter.rotate(cluster.rotation)
        painter.setPen(Qt.PenStyle.NoPen)

        envelope = QPainterPath()
        envelope.addEllipse(
            QRectF(
                -cluster.radius_x,
                -cluster.radius_y,
                cluster.radius_x * 2.0,
                cluster.radius_y * 2.0,
            )
        )
        painter.setClipPath(envelope, Qt.ClipOperation.IntersectClip)

        painter.setBrush(_qcolor(style.palette.foliage_shadow, 150 + lighting.shadow_alpha))
        painter.drawPath(envelope)

        shadow_x = lighting.shadow_offset.x() * 0.22
        shadow_y = lighting.shadow_offset.y() * 0.22
        highlight_x = lighting.highlight_offset.x() * 0.28
        highlight_y = lighting.highlight_offset.y() * 0.28

        for lobe in cluster.lobes:
            center_x = lobe.offset_x * cluster.radius_x
            center_y = lobe.offset_y * cluster.radius_y
            radius_x = lobe.scale_x * cluster.radius_x
            radius_y = lobe.scale_y * cluster.radius_y

            painter.setOpacity(0.58)
            painter.setBrush(_qcolor(style.palette.foliage_shadow, lighting.shadow_alpha))
            painter.drawEllipse(
                QRectF(
                    center_x - radius_x + shadow_x,
                    center_y - radius_y + shadow_y,
                    radius_x * 2.0,
                    radius_y * 2.0,
                )
            )

            painter.setOpacity(1.0)
            painter.setBrush(_qcolor(style.palette.foliage))
            painter.drawEllipse(
                QRectF(
                    center_x - radius_x,
                    center_y - radius_y,
                    radius_x * 2.0,
                    radius_y * 2.0,
                )
            )

            painter.setOpacity(0.18 + style.foliage_vitality * 0.26)
            painter.setBrush(_qcolor(style.palette.foliage_highlight, lighting.highlight_alpha))
            highlight_radius_x = radius_x * 0.56
            highlight_radius_y = radius_y * 0.44
            painter.drawEllipse(
                QRectF(
                    center_x - highlight_radius_x + highlight_x,
                    center_y - highlight_radius_y + highlight_y,
                    highlight_radius_x * 2.0,
                    highlight_radius_y * 2.0,
                )
            )

        painter.restore()

    painter.restore()


def build_bonsai_scene(
    state: GardenRenderState,
    style: SceneStyle,
) -> BonsaiScene:
    density = _clamp_unit(state.canopy_density)
    visible_count = 3 + int((len(_CANOPY_SITES) - 3) * density)
    droop = style.canopy_droop * 80.0

    canopy = tuple(
        CanopyCluster(
            center_x=center_x + (stable_unit(state.seed, "canopy-x", index) - 0.5) * 10.0,
            center_y=center_y + droop + (stable_unit(state.seed, "canopy-y", index) - 0.5) * 8.0,
            radius_x=radius_x
            * style.canopy_spread
            * (0.88 + stable_unit(state.seed, "canopy-width", index) * 0.22),
            radius_y=radius_y
            * style.canopy_spread
            * (0.88 + stable_unit(state.seed, "canopy-height", index) * 0.22),
            rotation=rotation + (stable_unit(state.seed, "canopy-rotation", index) - 0.5) * 8.0,
            lobes=_canopy_lobes(state.seed, index),
        )
        for index, (center_x, center_y, radius_x, radius_y, rotation) in enumerate(
            _CANOPY_SITES[:visible_count]
        )
    )

    trunk = BezierStroke(
        start=_TRUNK.start,
        control_one=_TRUNK.control_one,
        control_two=_TRUNK.control_two,
        end=_TRUNK.end,
        width=_TRUNK.width * style.root_flare,
    )

    return BonsaiScene(
        trunk=trunk,
        roots=tuple(_flared_root(root, style.root_flare) for root in _ROOT_TEMPLATES),
        branches=tuple(_scaled_branch(branch, style.branch_reach) for branch in _BRANCH_TEMPLATES),
        canopy=canopy,
    )
