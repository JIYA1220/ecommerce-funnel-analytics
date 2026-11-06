# Data quality

What is usable, what is not, and how each analysis handles it. All numbers come from the files in `results/` named in each row. Shares are of **events** (rows in `events_*`), not of users or sessions, unless stated. Metric definitions are in `METRICS.md`.

## Summary

| Area | Verdict |
|---|---|
| User id, session id | Usable. No nulls in 4,295,584 events. |
| Event names | Usable. 17 event names; all six funnel events exist. |
| Device category | Usable. No placeholders. |
| Country | Usable. 0.75% `(not set)`. |
| City | Not used. 41.8% `(not set)`. |
| Traffic source, medium, name | Use with care. 21% to 34% placeholder, and it is first-touch, not per session. |
| Items (id, name, category) | Usable. 3% to 4% unusable. |
| Purchase counts | Usable at session level. |
| Revenue and AOV | Partly usable. Understated, see below. |

## Field by field

Source: `results/01_profile_overview.csv`, `results/03_missing_values.csv`, `results/04_missing_values_items.csv`.

| Field | Rows | Unusable share | What the unusable values are | Handling |
|---|---|---|---|---|
| `user_pseudo_id` | 4,295,584 | 0% | none | Used as is. |
| `ga_session_id` (event_params) | 4,295,584 | 0% | none | Used with `user_pseudo_id` as the session key. |
| `device.category` | 4,295,584 | 0.00% | none | Used as a segment. |
| `device.operating_system` | 4,295,584 | 2.57% | `<Other>` 110,323 | Not used for segments. |
| `geo.country` | 4,295,584 | 0.75% | `(not set)` 32,208 | Top 10 countries plus "Other". `(not set)` is grouped into "Other". |
| `geo.city` | 4,295,584 | 41.80% | `(not set)` 1,795,444 | Not used. |
| `traffic_source.medium` | 4,295,584 | 21.22% | `(data deleted)` 313,917; `<Other>` 597,482 | Used as a segment with an explicit "unknown" group for these values. Reported separately, never merged into a real medium. |
| `traffic_source.source` | 4,295,584 | 33.52% | `(data deleted)` 308,695; `<Other>` 1,131,013 | Not used as a segment. Too much is unknown. |
| `traffic_source.name` | 4,295,584 | 25.34% | `(data deleted)` 306,045; `<Other>` 782,379 | Not used. |
| `items.item_id` | 3,982,732 item rows | 3.28% | `(not set)` 130,641 | Used. Unusable rows are dropped from product tables and the count is reported. |
| `items.item_name` | 3,982,732 | 3.73% | `(not set)` 148,458 | Same. |
| `items.item_category` | 3,982,732 | 4.14% | empty 16,397; `(not set)` 148,459 | Same. Category tables show an "unknown" row. |

## Things to know before reading any result

1. **Traffic source is first-touch.** In the GA4 export, `traffic_source` describes how the user was first acquired, not where the current session came from. A segment by medium answers "how were these users first acquired", not "which channel drove this session". Findings must be worded that way.
2. **"Unknown" medium is large.** 21.22% of events have a medium that is `(data deleted)` or `<Other>`. Comparisons across mediums leave out this group or show it separately.
3. **Obfuscation.** Google says internal consistency is limited. Totals should not be compared with Google's separate demo account.
4. **Window edges.** The data starts on 2020-11-01. "New" users and cohort start weeks are relative to the window, not to the business.
5. **Session start events.** There are 354,970 `session_start` events (`results/02_event_names.csv`) and 360,129 valid sessions (`results/01_profile_overview.csv`), so about 5,159 more sessions than `session_start` events. Some sessions may have started before the window or the event may be missing. The funnel entry step is therefore `session_start` or `page_view`, as in `METRICS.md`.
6. **Extra funnel event.** `add_shipping_info` exists (19,722 events) between `begin_checkout` and `add_payment_info`. It is not one of the funnel steps requested for this project, so it is not a step, but it is mentioned where relevant.

## Purchases, revenue and duplicates

Source: `results/05_purchase_quality.csv` and `results/06_purchase_dedup.csv`.

| Measure | Value |
|---|---|
| Purchase events | 5,692 |
| Buyers (distinct users with a purchase) | 4,419 |
| Events with a real transaction id | 4,786 |
| Events with placeholder transaction id | 883 |
| Events with null transaction id | 23 |
| Distinct real transaction ids | 4,451 |
| Real ids that appear in more than 1 event | 326 |
| Extra duplicate events among real ids | 335 |
| Real ids whose duplicates have different revenue values | 15 |
| Events with null revenue | 450 (all of them have a placeholder transaction id) |
| Zero or negative revenue | 0 |
| Revenue range, median (per event) | 1.0 to 1530.0, median 48.0 |

How each analysis handles this:

- **Conversion rates** count sessions with at least one `purchase` event. They do not depend on the transaction id, so duplicate events and missing ids do not change them.
- **Purchases, revenue, AOV, revenue per user** use only events with a real transaction id, one event per id (the earliest by `event_timestamp`). For the 15 ids with differing revenue, the earliest event is used, and this choice is stated wherever it matters.
- Events with a placeholder or null transaction id (906 events, 883 + 23) cannot be de-duplicated, so they are left out of revenue. Of the 883 placeholder events, 450 also have null revenue. This means revenue and AOV are **understated, and the size of the gap is not measurable** from this data. Any revenue number in this project carries that note.
- Purchase events are 5,692 but real distinct transaction ids are 4,451. Purchase counts based on events would be overstated by duplicates, so event counts are never reported as "orders".

## Item ids differ between event types

Item ids in `purchase` events are numeric (for example `9195292`), while `view_item` and `add_to_cart` events use another scheme (for example `GGOEG...`). Joining views to purchases on `item_id` would put 305,014 of 307,562 item revenue on products with no views (measured while building `sql/31_product_table.sql`). Product tables that combine views, carts and revenue therefore use `item_name`. After joining by name, 8 of 390 purchased products have no views (12,039 item revenue, `results/31_product_table.csv`). Product add-to-cart rates in `sql/28_*.sql` compare view and cart events only, which share one id scheme.

## What is not usable

- City level analysis.
- Source level and campaign name level analysis.
- Operating system analysis (kept out for focus, not because it is bad).
- Exact order counts and exact revenue (see above).
- Any claim about individual people. A user id is a browser or device.
