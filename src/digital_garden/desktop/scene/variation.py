import hashlib
from dataclasses import dataclass


@dataclass(frozen=True)
class VisualCandidate:
    index: int
    x: float
    y: float
    scale: float


def stable_unit(seed: int, object_id: str, index: int = 0) -> float:
    payload = f"{seed}:{object_id}:{index}".encode()
    digest = hashlib.blake2b(payload, digest_size=8).digest()
    return int.from_bytes(digest, byteorder="big") / ((1 << 64) - 1)


def candidate_pool(
    seed: int,
    object_id: str,
    count: int,
) -> tuple[VisualCandidate, ...]:
    return tuple(
        VisualCandidate(
            index=index,
            x=stable_unit(seed, f"{object_id}:x", index),
            y=stable_unit(seed, f"{object_id}:y", index),
            scale=0.55 + stable_unit(seed, f"{object_id}:scale", index) * 0.70,
        )
        for index in range(count)
    )


def visible_candidates(
    candidates: tuple[VisualCandidate, ...],
    density: float,
) -> tuple[VisualCandidate, ...]:
    clamped_density = max(0.0, min(1.0, density))
    visible_count = int(len(candidates) * clamped_density)
    return candidates[:visible_count]
