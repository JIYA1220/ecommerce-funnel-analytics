-- Phase 1: how purchase events split by transaction id quality, and duplicates among real ids.
WITH p AS (
  SELECT
    ecommerce.transaction_id AS tid,
    ecommerce.purchase_revenue AS revenue,
    CASE
      WHEN ecommerce.transaction_id IS NULL THEN 'null'
      WHEN ecommerce.transaction_id IN ('', '(not set)', '<Other>') THEN 'placeholder'
      ELSE 'real'
    END AS tid_class
  FROM `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`
  WHERE _TABLE_SUFFIX BETWEEN '20201101' AND '20210131'
    AND event_name = 'purchase'
),
real_ids AS (
  SELECT tid, COUNT(*) AS n_events, COUNT(DISTINCT revenue) AS n_distinct_revenue,
         LOGICAL_OR(revenue IS NULL) AS any_null_revenue
  FROM p WHERE tid_class = 'real' GROUP BY tid
)
SELECT 'events: tid real' AS measure, COUNTIF(tid_class = 'real') AS value FROM p UNION ALL
SELECT 'events: tid placeholder', COUNTIF(tid_class = 'placeholder') FROM p UNION ALL
SELECT 'events: tid null', COUNTIF(tid_class = 'null') FROM p UNION ALL
SELECT 'events: tid placeholder, revenue null', COUNTIF(tid_class = 'placeholder' AND revenue IS NULL) FROM p UNION ALL
SELECT 'events: tid null, revenue null', COUNTIF(tid_class = 'null' AND revenue IS NULL) FROM p UNION ALL
SELECT 'events: tid real, revenue null', COUNTIF(tid_class = 'real' AND revenue IS NULL) FROM p UNION ALL
SELECT 'real tids: distinct', COUNT(*) FROM real_ids UNION ALL
SELECT 'real tids: with more than 1 event', COUNTIF(n_events > 1) FROM real_ids UNION ALL
SELECT 'real tids: extra duplicate events', SUM(n_events - 1) FROM real_ids UNION ALL
SELECT 'real tids: duplicates with differing revenue', COUNTIF(n_events > 1 AND n_distinct_revenue > 1) FROM real_ids UNION ALL
SELECT 'real tids: all events revenue null', COUNTIF(any_null_revenue AND n_distinct_revenue = 0) FROM real_ids
