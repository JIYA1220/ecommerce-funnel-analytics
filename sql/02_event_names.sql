-- Phase 1: event names, counts and distinct users.
SELECT
  event_name,
  COUNT(*) AS events,
  COUNT(DISTINCT user_pseudo_id) AS users,
  ROUND(100 * COUNT(*) / SUM(COUNT(*)) OVER (), 3) AS pct_of_events
FROM `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`
WHERE _TABLE_SUFFIX BETWEEN '20201101' AND '20210131'
GROUP BY event_name
ORDER BY events DESC
