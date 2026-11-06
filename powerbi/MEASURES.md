# Power BI model, measures and layout

Dashboard name: **Merchandise Store Funnel and Retention** (3 pages). Data: GA4 sample e-commerce dataset, 2020-11-01 to 2021-01-31. All CSVs in this folder are built by `python -m scripts.export_powerbi` from files in `results/`, and tests check that they add up (`tests/test_powerbi_export.py`).

Status note: the DAX below was written without opening Power BI. After you build the dashboard, compare it with `results/dashboard_expected_values.csv` (see the last section). Tell me about any value that differs.

## 1. Data model

### Tables

| Table | File | Grain (one row per) | Columns |
|---|---|---|---|
| `daily_kpis` | `daily_kpis.csv` | day (92 rows) | `date`, `sessions`, `new_sessions`, `returning_sessions`, `sessions_with_purchase`, `purchases`, `revenue` |
| `dim_date` | made in DAX | day | `Date`, `Month`, `Weekday No`, `Weekday`, `Week Start` |
| `dim_step` | `dim_step.csv` | funnel step (6 rows) | `step_no`, `step` |
| `dim_segment` | `dim_segment.csv` | segment (21 rows plus "all") | `segment_key`, `dimension`, `segment`, `sessions`, `reliable` |
| `funnel_by_segment` | `funnel_by_segment.csv` | segment and step | `segment_key`, `dimension`, `segment`, `step_no`, `step`, `sessions` |
| `segment_kpis` | `segment_kpis.csv` | segment | `segment_key`, `dimension`, `segment`, `sessions`, `users`, `sessions_with_purchase`, `purchases`, `revenue`, `buyers`, `reliable` |
| `cohort_retention` | `cohort_retention.csv` | cohort week and week offset | `cohort_week`, `cohort_week_is_partial`, `cohort_size`, `week_n`, `observable`, `retained_users`, `retention` |
| `products` | `products.csv` | product name (430 rows) | `item_name`, `item_category`, `view_sessions`, `viewed_and_carted`, `item_revenue`, `units`, `transactions` |
| `Week N` | made in DAX | week offset 0 to 13 | `Week N` (a what-if style list) |
| `_Measures` | empty table | none | holds all measures |

### Relationships (all many-to-one, single direction, from the many side to the one side)

| From (many) | To (one) |
|---|---|
| `daily_kpis[date]` | `dim_date[Date]` |
| `funnel_by_segment[step_no]` | `dim_step[step_no]` |
| `funnel_by_segment[segment_key]` | `dim_segment[segment_key]` |
| `segment_kpis[segment_key]` | `dim_segment[segment_key]` |

`cohort_retention`, `products` and `Week N` have no relationships. `Week N` is only a selector for the measure `Retention Week N`.

### Rule that avoids double counting

Each session appears once in every segment dimension (device, medium, country, visitor type) and once in "all". If you add up across dimensions you count sessions several times. So every segment and funnel measure returns blank unless exactly one `dimension` is selected. Keep a single-select slicer on `dim_segment[dimension]`, default value **all**.

### Things the model cannot do

- Distinct users cannot be summed over days. `Revenue Per User` therefore uses `segment_kpis` (users counted once per segment) and has no daily version.
- Segment and funnel tables cover the whole 92 days. The date slicer must not filter them (turn off the interaction, see build steps).
- Retention is about first visit cohorts in the window, so the first cohort (week of 2020-10-26, one day of data) is flagged `cohort_week_is_partial` and left out of the weighted retention measure.

## 2. DAX

### Calendar and parameter tables (Modeling, New table)

```dax
dim_date =
ADDCOLUMNS (
    CALENDAR ( DATE ( 2020, 11, 1 ), DATE ( 2021, 1, 31 ) ),
    "Month", FORMAT ( [Date], "yyyy-mm" ),
    "Weekday No", WEEKDAY ( [Date], 2 ),
    "Weekday", FORMAT ( [Date], "ddd" ),
    "Week Start", [Date] - WEEKDAY ( [Date], 2 ) + 1
)
```

