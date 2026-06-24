"""Tests for src/evolution.py — GA components and orchestrator."""
import json
import numpy as np
import pytest

from evolution import (
    Universe,
    initialize_population,
    evaluate_population,
    select_elite,
    reproduce,
    mutate,
    run_evolution,
)
from fitness import gaussian_fitness, OUR_UNIVERSE


# ---------------------------------------------------------------------------
# Universe dataclass
# ---------------------------------------------------------------------------

class TestUniverse:
    def test_random_factory_uses_rng(self):
        rng = np.random.default_rng(0)
        u = Universe.random(rng, id=5)
        assert u.id == 5
        for v in u.constants.values():
            assert 0.0 <= v <= 1.0

    def test_random_factory_reproducible(self):
        u1 = Universe.random(np.random.default_rng(42))
        u2 = Universe.random(np.random.default_rng(42))
        assert u1.constants == u2.constants

    def test_our_universe_matches_fitness_module(self):
        assert Universe.our_universe() == OUR_UNIVERSE


# ---------------------------------------------------------------------------
# initialize_population
# ---------------------------------------------------------------------------

class TestInitializePopulation:
    def test_correct_size(self):
        rng = np.random.default_rng(0)
        pop = initialize_population(30, rng)
        assert len(pop) == 30

    def test_all_constants_in_range(self):
        rng = np.random.default_rng(1)
        pop = initialize_population(20, rng)
        for u in pop:
            for v in u.constants.values():
                assert 0.0 <= v <= 1.0

    def test_unique_ids(self):
        rng = np.random.default_rng(2)
        pop = initialize_population(10, rng)
        ids = [u.id for u in pop]
        assert len(set(ids)) == len(ids)

    def test_reproducible(self):
        pop1 = initialize_population(10, np.random.default_rng(99))
        pop2 = initialize_population(10, np.random.default_rng(99))
        for u1, u2 in zip(pop1, pop2):
            assert u1.constants == u2.constants


# ---------------------------------------------------------------------------
# evaluate_population
# ---------------------------------------------------------------------------

class TestEvaluatePopulation:
    def test_sets_fitness(self):
        rng = np.random.default_rng(3)
        pop = initialize_population(10, rng)
        evaluate_population(pop, gaussian_fitness)
        for u in pop:
            assert 0.0 <= u.fitness <= 1.0 + 1e-9

    def test_sets_generation(self):
        rng = np.random.default_rng(4)
        pop = initialize_population(5, rng)
        evaluate_population(pop, gaussian_fitness, generation=7)
        assert all(u.generation == 7 for u in pop)

    def test_accepts_custom_fitness(self):
        rng = np.random.default_rng(5)
        pop = initialize_population(5, rng)
        evaluate_population(pop, lambda c: 0.42)
        assert all(u.fitness == 0.42 for u in pop)


# ---------------------------------------------------------------------------
# select_elite
# ---------------------------------------------------------------------------

class TestSelectElite:
    def setup_method(self):
        rng = np.random.default_rng(6)
        self.pop = initialize_population(20, rng)
        evaluate_population(self.pop, gaussian_fitness)

    def test_returns_correct_fraction(self):
        elite = select_elite(self.pop, elite_frac=0.2)
        assert len(elite) == 4  # 20% of 20

    def test_minimum_two_elite(self):
        tiny_pop = self.pop[:4]
        elite = select_elite(tiny_pop, elite_frac=0.1)
        assert len(elite) == 2

    def test_sorted_descending(self):
        elite = select_elite(self.pop, elite_frac=0.3)
        for i in range(len(elite) - 1):
            assert elite[i].fitness >= elite[i + 1].fitness

    def test_population_sorted_after_call(self):
        select_elite(self.pop, 0.2)
        # Population should now be sorted
        for i in range(len(self.pop) - 1):
            assert self.pop[i].fitness >= self.pop[i + 1].fitness


# ---------------------------------------------------------------------------
# mutate
# ---------------------------------------------------------------------------

