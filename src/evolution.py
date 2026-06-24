"""evolution.py — Cosmological Genetic Algorithm

Simulates universe evolution through intelligence-driven cycles.
Each universe has physical constants; those producing intelligence
get to reproduce (spawn new universes with mutated constants).

The Ouroboros question: does this converge toward our universe's constants?

Refactored design
-----------------
The monolithic ``run_evolution`` loop has been split into small, testable
units: :func:`initialize_population`, :func:`evaluate_population`,
:func:`select_elite`, :func:`reproduce`.  All random operations accept an
explicit ``numpy.random.Generator`` (``rng``) so results are reproducible
with a fixed ``seed``.  The default fitness function is now
:func:`~fitness.gaussian_fitness` — the Gaussian geometric-mean model that
is grounded in the anthropic constraint literature (Davies 2003).
"""

from __future__ import annotations

import datetime
import json
import logging
import os
import sys
from dataclasses import dataclass, field
from typing import Callable, List, Optional

import matplotlib.pyplot as plt
import numpy as np

# Allow running as a script directly from the src/ directory
sys.path.insert(0, os.path.dirname(__file__))
from fitness import FitnessFunction, OUR_UNIVERSE, gaussian_fitness  # noqa: E402

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Universe dataclass
# ---------------------------------------------------------------------------

@dataclass
class Universe:
    """A universe defined by its fundamental physical constants."""

    constants: dict = field(default_factory=dict)
    fitness: float = 0.0
    generation: int = 0
    parent_id: int = -1
    id: int = 0

    def __post_init__(self) -> None:
        if not self.constants:
            # Fallback: use global RNG (legacy path, not reproducible)
            self.constants = {k: float(np.random.uniform(0, 1)) for k in OUR_UNIVERSE}

    @classmethod
    def random(cls, rng: np.random.Generator, id: int = 0) -> "Universe":
        """Create a universe with random constants drawn from *rng*.

        Parameters
        ----------
        rng:
            A seeded :class:`numpy.random.Generator` for reproducibility.
        id:
            Integer identifier (used for lineage tracking).
        """
        constants = {k: float(rng.uniform(0, 1)) for k in OUR_UNIVERSE}
        return cls(constants=constants, id=id)

    @staticmethod
    def our_universe() -> dict:
        """Return the normalized constants of our universe (proxy for ``OUR_UNIVERSE``)."""
        return dict(OUR_UNIVERSE)


# ---------------------------------------------------------------------------
# Mutation operator
# ---------------------------------------------------------------------------

def mutate(
    constants: dict,
    mutation_rate: float = 0.1,
    rng: Optional[np.random.Generator] = None,
) -> dict:
    """Mutate constants — information carried through the singularity.

    Each constant is mutated independently with probability 0.3.  Mutations
    are Gaussian perturbations with standard deviation *mutation_rate*,
    clipped to [0, 1].

    Parameters
    ----------
    constants:
        Source constants dict.
    mutation_rate:
        Standard deviation of the Gaussian perturbation.
    rng:
        Seeded generator.  If *None*, falls back to the global NumPy RNG
        (not reproducible — pass an explicit rng for academic use).
    """
    _rng = rng if rng is not None else np.random.default_rng()
    new = {}
    for key, val in constants.items():
        if _rng.random() < 0.3:
            new[key] = float(np.clip(val + _rng.normal(0, mutation_rate), 0.0, 1.0))
        else:
            new[key] = val
    return new


# ---------------------------------------------------------------------------
# Decomposed evolution steps
# ---------------------------------------------------------------------------

def initialize_population(
    population_size: int,
    rng: np.random.Generator,
) -> List[Universe]:
    """Create an initial population of universes with random constants.

    Parameters
    ----------
    population_size:
        Number of universes in the population.
    rng:
        Seeded generator.
    """
    return [Universe.random(rng, id=i) for i in range(population_size)]


def evaluate_population(
    population: List[Universe],
    fitness_fn: FitnessFunction,
    generation: int = 0,
) -> None:
    """Evaluate fitness of every universe in *population* (in-place update).

    Parameters
    ----------
    population:
        List of :class:`Universe` instances to evaluate.
    fitness_fn:
        Any callable satisfying :class:`~fitness.FitnessFunction`.
    generation:
        Current generation index, stored on each universe for bookkeeping.
    """
    for u in population:
        u.fitness = fitness_fn(u.constants)
        u.generation = generation


