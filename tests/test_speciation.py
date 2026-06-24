"""Tests for src/speciation.py — multimodal fitness and niched GA."""
import numpy as np
import pytest

from speciation import multimodal_fitness, fitness_sharing, run_speciation

# Canonical key names used by speciation.py
_KEYS = [
    "Gravity (G)", "EM Coupling (α)", "Strong Force",
    "Weak Force", "Dark Energy (Λ)", "Mass Ratio (mₚ/mₑ)",
]

# Our universe in speciation's key convention
_OUR_UNIVERSE_SPEC = dict(zip(_KEYS, [0.15, 0.45, 0.65, 0.30, 0.02, 0.55]))


# ---------------------------------------------------------------------------
# multimodal_fitness
# ---------------------------------------------------------------------------

class TestMultimodalFitness:
    def test_our_universe_near_one(self):
        """Peak 1 is centred on our universe — should score > 0.9."""
        assert multimodal_fitness(_OUR_UNIVERSE_SPEC) > 0.9

    def test_range_for_random_constants(self):
        rng = np.random.default_rng(0)
        for _ in range(100):
            c = {k: float(rng.uniform(0, 1)) for k in _KEYS}
            f = multimodal_fitness(c)
            assert 0.0 <= f <= 1.0 + 1e-9

    def test_returns_float(self):
        assert isinstance(multimodal_fitness(_OUR_UNIVERSE_SPEC), float)

    def test_zero_constants_score_low(self):
        zeros = {k: 0.0 for k in _KEYS}
        assert multimodal_fitness(zeros) < 0.1


# ---------------------------------------------------------------------------
# fitness_sharing
# ---------------------------------------------------------------------------

class TestFitnessSharing:
    def test_identical_individuals_get_reduced_fitness(self):
        """10 identical individuals should each share the niche, reducing shared fitness."""
        pop = [{k: 0.5 for k in _KEYS} for _ in range(10)]
        fitnesses = [1.0] * 10
        shared = fitness_sharing(pop, fitnesses, sigma_share=0.5)
        assert all(s < 0.5 for s in shared)

    def test_isolated_individual_keeps_full_fitness(self):
        """An individual far from all others keeps its raw fitness."""
        pop = [
            {k: 0.0 for k in _KEYS},   # isolated
            {k: 1.0 for k in _KEYS},   # far away
        ]
        fitnesses = [1.0, 1.0]
        shared = fitness_sharing(pop, fitnesses, sigma_share=0.1)
        # Each individual is far from the other (distance >> sigma_share)
        for s in shared:
            assert s > 0.5

    def test_shared_fitness_non_negative(self):
        rng = np.random.default_rng(0)
        pop = [{k: float(rng.uniform(0, 1)) for k in _KEYS} for _ in range(20)]
        fitnesses = [float(rng.uniform(0, 1)) for _ in range(20)]
        shared = fitness_sharing(pop, fitnesses)
        assert all(s >= 0.0 for s in shared)

    def test_returns_same_length(self):
        pop = [{k: 0.5 for k in _KEYS} for _ in range(7)]
        shared = fitness_sharing(pop, [0.8] * 7)
        assert len(shared) == 7


# ---------------------------------------------------------------------------
# run_speciation (smoke test)
# ---------------------------------------------------------------------------

class TestRunSpeciation:
    def test_smoke_5_gens(self):
        history, positions = run_speciation(pop_size=20, generations=5, seed=42)
        assert len(history["gen"]) == 5
        assert len(history["n_species"]) == 5
        assert len(history["best_fit"]) == 5

    def test_positions_shape(self):
        _, positions = run_speciation(pop_size=20, generations=5, seed=0)
        assert positions.shape == (5, 20, len(_KEYS))

    def test_reproducible(self):
        h1, p1 = run_speciation(pop_size=20, generations=5, seed=7)
        h2, p2 = run_speciation(pop_size=20, generations=5, seed=7)
        assert h1["best_fit"] == h2["best_fit"]
        np.testing.assert_array_equal(p1, p2)

    def test_best_fitness_non_negative(self):
        history, _ = run_speciation(pop_size=15, generations=5, seed=1)
        assert all(f >= 0.0 for f in history["best_fit"])
