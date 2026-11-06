# Data

## Phase 1 to 3: GA4 sample e-commerce dataset

- Table: `bigquery-public-data.ga4_obfuscated_sample_ecommerce.events_*` (one table per day, `events_YYYYMMDD`).
- What it is: a sample of Google Analytics 4 event export data from the Google Merchandise Store, an online shop for Google-branded products.
- Source and documentation: https://developers.google.com/analytics/bigquery/web-ecommerce-demo-dataset (read on 2026-11-06).
- Access: BigQuery Sandbox (free). Queries use `_TABLE_SUFFIX` to select dates and only the columns they need.

### Size, measured (`results/01_profile_overview.csv`)

| Item | Value |
|---|---|
| First and last date | 2020-11-01 to 2021-01-31 |
| Days with data | 92 (no missing days) |
| Events | 4,295,584 |
| Users (`user_pseudo_id`) | 270,154 |
| Valid sessions (`user_pseudo_id` + `ga_session_id`) | 360,129 |
| Events with null user id or null session id | 0 and 0 |

### Limitations stated by Google's documentation

- The data is obfuscated. Google says it is meant to "emulate" a real implementation, and that internal consistency is somewhat limited because of the obfuscation.
- Some fields contain placeholder values: `<Other>`, `NULL` and empty strings. The page does not say which fields.
- The data cannot be compared with Google's separate Analytics demo account for the same store. The two differ.
- The page does not mention sessions, traffic source, items or revenue handling. Those limits were measured in Phase 1 (see below).

### Limitations measured in this project

The documentation does not mention the value `(data deleted)`, but it appears in the traffic source fields. Shares of placeholder values, by field, are in `docs/DATA_QUALITY.md`, with files in `results/03_*`, `results/04_*`, `results/05_*` and `results/06_*`.

Short version:

- Traffic source fields have the most missing or placeholder values (21% to 34% of events).
- City is `(not set)` for 41.8% of events. Country is `(not set)` for 0.75%.
- Device category has no placeholders.
- About 16% of `purchase` events have no usable transaction id, so revenue cannot be safely de-duplicated for them.
- This is a sample of one store over 3 months, and during the holiday season. It says nothing about other stores or other times of year.

## Phase 4 (A/B test): Cookie Cats

Mobile game A/B test (Kaggle, https://www.kaggle.com/datasets/yufengsui/mobile-games-ab-testing), gate at level 30 vs level 40, from a DataCamp project. Downloaded by hand into `ab_test/data/` (not committed).

**License: the Kaggle page lists it as Unknown** (checked 2026-11-07). It was used anyway on the owner's decision, for analysis only: the raw file is not redistributed, and only code and aggregated results are committed. Reuse of the raw data is at your own risk.
