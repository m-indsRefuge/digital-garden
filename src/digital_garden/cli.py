import argparse
import json

from digital_garden.domain import make_initial_state
from digital_garden.service import GardenService


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="digital-garden")
    subparsers = parser.add_subparsers(dest="command", required=True)
    simulate = subparsers.add_parser("simulate")
    simulate.add_argument("--seed", type=int, required=True)
    simulate.add_argument("--ticks", type=int, required=True)
    args = parser.parse_args(argv)

    if args.command == "simulate":
        if args.ticks < 0:
            parser.error("--ticks must not be negative")

        service = GardenService(make_initial_state(args.seed))
        service.advance(args.ticks)
        snapshot = service.snapshot()
        derived = snapshot["derived"]
        summary = {
            "seed": service.state.seed,
            "tick": service.state.tick,
            "day_index": service.state.day_index,
            "hour_of_day": service.state.hour_of_day,
            "weather": service.state.weather.value,
            "soil_moisture": service.state.soil.moisture,
            "bonsai_health": service.state.bonsai.health,
            "bonsai_stress": service.state.bonsai.stress,
            "overgrowth": derived["overgrowth"],
            "condition": derived["condition"],
            "anchor_state": derived["anchor_state"],
            "observation_length": len(service.observation()),
        }
        print(json.dumps(summary, sort_keys=True))


if __name__ == "__main__":
    main()
