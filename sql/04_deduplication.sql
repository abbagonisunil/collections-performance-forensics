-- ============================================================================
-- 04_deduplication.sql
-- Forensic deduplication of payment records, webhook replays, and reversals
-- ============================================================================

-- Step 1: Detect and flag duplicate payments with forensic decision rules
CREATE OR REPLACE TABLE payment_deduplication_log AS
WITH base_payments AS (
    SELECT 
        payment_id,
        transaction_reference,
        account_id,
        amount_paid,
        principal_component,
        interest_component,
        fee_component,
        payment_method,
        payment_status,
        payment_timestamp,
        settlement_timestamp,
        -- Detect exact duplicate rows on transaction reference or payment_id
        ROW_NUMBER() OVER (
            PARTITION BY transaction_reference 
            ORDER BY payment_timestamp, payment_id
        ) AS exact_ref_occurence,
        -- Detect rapid webhook retries / replays (same account and exact same amount within 10 minutes)
        LAG(payment_timestamp) OVER (
            PARTITION BY account_id, amount_paid 
            ORDER BY payment_timestamp
        ) AS prev_payment_time_same_amount
    FROM stg_payments
)
SELECT 
    payment_id,
    transaction_reference,
    account_id,
    amount_paid,
    payment_method,
    payment_status,
    payment_timestamp,
    settlement_timestamp,
    
    -- Forensic Decision Rule
    CASE 
        WHEN amount_paid IS NULL OR amount_paid <= 0 THEN 'EXCLUDED_INVALID_AMOUNT'
        WHEN payment_status IN ('FAILED', 'REVERSED', 'REFUNDED', 'CHARGEBACK') THEN 'EXCLUDED_REVERSAL_OR_FAILED'
        WHEN exact_ref_occurence > 1 THEN 'EXCLUDED_EXACT_REF_DUPLICATE'
        WHEN prev_payment_time_same_amount IS NOT NULL 
             AND EXTRACT(EPOCH FROM (payment_timestamp - prev_payment_time_same_amount)) BETWEEN 0 AND 600
             THEN 'EXCLUDED_WEBHOOK_REPLAY_RETRY'
        ELSE 'RETAINED_CANONICAL'
    END AS dedup_decision,
    
    CASE 
        WHEN amount_paid IS NULL OR amount_paid <= 0 THEN 'Payment amount non-positive'
        WHEN payment_status IN ('FAILED', 'REVERSED', 'REFUNDED', 'CHARGEBACK') THEN 'Transaction failed or reversed'
        WHEN exact_ref_occurence > 1 THEN 'Duplicate transaction reference ingested multiple times'
        WHEN prev_payment_time_same_amount IS NOT NULL 
             AND EXTRACT(EPOCH FROM (payment_timestamp - prev_payment_time_same_amount)) BETWEEN 0 AND 600
             THEN 'Replay event: duplicate transaction submitted within 10-minute retry window'
        ELSE 'Valid canonical realized cash recovery'
    END AS decision_reason,
    
    CASE 
        WHEN exact_ref_occurence = 1 
             AND payment_status = 'SUCCESS' 
             AND (prev_payment_time_same_amount IS NULL OR EXTRACT(EPOCH FROM (payment_timestamp - prev_payment_time_same_amount)) > 600)
             AND amount_paid > 0
             THEN TRUE 
        ELSE FALSE 
    END AS is_canonical_payment
FROM base_payments;

-- Step 2: Forensic Reconciliation of Deduplication Impact
CREATE OR REPLACE VIEW v_payment_deduplication_audit AS
SELECT 
    dedup_decision,
    decision_reason,
    COUNT(*) AS transaction_count,
    ROUND(SUM(COALESCE(amount_paid, 0.0)), 2) AS total_amount_inr,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS pct_of_transactions,
    ROUND(100.0 * SUM(COALESCE(amount_paid, 0.0)) / SUM(SUM(COALESCE(amount_paid, 0.0))) OVER (), 2) AS pct_of_gross_amount
FROM payment_deduplication_log
GROUP BY 1, 2
ORDER BY 4 DESC;

-- Step 3: Forensic Overstatement Summary (Naive Collections vs Canonical Collections)
CREATE OR REPLACE VIEW v_forensic_recovery_inflation AS
SELECT 
    ROUND(SUM(amount_paid), 2) AS naive_gross_collections_inr,
    ROUND(SUM(CASE WHEN is_canonical_payment THEN amount_paid ELSE 0 END), 2) AS canonical_collections_inr,
    ROUND(SUM(CASE WHEN NOT is_canonical_payment THEN amount_paid ELSE 0 END), 2) AS total_overstatement_inr,
    ROUND(100.0 * SUM(CASE WHEN NOT is_canonical_payment THEN amount_paid ELSE 0 END) / NULLIF(SUM(CASE WHEN is_canonical_payment THEN amount_paid ELSE 0 END), 0), 2) AS recovery_inflation_pct
FROM payment_deduplication_log;
