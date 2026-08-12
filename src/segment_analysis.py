"""
segment_analysis.py
---------------------
Runs the segment-level delinquency trend SQL query and produces:
  1. A CSV export for Power BI (outputs/powerbi_exports/segment_trends.csv)
  2. An interactive plotly line chart: 30+ DPD rate over time by credit band
  3. A static seaborn bar chart: current charge-off rate by region
"""

import sqlite3
import pandas as pd
import os
from src.visualize import save_plotly_line, save_lineplot

DB_PATH = "data/credit_risk.db"
SQL_PATH = "sql/04_segment_analysis.sql"
EXPORT_DIR = "outputs/powerbi_exports"


def run():
    os.makedirs(EXPORT_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    with open(SQL_PATH, "r") as f:
        query = f.read()
    df = pd.read_sql_query(query, conn)
    conn.close()

    df.to_csv(os.path.join(EXPORT_DIR, "segment_trends.csv"), index=False)
    print(f"Segment trend data exported: {len(df):,} rows")

    # ---- Portfolio-level 30+ DPD rate over time, by credit score band ----
    band_trend = (
        df.groupby(["snapshot_month", "credit_score_band"])
        .apply(lambda g: pd.Series({
            "n_accounts": g["n_accounts"].sum(),
            "n_delinquent_30plus": g["n_delinquent_30plus"].sum(),
        }))
        .reset_index()
    )
    band_trend["delinquency_30plus_rate_pct"] = (
        100 * band_trend["n_delinquent_30plus"] / band_trend["n_accounts"]
    ).round(2)

    save_plotly_line(
        band_trend,
        x="snapshot_month",
        y="delinquency_30plus_rate_pct",
        color="credit_score_band",
        title="30+ DPD Delinquency Rate Over Time, by Credit Score Band",
        filename="segment_delinquency_trend.html",
    )

    save_lineplot(
        band_trend,
        x="snapshot_month",
        y="delinquency_30plus_rate_pct",
        hue="credit_score_band",
        title="30+ DPD Delinquency Rate Over Time, by Credit Score Band",
        filename="segment_delinquency_trend.png",
        ylabel="30+ DPD Rate (%)",
    )

    # ---- Latest-month charge-off rate by region ----
    latest_month = df["snapshot_month"].max()
    latest = df[df["snapshot_month"] == latest_month]
    region_summary = (
        latest.groupby("region")
        .apply(lambda g: pd.Series({
            "n_accounts": g["n_accounts"].sum(),
            "n_charged_off": g["n_charged_off"].sum(),
        }))
        .reset_index()
    )
    region_summary["charge_off_rate_pct"] = (
        100 * region_summary["n_charged_off"] / region_summary["n_accounts"]
    ).round(2)
    region_summary.to_csv(os.path.join(EXPORT_DIR, "region_summary_latest_month.csv"), index=False)

    return df


if __name__ == "__main__":
    run()
