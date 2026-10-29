-- ============================================================================
-- 09_metrics.sql
-- Verified, independent metric calculations challenging legacy reporting
-- ============================================================================

-- View: Standardized Metrics by Month
CREATE OR REPLACE VIEW v_standardized_monthly_metrics AS
WITH monthly_cohort AS (
    SELECT 
        DATE_TRUNC('month', due_date) AS reporting_month,
        COUNT(DISTINCT account_id) AS eligible_accounts_count,
        ROUND(SUM(opening_principal), 2) AS opening_exposure_inr
    FROM dim_account
    WHERE dpd > 0
    GROUP BY 1
),
monthly_targeting AS (
    SELECT 
        DATE_TRUNC('month', target_date) AS reporting_month,
        COUNT(DISTINCT account_id) AS targeted_accounts_count
    FROM stg_daily_targeting
    WHERE is_suppressed = FALSE
    GROUP BY 1
),
monthly_calls AS (
    SELECT 
        DATE_TRUNC('month', call_start_time) AS reporting_month,
        COUNT(DISTINCT call_id) AS total_call_attempts,
        COUNT(DISTINCT account_id) AS unique_accounts_attempted,
        COUNT(DISTINCT CASE WHEN duration_seconds >= 15 THEN account_id END) AS connected_accounts,
        COUNT(DISTINCT CASE WHEN disposition_category = 'RPC' THEN account_id END) AS rpc_accounts
    FROM clean_calls
    GROUP BY 1
),
monthly_ptp AS (
    SELECT 
        DATE_TRUNC('month', ptp_created_time) AS reporting_month,
        COUNT(DISTINCT ptp_id) AS total_ptp_commitments,
        COUNT(DISTINCT account_id) AS unique_ptp_accounts,
        COUNT(DISTINCT CASE WHEN audited_promise_status = 'KEPT' THEN ptp_id END) AS kept_ptp_commitments,
        COUNT(DISTINCT CASE WHEN promised_due_date <= CURRENT_DATE THEN ptp_id END) AS matured_ptp_commitments
    FROM fact_ptp
    GROUP BY 1
),
monthly_payments AS (
    SELECT 
        DATE_TRUNC('month', payment_timestamp) AS reporting_month,
        COUNT(DISTINCT payment_id) AS canonical_payments_count,
        COUNT(DISTINCT account_id) AS paying_accounts_count,
        ROUND(SUM(amount_paid), 2) AS canonical_recovered_inr
    FROM fact_payment
    GROUP BY 1
),
monthly_agent_hours AS (
    SELECT 
        DATE_TRUNC('month', login_time) AS reporting_month,
        ROUND(SUM(productive_hours), 2) AS productive_agent_hours
    FROM clean_agent_sessions
    GROUP BY 1
)
SELECT 
    c.reporting_month,
    COALESCE(c.eligible_accounts_count, 0) AS eligible_accounts,
    COALESCE(c.opening_exposure_inr, 0.0) AS opening_exposure_inr,
    COALESCE(t.targeted_accounts_count, 0) AS targeted_accounts,
    
    -- Operational Volumes
    COALESCE(ca.total_call_attempts, 0) AS total_call_attempts,
    COALESCE(ca.unique_accounts_attempted, 0) AS accounts_attempted,
    COALESCE(ca.connected_accounts, 0) AS connected_accounts,
    COALESCE(ca.rpc_accounts, 0) AS rpc_accounts,
    COALESCE(p.unique_ptp_accounts, 0) AS ptp_accounts,
    COALESCE(p.matured_ptp_commitments, 0) AS matured_ptps,
    COALESCE(p.kept_ptp_commitments, 0) AS kept_ptps,
    
    -- Realized Cash Recovery
    COALESCE(pay.canonical_recovered_inr, 0.0) AS canonical_recovered_inr,
    COALESCE(pay.paying_accounts_count, 0) AS paying_accounts,
    COALESCE(ah.productive_agent_hours, 0.0) AS productive_agent_hours,
    
    -- 1. Contact Rate (Connected Accounts / Targeted Accounts)
    ROUND(100.0 * COALESCE(ca.connected_accounts, 0) / NULLIF(t.targeted_accounts_count, 0), 2) AS contact_rate_pct,
    
    -- 2. Right-Party Contact (RPC) Rate (RPC Accounts / Connected Accounts)
    ROUND(100.0 * COALESCE(ca.rpc_accounts, 0) / NULLIF(ca.connected_accounts, 0), 2) AS rpc_rate_pct,
    
    -- 3. Promise-to-Pay (PTP) Conversion Rate (PTP Accounts / RPC Accounts)
    ROUND(100.0 * COALESCE(p.unique_ptp_accounts, 0) / NULLIF(ca.rpc_accounts, 0), 2) AS ptp_rate_pct,
    
    -- 4. PTP Kept Rate (Kept PTPs / Matured PTPs)
    ROUND(100.0 * COALESCE(p.kept_ptp_commitments, 0) / NULLIF(p.matured_ptp_commitments, 0), 2) AS ptp_kept_rate_pct,
    
    -- 5. Primary Recovery Rate (Canonical Collections / Opening Exposure)
    ROUND(100.0 * COALESCE(pay.canonical_recovered_inr, 0.0) / NULLIF(c.opening_exposure_inr, 0.0), 3) AS recovery_rate_pct,
    
    -- 6. Realized Recovery Per Eligible Account
    ROUND(COALESCE(pay.canonical_recovered_inr, 0.0) / NULLIF(c.eligible_accounts_count, 0), 2) AS recovery_per_account_inr,
    
    -- 7. Recovery Per Productive Agent-Hour
    ROUND(COALESCE(pay.canonical_recovered_inr, 0.0) / NULLIF(ah.productive_agent_hours, 0.0), 2) AS recovery_per_agent_hour_inr
FROM monthly_cohort c
LEFT JOIN monthly_targeting t ON c.reporting_month = t.reporting_month
LEFT JOIN monthly_calls ca ON c.reporting_month = ca.reporting_month
LEFT JOIN monthly_ptp p ON c.reporting_month = p.reporting_month
LEFT JOIN monthly_payments pay ON c.reporting_month = pay.reporting_month
LEFT JOIN monthly_agent_hours ah ON c.reporting_month = ah.reporting_month
ORDER BY c.reporting_month;
