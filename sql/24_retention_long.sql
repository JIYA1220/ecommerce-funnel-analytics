-- Phase 2.3: weekly cohort retention, long format (one row per cohort and week offset).
-- Cohort = Monday-start week of the user's first valid session in the data window.
-- Retention week N = users with any session in cohort week + N / cohort size.
-- retention is NULL when week N is after the last week of data (not observable, not 0%).
WITH u AS (SELECT user_pseudo_id, MIN(session_date) AS first_date FROM sessions GROUP BY user_pseudo_id),
uw AS (SELECT user_pseudo_id, first_date, DATE_TRUNC(first_date, WEEK(MONDAY)) AS cohort_week FROM u),
bounds AS (SELECT MIN(session_date) AS first_data_date, MAX(session_date) AS last_data_date FROM sessions),
act AS (
  SELECT DISTINCT s.user_pseudo_id,
         DATE_DIFF(DATE_TRUNC(s.session_date, WEEK(MONDAY)), uw.cohort_week, WEEK) AS week_n
  FROM sessions s JOIN uw USING (user_pseudo_id)
),
cs AS (SELECT cohort_week, COUNT(*) AS cohort_size FROM uw GROUP BY cohort_week),
grid AS (SELECT cohort_week, cohort_size, week_n FROM cs, UNNEST(GENERATE_ARRAY(0, 13)) AS week_n),
ret AS (
  SELECT uw.cohort_week, act.week_n, COUNT(*) AS retained
  FROM act JOIN uw USING (user_pseudo_id) GROUP BY uw.cohort_week, act.week_n
)
SELECT
  g.cohort_week,
  g.cohort_week < b.first_data_date AS cohort_week_is_partial,
  g.cohort_size,
  g.week_n,
  DATE_ADD(g.cohort_week, INTERVAL g.week_n WEEK) <= DATE_TRUNC(b.last_data_date, WEEK(MONDAY)) AS observable,
  IF(DATE_ADD(g.cohort_week, INTERVAL g.week_n WEEK) <= DATE_TRUNC(b.last_data_date, WEEK(MONDAY)),
     COALESCE(r.retained, 0), NULL) AS retained_users,
  IF(DATE_ADD(g.cohort_week, INTERVAL g.week_n WEEK) <= DATE_TRUNC(b.last_data_date, WEEK(MONDAY)),
     ROUND(COALESCE(r.retained, 0) / g.cohort_size, 4), NULL) AS retention
FROM grid g CROSS JOIN bounds b
LEFT JOIN ret r ON r.cohort_week = g.cohort_week AND r.week_n = g.week_n
ORDER BY g.cohort_week, g.week_n
