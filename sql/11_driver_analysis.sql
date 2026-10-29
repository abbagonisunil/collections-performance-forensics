-- ============================================================================
-- 11_driver_analysis.sql
-- Forensic decomposition across all 13 required business dimensions
-- ============================================================================

-- Dimension 1: Portfolio Mix (Product Type)
CREATE OR REPLACE VIEW v_driver_01_product_portfolio AS
SELECT 
    product_type,
    COUNT(DISTINCT account_id) AS total_accounts,
    ROUND(SUM(opening_principal), 2) AS opening_exposure_inr,
    ROUND(SUM(total_recovered_amount), 2) AS canonical_recovered_inr,
    ROUND(100.0 * SUM(total_recovered_amount) / NULLIF(SUM(opening_principal), 0), 2) AS recovery_rate_pct
FROM features_account_level
GROUP BY 1
ORDER BY 3 DESC;

-- Dimension 2: DPD Bucket
CREATE OR REPLACE VIEW v_driver_02_dpd_bucket AS
SELECT 
    dpd_bucket,
    COUNT(DISTINCT account_id) AS total_accounts,
    ROUND(SUM(opening_principal), 2) AS opening_exposure_inr,
    ROUND(SUM(total_recovered_amount), 2) AS canonical_recovered_inr,
    ROUND(100.0 * SUM(total_recovered_amount) / NULLIF(SUM(opening_principal), 0), 2) AS recovery_rate_pct
FROM features_account_level
GROUP BY 1
ORDER BY 1;

-- Dimension 3: Client Portfolio
CREATE OR REPLACE VIEW v_driver_03_client AS
SELECT 
    client_name,
    COUNT(DISTINCT account_id) AS total_accounts,
    ROUND(SUM(opening_principal), 2) AS opening_exposure_inr,
    ROUND(SUM(total_recovered_amount), 2) AS canonical_recovered_inr,
    ROUND(100.0 * SUM(total_recovered_amount) / NULLIF(SUM(opening_principal), 0), 2) AS recovery_rate_pct
FROM features_account_level
GROUP BY 1
ORDER BY 3 DESC;

-- Dimension 4: Geography (State)
CREATE OR REPLACE VIEW v_driver_04_geography AS
SELECT 
    borrower_state,
    COUNT(DISTINCT account_id) AS total_accounts,
    ROUND(SUM(opening_principal), 2) AS opening_exposure_inr,
    ROUND(SUM(total_recovered_amount), 2) AS canonical_recovered_inr,
    ROUND(100.0 * SUM(total_recovered_amount) / NULLIF(SUM(opening_principal), 0), 2) AS recovery_rate_pct
FROM features_account_level
GROUP BY 1
ORDER BY 3 DESC;

-- Dimension 5: Language
CREATE OR REPLACE VIEW v_driver_05_language AS
SELECT 
    borrower_language,
    COUNT(DISTINCT account_id) AS total_accounts,
    ROUND(SUM(opening_principal), 2) AS opening_exposure_inr,
    ROUND(SUM(total_recovered_amount), 2) AS canonical_recovered_inr,
    ROUND(100.0 * SUM(total_recovered_amount) / NULLIF(SUM(opening_principal), 0), 2) AS recovery_rate_pct
FROM features_account_level
GROUP BY 1
ORDER BY 3 DESC;

-- Dimension 6 & 7: Agent & Agent Tenure
CREATE OR REPLACE VIEW v_driver_06_07_agent_tenure AS
SELECT 
    ag.tenure_bucket,
    COUNT(DISTINCT c.agent_id) AS active_agent_count,
    COUNT(DISTINCT c.call_id) AS calls_handled,
    COUNT(DISTINCT CASE WHEN c.disposition_category = 'RPC' THEN c.call_id END) AS rpc_calls,
    ROUND(100.0 * COUNT(DISTINCT CASE WHEN c.disposition_category = 'RPC' THEN c.call_id END) / NULLIF(COUNT(DISTINCT c.call_id), 0), 2) AS rpc_rate_pct,
    ROUND(SUM(COALESCE(p.amount_paid, 0.0)), 2) AS attributed_recovery_inr
FROM clean_calls c
JOIN dim_agent ag ON c.agent_id = ag.agent_id
LEFT JOIN fact_payment p ON c.account_id = p.account_id AND p.payment_timestamp >= c.call_start_time AND p.payment_timestamp <= (c.call_start_time + INTERVAL 14 DAY)
GROUP BY 1
ORDER BY 1;

-- Dimension 8: Campaign
CREATE OR REPLACE VIEW v_driver_08_campaign AS
SELECT 
    COALESCE(cmp.campaign_name, 'UNMAPPED_CAMPAIGN') AS campaign_name,
    COALESCE(cmp.strategy_type, 'STANDARD') AS strategy_type,
    COUNT(DISTINCT c.account_id) AS accounts_targeted,
    COUNT(DISTINCT c.call_id) AS calls_made,
    ROUND(SUM(COALESCE(p.amount_paid, 0.0)), 2) AS attributed_collections_inr
