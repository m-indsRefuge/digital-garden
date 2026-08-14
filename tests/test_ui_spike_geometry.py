from PySide6.QtCore import QPoint, QRect, QSize

from digital_garden.ui_spike.geometry import adjacent_patch_origin


def test_patch_prefers_left_when_space_exists() -> None:
    assert adjacent_patch_origin(
        QRect(1800, 700, 96, 180), QSize(520, 420), QRect(0, 0, 1920, 1080)
    ) == QPoint(1272, 579)


def test_patch_flips_right_near_left_edge() -> None:
    assert adjacent_patch_origin(
        QRect(10, 500, 96, 180), QSize(520, 420), QRect(0, 0, 1920, 1080)
    ) == QPoint(114, 379)
