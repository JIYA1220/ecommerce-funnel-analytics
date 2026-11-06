"""Numbers for the business analyst pack, derived only from files in results/.

Usage (PowerShell): python -m scripts.ba_numbers

Writes:
  results/ba_scenarios.csv        scenario table for ba/BUSINESS_CASE.md
  results/ba_kpi_tree_values.csv  current values for ba/KPI_TREE.md

The scenarios are "what if" arithmetic, not forecasts. Assumptions are stated in the business case.
"""

from __future__ import annotations

import csv
from pathlib import Path

from scripts.export_powerbi import read_csv

RESULTS = Path("results")

CHECKOUT_POINTS = (2, 5, 10)
CART_POINTS = (1, 2, 5)


def scenario_rows(funnel: dict[int, int], aov: float, window_revenue: float) -> list[dict]:
    """Extra purchase sessions and revenue if one funnel step converts better by N percentage points.

    Assumptions (labeled in the business case): extra purchasing sessions place one order at the
    current AOV, later step conversions stay as they are, and the window is the 92 days of data.
    """
    rows = []
    n2, n3, n4, n6 = funnel[2], funnel[3], funnel[4], funnel[6]
    base_checkout = n6 / n4
    base_cart = n3 / n2
    downstream_from_cart = n6 / n3
    for pts in CHECKOUT_POINTS:
        extra = n4 * pts / 100
        rows.append({
            "lever": "checkout completion (begin_checkout to purchase)",
            "baseline_rate": round(base_checkout, 4), "improvement_points": pts,
            "sessions_at_step": n4, "extra_purchase_sessions": round(extra, 1),
            "extra_revenue": round(extra * aov), "share_of_window_revenue": round(extra * aov / window_revenue, 4),
        })
    for pts in CART_POINTS:
        extra_cart = n2 * pts / 100
        extra = extra_cart * downstream_from_cart
        rows.append({
            "lever": "add to cart rate (view_item to add_to_cart)",
            "baseline_rate": round(base_cart, 4), "improvement_points": pts,
            "sessions_at_step": n2, "extra_purchase_sessions": round(extra, 1),
            "extra_revenue": round(extra * aov), "share_of_window_revenue": round(extra * aov / window_revenue, 4),
        })
    return rows


def kpi_tree_rows(funnel: dict[int, int], sessions: int, orders: int, revenue: float,
                  new_sessions: int, returning_sessions: int) -> list[dict]:
    aov = revenue / orders
    orders_per_session = orders / sessions
    out = [
        ("Revenue (north star)", revenue),
        ("Sessions", sessions),
        ("New sessions", new_sessions),
        ("Returning sessions", returning_sessions),
        ("Orders (distinct real transaction ids)", orders),
        ("Orders per session", round(orders_per_session, 5)),
        ("AOV", round(aov, 2)),
        ("Revenue check: sessions x orders per session x AOV", round(sessions * orders_per_session * aov, 2)),
        ("Entry to view_item", round(funnel[2] / funnel[1], 4)),
        ("view_item to add_to_cart", round(funnel[3] / funnel[2], 4)),
        ("add_to_cart to begin_checkout", round(funnel[4] / funnel[3], 4)),
        ("begin_checkout to add_payment_info", round(funnel[5] / funnel[4], 4)),
        ("add_payment_info to purchase", round(funnel[6] / funnel[5], 4)),
        ("begin_checkout to purchase", round(funnel[6] / funnel[4], 4)),
        ("Overall funnel conversion (entry to purchase)", round(funnel[6] / funnel[1], 5)),
    ]
    return [{"metric": m, "value": v} for m, v in out]


def write(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def main() -> int:
    funnel = {int(r["step_no"]): int(r["sessions_ordered"]) for r in read_csv("20_funnel.csv")}
    rev = next(r for r in read_csv("26_revenue_by_segment.csv") if r["dimension"] == "all")
    orders, revenue = int(rev["purchases"]), float(rev["revenue"])
    sessions = int(rev["sessions"])
    vt = {r["segment"]: int(r["sessions"]) for r in read_csv("22_segment_funnel.csv")
          if r["dimension"] == "visitor_type"}
    aov = revenue / orders
    write(RESULTS / "ba_scenarios.csv", scenario_rows(funnel, aov, revenue))
    write(RESULTS / "ba_kpi_tree_values.csv",
          kpi_tree_rows(funnel, sessions, orders, revenue, vt["new"], vt["returning"]))
    print("Wrote results/ba_scenarios.csv and results/ba_kpi_tree_values.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
