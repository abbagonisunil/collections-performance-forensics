-- ============================================================================
-- 10_monthly_performance.sql
-- 12-Month performance reconstruction and forensic audit of the 11% claim
-- ============================================================================

CREATE OR REPLACE TABLE monthly_performance_audit AS
WITH monthly_raw_payments AS (
    SELECT 
        DATE_TRUNC('month', payment_timestamp) AS reporting_month,
        ROUND(SUM(amount_paid), 2) AS naive_gross_collections_inr,
        COUNT(DISTINCT payment_id) AS raw_payment_rows
    FROM stg_payments
    GROUP BY 1
),
monthly_metrics AS (
    SELECT 
        m.reporting_month,
        m.eligible_accounts,
        m.opening_exposure_inr,
        m.canonical_recovered_inr,
        m.recovery_rate_pct AS canonical_recovery_rate_pct,
        m.contact_rate_pct,
        m.rpc_rate_pct,
        m.ptp_rate_pct,
        m.ptp_kept_rate_pct,
        m.recovery_per_account_inr,
        m.recovery_per_agent_hour_inr,
        COALESCE(rp.naive_gross_collections_inr, m.canonical_recovered_inr) AS naive_gross_collections_inr,
        ROUND(100.0 * COALESCE(rp.naive_gross_collections_inr, m.canonical_recovered_inr) / NULLIF(m.opening_exposure_inr, 0.0), 3) AS naive_recovery_rate_pct
    FROM v_standardized_monthly_metrics m
    LEFT JOIN monthly_raw_payments rp ON m.reporting_month = rp.reporting_month
)
SELECT 
    reporting_month,
    ROW_NUMBER() OVER (ORDER BY reporting_month) AS month_index,
    eligible_accounts,
    opening_exposure_inr,
    
    -- Naive (Reported) Collections & Rate
    naive_gross_collections_inr,
    naive_recovery_rate_pct,
    
    -- Canonical (Audited) Collections & Rate
    canonical_recovered_inr,
    canonical_recovery_rate_pct,
    
    -- Monetary Overstatement from Duplicates/Replays
    ROUND(naive_gross_collections_inr - canonical_recovered_inr, 2) AS monthly_overstatement_inr,
    
    -- Month-over-Month Relative Growth in Naive Recovery Rate
    ROUND(100.0 * (naive_recovery_rate_pct - LAG(naive_recovery_rate_pct) OVER (ORDER BY reporting_month)) 
          / NULLIF(LAG(naive_recovery_rate_pct) OVER (ORDER BY reporting_month), 0), 2) AS naive_mom_recovery_growth_pct,
          
    -- Month-over-Month Relative Growth in Canonical Recovery Rate
    ROUND(100.0 * (canonical_recovery_rate_pct - LAG(canonical_recovery_rate_pct) OVER (ORDER BY reporting_month)) 
          / NULLIF(LAG(canonical_recovery_rate_pct) OVER (ORDER BY reporting_month), 0), 2) AS canonical_mom_recovery_growth_pct,
          
    -- Absolute Percentage-Point Change in Canonical Rate
    ROUND(canonical_recovery_rate_pct - LAG(canonical_recovery_rate_pct) OVER (ORDER BY reporting_month), 3) AS canonical_mom_pp_change,
    
    -- Operational Efficiency Indicators
    contact_rate_pct,
    rpc_rate_pct,
    ptp_rate_pct,
    ptp_kept_rate_pct,
    recovery_per_account_inr,
    recovery_per_agent_hour_inr
FROM monthly_metrics
ORDER BY reporting_month;

-- Forensic Verdict on the "11% Month-on-Month" Claim
CREATE OR REPLACE VIEW v_audit_verdict_11_pct_claim AS
WITH audit_summary AS (
    SELECT 
        COUNT(*) AS evaluated_months_count,
        ROUND(AVG(naive_mom_recovery_growth_pct), 2) AS avg_reported_naive_mom_growth_pct,
        ROUND(AVG(canonical_mom_recovery_growth_pct), 2) AS avg_audited_canonical_mom_growth_pct,
        ROUND(AVG(naive_mom_recovery_growth_pct) - AVG(canonical_mom_recovery_growth_pct), 2) AS growth_rate_distortion_pct,
        ROUND(SUM(monthly_overstatement_inr), 2) AS cumulative_recovery_overstatement_inr,
        ROUND(SUM(canonical_recovered_inr), 2) AS total_canonical_recovered_inr,
        ROUND(SUM(naive_gross_collections_inr), 2) AS total_naive_gross_collections_inr
    FROM monthly_performance_audit
    WHERE month_index > 1
)
SELECT 
    evaluated_months_count,
    avg_reported_naive_mom_growth_pct,
    avg_audited_canonical_mom_growth_pct,
    growth_rate_distortion_pct,
    cumulative_recovery_overstatement_inr,
    total_canonical_recovered_inr,
    total_naive_gross_collections_inr,
    CASE 
        WHEN evaluated_months_count IS NULL OR evaluated_months_count = 0 THEN 'AWAITING_RAW_COLLECTIONS_DATA'
        WHEN avg_audited_canonical_mom_growth_pct >= 10.5 THEN 'SUPPORTED_REAL'
        WHEN avg_reported_naive_mom_growth_pct >= 10.0 AND avg_audited_canonical_mom_growth_pct < 6.0 THEN 'DISPROVEN_ARTIFICIAL_INFLATION'
        ELSE 'AMBIGUOUS_UNVERIFIED'
    END AS forensic_verdict
FROM audit_summary;
