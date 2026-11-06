"""Write results/dashboard_expected_values.csv: the numbers the Power BI dashboard should show.

Usage (PowerShell): python -m scripts.expected_values

Every value is read or derived (sums and ratios) from files in results/. The source column names them.
"""

from __future__ import annotations

import csv
from pathlib import Path

from scripts.export_powerbi import read_csv
from scripts.stats import wilson_ci

OUT = Path("results/dashboard_expected_values.csv")


def weighted_retention(rows: list[dict], week_n: int) -> tuple[int, int]:
    """(retained, cohort size) summed over observable, non-partial cohorts at week N."""
    keep = [r for r in rows if int(r["week_n"]) == week_n and r["observable"] == "True"
            and r["cohort_week_is_partial"] == "False"]
    return sum(int(r["retained_users"]) for r in keep), sum(int(r["cohort_size"]) for r in keep)


def build() -> list[dict]:
    out: list[dict] = []

    def add(metric, value, source):
        out.append({"metric": metric, "value": value, "source": source})

    f = read_csv("20_funnel.csv")
    total = int(f[0]["all_valid_sessions"])
    swp = int(read_csv("21b_purchase_sessions_missing_steps.csv")[0]["sessions_with_purchase"])
    add("Sessions", total, "20_funnel.csv")
    add("Sessions with purchase", swp, "21b_purchase_sessions_missing_steps.csv")
    add("Session conversion rate", round(swp / total, 5), "derived: sessions with purchase / sessions")
    lo, hi = wilson_ci(swp, total)
    add("Session conversion Wilson low", round(lo, 5), "derived (Wilson 95%)")
    add("Session conversion Wilson high", round(hi, 5), "derived (Wilson 95%)")

    r = next(x for x in read_csv("26_revenue_by_segment.csv") if x["dimension"] == "all")
    add("Purchases", int(r["purchases"]), "26_revenue_by_segment.csv")
    add("Revenue", float(r["revenue"]), "26_revenue_by_segment.csv")
    add("AOV", float(r["aov"]), "26_revenue_by_segment.csv")
    add("Users", int(r["users"]), "26_revenue_by_segment.csv")
    add("Revenue per user", float(r["revenue_per_user"]), "26_revenue_by_segment.csv")

    for row in f:
        add(f"Funnel step {row['step_no']} sessions", int(row["sessions_ordered"]), "20_funnel.csv")
        if row["step_to_step_conversion"]:
            add(f"Funnel step {row['step_no']} step conversion", float(row["step_to_step_conversion"]),
                "20_funnel.csv")
            add(f"Funnel step {row['step_no']} drop-off", float(row["dropoff_share"]), "20_funnel.csv")
    add("Overall funnel conversion", float(f[-1]["conversion_from_entry"]), "20_funnel.csv")

    for seg in ("new", "returning"):
        s = next(x for x in read_csv("22_segment_funnel.csv")
                 if x["dimension"] == "visitor_type" and x["segment"] == seg)
        add(f"Session conversion, {seg}", float(s["session_conversion_rate"]), "22_segment_funnel.csv")

    ret = read_csv("24_retention_long.csv")
    for n in (1, 2, 4):
        x, d = weighted_retention(ret, n)
        add(f"Retention week {n} (all full cohorts, weighted)", round(x / d, 4),
            f"derived from 24_retention_long.csv: {x} / {d}")

    p = read_csv("31_product_table.csv")[0]
    add("Top product by revenue", p["item_name"], "31_product_table.csv")
    add("Top product item revenue", float(p["item_revenue"]), "31_product_table.csv")
    return out


def main() -> int:
    rows = build()
    with OUT.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["metric", "value", "source"])
        w.writeheader()
        w.writerows(rows)
    print(f"Wrote {len(rows)} values to {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
