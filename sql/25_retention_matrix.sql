-- Phase 2.3: cohort matrix (wide). Rows = cohort week, columns = weeks after the first visit week.
-- Blank = week not observable in the data window. Partial first cohort is flagged.
WITH u AS (SELECT user_pseudo_id, MIN(session_date) AS first_date FROM sessions GROUP BY user_pseudo_id),
uw AS (SELECT user_pseudo_id, DATE_TRUNC(first_date, WEEK(MONDAY)) AS cohort_week FROM u),
bounds AS (SELECT MIN(session_date) AS first_data_date, DATE_TRUNC(MAX(session_date), WEEK(MONDAY)) AS last_week FROM sessions),
act AS (
  SELECT DISTINCT s.user_pseudo_id,
         DATE_DIFF(DATE_TRUNC(s.session_date, WEEK(MONDAY)), uw.cohort_week, WEEK) AS week_n
  FROM sessions s JOIN uw USING (user_pseudo_id)
),
cs AS (SELECT cohort_week, COUNT(*) AS cohort_size FROM uw GROUP BY cohort_week),
ret AS (
  SELECT uw.cohort_week, act.week_n, COUNT(*) AS retained
  FROM act JOIN uw USING (user_pseudo_id) GROUP BY uw.cohort_week, act.week_n
)
SELECT
  cs.cohort_week, cs.cohort_week < b.first_data_date AS cohort_week_is_partial, cs.cohort_size,
  ARRAY_AGG(IF(DATE_ADD(cs.cohort_week, INTERVAL r.week_n WEEK) <= b.last_week, ROUND(r.retained / cs.cohort_size, 4), NULL)
            ORDER BY r.week_n)[SAFE_OFFSET(0)] AS w0,
  MAX(IF(r.week_n = 1 AND DATE_ADD(cs.cohort_week, INTERVAL 1 WEEK) <= b.last_week, ROUND(r.retained / cs.cohort_size, 4), NULL)) AS w1,
  MAX(IF(r.week_n = 2 AND DATE_ADD(cs.cohort_week, INTERVAL 2 WEEK) <= b.last_week, ROUND(r.retained / cs.cohort_size, 4), NULL)) AS w2,
  MAX(IF(r.week_n = 3 AND DATE_ADD(cs.cohort_week, INTERVAL 3 WEEK) <= b.last_week, ROUND(r.retained / cs.cohort_size, 4), NULL)) AS w3,
  MAX(IF(r.week_n = 4 AND DATE_ADD(cs.cohort_week, INTERVAL 4 WEEK) <= b.last_week, ROUND(r.retained / cs.cohort_size, 4), NULL)) AS w4,
  MAX(IF(r.week_n = 5 AND DATE_ADD(cs.cohort_week, INTERVAL 5 WEEK) <= b.last_week, ROUND(r.retained / cs.cohort_size, 4), NULL)) AS w5,
  MAX(IF(r.week_n = 6 AND DATE_ADD(cs.cohort_week, INTERVAL 6 WEEK) <= b.last_week, ROUND(r.retained / cs.cohort_size, 4), NULL)) AS w6,
  MAX(IF(r.week_n = 7 AND DATE_ADD(cs.cohort_week, INTERVAL 7 WEEK) <= b.last_week, ROUND(r.retained / cs.cohort_size, 4), NULL)) AS w7,
  MAX(IF(r.week_n = 8 AND DATE_ADD(cs.cohort_week, INTERVAL 8 WEEK) <= b.last_week, ROUND(r.retained / cs.cohort_size, 4), NULL)) AS w8,
  MAX(IF(r.week_n = 9 AND DATE_ADD(cs.cohort_week, INTERVAL 9 WEEK) <= b.last_week, ROUND(r.retained / cs.cohort_size, 4), NULL)) AS w9,
  MAX(IF(r.week_n = 10 AND DATE_ADD(cs.cohort_week, INTERVAL 10 WEEK) <= b.last_week, ROUND(r.retained / cs.cohort_size, 4), NULL)) AS w10,
  MAX(IF(r.week_n = 11 AND DATE_ADD(cs.cohort_week, INTERVAL 11 WEEK) <= b.last_week, ROUND(r.retained / cs.cohort_size, 4), NULL)) AS w11,
  MAX(IF(r.week_n = 12 AND DATE_ADD(cs.cohort_week, INTERVAL 12 WEEK) <= b.last_week, ROUND(r.retained / cs.cohort_size, 4), NULL)) AS w12,
  MAX(IF(r.week_n = 13 AND DATE_ADD(cs.cohort_week, INTERVAL 13 WEEK) <= b.last_week, ROUND(r.retained / cs.cohort_size, 4), NULL)) AS w13
FROM cs CROSS JOIN bounds b
LEFT JOIN ret r ON r.cohort_week = cs.cohort_week
GROUP BY cs.cohort_week, cs.cohort_size, b.first_data_date
ORDER BY cs.cohort_week
