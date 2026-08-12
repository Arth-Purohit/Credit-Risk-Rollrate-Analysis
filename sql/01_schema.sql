-- 01_schema.sql
-- Schema for the credit risk roll-rate / vintage analysis database.

DROP TABLE IF EXISTS monthly_performance;
DROP TABLE IF EXISTS customers;

CREATE TABLE customers (
    customer_id         INTEGER PRIMARY KEY,
    vintage_month        TEXT NOT NULL,      -- origination month (YYYY-MM-01)
    credit_score_band    TEXT NOT NULL,      -- Prime / Near_Prime / Subprime
    credit_score         INTEGER NOT NULL,
    income_band          TEXT NOT NULL,      -- Low / Medium / High
    region                TEXT NOT NULL,
    loan_purpose          TEXT NOT NULL,
    origination_balance   REAL NOT NULL
);

CREATE TABLE monthly_performance (
    customer_id     INTEGER NOT NULL,
    snapshot_month  TEXT NOT NULL,           -- reporting month (YYYY-MM-01)
    months_on_book  INTEGER NOT NULL,
    dpd_bucket      TEXT NOT NULL,           -- Current / DPD_30 / DPD_60 / DPD_90_PLUS / Charged_Off / Paid_Off
    balance         REAL NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

CREATE INDEX idx_perf_customer ON monthly_performance(customer_id);
CREATE INDEX idx_perf_snapshot ON monthly_performance(snapshot_month);
CREATE INDEX idx_perf_mob ON monthly_performance(months_on_book);
CREATE INDEX idx_cust_vintage ON customers(vintage_month);
CREATE INDEX idx_cust_band ON customers(credit_score_band);
