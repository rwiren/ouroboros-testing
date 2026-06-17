# Ouroboros Testing

[![Version](https://img.shields.io/badge/Version-v0.1.0-yellow.svg)](CHANGELOG.md)
[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/rwiren/ouroboros-testing/blob/main/notebooks/ouroboros_simulation.ipynb)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Last Updated](https://img.shields.io/badge/Last%20Updated-2026--06--17-orange.svg)](#)

Exploring the **Ouroboros Singularity Hypothesis** through simulation — can universes evolve intelligence that seeds new universes, forming a closed cosmic loop?

## The Hypothesis

```
Universe₁ → Intelligence₁ → Compression → Big Bang₂ → Universe₂ → Intelligence₂ → ...
     ↑                                                                              │
     └──────────────────────── The Ouroboros Loop ──────────────────────────────────┘
```

A technological singularity doesn't expand forever — it collapses into a point of pure information that triggers a new Big Bang. The physical constants of each new universe are "written" by the intelligence of the previous cycle.

## What We're Simulating

### Cosmological Genetic Algorithm

Each "universe" is defined by a set of physical constants. We simulate whether complexity/intelligence emerges, then allow successful universes to "reproduce" with mutated constants.

**Key question:** Does the evolutionary process converge toward constants that resemble our universe?

### Phases

| Phase | Simulation |
|-------|-----------|
| 1. Linear Ascent | Complexity emergence from initial constants |
| 2. Cosmic Ingestion | Intelligence growth rate in the universe |
| 3. Microscopic Collapse | Information compression to seed |
| 4. The Tail-Bite | New universe spawned with mutated constants |

## Theoretical Foundation

| Concept | Author | Role in Simulation |
|---------|--------|-------------------|
| Conformal Cyclic Cosmology | Roger Penrose | Universe iteration model |
| Cosmological Natural Selection | Lee Smolin | Fitness function for universes |
| Fine-Tuning Problem | Various | Why simulate — does evolution explain fine-tuning? |
| "It from Bit" | John A. Wheeler | Information ↔ physics equivalence |
| Simulation Hypothesis | Nick Bostrom | Meta-layer: are we in a loop? |

## Project Structure

```
├── src/
│   ├── universe.py          ← Universe class (constants + physics rules)
│   ├── intelligence.py      ← Complexity/intelligence emergence model
│   ├── evolution.py         ← Genetic algorithm (selection, mutation, reproduction)
│   └── visualize.py         ← Visualization of evolutionary landscape
├── notebooks/
│   └── ouroboros_sim.ipynb  ← Interactive simulation notebook
├── outputs/
│   └── generations/         ← Saved evolution runs
└── docs/
    └── hypothesis.md        ← Full theoretical writeup
```

## Quick Start

```bash
pip install numpy matplotlib
python src/evolution.py --generations 100 --population 50
```

## Status

- [x] Hypothesis documented
- [ ] Universe model (parameterized physical constants)
- [ ] Complexity fitness function
- [ ] Genetic algorithm loop
- [ ] Visualization (constant landscape + convergence)
- [ ] Analysis: does it converge to our universe?

## References

- Penrose, R. (2010). *Cycles of Time: An Extraordinary New View of the Universe*
- Smolin, L. (1992). "Did the Universe Evolve?" *Classical and Quantum Gravity*
- Wheeler, J.A. (1990). "Information, Physics, Quantum: The Search for Links"
- Bostrom, N. (2003). "Are You Living in a Computer Simulation?"
