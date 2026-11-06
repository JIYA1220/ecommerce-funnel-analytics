# Process flows: detecting and reacting to a conversion drop

Important: the **as-is** flow is an **assumed** picture of a typical store team without a funnel dashboard. It is not an observed process, because no process data was available. It must be validated with the team before it is used to justify change. The **to-be** flow is the process the Funnel Monitoring Dashboard in `BRD.md` supports. Role names match `KPI_TREE.md` and `BRD.md`.

Editable versions: `as_is.drawio` and `to_be.drawio` (open at https://app.diagrams.net or in draw.io Desktop).

## As-is (assumed)

```mermaid
flowchart TD
    A["Sales or revenue looks low<br/>in a weekly report"] --> B["Manager asks the data analyst<br/>to look into it"]
    B --> C["Analyst pulls data by hand<br/>from the analytics tool"]
    C --> D{"Do the numbers match<br/>other reports?"}
    D -- "No" --> E["Debate which number is right<br/>(days)"]
    E --> C
    D -- "Yes" --> F["Analyst checks a few segments<br/>chosen by guess"]
    F --> G["Findings sent by email or slide"]
    G --> H{"Cause clear?"}
    H -- "No" --> I["Issue left open<br/>no owner, no follow-up"]
    H -- "Yes" --> J["Product or marketing<br/>decides on a fix"]
    J --> K["Fix released<br/>effect not measured"]
```

Pain points (assumed): detection depends on a weekly report, so a drop can run for days; numbers differ between reports; segments are chosen by guess; there is no owner or log; the effect of a fix is not measured.

## To-be

```mermaid
flowchart TD
    A["Daily data refresh<br/>and reconciliation check"] --> B{"Check passed?"}
    B -- "No" --> C["Publishing stops<br/>analytics team notified"]
    C --> A
    B -- "Yes" --> D["Dashboard updated<br/>with refresh time"]
    D --> E{"Daily session conversion<br/>below the alert rule?"}
    E -- "No" --> F["No alert<br/>weekly review only"]
    E -- "Yes" --> G["Alert to the metric owner<br/>with step and segment that moved most"]
    G --> H["Owner opens the alert<br/>in the alert log"]
    H --> I["Owner checks the data quality panel<br/>and the funnel by segment"]
    I --> J{"Tracking or data issue?"}
    J -- "Yes" --> K["Analytics engineer fixes<br/>the tracking"]
    J -- "No" --> L{"Explained by season,<br/>promotion or known change?"}
    L -- "Yes" --> M["Log explanation<br/>close alert"]
    L -- "No" --> N["Owner proposes a fix<br/>or an A/B test"]
    K --> O["Re-check next refresh"]
    N --> O
    O --> P{"Conversion back<br/>in the usual range?"}
    P -- "Yes" --> M
    P -- "No" --> G
    F --> Q["Weekly review of overdue alerts<br/>and data quality trends"]
    M --> Q
```

What changes (design intent, not measured results): detection becomes daily, the alert names a step and a segment, there is one set of definitions, each alert has an owner and a status, and a fix is checked on the next refresh. Whether this shortens the time to detect is measured after go-live (`BRD.md`, section 10).

## Roles in the to-be flow

| Step | Role |
|---|---|
| Refresh and reconciliation | Analytics engineer, data analyst |
| Alert rule | Product manager and data analyst (RACI in `BRD.md`) |
| Respond to the alert | Metric owner (product, marketing or operations manager) |
| Tracking fixes | Analytics engineer |
| Weekly review | Head of e-commerce chairs, all owners attend |
