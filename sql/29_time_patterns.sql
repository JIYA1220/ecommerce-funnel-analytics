-- Phase 2.5: session conversion (sessions with purchase / all valid sessions) by day of week, week, month.
-- Nov and Dec include Black Friday and the holiday season: do not read time changes as effects of causes.
CREATE TEMP FUNCTION wlo(x INT64, n INT64) AS (IF(n = 0, NULL,
  ((x / n + 1.96 * 1.96 / (2 * n)) - 1.96 * SQRT((x / n) * (1 - x / n) / n + 1.96 * 1.96 / (4 * n * n))) / (1 + 1.96 * 1.96 / n)));
CREATE TEMP FUNCTION whi(x INT64, n INT64) AS (IF(n = 0, NULL,
  ((x / n + 1.96 * 1.96 / (2 * n)) + 1.96 * SQRT((x / n) * (1 - x / n) / n + 1.96 * 1.96 / (4 * n * n))) / (1 + 1.96 * 1.96 / n)));
WITH long AS (
  SELECT 'day_of_week' AS grain, FORMAT_DATE('%u %A', session_date) AS period, has_purchase, session_date FROM sessions UNION ALL
  SELECT 'week (Monday start)', CAST(DATE_TRUNC(session_date, WEEK(MONDAY)) AS STRING), has_purchase, session_date FROM sessions UNION ALL
  SELECT 'month', FORMAT_DATE('%Y-%m', session_date), has_purchase, session_date FROM sessions
),
agg AS (
  SELECT grain, period, COUNT(*) AS sessions, COUNTIF(has_purchase) AS sessions_with_purchase,
         COUNT(DISTINCT session_date) AS days_in_window
  FROM long GROUP BY grain, period
)
SELECT grain, period, days_in_window, sessions, sessions_with_purchase,
       ROUND(sessions_with_purchase / sessions, 5) AS session_conversion_rate,
       ROUND(wlo(sessions_with_purchase, sessions), 5) AS ci_low,
       ROUND(whi(sessions_with_purchase, sessions), 5) AS ci_high,
       ROUND(sessions / days_in_window, 1) AS sessions_per_day
FROM agg ORDER BY grain, period
