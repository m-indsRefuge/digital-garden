import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication

from digital_garden.desktop.app import build_desktop_shell
from digital_garden.desktop.persistence import (
    DesktopPreferences,
    DesktopPreferencesStore,
)
from digital_garden.domain import make_initial_state
from digital_garden.service import GardenService


def test_shell_starts_collapsed_and_does_not_mutate_garden(tmp_path) -> None:
    app = QApplication.instance() or QApplication([])
    service = GardenService(make_initial_state(seed=7))
    store = DesktopPreferencesStore(tmp_path / "desktop.json")

    shell = build_desktop_shell(service, store)

    assert shell.anchor.isVisible() is False
    assert shell.patch.isVisible() is False
    assert service.state == make_initial_state(seed=7)

    shell.anchor.close()
    shell.patch.close()
    app.processEvents()


def test_committed_anchor_position_is_saved_as_desktop_only_preference(
    tmp_path,
) -> None:
    app = QApplication.instance() or QApplication([])
    service = GardenService(make_initial_state(seed=7))
    store = DesktopPreferencesStore(tmp_path / "desktop.json")

    shell = build_desktop_shell(service, store)

    shell.anchor.position_committed.emit(
        "SCREEN-X",
        120,
        240,
    )

    assert store.load() == DesktopPreferences(
        "SCREEN-X",
        120,
        240,
    )
    assert service.state == make_initial_state(seed=7)

    shell.anchor.close()
    shell.patch.close()
    app.processEvents()
