-- Phase 2.1: for sessions with a purchase event, which earlier steps never appear at all.
SELECT
  COUNT(*) AS sessions_with_purchase,
  COUNTIF(NOT has_entry) AS missing_entry,
  COUNTIF(NOT has_view_item) AS missing_view_item,
  COUNTIF(NOT has_add_to_cart) AS missing_add_to_cart,
  COUNTIF(NOT has_begin_checkout) AS missing_begin_checkout,
  COUNTIF(NOT has_add_payment_info) AS missing_add_payment_info,
  COUNTIF(has_entry AND has_view_item AND has_add_to_cart AND has_begin_checkout AND has_add_payment_info) AS has_all_steps,
  COUNTIF(reach_purchase IS NOT NULL) AS full_ordered_path,
  (SELECT COUNT(*) FROM sessions) AS all_valid_sessions,
  ROUND(SAFE_DIVIDE(COUNT(*), (SELECT COUNT(*) FROM sessions)), 5) AS session_conversion_rate
FROM sessions
WHERE has_purchase
