from dataclasses import dataclass

from digital_garden.desktop.presentation import GardenRenderState


@dataclass(frozen=True)
class Color:
    red: int
    green: int
    blue: int
    alpha: int = 255


@dataclass(frozen=True)
class ScenePalette:
    ambient: Color
    anchor_leaf: Color
    foliage: Color
    foliage_highlight: Color
    foliage_shadow: Color
    moss: Color
    overlay_backing: Color
    overlay_text: Color
    soil: Color
    trunk: Color
    vine: Color
    wet_highlight: Color


@dataclass(frozen=True)
class _WeatherAtmosphere:
    brightness: float
    warmth: float
    coolness: float
    ambient: Color


_WEATHER_ATMOSPHERE = {
    "SUNNY": _WeatherAtmosphere(0.82, 0.72, 0.12, Color(239, 195, 118, 38)),
    "CLOUDY": _WeatherAtmosphere(0.62, 0.34, 0.42, Color(152, 177, 165, 34)),
    "RAINY": _WeatherAtmosphere(0.42, 0.14, 0.78, Color(74, 118, 151, 56)),
}

_ANCHOR_VITALITY = {
    "CALM": (0.58, "#6f9664"),
    "DRY": (0.30, "#9b7d4f"),
    "WILD": (0.72, "#4f8b45"),
    "THRIVING": (0.92, "#80b763"),
    "STRESSED": (0.40, "#756653"),
}

_LOW_HEALTH_FOLIAGE = Color(102, 103, 71)
_HEALTHY_FOLIAGE = Color(65, 122, 67)
_STRESSED_FOLIAGE = Color(112, 103, 79)
_DRY_MOSS = Color(95, 104, 62)
_WET_MOSS = Color(45, 108, 70)
_DRY_SOIL = Color(142, 105, 70)
_WET_SOIL = Color(83, 67, 52)


def _mix_color(first: Color, second: Color, amount: float) -> Color:
    amount = _clamp_unit(amount)
    return Color(
        red=round(first.red + (second.red - first.red) * amount),
        green=round(first.green + (second.green - first.green) * amount),
        blue=round(first.blue + (second.blue - first.blue) * amount),
        alpha=round(first.alpha + (second.alpha - first.alpha) * amount),
    )


def _color_from_hex(value: str) -> Color:
    return Color(
        red=int(value[1:3], 16),
        green=int(value[3:5], 16),
        blue=int(value[5:7], 16),
    )


@dataclass(frozen=True)
class SceneStyle:
    anchor_leaf_color: str
    anchor_vitality: float
    ambient_brightness: float
    atmosphere_coolness: float
    canopy_droop: float
    exposed_branch_visibility: float
    foliage_vitality: float
    foliage_saturation: float
    ground_lushness: float
    highlight_warmth: float
    palette: ScenePalette
    soil_lightness: float
    wet_highlight_opacity: float


def _clamp_unit(value: float) -> float:
    return max(0.0, min(1.0, value))


def scene_style(state: GardenRenderState) -> SceneStyle:
    health = _clamp_unit(state.bonsai_health)
    light_level = _clamp_unit(state.light_level)
    moisture = _clamp_unit(state.soil_moisture)
    stress = _clamp_unit(state.bonsai_stress)
    humidity = _clamp_unit(state.humidity)
    weather_style = _WEATHER_ATMOSPHERE.get(
        state.weather,
        _WEATHER_ATMOSPHERE["CLOUDY"],
    )
    anchor_vitality, anchor_leaf_color = _ANCHOR_VITALITY.get(
        state.anchor_state,
        _ANCHOR_VITALITY["CALM"],
    )
    foliage = _mix_color(_LOW_HEALTH_FOLIAGE, _HEALTHY_FOLIAGE, health)
    foliage = _mix_color(foliage, _STRESSED_FOLIAGE, stress * 0.24)
    moss = _mix_color(_DRY_MOSS, _WET_MOSS, moisture)
    soil = _mix_color(_DRY_SOIL, _WET_SOIL, moisture)
    palette = ScenePalette(
        ambient=weather_style.ambient,
        anchor_leaf=_color_from_hex(anchor_leaf_color),
        foliage=foliage,
        foliage_highlight=_mix_color(foliage, Color(230, 224, 175), 0.26),
        foliage_shadow=_mix_color(foliage, Color(24, 50, 34), 0.42),
        moss=moss,
        overlay_backing=Color(20, 43, 32, 138),
        overlay_text=Color(232, 240, 214),
        soil=soil,
        trunk=_mix_color(Color(112, 76, 49), Color(84, 61, 43), state.bonsai_growth),
        vine=_mix_color(moss, _color_from_hex(anchor_leaf_color), 0.30),
        wet_highlight=Color(195, 215, 204, round(90 * moisture)),
    )

    return SceneStyle(
        anchor_leaf_color=anchor_leaf_color,
        anchor_vitality=anchor_vitality,
        ambient_brightness=weather_style.brightness * 0.72 + light_level * 0.28,
        atmosphere_coolness=_clamp_unit(weather_style.coolness + humidity * 0.08),
        canopy_droop=stress * 0.16,
        exposed_branch_visibility=0.20 + stress * 0.42,
        foliage_vitality=0.35 + health * 0.65,
        foliage_saturation=0.28 + health * 0.42,
        ground_lushness=0.30 + moisture * 0.55,
        highlight_warmth=weather_style.warmth,
        palette=palette,
        soil_lightness=0.62 - moisture * 0.24,
        wet_highlight_opacity=moisture * 0.35,
    )