```dax
Week N = GENERATESERIES ( 0, 13, 1 )
```

After creating `dim_date`: set `Weekday` to sort by `Weekday No`, and mark the table as a date table on `Date`.

### Overview measures (from `daily_kpis`)

```dax
Sessions = SUM ( daily_kpis[sessions] )
New Sessions = SUM ( daily_kpis[new_sessions] )
Returning Sessions = SUM ( daily_kpis[returning_sessions] )
Sessions With Purchase = SUM ( daily_kpis[sessions_with_purchase] )
Session Conversion Rate = DIVIDE ( [Sessions With Purchase], [Sessions] )
Purchases = SUM ( daily_kpis[purchases] )
Revenue = SUM ( daily_kpis[revenue] )
AOV = DIVIDE ( [Revenue], [Purchases] )
```

Definitions are in `docs/METRICS.md`. Session conversion rate = sessions with a purchase event / all valid sessions. Purchases and revenue count one event per real transaction id, so revenue is understated by an unknown amount (`docs/DATA_QUALITY.md`).

### Segment measures (from `segment_kpis`)

```dax
One Dimension Selected = HASONEVALUE ( dim_segment[dimension] )

Segment Sessions =
IF ( [One Dimension Selected], SUM ( segment_kpis[sessions] ) )

Segment Users =
IF ( [One Dimension Selected], SUM ( segment_kpis[users] ) )

Segment Purchases =
IF ( [One Dimension Selected], SUM ( segment_kpis[purchases] ) )

Segment Revenue =
IF ( [One Dimension Selected], SUM ( segment_kpis[revenue] ) )

Segment AOV =
IF ( [One Dimension Selected], DIVIDE ( SUM ( segment_kpis[revenue] ), SUM ( segment_kpis[purchases] ) ) )

Revenue Per User =
IF ( [One Dimension Selected], DIVIDE ( SUM ( segment_kpis[revenue] ), SUM ( segment_kpis[users] ) ) )

Segment Conversion Rate =
IF (
    [One Dimension Selected],
    DIVIDE ( SUM ( segment_kpis[sessions_with_purchase] ), SUM ( segment_kpis[sessions] ) )
)

Wilson Low =
VAR n = SUM ( segment_kpis[sessions] )
VAR x = SUM ( segment_kpis[sessions_with_purchase] )
VAR z = 1.96
VAR p = DIVIDE ( x, n )
RETURN
    IF (
        [One Dimension Selected] && n > 0,
        DIVIDE ( p + z ^ 2 / ( 2 * n ) - z * SQRT ( p * ( 1 - p ) / n + z ^ 2 / ( 4 * n ^ 2 ) ), 1 + z ^ 2 / n )
    )

Wilson High =
VAR n = SUM ( segment_kpis[sessions] )
VAR x = SUM ( segment_kpis[sessions_with_purchase] )
VAR z = 1.96
VAR p = DIVIDE ( x, n )
RETURN
    IF (
        [One Dimension Selected] && n > 0,
        DIVIDE ( p + z ^ 2 / ( 2 * n ) + z * SQRT ( p * ( 1 - p ) / n + z ^ 2 / ( 4 * n ^ 2 ) ), 1 + z ^ 2 / n )
    )

Reliability =
IF ( SUM ( segment_kpis[sessions] ) >= 100, "reliable", "unreliable (under 100 sessions)" )
```

Reading the Wilson measures: two segments differ by more than noise only when their intervals do not overlap (the rule used in `docs/FINDINGS.md`).

### Funnel measures (from `funnel_by_segment`)

