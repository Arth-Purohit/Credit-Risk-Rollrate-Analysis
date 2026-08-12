"""
db_setup.py
-----------
Creates the SQLite database and loads the generated CSVs into it using
the schema defined in sql/01_schema.sql.
"""

import sqlite3
import pandas as pd
import os

DB_PATH = "data/credit_risk.db"
SCHEMA_PATH = "sql/01_schema.sql"


def build_database():
    os.makedirs("data", exist_ok=True)
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    with open(SCHEMA_PATH, "r") as f:
        conn.executescript(f.read())

    customers = pd.read_csv("data/raw/customers.csv")
    performance = pd.read_csv("data/raw/monthly_performance.csv")

    customers.to_sql("customers", conn, if_exists="append", index=False)
    performance.to_sql("monthly_performance", conn, if_exists="append", index=False)

    conn.commit()

    n_cust = conn.execute("SELECT COUNT(*) FROM customers").fetchone()[0]
    n_perf = conn.execute("SELECT COUNT(*) FROM monthly_performance").fetchone()[0]
    conn.close()

    print(f"Database built at {DB_PATH}")
    print(f"  customers table: {n_cust:,} rows")
    print(f"  monthly_performance table: {n_perf:,} rows")


if __name__ == "__main__":
    build_database()
