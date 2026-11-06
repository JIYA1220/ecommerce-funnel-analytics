-- Phase 1: placeholder shares in item fields, and transaction id / revenue quality on purchase events.
WITH it AS (
  SELECT i.item_id, i.item_name, i.item_category, i.price
  FROM `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`, UNNEST(items) i
  WHERE _TABLE_SUFFIX BETWEEN '20201101' AND '20210131'
),
long AS (
  SELECT 'items.item_id' AS field, item_id AS v FROM it UNION ALL
  SELECT 'items.item_name', item_name FROM it UNION ALL
  SELECT 'items.item_category', item_category FROM it
)
SELECT
  field,
  COUNT(*) AS rows_total,
  COUNTIF(v IS NULL) AS null_n,
  COUNTIF(v = '') AS empty_n,
  COUNTIF(v = '(data deleted)') AS data_deleted_n,
  COUNTIF(v = '(not set)') AS not_set_n,
  COUNTIF(v = '<Other>') AS other_placeholder_n,
  ROUND(100 * COUNTIF(v IS NULL OR v IN ('', '(data deleted)', '(not set)', '<Other>')) / COUNT(*), 2) AS pct_unusable
FROM long
GROUP BY field
ORDER BY field
