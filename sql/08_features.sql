-- ============================================================================
-- 08_features.sql
-- Feature engineering for statistical driver analysis, bias detection, and counterfactuals
-- ============================================================================

CREATE OR REPLACE TABLE features_account_level AS
WITH targeting_features AS (
    SELECT 
        account_id,
        COUNT(DISTINCT target_date) AS days_targeted_count,
        AVG(propensity_score) AS avg_propensity_score,
        MAX(CASE WHEN is_suppressed THEN 1 ELSE 0 END) AS was_ever_suppressed,
        MAX(CASE WHEN target_date >= '2024-07-01' THEN 1 ELSE 0 END) AS targeted_in_post_period
    FROM stg_daily_targeting
    GROUP BY 1
),
interaction_features AS (
    SELECT 
        account_id,
        COUNT(DISTINCT interaction_id) AS total_interactions_count,
        SUM(CASE WHEN channel = 'CALL' THEN 1 ELSE 0 END) AS call_attempts_count,
        SUM(CASE WHEN channel = 'CALL' AND is_rpc THEN 1 ELSE 0 END) AS rpc_contacts_count,
        SUM(CASE WHEN channel = 'WHATSAPP' THEN 1 ELSE 0 END) AS wa_events_count,
        SUM(CASE WHEN channel = 'SMS' THEN 1 ELSE 0 END) AS sms_events_count,
        SUM(CASE WHEN channel = 'FIELD_VISIT' THEN 1 ELSE 0 END) AS field_visits_count,
        MAX(interaction_timestamp) AS latest_interaction_ts
    FROM fact_interaction
    GROUP BY 1
),
ptp_features AS (
    SELECT 
        account_id,
        COUNT(DISTINCT ptp_id) AS total_ptp_commitments_count,
        SUM(CASE WHEN audited_promise_status = 'KEPT' THEN 1 ELSE 0 END) AS kept_ptp_count,
        SUM(CASE WHEN audited_promise_status = 'BROKEN' THEN 1 ELSE 0 END) AS broken_ptp_count
    FROM fact_ptp
    GROUP BY 1
),
payment_features AS (
    SELECT 
        account_id,
        COUNT(DISTINCT payment_id) AS total_payment_count,
        ROUND(SUM(amount_paid), 2) AS total_recovered_amount,
        MIN(payment_timestamp) AS first_payment_ts,
        MAX(payment_timestamp) AS last_payment_ts
    FROM fact_payment
    GROUP BY 1
)
SELECT 
    a.account_id,
    a.borrower_id,
    a.client_name,
    a.product_type,
    a.borrower_state,
    a.borrower_language,
    a.borrower_risk_tier,
    a.opening_principal,
    a.dpd,
    a.dpd_bucket,
    a.account_status,
    
    -- Targeting Features
    COALESCE(tf.days_targeted_count, 0) AS days_targeted_count,
    COALESCE(tf.avg_propensity_score, 0.5) AS avg_propensity_score,
    COALESCE(tf.was_ever_suppressed, 0) AS was_ever_suppressed,
    COALESCE(tf.targeted_in_post_period, 0) AS targeted_in_post_period,
    
    -- Interaction Features
    COALESCE(inf.total_interactions_count, 0) AS total_interactions_count,
    COALESCE(inf.call_attempts_count, 0) AS call_attempts_count,
    COALESCE(inf.rpc_contacts_count, 0) AS rpc_contacts_count,
    COALESCE(inf.wa_events_count, 0) AS wa_events_count,
    COALESCE(inf.sms_events_count, 0) AS sms_events_count,
    COALESCE(inf.field_visits_count, 0) AS field_visits_count,
    
    -- PTP Features
    COALESCE(pf.total_ptp_commitments_count, 0) AS total_ptp_commitments_count,
    COALESCE(pf.kept_ptp_count, 0) AS kept_ptp_count,
    COALESCE(pf.broken_ptp_count, 0) AS broken_ptp_count,
    
    -- Outcome Features
    COALESCE(pay.total_payment_count, 0) AS total_payment_count,
    COALESCE(pay.total_recovered_amount, 0.0) AS total_recovered_amount,
    CASE WHEN COALESCE(pay.total_recovered_amount, 0.0) > 0 THEN 1 ELSE 0 END AS has_paid,
    ROUND(COALESCE(pay.total_recovered_amount, 0.0) / NULLIF(a.opening_principal, 0), 4) AS account_recovery_rate
FROM dim_account a
LEFT JOIN targeting_features tf ON a.account_id = tf.account_id
LEFT JOIN interaction_features inf ON a.account_id = inf.account_id
LEFT JOIN ptp_features pf ON a.account_id = pf.account_id
LEFT JOIN payment_features pay ON a.account_id = pay.account_id;
