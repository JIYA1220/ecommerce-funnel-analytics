# Metric definitions

Written in Phase 1 before any metric is computed. Phase 2 queries must follow these exactly. If a definition has to change, it is changed here first and the reason is noted at the bottom.

Source: `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*`, 2020-11-01 to 2021-01-31.

## Building blocks

| Term | Definition |
|---|---|
| Event | One row in `events_*`. |
| User | A distinct `user_pseudo_id`. This is a browser or device id, not a person. One person on two devices counts twice. |
| Session | A distinct pair (`user_pseudo_id`, `ga_session_id`). `ga_session_id` is read from `event_params` where `key = 'ga_session_id'` (`value.int_value`). `ga_session_id` alone is a timestamp and is not unique across users. |
| Valid session | A session where both parts of the key are present. Events without a `ga_session_id` are excluded from every session metric and counted separately in the profile. |
| Session date | The date of the first event in the session (by `event_timestamp`). |
| New session | A session whose `ga_session_number` event param equals 1. |
| Returning session | A session whose `ga_session_number` is greater than 1. Missing means "unknown". "New" here means new within what the data records for that browser, not new to the business. |

## Funnel

Steps, in order:

1. **Entry**: the session has a `session_start` or a `page_view` event.
2. **View item**: `view_item`
3. **Add to cart**: `add_to_cart`
4. **Begin checkout**: `begin_checkout`
5. **Add payment info**: `add_payment_info`
6. **Purchase**: `purchase`

**Order rule (strict funnel).** A session reaches step k only if it reached step k-1 and has a step k event whose `event_timestamp` is greater than or equal to the earliest timestamp of step k-1 in the same session. Ties are allowed because GA4 can stamp several events with the same microsecond. Counts in the main funnel use this rule.

**Unordered counts (for comparison).** The number of sessions that have each event at least once, ignoring order.

**Skipping.** A session "skips" if it has a later step event but did not reach the earlier step under the order rule. For example, a `purchase` with no `begin_checkout`. Phase 2 reports how many sessions do this.

## Conversion metrics

| Metric | Formula |
|---|---|
| Step-to-step conversion (step k) | sessions reaching step k / sessions reaching step k-1 |
| Drop-off at step k | 1 - step-to-step conversion at step k (as a share), and the count lost: sessions reaching k-1 minus sessions reaching k |
| Overall funnel conversion | sessions reaching purchase / sessions reaching Entry |
| Session conversion rate | sessions with at least one `purchase` event / all valid sessions |
| User conversion rate | users with at least one `purchase` event / all users with a valid session |
| Add-to-cart rate (product) | sessions with both `view_item` and `add_to_cart` for the item (same session, any order) / sessions with `view_item` for the item |

The session conversion rate uses all valid sessions as the base. The overall funnel conversion uses sessions reaching Entry as the base. These can differ slightly. Both are labeled where used.

## Revenue metrics

| Metric | Formula |
|---|---|
| Purchases | distinct real `ecommerce.transaction_id` among `purchase` events. A real id is not null and not `''`, `(not set)` or `<Other>`. Events without a real id are excluded from purchase counts and revenue (906 events in Phase 1, see `DATA_QUALITY.md`). |
| Revenue | sum of `ecommerce.purchase_revenue` (USD) over those purchases, one event per transaction id (the earliest by `event_timestamp`). Understated by an unmeasurable amount. |
| Average order value (AOV) | revenue / purchases |
| Revenue per user | revenue / distinct users in the same segment (all users with a valid session, buyers or not) |
| Item revenue | sum of `items.item_revenue` over purchase events |

## Segments

| Segment | Field | Notes |
|---|---|---|
| Device category | `device.category` | |
| Traffic medium | `traffic_source.medium` | In this export this is the user's first-touch acquisition source, not the source of the current session. Segments by medium describe how users were first acquired. |
| Country | `geo.country` | Top 10 by session count, rest grouped as "Other". |
| New vs returning | `ga_session_number` | See above. |

A session takes the segment value from its first event. A segment with fewer than 100 sessions is marked **unreliable** and not used for conclusions.

## Cohort retention

| Term | Definition |
|---|---|
| Cohort week | The week (starting Monday) of a user's first valid session in the data window. |
| Retention week N | Users in the cohort with at least one valid session in cohort week + N, divided by cohort size. Week 0 is 100% by definition. |
| Edge effect | The window starts on 2020-11-01, so users first seen in the first week may have visited before. The last cohorts have fewer weeks of follow-up and are shown as blank, not 0%. |

## Statistical care

- Confidence interval for any rate: Wilson 95% interval.
- Difference between two segments: reported as "larger than noise" only when the two Wilson intervals do not overlap. Otherwise "not distinguishable from noise".
- No causal claims. The data is observational.
- Segments under 100 sessions are labeled unreliable.

## Time patterns

- Day of week and week are taken from the session date. Weeks start on Monday.
- November and December include Black Friday and the holiday season. Changes over time are not attributed to causes without a control.

## Change log

- Phase 1: first version.
- Phase 1 (after profiling): purchase and revenue definitions now exclude events without a real transaction id and keep one event per id, because 5,692 purchase events map to 4,451 real ids plus 906 events with no usable id.
- Phase 2: product add-to-cart rate now counts only sessions that also viewed the item, so the rate stays between 0 and 100%.
- Phase 2: in `sql/21_funnel_skipping.sql`, "chain broken" means the previous step event exists but the strict chain is broken (wrong order here, or an earlier step missing or out of order).
- Phase 2: reach time of step k is the earliest step k event at or after the reach time of step k-1 (clarifies the order rule).