def select_elite(
    population: List[Universe],
    elite_frac: float = 0.2,
) -> List[Universe]:
    """Sort *population* by fitness and return the top fraction as elite.

    The sort is **in-place** so ``population[0]`` is the best after this call.

    Parameters
    ----------
    population:
        Already-evaluated list of universes.
    elite_frac:
        Fraction to keep (e.g. 0.2 → top 20 %).

    Returns
    -------
    List[Universe]
        The elite subset (at least 2 individuals).
    """
    population.sort(key=lambda u: u.fitness, reverse=True)
    n_elite = max(2, int(len(population) * elite_frac))
    return population[:n_elite]


def reproduce(
    elite: List[Universe],
    target_size: int,
    mutation_rate: float,
    rng: np.random.Generator,
) -> List[Universe]:
    """Fill a new population by mutating elite universes.

    Elite individuals survive unchanged (elitist strategy); children are
    created by randomly selecting an elite parent and applying :func:`mutate`.

    Parameters
    ----------
    elite:
        Top-ranked universes that survive to the next generation.
    target_size:
        Desired population size.
    mutation_rate:
        Passed to :func:`mutate`.
    rng:
        Seeded generator.
    """
    new_population: List[Universe] = list(elite)
    while len(new_population) < target_size:
        parent = elite[rng.integers(0, len(elite))]
        child_constants = mutate(parent.constants, mutation_rate, rng)
        child = Universe(constants=child_constants, parent_id=parent.id)
        new_population.append(child)
    return new_population


# ---------------------------------------------------------------------------
# Main orchestrator
# ---------------------------------------------------------------------------

def run_evolution(
    population_size: int = 50,
    generations: int = 100,
    mutation_rate: float = 0.08,
    elite_frac: float = 0.2,
    seed: Optional[int] = None,
    fitness_fn: Optional[FitnessFunction] = None,
) -> dict:
    """Run the cosmological genetic algorithm.

    Parameters
    ----------
    population_size:
        Number of universes per generation.
    generations:
        Number of cosmic cycles to simulate.
    mutation_rate:
        Standard deviation of Gaussian mutations applied to each constant.
    elite_frac:
        Fraction of top individuals that survive each generation.
    seed:
        Integer seed for :class:`numpy.random.Generator`.  Set to reproduce
        results exactly; leave *None* for a non-deterministic run.
    fitness_fn:
        Callable matching :class:`~fitness.FitnessFunction`.  Defaults to
        :func:`~fitness.gaussian_fitness`.

    Returns
    -------
    dict
        History dict with keys ``generations``, ``best_fitness``,
        ``mean_fitness``, ``best_constants``, ``diversity``.
    """
    if fitness_fn is None:
        fitness_fn = gaussian_fitness

    rng = np.random.default_rng(seed)
    population = initialize_population(population_size, rng)

    history: dict = {
        "generations":    [],
        "best_fitness":   [],
        "mean_fitness":   [],
        "best_constants": [],
        "diversity":      [],
    }

    our = OUR_UNIVERSE
    logger.info(
        "Starting evolution: generations=%d population=%d "
        "mutation_rate=%.3f elite_frac=%.2f seed=%s",
        generations, population_size, mutation_rate, elite_frac, seed,
    )
    logger.debug("Target (our universe): %s", our)

    for gen in range(generations):
        evaluate_population(population, fitness_fn, generation=gen)
        elite = select_elite(population, elite_frac)

        fitnesses = [u.fitness for u in population]
        best = population[0]
        diversity = float(np.std([[v for v in u.constants.values()] for u in population]))

        history["generations"].append(gen)
        history["best_fitness"].append(float(best.fitness))
        history["mean_fitness"].append(float(np.mean(fitnesses)))
        history["best_constants"].append(dict(best.constants))
        history["diversity"].append(diversity)

        if gen % 20 == 0 or gen == generations - 1:
            dist = float(np.sqrt(sum((best.constants[k] - our[k]) ** 2 for k in our)))
            logger.info(
                "Gen %3d | Best: %.4f | Mean: %.4f | Dist to us: %.3f | Diversity: %.3f",
                gen, best.fitness, np.mean(fitnesses), dist, diversity,
            )

        population = reproduce(elite, population_size, mutation_rate, rng)

    return history


# ---------------------------------------------------------------------------
# Visualisation
# ---------------------------------------------------------------------------

