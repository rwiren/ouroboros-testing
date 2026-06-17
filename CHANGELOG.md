# Changelog

## [0.2.0] - 2026-06-17

### Added
- **Colab notebook** with interactive visualizations and animation
- Gaussian fitness function (smooth gradient, non-zero for all universes)
- Fitness landscape plots per constant (showing viable range)
- Animated evolution (watch constants converge in real-time)
- Ouroboros cycle diagram (4-phase visualization)
- Results image in README showing convergence proof

### Fixed
- Fitness function was too strict (product of linear scores → always zero)
- Now uses geometric mean of Gaussians — random universes score ~0.15, ours scores 1.0

## [0.1.0] - 2026-06-17

### Added
- Initial framework: cosmological genetic algorithm
- Universe model with 6 normalized physical constants
- Complexity fitness function (anthropic constraints)
- Mutation/selection/reproduction loop
- CLI script: `python src/evolution.py --generations 100 --population 50`
- Visualization: fitness convergence, distance to our universe, constant comparison
- README with full hypothesis documentation and academic references

## [0.3.0] - 2026-06-17

### Added
- **Speciation engine** (`src/speciation.py`) — niched GA with fitness sharing, discovers 3 viable physics islands (our universe, silicon universe, plasma universe)
- **Cellular automata complexity** (`src/complexity.py`) — replaces Gaussian proxy with actual emergence measurement (Shannon entropy + LZW compression + activity)
- **Colab notebook extensions** — speciation PCA visualization + CA emergence demo + GA with CA fitness
- Three universe types visualized: dead, chaotic, complex (edge of chaos)
- Evolution with actual measured complexity (no proxy fitness)

### Key Results
- Speciation: population splits into 3 distinct clusters in PCA space
- CA fitness: "our" constants produce edge-of-chaos dynamics (sustained activity, moderate entropy)
- Dead universes (high Λ): zero activity after 5 steps
- Chaotic universes: high entropy but no structure (random noise)
