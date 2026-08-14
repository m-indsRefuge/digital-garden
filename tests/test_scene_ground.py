from dataclasses import replace

from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QImage, QPainter

from digital_garden.desktop.presentation import GardenRenderState
from digital_garden.desktop.scene.ground import (
    build_ground_scene,
    ground_mask_region,
    paint_ground,
)
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


def test_ground_density_reveals_a_stable_prefix_of_clover_sites() -> None:
    state = _render_state()

    sparse = build_ground_scene(
        replace(state, ground_density=0.25),
        scene_style(state),
    )
    lush = build_ground_scene(
        replace(state, ground_density=0.75),
        scene_style(state),
    )

    assert 0 < len(sparse.clover) < len(lush.clover)
    assert lush.clover[: len(sparse.clover)] == sparse.clover


def test_ground_scene_defines_an_organic_patch_inside_the_expanded_bounds() -> None:
    state = _render_state()
    scene = build_ground_scene(state, scene_style(state))

    assert len(scene.outline) >= 12
    assert all(0.0 <= point.x <= 520.0 and 0.0 <= point.y <= 420.0 for point in scene.outline)
    assert min(point.y for point in scene.outline) < 280.0
    assert max(point.y for point in scene.outline) > 380.0


def test_dense_ground_composes_all_stable_botanical_detail_families() -> None:
    state = replace(_render_state(), ground_density=0.75)
    scene = build_ground_scene(state, scene_style(state))

    assert scene.moss
    assert scene.grass
    assert scene.flowers
    assert scene.stones


def test_paint_ground_draws_a_prepared_organic_patch() -> None:
    state = _render_state()
    style = scene_style(state)
    image = QImage(520, 420, QImage.Format.Format_ARGB32_Premultiplied)
    image.fill(Qt.GlobalColor.transparent)
    painter = QPainter(image)

    paint_ground(painter, build_ground_scene(state, style), style)
    painter.end()

    assert any(
        image.pixelColor(x, y).alpha() > 0 for x in range(40, 500, 20) for y in range(260, 405, 20)
    )


def test_ground_mask_contains_visible_cover_but_not_the_transparent_corner() -> None:
    state = _render_state()
    scene = build_ground_scene(state, scene_style(state))
    mask = ground_mask_region(scene)

    assert mask.contains(QPoint(round(scene.clover[0].center_x), round(scene.clover[0].center_y)))
    assert not mask.contains(QPoint(10, 10))


def test_ground_mask_covers_the_opaque_ground_rendering() -> None:
    state = _render_state()
    style = scene_style(state)
    scene = build_ground_scene(state, style)
    image = QImage(520, 420, QImage.Format.Format_ARGB32_Premultiplied)
    image.fill(Qt.GlobalColor.transparent)
    painter = QPainter(image)

    paint_ground(painter, scene, style)
    painter.end()

    mask = ground_mask_region(scene)
    outside_mask = [
        QPoint(x, y)
        for x in range(image.width())
        for y in range(image.height())
        if image.pixelColor(x, y).alpha() > 0 and not mask.contains(QPoint(x, y))
    ]

    assert not outside_mask
