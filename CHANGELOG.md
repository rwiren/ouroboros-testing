# Changelog

## [0.4.0] - 2026-06-24

### Added
- **`src/fitness.py`** — `FitnessFunction` protocol (typing.Protocol); `gaussian_fitness` (geometric mean of Gaussians, default); legacy `complexity_fitness` kept for backward compatibility
- **`src/analysis.py`** — `multi_run_analysis` (N-seed statistical aggregation: mean ± std of final fitness, convergence generation, distance to target); `sensitivity_analysis` (OFAT parameter sweeps); matching visualisation functions; CLI (`python src/analysis.py --mode multi-run|sensitivity`)
- **`tests/`** — 72 pytest tests covering all pure functions: `test_fitness.py`, `test_evolution.py`, `test_complexity.py`, `test_speciation.py`
- **`configs/default.yaml`** — version-controlled canonical hyperparameter configuration
- **`pyproject.toml`** + **`requirements.txt`** — proper package metadata and dependency pinning
- **`.github/workflows/ci.yml`** — GitHub Actions CI: runs pytest on Python 3.10/3.11/3.12 + smoke test on every push/PR
- **`docs/methods.md`** — formal methods description (population representation, fitness derivation, selection, mutation, statistical protocol, limitations)
- **`references.bib`** — BibTeX bibliography for all cited papers

### Changed
- **`src/evolution.py`** — refactored `run_evolution` into testable units: `initialize_population`, `evaluate_population`, `select_elite`, `reproduce`; all random operations accept `rng=np.random.default_rng(seed)`; default fitness function switched from linear proxy to `gaussian_fitness`; `print()` replaced with `logging`; `visualize_evolution` accepts an `output_path` parameter; CLI supports `--config`, `--seed`, `--fitness`, `--log-level`, and timestamped output directories
- **`src/complexity.py`** — `run_ca` and `ca_fitness` accept `rng` and `steps` parameters for reproducibility and speed control
- **`src/speciation.py`** — `run_speciation` accepts `seed` parameter; module docstring explicitly labels Silicon/Plasma peaks as hypothetical toy configurations
- **`README.md`** — added ⚠️ Limitations section; updated Project Structure; updated Quick Start with `--config` and multi-run examples

### Fixed
- Single-run results were non-reproducible (global NumPy RNG); now every stochastic call is routed through a seeded `np.random.default_rng`

---

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

---

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

---

## [0.1.0] - 2026-06-17

### Added
- Initial framework: cosmological genetic algorithm
- Universe model with 6 normalized physical constants
- Complexity fitness function (anthropic constraints)
- Mutation/selection/reproduction loop
- CLI script: `python src/evolution.py --generations 100 --population 50`
- Visualization: fitness convergence, distance to our universe, constant comparison
- README with full hypothesis documentation and academic references
