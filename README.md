# E-commerce Funnel and Retention Analytics

Funnel, retention and segmentation analysis of the Google Merchandise Store (GA4 sample data, BigQuery), with a business analyst pack (business case, KPI tree, BRD, process flows) and an A/B test analysis (Cookie Cats). Built for Data Analyst and Business Analyst roles. Every number in this repository comes from a saved query or script output in `results/`. Anything not measured is labeled "not yet measured", an assumption, or a scenario.

**Headline:** in the 92 days to 2021-01-31, 0.79% of 359,815 entering sessions reached purchase. Most shoppers are lost before the cart (79% never view an item, 80% of viewers never add to cart), returning visitors convert 4.6 times as often as new ones, and about 41% of purchase sessions have no add-to-cart event, which looks like a tracking gap. In a separate A/B test, moving a mobile game's first gate from level 30 to 40 lowered 7-day retention by 0.82 percentage points.

## Business questions

1. Where do shoppers drop out between entering the store and buying, and does it differ by device, acquisition medium, country or new vs returning visitors?
2. Do visitors come back (weekly cohort retention)?
3. Which products get views but few add-to-carts, and what drives revenue?
4. Is a seasonal pattern hiding in the conversion numbers?
5. What should the business change, and what should be built to track it? (`ba/`)
6. Does a different gate position change 7-day retention in a mobile game? (`ab_test/`)

## Data and limitations

Details: [DATA.md](DATA.md), [docs/DATA_QUALITY.md](docs/DATA_QUALITY.md), [docs/METRICS.md](docs/METRICS.md).

- **GA4 sample e-commerce dataset:** `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`, 2020-11-01 to 2021-01-31, 4,295,584 events, 270,154 users, 360,129 sessions. Obfuscated by Google; one store; three months including the holiday season.
- **Traffic source is first-touch**, not per session, and 21% of events have an unknown medium (`(data deleted)` or `<Other>`).
- **Revenue and orders are understated by an unknown amount:** 906 of 5,692 purchase events have no usable transaction id.
- **About 41% of purchase sessions have no add-to-cart event** (2,000 of 4,848). Real behaviour or missing events cannot be told apart.
- **Item ids differ between event types**, so product tables join on item name.
- **Cookie Cats:** the Kaggle page lists its license as **Unknown**. It is used for analysis only; the raw file is not in this repository.

## Method

- **SQL:** BigQuery Standard SQL with CTEs, `UNNEST(event_params)`, window functions and array functions. Each query is one numbered file in `sql/`; each output is a CSV in `results/`. Metrics are defined in `docs/METRICS.md` before they are computed.
- **Funnel:** session level (user id plus session id), six steps, with a strict order rule (a step counts only after the previous one). The number of sessions that skip steps is reported (`results/21_funnel_skipping.csv`).
- **Retention:** weekly cohorts by first-visit week; weeks not yet observed are blank, not zero.
- **Statistics:** Wilson 95% intervals for every headline rate; a difference is "larger than noise" only when intervals do not overlap; no causal claims from observational data. SQL intervals are checked against `statsmodels` in the tests.
- **BigQuery cost control:** every query does a dry run first and is blocked above 1 GB unless approved. Bytes are logged in `results/_bytes_log.csv`. Two one-time table builds of 1.12 GB and 1.20 GB were approved.
- **A/B test:** design written and committed before the data was opened ([ab_test/DESIGN.md](ab_test/DESIGN.md)), two-proportion z-test plus bootstrap check, sample ratio check, power analysis, decision rule fixed in advance.

## Key findings (copied from `results/`)

Period 2020-11-01 to 2021-01-31. Intervals are 95% Wilson intervals. More in [docs/FINDINGS.md](docs/FINDINGS.md).

| Finding | Value | 95% interval | Source |
|---|---|---|---|
| Valid sessions / users | 360,129 / 270,154 | | `results/01_profile_overview.csv` |
| Overall funnel conversion (entry to purchase, ordered) | 0.79% (2,834 of 359,815) | 0.76% to 0.82% | `results/20_funnel.csv` |
| Session conversion rate (sessions with a purchase event) | 1.35% (4,848 of 360,129) | 1.31% to 1.38% | `results/21b_purchase_sessions_missing_steps.csv` |
| Entry to view item | 21.4% | 21.3% to 21.5% | `results/20_funnel.csv` |
| View item to add to cart | 19.7% | 19.4% to 20.0% | `results/20_funnel.csv` |
| Begin checkout to purchase | 52.3% | 51.0% to 53.7% | `results/20_funnel.csv` |
| Purchase sessions with no add-to-cart event | 2,000 of 4,848 | | `results/21b_purchase_sessions_missing_steps.csv` |
| Session conversion, returning vs new | 3.10% vs 0.68% | 3.00% to 3.21% vs 0.65% to 0.71% | `results/23_headline_comparisons.csv` |
| Session conversion, referral vs paid search (first touch) | 1.66% vs 0.98% | 1.57% to 1.77% vs 0.84% to 1.15% | `results/23_headline_comparisons.csv` |
| Device, mobile vs tablet; country, Spain vs Italy | not distinguishable from noise | intervals overlap | `results/23_headline_comparisons.csv` |
| Week 1 retention (full cohorts, pooled) | 4.20% | 4.12% to 4.28% | `results/dashboard_expected_values.csv` |
| Revenue / orders / AOV (understated) | 307,640 / 4,451 / 69.12 | | `results/26_revenue_by_segment.csv` |
| Weekly conversion, peak vs lowest week | 1.99% (2020-12-07) vs 0.56% (2021-01-04) | | `results/29_time_patterns.csv` |

