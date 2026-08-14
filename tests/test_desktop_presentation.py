from dataclasses import replace

import pytest

from digital_garden.desktop.controller import DesktopController
from digital_garden.desktop.presentation import (
    GardenRenderState,
    render_state_from_snapshot,
)
from digital_garden.domain import (
    BonsaiState,
    GroundState,
    SoilState,
    VineState,
    Weather,
    make_initial_state,
)
from digital_garden.observation import inspection_snapshot
from digital_garden.service import GardenService


def test_snapshot_maps_to_complete_immutable_render_state() -> None:
    state = replace(
        make_initial_state(seed=7),
        tick=12,
        weather=Weather.RAINY,
        light_level=0.25,
        humidity=0.90,
        soil=SoilState(0.67),
        bonsai=BonsaiState(0.81, 0.22, 0.31, 0.64),
        ground=GroundState(0.48),
        vine=VineState(0.39),
    )
    render_state = render_state_from_snapshot(inspection_snapshot(state))

    assert render_state == GardenRenderState(
        seed=7,
        tick=12,
        weather="RAINY",
        light_level=0.25,
        humidity=0.90,
        soil_moisture=0.67,
        bonsai_health=0.81,
        bonsai_stress=0.22,
        bonsai_growth=0.31,
        canopy_density=0.64,
        ground_density=0.48,
        vine_extent=0.39,
        condition="HEALTHY",
        anchor_state="CALM",
    )


def test_controller_delegates_only_to_service_snapshot() -> None:
    service = GardenService(make_initial_state(seed=7))
    controller = DesktopController(service)

    assert controller.render_state() == render_state_from_snapshot(service.snapshot())
    assert service.state == make_initial_state(seed=7)


def test_presentation_rejects_malformed_snapshot() -> None:
    with pytest.raises(TypeError, match="snapshot state"):
        render_state_from_snapshot({"state": "bad", "derived": {}})
