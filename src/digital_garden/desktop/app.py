import sys
from dataclasses import dataclass

from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QApplication

from digital_garden.desktop.controller import DesktopController
from digital_garden.desktop.persistence import (
    DesktopPreferences,
    DesktopPreferencesStore,
    default_preferences_path,
)
from digital_garden.desktop.placement import (
    ScreenGeometry,
    choose_screen,
    restore_anchor_origin,
)
from digital_garden.desktop.scene.renderer import (
    ANCHOR_SIZE,
    QPainterShellRenderer,
)
from digital_garden.desktop.windows import (
    GardenPatchWindow,
    VineAnchorWindow,
)
from digital_garden.domain import make_initial_state
from digital_garden.service import GardenService


@dataclass
class DesktopShell:
    anchor: VineAnchorWindow
    patch: GardenPatchWindow


def _screen_geometries() -> tuple[ScreenGeometry, ...]:
    screens = QGuiApplication.screens()

    if not screens:
        raise RuntimeError("no desktop screens are available")

    primary = QGuiApplication.primaryScreen()

    ordered = ([primary] if primary is not None else []) + [
        screen for screen in screens if screen is not primary
    ]

    return tuple(
        ScreenGeometry(
            screen.name(),
            screen.availableGeometry(),
        )
        for screen in ordered
    )


def build_desktop_shell(
    service: GardenService,
    preferences_store: DesktopPreferencesStore,
) -> DesktopShell:
    controller = DesktopController(service)
    renderer = QPainterShellRenderer()

    anchor = VineAnchorWindow(
        controller,
        renderer,
    )
    patch = GardenPatchWindow(
        controller,
        renderer,
    )

    anchor.attach_patch(patch)

    preferences = preferences_store.load()
    screen = choose_screen(
        _screen_geometries(),
        preferences.screen_name,
    )

    anchor.move(
        restore_anchor_origin(
            preferences,
            screen,
            ANCHOR_SIZE,
        )
    )

    def save_anchor_position(
        screen_name: str,
        x: int,
        y: int,
    ) -> None:
        preferences_store.save(
            DesktopPreferences(
                screen_name,
                x,
                y,
            )
        )

    anchor.position_committed.connect(save_anchor_position)

    return DesktopShell(
        anchor=anchor,
        patch=patch,
    )


def main() -> None:
    app = QApplication.instance() or QApplication(sys.argv)

    # V0-B.1 deliberately keeps Garden lifecycle simple.
    # V0-B.4 integrates authoritative persisted Garden resume
    # without introducing a second clock.
    service = GardenService(make_initial_state(seed=7))
    store = DesktopPreferencesStore(default_preferences_path())

    shell = build_desktop_shell(
        service,
        store,
    )

    shell.anchor.show()

    raise SystemExit(app.exec())
