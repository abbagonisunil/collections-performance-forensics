-- ============================================================================
-- 01_staging.sql
-- Schema normalization, type casting, and null handling for 17 sources
-- ============================================================================

-- Staging 1: Borrowers
CREATE OR REPLACE VIEW stg_borrowers AS
SELECT 
    TRIM(borrower_id) AS borrower_id,
    TRIM(external_borrower_id) AS external_borrower_id,
    TRIM(full_name) AS full_name,
    TRIM(phone_hash) AS phone_hash,
    UPPER(TRIM(COALESCE(state, 'UNKNOWN'))) AS state,
    TRIM(COALESCE(city, 'UNKNOWN')) AS city,
    TRIM(COALESCE(pin_code, '000000')) AS pin_code,
    UPPER(TRIM(COALESCE(risk_tier, 'TIER_C'))) AS risk_tier,
    UPPER(TRIM(COALESCE(preferred_language, 'ENGLISH'))) AS preferred_language,
    CAST(annual_income AS DOUBLE) AS annual_income,
    CAST(credit_score AS INTEGER) AS credit_score,
    CAST(created_at AS TIMESTAMP) AS created_at,
    CAST(updated_at AS TIMESTAMP) AS updated_at
FROM raw_borrowers;

-- Staging 2: Accounts
CREATE OR REPLACE VIEW stg_accounts AS
SELECT 
    TRIM(account_id) AS account_id,
    TRIM(borrower_id) AS borrower_id,
    UPPER(TRIM(client_name)) AS client_name,
    UPPER(TRIM(product_type)) AS product_type,
    CAST(disbursed_amount AS DOUBLE) AS disbursed_amount,
    CAST(opening_principal AS DOUBLE) AS opening_principal,
    CAST(current_outstanding AS DOUBLE) AS current_outstanding,
    CAST(dpd AS INTEGER) AS dpd,
    CASE 
        WHEN CAST(dpd AS INTEGER) <= 30 THEN 'DPD 1-30'
        WHEN CAST(dpd AS INTEGER) <= 60 THEN 'DPD 31-60'
        WHEN CAST(dpd AS INTEGER) <= 90 THEN 'DPD 61-90'
        WHEN CAST(dpd AS INTEGER) <= 120 THEN 'DPD 91-120'
        ELSE 'DPD 120+'
    END AS dpd_bucket,
    UPPER(TRIM(status)) AS status,
    CAST(disbursed_at AS TIMESTAMP) AS disbursed_at,
    CAST(due_date AS TIMESTAMP) AS due_date
FROM raw_accounts;

-- Staging 3: Agents
CREATE OR REPLACE VIEW stg_agents AS
SELECT 
    TRIM(agent_id) AS agent_id,
    LOWER(TRIM(login_username)) AS login_username,
    TRIM(agent_name) AS agent_name,
    TRIM(team_lead_id) AS team_lead_id,
    UPPER(TRIM(COALESCE(center_location, 'UNKNOWN'))) AS center_location,
    UPPER(TRIM(COALESCE(primary_language, 'ENGLISH'))) AS primary_language,
    CAST(tenure_months AS INTEGER) AS tenure_months,
    CASE 
        WHEN CAST(tenure_months AS INTEGER) < 3 THEN '0-3 Months (Trainee)'
        WHEN CAST(tenure_months AS INTEGER) < 6 THEN '3-6 Months (Junior)'
        WHEN CAST(tenure_months AS INTEGER) < 12 THEN '6-12 Months (Mid)'
        ELSE '12+ Months (Senior)'
    END AS tenure_bucket,
    UPPER(TRIM(agent_tier)) AS agent_tier,
    CAST(hire_date AS DATE) AS hire_date,
    CAST(exit_date AS DATE) AS exit_date,
    COALESCE(CAST(is_active AS BOOLEAN), TRUE) AS is_active
FROM raw_agents;

-- Staging 4: Agent Sessions
CREATE OR REPLACE VIEW stg_agent_sessions AS
SELECT 
    TRIM(session_id) AS session_id,
    TRIM(agent_id) AS agent_id,
    CAST(login_time AS TIMESTAMP) AS login_time,
    CAST(logout_time AS TIMESTAMP) AS logout_time,
    CAST(total_duration_sec AS INTEGER) AS total_duration_sec,
    CAST(talk_duration_sec AS INTEGER) AS talk_duration_sec,
    CAST(wrap_up_duration_sec AS INTEGER) AS wrap_up_duration_sec,
    CAST(idle_duration_sec AS INTEGER) AS idle_duration_sec,
    CAST(break_duration_sec AS INTEGER) AS break_duration_sec,
    (CAST(talk_duration_sec AS INTEGER) + CAST(wrap_up_duration_sec AS INTEGER)) / 3600.0 AS productive_hours
