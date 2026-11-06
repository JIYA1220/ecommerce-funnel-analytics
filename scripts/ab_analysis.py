"""Run the A/B test analysis exactly as planned in ab_test/DESIGN.md.

Usage (PowerShell): python -m scripts.ab_analysis [--data ab_test/data/cookie_cats.csv]

Steps: load and validate, sanity checks (sample ratio mismatch, duplicates, outliers), then the
effect on 7-day retention (primary), 1-day retention (secondary) and game rounds (guardrail),
then power and the decision rule. Writes results/ab_*.json and results/ab_*.csv.
The analysis is run once. It does not look at partial results.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import numpy as np
import pandas as pd

from scripts import ab_stats as S

REQUIRED = ["userid", "version", "sum_gamerounds", "retention_1", "retention_7"]
CONTROL, TREATMENT = "gate_30", "gate_40"
SRM_ALPHA = 0.001
THRESHOLD = 0.01  # practical threshold, 1 percentage point (DESIGN.md)
RESULTS = Path("results")


def load_data(path: Path) -> pd.DataFrame:
    """Load the CSV and check columns, types and missing values. Stops on any problem."""
    df = pd.read_csv(path)
    missing_cols = [c for c in REQUIRED if c not in df.columns]
    if missing_cols:
        raise ValueError(f"missing columns: {missing_cols}")
    if df[REQUIRED].isna().any().any():
        raise ValueError("missing values found: " + str(df[REQUIRED].isna().sum().to_dict()))
    for c in ("retention_1", "retention_7"):
        df[c] = df[c].astype(str).str.lower().map({"true": True, "false": False, "1": True, "0": False})
        if df[c].isna().any():
            raise ValueError(f"{c} has values that are not true or false")
        df[c] = df[c].astype(bool)
    if set(df["version"].unique()) != {CONTROL, TREATMENT}:
        raise ValueError(f"version must be exactly {CONTROL} and {TREATMENT}, got {sorted(df['version'].unique())}")
    if not pd.api.types.is_numeric_dtype(df["sum_gamerounds"]) or (df["sum_gamerounds"] < 0).any():
        raise ValueError("sum_gamerounds must be numeric and not negative")
    return df[REQUIRED].copy()


def sanity_and_clean(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Sanity checks from DESIGN.md. Returns the cleaned data and a report."""
    n_rows = len(df)
    exact_dups = int(df.duplicated().sum())
    df = df.drop_duplicates()
    dup_ids = int(df["userid"].duplicated().sum())
    groups_per_user = df.groupby("userid")["version"].nunique()
    in_both = groups_per_user[groups_per_user > 1].index
    df = df[~df["userid"].isin(in_both)]
    n1 = int((df["version"] == CONTROL).sum())
    n2 = int((df["version"] == TREATMENT).sum())
    chi2, p = S.srm_test(n1, n2)
    r = df["sum_gamerounds"].to_numpy(dtype=float)
    pct = {f"p{q}": float(np.quantile(r, q / 100)) for q in (50, 90, 99, 99.9)}
    report = {
        "rows_in_file": n_rows,
        "exact_duplicate_rows_dropped": exact_dups,
        "userids_repeated_after_exact_dedup": dup_ids,
        "userids_in_both_groups_excluded": len(in_both),
        "players_analysed": len(df),
        "n_control": n1, "n_treatment": n2,
        "share_control": n1 / (n1 + n2),
        "srm_chi2": chi2, "srm_p_value": p, "srm_alpha": SRM_ALPHA,
        "srm_failed": bool(p < SRM_ALPHA),
        "rounds_percentiles": pct, "rounds_max": float(r.max()),
        "players_with_zero_rounds": int((r == 0).sum()),
        "players_above_p99_9": int((r > pct["p99.9"]).sum()),
    }
    return df, report


