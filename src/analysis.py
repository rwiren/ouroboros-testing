"""analysis.py — Statistical analysis and parameter sensitivity for the CGA.

Provides two main capabilities:

1. **Multi-run statistical analysis** — runs the genetic algorithm with *n*
   independent random seeds and reports mean ± std of key metrics.  A single
   run is anecdotal; 30 runs provide the minimum sample size for reliable
   inference (Eiben & Smith 2003, §11.2).

2. **Parameter sensitivity analysis** — sweeps one hyperparameter at a time
   while holding the others fixed, following the one-factor-at-a-time (OFAT)
   protocol described in Eiben & Smith (2003, §11.4).  Useful for identifying
   which parameters most influence convergence speed and final quality.

Usage (CLI)
-----------
    python src/analysis.py --mode multi-run --runs 30 --generations 100
    python src/analysis.py --mode sensitivity --param mutation_rate
"""

from __future__ import annotations

import logging
import os
import sys
from typing import Any, Dict, List, Optional

import matplotlib.pyplot as plt
import numpy as np

# Allow running as a script directly from the src/ directory
sys.path.insert(0, os.path.dirname(__file__))
from fitness import OUR_UNIVERSE, gaussian_fitness  # noqa: E402
from evolution import run_evolution  # noqa: E402

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Multi-run statistical analysis
# ---------------------------------------------------------------------------

def multi_run_analysis(
    n_runs: int = 30,
    population_size: int = 50,
    generations: int = 100,
    mutation_rate: float = 0.08,
    elite_frac: float = 0.2,
    fitness_fn=None,
    convergence_threshold: float = 0.9,
) -> Dict[str, Any]:
    """Run the GA *n_runs* times with seeds 0 … n_runs-1 and aggregate stats.

    Parameters
    ----------
    n_runs:
        Number of independent replicates.
    population_size, generations, mutation_rate, elite_frac:
        Evolution hyperparameters (passed through to :func:`~evolution.run_evolution`).
    fitness_fn:
        Fitness callable.  Defaults to :func:`~fitness.gaussian_fitness`.
    convergence_threshold:
        Best-fitness threshold used to define the "convergence generation"
        (first generation where best fitness exceeds this value).

    Returns
    -------
    dict
        Keys: ``final_fitness``, ``convergence_gen``, ``final_distance``,
        each a list of *n_runs* scalar values, plus summary statistics
        under ``summary``.
    """
    if fitness_fn is None:
        fitness_fn = gaussian_fitness

    final_fitnesses: List[float] = []
    convergence_gens: List[int] = []
    final_distances: List[float] = []

    our = OUR_UNIVERSE

    for seed in range(n_runs):
        logger.info("Multi-run: seed %d / %d", seed + 1, n_runs)
        history = run_evolution(
            population_size=population_size,
            generations=generations,
            mutation_rate=mutation_rate,
            elite_frac=elite_frac,
            seed=seed,
            fitness_fn=fitness_fn,
        )

        # Final best fitness
        final_fitnesses.append(history["best_fitness"][-1])

        # Convergence generation: first gen exceeding threshold
        conv_gen = generations  # did not converge
        for g, f in zip(history["generations"], history["best_fitness"]):
            if f >= convergence_threshold:
                conv_gen = g
                break
        convergence_gens.append(conv_gen)

        # Euclidean distance from final best constants to our universe
        bc = history["best_constants"][-1]
        dist = float(np.sqrt(sum((bc[k] - our[k]) ** 2 for k in our)))
        final_distances.append(dist)

    results: Dict[str, Any] = {
        "final_fitness":    final_fitnesses,
        "convergence_gen":  convergence_gens,
        "final_distance":   final_distances,
        "n_runs":           n_runs,
        "config": {
            "population_size": population_size,
            "generations":     generations,
            "mutation_rate":   mutation_rate,
            "elite_frac":      elite_frac,
        },
        "summary": {
            "final_fitness_mean":   float(np.mean(final_fitnesses)),
            "final_fitness_std":    float(np.std(final_fitnesses)),
            "convergence_gen_mean": float(np.mean(convergence_gens)),
            "convergence_gen_std":  float(np.std(convergence_gens)),
            "final_distance_mean":  float(np.mean(final_distances)),
            "final_distance_std":   float(np.std(final_distances)),
        },
    }

    s = results["summary"]
    logger.info(
        "Multi-run summary (%d runs): "
        "final_fitness=%.3f±%.3f  conv_gen=%.1f±%.1f  distance=%.3f±%.3f",
        n_runs,
        s["final_fitness_mean"],  s["final_fitness_std"],
        s["convergence_gen_mean"], s["convergence_gen_std"],
        s["final_distance_mean"],  s["final_distance_std"],
    )

    return results


