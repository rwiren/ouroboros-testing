# Methods: Cosmological Genetic Algorithm (CGA)

> **Version:** 0.4.0 | **Status:** Toy / proof-of-concept simulation

---

## 1. Overview

This simulation implements a **Cosmological Genetic Algorithm (CGA)** — a real-valued evolutionary algorithm (Holland 1975; Eiben & Smith 2003) in which the "chromosomes" are normalised vectors of physical constants.  The fitness landscape rewards universes whose constants simultaneously satisfy a set of anthropic constraints.

The central question: starting from uniformly random constants, does selection for intelligence-producing universes drive convergence toward our universe's known constants?

---

## 2. Population Representation

Each individual (called a "universe") is a vector **c** ∈ [0, 1]⁶ of six normalised physical constants:

| Index | Key | Physical meaning | Normalization basis |
|-------|-----|-----------------|---------------------|
| 0 | `gravity` | Gravitational coupling G | Linear over [G_min, G_max] where stars are possible (Adams 2019, §3.1) |
| 1 | `em_coupling` | Electromagnetic coupling α | Range over which chemistry is viable (Davies 2003, §3) |
| 2 | `strong_force` | Strong nuclear force g_s | Range admitting stable nuclei (Harnik et al. 2006) |
| 3 | `weak_force` | Weak nuclear force g_w | Range over which stellar lifetimes allow biological evolution (Adams 2019, §5) |
| 4 | `cosmological_const` | Dark energy Λ | Range below Weinberg's anthropic bound (Weinberg 1987) |
| 5 | `mass_ratio` | Proton/electron mass ratio m_p/m_e | Range supporting stable atomic structure (Davies 2003, §4) |

**Important caveat on normalisation:** The mapping of physical constants to [0, 1] is a simplified linear normalisation over anthropically plausible ranges.  It is a **model assumption**, not a physically derived dimensionless parameter.  The targets below are chosen so that our universe scores exactly 1.0 under the fitness function; they do not correspond to measured dimensionless ratios.

---

## 3. Fitness Function

### 3.1 Gaussian Fitness (Default, `src/fitness.py`)

Each constant is evaluated against a target value *t_i* with tolerance *σ_i*:

$$f_i(c_i) = \exp\!\left(-\frac{(c_i - t_i)^2}{2\sigma_i^2}\right)$$

The overall fitness is the **geometric mean** of the six per-constant scores:

$$F(\mathbf{c}) = \exp\!\left(\frac{1}{6}\sum_{i=1}^{6} \ln f_i(c_i)\right)$$

Using the geometric mean (rather than arithmetic mean) means that a **single constant violating its constraint drives the product toward zero** — faithfully modelling the anthropic principle that all constraints must hold simultaneously (Davies 2003).

**Target values and tolerances:**

| Constant | Target *t_i* | Tolerance *σ_i* | Academic basis |
|----------|-------------|-----------------|----------------|
| Gravity | 0.15 | 0.10 | Stars viable over ~2 decades of G (Adams 2019, §3.1) |
| EM coupling | 0.45 | 0.15 | Chemistry requires 0.1 ≲ α ≲ 0.8 (Davies 2003, §3) |
| Strong force | 0.65 | 0.12 | Narrow range for stable nuclei (Harnik et al. 2006) |
| Weak force | 0.30 | 0.12 | Stellar lifetime constraints (Adams 2019, §5) |
| Cosmological Λ | 0.02 | 0.05 | Low Λ prevents vacuum-energy rip (Weinberg 1987) |
| Mass ratio | 0.55 | 0.15 | Atomic structure within factor ~3 (Davies 2003, §4) |

A uniformly random universe scores approximately **F ≈ 0.15**; our universe scores exactly **F = 1.0**.

### 3.2 CA Fitness (Optional, `src/complexity.py`)

An alternative fitness function replacing the Gaussian proxy with **measured emergence** from a 2D cellular automaton:

1. Map physical constants to CA birth/survival/decay rules.
2. Run the CA for `steps` time-steps on a 64 × 64 grid.
3. Measure complexity via:
   - **Shannon entropy** of the final state (binary distribution, max = 1 bit).
   - **Compression ratio** (zlib) of the full history — a proxy for Kolmogorov complexity.
   - **Mean activity** — fraction of cells changing per step.
   - **Lifespan** — steps until activity < 1 %.
4. Complexity score = entropy × (1 − compression) × min(1, activity × 10) × lifespan fraction.

This operationalises the "edge of chaos" criterion (Langton 1990): complex self-organising systems live at the boundary between ordered and chaotic regimes.

