"""evolution.py — Cosmological Genetic Algorithm

Simulates universe evolution through intelligence-driven cycles.
Each universe has physical constants; those producing intelligence
get to reproduce (spawn new universes with mutated constants).

The Ouroboros question: does this converge toward our universe's constants?
"""

import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass, field
from typing import List
import json, os


@dataclass
class Universe:
    """A universe defined by its fundamental constants."""
    constants: dict = field(default_factory=dict)
    fitness: float = 0.0
    generation: int = 0
    parent_id: int = -1
    id: int = 0

    def __post_init__(self):
        if not self.constants:
            self.constants = self.random_constants()

    @staticmethod
    def random_constants() -> dict:
        """Generate random physical constants (normalized 0-1 scale)."""
        return {
            "gravity": np.random.uniform(0, 1),          # G strength
            "em_coupling": np.random.uniform(0, 1),      # electromagnetic coupling
            "strong_force": np.random.uniform(0, 1),     # strong nuclear force
            "weak_force": np.random.uniform(0, 1),       # weak nuclear force
            "cosmological_const": np.random.uniform(0, 1),  # dark energy
            "mass_ratio": np.random.uniform(0, 1),       # proton/electron mass ratio
        }

    @staticmethod
    def our_universe() -> dict:
        """Our universe's constants (normalized to 0-1 range)."""
        return {
            "gravity": 0.15,
            "em_coupling": 0.45,
            "strong_force": 0.65,
            "weak_force": 0.30,
            "cosmological_const": 0.02,
            "mass_ratio": 0.55,
        }


def complexity_fitness(constants: dict) -> float:
    """Estimate whether a universe develops complexity/intelligence.

    Based on anthropic constraints:
    - Gravity too strong → universe collapses before stars form
    - Gravity too weak → no structure forms
    - Strong force too high → only hydrogen, no chemistry
    - Cosmological constant too high → expansion rips matter apart
    - Need balance for: stars, chemistry, planets, time for evolution
    """
    g = constants["gravity"]
    em = constants["em_coupling"]
    sf = constants["strong_force"]
    wf = constants["weak_force"]
    cc = constants["cosmological_const"]
    mr = constants["mass_ratio"]

    # Stars form: need moderate gravity
    star_score = 1.0 - abs(g - 0.15) * 4  # peaks at our G

    # Chemistry works: need right EM + strong force balance
    chem_score = 1.0 - abs(em - 0.45) * 3 - abs(sf - 0.65) * 3

    # Universe doesn't rip apart or collapse
    stability_score = 1.0 - cc * 5  # low cosmological constant is good

    # Enough time for evolution (weak force affects stellar lifetime)
    time_score = 1.0 - abs(wf - 0.30) * 3

    # Complex atoms form
    atom_score = 1.0 - abs(mr - 0.55) * 3

    # Combined fitness (all must be positive for intelligence)
    raw = star_score * max(0, chem_score) * max(0, stability_score) * max(0, time_score) * max(0, atom_score)
    return max(0.0, raw)


def mutate(constants: dict, mutation_rate: float = 0.1) -> dict:
    """Mutate constants — the 'information carried through the singularity'."""
    new = {}
    for key, val in constants.items():
        if np.random.random() < 0.3:  # 30% chance to mutate each constant
            new[key] = np.clip(val + np.random.normal(0, mutation_rate), 0, 1)
        else:
            new[key] = val
    return new


