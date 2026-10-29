-- ============================================================================
-- 06_golden_dataset.sql
-- Golden dimensional and fact models at auditable, explicit grains
-- ============================================================================

-- 1. Dimension: Borrowers
CREATE OR REPLACE TABLE dim_borrower AS
SELECT 
    b.borrower_id,
    b.external_borrower_id,
    b.full_name,
    b.state,
    b.city,
    b.pin_code,
    b.risk_tier,
    b.preferred_language,
    b.annual_income,
    b.credit_score,
    b.created_at
FROM stg_borrowers b;

-- 2. Dimension: Accounts
CREATE OR REPLACE TABLE dim_account AS
SELECT 
    a.account_id,
    a.borrower_id,
    b.state AS borrower_state,
    b.preferred_language AS borrower_language,
    b.risk_tier AS borrower_risk_tier,
    a.client_name,
    a.product_type,
    a.disbursed_amount,
    a.opening_principal,
    a.current_outstanding,
    a.dpd,
    a.dpd_bucket,
    a.status AS account_status,
    a.disbursed_at,
    a.due_date
FROM stg_accounts a
LEFT JOIN dim_borrower b ON a.borrower_id = b.borrower_id;

-- 3. Dimension: Agents
CREATE OR REPLACE TABLE dim_agent AS
SELECT 
    a.canonical_agent_id AS agent_id,
    ag.agent_name,
    ag.center_location,
    ag.primary_language,
    ag.tenure_months,
    ag.tenure_bucket,
    ag.agent_tier,
    ag.hire_date,
    ag.is_active
FROM (SELECT DISTINCT canonical_agent_id FROM dim_agent_crosswalk) a
LEFT JOIN stg_agents ag ON a.canonical_agent_id = ag.agent_id;

-- 4. Dimension: Campaigns
CREATE OR REPLACE TABLE dim_campaign AS
SELECT 
    campaign_id,
    campaign_name,
    strategy_type,
    target_bucket,
    primary_channel,
    start_date,
    end_date,
    status
FROM stg_campaigns;

-- 5. Fact: Canonical Payments
CREATE OR REPLACE TABLE fact_payment AS
SELECT 
    p.payment_id,
    p.transaction_reference,
    p.account_id,
    a.borrower_id,
    a.client_name,
    a.product_type,
    a.dpd_bucket,
    p.amount_paid,
    p.payment_method,
    p.payment_status,
    p.payment_timestamp,
    p.payment_date,
    p.payment_month
FROM clean_payments p
LEFT JOIN dim_account a ON p.account_id = a.account_id;

-- 6. Fact: Unified Omnichannel Interactions
CREATE OR REPLACE TABLE fact_interaction AS
-- Calling interactions
SELECT 
    'CALL_' || call_id AS interaction_id,
    account_id,
    agent_id,
    campaign_id,
    'CALL' AS channel,
    call_start_time AS interaction_timestamp,
    CAST(call_start_time AS DATE) AS interaction_date,
    DATE_TRUNC('month', CAST(call_start_time AS DATE)) AS interaction_month,
    duration_seconds,
    disposition_category,
    CASE WHEN disposition_category = 'RPC' THEN TRUE ELSE FALSE END AS is_rpc,
    is_ptp_promise
FROM clean_calls

UNION ALL

-- WhatsApp interactions
SELECT 
    'WA_' || event_id AS interaction_id,
    account_id,
    NULL AS agent_id,
    NULL AS campaign_id,
    'WHATSAPP' AS channel,
    event_timestamp AS interaction_timestamp,
    CAST(event_timestamp AS DATE) AS interaction_date,
    DATE_TRUNC('month', CAST(event_timestamp AS DATE)) AS interaction_month,
    0 AS duration_seconds,
    CASE WHEN event_type IN ('BUTTON_CLICK', 'INBOUND_REPLY') THEN 'RPC' ELSE 'DELIVERED' END AS disposition_category,
    CASE WHEN event_type IN ('BUTTON_CLICK', 'INBOUND_REPLY') THEN TRUE ELSE FALSE END AS is_rpc,
    FALSE AS is_ptp_promise
FROM stg_whatsapp_events

UNION ALL

-- SMS interactions
SELECT 
    'SMS_' || event_id AS interaction_id,
    account_id,
    NULL AS agent_id,
    campaign_id,
    'SMS' AS channel,
    event_timestamp AS interaction_timestamp,
    CAST(event_timestamp AS DATE) AS interaction_date,
    DATE_TRUNC('month', CAST(event_timestamp AS DATE)) AS interaction_month,
    0 AS duration_seconds,
    CASE WHEN event_type = 'LINK_CLICKED' THEN 'ENGAGED' ELSE 'SENT' END AS disposition_category,
    FALSE AS is_rpc,
    FALSE AS is_ptp_promise
