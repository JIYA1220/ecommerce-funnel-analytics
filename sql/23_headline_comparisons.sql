-- Phase 2.6: for each segment dimension, highest vs lowest session conversion among reliable segments
-- (>= 100 sessions), with Wilson 95% intervals. "Larger than noise" = intervals do not overlap.
-- Observational data: no causal claims.
CREATE TEMP FUNCTION wlo(x INT64, n INT64) AS (IF(n = 0, NULL,
  ((x / n + 1.96 * 1.96 / (2 * n)) - 1.96 * SQRT((x / n) * (1 - x / n) / n + 1.96 * 1.96 / (4 * n * n))) / (1 + 1.96 * 1.96 / n)));
CREATE TEMP FUNCTION whi(x INT64, n INT64) AS (IF(n = 0, NULL,
  ((x / n + 1.96 * 1.96 / (2 * n)) + 1.96 * SQRT((x / n) * (1 - x / n) / n + 1.96 * 1.96 / (4 * n * n))) / (1 + 1.96 * 1.96 / n)));
WITH top_c AS (
  SELECT country FROM sessions WHERE country != 'Other' GROUP BY country ORDER BY COUNT(*) DESC LIMIT 10
),
s AS (
  SELECT *, IF(session_number = 1, 'new', IF(session_number > 1, 'returning', 'unknown')) AS visitor_type,
         IF(country IN (SELECT country FROM top_c), country, 'Other') AS country_group
  FROM sessions
),
long AS (
  SELECT 'device_category' AS dimension, COALESCE(device_category, 'unknown') AS segment, has_purchase FROM s UNION ALL
  SELECT 'traffic_medium (first touch)', medium, has_purchase FROM s UNION ALL
  SELECT 'country', country_group, has_purchase FROM s UNION ALL
  SELECT 'visitor_type', visitor_type, has_purchase FROM s
),
agg AS (
  SELECT dimension, segment, COUNT(*) AS n, COUNTIF(has_purchase) AS x
  FROM long GROUP BY dimension, segment HAVING COUNT(*) >= 100
),
r AS (
  SELECT *, x / n AS p, wlo(x, n) AS lo, whi(x, n) AS hi,
    ROW_NUMBER() OVER (PARTITION BY dimension ORDER BY x / n DESC) AS rk_hi,
    ROW_NUMBER() OVER (PARTITION BY dimension ORDER BY x / n ASC) AS rk_lo
  FROM agg
)
SELECT
  h.dimension,
  h.segment AS highest_segment, h.n AS highest_sessions, ROUND(h.p, 5) AS highest_rate, ROUND(h.lo, 5) AS highest_ci_low, ROUND(h.hi, 5) AS highest_ci_high,
  l.segment AS lowest_segment, l.n AS lowest_sessions, ROUND(l.p, 5) AS lowest_rate, ROUND(l.lo, 5) AS lowest_ci_low, ROUND(l.hi, 5) AS lowest_ci_high,
  ROUND(100 * (h.p - l.p), 3) AS diff_percentage_points,
  IF(l.hi < h.lo, 'larger than noise (intervals do not overlap)', 'not distinguishable from noise (intervals overlap)') AS verdict
FROM r h JOIN r l ON h.dimension = l.dimension AND h.rk_hi = 1 AND l.rk_lo = 1
ORDER BY h.dimension
