-- 04_segment_analysis.sql
-- Segment-level delinquency (30+ DPD) rate by snapshot month, sliced by
-- credit score band, income band and region. Used for exec-level
-- portfolio health reporting (feeds the Power BI dashboard).

WITH flagged AS (
    SELECT
        p.snapshot_month,
        c.credit_score_band,
        c.income_band,
        c.region,
        p.dpd_bucket,
        CASE WHEN p.dpd_bucket IN ('DPD_30','DPD_60','DPD_90_PLUS') THEN 1 ELSE 0 END AS is_delinquent_30plus,
        CASE WHEN p.dpd_bucket IN ('DPD_90_PLUS') THEN 1 ELSE 0 END AS is_delinquent_90plus,
        CASE WHEN p.dpd_bucket = 'Charged_Off' THEN 1 ELSE 0 END AS is_charged_off,
        p.balance
    FROM monthly_performance p
    JOIN customers c ON c.customer_id = p.customer_id
)
SELECT
    snapshot_month,
    credit_score_band,
    income_band,
    region,
    COUNT(*) AS n_accounts,
    SUM(is_delinquent_30plus) AS n_delinquent_30plus,
    SUM(is_delinquent_90plus) AS n_delinquent_90plus,
    SUM(is_charged_off) AS n_charged_off,
    ROUND(100.0 * SUM(is_delinquent_30plus) / COUNT(*), 3) AS delinquency_30plus_rate_pct,
    ROUND(100.0 * SUM(is_delinquent_90plus) / COUNT(*), 3) AS delinquency_90plus_rate_pct,
    ROUND(100.0 * SUM(is_charged_off) / COUNT(*), 3) AS charge_off_rate_pct,
    ROUND(SUM(balance), 2) AS total_balance
FROM flagged
GROUP BY snapshot_month, credit_score_band, income_band, region
ORDER BY snapshot_month, credit_score_band, income_band, region;
