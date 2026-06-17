"""complexity.py — Cellular Automata emergence engine.

Replaces the Gaussian proxy fitness with actual complexity measurement.
Each universe's constants are mapped to a 2D cellular automata rule-set.
We run the CA and measure emergent complexity via Shannon entropy + compression.

The "edge of chaos" — moderate entropy, low compression — indicates
complex self-organizing systems (where intelligence could emerge).
"""

import numpy as np
import matplotlib.pyplot as plt
from collections import Counter
import zlib


def constants_to_ca_rule(constants: dict) -> dict:
    """Map physical constants to cellular automata parameters.
    
    Constants determine:
    - birth/survival thresholds (from gravity + strong force)
    - neighborhood radius (from EM coupling)
    - decay rate (from dark energy / cosmological constant)
    """
    vals = list(constants.values())
    
    # Birth threshold: how many neighbors needed to create life
    birth_min = int(vals[0] * 4) + 1  # 1-4 based on gravity
    birth_max = birth_min + int(vals[2] * 3) + 1  # range from strong force
    
    # Survival threshold
    survive_min = max(1, int(vals[1] * 3))  # from EM coupling
    survive_max = survive_min + int(vals[5] * 4) + 1  # from mass ratio
    
    # Decay probability (dark energy destroys structure)
    decay = vals[4] * 0.3  # 0-30% chance of spontaneous death
    
    return {
        "birth": set(range(birth_min, min(birth_max + 1, 9))),
        "survive": set(range(survive_min, min(survive_max + 1, 9))),
        "decay": decay,
        "grid_size": 64,
    }


def run_ca(rule: dict, steps: int = 100) -> np.ndarray:
    """Run 2D cellular automata with given rules. Returns history."""
    size = rule["grid_size"]
    grid = (np.random.random((size, size)) < 0.3).astype(np.uint8)
    history = [grid.copy()]
    
    for _ in range(steps):
        # Count neighbors (Moore neighborhood)
        neighbors = sum(
            np.roll(np.roll(grid, i, axis=0), j, axis=1)
            for i in [-1, 0, 1] for j in [-1, 0, 1]
            if not (i == 0 and j == 0)
        )
        
        # Apply rules
        new_grid = np.zeros_like(grid)
        # Birth
        birth_mask = (grid == 0) & np.isin(neighbors, list(rule["birth"]))
        new_grid[birth_mask] = 1
        # Survival
        survive_mask = (grid == 1) & np.isin(neighbors, list(rule["survive"]))
        new_grid[survive_mask] = 1
        # Decay
        if rule["decay"] > 0:
            decay_mask = np.random.random((size, size)) < rule["decay"]
            new_grid[decay_mask] = 0
        
        grid = new_grid
        history.append(grid.copy())
    
    return np.array(history)


def measure_complexity(history: np.ndarray) -> dict:
    """Measure emergent complexity of a CA run.
    
    Returns metrics that identify "edge of chaos":
    - Shannon entropy of final state
    - Compression ratio (LZW) of full history
    - Activity: fraction of cells that change per step
    - Lifespan: how many steps until static/dead
    """
    # Shannon entropy of final state
    final = history[-1].flatten()
    counts = Counter(final)
    total = len(final)
    entropy = -sum((c/total) * np.log2(c/total) for c in counts.values() if c > 0)
    
    # Compression ratio (proxy for Kolmogorov complexity)
    raw_bytes = history.tobytes()
    compressed = zlib.compress(raw_bytes, level=9)
    compression_ratio = len(compressed) / len(raw_bytes)
    
    # Activity (average fraction of cells changing per step)
    changes = [np.mean(history[i] != history[i-1]) for i in range(1, len(history))]
    mean_activity = np.mean(changes)
    
    # Lifespan (steps until <1% activity)
    lifespan = len(history)
    for i, c in enumerate(changes):
        if c < 0.01:
            lifespan = i
            break
    
    # Complexity score: edge of chaos = moderate entropy + low compression + sustained activity
    # Dead universe: entropy=0, compression~0, activity=0
    # Chaotic: entropy=1, compression~1, high activity (random noise)
    # Complex: entropy~0.7, compression~0.3, moderate sustained activity
    complexity = entropy * (1 - compression_ratio) * min(1.0, mean_activity * 10) * (lifespan / len(history))
    
    return {
        "entropy": entropy,
        "compression_ratio": compression_ratio,
        "mean_activity": mean_activity,
        "lifespan": lifespan,
        "complexity_score": complexity,
    }


def ca_fitness(constants: dict) -> float:
    """Compute fitness by actually running a cellular automaton.
    
    This replaces the Gaussian proxy with measured emergence.
    """
    rule = constants_to_ca_rule(constants)
    history = run_ca(rule, steps=80)
    metrics = measure_complexity(history)
    return metrics["complexity_score"]


def visualize_ca_examples():
    """Show three types of universes: dead, chaotic, complex."""
    keys = ["Gravity (G)", "EM Coupling (α)", "Strong Force", "Weak Force", "Dark Energy (Λ)", "Mass Ratio (mₚ/mₑ)"]
    
    examples = {
        "Dead Universe\n(high dark energy)": dict(zip(keys, [0.15, 0.45, 0.65, 0.30, 0.90, 0.55])),
        "Chaotic Universe\n(extreme forces)": dict(zip(keys, [0.95, 0.95, 0.95, 0.95, 0.00, 0.95])),
        "Complex Universe\n(our constants)": dict(zip(keys, [0.15, 0.45, 0.65, 0.30, 0.02, 0.55])),
    }
    
    fig, axes = plt.subplots(2, 3, figsize=(14, 9))
    
    for col, (name, constants) in enumerate(examples.items()):
        rule = constants_to_ca_rule(constants)
        history = run_ca(rule, steps=80)
        metrics = measure_complexity(history)
        
        # Show final state
        axes[0, col].imshow(history[-1], cmap='viridis', interpolation='nearest')
        axes[0, col].set_title(f"{name}\nComplexity: {metrics['complexity_score']:.3f}", fontsize=10)
        axes[0, col].axis('off')
        
        # Show activity over time
        changes = [np.mean(history[i] != history[i-1]) for i in range(1, len(history))]
        axes[1, col].plot(changes, color=['red', 'orange', 'green'][col], lw=1.5)
        axes[1, col].set_xlabel("Time Step")
        axes[1, col].set_ylabel("Activity")
        axes[1, col].set_title(f"H={metrics['entropy']:.2f}, C={metrics['compression_ratio']:.2f}", fontsize=9)
        axes[1, col].set_ylim(0, 0.6)
        axes[1, col].grid(True, alpha=0.3)
    
    plt.suptitle("Cellular Automata Emergence — Universe Types", fontsize=14)
    plt.tight_layout()
    plt.savefig("ca_emergence_results.png", dpi=150, bbox_inches='tight')
    plt.show()


if __name__ == "__main__":
    visualize_ca_examples()
