from dataclasses import dataclass

from PySide6.QtCore import QPointF, Qt
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPen

from digital_garden.desktop.presentation import GardenRenderState
from digital_garden.desktop.scene.style import Color, SceneStyle
from digital_garden.desktop.scene.variation import (
    candidate_pool,
    stable_unit,
    visible_candidates,
)


@dataclass(frozen=True)
class VinePoint:
    x: float
    y: float


@dataclass(frozen=True)
class VineStem:
    start: VinePoint
    control_one: VinePoint
    control_two: VinePoint
    end: VinePoint
    width: float


@dataclass(frozen=True)
class VineLeaf:
    center: VinePoint
    radius_x: float
    radius_y: float
    angle: float
    form: str
    opacity: float


@dataclass(frozen=True)
class EdgeVineScene:
    stems: tuple[VineStem, ...]


@dataclass(frozen=True)
class AnchorVineScene:
    stems: tuple[VineStem, ...]
    leaves: tuple[VineLeaf, ...]
    vitality: float


def _qcolor(color: Color, alpha: int | None = None) -> QColor:
    return QColor(
        color.red,
        color.green,
        color.blue,
        color.alpha if alpha is None else alpha,
    )


def _stem_path(stem: VineStem) -> QPainterPath:
    path = QPainterPath(QPointF(stem.start.x, stem.start.y))
    path.cubicTo(
        QPointF(stem.control_one.x, stem.control_one.y),
        QPointF(stem.control_two.x, stem.control_two.y),
        QPointF(stem.end.x, stem.end.y),
    )
    return path


def paint_edge_vines(
    painter: QPainter,
    scene: EdgeVineScene,
    style: SceneStyle,
) -> None:
    painter.save()
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setBrush(Qt.BrushStyle.NoBrush)

    for stem in scene.stems:
        pen = QPen(_qcolor(style.palette.vine, 210))
        pen.setWidthF(stem.width)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.drawPath(_stem_path(stem))

    painter.restore()


def build_edge_vine_scene(
    state: GardenRenderState,
    _style: SceneStyle,
) -> EdgeVineScene:
    extent = max(0.0, min(1.0, state.vine_extent))
    candidates = candidate_pool(state.seed, "edge-vine", 5)
    visible = visible_candidates(candidates, 0.25 + extent * 0.75)
    stems = tuple(
        _edge_stem(candidate.x, candidate.y, candidate.scale, extent)
        for candidate in visible
    )
    return EdgeVineScene(stems=stems)


def _edge_stem(x: float, y: float, scale: float, extent: float) -> VineStem:
    start = VinePoint(426.0 + x * 42.0, 326.0 + y * 50.0)
    reach = 24.0 + extent * (42.0 + scale * 16.0)
    end = VinePoint(min(516.0, start.x + reach), start.y - (18.0 + y * 28.0))
    return VineStem(
        start=start,
        control_one=VinePoint(start.x + reach * 0.24, start.y - 18.0 * scale),
        control_two=VinePoint(end.x - reach * 0.30, end.y + 16.0 * scale),
        end=end,
        width=1.6 + scale * 1.1,
    )


def build_anchor_vine_scene(
    state: GardenRenderState,
    style: SceneStyle,
) -> AnchorVineScene:
    vitality = style.anchor_vitality
    leaf_scale = 0.72 + vitality * 0.34
    stems = (
        VineStem(
            start=VinePoint(47.0, 168.0),
            control_one=VinePoint(36.0, 131.0),
            control_two=VinePoint(60.0, 78.0),
            end=VinePoint(45.0, 16.0),
            width=2.4 + vitality * 1.7,
        ),
        VineStem(
            start=VinePoint(47.0, 123.0),
            control_one=VinePoint(64.0, 109.0),
            control_two=VinePoint(29.0, 78.0),
            end=VinePoint(52.0, 48.0),
            width=1.4 + vitality * 1.1,
        ),
    )
    leaves = tuple(
        _anchor_leaf(
            state,
            index,
            x,
            y,
            radius_x,
            radius_y,
            angle,
            form,
            leaf_scale,
            vitality,
        )
        for index, (x, y, radius_x, radius_y, angle, form) in enumerate(
            (
                (34.0, 37.0, 10.0, 6.0, -36.0, "pointed"),
                (57.0, 60.0, 11.0, 7.0, 28.0, "round"),
                (31.0, 93.0, 12.0, 6.5, -28.0, "pointed"),
                (60.0, 125.0, 10.0, 7.0, 35.0, "round"),
                (42.0, 148.0, 8.0, 5.0, -8.0, "pointed"),
            )
        )
    )
    return AnchorVineScene(stems=stems, leaves=leaves, vitality=vitality)


def _anchor_leaf(
    state: GardenRenderState,
    index: int,
    x: float,
    y: float,
    radius_x: float,
    radius_y: float,
    angle: float,
    form: str,
    leaf_scale: float,
    vitality: float,
) -> VineLeaf:
    return VineLeaf(
        center=VinePoint(
            x + (stable_unit(state.seed, "anchor-leaf-x", index) - 0.5) * 3.0,
            y + (stable_unit(state.seed, "anchor-leaf-y", index) - 0.5) * 3.0,
        ),
        radius_x=radius_x * leaf_scale,
        radius_y=radius_y * leaf_scale,
        angle=angle + (stable_unit(state.seed, "anchor-leaf-angle", index) - 0.5) * 8.0,
        form=form,
        opacity=0.56 + vitality * 0.40,
    )