## Dashboard

The Power BI data, data model, DAX measures, page layout and a beginner build guide are ready: [powerbi/MEASURES.md](powerbi/MEASURES.md), [powerbi/BUILD_STEPS.md](powerbi/BUILD_STEPS.md), and the CSVs in `powerbi/`. `results/dashboard_expected_values.csv` lists the values the dashboard must show.

**Not yet done:** the `.pbix` file and screenshots are built by hand and have not been added. The DAX has not been run in Power BI, so there are no screenshots here yet. They will go in `powerbi/screenshots/` and be checked against `results/`.

## Business analyst pack

| Document | Purpose |
|---|---|
| [ba/BUSINESS_CASE.md](ba/BUSINESS_CASE.md) | Problem, stakeholders, current state, scenario table, options compared, recommendation |
| [ba/KPI_TREE.md](ba/KPI_TREE.md) | Revenue broken into sessions, orders per session and AOV, then step conversions, with owners (Mermaid diagram) |
| [ba/BRD.md](ba/BRD.md) | Funnel Monitoring Dashboard requirements: 12 user stories with Given/When/Then, RACI |
| [ba/PROCESS_FLOW.md](ba/PROCESS_FLOW.md) | As-is (assumed) and to-be flows; editable `ba/as_is.drawio`, `ba/to_be.drawio` |
| [ba/STAKEHOLDER_SUMMARY.md](ba/STAKEHOLDER_SUMMARY.md) | One-page plain language summary |

Scenario amounts (for example, +1 point of add-to-cart rate is worth 9,943 over the 92 days, 3.2% of revenue) are what-if arithmetic with stated assumptions, not forecasts (`results/ba_scenarios.csv`).

## A/B test result (Cookie Cats)

Memo: [ab_test/DECISION.md](ab_test/DECISION.md). 90,189 players, gate at level 30 vs level 40.

| Metric | gate_30 | gate_40 | Difference | 95% interval | p-value |
|---|---|---|---|---|---|
| 7-day retention (primary) | 19.02% | 18.20% | -0.82 points | -1.33 to -0.31 | 0.0016 |
| 1-day retention (secondary) | 44.82% | 44.23% | -0.59 points | -1.24 to +0.06 | 0.074 |

Guardrail (game rounds) shows no clear change. The rule written before the analysis gives **do not ship gate_40**. Caveats: group sizes are slightly uneven (sample ratio check p = 0.0086, above the strict stop threshold of 0.001), there is no revenue data, and the dataset license is unknown. Source files: `results/ab_effects.csv`, `results/ab_guardrail.csv`, `results/ab_power.json`, `results/ab_sanity.json`.

## How to reproduce

Setup (PowerShell, from the repo root):

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
gcloud auth application-default login
$env:GOOGLE_CLOUD_PROJECT = "<your-sandbox-project-id>"
```

Each phase is one command. Add `-DryRunOnly` to see the bytes each query would scan without running anything.

| Phase | Command |
|---|---|
| 0 Smoke test | `powershell -ExecutionPolicy Bypass -File scripts\reproduce.ps1 -Phase 0` |
| 1 Data profile | `powershell -ExecutionPolicy Bypass -File scripts\reproduce.ps1 -Phase 1` |
| 2 Funnel, retention, segments | `powershell -ExecutionPolicy Bypass -File scripts\reproduce.ps1 -Phase 2` |
| 3 Power BI files | `powershell -ExecutionPolicy Bypass -File scripts\reproduce.ps1 -Phase 3` |
| 4 BA pack numbers and diagrams | `powershell -ExecutionPolicy Bypass -File scripts\reproduce.ps1 -Phase 4` |
| 5 A/B test (needs `ab_test\data\cookie_cats.csv`) | `powershell -ExecutionPolicy Bypass -File scripts\reproduce.ps1 -Phase 5` |

Tests and checks:

```powershell
python -m pytest -q
```

Phase 1 scans about 1.8 GB and Phase 2 about 3.6 GB of BigQuery data (free Sandbox, no billing). The dry-run mode was tested for phases 0 to 2, and phase 4 was run in full. Phases 3 and 5 were run through their individual commands rather than through this script. A full re-run is not required, since the results are saved in `results/`.

## Repository layout

`sql/` numbered queries, `scripts/` Python runners and statistics, `results/` outputs of every query, `powerbi/` Power BI data and build guide, `ba/` business analyst pack, `ab_test/` A/B design and decision, `docs/` metrics, data quality and findings, `tests/` tests (CI runs lint, tests and a credential scan).

## Skills shown

BigQuery SQL, CTEs, window functions, `UNNEST` and array functions, funnel analysis, cohort retention analysis, segmentation, Wilson confidence intervals, data quality profiling, metric definition, Python (pandas, scipy, statsmodels), A/B testing (sample ratio check, two-proportion z-test, bootstrap, power and minimum detectable effect), business case and scenario analysis, KPI trees, requirements documentation (BRD, user stories, acceptance criteria, RACI), process mapping, Power BI data model and DAX measures (designed and documented; the dashboard build is pending), testing and CI.

## License

MIT, see [LICENSE](LICENSE). The data sources have their own terms: the GA4 sample is Google's public dataset; Cookie Cats is listed on Kaggle with license Unknown.