def run_evolution(population_size: int = 50, generations: int = 100,
                  mutation_rate: float = 0.08, elite_frac: float = 0.2) -> dict:
    """Run the cosmological genetic algorithm.

    Returns history of all generations for analysis.
    """
    # Initialize random population of universes
    population = [Universe(id=i) for i in range(population_size)]
    history = {"generations": [], "best_fitness": [], "mean_fitness": [],
               "best_constants": [], "diversity": []}
    uid_counter = population_size

    our = Universe.our_universe()
    print(f"Target (our universe): {our}")
    print(f"Running {generations} generations with {population_size} universes...\n")

    for gen in range(generations):
        # Evaluate fitness
        for u in population:
            u.fitness = complexity_fitness(u.constants)
            u.generation = gen

        # Sort by fitness
        population.sort(key=lambda u: u.fitness, reverse=True)

        # Record stats
        fitnesses = [u.fitness for u in population]
        best = population[0]
        diversity = np.std([[v for v in u.constants.values()] for u in population])

        history["generations"].append(gen)
        history["best_fitness"].append(best.fitness)
        history["mean_fitness"].append(np.mean(fitnesses))
        history["best_constants"].append(dict(best.constants))
        history["diversity"].append(diversity)

        if gen % 20 == 0 or gen == generations - 1:
            dist = np.sqrt(sum((best.constants[k] - our[k])**2 for k in our))
            print(f"Gen {gen:3d} | Best: {best.fitness:.4f} | Mean: {np.mean(fitnesses):.4f} | "
                  f"Dist to us: {dist:.3f} | Diversity: {diversity:.3f}")

        # Selection: keep top elite_frac
        n_elite = max(2, int(population_size * elite_frac))
        elite = population[:n_elite]

        # Reproduction: elite spawn children with mutations
        new_population = list(elite)  # elites survive
        while len(new_population) < population_size:
            parent = elite[np.random.randint(0, n_elite)]
            child_constants = mutate(parent.constants, mutation_rate)
            child = Universe(constants=child_constants, parent_id=parent.id, id=uid_counter)
            uid_counter += 1
            new_population.append(child)

        population = new_population

    return history


def visualize_evolution(history: dict):
    """Plot the evolutionary trajectory."""
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))

    # Fitness over generations
    ax = axes[0, 0]
    ax.plot(history["generations"], history["best_fitness"], 'b-', label="Best")
    ax.plot(history["generations"], history["mean_fitness"], 'r--', alpha=0.7, label="Mean")
    ax.set_xlabel("Generation (Cosmic Cycle)")
    ax.set_ylabel("Fitness (Intelligence Emergence)")
    ax.set_title("Ouroboros Evolution — Fitness Convergence")
    ax.legend()
    ax.grid(True, alpha=0.3)

    # Distance to our universe
    our = Universe.our_universe()
    distances = [np.sqrt(sum((h[k] - our[k])**2 for k in our))
                 for h in history["best_constants"]]
    ax = axes[0, 1]
    ax.plot(history["generations"], distances, 'g-')
    ax.set_xlabel("Generation")
    ax.set_ylabel("Distance to Our Universe")
    ax.set_title("Convergence Toward Our Constants")
    ax.grid(True, alpha=0.3)

    # Final best constants vs ours
    ax = axes[1, 0]
    final = history["best_constants"][-1]
    keys = list(our.keys())
    x = np.arange(len(keys))
    ax.bar(x - 0.2, [our[k] for k in keys], 0.35, label="Our Universe", color="gold")
    ax.bar(x + 0.2, [final[k] for k in keys], 0.35, label="Evolved Best", color="blue")
    ax.set_xticks(x)
    ax.set_xticklabels(keys, rotation=45, ha="right")
    ax.set_ylabel("Normalized Value")
    ax.set_title("Physical Constants: Ours vs Evolved")
    ax.legend()

    # Diversity
    ax = axes[1, 1]
    ax.plot(history["generations"], history["diversity"], 'm-')
    ax.set_xlabel("Generation")
    ax.set_ylabel("Population Diversity")
    ax.set_title("Genetic Diversity Over Time")
    ax.grid(True, alpha=0.3)

    plt.suptitle("The Ouroboros Singularity — Cosmological Genetic Algorithm", fontsize=14)
    plt.tight_layout()
    plt.savefig("outputs/ouroboros_evolution.png", dpi=150)
    plt.show()
    print("Saved: outputs/ouroboros_evolution.png")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Ouroboros Cosmological GA")
    parser.add_argument("--generations", type=int, default=100)
    parser.add_argument("--population", type=int, default=50)
    parser.add_argument("--mutation-rate", type=float, default=0.08)
    args = parser.parse_args()

    os.makedirs("outputs", exist_ok=True)
    history = run_evolution(args.population, args.generations, args.mutation_rate)
    visualize_evolution(history)

    # Save results
    with open("outputs/evolution_history.json", "w") as f:
        json.dump(history, f, indent=2)
    print("Saved: outputs/evolution_history.json")
