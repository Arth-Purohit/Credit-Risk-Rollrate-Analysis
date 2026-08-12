"""
vintage_analysis.py
--------------------
Runs the vintage-curve SQL query and produces:
  1. A CSV export for Power BI (outputs/powerbi_exports/vintage_curve.csv)
  2. A heatmap of cumulative 90+ DPD delinquency % by vintage x months-on-book
  3. A line chart comparing vintage curves across credit score bands
"""

import sqlite3
import pandas as pd
import os
from src.visualize import save_heatmap, save_lineplot

DB_PATH = "data/credit_risk.db"
SQL_PATH = "sql/02_vintage_analysis.sql"
EXPORT_DIR = "outputs/powerbi_exports"


def run():
    os.makedirs(EXPORT_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    with open(SQL_PATH, "r") as f:
        query = f.read()
    df = pd.read_sql_query(query, conn)
    conn.close()

    df.to_csv(os.path.join(EXPORT_DIR, "vintage_curve.csv"), index=False)
    print(f"Vintage curve data exported: {len(df):,} rows")

    # ---- Chart 1: heatmap of 90+ DPD % by vintage x months-on-book (overall) ----
    dpd90 = df[df["dpd_bucket"] == "DPD_90_PLUS"]
    agg = (
        dpd90.groupby(["vintage_month", "months_on_book"])["pct_of_cohort"]
        .sum()
        .reset_index()
    )
    pivot = agg.pivot(index="vintage_month", columns="months_on_book", values="pct_of_cohort").fillna(0)
    save_heatmap(
        pivot,
        title="Cumulative 90+ DPD % of Original Cohort, by Vintage x Months on Book",
        filename="vintage_heatmap_90plus_dpd.png",
        figsize=(16, 8),
    )

    # ---- Chart 2: cumulative charge-off curve by credit score band ----
    chg = df[df["dpd_bucket"] == "Charged_Off"]
    chg_by_band = (
        chg.groupby(["credit_score_band", "months_on_book"])["pct_of_cohort"]
        .mean()
        .reset_index()
    )
    save_lineplot(
        chg_by_band,
        x="months_on_book",
        y="pct_of_cohort",
        hue="credit_score_band",
        title="Cumulative Charge-Off Rate by Months on Book, by Credit Score Band",
        filename="vintage_chargeoff_by_band.png",
        ylabel="Cumulative Charge-Off %",
    )

    return df


if __name__ == "__main__":
    run()
