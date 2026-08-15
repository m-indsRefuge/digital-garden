from dataclasses import replace

from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPainter

from digital_garden.desktop.presentation import GardenRenderState
from digital_garden.desktop.scene.style import scene_style
from digital_garden.desktop.scene.vines import (
    build_anchor_vine_scene,
    build_edge_vine_scene,
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

    paint_edge_vines(painter, build_edge_vine_scene(state, style), style)
    painter.end()

    assert any(
        image.pixelColor(x, y).alpha() > 0
        for x in range(420, 520)
        for y in range(240, 390)
    )
