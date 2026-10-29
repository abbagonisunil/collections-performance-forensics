-- ============================================================================
-- 02_data_quality.sql
-- Automated data quality checks, anomaly quarantine, and audit metrics
-- ============================================================================

-- Table to store identified data quality issues and quarantine records
CREATE TABLE IF NOT EXISTS dq_issue_log (
    issue_id VARCHAR,
    source_table VARCHAR,
    record_id VARCHAR,
    severity VARCHAR, -- CRITICAL, HIGH, MEDIUM, LOW
    rule_name VARCHAR,
    issue_description VARCHAR,
    monetary_exposure_inr DOUBLE,
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- DQ Rule 1: Non-positive or Null Payment Amounts
CREATE OR REPLACE VIEW v_dq_invalid_payments AS
SELECT 
    'DQ_PAY_001' AS issue_id,
    'payments' AS source_table,
    payment_id AS record_id,
    'CRITICAL' AS severity,
    'INVALID_PAYMENT_AMOUNT' AS rule_name,
    'Payment amount is NULL or <= 0' AS issue_description,
    COALESCE(amount_paid, 0.0) AS monetary_exposure_inr
FROM stg_payments
WHERE amount_paid IS NULL OR amount_paid <= 0;

-- DQ Rule 2: Chronological Anomalies in Calls
CREATE OR REPLACE VIEW v_dq_call_time_anomalies AS
SELECT 
    'DQ_CALL_002' AS issue_id,
    'calls' AS source_table,
    call_id AS record_id,
    'HIGH' AS severity,
    'NEGATIVE_CALL_DURATION' AS rule_name,
    'Call end timestamp precedes call start timestamp' AS issue_description,
    0.0 AS monetary_exposure_inr
FROM stg_calls
WHERE call_end_time < call_start_time OR duration_seconds < 0;

-- DQ Rule 3: Orphaned Payments (Account ID does not exist in master)
CREATE OR REPLACE VIEW v_dq_orphaned_payments AS
SELECT 
    'DQ_PAY_003' AS issue_id,
    'payments' AS source_table,
    p.payment_id AS record_id,
    'CRITICAL' AS severity,
    'ORPHANED_PAYMENT_ACCOUNT' AS rule_name,
    'Payment recorded for non-existent account ID' AS issue_description,
    p.amount_paid AS monetary_exposure_inr
FROM stg_payments p
LEFT JOIN stg_accounts a ON p.account_id = a.account_id
WHERE a.account_id IS NULL;

-- DQ Rule 4: Orphaned Interactions (Calls without accounts)
CREATE OR REPLACE VIEW v_dq_orphaned_calls AS
SELECT 
    'DQ_CALL_004' AS issue_id,
    'calls' AS source_table,
    c.call_id AS record_id,
    'HIGH' AS severity,
    'ORPHANED_CALL_ACCOUNT' AS rule_name,
    'Call recorded for non-existent account ID' AS issue_description,
    0.0 AS monetary_exposure_inr
FROM stg_calls c
LEFT JOIN stg_accounts a ON c.account_id = a.account_id
WHERE a.account_id IS NULL;

-- DQ Rule 5: Future Dated Events
CREATE OR REPLACE VIEW v_dq_future_events AS
SELECT 
    'DQ_TIME_005' AS issue_id,
    'payments' AS source_table,
    payment_id AS record_id,
    'HIGH' AS severity,
    'FUTURE_DATED_PAYMENT' AS rule_name,
    'Payment timestamp is in the future' AS issue_description,
    amount_paid AS monetary_exposure_inr
FROM stg_payments
WHERE payment_timestamp > CURRENT_TIMESTAMP;

-- Unified DQ Summary View
CREATE OR REPLACE VIEW v_dq_summary_stats AS
WITH all_issues AS (
    SELECT * FROM v_dq_invalid_payments
    UNION ALL SELECT * FROM v_dq_call_time_anomalies
    UNION ALL SELECT * FROM v_dq_orphaned_payments
    UNION ALL SELECT * FROM v_dq_orphaned_calls
    UNION ALL SELECT * FROM v_dq_future_events
)
SELECT 
    severity,
    rule_name,
    COUNT(*) AS total_affected_records,
    ROUND(SUM(monetary_exposure_inr), 2) AS total_monetary_exposure_inr
FROM all_issues
GROUP BY 1, 2
ORDER BY 3 DESC;
