"""speciation.py — Multi-population niched GA for discovering alternative physics.

Tests whether our universe is the only stable attractor, or if alien physics
matrices can also sustain complex intelligence (multiple fitness peaks).

Uses fitness sharing: universes near each other in parameter space share a
fitness penalty, forcing populations to speciate into separate peaks.

**Important caveat on the fitness peaks**
-----------------------------------------
The three peaks defined in :func:`multimodal_fitness` are **hypothetical toy
configurations**, not physically derived alternatives.  The "Silicon Universe"
and "Plasma Universe" parameter vectors are chosen to create well-separated
peaks in the 6D constant space for demonstration purposes.  They do not
correspond to specific proposals in the alternative-physics literature (e.g.,
Harnik et al. 2006 on weakless universes, or Adams 2019 §7 on alternate
chemistry).  Do not interpret convergence toward these peaks as evidence for
viable alternative physics.
"""

import os
import sys
from typing import Optional

import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA

# Allow running as a script directly from the src/ directory
sys.path.insert(0, os.path.dirname(__file__))


def multimodal_fitness(c):
    """Multi-modal fitness landscape with several viable physics configurations.
    
    Peak 1: Our universe (carbon-based life)
    Peak 2: "Silicon universe" — stronger EM, weaker gravity
    Peak 3: "Plasma universe" — strong force dominant, high energy
    """
    vals = np.array(list(c.values()))
    
    peaks = [
        {"center": np.array([0.15, 0.45, 0.65, 0.30, 0.02, 0.55]), "height": 1.0, "sigma": 0.12},  # Our universe
        {"center": np.array([0.08, 0.70, 0.50, 0.25, 0.05, 0.40]), "height": 0.85, "sigma": 0.10},  # Silicon universe
        {"center": np.array([0.30, 0.35, 0.85, 0.45, 0.01, 0.65]), "height": 0.75, "sigma": 0.11},  # Plasma universe
    ]
    
    fitness = 0
    for peak in peaks:
        dist = np.sqrt(np.sum((vals - peak["center"])**2))
        fitness = max(fitness, peak["height"] * np.exp(-dist**2 / (2 * peak["sigma"]**2)))
    return fitness


def fitness_sharing(population, fitnesses, sigma_share=0.15, alpha=1.0):
    """Apply fitness sharing to promote niche formation."""
    n = len(population)
    shared = np.array(fitnesses, dtype=float)
    
    for i in range(n):
        niche_count = 0
        vi = np.array(list(population[i].values()))
        for j in range(n):
            vj = np.array(list(population[j].values()))
            dist = np.sqrt(np.sum((vi - vj)**2))
            if dist < sigma_share:
                niche_count += 1 - (dist / sigma_share) ** alpha
        shared[i] = fitnesses[i] / max(1, niche_count)
    return shared