def plot_multi_run_summary(results: Dict[str, Any], output_path: str = "outputs/multi_run_summary.png") -> None:
    """Box-and-whisker summary of multi-run statistics.

    Parameters
    ----------
    results:
        Dict returned by :func:`multi_run_analysis`.
    output_path:
        Where to save the figure.
    """
    fig, axes = plt.subplots(1, 3, figsize=(14, 5))

    metrics = [
        ("final_fitness",   "Final Best Fitness",    "blue"),
        ("convergence_gen", "Convergence Generation", "green"),
        ("final_distance",  "Final Distance to Our Universe", "red"),
    ]

    for ax, (key, title, color) in zip(axes, metrics):
        vals = results[key]
        bp = ax.boxplot(vals, patch_artist=True,
                        boxprops=dict(facecolor=color, alpha=0.4),
                        medianprops=dict(color="black", lw=2))
        mean = np.mean(vals)
        std  = np.std(vals)
        ax.axhline(mean, color=color, lw=1.5, linestyle="--", alpha=0.8, label=f"mean={mean:.3f}")
        ax.set_title(title)
        ax.set_xticks([])
        ax.set_ylabel(title)
        ax.legend(fontsize=9)
        ax.text(1.05, mean, f"±{std:.3f}", va="center", fontsize=8,
                color=color, transform=ax.get_yaxis_transform())
        ax.grid(True, alpha=0.3)

    n = results["n_runs"]
    cfg = results["config"]
    plt.suptitle(
        f"Multi-Run Analysis ({n} seeds) — pop={cfg['population_size']}, "
        f"gen={cfg['generations']}, μ={cfg['mutation_rate']}",
        fontsize=12,
    )
    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    plt.savefig(output_path, dpi=150)
    plt.close(fig)
    logger.info("Saved multi-run plot: %s", output_path)


# ---------------------------------------------------------------------------
# Parameter sensitivity analysis
# ---------------------------------------------------------------------------

#: Default parameter grid for one-factor-at-a-time sweeps.
SENSITIVITY_GRID: Dict[str, List[Any]] = {
    "mutation_rate":   [0.02, 0.04, 0.06, 0.08, 0.10, 0.15, 0.20],
    "population_size": [20, 30, 50, 80, 120, 200],
    "elite_frac":      [0.05, 0.10, 0.20, 0.30, 0.40],
    "generations":     [25, 50, 75, 100, 150, 200],
}


def sensitivity_analysis(
    param_name: str,
    values: Optional[List[Any]] = None,
    n_runs: int = 10,
    base_population_size: int = 50,
    base_generations: int = 100,
    base_mutation_rate: float = 0.08,
    base_elite_frac: float = 0.2,
    convergence_threshold: float = 0.9,
) -> Dict[str, Any]:
    """Sweep one parameter while holding others at their base values.

    Parameters
    ----------
    param_name:
        One of ``mutation_rate``, ``population_size``, ``elite_frac``,
        ``generations``.
    values:
        Values to sweep.  Defaults to :data:`SENSITIVITY_GRID[param_name]`.
    n_runs:
        Independent replicates per parameter value.
    base_*:
        Held-fixed base configuration.
    convergence_threshold:
        Fitness threshold defining "convergence generation".

    Returns
    -------
    dict
        Keys ``param_name``, ``values``, and for each value a sub-dict with
        ``final_fitness``, ``convergence_gen``, ``final_distance`` lists.
    """
    if values is None:
        if param_name not in SENSITIVITY_GRID:
            raise ValueError(
                f"Unknown param '{param_name}'. "
                f"Choose from: {list(SENSITIVITY_GRID)}"
            )
        values = SENSITIVITY_GRID[param_name]

    our = OUR_UNIVERSE
    per_value: List[Dict[str, Any]] = []

    for val in values:
        cfg = {
            "population_size": base_population_size,
            "generations":     base_generations,
            "mutation_rate":   base_mutation_rate,
            "elite_frac":      base_elite_frac,
        }
        cfg[param_name] = val

        final_fitnesses: List[float] = []
        convergence_gens: List[int] = []
        final_distances: List[float] = []

        for seed in range(n_runs):
            logger.info("Sensitivity %s=%s  seed %d/%d", param_name, val, seed + 1, n_runs)
            history = run_evolution(seed=seed, fitness_fn=gaussian_fitness, **cfg)

            final_fitnesses.append(history["best_fitness"][-1])

            conv_gen = cfg["generations"]
            for g, f in zip(history["generations"], history["best_fitness"]):
                if f >= convergence_threshold:
                    conv_gen = g
                    break
            convergence_gens.append(conv_gen)

            bc = history["best_constants"][-1]
            dist = float(np.sqrt(sum((bc[k] - our[k]) ** 2 for k in our)))
            final_distances.append(dist)

        per_value.append({
            "value":          val,
            "final_fitness":  final_fitnesses,
            "convergence_gen": convergence_gens,
            "final_distance": final_distances,
            "mean_fitness":   float(np.mean(final_fitnesses)),
            "std_fitness":    float(np.std(final_fitnesses)),
            "mean_conv_gen":  float(np.mean(convergence_gens)),
            "std_conv_gen":   float(np.std(convergence_gens)),
        })

    return {
        "param_name":  param_name,
        "values":      values,
        "per_value":   per_value,
        "n_runs":      n_runs,
        "base_config": {
            "population_size": base_population_size,
            "generations":     base_generations,
            "mutation_rate":   base_mutation_rate,
            "elite_frac":      base_elite_frac,
        },
    }


