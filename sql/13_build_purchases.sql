-- Phase 2 build step 4: one row per real transaction id (earliest event), per docs/METRICS.md.
CREATE OR REPLACE TABLE purchases AS
SELECT
  transaction_id,
  ARRAY_AGG(STRUCT(user_pseudo_id, ga_session_id, event_date, purchase_revenue)
            ORDER BY event_timestamp LIMIT 1)[OFFSET(0)].*
FROM events_slim
WHERE event_name = 'purchase'
  AND transaction_id IS NOT NULL
  AND transaction_id NOT IN ('', '(not set)', '<Other>')
GROUP BY transaction_id
