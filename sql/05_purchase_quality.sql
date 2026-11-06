-- Phase 1: quality of purchase events: transaction ids, duplicates, revenue values.
WITH p AS (
  SELECT
    user_pseudo_id,
    ecommerce.transaction_id AS tid,
    ecommerce.purchase_revenue AS revenue,
    ecommerce.total_item_quantity AS qty
  FROM `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`
  WHERE _TABLE_SUFFIX BETWEEN '20201101' AND '20210131'
    AND event_name = 'purchase'
)
SELECT
  COUNT(*) AS purchase_events,
  COUNT(DISTINCT tid) AS distinct_transaction_ids,
  COUNTIF(tid IS NULL) AS null_tid,
  COUNTIF(tid IN ('', '(not set)', '<Other>')) AS placeholder_tid,
  COUNTIF(revenue IS NULL) AS null_revenue,
  COUNTIF(revenue = 0) AS zero_revenue,
  COUNTIF(revenue < 0) AS negative_revenue,
  MIN(revenue) AS min_revenue,
  MAX(revenue) AS max_revenue,
  APPROX_QUANTILES(revenue, 100)[OFFSET(50)] AS median_revenue,
  COUNT(DISTINCT user_pseudo_id) AS buyers
FROM p
