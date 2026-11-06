# Business requirements document: Funnel Monitoring Dashboard

Version 1.0 (draft for review). Related: `BUSINESS_CASE.md`, `KPI_TREE.md`, `PROCESS_FLOW.md`, `../docs/METRICS.md`. Baseline numbers come from `results/` as cited. Anything marked **(assumption)** or **(proposed)** is not measured and must be agreed with the stakeholders.

## 1. Objective

Give marketing, product, e-commerce operations and finance one trusted view of the shopping funnel, so that a drop in conversion is seen within a day, located to a step and a segment, and followed until it is explained or fixed. Success is measured in section 10.

## 2. Background

In 2020-11-01 to 2021-01-31 only 0.79% of 359,815 entering sessions reached purchase (`results/20_funnel.csv`). 2,000 of 4,848 purchase sessions have no add-to-cart event (`results/21b_purchase_sessions_missing_steps.csv`), and 21.2% of events have an unknown acquisition medium (`results/03_missing_values.csv`). Reports are produced by hand and no one owns the funnel numbers. The case is in `BUSINESS_CASE.md`.

## 3. Scope

In scope:
- A dashboard with the funnel, segments, retention and product views.
- Metric definitions as in `docs/METRICS.md`, shown in the dashboard.
- A daily data refresh and threshold alerts for conversion drops.
- A data quality panel (missing or placeholder values, tracking gap indicator).
- Access control and a named owner for each metric.

Out of scope:
- Changing the website or checkout flow.
- Fixing the tracking events (a separate task, but the dashboard must show the gap until it is closed).
- Personal data or any user level view. Only aggregated data is shown.
- Forecasting, attribution modelling and marketing spend reporting.
- A mobile app version.

## 4. Stakeholders

| Stakeholder | Role in this project |
|---|---|
| Head of e-commerce | Sponsor, approves scope and priorities |
| Product manager | Main user, owner of step conversions |
| Marketing manager | User, owner of sessions, medium and retention |
| E-commerce operations manager | User, owner of orders and average order value |
| Finance analyst | User, owner of revenue figures |
| Data analyst | Builds and maintains the dashboard |
| Analytics engineer | Maintains the data pipeline and tracking checks |
| Security or IT | Approves access rules |

## 5. Business requirements

| ID | Requirement |
|---|---|
| BR-1 | The business can see the six-step funnel (entry, view item, add to cart, begin checkout, add payment info, purchase) with counts, step conversion and drop-off. |
| BR-2 | The business can compare the funnel across device, first-touch medium, country and new vs returning visitors, and can tell which differences are bigger than noise. |
| BR-3 | A material fall in conversion is detected within one business day and routed to an owner. |
| BR-4 | Everyone sees the same metric definitions, and revenue figures state their known limits. |
| BR-5 | The business can see cohort retention and the products with many views and few add-to-carts. |
| BR-6 | Data gaps are visible, so no one acts on a number the data cannot support. |

## 6. Functional requirements

| ID | Requirement | Traces to |
|---|---|---|
| FR-1 | Show the funnel as a chart and a table with sessions per step, step conversion, drop-off share and sessions lost. | BR-1 |
| FR-2 | Apply the strict order rule (a step counts only after the previous step in the same session), and show the unordered count next to it. | BR-1, BR-6 |
| FR-3 | Provide slicers for date range, device category, first-touch medium, country (top 10 and Other) and new vs returning. | BR-2 |
| FR-4 | Show the 95% Wilson confidence interval for each conversion rate, and mark segments with fewer than 100 sessions as unreliable. | BR-2 |
| FR-5 | Show daily session conversion rate with a trend line and the holiday season marked. | BR-3 |
| FR-6 | Send an alert when the daily session conversion rate falls below the lower bound of the usual range (the rule is **proposed** in the assumptions below), with the step and segment that moved most. | BR-3 |
| FR-7 | Record each alert with owner, status (open, investigating, explained, fixed), a note and the date closed. | BR-3 |
| FR-8 | Show a definitions page with every metric formula, the source table and the owner (from `KPI_TREE.md`). | BR-4 |
| FR-9 | Show a weekly cohort retention matrix, with weeks not yet observed left blank. | BR-5 |
| FR-10 | Show a product table with views, add-to-cart rate, item revenue and a flag for products clearly below the all-items rate. | BR-5 |
| FR-11 | Show a data quality panel: share of unknown medium, share of purchase events without a usable transaction id, and the share of purchase sessions with no add-to-cart event. | BR-6 |
| FR-12 | Export any table to CSV. | BR-1 to BR-5 |

