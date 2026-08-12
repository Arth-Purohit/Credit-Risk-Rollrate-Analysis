-- 03_roll_rate_analysis.sql
-- Roll-rate analysis: for every customer, look at their DPD bucket this
-- month vs. their DPD bucket last month, using LAG() to build a prior/
-- current pair. Aggregating these pairs gives the month-over-month
-- transition (roll-rate) matrix that risk teams use to forecast losses.

WITH ordered_perf AS (
    SELECT
        p.customer_id,
        c.credit_score_band,
        p.snapshot_month,
        p.months_on_book,
        p.dpd_bucket,
        LAG(p.dpd_bucket) OVER (
            PARTITION BY p.customer_id ORDER BY p.months_on_book
        ) AS prior_bucket
    FROM monthly_performance p
    JOIN customers c ON c.customer_id = p.customer_id
),
transitions AS (
    SELECT
        credit_score_band,
        prior_bucket,
        dpd_bucket AS current_bucket,
        COUNT(*) AS n_transitions
    FROM ordered_perf
    WHERE prior_bucket IS NOT NULL
    GROUP BY credit_score_band, prior_bucket, dpd_bucket
),
prior_totals AS (
    SELECT credit_score_band, prior_bucket, SUM(n_transitions) AS n_prior_total
    FROM transitions
    GROUP BY credit_score_band, prior_bucket
)
SELECT
    t.credit_score_band,
    t.prior_bucket,
    t.current_bucket,
    t.n_transitions,
    pt.n_prior_total,
    ROUND(100.0 * t.n_transitions / pt.n_prior_total, 3) AS roll_rate_pct
FROM transitions t
JOIN prior_totals pt
    ON pt.credit_score_band = t.credit_score_band
   AND pt.prior_bucket = t.prior_bucket
ORDER BY t.credit_score_band, t.prior_bucket, t.current_bucket;
