-- Phase 2.4: purchases, revenue, AOV, revenue per user, overall and by segment.
-- Purchases = one event per real transaction id (docs/METRICS.md). Revenue is understated by an
-- unmeasurable amount (906 purchase events have no usable transaction id; see docs/DATA_QUALITY.md).
-- Revenue per user = revenue / distinct users with a valid session in the segment.
WITH top_c AS (
  SELECT country FROM sessions WHERE country != 'Other' GROUP BY country ORDER BY COUNT(*) DESC LIMIT 10
),
s AS (
  SELECT *, IF(session_number = 1, 'new', IF(session_number > 1, 'returning', 'unknown')) AS visitor_type,
         IF(country IN (SELECT country FROM top_c), country, 'Other') AS country_group
  FROM sessions
),
long AS (
  SELECT 'all' AS dimension, 'all sessions' AS segment, user_pseudo_id, ga_session_id FROM s UNION ALL
  SELECT 'device_category', COALESCE(device_category, 'unknown'), user_pseudo_id, ga_session_id FROM s UNION ALL
  SELECT 'traffic_medium (first touch)', medium, user_pseudo_id, ga_session_id FROM s UNION ALL
  SELECT 'country', country_group, user_pseudo_id, ga_session_id FROM s UNION ALL
  SELECT 'visitor_type', visitor_type, user_pseudo_id, ga_session_id FROM s
),
base AS (
  SELECT dimension, segment, COUNT(*) AS sessions, COUNT(DISTINCT user_pseudo_id) AS users
  FROM long GROUP BY dimension, segment
),
pur AS (
  SELECT l.dimension, l.segment, COUNT(*) AS purchases, SUM(p.purchase_revenue) AS revenue,
         COUNT(DISTINCT p.user_pseudo_id) AS buyers
  FROM purchases p JOIN long l ON l.user_pseudo_id = p.user_pseudo_id AND l.ga_session_id = p.ga_session_id
  GROUP BY l.dimension, l.segment
)
SELECT b.dimension, b.segment, b.sessions, b.users, b.sessions >= 100 AS reliable,
  COALESCE(p.purchases, 0) AS purchases, ROUND(COALESCE(p.revenue, 0), 2) AS revenue,
  ROUND(SAFE_DIVIDE(p.revenue, p.purchases), 2) AS aov,
  ROUND(SAFE_DIVIDE(p.revenue, b.users), 4) AS revenue_per_user,
  COALESCE(p.buyers, 0) AS buyers,
  (SELECT COUNT(*) FROM purchases) AS all_purchases_in_table,
  (SELECT ROUND(SUM(purchase_revenue), 2) FROM purchases) AS all_revenue_in_table
FROM base b LEFT JOIN pur p USING (dimension, segment)
ORDER BY b.dimension, revenue DESC
