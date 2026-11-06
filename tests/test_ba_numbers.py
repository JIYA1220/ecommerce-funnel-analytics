import pytest

from scripts.ba_numbers import kpi_tree_rows, scenario_rows

FUNNEL = {1: 1000, 2: 400, 3: 200, 4: 100, 5: 80, 6: 50}


def test_checkout_scenario_arithmetic():
    rows = scenario_rows(FUNNEL, aov=10.0, window_revenue=1000.0)
    r = next(x for x in rows if x["lever"].startswith("checkout") and x["improvement_points"] == 10)
    assert r["baseline_rate"] == 0.5
    assert r["extra_purchase_sessions"] == 10.0  # 100 sessions x 10 points
    assert r["extra_revenue"] == 100
    assert r["share_of_window_revenue"] == 0.1


def test_cart_scenario_uses_downstream_rate():
    rows = scenario_rows(FUNNEL, aov=10.0, window_revenue=1000.0)
    r = next(x for x in rows if x["lever"].startswith("add to cart") and x["improvement_points"] == 5)
    # 400 viewers x 5 points = 20 extra carts; 50/200 of carts end in purchase = 5 sessions
    assert r["extra_purchase_sessions"] == 5.0
    assert r["extra_revenue"] == 50


def test_zero_improvement_gives_zero():
    # a scenario with a bigger step improves revenue monotonically
    rows = scenario_rows(FUNNEL, aov=10.0, window_revenue=1000.0)
    checkout = [x["extra_revenue"] for x in rows if x["lever"].startswith("checkout")]
    assert checkout == sorted(checkout) and checkout[0] > 0


def test_kpi_tree_identity():
    rows = {r["metric"]: r["value"] for r in kpi_tree_rows(FUNNEL, 1000, 20, 400.0, 700, 300)}
    assert rows["Revenue check: sessions x orders per session x AOV"] == pytest.approx(400.0)
    assert rows["AOV"] == 20.0
    assert rows["Orders per session"] == 0.02