## 7. Non-functional requirements

| ID | Area | Requirement |
|---|---|---|
| NFR-1 | Data freshness | Data refreshes once a day, available by 08:00 local time **(proposed)**. The dashboard shows the time of the last refresh. |
| NFR-2 | Accuracy | Dashboard totals match the source queries exactly. A reconciliation test runs after every refresh and blocks publishing if it fails. |
| NFR-3 | Access | Only named staff in marketing, product, operations, finance and analytics can open it. View-only for most users, edit for the analytics team. No user level data. |
| NFR-4 | Performance | A page opens in under 5 seconds with the default filters **(proposed)**. |
| NFR-5 | Availability | Available during working hours on weekdays. A failed refresh shows a visible warning, not stale numbers without notice. |
| NFR-6 | Privacy | Aggregated data only. No user ids or personal data shown or exported. |
| NFR-7 | Maintainability | Metric logic is stored as versioned code, and changes to a definition are logged. |
| NFR-8 | Cost | Uses the existing data warehouse and BI licences. Any new paid resource needs finance approval. |

## 8. User stories

Each story has acceptance criteria in Given/When/Then form.

**US-1. See the funnel**
As a product manager, I want to see sessions at each funnel step with step conversion and drop-off, so that I know which step loses the most shoppers.
- Given the dashboard is open on the funnel page, when I select a date range, then I see sessions, step conversion, drop-off share and sessions lost for all six steps.
- Given the default date range is the full data window, when the page loads, then the step counts equal the totals in the source results (for the baseline window, 359,815 entering sessions and 2,834 purchasing sessions).

**US-2. Compare segments**
As a marketing manager, I want to compare the funnel by first-touch medium, so that I can see which acquisition groups convert best.
- Given the funnel page, when I choose the medium dimension, then I see one row per medium with sessions and session conversion rate.
- Given a medium has fewer than 100 sessions, when it is shown, then it is labeled unreliable.
- Given two segments, when their 95% intervals do not overlap, then the dashboard states the difference is larger than noise.

**US-3. Know when conversion drops**
As an e-commerce operations manager, I want an alert when daily conversion falls below the usual range, so that I can react within a day.
- Given the daily refresh has finished, when the session conversion rate is below the alert rule, then an alert is sent to the owner by 08:00 **(proposed)**.
- Given an alert is sent, then it shows the date, the rate, the usual range and the step and segment with the largest change.
- Given the rate is within the usual range, when the refresh finishes, then no alert is sent.

**US-4. Track an alert to closure**
As a product manager, I want to log what I found for each alert, so that the team can see which drops were explained or fixed.
- Given an alert exists, when I set its status and add a note, then the log stores the status, note, my name and the time.
- Given an alert has been open for more than 3 business days **(proposed)**, when the weekly summary runs, then it is listed as overdue.

**US-5. Read definitions**
As a finance analyst, I want to read how each metric is defined, so that I can trust and explain the numbers.
- Given the definitions page, when I open it, then each metric shows its formula, source and owner.
- Given a definition changes, when the change is published, then the change log shows the date and the reason.

**US-6. Understand revenue limits**
As a finance analyst, I want revenue figures to show their known limits, so that I do not report them as exact.
- Given any card or table with revenue, when I hover over it, then it states that revenue counts one event per real transaction id.
- Given the data quality panel, when it loads, then it shows the number of purchase events without a usable transaction id.

**US-7. See retention**
As a marketing manager, I want a weekly cohort retention matrix, so that I can see whether visitors come back.
- Given the retention page, when I open it, then each row is a first-visit week and each column a week after.
- Given a week has not happened yet for a cohort, when the matrix is shown, then the cell is blank and not zero.
- Given the first week of data is a partial week, when it is shown, then it is marked partial.

**US-8. Find weak product pages**
As an e-commerce operations manager, I want to see products with many views and a low add-to-cart rate, so that I can raise them with the product team.
- Given the product table, when I filter to products with at least 500 view sessions, then products are ranked by add-to-cart rate from lowest.
- Given a product's interval upper bound is below the all-items rate, then the row is flagged clearly below.

