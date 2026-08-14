from digital_garden.desktop.scene.variation import (
    candidate_pool,
    stable_unit,
    visible_candidates,
)


def test_stable_unit_repeats_for_the_same_visual_identity() -> None:
    first = stable_unit(7, "clover", 3)
    second = stable_unit(7, "clover", 3)

    assert first == second
    assert 0.0 <= first <= 1.0


def test_candidate_pool_is_reproducible_and_seed_sensitive() -> None:
    first = candidate_pool(7, "clover", 6)
    repeated = candidate_pool(7, "clover", 6)
    different_seed = candidate_pool(8, "clover", 6)

    assert first == repeated
    assert first != different_seed


def test_increasing_density_reveals_a_prefix_of_stable_candidate_sites() -> None:
    candidates = candidate_pool(7, "clover", 12)

    sparse = visible_candidates(candidates, 0.25)
    lush = visible_candidates(candidates, 0.75)

    assert 0 < len(sparse) < len(lush) <= len(candidates)
    assert lush[: len(sparse)] == sparse
