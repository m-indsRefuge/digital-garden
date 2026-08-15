from dataclasses import replace

from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QImage, QPainter

from digital_garden.desktop.presentation import GardenRenderState
from digital_garden.desktop.scene.bonsai import (
    bonsai_mask_region,
    build_bonsai_scene,
    paint_bonsai,
)
from digital_garden.desktop.scene.lighting import scene_lighting
from digital_garden.desktop.scene.style import scene_style


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


def test_canopy_density_reveals_a_stable_subset_of_asymmetric_clusters() -> None:
    state = _render_state()

    sparse = build_bonsai_scene(
        replace(state, canopy_density=0.20),
        scene_style(state),
    )
    dense = build_bonsai_scene(
        replace(state, canopy_density=0.85),
        scene_style(state),
    )

    assert 0 < len(sparse.canopy) < len(dense.canopy)
    assert dense.canopy[: len(sparse.canopy)] == sparse.canopy


def test_canopy_clusters_have_seed_stable_irregular_lobes() -> None:
    state = _render_state()
    scene = build_bonsai_scene(state, scene_style(state))
    again = build_bonsai_scene(state, scene_style(state))

    assert scene.canopy == again.canopy
    assert all(len(cluster.lobes) == 5 for cluster in scene.canopy)
    assert any(
        lobe.offset_x != 0.0 or lobe.offset_y != 0.0
        for cluster in scene.canopy
        for lobe in cluster.lobes
    )


def test_canopy_lobes_affect_the_rendered_bonsai_surface() -> None:
    state = _render_state()
    style = scene_style(state)
    lighting = scene_lighting(style)
    scene = build_bonsai_scene(state, style)
    plain_scene = replace(
        scene,
        canopy=tuple(replace(cluster, lobes=()) for cluster in scene.canopy),
    )

    def painted(prepared_scene):
        image = QImage(520, 420, QImage.Format.Format_ARGB32_Premultiplied)
        image.fill(Qt.GlobalColor.transparent)
        painter = QPainter(image)
        paint_bonsai(painter, prepared_scene, style, lighting)
        painter.end()
        return image

    textured = painted(scene)
    plain = painted(plain_scene)

    assert any(
        textured.pixelColor(x, y) != plain.pixelColor(x, y)
        for x in range(140, 410, 2)
        for y in range(65, 220, 2)
    )


def test_bonsai_scene_composes_a_curved_trunk_roots_and_readable_branches() -> None:
    state = _render_state()
    scene = build_bonsai_scene(state, scene_style(state))

    assert scene.trunk.start.y > scene.trunk.end.y
    assert scene.trunk.start.x != scene.trunk.control_one.x
    assert scene.trunk.control_one.x != scene.trunk.control_two.x
    assert len(scene.roots) >= 3
    assert len(scene.branches) >= 4


def test_growth_expands_existing_canopy_identity_without_relocating_it() -> None:
    state = _render_state()
    young_state = replace(state, bonsai_growth=0.10)
    mature_state = replace(state, bonsai_growth=0.90)

    young = build_bonsai_scene(young_state, scene_style(young_state))
    mature = build_bonsai_scene(mature_state, scene_style(mature_state))

    assert [cluster.center_x for cluster in mature.canopy] == [
        cluster.center_x for cluster in young.canopy
    ]
    assert mature.canopy[0].radius_x > young.canopy[0].radius_x
    assert mature.canopy[0].radius_y > young.canopy[0].radius_y


def test_bonsai_scene_exposes_bounds_inside_the_expanded_patch() -> None:
    state = _render_state()
    scene = build_bonsai_scene(state, scene_style(state))

    assert 0.0 <= scene.bounds.left < scene.bounds.right <= 520.0
    assert 0.0 <= scene.bounds.top < scene.bounds.bottom <= 420.0
    assert scene.bounds.left <= scene.trunk.start.x <= scene.bounds.right
    assert scene.bounds.top <= scene.trunk.end.y <= scene.bounds.bottom


def test_paint_bonsai_draws_a_prepared_scene_without_garden_access() -> None:
    state = _render_state()
    style = scene_style(state)
    image = QImage(520, 420, QImage.Format.Format_ARGB32_Premultiplied)
    image.fill(Qt.GlobalColor.transparent)
    painter = QPainter(image)

    paint_bonsai(
        painter,
        build_bonsai_scene(state, style),
        style,
        scene_lighting(style),
    )
    painter.end()

    assert any(
        image.pixelColor(x, y).alpha() > 0 for x in range(150, 390, 15) for y in range(90, 345, 15)
    )


def test_bonsai_mask_contains_key_prepared_scene_structures() -> None:
    state = _render_state()
    scene = build_bonsai_scene(state, scene_style(state))
    mask = bonsai_mask_region(scene)

    assert mask.contains(QPoint(round(scene.trunk.start.x), round(scene.trunk.start.y)))
    assert mask.contains(QPoint(round(scene.trunk.end.x), round(scene.trunk.end.y)))
    assert all(
        mask.contains(QPoint(round(cluster.center_x), round(cluster.center_y)))
        for cluster in scene.canopy
    )
