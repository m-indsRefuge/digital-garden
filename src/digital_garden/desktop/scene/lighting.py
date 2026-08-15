from dataclasses import dataclass

from PySide6.QtCore import QPointF

from digital_garden.desktop.scene.style import SceneStyle


@dataclass(frozen=True)
class SceneLighting:
    shadow_offset: QPointF
    highlight_offset: QPointF
    shadow_alpha: int
    highlight_alpha: int


def scene_lighting(style: SceneStyle) -> SceneLighting:
    brightness = max(0.0, min(1.0, style.ambient_brightness))
    coolness = max(0.0, min(1.0, style.atmosphere_coolness))
    return SceneLighting(
        shadow_offset=QPointF(7.0, 8.0),
        highlight_offset=QPointF(-3.0, -4.0),
        shadow_alpha=round(44 + coolness * 36 - brightness * 12),
        highlight_alpha=round(42 + brightness * 58 - coolness * 18),
    )