```dax
Step Sessions =
IF ( [One Dimension Selected], SUM ( funnel_by_segment[sessions] ) )

Previous Step Sessions =
VAR s = MAX ( dim_step[step_no] )
RETURN
    IF ( s > 1, CALCULATE ( [Step Sessions], FILTER ( ALL ( dim_step ), dim_step[step_no] = s - 1 ) ) )

Step Conversion = DIVIDE ( [Step Sessions], [Previous Step Sessions] )

Drop-off Rate = IF ( ISBLANK ( [Step Conversion] ), BLANK (), 1 - [Step Conversion] )

Sessions Lost At Step =
IF ( ISBLANK ( [Previous Step Sessions] ), BLANK (), [Previous Step Sessions] - [Step Sessions] )

Entry Sessions = CALCULATE ( [Step Sessions], dim_step[step_no] = 1 )

Purchase Step Sessions = CALCULATE ( [Step Sessions], dim_step[step_no] = 6 )

Overall Funnel Conversion = DIVIDE ( [Purchase Step Sessions], [Entry Sessions] )

Share Of Entry = DIVIDE ( [Step Sessions], [Entry Sessions] )

Weakest Step =
VAR t =
    ADDCOLUMNS ( FILTER ( ALL ( dim_step ), dim_step[step_no] > 1 ), "@c", [Step Conversion] )
VAR m = MINX ( t, [@c] )
RETURN
    IF ( [One Dimension Selected] && NOT ISBLANK ( m ), MINX ( FILTER ( t, [@c] = m ), dim_step[step] ) )
```

The funnel uses the strict order rule (a step counts only after the previous step, in time). That is why `Overall Funnel Conversion` (2,834 purchase sessions) is lower than `Session Conversion Rate` (4,848 sessions with a purchase event). See finding 3 in `docs/FINDINGS.md`.

### Retention measures (from `cohort_retention`)

```dax
Cohort Size =
CALCULATE ( SUM ( cohort_retention[cohort_size] ), cohort_retention[week_n] = 0 )

Retained Users = SUM ( cohort_retention[retained_users] )

Retention =
VAR d =
    CALCULATE ( SUM ( cohort_retention[cohort_size] ), cohort_retention[observable] = TRUE () )
RETURN
    IF ( ISBLANK ( [Retained Users] ), BLANK (), DIVIDE ( [Retained Users], d ) )

Retention Week N =
VAR n = SELECTEDVALUE ( 'Week N'[Week N], 1 )
RETURN
    CALCULATE (
        [Retention],
        cohort_retention[week_n] = n,
        cohort_retention[cohort_week_is_partial] = FALSE ()
    )
```

`Retention` in a matrix cell is the share of that cohort with a session N weeks after its first visit week. Cells for weeks that have not happened yet are blank, not 0%. `Retention Week N` is the weighted average over all full cohorts that can be observed at that week (retained users divided by cohort size, summed first).

### Product measures (from `products`)

```dax
View Sessions = SUM ( products[view_sessions] )
Viewed And Carted = SUM ( products[viewed_and_carted] )
Item Add To Cart Rate = DIVIDE ( [Viewed And Carted], [View Sessions] )
Item Revenue = SUM ( products[item_revenue] )
Units Sold = SUM ( products[units] )

Share Of Item Revenue =
DIVIDE ( [Item Revenue], CALCULATE ( [Item Revenue], ALL ( products ) ) )

All Items Rate =
DIVIDE (
    CALCULATE ( SUM ( products[viewed_and_carted] ), ALL ( products ) ),
    CALCULATE ( SUM ( products[view_sessions] ), ALL ( products ) )
)

Item Rate Wilson High =
VAR n = SUM ( products[view_sessions] )
VAR x = SUM ( products[viewed_and_carted] )
VAR z = 1.96
VAR p = DIVIDE ( x, n )
RETURN
    IF ( n > 0, DIVIDE ( p + z ^ 2 / ( 2 * n ) + z * SQRT ( p * ( 1 - p ) / n + z ^ 2 / ( 4 * n ^ 2 ) ), 1 + z ^ 2 / n ) )

Clearly Below All Items =
IF ( [Item Rate Wilson High] < [All Items Rate], "yes", "" )
```

Product names are used as the key because item ids in purchase events are a different scheme from the ids in view and cart events (explained in `sql/31_product_table.sql`). Product views here count a view in a session once.

## 3. Dashboard layout (3 pages, 16:9)

Use one colour for "this segment or period" and grey for the rest. Show percentages with 2 decimals for conversion rates, 0 decimals for counts. Put the data window and the revenue caveat in a small text box in the footer of every page.