### 3.3 Legacy Linear Fitness (Deprecated, `src/fitness.py`)

The original `complexity_fitness` function uses a product of linear penalty terms.  It is **not recommended** for new experiments because its flat zero regions (where any single term ≤ 0) produce vanishing gradients that stall evolution.  Retained for backward compatibility only.

---

## 4. Selection

**Elitist truncation selection** (Eiben & Smith 2003, §5.4):

1. Evaluate all *N* individuals.
2. Sort by fitness (descending).
3. Retain top *k* = max(2, ⌊elite_frac × N⌋) individuals unchanged.

Default `elite_frac = 0.2` (top 20 % survive each cycle).

---

## 5. Mutation Operator

**Gaussian perturbation with per-gene probability** (Bäck et al. 1997):

Each constant *c_i* is mutated independently:

$$c_i' = \text{clip}\!\left(c_i + \mathcal{N}(0,\, \sigma_m),\; 0,\; 1\right) \quad \text{with probability } p_m = 0.3$$

Default `mutation_rate` (σ_m) = 0.08.

The 30 % per-gene mutation probability is intentionally higher than the oft-cited 1/*L* rule (L = 6 genes) to model the noisy information channel through the singularity.

---

## 6. Reproduction

New population = elite (unchanged) + (N − k) children.  Each child has one parent selected uniformly at random from the elite set.  No crossover operator is currently implemented.

---

## 7. Termination

Fixed-generation termination: the algorithm runs for `generations` cycles regardless of convergence.

---

## 8. Default Hyperparameters

| Parameter | Default | Notes |
|-----------|---------|-------|
| `population_size` | 80 | Large enough to maintain diversity |
| `generations` | 150 | Sufficient for convergence at default mutation rate |
| `mutation_rate` (σ_m) | 0.06 | See sensitivity sweep in `src/analysis.py` |
| `elite_frac` | 0.20 | 20 % survival — balances selection pressure |
| `seed` | 42 | Set explicitly for reproducibility |

See `configs/default.yaml` for the canonical defaults.

---

## 9. Statistical Analysis Protocol

A single run is **anecdotal** (Eiben & Smith 2003, §11.2).  All published metrics should be computed over **≥ 30 independent seeds** using `src/analysis.py`:

```bash
python src/analysis.py --mode multi-run --runs 30 --generations 150
```

Reported statistics:
- **Final best fitness**: mean ± std
- **Convergence generation**: first generation where best fitness > 0.9 (mean ± std)
- **Final distance to target**: Euclidean distance in [0,1]⁶ space (mean ± std)

For parameter sensitivity, use:

```bash
python src/analysis.py --mode sensitivity --param mutation_rate
```

---

## 10. Limitations

See also the Limitations section in `README.md`.

1. **Proxy fitness**: The Gaussian fitness is a mathematical convenience, not a physically derived quantity.  No physical simulation of star formation, nucleosynthesis, or biological evolution is performed.

2. **Normalisation circularity**: The target constants are chosen so that our universe scores 1.0 by construction.  Convergence toward these targets is tautological, not evidence of actual cosmological selection.

3. **Single-parent reproduction**: No crossover operator is implemented, limiting exploration of the fitness landscape.

4. **Fixed dimensionality**: The simulation uses 6 constants.  Real fine-tuning analyses consider 20+ independent parameters (Adams 2019) and the landscape may be qualitatively different at higher dimensionality.

5. **Hypothetical speciation peaks**: The "Silicon Universe" and "Plasma Universe" peaks in `speciation.py` are toy configurations chosen to create well-separated clusters.  They have no grounding in specific alternative-physics proposals.

---

## References (abbreviated)

Full BibTeX entries are in `references.bib`.

- Adams, F.C. (2019). *Physics Reports*, 807, 1–111.
- Davies, P.C.W. (2003). *International Journal of Astrobiology*, 2(2), 115–120.
- Eiben, A.E. & Smith, J.E. (2003). *Introduction to Evolutionary Computing*. Springer.
- Gardner, A. & Conlon, J.P. (2013). *Complexity*, 18(5), 48–56.
- Harnik, R., Kribs, G.D. & Perez, G. (2006). *Physical Review D*, 74, 035006.
- Le Bihan, B. (2024). *Journal for General Philosophy of Science*.
- Meissner, K.A. & Penrose, R. (2025). arXiv:2503.24263.
- Weinberg, S. (1987). *Physical Review Letters*, 59(22), 2607–2610.
