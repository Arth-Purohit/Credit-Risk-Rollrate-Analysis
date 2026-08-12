# Power BI Dashboard Build Guide

This project doesn't ship a `.pbix` file (Power BI Desktop is Windows-only
and can't be scripted from this environment), but it gives you everything
you need to build the dashboard in ~20 minutes. The CSVs are already
shaped for direct import — no cleanup needed.

## 1. Data source

After running `python run_all.py`, import these three files into Power BI
Desktop via **Get Data → Text/CSV**:

| File | Description |
|---|---|
| `outputs/powerbi_exports/vintage_curve.csv` | % of each origination cohort in each DPD bucket, by months-on-book |
| `outputs/powerbi_exports/roll_rates.csv` | Month-over-month bucket transition probabilities |
| `outputs/powerbi_exports/segment_trends.csv` | Monthly delinquency/charge-off rates by credit band, income band, region |

(Optional) You can instead connect Power BI directly to `data/credit_risk.db`
using an ODBC SQLite driver if you want to demo live SQL connectivity in an
interview — but the CSVs are the simplest path.

## 2. Suggested report pages

### Page 1 — Portfolio Health Overview
- **KPI cards:** Total accounts, 30+ DPD rate (latest month), 90+ DPD rate (latest month), charge-off rate (latest month)
- **Line chart:** `delinquency_30plus_rate_pct` over `snapshot_month`, split by `credit_score_band` (from `segment_trends.csv`)
- **Stacked bar:** account count by `dpd_bucket` for the latest `snapshot_month`
- **Slicers:** `credit_score_band`, `region`, `income_band`

### Page 2 — Vintage Analysis
- **Matrix visual:** rows = `vintage_month`, columns = `months_on_book`, values = `pct_of_cohort`, filtered to `dpd_bucket = "DPD_90_PLUS"` — conditional formatting (color scale) recreates the vintage triangle
- **Line chart:** cumulative charge-off % by `months_on_book`, one line per `credit_score_band`

### Page 3 — Roll-Rate Matrix
- **Matrix visual:** rows = `prior_bucket`, columns = `current_bucket`, values = `roll_rate_pct`, sliced by `credit_score_band`
- Use conditional formatting (data bars or color scale) to make it read like a heatmap

## 3. Useful DAX measures

```DAX
30+ DPD Rate =
DIVIDE(
    SUM(segment_trends[n_delinquent_30plus]),
    SUM(segment_trends[n_accounts])
)

90+ DPD Rate =
DIVIDE(
    SUM(segment_trends[n_delinquent_90plus]),
    SUM(segment_trends[n_accounts])
)

Charge-Off Rate =
DIVIDE(
    SUM(segment_trends[n_charged_off]),
    SUM(segment_trends[n_accounts])
)

MoM Delinquency Change =
VAR CurrentRate = [30+ DPD Rate]
VAR PriorRate =
    CALCULATE(
        [30+ DPD Rate],
        DATEADD(segment_trends[snapshot_month], -1, MONTH)
    )
RETURN CurrentRate - PriorRate
```

## 4. Talking points for interviews

- Explain that the **vintage matrix** answers "are recent originations
  performing better or worse than older ones at the same age" — the key
  question underwriting/risk policy teams ask every quarter.
- Explain that the **roll-rate matrix** is what feeds loss forecasting —
  multiply current bucket balances by their roll-rate to the next bucket
  to project next month's delinquent balances.
- Mention that in a production setting this would connect to a live
  servicing-system extract refreshed monthly (e.g., via a scheduled
  SQL pull or dataflow), rather than a static CSV.
