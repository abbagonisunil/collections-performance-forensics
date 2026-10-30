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
    
    -- Metric 1: Absolute Collection Cash Growth (Current cash - Previous cash)
    ROUND(canonical_recovered_inr - LAG(canonical_recovered_inr) OVER (ORDER BY reporting_month), 2) AS absolute_collection_growth_inr,
    
    -- Metric 2: Percentage-Point Change (Current rate - Previous rate)
    ROUND(canonical_recovery_rate_pct - LAG(canonical_recovery_rate_pct) OVER (ORDER BY reporting_month), 3) AS percentage_point_change,
    
    -- Metric 3: Relative Month-over-Month Growth in Canonical Rate ((Rate_t - Rate_{t-1}) / Rate_{t-1} * 100)
    ROUND(100.0 * (canonical_recovery_rate_pct - LAG(canonical_recovery_rate_pct) OVER (ORDER BY reporting_month)) 
          / NULLIF(LAG(canonical_recovery_rate_pct) OVER (ORDER BY reporting_month), 0), 2) AS relative_mom_growth_pct,
          
    -- Relative MoM Growth in Reported Naive Rate
    ROUND(100.0 * (naive_recovery_rate_pct - LAG(naive_recovery_rate_pct) OVER (ORDER BY reporting_month)) 
          / NULLIF(LAG(naive_recovery_rate_pct) OVER (ORDER BY reporting_month), 0), 2) AS naive_mom_recovery_growth_pct,

    -- Duplicate or Rejected Payment Amounts (Naive event cash - Canonical settled cash)
    ROUND(naive_gross_collections_inr - canonical_recovered_inr, 2) AS duplicate_or_rejected_payment_amounts_inr,
    
    -- Eligible Population Changes (Cohort stability)
    ROUND(100.0 * (eligible_accounts - LAG(eligible_accounts) OVER (ORDER BY reporting_month)) 
          / NULLIF(LAG(eligible_accounts) OVER (ORDER BY reporting_month), 0), 2) AS eligible_population_change_pct,
          
    -- Data Completeness Indicator
    CASE WHEN eligible_accounts > 0 AND opening_exposure_inr > 0 THEN 100.0 ELSE 0.0 END AS data_completeness_pct,

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
-- Required Verdict Enum: SUPPORTED | CONTRADICTED | NOT_VERIFIABLE
CREATE OR REPLACE VIEW v_audit_verdict_11_pct_claim AS
WITH audit_summary AS (
    SELECT 
        COUNT(*) AS evaluated_months_count,
        MIN(reporting_month) AS period_start,
        MAX(reporting_month) AS period_end,
        ROUND(AVG(naive_mom_recovery_growth_pct), 2) AS avg_reported_naive_mom_growth_pct,
        ROUND(AVG(relative_mom_growth_pct), 2) AS avg_audited_canonical_mom_growth_pct,
        ROUND(AVG(naive_mom_recovery_growth_pct) - AVG(relative_mom_growth_pct), 2) AS growth_rate_distortion_pct,
        ROUND(SUM(duplicate_or_rejected_payment_amounts_inr), 2) AS cumulative_recovery_overstatement_inr,
        ROUND(SUM(canonical_recovered_inr), 2) AS total_canonical_recovered_inr,
        ROUND(SUM(opening_exposure_inr), 2) AS total_opening_exposure_inr,
        ROUND(SUM(naive_gross_collections_inr), 2) AS total_naive_gross_collections_inr
    FROM monthly_performance_audit
    WHERE month_index > 1
)
SELECT 
    evaluated_months_count,
    period_start,
    period_end,
    total_canonical_recovered_inr AS numerator_cash_recovered,
    total_opening_exposure_inr AS denominator_opening_exposure,
    'Canonical Rate = Total Realized Settled Cash / Total Opening Exposure * 100; Relative MoM = (Rate_t - Rate_{t-1}) / Rate_{t-1} * 100' AS formula,
    avg_reported_naive_mom_growth_pct,
    avg_audited_canonical_mom_growth_pct,
    growth_rate_distortion_pct,
    cumulative_recovery_overstatement_inr,
    total_canonical_recovered_inr,
    total_naive_gross_collections_inr,
    CASE 
        WHEN evaluated_months_count IS NULL OR evaluated_months_count = 0 THEN 'NOT_VERIFIABLE'
        WHEN avg_audited_canonical_mom_growth_pct >= 10.5 THEN 'SUPPORTED'
        WHEN avg_reported_naive_mom_growth_pct >= 10.0 AND avg_audited_canonical_mom_growth_pct < 6.0 THEN 'CONTRADICTED'
        ELSE 'NOT_VERIFIABLE'
    END AS forensic_verdict,
    CASE 
        WHEN evaluated_months_count IS NULL OR evaluated_months_count = 0 THEN 
            'The claim cannot currently be verified because required collections data and original reporting definitions are unavailable.'
        WHEN avg_audited_canonical_mom_growth_pct >= 10.5 THEN 
            'Audited canonical cash collections substantiate genuine ~11% average relative month-on-month recovery rate growth.'
        WHEN avg_reported_naive_mom_growth_pct >= 10.0 AND avg_audited_canonical_mom_growth_pct < 6.0 THEN 
            'The 11% claim is contradicted: naive reporting conflated duplicate webhook events, whereas canonical settled growth is significantly lower.'
        ELSE 
            'Historical data does not consistently verify the claimed 11% month-on-month improvement across canonical definitions.'
    END AS verdict_explanation
FROM audit_summary;
