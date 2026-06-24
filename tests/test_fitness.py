"""Tests for src/fitness.py — FitnessFunction protocol and concrete implementations."""
import json
import numpy as np
import pytest

from fitness import (
    FitnessFunction,
    OUR_UNIVERSE,
    gaussian_fitness,
    complexity_fitness,
)


# ---------------------------------------------------------------------------
# OUR_UNIVERSE
# ---------------------------------------------------------------------------

class TestOurUniverse:
    def test_has_six_constants(self):
        assert len(OUR_UNIVERSE) == 6

    def test_values_in_range(self):
        for v in OUR_UNIVERSE.values():
            assert 0.0 <= v <= 1.0


# ---------------------------------------------------------------------------
# FitnessFunction protocol
# ---------------------------------------------------------------------------

class TestFitnessFunctionProtocol:
    def test_gaussian_satisfies_protocol(self):
        assert isinstance(gaussian_fitness, FitnessFunction)

    def test_complexity_satisfies_protocol(self):
        assert isinstance(complexity_fitness, FitnessFunction)

    def test_lambda_satisfies_protocol(self):
        trivial = lambda c: 0.5  # noqa: E731
        assert isinstance(trivial, FitnessFunction)


# ---------------------------------------------------------------------------
# gaussian_fitness
# ---------------------------------------------------------------------------

class TestGaussianFitness:
    def test_our_universe_scores_one(self):
        """Our universe's normalized constants should yield fitness ≈ 1.0."""
        score = gaussian_fitness(OUR_UNIVERSE)
        assert abs(score - 1.0) < 1e-6

    def test_all_zeros_scores_low(self):
        zeros = {k: 0.0 for k in OUR_UNIVERSE}
        assert gaussian_fitness(zeros) < 0.1

    def test_all_ones_scores_low(self):
        ones = {k: 1.0 for k in OUR_UNIVERSE}
        assert gaussian_fitness(ones) < 0.1

    def test_returns_float(self):
        assert isinstance(gaussian_fitness(OUR_UNIVERSE), float)

    def test_range_over_random_constants(self):
        """Fitness must stay in [0, 1] for any constants in [0, 1]."""
        rng = np.random.default_rng(0)
        for _ in range(200):
            c = {k: float(rng.uniform(0, 1)) for k in OUR_UNIVERSE}
            f = gaussian_fitness(c)
            assert 0.0 <= f <= 1.0 + 1e-9  # small tolerance for floating-point

    def test_symmetric_around_target(self):
        """Same offset in opposite directions should yield same score."""
        offset = 0.05
        c_plus  = dict(OUR_UNIVERSE); c_plus["gravity"]  += offset
        c_minus = dict(OUR_UNIVERSE); c_minus["gravity"] -= offset
        assert abs(gaussian_fitness(c_plus) - gaussian_fitness(c_minus)) < 1e-9

    def test_json_serializable(self):
        """Return value should be directly JSON-serializable."""
        score = gaussian_fitness(OUR_UNIVERSE)
        json.dumps(score)  # must not raise


# ---------------------------------------------------------------------------
# complexity_fitness (legacy)
# ---------------------------------------------------------------------------

class TestComplexityFitnessLegacy:
    def test_our_universe_scores_positive(self):
        assert complexity_fitness(OUR_UNIVERSE) > 0.0

    def test_all_zeros_scores_zero(self):
        """Pathological case: linear product can go to zero."""
        zeros = {k: 0.0 for k in OUR_UNIVERSE}
        assert complexity_fitness(zeros) == 0.0

    def test_range_non_negative(self):
        rng = np.random.default_rng(1)
        for _ in range(100):
            c = {k: float(rng.uniform(0, 1)) for k in OUR_UNIVERSE}
            assert complexity_fitness(c) >= 0.0