FROM raw_agent_sessions;

-- Staging 5: Campaigns
CREATE OR REPLACE VIEW stg_campaigns AS
SELECT 
    TRIM(campaign_id) AS campaign_id,
    TRIM(campaign_name) AS campaign_name,
    UPPER(TRIM(strategy_type)) AS strategy_type,
    UPPER(TRIM(target_bucket)) AS target_bucket,
    UPPER(TRIM(primary_channel)) AS primary_channel,
    CAST(start_date AS DATE) AS start_date,
    CAST(end_date AS DATE) AS end_date,
    UPPER(TRIM(status)) AS status
FROM raw_campaigns;

-- Staging 6: Daily Targeting
CREATE OR REPLACE VIEW stg_daily_targeting AS
SELECT 
    TRIM(targeting_id) AS targeting_id,
    CAST(target_date AS DATE) AS target_date,
    TRIM(account_id) AS account_id,
    TRIM(campaign_id) AS campaign_id,
    UPPER(TRIM(assigned_channel)) AS assigned_channel,
    CAST(propensity_score AS DOUBLE) AS propensity_score,
    CAST(priority_rank AS INTEGER) AS priority_rank,
    COALESCE(CAST(is_suppressed AS BOOLEAN), FALSE) AS is_suppressed
FROM raw_daily_targeting;

-- Staging 7: Calls
CREATE OR REPLACE VIEW stg_calls AS
SELECT 
    TRIM(call_id) AS call_id,
    TRIM(account_id) AS account_id,
    TRIM(agent_id) AS agent_id,
    TRIM(campaign_id) AS campaign_id,
    CAST(call_start_time AS TIMESTAMP) AS call_start_time,
    CAST(call_end_time AS TIMESTAMP) AS call_end_time,
    CAST(duration_seconds AS INTEGER) AS duration_seconds,
    UPPER(TRIM(call_type)) AS call_type,
    UPPER(TRIM(vendor_id)) AS vendor_id,
    UPPER(TRIM(status)) AS status,
    EXTRACT(HOUR FROM CAST(call_start_time AS TIMESTAMP)) AS call_hour_local
FROM raw_calls;

-- Staging 8: Call Attempts
CREATE OR REPLACE VIEW stg_call_attempts AS
SELECT 
    TRIM(attempt_id) AS attempt_id,
    TRIM(call_id) AS call_id,
    TRIM(account_id) AS account_id,
    CAST(attempt_number AS INTEGER) AS attempt_number,
    CAST(attempt_time AS TIMESTAMP) AS attempt_time,
    UPPER(TRIM(telephony_status)) AS telephony_status
FROM raw_call_attempts;

-- Staging 9: Call Dispositions
CREATE OR REPLACE VIEW stg_call_dispositions AS
SELECT 
    TRIM(disposition_id) AS disposition_id,
    TRIM(call_id) AS call_id,
    UPPER(TRIM(disposition_code)) AS disposition_code_raw,
    UPPER(TRIM(disposition_category)) AS disposition_category_raw,
    UPPER(TRIM(sub_disposition)) AS sub_disposition,
    CAST(disposition_time AS TIMESTAMP) AS disposition_time,
    TRIM(agent_notes) AS agent_notes
FROM raw_call_dispositions;

-- Staging 10: WhatsApp Events
CREATE OR REPLACE VIEW stg_whatsapp_events AS
SELECT 
    TRIM(event_id) AS event_id,
    TRIM(account_id) AS account_id,
    TRIM(template_id) AS template_id,
    UPPER(TRIM(event_type)) AS event_type,
    CAST(event_timestamp AS TIMESTAMP) AS event_timestamp,
    UPPER(TRIM(COALESCE(cta_clicked, 'NONE'))) AS cta_clicked
FROM raw_whatsapp_events;

-- Staging 11: SMS Events
CREATE OR REPLACE VIEW stg_sms_events AS
SELECT 
    TRIM(event_id) AS event_id,
    TRIM(account_id) AS account_id,
    TRIM(campaign_id) AS campaign_id,
    UPPER(TRIM(event_type)) AS event_type,
    CAST(event_timestamp AS TIMESTAMP) AS event_timestamp,
    TRIM(link_url) AS link_url