def retention_effect(df: pd.DataFrame, col: str) -> dict:
    a, b = df[df["version"] == CONTROL][col], df[df["version"] == TREATMENT][col]
    x1, n1, x2, n2 = int(a.sum()), len(a), int(b.sum()), len(b)
    t = S.two_prop_test(x1, n1, x2, n2)
    bl, bh = S.bootstrap_diff_props(x1, n1, x2, n2)
    return {"metric": col, "n_control": n1, "n_treatment": n2, "x_control": x1, "x_treatment": x2,
            "rate_control": t["p_control"], "rate_treatment": t["p_treatment"],
            "diff_pp": 100 * t["diff"], "relative_lift": t["relative_lift"],
            "ci_low_pp": 100 * t["ci_low"], "ci_high_pp": 100 * t["ci_high"],
            "boot_ci_low_pp": 100 * bl, "boot_ci_high_pp": 100 * bh,
            "z": t["z"], "p_value": t["p_value"], "cohens_h": t["cohens_h"]}


def guardrail(df: pd.DataFrame) -> list[dict]:
    a = df[df["version"] == CONTROL]["sum_gamerounds"].to_numpy(dtype=float)
    b = df[df["version"] == TREATMENT]["sum_gamerounds"].to_numpy(dtype=float)
    _cap_all, cap = S.cap_at_quantile(np.concatenate([a, b]), 0.999)
    ca, cb = np.minimum(a, cap), np.minimum(b, cap)
    out = []
    for name, x, y, stat in [("mean rounds, all players", a, b, np.mean),
                             (f"mean rounds, capped at p99.9 ({cap:.0f})", ca, cb, np.mean),
                             ("median rounds", a, b, np.median)]:
        lo, hi = S.bootstrap_diff_stat(x, y, stat)
        d = float(stat(y) - stat(x))
        out.append({"measure": name, "control": float(stat(x)), "treatment": float(stat(y)),
                    "diff": d, "boot_ci_low": lo, "boot_ci_high": hi, "clearly_lower": bool(hi < 0)})
    return out


def power_report(p_base: float, n1: int, n2: int) -> dict:
    mde = S.mde_two_proportions(p_base, n1, n2)
    return {"baseline_7day_retention_control": p_base, "n_control": n1, "n_treatment": n2,
            "alpha": 0.05, "power": 0.8, "mde_pp": 100 * mde,
            "n_per_group_for_1pp": S.n_per_group_for_diff(p_base, THRESHOLD)}


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def run(data: Path, results: Path = RESULTS) -> dict:
    results.mkdir(parents=True, exist_ok=True)
    df, sanity = sanity_and_clean(load_data(data))
    (results / "ab_sanity.json").write_text(json.dumps(sanity, indent=2), encoding="utf-8")
    primary, secondary = retention_effect(df, "retention_7"), retention_effect(df, "retention_1")
    write_csv(results / "ab_effects.csv", [primary, secondary])
    g = guardrail(df)
    write_csv(results / "ab_guardrail.csv", g)
    pw = power_report(primary["rate_control"], sanity["n_control"], sanity["n_treatment"])
    (results / "ab_power.json").write_text(json.dumps(pw, indent=2), encoding="utf-8")
    if sanity["srm_failed"]:
        decision = "invalid test: sample ratio mismatch, effect not interpreted"
    else:
        decision = S.decide(primary["ci_low_pp"] / 100, primary["ci_high_pp"] / 100,
                            any(r["clearly_lower"] for r in g), pw["mde_pp"] / 100, THRESHOLD)
    (results / "ab_decision.json").write_text(json.dumps({"rule_result": decision}, indent=2), encoding="utf-8")
    return {"sanity": sanity, "primary": primary, "secondary": secondary, "guardrail": g,
            "power": pw, "decision": decision}


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--data", type=Path, default=Path("ab_test/data/cookie_cats.csv"))
    args = p.parse_args()
    if not args.data.exists():
        print(f"Data file not found: {args.data}. See ab_test/README.md.")
        return 1
    out = run(args.data)
    print(json.dumps(out["sanity"], indent=2))
    print("Rule result:", out["decision"])
    print("Written to results/ab_*.json and results/ab_*.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
