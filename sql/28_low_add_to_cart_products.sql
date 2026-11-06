-- Phase 2.4: products with many views but a low add-to-cart rate.
-- Item add-to-cart rate = sessions with view_item AND add_to_cart for the item (same session, any order)
-- / sessions with view_item for the item. Only items with >= 500 view sessions. Wilson 95% interval.
CREATE TEMP FUNCTION wlo(x INT64, n INT64) AS (IF(n = 0, NULL,
  ((x / n + 1.96 * 1.96 / (2 * n)) - 1.96 * SQRT((x / n) * (1 - x / n) / n + 1.96 * 1.96 / (4 * n * n))) / (1 + 1.96 * 1.96 / n)));
CREATE TEMP FUNCTION whi(x INT64, n INT64) AS (IF(n = 0, NULL,
  ((x / n + 1.96 * 1.96 / (2 * n)) + 1.96 * SQRT((x / n) * (1 - x / n) / n + 1.96 * 1.96 / (4 * n * n))) / (1 + 1.96 * 1.96 / n)));
WITH ev AS (
  SELECT user_pseudo_id, ga_session_id, item_id,
         ANY_VALUE(IF(item_name IS NULL OR item_name IN ('', '(not set)'), 'unknown', item_name)) AS item_name,
         LOGICAL_OR(event_name = 'view_item') AS viewed,
         LOGICAL_OR(event_name = 'add_to_cart') AS carted
  FROM item_events
  WHERE event_name IN ('view_item', 'add_to_cart') AND item_id IS NOT NULL AND item_id != '(not set)'
    AND ga_session_id IS NOT NULL
  GROUP BY user_pseudo_id, ga_session_id, item_id
),
per_item AS (
  SELECT item_id, ANY_VALUE(item_name) AS item_name,
         COUNTIF(viewed) AS view_sessions, COUNTIF(viewed AND carted) AS viewed_and_carted
  FROM ev GROUP BY item_id
),
site AS (SELECT SUM(viewed_and_carted) / SUM(view_sessions) AS site_rate FROM per_item)
SELECT item_id, item_name, view_sessions, viewed_and_carted,
       ROUND(viewed_and_carted / view_sessions, 4) AS add_to_cart_rate,
       ROUND(wlo(viewed_and_carted, view_sessions), 4) AS ci_low,
       ROUND(whi(viewed_and_carted, view_sessions), 4) AS ci_high,
       ROUND(site.site_rate, 4) AS all_items_rate,
       whi(viewed_and_carted, view_sessions) < site.site_rate AS clearly_below_all_items_rate
FROM per_item CROSS JOIN site
WHERE view_sessions >= 500
ORDER BY add_to_cart_rate ASC
LIMIT 20
