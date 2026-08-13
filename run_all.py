"""
run_all.py
----------
End-to-end pipeline runner:
  1. Load your CSVs (from datasets/raw/) into a SQLite database
  2. Run vintage-curve analysis
  3. Run roll-rate analysis
  4. Run segment-level delinquency trend analysis

Before running this, make sure your data is in place:
    datasets/raw/customers.csv
    datasets/raw/monthly_performance.csv

Run with:  python run_all.py
"""

import time
import sys


def main():
    t0 = time.time()

    print("=" * 70)
    print("STEP 1/4: Building SQLite database")
    print("=" * 70)
    from src.db_setup import build_database
    build_database()

    print("\n" + "=" * 70)
    print("STEP 2/4: Running vintage curve analysis")
    print("=" * 70)
    from src.vintage_analysis import run as run_vintage
    run_vintage()

    print("\n" + "=" * 70)
    print("STEP 3/4: Running roll-rate analysis")
    print("=" * 70)
    from src.roll_rate_analysis import run as run_rollrate
    run_rollrate()

    print("\n" + "=" * 70)
    print("STEP 4/4: Running segment-level delinquency analysis")
    print("=" * 70)
    from src.segment_analysis import run as run_segment
    run_segment()

    elapsed = time.time() - t0
    print("\n" + "=" * 70)
    print(f"PIPELINE COMPLETE in {elapsed:.1f}s")
    print("=" * 70)
    print("""
Outputs:
  datasets/credit_risk.db              -> SQLite database (query it directly!)
  outputs/charts/                      -> PNG + interactive HTML charts
  outputs/powerbi_exports/             -> CSVs ready to import into Power BI

Next steps:
  - Open outputs/charts/*.png and *.html to view the analysis
  - Open powerbi/DASHBOARD_GUIDE.md for Power BI dashboard build instructions
  - Explore datasets/credit_risk.db with any SQLite client or `sqlite3 datasets/credit_risk.db`
""")


if __name__ == "__main__":
    sys.path.insert(0, ".")
    main()
