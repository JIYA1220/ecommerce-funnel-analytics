-- Phase 2.4: top 10 products and categories by item revenue (purchase events, one event per real
-- transaction id). Rows with unusable item fields are shown as 'unknown'.
WITH pi AS (
  SELECT *, MIN(event_timestamp) OVER (PARTITION BY transaction_id) AS first_ts
  FROM item_events
  WHERE event_name = 'purchase' AND transaction_id IS NOT NULL
    AND transaction_id NOT IN ('', '(not set)', '<Other>')
),
d AS (
  SELECT transaction_id,
    IF(item_name IS NULL OR item_name IN ('', '(not set)'), 'unknown', item_name) AS item_name,
    IF(item_category IS NULL OR item_category IN ('', '(not set)'), 'unknown', item_category) AS item_category,
    quantity, item_revenue
  FROM pi WHERE event_timestamp = first_ts
),
prod AS (
  SELECT 'product' AS kind, item_name AS name, SUM(item_revenue) AS item_revenue, SUM(quantity) AS units,
         COUNT(DISTINCT transaction_id) AS transactions FROM d GROUP BY item_name
),
cat AS (
  SELECT 'category' AS kind, item_category AS name, SUM(item_revenue) AS item_revenue, SUM(quantity) AS units,
         COUNT(DISTINCT transaction_id) AS transactions FROM d GROUP BY item_category
),
allr AS (SELECT * FROM prod UNION ALL SELECT * FROM cat),
ranked AS (
  SELECT *, ROW_NUMBER() OVER (PARTITION BY kind ORDER BY item_revenue DESC) AS rnk,
         SUM(item_revenue) OVER (PARTITION BY kind) AS kind_total_item_revenue
  FROM allr
)
SELECT kind, rnk AS rank, name, ROUND(item_revenue, 2) AS item_revenue, units, transactions,
       ROUND(item_revenue / kind_total_item_revenue, 4) AS share_of_item_revenue,
       ROUND(kind_total_item_revenue, 2) AS total_item_revenue
FROM ranked WHERE rnk <= 10 ORDER BY kind, rnk
