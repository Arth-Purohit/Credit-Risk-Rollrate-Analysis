"""
generate_data.py
-----------------
Generates a synthetic but realistic loan-level dataset for a credit card /
installment loan portfolio, simulating monthly delinquency-bucket
performance using a Markov transition model.

This mimics the kind of loan-level performance data a Risk Analytics team
would pull from a servicing system: one row per customer per snapshot
month, with the delinquency bucket ("DPD state") they were in that month.

Output:
    data/raw/customers.csv            -> one row per customer (dimension table)
    data/raw/monthly_performance.csv  -> one row per customer per month (fact table)
"""

import numpy as np
import pandas as pd
from datetime import date
from dateutil.relativedelta import relativedelta
import os

# ------------------------------------------------------------------
# Config
# ------------------------------------------------------------------
SEED = 42
np.random.seed(SEED)

AS_OF_DATE = date(2026, 7, 1)          # most recent complete reporting month
N_VINTAGES = 23                        # origination months to simulate (~2 years)
CUSTOMERS_PER_VINTAGE_RANGE = (700, 1200)
MAX_MONTHS_ON_BOOK = 24                # cap loan life we simulate

STATES = ["Current", "DPD_30", "DPD_60", "DPD_90_PLUS", "Charged_Off", "Paid_Off"]
STATE_IDX = {s: i for i, s in enumerate(STATES)}
TERMINAL_STATES = {"Charged_Off", "Paid_Off"}

CREDIT_BANDS = ["Prime", "Near_Prime", "Subprime"]
CREDIT_BAND_WEIGHTS = [0.40, 0.35, 0.25]

INCOME_BANDS = ["Low", "Medium", "High"]
INCOME_BAND_WEIGHTS = [0.30, 0.45, 0.25]

REGIONS = ["Northeast", "Midwest", "South", "West"]
REGION_WEIGHTS = [0.22, 0.24, 0.32, 0.22]

LOAN_PURPOSES = ["Card_Refinance", "Retail_Purchase", "Travel", "Cash_Advance", "General_Spend"]

# Monthly transition matrices, keyed by credit band.
# Rows/cols follow STATES order. Rows must sum to 1.
TRANSITIONS = {
    "Prime": np.array([
        # Current   DPD30  DPD60  DPD90+ ChgOff PaidOff
        [0.9650, 0.0200, 0.0000, 0.0000, 0.0000, 0.0150],   # Current
        [0.5500, 0.2000, 0.2500, 0.0000, 0.0000, 0.0000],   # DPD_30
        [0.0000, 0.1500, 0.2000, 0.6500, 0.0000, 0.0000],   # DPD_60
        [0.0000, 0.0000, 0.0500, 0.3500, 0.6000, 0.0000],   # DPD_90_PLUS
        [0.0000, 0.0000, 0.0000, 0.0000, 1.0000, 0.0000],   # Charged_Off (absorbing)
        [0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 1.0000],   # Paid_Off (absorbing)
    ]),
    "Near_Prime": np.array([
        [0.9450, 0.0400, 0.0000, 0.0000, 0.0000, 0.0150],
        [0.4500, 0.2500, 0.3000, 0.0000, 0.0000, 0.0000],
        [0.0000, 0.1200, 0.2300, 0.6500, 0.0000, 0.0000],
        [0.0000, 0.0000, 0.0400, 0.3600, 0.6000, 0.0000],
        [0.0000, 0.0000, 0.0000, 0.0000, 1.0000, 0.0000],
        [0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 1.0000],
    ]),
    "Subprime": np.array([
        [0.9100, 0.0750, 0.0000, 0.0000, 0.0000, 0.0150],
        [0.3500, 0.3000, 0.3500, 0.0000, 0.0000, 0.0000],
        [0.0000, 0.1000, 0.2500, 0.6500, 0.0000, 0.0000],
        [0.0000, 0.0000, 0.0300, 0.3700, 0.6000, 0.0000],
        [0.0000, 0.0000, 0.0000, 0.0000, 1.0000, 0.0000],
        [0.0000, 0.0000, 0.0000, 0.0000, 0.0000, 1.0000],
    ]),
}


