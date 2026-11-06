-- Phase 1: overall profile. Date range, events, users, sessions.
WITH base AS (
  SELECT
    PARSE_DATE('%Y%m%d', event_date) AS d,
    user_pseudo_id,
    (SELECT ep.value.int_value FROM UNNEST(event_params) ep WHERE ep.key = 'ga_session_id') AS ga_session_id
  FROM `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`
  WHERE _TABLE_SUFFIX BETWEEN '20201101' AND '20210131'
)
SELECT
  MIN(d) AS first_date,
  MAX(d) AS last_date,
  COUNT(DISTINCT d) AS days_with_data,
  COUNT(*) AS events,
  COUNTIF(user_pseudo_id IS NULL) AS events_null_user,
  COUNTIF(ga_session_id IS NULL) AS events_null_session_id,
  COUNT(DISTINCT user_pseudo_id) AS users,
  COUNT(DISTINCT IF(ga_session_id IS NOT NULL AND user_pseudo_id IS NOT NULL,
        CONCAT(user_pseudo_id, '-', CAST(ga_session_id AS STRING)), NULL)) AS valid_sessions
FROM base
