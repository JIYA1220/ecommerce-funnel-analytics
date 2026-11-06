import numpy as np
import pytest
from scipy import stats
from statsmodels.stats.power import NormalIndPower
from statsmodels.stats.proportion import (
    confint_proportions_2indep,
    proportion_effectsize,
    proportions_ztest,
)

from scripts.ab_stats import (
    bootstrap_diff_props,
    bootstrap_diff_stat,
    cap_at_quantile,
    cohens_h,
    decide,
    mde_two_proportions,
    n_per_group_for_diff,
    srm_test,
    two_prop_test,
)

CASES = [(4000, 10000, 4100, 10000), (180, 1000, 215, 1100), (50, 5000, 80, 5200), (900, 2000, 880, 2100)]


@pytest.mark.parametrize("x1,n1,x2,n2", CASES)
def test_ztest_matches_statsmodels(x1, n1, x2, n2):
    r = two_prop_test(x1, n1, x2, n2)
    z, p = proportions_ztest([x2, x1], [n2, n1])  # pooled, same as ours
    assert r["z"] == pytest.approx(z, rel=1e-9)
    assert r["p_value"] == pytest.approx(p, rel=1e-9)


@pytest.mark.parametrize("x1,n1,x2,n2", CASES)
def test_interval_matches_statsmodels_wald(x1, n1, x2, n2):
    r = two_prop_test(x1, n1, x2, n2)
    lo, hi = confint_proportions_2indep(x2, n2, x1, n1, method="wald", compare="diff")
    assert r["ci_low"] == pytest.approx(lo, abs=1e-9)
    assert r["ci_high"] == pytest.approx(hi, abs=1e-9)


@pytest.mark.parametrize("p1,p2", [(0.1, 0.12), (0.45, 0.44), (0.9, 0.5)])
def test_cohens_h_matches_statsmodels(p1, p2):
    assert cohens_h(p1, p2) == pytest.approx(proportion_effectsize(p2, p1))


def test_srm_matches_scipy():
    chi2, p = srm_test(4500, 5500)
    ref = stats.chisquare([4500, 5500], f_exp=[5000, 5000])
    assert chi2 == pytest.approx(ref.statistic) and p == pytest.approx(ref.pvalue)
    assert srm_test(5000, 5000)[1] == pytest.approx(1.0)


def test_srm_bad_input():
    with pytest.raises(ValueError):
        srm_test(0, 0)
    with pytest.raises(ValueError):
        srm_test(1, 1, expected=(0.6, 0.6))


def test_bootstrap_props_agrees_with_analytic_and_is_reproducible():
    x1, n1, x2, n2 = 4400, 10000, 4550, 10000
    r = two_prop_test(x1, n1, x2, n2)
    lo, hi = bootstrap_diff_props(x1, n1, x2, n2, n_boot=20_000, seed=1)
    assert lo == pytest.approx(r["ci_low"], abs=0.002)
    assert hi == pytest.approx(r["ci_high"], abs=0.002)
    assert bootstrap_diff_props(x1, n1, x2, n2, n_boot=500, seed=7) == bootstrap_diff_props(
        x1, n1, x2, n2, n_boot=500, seed=7)


def test_bootstrap_mean_matches_t_interval():
    rng = np.random.default_rng(3)
    a, b = rng.normal(50, 10, 3000), rng.normal(51, 10, 3000)
    lo, hi = bootstrap_diff_stat(a, b, np.mean, n_boot=2000, seed=5)
    se = np.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))
    d = b.mean() - a.mean()
    assert lo == pytest.approx(d - 1.96 * se, abs=0.1)
    assert hi == pytest.approx(d + 1.96 * se, abs=0.1)


def test_cap_at_quantile():
    v = np.array([1.0] * 999 + [1000.0])
    capped, cap = cap_at_quantile(v, 0.99)
    assert cap == 1.0 and capped.max() == 1.0 and v.max() == 1000.0


def test_mde_gives_requested_power():
    p0, n1, n2 = 0.19, 45000, 45000
    mde = mde_two_proportions(p0, n1, n2)
    h = proportion_effectsize(p0 + mde, p0)
    assert NormalIndPower().power(effect_size=h, nobs1=n1, alpha=0.05, ratio=1.0) == pytest.approx(0.8, abs=1e-3)
    # more players, smaller detectable effect
    assert mde_two_proportions(p0, 90000, 90000) < mde


def test_sample_size_inverts_mde():
    n = n_per_group_for_diff(0.19, 0.01)
    assert mde_two_proportions(0.19, n, n) <= 0.01 + 1e-4
    assert n_per_group_for_diff(0.19, 0.02) < n


def test_decision_rule():
    assert decide(0.002, 0.012, False, 0.005) == "ship"
    assert decide(0.002, 0.012, True, 0.005) == "do not ship"
    assert decide(-0.012, -0.002, False, 0.005) == "do not ship"
    assert decide(-0.004, 0.006, False, 0.005).startswith("no evidence")
    assert decide(-0.004, 0.006, False, 0.02) == "run longer"
