# A/B test design: Cookie Cats gate position

**Written before the data file was opened.** No result, count or column value from the data had been seen when this was written. This file is committed on its own, before the analysis code is run, so the git history shows the order. The analysis follows it. Any change after the data is seen is listed at the bottom with the reason.

## Context

Cookie Cats is a mobile puzzle game. At certain points a "gate" makes players wait or pay to continue. The test moved the first gate from level 30 (`gate_30`) to level 40 (`gate_40`). Data: the Kaggle dataset "Mobile Games A/B Testing: Cookie Cats" (DataCamp project). The Kaggle page lists its license as **Unknown**. The raw file is not committed to this repository. Only the code and aggregated results are.

Columns, as described by the dataset documentation (checked when the file is loaded): `userid`, `version` (`gate_30` or `gate_40`), `sum_gamerounds` (rounds played in the first 14 days after install), `retention_1` (player played again 1 day after install), `retention_7` (player played again 7 days after install).

## Hypothesis

- Control: `gate_30` (current game). Treatment: `gate_40`.
- Business idea: a later gate lets players enjoy the game longer before a pause, which may keep more of them.
- Null hypothesis H0: 7-day retention is the same in both groups.
- Alternative H1: 7-day retention differs (two-sided test). A two-sided test is used because a later gate could also lower retention.

## Metrics

| Role | Metric | Definition |
|---|---|---|
| Primary | 7-day retention | Share of players with `retention_7` true. |
| Secondary | 1-day retention | Share of players with `retention_1` true. |
| Guardrail | Game rounds | Mean and median of `sum_gamerounds`. The guardrail fails if the treatment shows a clearly lower mean or median (95% interval for the difference below zero). |

The effect is always reported as `gate_40` minus `gate_30`.

## Unit of randomization and analysis

One player (`userid`) is the unit, assumed to be assigned once at install. Each player appears in one group and one row. The analysis unit equals the randomization unit, so a simple two-group comparison is valid. This is checked in the sanity checks, not assumed.

## Significance and decisions

- Significance level: **0.05**, two-sided, for the primary metric only. The decision is made on the primary metric.
- The secondary metric and the guardrail are reported with their own intervals. They are not used to override the primary decision, except for the guardrail rule below. No multiple-comparison adjustment is made, and this is stated in the memo.
- **Practical threshold (assumption, to be confirmed by the business):** a change of 1 percentage point in 7-day retention is the smallest change that would matter.
- Decision rule, fixed now:
  - **Ship `gate_40`** if the 95% interval for the difference in 7-day retention is entirely above 0 and the guardrail does not fail.
  - **Do not ship** if the interval is entirely below 0, or the guardrail fails.
  - **Otherwise** the result is inconclusive. If the minimum detectable effect (below) is at most 1 percentage point, the memo says there is no evidence of a material effect and the current gate stays. If the minimum detectable effect is larger than 1 percentage point, the recommendation is to run longer.

## Sanity checks (before the effect is analyzed)

1. **Sample ratio mismatch:** chi-square test on the two group sizes against an expected 50/50 split (assumption: the test was meant to be equal). A p-value below 0.001 means the assignment is suspect and the effect is not interpreted.
2. **Duplicates:** count duplicate `userid` values. Exact duplicate rows are dropped. Any `userid` appearing in both groups is excluded from the analysis, and the number is reported.
3. **Missing values and types:** every column must have no missing values and the expected types, otherwise the analysis stops.
4. **Outliers in game rounds:** report the distribution (percentiles, maximum) and the number of players with 0 rounds.

### Outlier handling, fixed now

- The retention metrics use **every player**. No players are removed because of extreme rounds. Retention is a yes or no and is not distorted by one large value.
- For the guardrail, report the mean with all players and the mean after capping `sum_gamerounds` at the 99.9th percentile of the combined sample, plus the median (which does not depend on extremes). The guardrail conclusion must agree under both, otherwise the memo says so.
- Players with 0 rounds are kept. They installed the game.

## Analysis plan

1. **Difference in retention** (`gate_40` minus `gate_30`) with a 95% confidence interval, using a two-proportion z-test (pooled standard error for the test, unpooled for the interval).
2. **Bootstrap check:** 10,000 bootstrap resamples with a fixed seed, percentile 95% interval. It should agree with the z interval. Any disagreement is reported.
3. **Effect size:** absolute difference in percentage points, relative lift, and Cohen's h.
4. **p-value, in one plain sentence:** "If the gate position made no difference to retention, we would see a gap at least this large in about p of 100 repeats of the test."
5. **Power and minimum detectable effect:** for two-sided alpha 0.05 and 80% power, using the group sizes and the control group's 7-day retention as the baseline. Also the sample size needed per group to detect 1 percentage point.
6. The analysis is run **once** after the sanity checks. No peeking at partial results and no changing of the metric after seeing the data.

## Known limits to state in the memo

- `retention_7` records whether the player was active on day 7, not whether they were active at any time up to day 7.
- No time stamps, so no check for time trends or novelty effects.
- No spending or revenue data, so the effect on revenue is unknown.
- One test on one population. Results do not transfer to other games or other gate positions.
- The dataset license is unknown, and the data is a public teaching dataset, so how the test was run in practice is not verified.

## Changes after the data was seen

None. The analysis ran once, with the plan as written. Note: the sample ratio check gave p = 0.0086, which is under 0.05 but above the stop threshold of 0.001 set here, so the analysis went ahead, and the memo reports it as a limitation.
