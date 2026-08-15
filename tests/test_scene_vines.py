from dataclasses import replace

from PySide6.QtCore import QPoint, QPointF, Qt
from PySide6.QtGui import QImage, QPainter

from digital_garden.desktop.presentation import GardenRenderState
from digital_garden.desktop.scene.lighting import scene_lighting
from digital_garden.desktop.scene.style import scene_style
from digital_garden.desktop.scene.vines import (
    anchor_vine_mask_region,
    build_anchor_vine_scene,
    build_edge_vine_scene,
    edge_vine_mask_region,
    paint_anchor_vine,
    paint_edge_vines,
)


def _render_state() -> GardenRenderState:
    return GardenRenderState(
        seed=7,
        tick=12,
        weather="CLOUDY",
        light_level=0.55,
        humidity=0.60,
        soil_moisture=0.50,
        bonsai_health=0.50,
        bonsai_stress=0.20,
        bonsai_growth=0.40,
        canopy_density=0.60,
        ground_density=0.50,
        vine_extent=0.40,
        condition="HEALTHY",
        anchor_state="CALM",
    )


def test_vine_extent_increases_stable_edge_vine_spread() -> None:
    state = _render_state()
    compact_state = replace(state, vine_extent=0.10)
    expanded_state = replace(state, vine_extent=0.90)

    compact = build_edge_vine_scene(compact_state, scene_style(compact_state))
    expanded = build_edge_vine_scene(expanded_state, scene_style(expanded_state))

    assert 0 < len(compact.stems) < len(expanded.stems)
    assert expanded.stems[0].end.x > compact.stems[0].end.x


def test_edge_vines_gain_seed_stable_leaves_as_extent_grows() -> None:
    state = _render_state()
    low_state = replace(state, vine_extent=0.15)
    high_state = replace(state, vine_extent=0.90)

    low = build_edge_vine_scene(low_state, scene_style(low_state))
    high = build_edge_vine_scene(high_state, scene_style(high_state))
    high_again = build_edge_vine_scene(high_state, scene_style(high_state))

    assert high == high_again
    assert len(high.leaves) > len(low.leaves)


def test_edge_vine_paint_responds_to_scene_lighting() -> None:
    state = replace(_render_state(), vine_extent=0.90)
    style = scene_style(state)
    scene = build_edge_vine_scene(state, style)
    lighting = scene_lighting(style)
    neutral = replace(
        lighting,
        shadow_offset=QPointF(0.0, 0.0),
        highlight_offset=QPointF(0.0, 0.0),
        shadow_alpha=0,
        highlight_alpha=0,
    )
    directional = replace(
        lighting,
        shadow_offset=QPointF(6.0, 7.0),
        highlight_offset=QPointF(-3.0, -4.0),
        shadow_alpha=84,
        highlight_alpha=116,
    )

    def painted(prepared_lighting):
        image = QImage(520, 420, QImage.Format.Format_ARGB32_Premultiplied)
        image.fill(Qt.GlobalColor.transparent)
        painter = QPainter(image)
        paint_edge_vines(painter, scene, style, prepared_lighting)
        painter.end()
        return image

    flat = painted(neutral)
    lit = painted(directional)

    assert any(
        flat.pixelColor(x, y) != lit.pixelColor(x, y)
        for x in range(420, 520, 2)
        for y in range(240, 390, 2)
    )


def test_anchor_state_controls_compact_vine_vitality_and_leaf_forms() -> None:
    state = _render_state()
    dry_state = replace(state, anchor_state="DRY")
    thriving_state = replace(state, anchor_state="THRIVING")

    dry = build_anchor_vine_scene(dry_state, scene_style(dry_state))
    thriving = build_anchor_vine_scene(thriving_state, scene_style(thriving_state))

    assert thriving.vitality > dry.vitality
    assert max(leaf.radius_x for leaf in thriving.leaves) > max(
        leaf.radius_x for leaf in dry.leaves
    )
    assert {leaf.form for leaf in thriving.leaves} >= {"round", "pointed"}


def test_paint_edge_vines_draws_a_prepared_scene_model() -> None:
    state = replace(_render_state(), vine_extent=0.80)
    style = scene_style(state)
    image = QImage(520, 420, QImage.Format.Format_ARGB32_Premultiplied)
    image.fill(Qt.GlobalColor.transparent)
    painter = QPainter(image)

    paint_edge_vines(
        painter,
        build_edge_vine_scene(state, style),
        style,
        scene_lighting(style),
    )
    painter.end()

    assert any(image.pixelColor(x, y).alpha() > 0 for x in range(420, 520) for y in range(240, 390))


def test_paint_anchor_vine_draws_the_prepared_compact_scene() -> None:
    state = replace(_render_state(), anchor_state="THRIVING")
    style = scene_style(state)
    image = QImage(96, 180, QImage.Format.Format_ARGB32_Premultiplied)
    image.fill(Qt.GlobalColor.transparent)
    painter = QPainter(image)

    paint_anchor_vine(
        painter,
        build_anchor_vine_scene(state, style),
        style,
        scene_lighting(style),
    )
    painter.end()

    assert any(image.pixelColor(x, y).alpha() > 0 for x in range(15, 80) for y in range(8, 172))


def test_vine_masks_are_derived_from_the_prepared_geometry() -> None:
    state = replace(_render_state(), vine_extent=0.80)
    style = scene_style(state)
    edge = build_edge_vine_scene(state, style)
    anchor = build_anchor_vine_scene(state, style)

    edge_mask = edge_vine_mask_region(edge)
    anchor_mask = anchor_vine_mask_region(anchor)

    for stem in edge.stems:
        assert edge_mask.contains(QPoint(round(stem.start.x), round(stem.start.y)))
        assert edge_mask.contains(QPoint(round(stem.end.x), round(stem.end.y)))

    for leaf in edge.leaves:
        assert edge_mask.contains(QPoint(round(leaf.center.x), round(leaf.center.y)))

    for stem in anchor.stems:
        assert anchor_mask.contains(QPoint(round(stem.start.x), round(stem.start.y)))
        assert anchor_mask.contains(QPoint(round(stem.end.x), round(stem.end.y)))

    for leaf in anchor.leaves:
        assert anchor_mask.contains(QPoint(round(leaf.center.x), round(leaf.center.y)))