def month_range_back(as_of: date, n: int):
    """Return n month-start dates ending at as_of (oldest first)."""
    return [as_of - relativedelta(months=(n - 1 - i)) for i in range(n)]


def simulate_customer_path(credit_band, months_available):
    """
    Simulate a single customer's monthly DPD-state path via Markov chain.
    Once a terminal state (Charged_Off / Paid_Off) is reached, it is carried
    forward for the remaining months so cumulative vintage curves behave
    like real charge-off/payoff curves (monotonic, not disappearing).
    """
    trans = TRANSITIONS[credit_band]
    path = []
    state = "Current"
    for m in range(1, months_available + 1):
        path.append(state)
        if state in TERMINAL_STATES:
            # carry the terminal state forward for the rest of the horizon
            path.extend([state] * (months_available - m))
            break
        probs = trans[STATE_IDX[state]]
        state = np.random.choice(STATES, p=probs)
    return path


def generate():
    vintages = month_range_back(AS_OF_DATE, N_VINTAGES)

    customers = []
    performance_rows = []
    customer_id = 100000

    for vintage_date in vintages:
        n_customers = np.random.randint(*CUSTOMERS_PER_VINTAGE_RANGE)
        months_available = min(
            MAX_MONTHS_ON_BOOK,
            (AS_OF_DATE.year - vintage_date.year) * 12 + (AS_OF_DATE.month - vintage_date.month) + 1,
        )

        for _ in range(n_customers):
            customer_id += 1
            credit_band = np.random.choice(CREDIT_BANDS, p=CREDIT_BAND_WEIGHTS)
            income_band = np.random.choice(INCOME_BANDS, p=INCOME_BAND_WEIGHTS)
            region = np.random.choice(REGIONS, p=REGION_WEIGHTS)
            purpose = np.random.choice(LOAN_PURPOSES)

            # credit score roughly consistent with band
            score_ranges = {"Prime": (720, 850), "Near_Prime": (660, 719), "Subprime": (580, 659)}
            credit_score = np.random.randint(*score_ranges[credit_band])

            base_amt = {"Prime": 9000, "Near_Prime": 6000, "Subprime": 3500}[credit_band]
            loan_amount = round(float(np.random.gamma(shape=3.0, scale=base_amt / 3.0)), 2)

            customers.append({
                "customer_id": customer_id,
                "vintage_month": vintage_date.strftime("%Y-%m-01"),
                "credit_score_band": credit_band,
                "credit_score": credit_score,
                "income_band": income_band,
                "region": region,
                "loan_purpose": purpose,
                "origination_balance": loan_amount,
            })

            path = simulate_customer_path(credit_band, months_available)
            balance = loan_amount
            for i, state in enumerate(path):
                snapshot_month = vintage_date + relativedelta(months=i)
                months_on_book = i + 1

                if state == "Paid_Off":
                    balance = 0.0
                elif state == "Charged_Off":
                    balance = round(balance, 2)
                else:
                    # amortize balance down gently over time, add noise
                    decay = np.random.uniform(0.03, 0.06)
                    balance = max(0.0, balance * (1 - decay))

                performance_rows.append({
                    "customer_id": customer_id,
                    "snapshot_month": snapshot_month.strftime("%Y-%m-01"),
                    "months_on_book": months_on_book,
                    "dpd_bucket": state,
                    "balance": round(balance, 2),
                })

    customers_df = pd.DataFrame(customers)
    performance_df = pd.DataFrame(performance_rows)

    os.makedirs("data/raw", exist_ok=True)
    customers_df.to_csv("data/raw/customers.csv", index=False)
    performance_df.to_csv("data/raw/monthly_performance.csv", index=False)

    print(f"Generated {len(customers_df):,} customers across {N_VINTAGES} vintages.")
    print(f"Generated {len(performance_df):,} monthly performance rows.")
    print("Saved to data/raw/customers.csv and data/raw/monthly_performance.csv")


if __name__ == "__main__":
    generate()
