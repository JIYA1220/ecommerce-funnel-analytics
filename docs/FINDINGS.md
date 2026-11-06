# Findings

Google Merchandise Store, GA4 sample data, 2020-11-01 to 2021-01-31 (92 days, 360,129 sessions, 270,154 users). Definitions are in `METRICS.md`, data limits in `DATA_QUALITY.md`. Every number below is in a file under `results/`. This is observational data, so the findings describe patterns and do not prove causes.

Headline: 4,848 of 360,129 sessions had a purchase event, a session conversion rate of 1.35% (`21b_purchase_sessions_missing_steps.csv`). In the strict ordered funnel, 359,815 sessions entered and 2,834 reached purchase, 0.79% (`20_funnel.csv`).

## 1. Most shoppers are lost before they add anything to the cart

Of 359,815 entry sessions, 76,965 viewed an item (21.4%) and 15,162 of those added to cart (19.7%). That is 282,850 sessions lost at the first step and 61,803 more at the second (`20_funnel.csv`). After add to cart the funnel holds up better: 70.7% go from checkout start to payment info and 74.0% from payment info to purchase. Add to cart is the lowest step conversion in every segment except returning visitors, where view item is marginally lower (`22_segment_funnel.csv`).

**Recommendation:** focus on product pages and the step from viewing to adding to cart (price and shipping clarity, size and stock information, photos). **Measure:** add-to-cart rate among sessions with `view_item`, tracked weekly with a Wilson interval, with an A/B test on any product page change.

## 2. Returning visitors convert 4.6 times as often as new visitors

Returning sessions convert at 3.10% (95% CI 2.996% to 3.212%) against 0.68% for new sessions (0.651% to 0.714%). The difference is larger than noise (`23_headline_comparisons.csv`). Returning sessions are 27.5% of sessions but 64.3% of purchases and 66.5% of revenue. Revenue per user is 3.95 for returning and 0.39 for new (`26_revenue_by_segment.csv`). Week 1 retention for the full cohorts ranges from 2.46% to 6.68% (`25_retention_matrix.csv`), so most first-time visitors never come back.

**Recommendation:** give new visitors a reason to return (email or account sign-up, a reminder for viewed items). **Measure:** week 1 retention by cohort and the new-visitor session conversion rate. Note that "new" means new to this data window, and one person on two devices counts twice.

## 3. Sessions reach checkout and purchase without an add-to-cart event: check the tracking

5,145 sessions have `begin_checkout` but no `add_to_cart`, and 2,000 of the 4,848 purchase sessions (41.3%) have no `add_to_cart` event (`21_funnel_skipping.csv`, `21b_purchase_sessions_missing_steps.csv`). Under the strict order rule these sessions drop out of the funnel, so the ordered funnel shows 2,834 purchases against 4,848 sessions that have one. This could be real behaviour (a direct "buy now" path, repeat buyers) or missing events. The data cannot say which.

**Recommendation:** have the analytics team check the cart and checkout event set up before any funnel number is used for targets. **Measure:** the share of purchase sessions with a matching add-to-cart event, expected to rise toward 100% if the gap is a tracking issue.

## 4. How users were first acquired matters, device and country do not separate

By first-touch medium, referral users convert at 1.66% (1.566% to 1.765%) and paid search (cpc) users at 0.98% (0.837% to 1.147%). The difference is larger than noise. By device the highest (mobile, 1.393%) and lowest (tablet, 1.300%) are not distinguishable, and neither are the top and bottom countries (Spain 1.485%, Italy 1.100%) (`23_headline_comparisons.csv`). Medium is the user's first-touch source, not the session source, and 21.2% of events have an unknown medium (`03_missing_values.csv`).

**Recommendation:** review paid search landing pages and targeting, and do not prioritise work by device or country on this evidence. **Measure:** session conversion by medium, using session-level source once it is captured.

## 5. Conversion followed the calendar, so do not credit or blame site changes

Weekly session conversion rose from 1.0% (week of 2020-11-02) to a peak of 1.99% (week of 2020-12-07), and fell to 0.56% in the week of 2021-01-04 (`29_time_patterns.csv`). December converted at 1.59% and January at 0.94%. By weekday, Friday is 1.61% (1.502% to 1.721%) and Sunday 0.95% (0.860% to 1.049%), larger than noise. The data covers one holiday season, so seasonal and promotion effects cannot be separated.

**Recommendation:** compare any change against the same period or a control group, never against the previous weeks. **Measure:** conversion in test and control groups over the same days.

## Also noted

- Google Tracking Hat had 1,458 view sessions and no add-to-cart (CI upper bound 0.26%) against 24.2% for all items. This may be an unavailable product or a tracking fault (`28_low_add_to_cart_products.csv`).
- Apparel gave 47.0% of item revenue, and the top product gave 3.4% (`27_top_products_categories.csv`).

## What this data cannot tell us

- **Causes.** It is a one-time observation, with no experiment.
- **Session-level channel.** Traffic source is first-touch, and 21% is unknown.
- **True revenue and orders.** 906 purchase events have no usable transaction id, so revenue (307,640 over 4,451 orders, AOV 69.12) is understated by an unknown amount.
- **People.** A user id is a browser or device.
- **Other times and stores.** It is one store, three months, a holiday season, and obfuscated by Google.
- **Why sessions skip add to cart.** Real behaviour or missing events cannot be told apart here.
- **Costs and margins.** There is no cost or profit data.
