"""Statistics for the A/B test, kept separate so they can be tested against scipy and statsmodels.

Convention: group 1 is control (gate_30), group 2 is treatment (gate_40).
The effect is always treatment minus control.
"""

from __future__ import annotations

import math

import numpy as np
from scipy import stats
from statsmodels.stats.power import NormalIndPower


def srm_test(n1: int, n2: int, expected: tuple[float, float] = (0.5, 0.5)) -> tuple[float, float]:
    """Sample ratio mismatch: chi-square test of the group sizes against the expected split."""
    if n1 < 0 or n2 < 0 or n1 + n2 == 0:
        raise ValueError("group sizes must be non-negative and not both zero")
    if abs(sum(expected) - 1) > 1e-9:
        raise ValueError("expected shares must sum to 1")
    total = n1 + n2
    chi2, p = stats.chisquare([n1, n2], f_exp=[total * expected[0], total * expected[1]])
    return float(chi2), float(p)


def two_prop_test(x1: int, n1: int, x2: int, n2: int, alpha: float = 0.05) -> dict:
    """Two-proportion z-test. Pooled standard error for z and p, unpooled for the interval."""
    if min(n1, n2) <= 0 or not (0 <= x1 <= n1 and 0 <= x2 <= n2):
        raise ValueError("invalid counts")
    p1, p2 = x1 / n1, x2 / n2
    diff = p2 - p1
    p_pool = (x1 + x2) / (n1 + n2)
    se_pool = math.sqrt(p_pool * (1 - p_pool) * (1 / n1 + 1 / n2))
    z = diff / se_pool if se_pool > 0 else 0.0
    p_value = float(2 * stats.norm.sf(abs(z)))
    se = math.sqrt(p1 * (1 - p1) / n1 + p2 * (1 - p2) / n2)
    zc = float(stats.norm.ppf(1 - alpha / 2))
    return {
        "p_control": p1, "p_treatment": p2, "diff": diff,
        "relative_lift": diff / p1 if p1 > 0 else float("nan"),
        "z": z, "p_value": p_value,
        "ci_low": diff - zc * se, "ci_high": diff + zc * se,
        "cohens_h": cohens_h(p1, p2),
    }


def cohens_h(p1: float, p2: float) -> float:
    """Cohen's h for two proportions (treatment minus control)."""
    return 2 * math.asin(math.sqrt(p2)) - 2 * math.asin(math.sqrt(p1))


def bootstrap_diff_props(x1: int, n1: int, x2: int, n2: int, n_boot: int = 10_000,
                         seed: int = 20240601, alpha: float = 0.05) -> tuple[float, float]:
    """Percentile bootstrap interval for p2 - p1.

    For a yes/no outcome, resampling players with replacement gives a Binomial(n, p_hat) count,
    so the resample is drawn directly. This is the same bootstrap, much faster.
    """
    rng = np.random.default_rng(seed)
    b1 = rng.binomial(n1, x1 / n1, n_boot) / n1
    b2 = rng.binomial(n2, x2 / n2, n_boot) / n2
    d = b2 - b1
    lo, hi = np.quantile(d, [alpha / 2, 1 - alpha / 2])
    return float(lo), float(hi)


def bootstrap_diff_stat(a: np.ndarray, b: np.ndarray, stat=np.mean, n_boot: int = 2_000,
                        seed: int = 20240601, alpha: float = 0.05) -> tuple[float, float]:
    """Percentile bootstrap interval for stat(b) - stat(a), resampling players with replacement."""
    rng = np.random.default_rng(seed)
    a, b = np.asarray(a), np.asarray(b)
    d = np.empty(n_boot)
    for i in range(n_boot):
        d[i] = stat(b[rng.integers(0, len(b), len(b))]) - stat(a[rng.integers(0, len(a), len(a))])
    lo, hi = np.quantile(d, [alpha / 2, 1 - alpha / 2])
    return float(lo), float(hi)


def cap_at_quantile(values: np.ndarray, q: float = 0.999) -> tuple[np.ndarray, float]:
    """Cap values at the q-quantile. Returns the capped array and the cap."""
    cap = float(np.quantile(values, q))
    return np.minimum(values, cap), cap


def mde_two_proportions(p_base: float, n1: int, n2: int, alpha: float = 0.05,
                        power: float = 0.8) -> float:
    """Smallest increase over p_base that the test detects with the given power (two-sided)."""
    h = NormalIndPower().solve_power(effect_size=None, nobs1=n1, alpha=alpha, power=power,
                                     ratio=n2 / n1, alternative="two-sided")
    p2 = math.sin(math.asin(math.sqrt(p_base)) + h / 2) ** 2
    return p2 - p_base


def n_per_group_for_diff(p_base: float, diff: float, alpha: float = 0.05, power: float = 0.8) -> int:
    """Players needed per group (equal groups) to detect an increase of diff over p_base."""
    h = 2 * math.asin(math.sqrt(p_base + diff)) - 2 * math.asin(math.sqrt(p_base))
    n = NormalIndPower().solve_power(effect_size=h, nobs1=None, alpha=alpha, power=power,
                                     ratio=1.0, alternative="two-sided")
    return math.ceil(n)


def decide(ci_low: float, ci_high: float, guardrail_failed: bool, mde: float,
           threshold: float = 0.01) -> str:
    """Decision rule from ab_test/DESIGN.md, fixed before the data was seen."""
    if guardrail_failed or ci_high < 0:
        return "do not ship"
    if ci_low > 0:
        return "ship"
    return "no evidence of a material effect, keep current gate" if mde <= threshold else "run longer"
