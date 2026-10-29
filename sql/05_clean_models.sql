-- ============================================================================
-- 05_clean_models.sql
-- Clean, normalized, validated base models with resolved entities and UTC timestamps
-- ============================================================================

-- Clean 1: Canonical Payments
CREATE OR REPLACE TABLE clean_payments AS
SELECT 
    payment_id,
    transaction_reference,
    account_id,
    amount_paid,
    payment_method,
    payment_status,
    payment_timestamp,
    settlement_timestamp,
    CAST(payment_timestamp AS DATE) AS payment_date,
    DATE_TRUNC('month', CAST(payment_timestamp AS DATE)) AS payment_month
FROM payment_deduplication_log
WHERE is_canonical_payment = TRUE;

-- Clean 2: Canonical Calls with Resolved Dispositions and Resolved Agent IDs
CREATE OR REPLACE TABLE clean_calls AS
SELECT 
    c.call_id,
    c.account_id,
    COALESCE(ac.canonical_agent_id, c.agent_id) AS agent_id,
    c.campaign_id,
    c.call_start_time,
    c.call_end_time,
    c.duration_seconds,
    c.call_type,
    c.vendor_id,
    c.status AS call_status,
    c.call_hour_local,
    COALESCE(rc.canonical_disposition_category, 'UNREACHED') AS disposition_category,
    COALESCE(rc.is_ptp_promise, FALSE) AS is_ptp_promise,
    d.disposition_code_raw,
    CAST(c.call_start_time AS DATE) AS call_date,
    DATE_TRUNC('month', CAST(c.call_start_time AS DATE)) AS call_month,
    CASE 
        WHEN c.call_hour_local >= 8 AND c.call_hour_local <= 19 THEN TRUE 
        ELSE FALSE 
    END AS is_rbi_compliant_calling_hour
FROM stg_calls c
LEFT JOIN stg_call_dispositions d ON c.call_id = d.call_id
LEFT JOIN ref_disposition_crosswalk rc ON d.disposition_code_raw = rc.disposition_code_raw
LEFT JOIN dim_agent_crosswalk ac ON c.agent_id = ac.source_agent_id
WHERE c.call_id IS NOT NULL;

-- Clean 3: Canonical Promises to Pay (PTP)
CREATE OR REPLACE TABLE clean_promises_to_pay AS
SELECT 
    p.ptp_id,
    p.account_id,
    p.call_id,
    COALESCE(ac.canonical_agent_id, p.agent_id) AS agent_id,
    p.channel_origin,
    p.ptp_created_time,
    p.promised_due_date,
    p.promised_amount,
    p.status AS promise_status,
    CAST(p.ptp_created_time AS DATE) AS ptp_created_date,
    DATE_TRUNC('month', CAST(p.ptp_created_time AS DATE)) AS ptp_month
FROM stg_promises_to_pay p
LEFT JOIN dim_agent_crosswalk ac ON p.agent_id = ac.source_agent_id
WHERE p.promised_amount > 0;

-- Clean 4: Canonical Productive Agent Sessions
CREATE OR REPLACE TABLE clean_agent_sessions AS
SELECT 
    s.session_id,
    COALESCE(ac.canonical_agent_id, s.agent_id) AS agent_id,
    s.login_time,
    s.logout_time,
    s.total_duration_sec,
    s.talk_duration_sec,
    s.wrap_up_duration_sec,
    s.idle_duration_sec,
    s.break_duration_sec,
    s.productive_hours,
    CAST(s.login_time AS DATE) AS session_date,
    DATE_TRUNC('month', CAST(s.login_time AS DATE)) AS session_month
FROM stg_agent_sessions s
LEFT JOIN dim_agent_crosswalk ac ON s.agent_id = ac.source_agent_id;
