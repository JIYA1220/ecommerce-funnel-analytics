-- Phase 2.2: funnel by segment (device, first-touch medium, country top 10 + Other, new vs returning).
-- Ordered funnel (strict order rule). Wilson 95% intervals. Segments under 100 sessions: reliable = FALSE.
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
  SELECT 'device_category' AS dimension, COALESCE(device_category, 'unknown') AS segment, * FROM s UNION ALL
  SELECT 'traffic_medium (first touch)', medium, * FROM s UNION ALL
  SELECT 'country', country_group, * FROM s UNION ALL
  SELECT 'visitor_type', visitor_type, * FROM s
),
agg AS (
  SELECT dimension, segment,
    COUNT(*) AS sessions,
    COUNTIF(reach_entry IS NOT NULL) AS n_entry,
    COUNTIF(reach_view_item IS NOT NULL) AS n_view_item,
    COUNTIF(reach_add_to_cart IS NOT NULL) AS n_add_to_cart,
    COUNTIF(reach_begin_checkout IS NOT NULL) AS n_begin_checkout,
    COUNTIF(reach_add_payment_info IS NOT NULL) AS n_add_payment_info,
    COUNTIF(reach_purchase IS NOT NULL) AS n_purchase,
    COUNTIF(has_purchase) AS sessions_with_purchase
  FROM long GROUP BY dimension, segment
)
SELECT
  dimension, segment, sessions, sessions >= 100 AS reliable,
  n_entry, n_view_item, n_add_to_cart, n_begin_checkout, n_add_payment_info, n_purchase,
  ROUND(SAFE_DIVIDE(n_view_item, n_entry), 4) AS conv_view_item,
  ROUND(SAFE_DIVIDE(n_add_to_cart, n_view_item), 4) AS conv_add_to_cart,
  ROUND(SAFE_DIVIDE(n_begin_checkout, n_add_to_cart), 4) AS conv_begin_checkout,
  ROUND(SAFE_DIVIDE(n_add_payment_info, n_begin_checkout), 4) AS conv_add_payment_info,
  ROUND(SAFE_DIVIDE(n_purchase, n_add_payment_info), 4) AS conv_purchase,
  ROUND(SAFE_DIVIDE(n_purchase, n_entry), 5) AS overall_funnel_conv,
  ROUND(wlo(n_purchase, n_entry), 5) AS overall_ci_low,
  ROUND(whi(n_purchase, n_entry), 5) AS overall_ci_high,
  sessions_with_purchase,
  ROUND(SAFE_DIVIDE(sessions_with_purchase, sessions), 5) AS session_conversion_rate,
  ROUND(wlo(sessions_with_purchase, sessions), 5) AS sessionconv_ci_low,
  ROUND(whi(sessions_with_purchase, sessions), 5) AS sessionconv_ci_high,
  (SELECT step FROM UNNEST([
     STRUCT('view_item' AS step, SAFE_DIVIDE(n_view_item, n_entry) AS r),
     STRUCT('add_to_cart', SAFE_DIVIDE(n_add_to_cart, n_view_item)),
     STRUCT('begin_checkout', SAFE_DIVIDE(n_begin_checkout, n_add_to_cart)),
     STRUCT('add_payment_info', SAFE_DIVIDE(n_add_payment_info, n_begin_checkout)),
     STRUCT('purchase', SAFE_DIVIDE(n_purchase, n_add_payment_info))]) WHERE r IS NOT NULL ORDER BY r LIMIT 1) AS lowest_step_conversion
FROM agg
ORDER BY dimension, sessions DESC
