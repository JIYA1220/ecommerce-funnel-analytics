"""End-to-end test of the A/B analysis on a small synthetic file (not the real data)."""

import csv
import json

import numpy as np
import pytest

from scripts import ab_analysis as A


def write_synthetic(path, n=6000, p1=0.2, p2=0.2, seed=1, extra_rows=()):
    rng = np.random.default_rng(seed)
    rows = []
    for i in range(n):
        v = A.CONTROL if i % 2 == 0 else A.TREATMENT
        p = p1 if v == A.CONTROL else p2
        r7 = bool(rng.random() < p)
        rows.append([i, v, int(rng.poisson(50)), bool(rng.random() < 0.4), r7])
    rows.extend(extra_rows)
    with path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(A.REQUIRED)
        w.writerows(rows)


def test_run_end_to_end_no_effect(tmp_path):
    f = tmp_path / "d.csv"
    write_synthetic(f)
    out = A.run(f, tmp_path / "res")
    assert out["sanity"]["players_analysed"] == 6000
    assert not out["sanity"]["srm_failed"]
    assert out["primary"]["ci_low_pp"] < 0 < out["primary"]["ci_high_pp"]
    assert (tmp_path / "res" / "ab_effects.csv").exists()
    assert json.loads((tmp_path / "res" / "ab_power.json").read_text())["mde_pp"] > 0


def test_detects_a_real_effect(tmp_path):
    f = tmp_path / "d.csv"
    write_synthetic(f, n=40000, p1=0.2, p2=0.24, seed=2)
    out = A.run(f, tmp_path / "res")
    assert out["primary"]["p_value"] < 0.001
    assert out["primary"]["diff_pp"] == pytest.approx(4, abs=1.2)
    assert out["decision"] == "ship"


def test_srm_failure_is_flagged(tmp_path):
    f = tmp_path / "d.csv"
    extra = [[10_000 + i, A.CONTROL, 10, False, False] for i in range(1500)]
    write_synthetic(f, extra_rows=extra)
    out = A.run(f, tmp_path / "res")
    assert out["sanity"]["srm_failed"]
    assert out["decision"].startswith("invalid test")


def test_duplicates_and_cross_group_users(tmp_path):
    f = tmp_path / "d.csv"
    extra = [[0, A.CONTROL, 0, False, False],  # exact duplicate of row 0 if it matches, else conflict
             [1, A.CONTROL, 5, True, True]]    # user 1 is in treatment already: in both groups
    write_synthetic(f, n=200, extra_rows=extra)
    _, report = A.sanity_and_clean(A.load_data(f))
    assert report["userids_in_both_groups_excluded"] >= 1
    assert report["players_analysed"] < 200 + 2


def test_validation_errors(tmp_path):
    f = tmp_path / "bad.csv"
    f.write_text("userid,version\n1,gate_30\n")
    with pytest.raises(ValueError, match="missing columns"):
        A.load_data(f)
    g = tmp_path / "bad2.csv"
    g.write_text("userid,version,sum_gamerounds,retention_1,retention_7\n1,gate_99,3,True,False\n")
    with pytest.raises(ValueError):
        A.load_data(g)
    h = tmp_path / "bad3.csv"
    h.write_text("userid,version,sum_gamerounds,retention_1,retention_7\n1,gate_30,,True,False\n")
    with pytest.raises(ValueError, match="missing values"):
        A.load_data(h)
