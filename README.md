# Credit Portfolio Delinquency & Roll-Rate Analysis

A SQL + Python + Power BI project that replicates how a **Credit Risk
Management** team monitors portfolio health at a card issuer: tracking how
accounts move through delinquency stages, comparing how different
origination cohorts ("vintages") season over time, and reporting
risk trends by customer segment.

## Business problem

When a lender originates loans/credit lines every month, the immediate
question isn't "did this loan default" — that takes years to know. The
real, actionable question is: **"is this month's cohort of accounts
behaving better or worse than prior cohorts at the same age, and how
fast are delinquent accounts rolling toward charge-off?"**

This project answers three questions a Risk Analyst is expected to own:

1. **Vintage analysis** — How does delinquency develop over the life of a
   loan, and are recent origination vintages riskier than older ones?
2. **Roll-rate analysis** — What % of accounts in each delinquency bucket
   (Current, 30/60/90+ DPD) "roll" to the next worse bucket each month?
   This is the core input to loss forecasting and reserve/provisioning
   estimates.
3. **Segment monitoring** — Which customer segments (credit score band,
   income band, region) are driving delinquency, and is it improving or
   worsening month over month?

## Data

The dataset is **synthetically generated** (see `data/generate_data.py`)
using a Markov-chain simulation calibrated so that Prime / Near-Prime /
Subprime segments have realistic, differentiated transition behavior
between delinquency states. This was a deliberate choice over using a
public dataset — real loan-level monthly performance panels (the kind
risk teams actually work with) aren't publicly available, so simulating
one with realistic transition dynamics is the closest honest substitute.
Every script in this repo works unmodified against a real servicing
extract if you swap the data source.

- **~22,600 customers** across **23 monthly origination vintages**
- **~270,000 monthly performance snapshots**
- DPD buckets: `Current → DPD_30 → DPD_60 → DPD_90_PLUS → Charged_Off`,
  plus a `Paid_Off` exit state

## Tech stack

| Layer | Tools |
|---|---|
| Data generation | Python (numpy, pandas) |
| Storage / querying | SQLite, raw SQL (window functions: `LAG`, CTEs) |
| Analysis | Python (pandas) |
| Visualization | seaborn, matplotlib, plotly |
| Reporting dashboard | Power BI |

No ML/AI — this is intentionally built around the statistical and
cohort-analysis techniques (vintage curves, transition matrices, segment
rate monitoring) that a Risk Analytics team uses operationally, not a
predictive model.

## Project structure

```
credit-risk-rollrate-analysis/
├── data/
│   ├── generate_data.py          # synthetic data generator (Markov simulation)
│   └── raw/                      # generated CSVs (created on first run)
├── sql/
│   ├── 01_schema.sql             # table definitions
│   ├── 02_vintage_analysis.sql   # vintage curve query
│   ├── 03_roll_rate_analysis.sql # roll-rate matrix query (uses LAG())
│   └── 04_segment_analysis.sql   # segment delinquency trend query
├── src/
│   ├── db_setup.py               # loads CSVs into SQLite
│   ├── vintage_analysis.py       # runs vintage SQL + builds charts
│   ├── roll_rate_analysis.py     # runs roll-rate SQL + builds charts
│   ├── segment_analysis.py       # runs segment SQL + builds charts
│   └── visualize.py              # shared plotting helpers
├── outputs/
│   ├── charts/                   # generated PNG/HTML charts
│   └── powerbi_exports/          # CSVs shaped for Power BI import
├── powerbi/
│   └── DASHBOARD_GUIDE.md        # step-by-step Power BI build guide + DAX
├── run_all.py                    # runs the full pipeline end to end
└── requirements.txt
```

## How to run

### 1. Set up the environment

```bash
cd credit-risk-rollrate-analysis
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Run the full pipeline

```bash
python run_all.py
```

This single command will:
1. Generate the synthetic loan-level dataset (`data/raw/*.csv`)
2. Build the SQLite database (`data/credit_risk.db`)
3. Run the vintage-curve SQL query and save charts + a Power BI CSV export
4. Run the roll-rate SQL query and save charts + a Power BI CSV export
5. Run the segment-trend SQL query and save charts + a Power BI CSV export

Takes about 15–20 seconds end to end.

### 3. Explore the outputs

- **Charts:** open the `.png` and `.html` files in `outputs/charts/`
- **SQL:** open `data/credit_risk.db` directly:
  ```bash
  sqlite3 data/credit_risk.db
  sqlite> .read sql/03_roll_rate_analysis.sql
  ```
- **Power BI:** follow `powerbi/DASHBOARD_GUIDE.md` — import the three
  CSVs in `outputs/powerbi_exports/` and build the dashboard using the
  page layout and DAX measures provided there.

### Run steps individually (optional)

```bash
python -m data.generate_data
python -m src.db_setup
python -m src.vintage_analysis
python -m src.roll_rate_analysis
python -m src.segment_analysis
```

## Key outputs

| Output | What it shows |
|---|---|
| `vintage_heatmap_90plus_dpd.png` | Classic "vintage triangle" — cumulative 90+ DPD % by vintage x months-on-book |
| `vintage_chargeoff_by_band.png` | Cumulative charge-off curves, Prime vs Near-Prime vs Subprime |
| `roll_rate_matrix_overall.png` | Month-over-month transition probabilities between DPD buckets |
| `roll_rate_matrix_{band}.png` | Same, split by credit score band |
| `segment_delinquency_trend.html` | Interactive 30+ DPD rate trend by segment |

## Sample findings (from the generated dataset)

- Subprime accounts roll from `DPD_30 → DPD_60` at a meaningfully higher
  rate than Prime accounts, confirming the transition model — but more
  importantly, it demonstrates the analysis correctly surfaces known
  risk hierarchies, the same sanity check a real risk team would run.
- ~60% of accounts that reach 90+ DPD charge off the following month
  across all segments — useful as a loss-forecasting rule of thumb.
- Recent vintages show early-stage delinquency in line with historical
  cohorts at the same months-on-book, i.e., no origination quality
  drift — the kind of statement a quarterly vintage review would need
  to make.

## Why this project

Built to demonstrate the analytical workflows used by Risk/Credit teams
at consumer lenders and card issuers: cohort/vintage analysis, roll-rate
modeling for loss forecasting, and segment-level portfolio monitoring —
using core SQL, Python, and Power BI rather than predictive modeling.
