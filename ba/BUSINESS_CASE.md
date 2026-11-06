# Business case: closing the gap between product view and purchase

Question: **The Google Merchandise Store loses most shoppers between product view and purchase. What should the business change, and what should be built to track it?**

Data: GA4 sample e-commerce data, 2020-11-01 to 2021-01-31 (92 days, obfuscated). Every number cites its file in `results/`. Scenarios are labeled as scenarios, not forecasts. Assumptions are labeled as assumptions. Money is in US dollars, as in the data.

## 1. Problem statement

Of every 100 sessions that enter the store, about 21 view a product, about 4 add something to the cart and fewer than 1 reaches purchase. The business has no single place that shows where shoppers drop, which segments drop more, or whether a change helped. Tracking also has gaps, so even the funnel itself is not fully trusted.

## 2. Stakeholders

| Stakeholder | What they care about | What they need from this work |
|---|---|---|
| Marketing | Quality of traffic, return visits | Conversion by acquisition source, new vs returning, retention |
| Product (site and UX) | Product page, cart and checkout experience | Step conversion, drop-off by step, product level add-to-cart rates |
| E-commerce operations | Catalogue, stock, promotions, orders | Products with many views and few carts, top sellers, order counts |
| Finance | Revenue and margin | Reliable revenue and order counts, size of the opportunity, cost of the work |
| Analytics and engineering (supporting) | Data quality, delivery | Clear requirements, tracking fixes, a maintained dashboard |

Owners for each metric are proposed in `KPI_TREE.md`.

## 3. Current state

| Item | Value | Source |
|---|---|---|
| Valid sessions | 360,129 | `results/20_funnel.csv` |
| Users (browsers or devices) | 270,154 | `results/01_profile_overview.csv` |
| Sessions entering the funnel | 359,815 | `results/20_funnel.csv` |
| Sessions with a view_item | 76,965 (21.4% of entry) | `results/20_funnel.csv` |
| Sessions with an add_to_cart | 15,162 (19.7% of viewers) | `results/20_funnel.csv` |
| Sessions beginning checkout | 5,416 (35.7% of cart sessions) | `results/20_funnel.csv` |
| Sessions adding payment info | 3,831 (70.7% of checkout starts) | `results/20_funnel.csv` |
| Sessions purchasing | 2,834 (74.0% of payment info) | `results/20_funnel.csv` |
| Overall funnel conversion | 0.79% | `results/20_funnel.csv` |
| Session conversion rate (sessions with a purchase event) | 1.35% (4,848 sessions) | `results/21b_purchase_sessions_missing_steps.csv` |
| Orders (real transaction ids) | 4,451 | `results/26_revenue_by_segment.csv` |
| Revenue | 307,640 | `results/26_revenue_by_segment.csv` |
| Average order value | 69.12 | `results/26_revenue_by_segment.csv` |
| Revenue per user | 1.14 | `results/26_revenue_by_segment.csv` |
| Sessions lost between checkout start and purchase | 2,582 (47.7% of checkout starts; sum of 1,585 lost before payment info and 997 lost before purchase) | `results/20_funnel.csv` |
| New vs returning conversion | 0.68% vs 3.10% | `results/23_headline_comparisons.csv` |
| Returning share of sessions and of revenue | 27.5% and 66.5% | `results/22_segment_funnel.csv`, `results/26_revenue_by_segment.csv` |
| Purchase sessions with no add_to_cart event | 2,000 of 4,848 | `results/21b_purchase_sessions_missing_steps.csv` |

Funnel counts use the strict order rule from `docs/METRICS.md`. Two cautions from `docs/DATA_QUALITY.md`: revenue and orders are understated by an unknown amount (906 purchase events have no usable transaction id), and the purchase count in the strict funnel (2,834) is lower than the number of sessions with a purchase event (4,848) because of the missing add-to-cart events.

Where shoppers are lost, in sessions: 282,850 before viewing an item, 61,803 between viewing an item and adding to cart, 9,746 between cart and checkout start, 2,582 between checkout start and purchase (`results/20_funnel.csv`).

## 4. Size of the opportunity (scenarios, not forecasts)

What the 92 days of revenue would have been if one step had converted better, everything else equal.