FROM clean_calls c
LEFT JOIN dim_campaign cmp ON c.campaign_id = cmp.campaign_id
LEFT JOIN fact_payment p ON c.account_id = p.account_id AND p.payment_timestamp >= c.call_start_time AND p.payment_timestamp <= (c.call_start_time + INTERVAL 14 DAY)
GROUP BY 1, 2
ORDER BY 5 DESC;

-- Dimension 9: Channel Conversion
CREATE OR REPLACE VIEW v_driver_09_channel AS
SELECT 
    channel,
    COUNT(DISTINCT interaction_id) AS total_events,
    COUNT(DISTINCT account_id) AS unique_accounts_reached,
    COUNT(DISTINCT CASE WHEN is_rpc THEN account_id END) AS unique_rpc_accounts,
    ROUND(100.0 * COUNT(DISTINCT CASE WHEN is_rpc THEN account_id END) / NULLIF(COUNT(DISTINCT account_id), 0), 2) AS rpc_conversion_pct
FROM fact_interaction
GROUP BY 1
ORDER BY 2 DESC;

-- Dimension 10: Telephony Vendor
CREATE OR REPLACE VIEW v_driver_10_telephony_vendor AS
SELECT 
    vendor_id,
    COUNT(DISTINCT call_id) AS total_calls,
    COUNT(DISTINCT CASE WHEN duration_seconds >= 15 THEN call_id END) AS connected_calls,
    ROUND(100.0 * COUNT(DISTINCT CASE WHEN duration_seconds >= 15 THEN call_id END) / NULLIF(COUNT(DISTINCT call_id), 0), 2) AS connect_rate_pct,
    COUNT(DISTINCT CASE WHEN disposition_category = 'RPC' THEN call_id END) AS rpc_calls,
    ROUND(100.0 * COUNT(DISTINCT CASE WHEN disposition_category = 'RPC' THEN call_id END) / NULLIF(COUNT(DISTINCT call_id), 0), 2) AS rpc_rate_pct
FROM clean_calls
GROUP BY 1
ORDER BY 2 DESC;

-- Dimension 11: Calling Time of Day (Local Hour)
CREATE OR REPLACE VIEW v_driver_11_calling_hour AS
SELECT 
    call_hour_local,
    is_rbi_compliant_calling_hour,
    COUNT(DISTINCT call_id) AS calls_dialed,
    COUNT(DISTINCT CASE WHEN duration_seconds >= 15 THEN call_id END) AS connected_calls,
    ROUND(100.0 * COUNT(DISTINCT CASE WHEN duration_seconds >= 15 THEN call_id END) / NULLIF(COUNT(DISTINCT call_id), 0), 2) AS connect_rate_pct,
    COUNT(DISTINCT CASE WHEN disposition_category = 'RPC' THEN call_id END) AS rpc_calls,
    ROUND(100.0 * COUNT(DISTINCT CASE WHEN disposition_category = 'RPC' THEN call_id END) / NULLIF(COUNT(DISTINCT CASE WHEN duration_seconds >= 15 THEN call_id END), 0), 2) AS rpc_rate_pct
FROM clean_calls
GROUP BY 1, 2
ORDER BY 1;

-- Dimension 12: Attempt Frequency
CREATE OR REPLACE VIEW v_driver_12_attempt_frequency AS
WITH account_attempts AS (
    SELECT 
        account_id,
        COUNT(DISTINCT call_id) AS call_attempts_bucket
    FROM clean_calls
    GROUP BY 1
)
SELECT 
    CASE 
        WHEN call_attempts_bucket = 1 THEN '1 Attempt'
        WHEN call_attempts_bucket BETWEEN 2 AND 3 THEN '2-3 Attempts'
        WHEN call_attempts_bucket BETWEEN 4 AND 6 THEN '4-6 Attempts'
        WHEN call_attempts_bucket BETWEEN 7 AND 10 THEN '7-10 Attempts'
        ELSE '11+ Attempts'
    END AS attempt_frequency_tier,
    COUNT(DISTINCT aa.account_id) AS accounts_count,
    ROUND(SUM(COALESCE(f.total_recovered_amount, 0.0)), 2) AS total_recovered_inr,
    ROUND(100.0 * SUM(COALESCE(f.total_recovered_amount, 0.0)) / NULLIF(SUM(f.opening_principal), 0), 2) AS recovery_rate_pct
FROM account_attempts aa
JOIN features_account_level f ON aa.account_id = f.account_id
GROUP BY 1
ORDER BY 2 DESC;

-- Dimension 13: Borrower Segment (Risk Tier)
CREATE OR REPLACE VIEW v_driver_13_borrower_segment AS
SELECT 
    borrower_risk_tier,
    COUNT(DISTINCT account_id) AS total_accounts,
    ROUND(SUM(opening_principal), 2) AS opening_exposure_inr,
    ROUND(SUM(total_recovered_amount), 2) AS canonical_recovered_inr,
    ROUND(100.0 * SUM(total_recovered_amount) / NULLIF(SUM(opening_principal), 0), 2) AS recovery_rate_pct
FROM features_account_level
GROUP BY 1
ORDER BY 1;