FROM raw_sms_events;

-- Staging 12: Field Visits
CREATE OR REPLACE VIEW stg_field_visits AS
SELECT 
    TRIM(visit_id) AS visit_id,
    TRIM(account_id) AS account_id,
    TRIM(officer_id) AS officer_id,
    CAST(visit_timestamp AS TIMESTAMP) AS visit_timestamp,
    CAST(latitude AS DOUBLE) AS latitude,
    CAST(longitude AS DOUBLE) AS longitude,
    UPPER(TRIM(outcome)) AS outcome,
    CAST(COALESCE(cash_collected, 0.0) AS DOUBLE) AS cash_collected,
    TRIM(receipt_number) AS receipt_number
FROM raw_field_visits;

-- Staging 13: Promises to Pay (PTP)
CREATE OR REPLACE VIEW stg_promises_to_pay AS
SELECT 
    TRIM(ptp_id) AS ptp_id,
    TRIM(account_id) AS account_id,
    TRIM(call_id) AS call_id,
    TRIM(agent_id) AS agent_id,
    UPPER(TRIM(channel_origin)) AS channel_origin,
    CAST(ptp_created_time AS TIMESTAMP) AS ptp_created_time,
    CAST(promised_due_date AS DATE) AS promised_due_date,
    CAST(promised_amount AS DOUBLE) AS promised_amount,
    UPPER(TRIM(status)) AS status
FROM raw_promises_to_pay;

-- Staging 14: Payments
CREATE OR REPLACE VIEW stg_payments AS
SELECT 
    TRIM(payment_id) AS payment_id,
    TRIM(transaction_reference) AS transaction_reference,
    TRIM(account_id) AS account_id,
    CAST(amount_paid AS DOUBLE) AS amount_paid,
    CAST(COALESCE(principal_component, amount_paid) AS DOUBLE) AS principal_component,
    CAST(COALESCE(interest_component, 0.0) AS DOUBLE) AS interest_component,
    CAST(COALESCE(fee_component, 0.0) AS DOUBLE) AS fee_component,
    UPPER(TRIM(payment_method)) AS payment_method,
    UPPER(TRIM(payment_status)) AS payment_status,
    CAST(payment_timestamp AS TIMESTAMP) AS payment_timestamp,
    CAST(COALESCE(settlement_timestamp, payment_timestamp) AS TIMESTAMP) AS settlement_timestamp
FROM raw_payments;

-- Staging 15: Vendor Telephony (Carrier Logs)
CREATE OR REPLACE VIEW stg_vendor_telephony AS
SELECT 
    TRIM(cdr_id) AS cdr_id,
    TRIM(call_id) AS call_id,
    UPPER(TRIM(carrier_name)) AS carrier_name,
    CAST(sip_response_code AS INTEGER) AS sip_response_code,
    TRIM(sip_reason) AS sip_reason,
    CAST(latency_ms AS INTEGER) AS latency_ms,
    CAST(event_time AS TIMESTAMP) AS event_time
FROM raw_vendor_telephony;

-- Staging 16: Complaints
CREATE OR REPLACE VIEW stg_complaints AS
SELECT 
    TRIM(complaint_id) AS complaint_id,
    TRIM(account_id) AS account_id,
    UPPER(TRIM(channel_reported)) AS channel_reported,
    UPPER(TRIM(category)) AS category,
    UPPER(TRIM(severity)) AS severity,
    CAST(logged_at AS TIMESTAMP) AS logged_at,
    CAST(resolved_at AS TIMESTAMP) AS resolved_at,
    UPPER(TRIM(status)) AS status
FROM raw_complaints;

-- Staging 17: Account Status History (SCD Type 2)
CREATE OR REPLACE VIEW stg_account_status_history AS
SELECT 
    TRIM(status_event_id) AS status_event_id,
    TRIM(account_id) AS account_id,
    CAST(effective_from AS TIMESTAMP) AS effective_from,
    CAST(effective_to AS TIMESTAMP) AS effective_to,
    UPPER(TRIM(old_status)) AS old_status,
    UPPER(TRIM(new_status)) AS new_status,
    CAST(old_dpd AS INTEGER) AS old_dpd,
    CAST(new_dpd AS INTEGER) AS new_dpd,
    TRIM(reason) AS reason
FROM raw_account_status_history;
