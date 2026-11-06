-- Phase 2.1: how many sessions skip steps or have steps out of order.
-- For each step: sessions with the event at all (unordered), sessions that reached it in order,
-- and the gap, split into "previous step event is absent" vs "previous step event present but the strict chain is broken (wrong order here, or an earlier step missing or out of order)".
WITH s AS (SELECT * FROM sessions),
x AS (
  SELECT 'view_item' AS step, 2 AS step_no,
    COUNTIF(has_view_item) AS has_step,
    COUNTIF(reach_view_item IS NOT NULL) AS reached_in_order,
    COUNTIF(has_view_item AND reach_view_item IS NULL AND NOT has_entry) AS gap_prev_absent,
    COUNTIF(has_view_item AND reach_view_item IS NULL AND has_entry) AS gap_prev_present_chain_broken FROM s UNION ALL
  SELECT 'add_to_cart', 3, COUNTIF(has_add_to_cart), COUNTIF(reach_add_to_cart IS NOT NULL),
    COUNTIF(has_add_to_cart AND reach_add_to_cart IS NULL AND NOT has_view_item),
    COUNTIF(has_add_to_cart AND reach_add_to_cart IS NULL AND has_view_item) FROM s UNION ALL
  SELECT 'begin_checkout', 4, COUNTIF(has_begin_checkout), COUNTIF(reach_begin_checkout IS NOT NULL),
    COUNTIF(has_begin_checkout AND reach_begin_checkout IS NULL AND NOT has_add_to_cart),
    COUNTIF(has_begin_checkout AND reach_begin_checkout IS NULL AND has_add_to_cart) FROM s UNION ALL
  SELECT 'add_payment_info', 5, COUNTIF(has_add_payment_info), COUNTIF(reach_add_payment_info IS NOT NULL),
    COUNTIF(has_add_payment_info AND reach_add_payment_info IS NULL AND NOT has_begin_checkout),
    COUNTIF(has_add_payment_info AND reach_add_payment_info IS NULL AND has_begin_checkout) FROM s UNION ALL
  SELECT 'purchase', 6, COUNTIF(has_purchase), COUNTIF(reach_purchase IS NOT NULL),
    COUNTIF(has_purchase AND reach_purchase IS NULL AND NOT has_add_payment_info),
    COUNTIF(has_purchase AND reach_purchase IS NULL AND has_add_payment_info) FROM s
)
SELECT step_no, step, has_step, reached_in_order, has_step - reached_in_order AS not_in_order_or_skipped,
       gap_prev_absent, gap_prev_present_chain_broken,
       ROUND(SAFE_DIVIDE(has_step - reached_in_order, has_step), 4) AS share_of_step_sessions_not_in_order
FROM x ORDER BY step_no
