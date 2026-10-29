-- ============================================================================
-- 00_source_profiling.sql
-- Profiling and metadata discovery across all 17 raw collection source tables
-- ============================================================================

-- Macro / helper pattern: Profile table volume, date range, nulls and distinct keys
-- Run against DuckDB raw schema or staging tables

-- 1. Source Table Volume and Basic Grain Profile
CREATE OR REPLACE VIEW v_source_inventory_profile AS
WITH source_summary AS (
    SELECT 'borrowers' AS source_name, COUNT(*) AS row_count FROM raw_borrowers
    UNION ALL SELECT 'accounts', COUNT(*) FROM raw_accounts
    UNION ALL SELECT 'agents', COUNT(*) FROM raw_agents
    UNION ALL SELECT 'agent_sessions', COUNT(*) FROM raw_agent_sessions
    UNION ALL SELECT 'campaigns', COUNT(*) FROM raw_campaigns
    UNION ALL SELECT 'daily_targeting', COUNT(*) FROM raw_daily_targeting
    UNION ALL SELECT 'calls', COUNT(*) FROM raw_calls
    UNION ALL SELECT 'call_attempts', COUNT(*) FROM raw_call_attempts
    UNION ALL SELECT 'call_dispositions', COUNT(*) FROM raw_call_dispositions
    UNION ALL SELECT 'whatsapp_events', COUNT(*) FROM raw_whatsapp_events
    UNION ALL SELECT 'sms_events', COUNT(*) FROM raw_sms_events
    UNION ALL SELECT 'field_visits', COUNT(*) FROM raw_field_visits
    UNION ALL SELECT 'promises_to_pay', COUNT(*) FROM raw_promises_to_pay
    UNION ALL SELECT 'payments', COUNT(*) FROM raw_payments
    UNION ALL SELECT 'vendor_telephony', COUNT(*) FROM raw_vendor_telephony
    UNION ALL SELECT 'complaints', COUNT(*) FROM raw_complaints
    UNION ALL SELECT 'account_status_history', COUNT(*) FROM raw_account_status_history
)
SELECT 
    source_name,
    row_count,
    CASE 
        WHEN row_count = 0 THEN 'EMPTY_AWAITING_DATA'
        ELSE 'AVAILABLE'
    END AS ingestion_status
FROM source_summary;

-- 2. Payments Profiling: Inspect potential duplicates, payment methods, and null amounts
CREATE OR REPLACE VIEW v_profile_raw_payments AS
SELECT 
    COUNT(*) AS total_payment_rows,
    COUNT(DISTINCT payment_id) AS distinct_payment_ids,
    COUNT(*) - COUNT(DISTINCT payment_id) AS duplicate_payment_id_count,
    COUNT(DISTINCT transaction_reference) AS distinct_transaction_refs,
    COUNT(*) - COUNT(DISTINCT transaction_reference) AS duplicate_transaction_ref_count,
    SUM(CASE WHEN amount_paid IS NULL THEN 1 ELSE 0 END) AS null_amount_count,
    SUM(CASE WHEN amount_paid <= 0 THEN 1 ELSE 0 END) AS non_positive_amount_count,
    MIN(payment_timestamp) AS earliest_payment_ts,
    MAX(payment_timestamp) AS latest_payment_ts,
    ROUND(SUM(COALESCE(amount_paid, 0)), 2) AS raw_gross_collections_inr
FROM raw_payments;

-- 3. Telephony Vendor and Dispositions Profiling
CREATE OR REPLACE VIEW v_profile_call_dispositions AS
SELECT 
    vendor_id,
    disposition_code,
    disposition_category,
    COUNT(*) AS event_count,
    MIN(call_start_time) AS first_observed,
    MAX(call_start_time) AS last_observed
FROM raw_calls c
LEFT JOIN raw_call_dispositions d ON c.call_id = d.call_id
GROUP BY 1, 2, 3
ORDER BY 1, 4 DESC;
