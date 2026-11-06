"""Check the Power BI CSVs against the saved query results (they must agree exactly)."""

import csv
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def rows(rel):
    with (ROOT / rel).open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def test_daily_totals_match_results():
    d = rows("powerbi/daily_kpis.csv")
    assert len(d) == 92
    sessions_total = int(rows("results/20_funnel.csv")[0]["all_valid_sessions"])
    assert sum(int(r["sessions"]) for r in d) == sessions_total
    assert sum(int(r["new_sessions"]) + int(r["returning_sessions"]) for r in d) == sessions_total
    assert sum(int(r["sessions_with_purchase"]) for r in d) == int(
        rows("results/21b_purchase_sessions_missing_steps.csv")[0]["sessions_with_purchase"])
    all_row = next(r for r in rows("results/26_revenue_by_segment.csv") if r["dimension"] == "all")
    assert sum(int(r["purchases"]) for r in d) == int(all_row["purchases"])
    assert sum(float(r["revenue"]) for r in d) == pytest.approx(float(all_row["revenue"]))


def test_every_dimension_sums_to_the_same_totals():
    k = rows("powerbi/segment_kpis.csv")
    all_row = next(r for r in k if r["dimension"] == "all")
    for dim in {r["dimension"] for r in k}:
        part = [r for r in k if r["dimension"] == dim]
        assert sum(int(r["sessions"]) for r in part) == int(all_row["sessions"]), dim
        assert sum(int(r["purchases"]) for r in part) == int(all_row["purchases"]), dim
        assert sum(float(r["revenue"]) for r in part) == pytest.approx(float(all_row["revenue"])), dim
        assert sum(int(r["sessions_with_purchase"]) for r in part) == int(
            all_row["sessions_with_purchase"]), dim


def test_funnel_long_matches_funnel_results():
    f = rows("powerbi/funnel_by_segment.csv")
    res = {int(r["step_no"]): int(r["sessions_ordered"]) for r in rows("results/20_funnel.csv")}
    for r in f:
        if r["dimension"] == "all":
            assert int(r["sessions"]) == res[int(r["step_no"])]
    # each dimension's entry step sums to the all-sessions entry step
    for dim in {r["dimension"] for r in f}:
        entry = sum(int(r["sessions"]) for r in f if r["dimension"] == dim and r["step_no"] == "1")
        assert entry == res[1], dim


def test_dim_tables_have_unique_keys_and_match_facts():
    dim = rows("powerbi/dim_segment.csv")
    keys = [r["segment_key"] for r in dim]
    assert len(keys) == len(set(keys))
    for rel in ("powerbi/funnel_by_segment.csv", "powerbi/segment_kpis.csv"):
        assert {r["segment_key"] for r in rows(rel)} <= set(keys)
    steps = {r["step_no"] for r in rows("powerbi/dim_step.csv")}
    assert {r["step_no"] for r in rows("powerbi/funnel_by_segment.csv")} <= steps


def test_cohort_sizes_sum_to_users():
    ret = rows("powerbi/cohort_retention.csv")
    users = int(rows("results/01_profile_overview.csv")[0]["users"])
    assert sum(int(r["cohort_size"]) for r in ret if r["week_n"] == "0") == users
    for r in ret:
        if r["observable"] == "False":
            assert r["retention"] == "" and r["retained_users"] == ""


def test_product_revenue_matches_top_products_total():
    p = rows("powerbi/products.csv")
    total = float(rows("results/27_top_products_categories.csv")[0]["total_item_revenue"])
    assert sum(float(r["item_revenue"]) for r in p) == pytest.approx(total)
    names = [r["item_name"] for r in p]
    assert len(names) == len(set(names))
