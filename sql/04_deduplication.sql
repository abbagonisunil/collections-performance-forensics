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
        -- Detect rapid payments on same account and exact same amount
        LAG(payment_timestamp) OVER (
            PARTITION BY account_id, amount_paid 
            ORDER BY payment_timestamp
        ) AS prev_payment_time_same_amount,
        LAG(transaction_reference) OVER (
            PARTITION BY account_id, amount_paid 
            ORDER BY payment_timestamp
        ) AS prev_ref_same_amount
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
        WHEN payment_status IN ('FAILED', 'REVERSED', 'REFUNDED', 'CHARGEBACK', 'CANCELLED') THEN 'EXCLUDED_REVERSAL_OR_FAILED'
        WHEN exact_ref_occurence > 1 THEN 'EXCLUDED_EXACT_REF_DUPLICATE'
        WHEN prev_payment_time_same_amount IS NOT NULL 
             AND EXTRACT(EPOCH FROM (payment_timestamp - prev_payment_time_same_amount)) BETWEEN 0 AND 600 THEN
             CASE 
                 -- Legitimate distinct transaction: distinct bank UTR with confirmed settlement
                 WHEN transaction_reference IS NOT NULL 
                      AND prev_ref_same_amount IS NOT NULL 
                      AND transaction_reference != prev_ref_same_amount 
                      AND settlement_timestamp IS NOT NULL 
                      AND payment_status = 'SUCCESS' THEN 'RETAINED_DISTINCT_REFERENCE'
                 -- Ambiguous candidate lacking distinct settlement proof
                 WHEN transaction_reference IS NOT NULL 
                      AND prev_ref_same_amount IS NOT NULL 
                      AND transaction_reference != prev_ref_same_amount 
                      AND settlement_timestamp IS NULL THEN 'FLAGGED_CANDIDATE_RETRY_UNRESOLVED'
                 -- Replay / retry without distinct reference
                 ELSE 'EXCLUDED_WEBHOOK_REPLAY_RETRY'
             END
        ELSE 'RETAINED_CANONICAL'
    END AS dedup_decision,
    
    CASE 
        WHEN amount_paid IS NULL OR amount_paid <= 0 THEN 'Payment amount non-positive or null'
        WHEN payment_status IN ('FAILED', 'REVERSED', 'REFUNDED', 'CHARGEBACK', 'CANCELLED') THEN 'Transaction failed, reversed, refunded, or charged back'
        WHEN exact_ref_occurence > 1 THEN 'Duplicate transaction reference ingested multiple times'
        WHEN prev_payment_time_same_amount IS NOT NULL 
             AND EXTRACT(EPOCH FROM (payment_timestamp - prev_payment_time_same_amount)) BETWEEN 0 AND 600 THEN
             CASE 
                 WHEN transaction_reference IS NOT NULL 
                      AND prev_ref_same_amount IS NOT NULL 
                      AND transaction_reference != prev_ref_same_amount 
                      AND settlement_timestamp IS NOT NULL 
                      AND payment_status = 'SUCCESS' THEN 'Valid distinct payment: verified distinct settlement UTR within 10 minutes'
                 WHEN transaction_reference IS NOT NULL 
                      AND prev_ref_same_amount IS NOT NULL 
                      AND transaction_reference != prev_ref_same_amount 
                      AND settlement_timestamp IS NULL THEN 'Candidate retry within 10-minute window lacking settlement proof'
                 ELSE 'Replay event: duplicate transaction submitted within 10-minute retry window lacking distinct reference'
             END
        ELSE 'Valid canonical realized cash recovery'
    END AS decision_reason,
    
    CASE 
        WHEN payment_status = 'SUCCESS' 
             AND amount_paid > 0
             AND exact_ref_occurence = 1
             AND (
                 prev_payment_time_same_amount IS NULL 
                 OR EXTRACT(EPOCH FROM (payment_timestamp - prev_payment_time_same_amount)) > 600
                 OR (
                     transaction_reference IS NOT NULL 
                     AND prev_ref_same_amount IS NOT NULL 
                     AND transaction_reference != prev_ref_same_amount 
                     AND settlement_timestamp IS NOT NULL
                 )
             )
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