**US-9. See data gaps**
As a data analyst, I want a data quality panel, so that stakeholders see where the data is weak before they act.
- Given the panel, when it loads, then it shows the unknown medium share, the purchase events with no usable transaction id, and the share of purchase sessions with no add-to-cart event.
- Given any of these values worsens by more than a **proposed** 5 points between refreshes, then the analytics team is notified.

**US-10. Trust that numbers match**
As a data analyst, I want a reconciliation check on every refresh, so that a wrong dashboard is never published.
- Given a refresh, when dashboard totals differ from the source query totals, then publishing stops and the analytics team is notified.
- Given the check passes, then the dashboard shows the refresh time.

**US-11. Control access**
As IT security, I want access limited to named staff and no user level data, so that privacy rules are met.
- Given a person not on the access list, when they try to open the dashboard, then access is refused.
- Given any page or export, when it is produced, then it contains no user id or personal data.

**US-12. Export a table**
As a marketing manager, I want to export a table to CSV, so that I can use it in a campaign review.
- Given any table on the dashboard, when I choose export, then I get a CSV with the same rows and the same filters.

## 9. Assumptions, dependencies and risks

Assumptions (labeled, not measured):
- A1. The funnel events (page view, view item, add to cart, begin checkout, add payment info, purchase) continue to be collected in the same form.
- A2. A daily refresh is enough. Hourly data is not needed.
- A3. The alert rule is **proposed**: alert when the daily session conversion rate falls below the lower end of the usual range, where the usual range is defined by the analytics team from at least 8 weeks of history, adjusted for weekday and season. The threshold is agreed before go-live. No threshold is chosen from this data alone, because the baseline covers only one holiday season.
- A4. Existing data warehouse and BI licences are available (NFR-8).
- A5. Stakeholders agree to name an owner for each metric (`KPI_TREE.md`).

Dependencies:
- D1. A tracking check of the cart and checkout events (the gap in `results/21_funnel_skipping.csv`).
- D2. Access to a session level source for traffic channel, because the current medium is first-touch only.

| ID | Risk | Likelihood and impact (judgment) | Mitigation |
|---|---|---|---|
| R1 | Tracking gap stays, so funnel numbers stay uncertain | Medium likelihood, high impact | Show the gap in the data quality panel, schedule the tracking check (D1) |
| R2 | Alerts fire too often and are ignored | Medium, medium | Agree the rule with owners, review it after the first month |
| R3 | One season of history gives a poor usual range | High, medium | Use at least 8 weeks, mark the holiday season, review as data grows |
| R4 | Metric owners are not named | Medium, high | Sponsor assigns owners before build starts |
| R5 | Revenue is read as exact | Medium, medium | Limits shown wherever revenue appears (US-6) |
| R6 | Privacy breach through exports | Low, high | Aggregated data only (NFR-6, US-11) |

## 10. Success measures

| Measure | Baseline | Target |
|---|---|---|
| Time to detect a conversion drop | not yet measured | within 1 business day **(proposed)** |
| Alerts with a recorded outcome | not yet measured | all alerts closed with a note |
| Share of purchase sessions with a matching add-to-cart event | 58.7% (2,848 of 4,848 purchase sessions have an add-to-cart event, 2,000 do not) (`results/21b_purchase_sessions_missing_steps.csv`) | to be set after the tracking check |
| Dashboard totals matching the source queries | tests pass on the baseline (`tests/test_powerbi_export.py`) | 100% on every refresh |

## 11. RACI

R = responsible, A = accountable, C = consulted, I = informed.

| Activity | Head of e-commerce | Product manager | Marketing manager | Operations manager | Finance analyst | Data analyst | Analytics engineer | IT security |
|---|---|---|---|---|---|---|---|---|
| Approve scope and priorities | A | C | C | C | C | R | I | I |
| Agree metric definitions | A | R | R | R | R | C | I | I |
| Name metric owners | A | C | C | C | C | I | I | I |
| Build the dashboard | I | C | C | C | C | A, R | C | I |
| Fix tracking events | I | C | I | I | I | C | A, R | I |
| Set alert rule | A | R | C | C | C | R | C | I |
| Respond to alerts | I | R | R | R | I | C | C | I |
| Data quality and reconciliation | I | I | I | I | C | A | R | I |
| Access and privacy | C | I | I | I | I | C | C | A, R |
| Maintain definitions and change log | I | C | C | C | C | A, R | C | I |
| Go-live decision | A | C | C | C | C | R | R | C |
