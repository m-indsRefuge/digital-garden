import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QPoint, Qt
from PySide6.QtGui import QImage, QPainter
from PySide6.QtWidgets import QApplication

from digital_garden.desktop.controller import DesktopController
from digital_garden.desktop.presentation import GardenRenderState
from digital_garden.desktop.scene.bonsai import build_bonsai_scene
from digital_garden.desktop.scene.renderer import QPainterShellRenderer
from digital_garden.desktop.scene.style import scene_style
from digital_garden.domain import make_initial_state
from digital_garden.service import GardenService


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


def test_patch_mask_contains_the_current_bonsai_scene_geometry() -> None:
    state = _render_state()
    scene = build_bonsai_scene(state, scene_style(state))

    mask = QPainterShellRenderer().patch_mask(state)

    assert mask.contains(QPoint(round(scene.trunk.start.x), round(scene.trunk.start.y)))
    assert mask.contains(QPoint(round(scene.branches[-1].end.x), round(scene.branches[-1].end.y)))
    assert mask.contains(QPoint(round(scene.canopy[-1].center_x), round(scene.canopy[-1].center_y)))


def test_patch_rendering_does_not_mutate_authoritative_service_state() -> None:
    app = QApplication.instance() or QApplication([])
    service = GardenService(make_initial_state(seed=7))
    state = DesktopController(service).render_state()
    before = service.state
    image = QImage(520, 420, QImage.Format.Format_ARGB32_Premultiplied)
    image.fill(Qt.GlobalColor.transparent)
    painter = QPainter(image)

    QPainterShellRenderer().paint_patch(painter, state)
    painter.end()

    assert service.state == before
    app.processEvents()
