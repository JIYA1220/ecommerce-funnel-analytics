# Decision memo: move the first gate from level 30 to level 40?

**Recommendation: do not ship `gate_40`.** Keep the gate at level 30.

This applies the decision rule written in `DESIGN.md` before the data was opened. The 95% interval for the change in 7-day retention is entirely below zero, and the guardrail did not fail. The analysis was run once, with no changes to the plan (see the end of `DESIGN.md`). Every number is from `results/ab_*.csv` and `results/ab_*.json`, produced by `python -m scripts.ab_analysis`.

## Result in one paragraph

Players who got the gate at level 40 came back on day 7 less often than players who got it at level 30: 18.20% against 19.02%, a drop of 0.82 percentage points (95% interval from -1.33 to -0.31 points). That is 4.3% fewer returning players in relative terms. The effect is small (Cohen's h = -0.021) but the test can tell it from noise.

## Data and checks (`results/ab_sanity.json`)

| Check | Result |
|---|---|
| Players analysed | 90,189 (44,700 `gate_30`, 45,489 `gate_40`) |
| Duplicate rows, players in both groups, missing values | none |
| Sample ratio mismatch (chi-square against 50/50) | chi-square 6.90, p = 0.0086. The pre-set stop threshold was 0.001, so the analysis went ahead. See limitations. |
| Game rounds | median 16, 99th percentile 493, maximum 49,854. 91 players are above the 99.9th percentile (1,074 rounds). 3,994 players have 0 rounds and were kept. |

Outliers do not affect the retention results (every player counts once, yes or no). They only matter for the guardrail, which is shown with and without capping.

## Effects (`results/ab_effects.csv`, `results/ab_guardrail.csv`)

Difference is `gate_40` minus `gate_30`.

| Metric | `gate_30` | `gate_40` | Difference | 95% interval (z-test) | Bootstrap interval | p-value |
|---|---|---|---|---|---|---|
| **7-day retention (primary)** | 19.02% (8,502 of 44,700) | 18.20% (8,279 of 45,489) | -0.82 points | -1.33 to -0.31 | -1.33 to -0.32 | 0.0016 |
| 1-day retention (secondary) | 44.82% | 44.23% | -0.59 points | -1.24 to +0.06 | -1.23 to +0.05 | 0.074 |

The z-test and the bootstrap (10,000 resamples) agree.

**The p-value in one sentence:** if the gate position made no difference to 7-day retention, a gap this large would appear in only about 1.6 of 1,000 repeats of the test.

**Guardrail, game rounds (`results/ab_guardrail.csv`):**

| Measure | `gate_30` | `gate_40` | Difference | Bootstrap 95% interval | Clearly lower? |
|---|---|---|---|---|---|
| Mean, all players | 52.46 | 51.30 | -1.16 | -4.26 to +0.91 | No |
| Mean, capped at 1,074 | 51.03 | 50.94 | -0.10 | -1.48 to +1.21 | No |
| Median | 17 | 16 | -1 | -1 to 0 | No |

The guardrail passes under all three views, so the conclusion does not depend on the extreme values. Rounds are not clearly different between the groups.

## Power (`results/ab_power.json`)

With these group sizes, a baseline 7-day retention of 19.02%, a 5% significance level and 80% power, the test can reliably detect a change of about 0.74 percentage points. Detecting 1 point would need about 24,658 players per group. So this sample is large enough for the 1 point practical threshold, and the observed drop (0.82 points) is just above the smallest change the test could reliably detect.

## Reasoning

1. The primary metric moved in the wrong direction, and the interval (-1.33 to -0.31 points) does not include zero. By the rule fixed in advance, that means do not ship.
2. The drop is modest. The best estimate (-0.82 points) is a little under the 1 point practical threshold, but the interval reaches beyond it (down to -1.33), so a loss larger than 1 point cannot be ruled out.
3. Nothing in the other metrics offsets the loss. 1-day retention is also lower, though not by more than noise. Rounds played show no clear change.

## Limitations

- **Sample ratio.** The groups are 49.56% and 50.44% of players. The mismatch test gives p = 0.0086. That passes the strict stop threshold of 0.001 set in the design, but it is below 0.05. If the assignment was not truly random, the effect could be biased. The data cannot show why the split is uneven. Ask whoever ran the test.
- **What retention means.** `retention_7` records activity on day 7, not at any time up to day 7.
- **No revenue.** The data has no spending, so the effect on revenue is unknown. A later gate could change income in either direction. The business may weigh this, and this memo does not.
- **No time stamps.** No check for novelty effects, weekday effects or trends over the test period.
- **One test, one population.** The result is about moving this gate from 30 to 40 in this game. It does not tell us about other positions.
- **Only the primary metric is tested at the 0.05 level.** The secondary metric and the guardrail are reported with their intervals and no adjustment for multiple comparisons.
- **Dataset.** A public teaching dataset whose Kaggle license is listed as Unknown. How the test was run in practice is not verified.
- **Why it happened is unknown.** The data shows that retention fell, not why. Any explanation would be a guess to test, not a finding.

## What to test next

1. **Check the assignment.** Confirm with the data owner how players were allocated, and why the split is uneven.
2. **Measure revenue and longer retention** (14 and 30 days) for the same players before deciding anything about gate position.
3. **Try other positions**, for example a gate earlier than level 30, with the same design: hypothesis, metrics and decision rule written before looking at results.
4. **Plan the sample size first.** About 25,000 players per group detects 1 point on 7-day retention. A smaller effect of interest needs more.
5. **Record time stamps** so novelty effects and trends can be checked.
