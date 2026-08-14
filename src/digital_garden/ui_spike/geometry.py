from PySide6.QtCore import QPoint, QRect, QSize

PATCH_GAP = 8


def adjacent_patch_origin(
    anchor_geometry: QRect,
    patch_size: QSize,
    available_geometry: QRect,
) -> QPoint:
    y = anchor_geometry.center().y() - patch_size.height() // 2
    y = min(
        max(y, available_geometry.top()),
        available_geometry.bottom() - patch_size.height() + 1,
    )
    left_x = anchor_geometry.left() - PATCH_GAP - patch_size.width()
    if left_x >= available_geometry.left():
        return QPoint(left_x, y)
    right_x = anchor_geometry.right() + 1 + PATCH_GAP
    maximum_x = available_geometry.right() - patch_size.width() + 1
    return QPoint(min(right_x, maximum_x), y)
