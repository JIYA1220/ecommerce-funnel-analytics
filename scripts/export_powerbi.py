"""Build the small, clean CSVs for Power BI from the saved query results (no BigQuery needed).

Usage (PowerShell): python -m scripts.export_powerbi

Reads results/*.csv, writes powerbi/*.csv. Nothing is computed here beyond reshaping:
every number in the output is a number from a file in results/.
"""

from __future__ import annotations

import csv
from pathlib import Path

RESULTS = Path("results")
OUT = Path("powerbi")

STEPS = [
    (1, "entry", "n_entry"),
    (2, "view_item", "n_view_item"),
    (3, "add_to_cart", "n_add_to_cart"),
    (4, "begin_checkout", "n_begin_checkout"),
    (5, "add_payment_info", "n_add_payment_info"),
    (6, "purchase", "n_purchase"),
]


def read_csv(name: str, results: Path = RESULTS) -> list[dict]:
    with (results / name).open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def segment_key(dimension: str, segment: str) -> str:
    return f"{dimension}|{segment}"


def build_funnel_long(funnel_all: list[dict], seg_rows: list[dict]) -> list[dict]:
    """Wide segment funnel (one column per step) to long format, plus the all-sessions funnel."""
    out = []
    by_no = {int(r["step_no"]): int(r["sessions_ordered"]) for r in funnel_all}
    for no, step, _ in STEPS:
        out.append({"segment_key": segment_key("all", "all sessions"), "dimension": "all",
                    "segment": "all sessions", "step_no": no, "step": step, "sessions": by_no[no]})
    for r in seg_rows:
        for no, step, col in STEPS:
            out.append({"segment_key": segment_key(r["dimension"], r["segment"]),
                        "dimension": r["dimension"], "segment": r["segment"],
                        "step_no": no, "step": step, "sessions": int(r[col])})
    return out


def build_segments(seg_rows: list[dict], rev_rows: list[dict], total_sessions: int,
                   total_swp: int) -> tuple[list[dict], list[dict]]:
    """dim_segment and segment_kpis (segment funnel file joined with the revenue file)."""
    rev = {segment_key(r["dimension"], r["segment"]): r for r in rev_rows}
    dim, kpi = [], []

    def add(dimension, segment, sessions, swp, reliable):
        key = segment_key(dimension, segment)
        r = rev[key]
        dim.append({"segment_key": key, "dimension": dimension, "segment": segment,
                    "sessions": sessions, "reliable": reliable})
        kpi.append({"segment_key": key, "dimension": dimension, "segment": segment,
                    "sessions": sessions, "users": int(r["users"]), "sessions_with_purchase": swp,
                    "purchases": int(r["purchases"]), "revenue": float(r["revenue"]),
                    "buyers": int(r["buyers"]), "reliable": reliable})

    add("all", "all sessions", total_sessions, total_swp, "TRUE")
    for r in seg_rows:
        add(r["dimension"], r["segment"], int(r["sessions"]),
            int(r["sessions_with_purchase"]), "TRUE" if r["reliable"] == "True" else "FALSE")
    return dim, kpi


def main() -> int:
    daily = read_csv("30_daily_kpis.csv")
    write_csv(OUT / "daily_kpis.csv", daily,
              ["date", "sessions", "new_sessions", "returning_sessions",
               "sessions_with_purchase", "purchases", "revenue"])

    funnel_all = read_csv("20_funnel.csv")
    seg_rows = read_csv("22_segment_funnel.csv")
    write_csv(OUT / "dim_step.csv", [{"step_no": n, "step": s} for n, s, _ in STEPS],
              ["step_no", "step"])
    write_csv(OUT / "funnel_by_segment.csv", build_funnel_long(funnel_all, seg_rows),
              ["segment_key", "dimension", "segment", "step_no", "step", "sessions"])

    total_sessions = int(funnel_all[0]["all_valid_sessions"])
    total_swp = int(read_csv("21b_purchase_sessions_missing_steps.csv")[0]["sessions_with_purchase"])
    dim, kpi = build_segments(seg_rows, read_csv("26_revenue_by_segment.csv"), total_sessions, total_swp)
    write_csv(OUT / "dim_segment.csv", dim, ["segment_key", "dimension", "segment", "sessions", "reliable"])
    write_csv(OUT / "segment_kpis.csv", kpi,
              ["segment_key", "dimension", "segment", "sessions", "users", "sessions_with_purchase",
               "purchases", "revenue", "buyers", "reliable"])

    ret = read_csv("24_retention_long.csv")
    write_csv(OUT / "cohort_retention.csv", ret,
              ["cohort_week", "cohort_week_is_partial", "cohort_size", "week_n", "observable",
               "retained_users", "retention"])

    prod = read_csv("31_product_table.csv")
    write_csv(OUT / "products.csv", prod,
              ["item_name", "item_category", "view_sessions", "viewed_and_carted",
               "item_revenue", "units", "transactions"])
    print(f"Wrote 8 files to {OUT}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
