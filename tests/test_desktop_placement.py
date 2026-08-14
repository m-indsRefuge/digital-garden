from PySide6.QtCore import QPoint, QRect, QSize

from digital_garden.desktop.persistence import DesktopPreferences
from digital_garden.desktop.placement import (
    ScreenGeometry,
    adjacent_patch_origin,
    choose_screen,
    restore_anchor_origin,
)


def test_choose_screen_prefers_saved_name_and_falls_back_to_primary() -> None:
    screens = (
        ScreenGeometry("PRIMARY", QRect(0, 0, 1920, 1080)),
        ScreenGeometry("SECONDARY", QRect(1920, 0, 1920, 1080)),
    )

    assert choose_screen(screens, "SECONDARY").name == "SECONDARY"
    assert choose_screen(screens, "MISSING").name == "PRIMARY"


def test_restore_anchor_clamps_saved_position_to_available_geometry() -> None:
    screen = ScreenGeometry("PRIMARY", QRect(0, 0, 1920, 1080))
    preferences = DesktopPreferences(
        screen_name="PRIMARY",
        anchor_x=5000,
        anchor_y=5000,
    )

    assert restore_anchor_origin(
        preferences,
        screen,
        QSize(96, 180),
    ) == QPoint(1824, 900)


def test_patch_prefers_left_and_flips_right_when_required() -> None:
    available = QRect(0, 0, 1920, 1080)
    patch_size = QSize(520, 420)

    assert adjacent_patch_origin(
        QRect(1800, 700, 96, 180),
        patch_size,
        available,
    ) == QPoint(1272, 580)

    assert adjacent_patch_origin(
        QRect(10, 500, 96, 180),
        patch_size,
        available,
    ) == QPoint(114, 380)