def plot_sensitivity(
    results: Dict[str, Any],
    output_path: Optional[str] = None,
) -> None:
    """Plot mean ± std of key metrics across parameter values.

    Parameters
    ----------
    results:
        Dict returned by :func:`sensitivity_analysis`.
    output_path:
        Where to save the figure.  Defaults to
        ``outputs/sensitivity_<param_name>.png``.
    """
    param = results["param_name"]
    if output_path is None:
        output_path = f"outputs/sensitivity_{param}.png"

    pv    = results["per_value"]
    xs    = [d["value"] for d in pv]
    means = [d["mean_fitness"]  for d in pv]
    stds  = [d["std_fitness"]   for d in pv]
    conv  = [d["mean_conv_gen"] for d in pv]
    conv_std = [d["std_conv_gen"] for d in pv]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    ax1.errorbar(xs, means, yerr=stds, fmt="o-", color="blue", capsize=4)
    ax1.set_xlabel(param)
    ax1.set_ylabel("Final Best Fitness (mean ± std)")
    ax1.set_title(f"Fitness vs {param}")
    ax1.grid(True, alpha=0.3)

    ax2.errorbar(xs, conv, yerr=conv_std, fmt="s-", color="green", capsize=4)
    ax2.set_xlabel(param)
    ax2.set_ylabel("Convergence Generation (mean ± std)")
    ax2.set_title(f"Convergence Speed vs {param}")
    ax2.grid(True, alpha=0.3)

    n = results["n_runs"]
    plt.suptitle(f"Sensitivity Analysis: {param}  ({n} runs per value)", fontsize=12)
    plt.tight_layout()
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    plt.savefig(output_path, dpi=150)
    plt.close(fig)
    logger.info("Saved sensitivity plot: %s", output_path)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> None:
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Ouroboros statistical analysis tools")
    parser.add_argument("--mode",        choices=["multi-run", "sensitivity"], required=True)
    parser.add_argument("--runs",        type=int,   default=30,
                        help="Number of independent replicates (multi-run mode)")
    parser.add_argument("--generations", type=int,   default=100)
    parser.add_argument("--population",  type=int,   default=50)
    parser.add_argument("--mutation-rate", type=float, default=0.08)
    parser.add_argument("--elite-frac",  type=float, default=0.2)
    parser.add_argument("--param",       type=str,   default="mutation_rate",
                        help="Parameter to sweep (sensitivity mode)")
    parser.add_argument("--output-dir",  type=str,   default="outputs")
    parser.add_argument("--log-level",   choices=["DEBUG", "INFO", "WARNING"], default="INFO")
    args = parser.parse_args()

    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    os.makedirs(args.output_dir, exist_ok=True)

    if args.mode == "multi-run":
        results = multi_run_analysis(
            n_runs=args.runs,
            population_size=args.population,
            generations=args.generations,
            mutation_rate=args.mutation_rate,
            elite_frac=args.elite_frac,
        )
        out_json = os.path.join(args.output_dir, "multi_run_results.json")
        with open(out_json, "w") as fh:
            json.dump(results, fh, indent=2)
        logger.info("Saved: %s", out_json)
        plot_multi_run_summary(
            results,
            output_path=os.path.join(args.output_dir, "multi_run_summary.png"),
        )

        s = results["summary"]
        print(f"\n{'='*60}")
        print(f"Multi-Run Results ({results['n_runs']} independent seeds)")
        print(f"{'='*60}")
        print(f"Final best fitness : {s['final_fitness_mean']:.3f} ± {s['final_fitness_std']:.3f}")
        print(f"Convergence gen    : {s['convergence_gen_mean']:.1f} ± {s['convergence_gen_std']:.1f}")
        print(f"Distance to target : {s['final_distance_mean']:.3f} ± {s['final_distance_std']:.3f}")

    elif args.mode == "sensitivity":
        results = sensitivity_analysis(
            param_name=args.param,
            n_runs=args.runs,
            base_population_size=args.population,
            base_generations=args.generations,
            base_mutation_rate=args.mutation_rate,
            base_elite_frac=args.elite_frac,
        )
        out_json = os.path.join(args.output_dir, f"sensitivity_{args.param}.json")
        with open(out_json, "w") as fh:
            json.dump(results, fh, indent=2)
        logger.info("Saved: %s", out_json)
        plot_sensitivity(
            results,
            output_path=os.path.join(args.output_dir, f"sensitivity_{args.param}.png"),
        )


if __name__ == "__main__":
    main()