Assumptions (labeled as assumptions, not measured):
1. Each extra purchasing session places one order at the current average order value (69.12).
2. Later steps keep their current conversion (for the add-to-cart lever, 18.7% of cart sessions end in a purchase).
3. The improvement is in percentage points on the current rate.
4. The window is the 92 days of data, not a year.
5. Revenue is understated by an unknown amount, so these amounts are on the low side of the true dollars.

Source of every figure: `results/ba_scenarios.csv`, produced by `python -m scripts.ba_numbers` from `results/20_funnel.csv` and `results/26_revenue_by_segment.csv`.

| Lever | Baseline rate | Improvement | Extra purchasing sessions | Extra revenue (92 days) | Share of window revenue |
|---|---|---|---|---|---|
| Checkout completion (begin checkout to purchase) | 52.3% | +2 points | 108 | 7,487 | 2.4% |
| Checkout completion | 52.3% | +5 points | 271 | 18,717 | 6.1% |
| Checkout completion | 52.3% | +10 points | 542 | 37,434 | 12.2% |
| Add to cart rate (view item to add to cart) | 19.7% | +1 point | 144 | 9,943 | 3.2% |
| Add to cart rate | 19.7% | +2 points | 288 | 19,886 | 6.5% |
| Add to cart rate | 19.7% | +5 points | 719 | 49,716 | 16.2% |

Reading the table: one point on the add-to-cart rate is worth roughly 2.7 times one point on checkout completion (9,943 against 3,743 per point, which is 7,487 divided by 2), because far more sessions sit at the earlier step. That does not say the add-to-cart rate is easier to move by a point. That is what the tests in option C would find out.

## 5. Options compared

Costs are relative (low, medium, high), because the data has no cost figures. Effort and risk are judgments to be checked with engineering. They are not measured.

| Option | What it is | Pros | Cons | Relative cost | Risk |
|---|---|---|---|---|---|
| A. Do nothing | Keep ad hoc reports | No spend | Drops stay invisible, tracking gap stays, cannot tell if anything works | None | High: decisions stay uninformed |
| B. Fix tracking and build the funnel monitoring dashboard | Check cart and checkout events, publish a daily funnel dashboard with alerts (`BRD.md`) | Makes every later step measurable, one version of the numbers, early warning on drops | Does not raise conversion by itself | Low to medium | Low |
| C. Product page and add-to-cart tests | A/B tests on product pages (price, shipping, size and stock info, images) | Largest step loss, scenario table shows the biggest dollars per point | Needs traffic and test discipline, results may be small | Medium | Medium: a change can lower conversion, so test before rollout |
| D. Checkout improvements | Simplify checkout, guest checkout, payment options | 2,582 sessions lost at this stage, close to purchase | Fewer sessions at stake, so fewer dollars per point | Medium to high | Medium |
| E. Returning visitor programme | Email, wishlist, reminders for viewed items | Returning visitors convert at 3.10% against 0.68% and bring 66.5% of revenue | Only 2.5% to 6.7% of full cohorts return in week 1 (`results/25_retention_matrix.csv`), needs consent and tooling | Medium | Medium |

## 6. Recommendation

1. **Do B first.** The tracking gap (2,000 of 4,848 purchase sessions with no add-to-cart event) means current funnel numbers are uncertain, and no test result can be read without the dashboard. It is also the cheapest option. The requirements are in `BRD.md`.
2. **Then run C as a series of A/B tests**, starting with the products that have many views and few carts (`results/28_low_add_to_cart_products.csv`). Decide a minimum effect worth shipping before each test.
3. **Run E in parallel as a small pilot**, measured by week 1 retention and returning-session conversion.
4. **Hold D** until the dashboard shows whether checkout completion is lower in some segments or devices. The data shows no distinguishable difference by device or country (`results/23_headline_comparisons.csv`).

Success measures and owners are in `KPI_TREE.md`. This is observational data, so no option is proven to work. The tests are how that is found out.

## 7. Limits of this case

- No cost, margin or traffic spend data, so there is no return on investment figure and no break-even.
- Scenario dollars are 92 day amounts, not annual, and use a flat average order value.
- Revenue and orders are understated by an unknown amount (`docs/DATA_QUALITY.md`).
- First-touch traffic source only, 21% unknown.
- One store, one holiday season, obfuscated data.
