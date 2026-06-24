"""Tests for src/complexity.py — CA rules, simulation, and emergence metrics."""
import numpy as np
import pytest

from complexity import constants_to_ca_rule, run_ca, measure_complexity, ca_fitness
from fitness import OUR_UNIVERSE


# ---------------------------------------------------------------------------
# constants_to_ca_rule
# ---------------------------------------------------------------------------

class TestConstantsToCaRule:
    def test_returns_required_keys(self):
        rule = constants_to_ca_rule(OUR_UNIVERSE)
        assert set(rule.keys()) == {"birth", "survive", "decay", "grid_size"}

    def test_birth_survive_are_sets(self):
        rule = constants_to_ca_rule(OUR_UNIVERSE)
        assert isinstance(rule["birth"],   set)
        assert isinstance(rule["survive"], set)

    def test_decay_range(self):
        rng = np.random.default_rng(0)
        for _ in range(50):
            c = {k: float(rng.uniform(0, 1)) for k in OUR_UNIVERSE}
            rule = constants_to_ca_rule(c)
            assert 0.0 <= rule["decay"] <= 0.3

    def test_birth_survive_neighbor_counts(self):
        """Birth and survive values must be valid Moore-neighborhood counts (1–8)."""
        rule = constants_to_ca_rule(OUR_UNIVERSE)
        for v in rule["birth"]:
            assert 1 <= v <= 8
        for v in rule["survive"]:
            assert 1 <= v <= 8

    def test_reproducible(self):
        r1 = constants_to_ca_rule(OUR_UNIVERSE)
        r2 = constants_to_ca_rule(OUR_UNIVERSE)
        assert r1 == r2


# ---------------------------------------------------------------------------
# run_ca
# ---------------------------------------------------------------------------

class TestRunCa:
    def setup_method(self):
        self.rule = constants_to_ca_rule(OUR_UNIVERSE)
        self.rng  = np.random.default_rng(42)

    def test_output_shape(self):
        steps = 10
        history = run_ca(self.rule, steps=steps, rng=self.rng)
        assert history.shape == (steps + 1, self.rule["grid_size"], self.rule["grid_size"])

    def test_binary_values(self):
        history = run_ca(self.rule, steps=5, rng=self.rng)
        assert set(np.unique(history)).issubset({0, 1})

    def test_reproducible_with_rng(self):
        h1 = run_ca(self.rule, steps=5, rng=np.random.default_rng(7))
        h2 = run_ca(self.rule, steps=5, rng=np.random.default_rng(7))
        np.testing.assert_array_equal(h1, h2)

    def test_different_seeds_differ(self):
        h1 = run_ca(self.rule, steps=5, rng=np.random.default_rng(1))
        h2 = run_ca(self.rule, steps=5, rng=np.random.default_rng(2))
        assert not np.array_equal(h1, h2)


# ---------------------------------------------------------------------------
# measure_complexity
# ---------------------------------------------------------------------------

class TestMeasureComplexity:
    def _make_history(self, steps=20):
        rule = constants_to_ca_rule(OUR_UNIVERSE)
        return run_ca(rule, steps=steps, rng=np.random.default_rng(42))

    def test_returns_required_keys(self):
        history = self._make_history()
        metrics = measure_complexity(history)
        assert set(metrics.keys()) == {
            "entropy", "compression_ratio", "mean_activity",
            "lifespan", "complexity_score",
        }

    def test_entropy_range(self):
        metrics = measure_complexity(self._make_history())
        assert 0.0 <= metrics["entropy"] <= 1.0 + 1e-9

    def test_compression_ratio_range(self):
        metrics = measure_complexity(self._make_history())
        # Ratio is len(compressed)/len(raw); raw can compress to near-zero
        assert 0.0 <= metrics["compression_ratio"] <= 1.0 + 1e-9

    def test_complexity_score_non_negative(self):
        metrics = measure_complexity(self._make_history())
        assert metrics["complexity_score"] >= 0.0

    def test_all_dead_universe_has_zero_entropy(self):
        """An all-zero grid should have zero entropy."""
        dead_history = np.zeros((10, 16, 16), dtype=np.uint8)
        metrics = measure_complexity(dead_history)
        assert metrics["entropy"] == 0.0
        assert metrics["complexity_score"] == 0.0


# ---------------------------------------------------------------------------
# ca_fitness
# ---------------------------------------------------------------------------

class TestCaFitness:
    def test_returns_non_negative_float(self):
        rng = np.random.default_rng(0)
        score = ca_fitness(OUR_UNIVERSE, rng=rng, steps=10)
        assert isinstance(score, float)
        assert score >= 0.0

    def test_reproducible_with_rng(self):
        s1 = ca_fitness(OUR_UNIVERSE, rng=np.random.default_rng(5), steps=10)
        s2 = ca_fitness(OUR_UNIVERSE, rng=np.random.default_rng(5), steps=10)
        assert s1 == s2

    def test_steps_parameter_respected(self):
        """Fewer steps should run faster; result may differ but must be valid."""
        rng = np.random.default_rng(1)
        score = ca_fitness(OUR_UNIVERSE, rng=rng, steps=5)
        assert score >= 0.0
