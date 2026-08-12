"""
run_all.py
----------
End-to-end pipeline runner:
  1. Generate synthetic loan-level performance data
  2. Load it into a SQLite database
  3. Run vintage-curve analysis
  4. Run roll-rate analysis
  5. Run segment-level delinquency trend analysis

Run with:  python run_all.py
"""

import time
import sys


def main():
    t0 = time.time()

    print("=" * 70)
    print("STEP 1/4: Generating synthetic portfolio data")
    print("=" * 70)
    from data.generate_data import generate
    generate()

    print("\n" + "=" * 70)
    print("STEP 2/4: Building SQLite database")
    print("=" * 70)
    from src.db_setup import build_database
    build_database()

    print("\n" + "=" * 70)
    print("STEP 3/4: Running vintage curve analysis")
    print("=" * 70)
    from src.vintage_analysis import run as run_vintage
    run_vintage()

    print("\n" + "=" * 70)
    print("STEP 4/4: Running roll-rate analysis")
    print("=" * 70)
    from src.roll_rate_analysis import run as run_rollrate
    run_rollrate()

    print("\n" + "=" * 70)
    print("STEP 5/5: Running segment-level delinquency analysis")
    print("=" * 70)
    from src.segment_analysis import run as run_segment
    run_segment()

    elapsed = time.time() - t0
    print("\n" + "=" * 70)
    print(f"PIPELINE COMPLETE in {elapsed:.1f}s")
    print("=" * 70)
    print("""
Outputs:
  data/credit_risk.db                  -> SQLite database (query it directly!)
  outputs/charts/                      -> PNG + interactive HTML charts
  outputs/powerbi_exports/             -> CSVs ready to import into Power BI

Next steps:
  - Open outputs/charts/*.png and *.html to view the analysis
  - Open powerbi/DASHBOARD_GUIDE.md for Power BI dashboard build instructions
  - Explore data/credit_risk.db with any SQLite client or `sqlite3 data/credit_risk.db`
""")


if __name__ == "__main__":
    sys.path.insert(0, ".")
    main()
