# Executive summary: Merchandise Store funnel

For: head of e-commerce, marketing, product, operations, finance. Period: 2020-11-01 to 2021-01-31 (Google Merchandise Store sample data, 92 days). Details and sources: `BUSINESS_CASE.md`. Every number is in `results/`.

## The short version

Most shoppers leave before they buy. Of 359,815 sessions that entered the store, 76,965 looked at a product, 15,162 added something to the cart, and 2,834 bought. That is under 1 in 100 sessions (0.79%). Shoppers are lost mainly early, at the product page, and not at checkout.

## What we found

1. **The biggest loss is before the cart.** 282,850 sessions never viewed a product, and 61,803 more viewed one but did not add it to the cart. Checkout loses 2,582 sessions, which is fewer, though almost half of the sessions that start checkout do not finish (47.7%).
2. **Returning visitors are worth far more.** They convert at 3.10%, new visitors at 0.68%. Returning visitors are 27.5% of sessions and 66.5% of revenue. But only 2.5% to 6.7% of first-time visitors come back the next week.
3. **Our tracking has a gap.** 2,000 of 4,848 sessions with a purchase have no add-to-cart event. We cannot tell if shoppers really skip the cart or if events are missing. Until this is checked, funnel numbers are uncertain.
4. **Revenue is understated.** 307,640 from 4,451 orders (average order 69.12). 906 purchase events have no usable order number, so true revenue is higher by an amount we cannot measure.

## What it could be worth (scenarios, not forecasts)

If one step improved, with everything else the same, over the same 92 days:

| If this improved | By | Extra revenue | Share of revenue |
|---|---|---|---|
| Add to cart rate | 1 point | 9,943 | 3.2% |
| Add to cart rate | 5 points | 49,716 | 16.2% |
| Checkout completion | 2 points | 7,487 | 2.4% |
| Checkout completion | 5 points | 18,717 | 6.1% |

These assume extra orders are worth the average order and later steps stay as they are. We have no cost data, so there is no return on investment figure.

## What we recommend

1. **Fix the tracking and build a funnel monitoring dashboard first** (low cost). It shows drops within a day and tells us if later changes work. Requirements are in `BRD.md`.
2. **Test product page changes** (price, shipping, stock and size information) with A/B tests, starting with products that have many views and few carts.
3. **Pilot a returning visitor programme** (email, reminders for viewed items).
4. **Wait on checkout work** until the dashboard shows where checkout is weakest.

## What we need from you

- Name an owner for each metric (proposed owners are in `KPI_TREE.md`).
- Approve the tracking check and the dashboard scope.
- Agree on the alert rule and who responds.

## Limits to keep in mind

This is one store, three months over a holiday season, and the data is obfuscated by Google. It shows patterns, not causes. Acquisition source is first-touch only, and 21% of it is unknown. Scenario amounts are for 92 days, not a full year.
