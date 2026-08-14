from collections.abc import Sequence
from dataclasses import dataclass

from PySide6.QtCore import QPoint, QRect, QSize

from digital_garden.desktop.persistence import DesktopPreferences

ANCHOR_MARGIN = 24
PATCH_GAP = 8


@dataclass(frozen=True)
class ScreenGeometry:
    name: str
    available: QRect


def choose_screen(
    screens: Sequence[ScreenGeometry],
    saved_name: str | None,
) -> ScreenGeometry:
    if not screens:
        raise ValueError("at least one screen is required")

    if saved_name is not None:
        for screen in screens:
            if screen.name == saved_name:
                return screen

    return screens[0]


def restore_anchor_origin(
    preferences: DesktopPreferences,
    screen: ScreenGeometry,
    anchor_size: QSize,
) -> QPoint:
    available = screen.available

    default_x = available.x() + available.width() - anchor_size.width() - ANCHOR_MARGIN
    default_y = available.y() + available.height() - anchor_size.height() - ANCHOR_MARGIN

    requested_x = preferences.anchor_x if preferences.anchor_x is not None else default_x
    requested_y = preferences.anchor_y if preferences.anchor_y is not None else default_y

    min_x = available.x()
    min_y = available.y()
    max_x = available.x() + available.width() - anchor_size.width()
    max_y = available.y() + available.height() - anchor_size.height()

    return QPoint(
        max(min_x, min(requested_x, max_x)),
        max(min_y, min(requested_y, max_y)),
    )


def adjacent_patch_origin(
    anchor_rect: QRect,
    patch_size: QSize,
    available: QRect,
) -> QPoint:
    preferred_left_x = anchor_rect.x() - PATCH_GAP - patch_size.width()
    right_x = anchor_rect.x() + anchor_rect.width() + PATCH_GAP

    min_x = available.x()
    max_x = available.x() + available.width() - patch_size.width()

    if preferred_left_x >= min_x:
        patch_x = preferred_left_x
    elif right_x <= max_x:
        patch_x = right_x
    else:
        patch_x = max(min_x, min(preferred_left_x, max_x))

    centered_y = anchor_rect.y() + anchor_rect.height() // 2 - patch_size.height() // 2

    min_y = available.y()
    max_y = available.y() + available.height() - patch_size.height()
    patch_y = max(min_y, min(centered_y, max_y))

    return QPoint(patch_x, patch_y)