def visualize_evolution(
    history: dict,
    output_path: str = "outputs/ouroboros_evolution.png",
) -> None:
    """Plot the evolutionary trajectory and save to *output_path*.

    Parameters
    ----------
    history:
        Dict returned by :func:`run_evolution`.
    output_path:
        File path for the saved figure.
    """
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))

    ax = axes[0, 0]
    ax.plot(history["generations"], history["best_fitness"], "b-", label="Best")
    ax.plot(history["generations"], history["mean_fitness"], "r--", alpha=0.7, label="Mean")
    ax.set_xlabel("Generation (Cosmic Cycle)")
    ax.set_ylabel("Fitness (Intelligence Emergence)")
    ax.set_title("Ouroboros Evolution — Fitness Convergence")
    ax.legend()
    ax.grid(True, alpha=0.3)

    our = OUR_UNIVERSE
    distances = [
        float(np.sqrt(sum((h[k] - our[k]) ** 2 for k in our)))
        for h in history["best_constants"]
    ]
    ax = axes[0, 1]
    ax.plot(history["generations"], distances, "g-")
    ax.set_xlabel("Generation")
    ax.set_ylabel("Distance to Our Universe")
    ax.set_title("Convergence Toward Our Constants")
    ax.grid(True, alpha=0.3)

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

    ax = axes[1, 1]
    ax.plot(history["generations"], history["diversity"], "m-")
    ax.set_xlabel("Generation")
    ax.set_ylabel("Population Diversity")
    ax.set_title("Genetic Diversity Over Time")
    ax.grid(True, alpha=0.3)

    plt.suptitle("The Ouroboros Singularity — Cosmological Genetic Algorithm", fontsize=14)
    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    plt.savefig(output_path, dpi=150)
    plt.close(fig)
    logger.info("Saved plot: %s", output_path)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def _make_run_dir(base_dir: str, seed: Optional[int], generations: int) -> str:
    """Return a timestamped output directory path and create it."""
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    seed_tag = f"seed{seed}" if seed is not None else "unseeded"
    run_dir = os.path.join(base_dir, f"run_{ts}_{seed_tag}_gen{generations}")
    os.makedirs(run_dir, exist_ok=True)
    return run_dir


def main() -> None:
    """CLI entry point.  Supports both argparse flags and a YAML config file."""
    import argparse

    parser = argparse.ArgumentParser(description="Ouroboros Cosmological GA")
    parser.add_argument("--config",        type=str,   default=None,
                        help="Path to YAML config file (e.g. configs/default.yaml)")
    parser.add_argument("--generations",   type=int,   default=None)
    parser.add_argument("--population",    type=int,   default=None)
    parser.add_argument("--mutation-rate", type=float, default=None)
    parser.add_argument("--seed",          type=int,   default=None)
    parser.add_argument("--output-dir",    type=str,   default=None)
    parser.add_argument("--fitness",       choices=["gaussian", "ca"], default=None)
    parser.add_argument("--log-level",     choices=["DEBUG", "INFO", "WARNING"],
                        default="INFO")
    args = parser.parse_args()

    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    # Defaults
    cfg: dict = {
        "population_size": 50,
        "generations":     100,
        "mutation_rate":   0.08,
        "elite_frac":      0.2,
        "seed":            None,
        "fitness_fn":      "gaussian",
        "output_dir":      "outputs",
    }

    # Override from config file
    if args.config:
        try:
            import yaml
        except ImportError:
            logger.error("pyyaml is required to load config files: pip install pyyaml")
            raise
        with open(args.config) as fh:
            file_cfg = yaml.safe_load(fh)
        cfg.update(file_cfg.get("evolution", {}))
        out_cfg = file_cfg.get("output", {})
        if "base_dir" in out_cfg:
            cfg["output_dir"] = out_cfg["base_dir"]

    # CLI flags override config file
    if args.generations   is not None: cfg["generations"]     = args.generations
    if args.population    is not None: cfg["population_size"] = args.population
    if args.mutation_rate is not None: cfg["mutation_rate"]   = args.mutation_rate
    if args.seed          is not None: cfg["seed"]            = args.seed
    if args.output_dir    is not None: cfg["output_dir"]      = args.output_dir
    if args.fitness       is not None: cfg["fitness_fn"]      = args.fitness

    # Resolve fitness function
    if cfg["fitness_fn"] == "ca":
        from complexity import ca_fitness
        fit_fn: FitnessFunction = ca_fitness
    else:
        fit_fn = gaussian_fitness

    run_dir = _make_run_dir(cfg["output_dir"], cfg["seed"], cfg["generations"])

    history = run_evolution(
        population_size=cfg["population_size"],
        generations=cfg["generations"],
        mutation_rate=cfg["mutation_rate"],
        elite_frac=cfg["elite_frac"],
        seed=cfg["seed"],
        fitness_fn=fit_fn,
    )

    visualize_evolution(history, output_path=os.path.join(run_dir, "ouroboros_evolution.png"))

    json_path = os.path.join(run_dir, "evolution_history.json")
    with open(json_path, "w") as fh:
        json.dump(history, fh, indent=2)
    logger.info("Saved history: %s", json_path)


if __name__ == "__main__":
    main()
