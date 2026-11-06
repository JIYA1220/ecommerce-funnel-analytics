-- Phase 3: product table for the dashboard. One row per item_name.
-- Why name and not item_id: item ids in purchase events (numeric, like 9195292) are a different id
-- scheme from the ids in view_item and add_to_cart events (like GGOEG...), so joining on id would put
-- almost all revenue on products with no views. Names match across event types.
-- Views and add-to-cart are session based (same definitions as sql/28_*.sql, grouped by name).
-- Revenue, units and transactions come from purchase events with a real transaction id, one event per id.
-- Unusable names ('(not set)', empty, null) are grouped as 'unknown'. If one name has several ids
-- (variants), they are counted together.
WITH ev AS (
  SELECT user_pseudo_id, ga_session_id,
         IF(item_name IS NULL OR item_name IN ('', '(not set)'), 'unknown', item_name) AS item_name,
         LOGICAL_OR(event_name = 'view_item') AS viewed,
         LOGICAL_OR(event_name = 'add_to_cart') AS carted
  FROM item_events
  WHERE event_name IN ('view_item', 'add_to_cart') AND ga_session_id IS NOT NULL
  GROUP BY user_pseudo_id, ga_session_id, item_name
),
per_item AS (
  SELECT item_name, COUNTIF(viewed) AS view_sessions, COUNTIF(viewed AND carted) AS viewed_and_carted
  FROM ev GROUP BY item_name
),
pi AS (
  SELECT *, MIN(event_timestamp) OVER (PARTITION BY transaction_id) AS first_ts
  FROM item_events
  WHERE event_name = 'purchase' AND transaction_id IS NOT NULL
    AND transaction_id NOT IN ('', '(not set)', '<Other>')
),
bought AS (
  SELECT IF(item_name IS NULL OR item_name IN ('', '(not set)'), 'unknown', item_name) AS item_name,
         ANY_VALUE(IF(item_category IS NULL OR item_category IN ('', '(not set)'), 'unknown', item_category)) AS item_category,
         ROUND(SUM(item_revenue), 2) AS item_revenue, SUM(quantity) AS units,
         COUNT(DISTINCT transaction_id) AS transactions
  FROM pi WHERE event_timestamp = first_ts GROUP BY 1
)
SELECT COALESCE(v.item_name, b.item_name) AS item_name,
       COALESCE(b.item_category, 'unknown') AS item_category,
       COALESCE(v.view_sessions, 0) AS view_sessions,
       COALESCE(v.viewed_and_carted, 0) AS viewed_and_carted,
       COALESCE(b.item_revenue, 0) AS item_revenue,
       COALESCE(b.units, 0) AS units,
       COALESCE(b.transactions, 0) AS transactions
FROM per_item v FULL OUTER JOIN bought b ON v.item_name = b.item_name
ORDER BY item_revenue DESC, view_sessions DESC
