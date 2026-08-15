import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from dataclasses import replace

from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPainter
from PySide6.QtWidgets import QApplication

from digital_garden.desktop.presentation import GardenRenderState
from digital_garden.desktop.scene import renderer as renderer_module
from digital_garden.desktop.scene.bonsai import build_bonsai_scene
from digital_garden.desktop.scene.renderer import QPainterShellRenderer
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


def test_weather_ambient_tints_static_canopy(monkeypatch) -> None:
    state = _render_state()
    base_style = scene_style(state)
    sunny_ambient = scene_style(replace(state, weather="SUNNY")).palette.ambient
    rainy_ambient = scene_style(replace(state, weather="RAINY")).palette.ambient
    sunny_style = replace(
        base_style,
        palette=replace(base_style.palette, ambient=sunny_ambient),
    )
    rainy_style = replace(
        base_style,
        palette=replace(base_style.palette, ambient=rainy_ambient),
    )
    canopy = build_bonsai_scene(state, base_style).canopy[0]
    sample_x = round(canopy.center_x)
    sample_y = round(canopy.center_y)

    monkeypatch.setattr(renderer_module, "scene_style", lambda _state: sunny_style)
    sunny = _paint_patch(state)
    monkeypatch.setattr(renderer_module, "scene_style", lambda _state: rainy_style)
    rainy = _paint_patch(state)

    assert sunny.pixelColor(sample_x, sample_y) != rainy.pixelColor(sample_x, sample_y)
