import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from dataclasses import replace

from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPainter
from PySide6.QtWidgets import QApplication

from digital_garden.desktop.presentation import GardenRenderState
from digital_garden.desktop.scene.renderer import QPainterShellRenderer


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


def _paint_patch(state: GardenRenderState) -> QImage:
    app = QApplication.instance() or QApplication([])
    image = QImage(520, 420, QImage.Format.Format_ARGB32_Premultiplied)
    image.fill(Qt.GlobalColor.transparent)
    painter = QPainter(image)
    QPainterShellRenderer().paint_patch(painter, state)
    painter.end()
    app.processEvents()
    return image


def test_weather_changes_static_ground_atmosphere() -> None:
    state = _render_state()
    sunny = _paint_patch(replace(state, weather="SUNNY"))
    rainy = _paint_patch(replace(state, weather="RAINY"))

    assert sunny.pixelColor(260, 360) != rainy.pixelColor(260, 360)
