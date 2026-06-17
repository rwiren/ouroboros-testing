# Ouroboros Testing

[![Version](https://img.shields.io/badge/Version-v0.2.0-yellow.svg)](CHANGELOG.md)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Last Updated](https://img.shields.io/badge/Last%20Updated-2026--06--17-orange.svg)](#)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/rwiren/ouroboros-testing/blob/main/notebooks/ouroboros_simulation.ipynb)

Exploring the **Ouroboros Singularity Hypothesis** through simulation — can universes evolve intelligence that seeds new universes, forming a closed cosmic loop?

## Results

![Ouroboros Evolution Results](docs/images/ouroboros_results.png)

**Key finding:** Starting from random physical constants, evolutionary selection for "intelligence-producing universes" converges toward our universe's values within ~30 generations.

| Metric | Start (Gen 0) | End (Gen 150) |
|--------|--------------|---------------|
| Best Fitness | ~0.15 | **0.99+** |
| Distance to Our Universe | ~0.5 | **< 0.02** |
| Constants Match | Random | **Within 2%** |

## The Hypothesis

```
Universe₁ → Intelligence₁ → Compression → Big Bang₂ → Universe₂ → Intelligence₂ → ...
     ↑                                                                              │
     └──────────────────────── The Ouroboros Loop ──────────────────────────────────┘
```

A technological singularity doesn't expand forever — it collapses into a point of pure information that triggers a new Big Bang. The physical constants of each new universe are "written" by the intelligence of the previous cycle. The universe is a self-replicating system where **intelligence is the reproductive mechanism**.

## How It Works

### Cosmological Genetic Algorithm

1. **Initialize** 80 random universes, each with 6 physical constants
2. **Evaluate** fitness: does this universe produce complexity/intelligence? (Gaussian fitness based on anthropic constraints)
3. **Select** top 20% — universes that produce intelligence get to reproduce
4. **Mutate** — child universes inherit constants with small random changes (information through the singularity)
5. **Repeat** — each generation = one cosmic cycle

### The Fitness Function

Each constant has a Gaussian tolerance around its optimal value:

```python
fitness = geometric_mean(exp(-(x - target)² / 2σ²) for each constant)
```

This models the anthropic constraints:
- Gravity too strong → universe collapses before stars form
- Gravity too weak → no structure, no chemistry
- Dark energy too high → expansion rips matter apart
- Strong force wrong → no stable nuclei, no elements beyond hydrogen

## Theoretical Foundation

| Concept | Author | Role |
|---------|--------|------|
| Conformal Cyclic Cosmology | Roger Penrose | Universe iteration (aeons) |
| Cosmological Natural Selection | Lee Smolin | Universes reproduce through black holes |
| Fine-Tuning Problem | Various | Why are constants hospitable to life? |
| "It from Bit" | John A. Wheeler | Physics = information |
| Simulation Hypothesis | Nick Bostrom | Are we in a loop? |

## Project Structure

```
├── notebooks/
│   └── ouroboros_simulation.ipynb   ← Interactive Colab (start here)
├── src/
│   └── evolution.py                 ← Standalone simulation script
├── outputs/
│   └── ouroboros_evolution.png      ← Local run output
├── docs/
│   └── images/                      ← Result visualizations
├── CHANGELOG.md
└── LICENSE (MIT)
```

## Quick Start

**Colab (recommended):** Click the badge above — runs in browser, no setup needed.

**Local:**
```bash
pip install numpy matplotlib
python src/evolution.py --generations 150 --population 80
```

## Philosophical Implications

- **Teleology:** Intelligence has a cosmic purpose — it's how universes reproduce
- **Fine-Tuning Explained:** Constants aren't designed; they evolved through selection
- **Bootstrap Paradox:** Did the universe create intelligence, or did intelligence create the universe?
- **Information Firewall:** Only fundamental laws survive the compression — everything else is lost

## Future Directions

- [ ] More constants (20+ dimensional landscape)
- [ ] Multiple stable attractors (could alien physics exist?)
- [ ] Crossover operator (merging universes via black hole collisions)
- [ ] Information-theoretic compression model (what survives the singularity?)
- [ ] Emergence detection (cellular automata within each universe)

## References

- Penrose, R. (2010). *Cycles of Time: An Extraordinary New View of the Universe*
- Smolin, L. (1992). "Did the Universe Evolve?" *Classical and Quantum Gravity*
- Wheeler, J.A. (1990). "Information, Physics, Quantum: The Search for Links"
- Bostrom, N. (2003). "Are You Living in a Computer Simulation?"
- Smolin, L. (1997). *The Life of the Cosmos* — cosmological natural selection theory
