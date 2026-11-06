"""Small statistics helpers, used to cross-check the SQL results."""

from __future__ import annotations

import math


def wilson_ci(successes: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """Wilson score interval for a proportion (same formula as the SQL in sql/22_*.sql)."""
    if n <= 0:
        raise ValueError("n must be positive")
    if not 0 <= successes <= n:
        raise ValueError("successes must be between 0 and n")
    p = successes / n
    denom = 1 + z * z / n
    centre = p + z * z / (2 * n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return (centre - half) / denom, (centre + half) / denom


def intervals_overlap(a: tuple[float, float], b: tuple[float, float]) -> bool:
    """True when two (low, high) intervals overlap."""
    return not (a[1] < b[0] or b[1] < a[0])
