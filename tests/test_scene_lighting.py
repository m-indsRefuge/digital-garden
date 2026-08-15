import importlib
from dataclasses import replace

from digital_garden.desktop.presentation import GardenRenderState
from digital_garden.desktop.scene.style import scene_style


def _state() -> GardenRenderState:
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


def test_scene_lighting_keeps_one_direction_but_weather_changes_strength() -> None:
    try:
        lighting_module = importlib.import_module("digital_garden.desktop.scene.lighting")
    except ModuleNotFoundError:
        lighting_module = None

    assert lighting_module is not None, "scene lighting contract is not implemented"

    state = _state()
    sunny = lighting_module.scene_lighting(scene_style(replace(state, weather="SUNNY")))
    rainy = lighting_module.scene_lighting(scene_style(replace(state, weather="RAINY")))

    assert sunny.shadow_offset == rainy.shadow_offset
    assert sunny.highlight_offset == rainy.highlight_offset
    assert sunny.highlight_alpha > rainy.highlight_alpha
    assert rainy.shadow_alpha > sunny.shadow_alpha
