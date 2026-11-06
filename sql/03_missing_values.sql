-- Phase 1: share of null, empty, '(data deleted)', '(not set)', '<Other>' in key event-level fields.
WITH e AS (
  SELECT
    traffic_source.source AS ts_source,
    traffic_source.medium AS ts_medium,
    traffic_source.name AS ts_name,
    device.category AS device_category,
    device.operating_system AS os,
    geo.country AS country,
    geo.city AS city
  FROM `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`
  WHERE _TABLE_SUFFIX BETWEEN '20201101' AND '20210131'
),
long AS (
  SELECT 'traffic_source.source' AS field, ts_source AS v FROM e UNION ALL
  SELECT 'traffic_source.medium', ts_medium FROM e UNION ALL
  SELECT 'traffic_source.name', ts_name FROM e UNION ALL
  SELECT 'device.category', device_category FROM e UNION ALL
  SELECT 'device.operating_system', os FROM e UNION ALL
  SELECT 'geo.country', country FROM e UNION ALL
  SELECT 'geo.city', city FROM e
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
