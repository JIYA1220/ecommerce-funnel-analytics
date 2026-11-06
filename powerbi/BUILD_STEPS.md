# Build the dashboard step by step (Power BI Desktop, beginner)

Time: about 2 to 3 hours the first time. You need Power BI Desktop (free, Windows) and this repo cloned on your computer. Formulas to paste are in `MEASURES.md`. Read section 1 and 2 of that file first.

Before you start, in PowerShell inside the repo folder, make sure the CSV files are fresh:

```powershell
python -m scripts.export_powerbi
python -m scripts.expected_values
```

## Part A. Load the data (Power Query)

1. Open Power BI Desktop. Close the welcome screen. Choose **File, Save as**, and save an empty file as `ecommerce_funnel.pbix` inside the `powerbi` folder of the repo.
2. On the **Home** tab choose **Get data**, then **Text/CSV**. Pick `daily_kpis.csv` from the `powerbi` folder and click **Open**.
3. In the preview window click **Transform Data** (not Load). The Power Query Editor opens.
4. For the first table, check that the top row shows the real column names (`date`, `sessions`, and so on). If it shows Column1, Column2, click **Use First Row as Headers** on the **Home** tab.
5. Set the column types as in the table below. To change a type, click the small icon at the left of the column name, or select the column and use **Transform, Data Type**. If Power BI asks, choose **Replace current**.
6. Load the other files the same way. In the editor use **New Source, Text/CSV** for each of these: `dim_step.csv`, `dim_segment.csv`, `funnel_by_segment.csv`, `segment_kpis.csv`, `cohort_retention.csv`, `products.csv`. Set types as below.
7. When all 7 queries are set, click **Close and Apply** on the **Home** tab.

If your Windows region uses a comma for decimals, do this for `daily_kpis`, `segment_kpis` and `products` money columns: **Transform, Data Type, Using Locale**, choose the type, set the locale to **English (United States)**.

### Column types

| Table | Column | Type |
|---|---|---|
| `daily_kpis` | `date` | Date |
| `daily_kpis` | `sessions`, `new_sessions`, `returning_sessions`, `sessions_with_purchase`, `purchases` | Whole number |
| `daily_kpis` | `revenue` | Fixed decimal number |
| `dim_step` | `step_no` | Whole number |
| `dim_step` | `step` | Text |
| `dim_segment` | `segment_key`, `dimension`, `segment` | Text |
| `dim_segment` | `sessions` | Whole number |
| `dim_segment` | `reliable` | True/False |
| `funnel_by_segment` | `segment_key`, `dimension`, `segment`, `step` | Text |
| `funnel_by_segment` | `step_no`, `sessions` | Whole number |
| `segment_kpis` | `segment_key`, `dimension`, `segment` | Text |
| `segment_kpis` | `sessions`, `users`, `sessions_with_purchase`, `purchases`, `buyers` | Whole number |
| `segment_kpis` | `revenue` | Fixed decimal number |
| `segment_kpis` | `reliable` | True/False |
| `cohort_retention` | `cohort_week` | Date |
| `cohort_retention` | `cohort_week_is_partial`, `observable` | True/False |
| `cohort_retention` | `cohort_size`, `week_n`, `retained_users` | Whole number |
| `cohort_retention` | `retention` | Decimal number |
| `products` | `item_name`, `item_category` | Text |
| `products` | `view_sessions`, `viewed_and_carted`, `units`, `transactions` | Whole number |
| `products` | `item_revenue` | Fixed decimal number |

Notes for the Power Query steps:

- In `cohort_retention`, the blank cells in `retained_users` and `retention` are meant to be blank (that week has not happened yet). Leave them as null. Do not replace them with 0.
- Do not remove or filter any rows in Power Query. The tests check the totals of these files.
- The text `True` and `False` convert to True/False type directly. If you see errors after the change, use **Transform, Replace Values** to change `TRUE` to `True` and `FALSE` to `False` first, then convert.

## Part B. Add the extra tables

1. Go to the **Modeling** tab (or **Table tools**) and choose **New table**. Paste the `dim_date` formula from `MEASURES.md`. Press Enter.
2. Select the new `dim_date` table in the Data pane. On the **Table tools** tab choose **Mark as date table**, and pick the `Date` column.
3. Click the `Weekday` column, then **Column tools, Sort by column**, and choose `Weekday No`.
4. Create another **New table** with the `Week N` formula.
5. Create an empty measures table: **Home, Enter data**, leave the grid empty, name it `_Measures`, click **Load**.

## Part C. Relationships

1. Open the **Model** view (the third icon on the left side).
2. Drag to create these links (drag from the many side to the one side). The four from `MEASURES.md` section 1:
   - `daily_kpis[date]` to `dim_date[Date]`
   - `funnel_by_segment[step_no]` to `dim_step[step_no]`
   - `funnel_by_segment[segment_key]` to `dim_segment[segment_key]`
   - `segment_kpis[segment_key]` to `dim_segment[segment_key]`
3. Double-click each line and check: **Many to one (*:1)**, **Cross filter direction: Single**, and **Make this relationship active** ticked.
4. Remove any other automatic relationship Power BI created (right-click the line, **Delete**). `cohort_retention`, `products` and `Week N` stay unconnected.

## Part D. Measures

