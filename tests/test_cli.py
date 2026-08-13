import json
import subprocess
import sys


def test_simulate_command_produces_machine_readable_summary() -> None:
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "digital_garden.cli",
            "simulate",
            "--seed",
            "7",
            "--ticks",
            "48",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(completed.stdout)
    assert payload["seed"] == 7
    assert payload["tick"] == 48
    assert payload["day_index"] == 2
    assert payload["observation_length"] == 12
    assert payload["condition"] in {"THRIVING", "HEALTHY", "WILD", "STRESSED", "STRUGGLING"}