def run_speciation(pop_size=120, generations=150, mutation_rate=0.06, seed: Optional[int] = None):
    """Run niched GA to discover multiple attractors.

    Parameters
    ----------
    pop_size:
        Population size.
    generations:
        Number of generations.
    mutation_rate:
        Standard deviation of Gaussian mutations.
    seed:
        Integer seed for reproducibility.  Leave *None* for a non-deterministic run.
    """
    rng = np.random.default_rng(seed)
    keys = ["Gravity (G)", "EM Coupling (α)", "Strong Force", "Weak Force", "Dark Energy (Λ)", "Mass Ratio (mₚ/mₑ)"]
    population = [{k: float(rng.uniform(0, 1)) for k in keys} for _ in range(pop_size)]

    all_positions = []  # Track all individuals over time
    history = {"gen": [], "n_species": [], "best_fit": [], "species_centers": []}

    for gen in range(generations):
        # Evaluate
        raw_fitnesses = [multimodal_fitness(u) for u in population]

        # Apply fitness sharing
        shared_fitnesses = fitness_sharing(population, raw_fitnesses)

        # Record
        all_positions.append([list(u.values()) for u in population])

        # Identify species (cluster by proximity)
        vals = np.array([list(u.values()) for u in population])
        from scipy.cluster.hierarchy import fcluster, linkage
        Z = linkage(vals, method='ward')
        clusters = fcluster(Z, t=0.3, criterion='distance')
        n_species = len(set(clusters))

        history["gen"].append(gen)
        history["n_species"].append(n_species)
        history["best_fit"].append(max(raw_fitnesses))

        # Species centers
        centers = []
        for cid in set(clusters):
            mask = clusters == cid
            center = vals[mask].mean(axis=0)
            centers.append(center.tolist())
        history["species_centers"].append(centers)

        # Selection + reproduction
        ranked = np.argsort(shared_fitnesses)[::-1]
        n_elite = max(4, pop_size // 5)
        elite = [population[i] for i in ranked[:n_elite]]

        new_pop = list(elite)
        while len(new_pop) < pop_size:
            parent = elite[rng.integers(0, n_elite)]
            child = {}
            for k, v in parent.items():
                if rng.random() < 0.3:
                    child[k] = float(np.clip(v + rng.normal(0, mutation_rate), 0, 1))
                else:
                    child[k] = v
            new_pop.append(child)
        population = new_pop

        if gen % 50 == 0:
            print(f"Gen {gen}: {n_species} species, best={max(raw_fitnesses):.3f}")

    return history, np.array(all_positions)


def visualize_speciation(history, all_positions):
    """Visualize species formation using PCA."""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # PCA of final generation
    final_gen = all_positions[-1]
    pca = PCA(n_components=2)
    pca.fit(all_positions[0])  # Fit on initial for consistent axes
    
    # Plot initial vs final
    ax = axes[0, 0]
    proj = pca.transform(all_positions[0])
    ax.scatter(proj[:, 0], proj[:, 1], c='gray', alpha=0.5, s=20)
    ax.set_title("Generation 0 — Random Initialization")
    ax.set_xlabel("PC1"); ax.set_ylabel("PC2")
    
    ax = axes[0, 1]
    proj = pca.transform(all_positions[-1])
    # Color by nearest peak
    peaks = np.array([[0.15, 0.45, 0.65, 0.30, 0.02, 0.55],
                      [0.08, 0.70, 0.50, 0.25, 0.05, 0.40],
                      [0.30, 0.35, 0.85, 0.45, 0.01, 0.65]])
    colors = []
    for ind in all_positions[-1]:
        dists = [np.sqrt(np.sum((np.array(ind) - p)**2)) for p in peaks]
        colors.append(['blue', 'red', 'green'][np.argmin(dists)])
    ax.scatter(proj[:, 0], proj[:, 1], c=colors, alpha=0.7, s=30)
    ax.set_title(f"Generation {len(all_positions)-1} — Speciated")
    ax.set_xlabel("PC1"); ax.set_ylabel("PC2")
    
    # Mark peaks
    peak_proj = pca.transform(peaks)
    for i, (px, py) in enumerate(peak_proj):
        label = ["Our Universe", "Silicon Universe", "Plasma Universe"][i]
        ax.plot(px, py, '*', markersize=20, color=['blue', 'red', 'green'][i], markeredgecolor='black')
        ax.annotate(label, (px, py), fontsize=8, ha='center', va='bottom')
    
    # Species count over time
    ax = axes[1, 0]
    ax.plot(history["gen"], history["n_species"], 'purple', lw=2)
    ax.set_xlabel("Generation"); ax.set_ylabel("Number of Species")
    ax.set_title("🧬 Speciation Over Time"); ax.grid(True, alpha=0.3)
    
    # Fitness
    ax = axes[1, 1]
    ax.plot(history["gen"], history["best_fit"], 'b-', lw=2)
    ax.set_xlabel("Generation"); ax.set_ylabel("Best Fitness")
    ax.set_title("🏆 Peak Fitness"); ax.grid(True, alpha=0.3)
    
    plt.suptitle("Multiple Attractors — Can Alternative Physics Sustain Intelligence?", fontsize=14)
    plt.tight_layout()
    plt.savefig("speciation_results.png", dpi=150, bbox_inches='tight')
    plt.show()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Ouroboros Speciation GA")
    parser.add_argument("--pop-size",      type=int,   default=120)
    parser.add_argument("--generations",   type=int,   default=150)
    parser.add_argument("--mutation-rate", type=float, default=0.06)
    parser.add_argument("--seed",          type=int,   default=None)
    args = parser.parse_args()

    history, positions = run_speciation(
        pop_size=args.pop_size,
        generations=args.generations,
        mutation_rate=args.mutation_rate,
        seed=args.seed,
    )
    visualize_speciation(history, positions)
