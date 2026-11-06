import csv
from pathlib import Path

import pytest
from statsmodels.stats.proportion import proportion_confint

from scripts.stats import intervals_overlap, wilson_ci

RESULTS = Path(__file__).resolve().parents[1] / "results"


def read_rows(name):
    with (RESULTS / name).open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


@pytest.mark.parametrize("x,n", [(0, 100), (5, 100), (50, 100), (100, 100), (2834, 359815), (1, 3)])
def test_wilson_matches_statsmodels(x, n):
    lo, hi = wilson_ci(x, n)
    s_lo, s_hi = proportion_confint(x, n, alpha=0.05, method="wilson")
    assert lo == pytest.approx(s_lo, abs=1e-3)  # statsmodels uses z=1.959964
    assert hi == pytest.approx(s_hi, abs=1e-3)


def test_wilson_bad_input():
    with pytest.raises(ValueError):
        wilson_ci(1, 0)
    with pytest.raises(ValueError):
        wilson_ci(5, 3)


def test_overlap():
    assert intervals_overlap((0.1, 0.2), (0.15, 0.3))
    assert not intervals_overlap((0.1, 0.2), (0.21, 0.3))


def test_sql_intervals_match_python():
    """Every Wilson interval saved by sql/22_segment_funnel.sql equals the Python result."""
    rows = read_rows("22_segment_funnel.csv")
    assert rows
    for r in rows:
        lo, hi = wilson_ci(int(r["sessions_with_purchase"]), int(r["sessions"]))
        assert float(r["sessionconv_ci_low"]) == pytest.approx(lo, abs=1e-5)
        assert float(r["sessionconv_ci_high"]) == pytest.approx(hi, abs=1e-5)
        lo, hi = wilson_ci(int(r["n_purchase"]), int(r["n_entry"]))
        assert float(r["overall_ci_low"]) == pytest.approx(lo, abs=1e-5)
        assert float(r["overall_ci_high"]) == pytest.approx(hi, abs=1e-5)


def test_funnel_counts_are_monotonic():
    rows = read_rows("20_funnel.csv")
    counts = [int(r["sessions_ordered"]) for r in rows]
    assert counts == sorted(counts, reverse=True)
