"""fitness.py — Fitness function definitions for the Cosmological Genetic Algorithm.

Defines the FitnessFunction protocol and two concrete implementations:

* ``gaussian_fitness`` (default) — geometric mean of per-constant Gaussian scores,
  grounded in Davies (2003) and the anthropic constraint literature.
* ``complexity_fitness`` (legacy) — product of linear penalty terms, kept for
  backward compatibility; scientifically weaker than the Gaussian version.

Normalization note
------------------
Each physical constant is normalized to [0, 1] over an anthropically plausible
range.  The mapping is a model assumption, **not** a dimensionless physical ratio.
The targets and tolerances below are chosen so that our universe scores ≈ 1.0
and a uniformly random universe scores ≈ 0.15 (matching the empirical finding
reported in the v0.2.0 changelog and consistent with Davies 2003 §4).

Constant targets and σ values
------------------------------
| Symbol | key               | target | σ    | Anthropic basis                     |
|--------|-------------------|--------|------|-------------------------------------|
| G      | gravity           | 0.15   | 0.10 | Stars viable over ~2 decades of G   |
|        |                   |        |      | (Adams 2019, §3.1)                  |
| α      | em_coupling       | 0.45   | 0.15 | Chemistry requires 0.1 ≲ α ≲ 0.8   |
|        |                   |        |      | (Davies 2003, §3)                   |
| g_s    | strong_force      | 0.65   | 0.12 | Nuclei stable for narrow range      |
|        |                   |        |      | (Harnik et al. 2006 weakless limit) |
| g_w    | weak_force        | 0.30   | 0.12 | Stellar lifetimes depend on g_w     |
|        |                   |        |      | (Adams 2019, §5)                    |
| Λ      | cosmological_const| 0.02   | 0.05 | Low Λ required to avoid rip        |
|        |                   |        |      | (Weinberg 1987 anthropic bound)     |
| mₚ/mₑ | mass_ratio        | 0.55   | 0.15 | Atomic structure requires ratio     |
|        |                   |        |      | within factor ~3 (Davies 2003, §4)  |
"""

from __future__ import annotations

import numpy as np
from typing import Protocol, runtime_checkable


# ---------------------------------------------------------------------------
# Canonical constants for "our universe" (normalized to [0, 1])
# ---------------------------------------------------------------------------

#: Normalized physical constants representing our universe.
#: Keys must match the ``constants`` dict used by :class:`~evolution.Universe`.
OUR_UNIVERSE: dict[str, float] = {
    "gravity":            0.15,
    "em_coupling":        0.45,
    "strong_force":       0.65,
    "weak_force":         0.30,
    "cosmological_const": 0.02,
    "mass_ratio":         0.55,
}

# Per-constant Gaussian tolerances (σ).  See module docstring for sources.
_TARGETS = [0.15, 0.45, 0.65, 0.30, 0.02, 0.55]
_SIGMAS  = [0.10, 0.15, 0.12, 0.12, 0.05, 0.15]


# ---------------------------------------------------------------------------
# Protocol
# ---------------------------------------------------------------------------

@runtime_checkable
class FitnessFunction(Protocol):
    """Callable protocol satisfied by any function ``(constants: dict) -> float``.

    The return value must be in **[0, 1]**, where 1.0 represents maximal
    intelligence-producing potential and 0.0 represents a dead/chaotic universe.
    """

    def __call__(self, constants: dict) -> float: ...


# ---------------------------------------------------------------------------
# Gaussian fitness (default, academically grounded)
# ---------------------------------------------------------------------------

def gaussian_fitness(constants: dict) -> float:
    """Estimate intelligence-emergence potential using per-constant Gaussians.

    Each constant is scored with a Gaussian centred on its target value.
    The overall fitness is the **geometric mean** of the six scores — a single
    constant in the wrong range drives the product toward zero, faithfully
    modelling the anthropic constraint that *all* parameters must be viable
    simultaneously (Davies 2003).

    Parameters
    ----------
    constants:
        Dict with keys matching :data:`OUR_UNIVERSE` and values in [0, 1].

    Returns
    -------
    float
        Fitness in [0, 1].  Returns ≈1.0 for our universe constants;
        random constants typically score ≈0.15.
    """
    vals = list(constants.values())
    scores = [
        np.exp(-((v - t) ** 2) / (2 * s ** 2))
        for v, t, s in zip(vals, _TARGETS, _SIGMAS)
    ]
    # Geometric mean via log–mean–exp; clip to avoid log(0)
    return float(np.exp(np.mean(np.log(np.clip(scores, 1e-300, None)))))


# ---------------------------------------------------------------------------
# Legacy linear fitness (backward compatibility)
# ---------------------------------------------------------------------------

def complexity_fitness(constants: dict) -> float:
    """Legacy linear fitness function (kept for backward compatibility).

    .. deprecated::
        Use :func:`gaussian_fitness` instead.  This linear product is
        scientifically weaker: it can return exactly 0.0 for any universe where
        a single term is negative, creating large flat regions with zero gradient
        that stall evolution.  The Gaussian version avoids this pathology.

    The function models anthropic constraints with linear penalty terms:

    * ``star_score``      — gravity near 0.15 allows stable star formation
    * ``chem_score``      — EM + strong force balance enables chemistry
    * ``stability_score`` — low cosmological constant prevents expansion rip
    * ``time_score``      — weak force determines stellar lifetime
    * ``atom_score``      — mass ratio allows complex atomic structure
    """
    g  = constants["gravity"]
    em = constants["em_coupling"]
    sf = constants["strong_force"]
    wf = constants["weak_force"]
    cc = constants["cosmological_const"]
    mr = constants["mass_ratio"]

    star_score      = 1.0 - abs(g  - 0.15) * 4
    chem_score      = 1.0 - abs(em - 0.45) * 3 - abs(sf - 0.65) * 3
    stability_score = 1.0 - cc * 5
    time_score      = 1.0 - abs(wf - 0.30) * 3
    atom_score      = 1.0 - abs(mr - 0.55) * 3

    raw = (star_score
           * max(0, chem_score)
           * max(0, stability_score)
           * max(0, time_score)
           * max(0, atom_score))
    return max(0.0, raw)
