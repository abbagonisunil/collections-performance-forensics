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

-- Dimension 6 & 7: Agent & Agent Tenure (Using Canonical Attribution Bridge - Zero Fanout)
CREATE OR REPLACE VIEW v_driver_06_07_agent_tenure AS
WITH unique_agent_attributions AS (
    -- At most 1 primary call interaction per payment using canonical last-touch attribution
    SELECT 
        agent_id,
        SUM(amount_paid) AS total_attributed_recovery_inr
    FROM bridge_payment_interaction
    WHERE last_touch_rank = 1 AND channel = 'CALL' AND agent_id IS NOT NULL
    GROUP BY agent_id
)
SELECT 
    ag.tenure_bucket,
    COUNT(DISTINCT c.agent_id) AS active_agent_count,
    COUNT(DISTINCT c.call_id) AS calls_handled,
    COUNT(DISTINCT CASE WHEN c.disposition_category = 'RPC' THEN c.call_id END) AS rpc_calls,
    ROUND(100.0 * COUNT(DISTINCT CASE WHEN c.disposition_category = 'RPC' THEN c.call_id END) / NULLIF(COUNT(DISTINCT c.call_id), 0), 2) AS rpc_rate_pct,
    ROUND(SUM(COALESCE(u.total_attributed_recovery_inr, 0.0)), 2) AS attributed_recovery_inr
FROM dim_agent ag
LEFT JOIN clean_calls c ON ag.agent_id = c.agent_id
LEFT JOIN unique_agent_attributions u ON ag.agent_id = u.agent_id
GROUP BY 1
ORDER BY 1;

-- Dimension 8: Campaign (Using Canonical Attribution Bridge - Zero Fanout)
CREATE OR REPLACE VIEW v_driver_08_campaign AS
WITH unique_campaign_attributions AS (
    -- At most 1 primary campaign interaction per payment using canonical last-touch attribution
    SELECT 
        campaign_id,
        SUM(amount_paid) AS total_attributed_recovery_inr
    FROM bridge_payment_interaction
    WHERE last_touch_rank = 1 AND campaign_id IS NOT NULL
    GROUP BY campaign_id
),
campaign_calls AS (
    SELECT 
        campaign_id,
        COUNT(DISTINCT account_id) AS accounts_targeted,
        COUNT(DISTINCT call_id) AS calls_made
    FROM clean_calls
    GROUP BY campaign_id
)
SELECT 
    COALESCE(cmp.campaign_name, 'UNMAPPED_CAMPAIGN') AS campaign_name,
    COALESCE(cmp.strategy_type, 'STANDARD') AS strategy_type,
    COALESCE(cc.accounts_targeted, 0) AS accounts_targeted,
    COALESCE(cc.calls_made, 0) AS calls_made,
    ROUND(COALESCE(u.total_attributed_recovery_inr, 0.0), 2) AS attributed_collections_inr
FROM dim_campaign cmp
LEFT JOIN campaign_calls cc ON cmp.campaign_id = cc.campaign_id
LEFT JOIN unique_campaign_attributions u ON cmp.campaign_id = u.campaign_id
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

-- ============================================================================
-- SQL Validation Checks: Duplicate Payment Attribution & Invariant Reconciliations
-- ============================================================================

-- Validation 1: Anti-Fanout Check (Verifies no payment is multi-counted in unique last-touch attribution)
CREATE OR REPLACE VIEW v_validation_attribution_anti_fanout AS
SELECT 
    payment_id,
    COUNT(CASE WHEN last_touch_rank = 1 THEN 1 END) AS last_touch_count,
    SUM(weight_last_touch) AS sum_last_touch_weight
FROM bridge_payment_interaction
GROUP BY payment_id
HAVING COUNT(CASE WHEN last_touch_rank = 1 THEN 1 END) > 1 
    OR SUM(weight_last_touch) > 1.0001;

-- Validation 2: Payment Attribution Reconciliation Check
CREATE OR REPLACE VIEW v_validation_attribution_reconciliation AS
WITH total_payments AS (
    SELECT 
        COUNT(DISTINCT payment_id) AS total_payment_count,
        ROUND(SUM(amount_paid), 2) AS total_canonical_cash_inr
    FROM fact_payment
),
attributed_payments AS (
    SELECT 
        COUNT(DISTINCT payment_id) AS attributed_payment_count,
        ROUND(SUM(amount_paid * weight_last_touch), 2) AS total_attributed_cash_inr
    FROM bridge_payment_interaction
    WHERE last_touch_rank = 1
)
SELECT 
    t.total_payment_count,
    t.total_canonical_cash_inr,
    COALESCE(a.attributed_payment_count, 0) AS attributed_payment_count,
    COALESCE(a.total_attributed_cash_inr, 0.0) AS total_attributed_cash_inr,
    ROUND(t.total_canonical_cash_inr - COALESCE(a.total_attributed_cash_inr, 0.0), 2) AS unattributed_organic_cash_inr,
    CASE 
        WHEN COALESCE(a.total_attributed_cash_inr, 0.0) <= t.total_canonical_cash_inr THEN 'PASS: NO ATTRIBUTION INFLATION'
        ELSE 'FAIL: ATTRIBUTED CASH EXCEEDS TOTAL CANONICAL CASH'
    END AS reconciliation_status
FROM total_payments t
LEFT JOIN attributed_payments a ON 1=1;
