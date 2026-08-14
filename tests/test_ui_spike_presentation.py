from digital_garden.domain import GardenAction, make_initial_state
from digital_garden.service import GardenService
from digital_garden.ui_spike.presentation import GardenSnapshotView, GardenSpikeController


def test_controller_reads_real_derived_state() -> None:
    controller = GardenSpikeController(GardenService(make_initial_state(seed=7)))
    assert controller.view() == GardenSnapshotView(anchor_state="CALM", condition="HEALTHY")


def test_water_routes_through_garden_service() -> None:
    service = GardenService(make_initial_state(seed=7))
    controller = GardenSpikeController(service)
    before = service.state.soil.moisture
    controller.water()
    assert service.state.soil.moisture > before
    assert controller.last_action is GardenAction.WATER