1. In the **Data** pane right-click `_Measures` and choose **New measure**.
2. Paste one measure at a time from `MEASURES.md` (each starts with a name, then `=`). Press Enter after each one.
3. Do them in this order: overview, segment, funnel, retention, product. A measure that uses another one needs that one to exist first.
4. After pasting, select each measure and set its format on **Measure tools**: percentages (conversion, drop-off, retention, shares, Wilson) as Percentage with 2 decimals; Revenue, AOV, Revenue Per User, Item Revenue as Currency with 2 decimals (the data is in US dollars); counts as Whole number with thousands separator.
5. If a measure shows a red underline, hover over it to read the error. The most common mistake is a missing table name or a smart quote (a curly `'`). Retype quotes as plain straight ones.

## Part E. Page 1: Overview KPIs

1. Rename the page **Overview**. Add a text box title: "Merchandise Store Funnel and Retention".
2. Add a **Slicer**, put `dim_date[Date]` in it, and change its style to **Between**.
3. Add 5 **Card** visuals: `Sessions`, `Session Conversion Rate`, `Purchases`, `Revenue`, `AOV`.
4. Add a **Line chart**: X-axis `dim_date[Week Start]`, Y-axis `Session Conversion Rate`.
5. Add a **Clustered column chart**: X-axis `dim_date[Week Start]`, Y-axis `Sessions`.
6. Add a **Clustered column chart**: X-axis `dim_date[Weekday]`, Y-axis `Session Conversion Rate`.
7. Add a **Donut chart**: Values `New Sessions` and `Returning Sessions` (drag both measures into Values).
8. Add a text box as the footer note from `MEASURES.md`.

## Part F. Page 2: Funnel and segments

1. Add a page and rename it **Funnel and segments**.
2. Add a slicer on `dim_segment[dimension]`. Change the style to **Tile** or **List**. In **Format, Slicer settings, Selection**, turn **Single select** on. Click the value **all**.
3. Add a slicer on `dim_segment[segment]` (dropdown style).
4. Add a **Funnel** visual. Group: `dim_step[step]`; Values: `Step Sessions`. In the visual's **...** menu, **Sort axis** by `step_no` ascending. If you cannot choose it, first select `dim_step[step]` in the Data pane and set **Sort by column** to `step_no`.
5. Add a **Table**: `dim_step[step]`, `Step Sessions`, `Step Conversion`, `Drop-off Rate`, `Sessions Lost At Step`. Sort by `dim_step[step]` (which now follows `step_no`).
6. Add a second **Table**: `dim_segment[segment]`, `Segment Sessions`, `Segment Conversion Rate`, `Wilson Low`, `Wilson High`, `Reliability`, `Segment AOV`, `Revenue Per User`, `Weakest Step`. Sort by `Segment Sessions` descending.
7. Add two **Card** visuals: `Overall Funnel Conversion` and `Segment Conversion Rate`.
8. Test: pick **device_category** in the dimension slicer. The segment table should show desktop, mobile and tablet. Pick **all** again. If the segment table is blank when no dimension is chosen, that is correct (see the double counting rule in `MEASURES.md`).

## Part G. Page 3: Retention and products

1. Add a page and rename it **Retention and products**.
2. Add a **Matrix**: Rows `cohort_retention[cohort_week]`, Columns `cohort_retention[week_n]`, Values `Retention`.
3. Colour it: select the matrix, **Format, Cell elements, Background color, fx**, choose **Gradient** on `Retention`. Leave blank cells without colour.
4. Add a slicer on `'Week N'[Week N]` (dropdown) and a **Card** with `Retention Week N`. Pick Week N = 1.
5. Add a **Bar chart**: Axis `products[item_name]`, Values `Item Revenue`. In the **Filters** pane set `item_name` to **Top N**, Top 10, by value `Item Revenue`.
6. Add a **Table**: `products[item_name]`, `View Sessions`, `Item Add To Cart Rate`, `Item Rate Wilson High`, `All Items Rate`, `Clearly Below All Items`. In the Filters pane for this visual set `View Sessions` **is greater than or equal to** 500. Sort by `Item Add To Cart Rate` ascending.
7. Add a slicer on `products[item_category]`.

## Part H. Check, save and send me the files

1. Open `results/dashboard_expected_values.csv` in Excel or Notepad. For each row listed in the check table at the end of `MEASURES.md`, compare it with what your page shows.
2. Save the file (**Ctrl+S**). It must be at `powerbi/ecommerce_funnel.pbix`.
3. Take one screenshot of each page (Windows key + Shift + S, then save the file). Name them:
   - `powerbi/screenshots/page1_overview.png`
   - `powerbi/screenshots/page2_funnel_all.png` (dimension = all)
   - `powerbi/screenshots/page2_funnel_visitor_type.png` (dimension = visitor_type)
   - `powerbi/screenshots/page3_retention_products.png` (Week N = 1)
4. Tell me when the files are in place. I will compare every number on the screenshots with `results/` and list any mismatch.

## If something looks wrong

| Problem | Likely cause and fix |
|---|---|
| A card shows blank | A segment or funnel measure needs exactly one `dimension` selected. Select one value in the dimension slicer. |
| Retention matrix shows 0% in later weeks | The `observable` or `retained_users` blanks were replaced with 0 in Power Query. Reload the CSV and leave nulls. |
| `Step Conversion` blank on every row | The `funnel_by_segment[step_no]` to `dim_step[step_no]` relationship is missing or inactive. |
| Weekday columns in the wrong order | Set `Weekday` to sort by `Weekday No`. |
| Totals look too high | You are summing across dimensions. Keep a single-select dimension slicer. |
