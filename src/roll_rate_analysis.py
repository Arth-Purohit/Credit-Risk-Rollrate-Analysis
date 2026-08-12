"""
roll_rate_analysis.py
-----------------------
Runs the roll-rate SQL query (month-over-month bucket transitions) and
produces:
  1. A CSV export for Power BI (outputs/powerbi_exports/roll_rates.csv)
  2. A roll-rate matrix heatmap for the overall portfolio
  3. Roll-rate matrix heatmaps split out by credit score band
"""

import sqlite3
import pandas as pd
import os
from src.visualize import save_heatmap

DB_PATH = "data/credit_risk.db"
SQL_PATH = "sql/03_roll_rate_analysis.sql"
EXPORT_DIR = "outputs/powerbi_exports"

BUCKET_ORDER = ["Current", "DPD_30", "DPD_60", "DPD_90_PLUS", "Charged_Off", "Paid_Off"]


def run():
    os.makedirs(EXPORT_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    with open(SQL_PATH, "r") as f:
        query = f.read()
    df = pd.read_sql_query(query, conn)
    conn.close()

    df.to_csv(os.path.join(EXPORT_DIR, "roll_rates.csv"), index=False)
    print(f"Roll-rate data exported: {len(df):,} rows")

    # ---- Overall roll-rate matrix (collapsed across credit bands) ----
    overall = (
        df.groupby(["prior_bucket", "current_bucket"])
        .apply(lambda g: pd.Series({
            "n_transitions": g["n_transitions"].sum(),
        }))
        .reset_index()
    )
    prior_totals = overall.groupby("prior_bucket")["n_transitions"].transform("sum")
    overall["roll_rate_pct"] = (100 * overall["n_transitions"] / prior_totals).round(2)

    pivot_overall = overall.pivot(index="prior_bucket", columns="current_bucket", values="roll_rate_pct").fillna(0)
    pivot_overall = pivot_overall.reindex(index=BUCKET_ORDER, columns=BUCKET_ORDER, fill_value=0)
    save_heatmap(
        pivot_overall,
        title="Overall Portfolio Roll-Rate Matrix (Month-over-Month, %)",
        filename="roll_rate_matrix_overall.png",
        fmt=".1f",
        cmap="Blues",
        figsize=(9, 6.5),
    )

    # ---- Per credit-score-band roll-rate matrices ----
    for band in df["credit_score_band"].unique():
        sub = df[df["credit_score_band"] == band]
        pivot = sub.pivot(index="prior_bucket", columns="current_bucket", values="roll_rate_pct").fillna(0)
        pivot = pivot.reindex(index=BUCKET_ORDER, columns=BUCKET_ORDER, fill_value=0)
        save_heatmap(
            pivot,
            title=f"Roll-Rate Matrix - {band} Segment (%)",
            filename=f"roll_rate_matrix_{band.lower()}.png",
            fmt=".1f",
            cmap="Blues",
            figsize=(9, 6.5),
        )

    return df


if __name__ == "__main__":
    run()