class TestMutate:
    def test_values_stay_in_range(self):
        rng = np.random.default_rng(7)
        constants = {k: v for k, v in OUR_UNIVERSE.items()}
        for _ in range(100):
            mutated = mutate(constants, mutation_rate=0.5, rng=rng)
            for v in mutated.values():
                assert 0.0 <= v <= 1.0

    def test_same_keys(self):
        rng = np.random.default_rng(8)
        mutated = mutate(OUR_UNIVERSE, rng=rng)
        assert set(mutated.keys()) == set(OUR_UNIVERSE.keys())

    def test_large_mutation_still_clips(self):
        rng = np.random.default_rng(9)
        constants = {k: 0.5 for k in OUR_UNIVERSE}
        for _ in range(200):
            mutated = mutate(constants, mutation_rate=10.0, rng=rng)
            for v in mutated.values():
                assert 0.0 <= v <= 1.0

    def test_reproducible_with_rng(self):
        c = dict(OUR_UNIVERSE)
        m1 = mutate(c, mutation_rate=0.1, rng=np.random.default_rng(42))
        m2 = mutate(c, mutation_rate=0.1, rng=np.random.default_rng(42))
        assert m1 == m2


# ---------------------------------------------------------------------------
# reproduce
# ---------------------------------------------------------------------------

class TestReproduce:
    def test_target_size_met(self):
        rng = np.random.default_rng(10)
        pop = initialize_population(10, rng)
        evaluate_population(pop, gaussian_fitness)
        elite = select_elite(pop, 0.2)
        new_pop = reproduce(elite, 10, 0.08, rng)
        assert len(new_pop) == 10

    def test_elite_preserved(self):
        rng = np.random.default_rng(11)
        pop = initialize_population(10, rng)
        evaluate_population(pop, gaussian_fitness)
        elite = select_elite(pop, 0.2)
        elite_constants = [dict(e.constants) for e in elite]
        new_pop = reproduce(elite, 10, 0.08, rng)
        # First len(elite) individuals should be the same elite
        for i, ec in enumerate(elite_constants):
            assert new_pop[i].constants == ec


# ---------------------------------------------------------------------------
# run_evolution (orchestrator)
# ---------------------------------------------------------------------------

class TestRunEvolution:
    def test_smoke_5_gens(self):
        history = run_evolution(population_size=10, generations=5, seed=42)
        assert len(history["generations"]) == 5
        assert len(history["best_fitness"]) == 5
        assert len(history["mean_fitness"]) == 5
        assert len(history["best_constants"]) == 5
        assert len(history["diversity"]) == 5

    def test_best_fitness_monotone(self):
        """Elitist selection must ensure best fitness never decreases."""
        history = run_evolution(population_size=20, generations=10, seed=0)
        for i in range(1, len(history["best_fitness"])):
            assert history["best_fitness"][i] >= history["best_fitness"][i - 1] - 1e-10, \
                f"Fitness decreased at gen {i}: {history['best_fitness'][i - 1]} → {history['best_fitness'][i]}"

    def test_fitness_in_range(self):
        history = run_evolution(population_size=10, generations=5, seed=1)
        for f in history["best_fitness"]:
            assert 0.0 <= f <= 1.0 + 1e-9

    def test_reproducibility(self):
        """Same seed must produce byte-identical histories."""
        h1 = run_evolution(population_size=15, generations=8, seed=77)
        h2 = run_evolution(population_size=15, generations=8, seed=77)
        assert h1["best_fitness"]    == h2["best_fitness"]
        assert h1["best_constants"]  == h2["best_constants"]
        assert h1["diversity"]       == h2["diversity"]

    def test_different_seeds_differ(self):
        h1 = run_evolution(population_size=15, generations=5, seed=1)
        h2 = run_evolution(population_size=15, generations=5, seed=2)
        # Very unlikely to be identical
        assert h1["best_fitness"] != h2["best_fitness"]

    def test_json_serializable(self):
        history = run_evolution(population_size=10, generations=3, seed=42)
        json.dumps(history)  # must not raise

    def test_best_constants_keys_match_our_universe(self):
        history = run_evolution(population_size=10, generations=3, seed=0)
        for bc in history["best_constants"]:
            assert set(bc.keys()) == set(OUR_UNIVERSE.keys())

    def test_custom_fitness_fn(self):
        """run_evolution should accept any callable fitness function."""
        from fitness import complexity_fitness
        history = run_evolution(
            population_size=10, generations=3, seed=0,
            fitness_fn=complexity_fitness,
        )
        assert len(history["best_fitness"]) == 3
