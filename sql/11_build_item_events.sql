-- Phase 2 build step 2: one row per item per item-level event (view_item, add_to_cart, purchase),
-- with the session key. Creates table funnel.item_events.
CREATE OR REPLACE TABLE item_events AS
SELECT
  user_pseudo_id,
  (SELECT ep.value.int_value FROM UNNEST(event_params) ep WHERE ep.key = 'ga_session_id') AS ga_session_id,
  event_timestamp,
  event_name,
  ecommerce.transaction_id AS transaction_id,
  i.item_id,
  i.item_name,
  i.item_category,
  i.quantity,
  i.item_revenue
FROM `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`, UNNEST(items) i
WHERE _TABLE_SUFFIX BETWEEN '20201101' AND '20210131'
  AND event_name IN ('view_item', 'add_to_cart', 'purchase')
