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