FROM stg_sms_events

UNION ALL

-- Field Visits
SELECT 
    'FIELD_' || visit_id AS interaction_id,
    account_id,
    officer_id AS agent_id,
    NULL AS campaign_id,
    'FIELD_VISIT' AS channel,
    visit_timestamp AS interaction_timestamp,
    CAST(visit_timestamp AS DATE) AS interaction_date,
    DATE_TRUNC('month', CAST(visit_timestamp AS DATE)) AS interaction_month,
    1800 AS duration_seconds, -- estimated 30 min visit
    CASE WHEN outcome = 'MET_BORROWER' THEN 'RPC' ELSE 'UNREACHED' END AS disposition_category,
    CASE WHEN outcome = 'MET_BORROWER' THEN TRUE ELSE FALSE END AS is_rpc,
    CASE WHEN outcome = 'PTP_OBTAINED' THEN TRUE ELSE FALSE END AS is_ptp_promise
FROM stg_field_visits;

-- 7. Fact: Promises to Pay (PTP) with Kept Validation
CREATE OR REPLACE TABLE fact_ptp AS
SELECT 
    p.ptp_id,
    p.account_id,
    p.call_id,
    p.agent_id,
    p.channel_origin,
    p.ptp_created_time,
    p.promised_due_date,
    p.promised_amount,
    p.ptp_month,
    
    -- Check if kept: payment within promised due date + 3-day grace period
    CASE 
        WHEN pay.payment_id IS NOT NULL THEN 'KEPT'
        WHEN p.promised_due_date > CURRENT_DATE THEN 'PENDING'
        ELSE 'BROKEN'
    END AS audited_promise_status,
    
    pay.amount_paid AS realized_repaid_amount,
    pay.payment_timestamp AS kept_payment_timestamp
FROM clean_promises_to_pay p
LEFT JOIN fact_payment pay 
    ON p.account_id = pay.account_id 
    AND pay.payment_timestamp >= p.ptp_created_time 
    AND pay.payment_date <= (p.promised_due_date + INTERVAL 3 DAY);

-- 8. Fact: Account-Month Cohort Snapshot
CREATE OR REPLACE TABLE fact_account_month AS
WITH monthly_payments AS (
    SELECT 
        account_id,
        payment_month,
        SUM(amount_paid) AS monthly_recovered_amount,
        COUNT(DISTINCT payment_id) AS payment_transactions_count
    FROM fact_payment
    GROUP BY 1, 2
),
monthly_interactions AS (
    SELECT 
        account_id,
        interaction_month,
        COUNT(*) AS total_interactions,
        SUM(CASE WHEN channel = 'CALL' THEN 1 ELSE 0 END) AS call_count,
        SUM(CASE WHEN channel = 'WHATSAPP' THEN 1 ELSE 0 END) AS wa_count,
        SUM(CASE WHEN channel = 'SMS' THEN 1 ELSE 0 END) AS sms_count,
        SUM(CASE WHEN channel = 'FIELD_VISIT' THEN 1 ELSE 0 END) AS field_count,
        MAX(CASE WHEN is_rpc THEN 1 ELSE 0 END) AS had_rpc_contact
    FROM fact_interaction
    GROUP BY 1, 2
)
SELECT 
    a.account_id,
    a.borrower_id,
    a.client_name,
    a.product_type,
    a.borrower_state,
    a.borrower_language,
    a.borrower_risk_tier,
    a.dpd_bucket,
    COALESCE(mp.payment_month, mi.interaction_month, DATE_TRUNC('month', CURRENT_DATE)) AS snapshot_month,
    a.opening_principal,
    COALESCE(mp.monthly_recovered_amount, 0.0) AS monthly_recovered_amount,
    COALESCE(mp.payment_transactions_count, 0) AS payment_transactions_count,
    COALESCE(mi.total_interactions, 0) AS total_interactions,
    COALESCE(mi.call_count, 0) AS call_count,
    COALESCE(mi.wa_count, 0) AS wa_count,
    COALESCE(mi.sms_count, 0) AS sms_count,
    COALESCE(mi.field_count, 0) AS field_count,
    COALESCE(mi.had_rpc_contact, 0) AS had_rpc_contact,
    CASE 
        WHEN COALESCE(mp.monthly_recovered_amount, 0.0) > 0 THEN TRUE 
        ELSE FALSE 
    END AS is_paying_account
FROM dim_account a
LEFT JOIN monthly_payments mp ON a.account_id = mp.account_id
LEFT JOIN monthly_interactions mi ON a.account_id = mi.account_id;
