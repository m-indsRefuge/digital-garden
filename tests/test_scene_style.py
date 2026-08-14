from dataclasses import replace

from digital_garden.desktop.presentation import GardenRenderState
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


def test_style_increases_foliage_vitality_with_authoritative_health() -> None:
    state = _render_state()

    low_health = scene_style(replace(state, bonsai_health=0.15))
    high_health = scene_style(replace(state, bonsai_health=0.90))

    assert high_health.foliage_vitality > low_health.foliage_vitality
    assert high_health.foliage_saturation > low_health.foliage_saturation


def test_style_adds_subtle_canopy_tension_with_authoritative_stress() -> None:
    state = _render_state()

    calm = scene_style(replace(state, bonsai_stress=0.10))
    stressed = scene_style(replace(state, bonsai_stress=0.85))

    assert stressed.canopy_droop > calm.canopy_droop
    assert stressed.exposed_branch_visibility > calm.exposed_branch_visibility


def test_style_maps_authoritative_moisture_to_ground_richness() -> None:
    state = _render_state()

    dry = scene_style(replace(state, soil_moisture=0.10))
    wet = scene_style(replace(state, soil_moisture=0.90))

    assert wet.ground_lushness > dry.ground_lushness
    assert wet.soil_lightness < dry.soil_lightness
    assert wet.wet_highlight_opacity > dry.wet_highlight_opacity


def test_style_maps_authoritative_weather_to_atmosphere() -> None:
    state = _render_state()

    sunny = scene_style(replace(state, weather="SUNNY"))
    rainy = scene_style(replace(state, weather="RAINY"))

    assert sunny.ambient_brightness > rainy.ambient_brightness
    assert sunny.highlight_warmth > rainy.highlight_warmth
    assert rainy.atmosphere_coolness > sunny.atmosphere_coolness


def test_style_maps_authoritative_weather_to_a_painterly_palette() -> None:
    state = _render_state()

    sunny = scene_style(replace(state, weather="SUNNY"))
    rainy = scene_style(replace(state, weather="RAINY"))

    assert sunny.palette.ambient.red > rainy.palette.ambient.red
    assert rainy.palette.ambient.blue > sunny.palette.ambient.blue


def test_style_maps_authoritative_anchor_state_to_compact_vitality() -> None:
    state = _render_state()

    dry = scene_style(replace(state, anchor_state="DRY"))
    thriving = scene_style(replace(state, anchor_state="THRIVING"))

    assert thriving.anchor_vitality > dry.anchor_vitality
    assert thriving.anchor_leaf_color != dry.anchor_leaf_color
