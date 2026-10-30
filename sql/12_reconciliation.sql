-- ============================================================================
-- 12_reconciliation.sql
-- Production monetary and population reconciliation across all layers
-- ============================================================================

-- 1. End-to-End Monetary Reconciliation View
CREATE OR REPLACE VIEW v_reconciliation_monetary_trail AS
WITH raw_total AS (
    SELECT 
        '1. RAW_PAYMENTS_INGESTED' AS stage,
        COUNT(*) AS transaction_count,
        ROUND(SUM(COALESCE(amount_paid, 0.0)), 2) AS total_collections_inr
    FROM stg_payments
),
clean_total AS (
    SELECT 
        '2. CLEAN_CANONICAL_SETTLED' AS stage,
        COUNT(*) AS transaction_count,
        ROUND(SUM(COALESCE(amount_paid, 0.0)), 2) AS total_collections_inr
    FROM clean_payments
),
golden_total AS (
    SELECT 
        '3. GOLDEN_FACT_PAYMENT' AS stage,
        COUNT(*) AS transaction_count,
        ROUND(SUM(COALESCE(amount_paid, 0.0)), 2) AS total_collections_inr
    FROM fact_payment
),
attribution_total AS (
    SELECT 
        '4. ATTRIBUTED_OUTREACH_CASH' AS stage,
        COUNT(DISTINCT payment_id) AS transaction_count,
        ROUND(SUM(COALESCE(attributed_inr_last_touch, 0.0)), 2) AS total_collections_inr
    FROM fact_payment_attribution
),
unattributed_total AS (
    SELECT 
        '5. ORGANIC_UNATTRIBUTED_CASH' AS stage,
        COUNT(DISTINCT p.payment_id) AS transaction_count,
        ROUND(SUM(COALESCE(p.amount_paid, 0.0)), 2) AS total_collections_inr
    FROM fact_payment p
    LEFT JOIN (SELECT DISTINCT payment_id FROM fact_payment_attribution) a ON p.payment_id = a.payment_id
    WHERE a.payment_id IS NULL
)
SELECT * FROM raw_total
UNION ALL SELECT * FROM clean_total
UNION ALL SELECT * FROM golden_total
UNION ALL SELECT * FROM attribution_total
UNION ALL SELECT * FROM unattributed_total;

-- 2. Forensic Deduplication Ledger Balance Check
CREATE OR REPLACE VIEW v_reconciliation_dedup_balance AS
SELECT 
    ROUND(SUM(amount_paid), 2) AS gross_raw_collections,
    ROUND(SUM(CASE WHEN dedup_decision = 'RETAINED_CANONICAL' THEN amount_paid ELSE 0 END), 2) AS canonical_cash,
    ROUND(SUM(CASE WHEN dedup_decision = 'EXCLUDED_EXACT_DUPLICATE' THEN amount_paid ELSE 0 END), 2) AS excluded_exact_duplicates,
    ROUND(SUM(CASE WHEN dedup_decision = 'EXCLUDED_FAILED' THEN amount_paid ELSE 0 END), 2) AS excluded_failed_transactions,
    ROUND(SUM(CASE WHEN dedup_decision = 'EXCLUDED_REVERSED' THEN amount_paid ELSE 0 END), 2) AS excluded_reversals_refunds,
    ROUND(SUM(CASE WHEN dedup_decision = 'FLAGGED_UNRESOLVED' THEN amount_paid ELSE 0 END), 2) AS flagged_unresolved_retries,
    ROUND(SUM(CASE WHEN dedup_decision = 'OTHER_DOCUMENTED_DECISIONS' THEN amount_paid ELSE 0 END), 2) AS other_documented_exclusions,
    -- Audit Balance Check: Gross - (Canonical + Exclusions) must equal 0.00
    ROUND(SUM(amount_paid) - (
        SUM(CASE WHEN dedup_decision = 'RETAINED_CANONICAL' THEN amount_paid ELSE 0 END) +
        SUM(CASE WHEN dedup_decision = 'EXCLUDED_EXACT_DUPLICATE' THEN amount_paid ELSE 0 END) +
        SUM(CASE WHEN dedup_decision = 'EXCLUDED_FAILED' THEN amount_paid ELSE 0 END) +
        SUM(CASE WHEN dedup_decision = 'EXCLUDED_REVERSED' THEN amount_paid ELSE 0 END) +
        SUM(CASE WHEN dedup_decision = 'FLAGGED_UNRESOLVED' THEN amount_paid ELSE 0 END) +
        SUM(CASE WHEN dedup_decision = 'OTHER_DOCUMENTED_DECISIONS' THEN amount_paid ELSE 0 END)
    ), 4) AS audit_discrepancy_inr
FROM payment_deduplication_log;

-- 3. Production Invariant Test Assertions (Must return 0 rows if compliant)
CREATE OR REPLACE VIEW v_production_integrity_failures AS
SELECT 
    'PAYMENT_FANOUT_VIOLATION' AS check_name,
    'Golden fact_payment has more total amount than clean_payments' AS failure_detail
WHERE (SELECT ROUND(SUM(amount_paid), 2) FROM fact_payment) > (SELECT ROUND(SUM(amount_paid), 2) FROM clean_payments)

UNION ALL

SELECT 
    'RATE_BOUND_VIOLATION' AS check_name,
    'Account level recovery rate is negative' AS failure_detail
FROM features_account_level
WHERE account_recovery_rate < 0

UNION ALL

SELECT 
    'ORPHANED_GOLDEN_PAYMENT' AS check_name,
    'Payment present without valid account dimension join' AS failure_detail
FROM fact_payment
WHERE account_id IS NULL OR borrower_id IS NULL;
