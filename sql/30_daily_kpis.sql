-- Phase 3: daily KPIs for the dashboard. One row per session date.
-- Sessions are dated by their first event. Purchases and revenue are dated by the purchase event
-- (one event per real transaction id, see docs/METRICS.md), so a late-night session can sit on a
-- different day from its purchase. Distinct users are NOT included because they cannot be summed over days.
WITH s AS (
  SELECT session_date AS date,
         COUNT(*) AS sessions,
         COUNTIF(session_number = 1) AS new_sessions,
         COUNTIF(session_number > 1) AS returning_sessions,
         COUNTIF(has_purchase) AS sessions_with_purchase
  FROM sessions GROUP BY session_date
),
p AS (
  SELECT event_date AS date, COUNT(*) AS purchases, SUM(purchase_revenue) AS revenue
  FROM purchases GROUP BY event_date
)
SELECT s.date, s.sessions, s.new_sessions, s.returning_sessions, s.sessions_with_purchase,
       COALESCE(p.purchases, 0) AS purchases, ROUND(COALESCE(p.revenue, 0), 2) AS revenue
FROM s LEFT JOIN p USING (date)
ORDER BY s.date
