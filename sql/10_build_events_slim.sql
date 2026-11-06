-- Phase 2 build step 1: narrow copy of the events (one row per event) with the session key,
-- session number and first-touch segment fields extracted once, so later queries are small.
-- Creates table funnel.events_slim in the Sandbox project (free).
CREATE OR REPLACE TABLE events_slim AS
SELECT
  user_pseudo_id,
  (SELECT ep.value.int_value FROM UNNEST(event_params) ep WHERE ep.key = 'ga_session_id') AS ga_session_id,
  (SELECT ep.value.int_value FROM UNNEST(event_params) ep WHERE ep.key = 'ga_session_number') AS ga_session_number,
  event_timestamp,
  PARSE_DATE('%Y%m%d', event_date) AS event_date,
  event_name,
  device.category AS device_category,
  traffic_source.medium AS medium,
  geo.country AS country,
  ecommerce.transaction_id AS transaction_id,
  ecommerce.purchase_revenue AS purchase_revenue
FROM `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`
WHERE _TABLE_SUFFIX BETWEEN '20201101' AND '20210131'
