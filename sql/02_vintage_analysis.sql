-- 02_vintage_analysis.sql
-- Vintage curve: for each origination vintage, tracks what % of the
-- ORIGINAL cohort is sitting in each DPD bucket at every month-on-book.
-- This is the classic "vintage triangle" risk teams use to compare how
-- different origination cohorts season over time.

WITH cohort_size AS (
    SELECT vintage_month, COUNT(*) AS cohort_accounts
    FROM customers
    GROUP BY vintage_month
),
bucket_counts AS (
    SELECT
        c.vintage_month,
        c.credit_score_band,
        p.months_on_book,
        p.dpd_bucket,
        COUNT(*) AS n_accounts,
        SUM(p.balance) AS total_balance
    FROM monthly_performance p
    JOIN customers c ON c.customer_id = p.customer_id
    GROUP BY c.vintage_month, c.credit_score_band, p.months_on_book, p.dpd_bucket
)
SELECT
    b.vintage_month,
    b.credit_score_band,
    b.months_on_book,
    b.dpd_bucket,
    b.n_accounts,
    b.total_balance,
    cs.cohort_accounts,
    ROUND(100.0 * b.n_accounts / cs.cohort_accounts, 3) AS pct_of_cohort
FROM bucket_counts b
JOIN cohort_size cs ON cs.vintage_month = b.vintage_month
ORDER BY b.vintage_month, b.credit_score_band, b.months_on_book, b.dpd_bucket;