### Page 1: Overview KPIs

| Item | Visual | Fields |
|---|---|---|
| Date slicer | Between slicer | `dim_date[Date]` |
| KPI cards (5) | Card | `Sessions`, `Session Conversion Rate`, `Purchases`, `Revenue`, `AOV` |
| Weekly conversion | Line chart | X: `dim_date[Week Start]`, Y: `Session Conversion Rate` |
| Weekly sessions | Column chart | X: `dim_date[Week Start]`, Y: `Sessions` |
| Conversion by weekday | Column chart | X: `dim_date[Weekday]`, Y: `Session Conversion Rate` |
| New vs returning sessions | Donut | Values: `New Sessions`, `Returning Sessions` |
| Footer note | Text box | "Revenue counts one event per real transaction id and is understated by an unknown amount. Nov to Jan covers the holiday season." |

Slicers on this page: date.

### Page 2: Funnel and segments

| Item | Visual | Fields |
|---|---|---|
| Dimension slicer | Single-select list or tiles, default **all** | `dim_segment[dimension]` |
| Segment slicer | Dropdown | `dim_segment[segment]` |
| Funnel | Funnel chart | Category: `dim_step[step]` (sorted by `step_no`), Values: `Step Sessions` |
| Step table | Table | `dim_step[step]`, `Step Sessions`, `Step Conversion`, `Drop-off Rate`, `Sessions Lost At Step` |
| Segment table | Table | `dim_segment[segment]`, `Segment Sessions`, `Segment Conversion Rate`, `Wilson Low`, `Wilson High`, `Reliability`, `Segment AOV`, `Revenue Per User`, `Weakest Step` |
| KPI cards | Card | `Overall Funnel Conversion`, `Segment Conversion Rate` |

Slicers on this page: dimension and segment. Use **Format, Edit interactions** to stop the date slicer on page 1 from affecting this page (it is on another page, so the only thing to check is that no date slicer is synced to this page). Sort the segment table by `Segment Sessions` descending. Grey out rows marked "unreliable".

### Page 3: Retention and products

| Item | Visual | Fields |
|---|---|---|
| Cohort matrix | Matrix | Rows: `cohort_retention[cohort_week]`, Columns: `cohort_retention[week_n]`, Values: `Retention` (conditional colour scale, blank cells stay blank) |
| Week selector | Dropdown slicer | `'Week N'[Week N]` |
| Retention card | Card | `Retention Week N` |
| Cohort size column | Table or matrix extra column | `Cohort Size` next to the matrix |
| Top 10 products | Bar chart | Axis: `products[item_name]`, Values: `Item Revenue`; filter: Top N 10 by `Item Revenue` |
| Low add-to-cart products | Table | `products[item_name]`, `View Sessions`, `Item Add To Cart Rate`, `Item Rate Wilson High`, `All Items Rate`, `Clearly Below All Items`; filter: `View Sessions` at least 500; sort by `Item Add To Cart Rate` ascending |
| Category filter | Slicer | `products[item_category]` |

## 4. Check your dashboard against the results

When you have built the dashboard, put the `.pbix` and screenshots (one per page, plus one of the Page 2 funnel with the **all** dimension selected) in this folder. The file `results/dashboard_expected_values.csv` lists the values the cards and tables must show, with the source file for each. Open these on your pages and compare:

| Page | Visual state | Expected, from `results/dashboard_expected_values.csv` |
|---|---|---|
| 1 | No date filter | Sessions, Session Conversion Rate, Purchases, Revenue, AOV |
| 2 | Dimension = all | Funnel step sessions, step conversions, drop-offs, Overall Funnel Conversion, Revenue Per User |
| 2 | Dimension = visitor_type | Segment Conversion Rate for new and returning |
| 3 | Week N = 1, 2, 4 | Retention Week N (the weighted values in the file) |
| 3 | Top products | Top product by revenue and its item revenue |

Round as the file does. Small rounding differences in the last digit are fine. Anything else is a mismatch to report.
