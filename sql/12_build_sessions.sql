-- Phase 2 build step 3: one row per valid session (see docs/METRICS.md).
-- Funnel reach times follow the strict order rule: reach time of step k is the earliest step k
-- event at or after the reach time of step k-1. NULL means the step was not reached in order.
-- has_* columns are the unordered flags (never NULL; ARRAY_AGG IGNORE NULLS returns a NULL array when empty, hence COALESCE) (event present at least once in the session).
CREATE OR REPLACE TABLE sessions AS
WITH valid AS (
  SELECT * FROM events_slim WHERE user_pseudo_id IS NOT NULL AND ga_session_id IS NOT NULL
),
agg AS (
  SELECT
    user_pseudo_id,
    ga_session_id,
    ARRAY_AGG(event_date ORDER BY event_timestamp LIMIT 1)[OFFSET(0)] AS session_date,
    MIN(event_timestamp) AS session_first_ts,
    MAX(ga_session_number) AS session_number,
    ARRAY_AGG(device_category ORDER BY event_timestamp LIMIT 1)[OFFSET(0)] AS device_category,
    ARRAY_AGG(medium ORDER BY event_timestamp LIMIT 1)[OFFSET(0)] AS medium_raw,
    ARRAY_AGG(country ORDER BY event_timestamp LIMIT 1)[OFFSET(0)] AS country_raw,
    COUNT(*) AS n_events,
    ARRAY_AGG(IF(event_name IN ('session_start', 'page_view'), event_timestamp, NULL) IGNORE NULLS) AS a_entry,
    ARRAY_AGG(IF(event_name = 'view_item', event_timestamp, NULL) IGNORE NULLS) AS a_view_item,
    ARRAY_AGG(IF(event_name = 'add_to_cart', event_timestamp, NULL) IGNORE NULLS) AS a_add_to_cart,
    ARRAY_AGG(IF(event_name = 'begin_checkout', event_timestamp, NULL) IGNORE NULLS) AS a_begin_checkout,
    ARRAY_AGG(IF(event_name = 'add_payment_info', event_timestamp, NULL) IGNORE NULLS) AS a_add_payment_info,
    ARRAY_AGG(IF(event_name = 'purchase', event_timestamp, NULL) IGNORE NULLS) AS a_purchase,
    COUNTIF(event_name = 'add_shipping_info') AS n_add_shipping_info,
    COUNTIF(event_name = 'purchase') AS n_purchase_events
  FROM valid
  GROUP BY user_pseudo_id, ga_session_id
),
r1 AS (SELECT *, (SELECT MIN(x) FROM UNNEST(a_entry) x) AS reach_entry FROM agg),
r2 AS (SELECT *, (SELECT MIN(x) FROM UNNEST(a_view_item) x WHERE x >= reach_entry) AS reach_view_item FROM r1),
r3 AS (SELECT *, (SELECT MIN(x) FROM UNNEST(a_add_to_cart) x WHERE x >= reach_view_item) AS reach_add_to_cart FROM r2),
r4 AS (SELECT *, (SELECT MIN(x) FROM UNNEST(a_begin_checkout) x WHERE x >= reach_add_to_cart) AS reach_begin_checkout FROM r3),
r5 AS (SELECT *, (SELECT MIN(x) FROM UNNEST(a_add_payment_info) x WHERE x >= reach_begin_checkout) AS reach_add_payment_info FROM r4),
r6 AS (SELECT *, (SELECT MIN(x) FROM UNNEST(a_purchase) x WHERE x >= reach_add_payment_info) AS reach_purchase FROM r5)
SELECT
  user_pseudo_id, ga_session_id, session_date, session_first_ts, session_number,
  device_category,
  IF(medium_raw IS NULL OR medium_raw IN ('', '(data deleted)', '<Other>'), 'unknown', medium_raw) AS medium,
  IF(country_raw IS NULL OR country_raw IN ('', '(not set)'), 'Other', country_raw) AS country,
  n_events,
  COALESCE(ARRAY_LENGTH(a_entry), 0) > 0 AS has_entry,
  COALESCE(ARRAY_LENGTH(a_view_item), 0) > 0 AS has_view_item,
  COALESCE(ARRAY_LENGTH(a_add_to_cart), 0) > 0 AS has_add_to_cart,
  COALESCE(ARRAY_LENGTH(a_begin_checkout), 0) > 0 AS has_begin_checkout,
  COALESCE(ARRAY_LENGTH(a_add_payment_info), 0) > 0 AS has_add_payment_info,
  COALESCE(ARRAY_LENGTH(a_purchase), 0) > 0 AS has_purchase,
  n_add_shipping_info, n_purchase_events,
  reach_entry, reach_view_item, reach_add_to_cart, reach_begin_checkout, reach_add_payment_info, reach_purchase
FROM r6
