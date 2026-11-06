-- Phase 2.1: session-level funnel with the strict order rule (docs/METRICS.md).
WITH s AS (SELECT * FROM sessions),
steps AS (
  SELECT 1 AS step_no, 'entry (session_start or page_view)' AS step,
         COUNTIF(reach_entry IS NOT NULL) AS sessions_ordered, COUNTIF(has_entry) AS sessions_unordered FROM s UNION ALL
  SELECT 2, 'view_item', COUNTIF(reach_view_item IS NOT NULL), COUNTIF(has_view_item) FROM s UNION ALL
  SELECT 3, 'add_to_cart', COUNTIF(reach_add_to_cart IS NOT NULL), COUNTIF(has_add_to_cart) FROM s UNION ALL
  SELECT 4, 'begin_checkout', COUNTIF(reach_begin_checkout IS NOT NULL), COUNTIF(has_begin_checkout) FROM s UNION ALL
  SELECT 5, 'add_payment_info', COUNTIF(reach_add_payment_info IS NOT NULL), COUNTIF(has_add_payment_info) FROM s UNION ALL
  SELECT 6, 'purchase', COUNTIF(reach_purchase IS NOT NULL), COUNTIF(has_purchase) FROM s
)
SELECT
  step_no, step, sessions_ordered, sessions_unordered,
  ROUND(SAFE_DIVIDE(sessions_ordered, LAG(sessions_ordered) OVER (ORDER BY step_no)), 4) AS step_to_step_conversion,
  ROUND(SAFE_DIVIDE(sessions_ordered, FIRST_VALUE(sessions_ordered) OVER (ORDER BY step_no)), 4) AS conversion_from_entry,
  LAG(sessions_ordered) OVER (ORDER BY step_no) - sessions_ordered AS sessions_lost_at_step,
  ROUND(1 - SAFE_DIVIDE(sessions_ordered, LAG(sessions_ordered) OVER (ORDER BY step_no)), 4) AS dropoff_share,
  (SELECT COUNT(*) FROM s) AS all_valid_sessions
FROM steps
ORDER BY step_no
