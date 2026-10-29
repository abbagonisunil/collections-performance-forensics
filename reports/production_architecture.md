# Production Analytics Architecture: Collections Performance Forensics

**Architecture Standard**: Audited Lakehouse Pattern for Financial Collections Analytics  
**Version**: 1.0.0 (Production Blueprint)  
**Author**: Analytics Architect & Principal Data Engineer  

---

## 1. System Architecture Overview

The production architecture implements a robust, auditable 6-stage data flow:
```
[Raw Sources (17)] ──> [Staging Layer] ──> [Clean Layer] ──> [Golden Layer] ──> [Feature Layer] ──> [Metrics Layer] ──> [Executive Dashboard]
                             │                  │                 │
                      (Schema Validation)  (Deduplication   (Dimensional
                                           & Quarantine)    & Fact Models)
```

---

## 2. Layer-by-Layer Architectural Specifications

### 2.1 Raw Ingestion Layer
* **Storage**: Immutable object storage (Parquet / S3 / GCS) or file archive.
* **Guarantees**: Append-only, write-once, read-many (WORM). Raw files are never modified in place.
* **Metadata Columns**: `_ingestion_id`, `_ingested_at`, `_source_file_checksum`, `_schema_version`.
* **Idempotency**: Webhook events and CDR batch drops are de-duplicated by transaction reference or event hash prior to staging staging table registration.

### 2.2 Staging Layer (Type Casting & Normalization)
* **Purpose**: Cast strings to strongly typed SQL primitives (Timestamp, Integer, Double, Date).
* **Null Handling**: String variants (`'NULL'`, `'N/A'`, `'none'`, `''`) converted to genuine SQL `NULL`.
* **Code Preservation**: Raw vendor disposition codes, gateway response codes, and status strings are strictly preserved alongside standardized fields.

### 2.3 Clean Layer (Entity Resolution & Forensic Deduplication)
* **Canonical Timestamps**: All event timestamps normalized to UTC, with local business timestamps (`Asia/Kolkata`) generated for compliance auditing.
* **Deduplication Engine**: Evaluates transaction references and rapid webhook retry bursts (<600 seconds). Non-canonical duplicates, failed retries, and reversals are partitioned into `payment_deduplication_log` with auditable decision codes.
* **Quarantine Pipeline**: Records violating referential integrity or chronological consistency (e.g. `call_end_time < call_start_time`) are routed to `dq_issue_log` without breaking downstream pipelines.

### 2.4 Golden Layer (Dimensional & Fact Modeling)
* **Dimensional Entities**:
  * `dim_borrower` (SCD Type 1 with external crosswalks)
  * `dim_account` (Loan terms, product, opening balance, static cohort tags)
  * `dim_agent` (Consolidated canonical agent identities, tenure buckets)
  * `dim_campaign` (Strategy codes, champion/challenger classification)
* **Fact Entities**:
  * `fact_payment` (Canonical realized settled cash collections; grain: 1 row per settled payment)
  * `fact_interaction` (Unified omnichannel events: calls, WhatsApp, SMS, field visits)
  * `fact_ptp` (Commitments matched to realized cash within maturity windows)
  * `fact_account_month` (Monthly portfolio snapshot for cohort recovery tracking)

### 2.5 Feature Layer (Machine Learning & Causal Inference)
* Generates account-level and cohort-level behavioral aggregates:
  * Rolling 30d/60d contact intensity, cumulative promises, delinquency velocity.
  * Propensity score deciles and pre/post policy intervention flags.

### 2.6 Metrics & Reporting Layer
* Version-controlled, audited SQL aggregation views (`sql/09_metrics.sql`, `sql/10_monthly_performance.sql`).
* Enforces invariant assertions (e.g., Gross = Canonical + Quarantined). If any invariant is violated, the publishing pipeline fails with a hard halt.

---

## 3. Data Contracts & Key Constraints

```yaml
data_contracts:
  fact_payment:
    primary_key: [payment_id]
    foreign_keys:
      account_id: dim_account.account_id
    invariants:
      amount_paid: "> 0.0"
      payment_status: "IN ('SUCCESS')"
      is_canonical_payment: "TRUE"
    freshness:
      maximum_lag_hours: 6

  clean_calls:
    primary_key: [call_id]
    foreign_keys:
      account_id: dim_account.account_id
      agent_id: dim_agent.agent_id
    invariants:
      duration_seconds: ">= 0"
      call_end_time: ">= call_start_time"
```

---

## 4. Operational Reliability & Lifecycle Management

### 4.1 Incremental Processing & Late-Arriving Data
* **Event-Time Watermarking**: Financial settlements and bank UTRs often arrive with a 24–48 hour delay. Pipelines process data using an **event-time watermark of 72 hours**.
* **Idempotent Upserts**: Updates to account balances and status transitions use deterministic upsert logic (`MERGE INTO` or surrogate key hash matching).

### 4.2 Automated Anomaly Detection & Dashboard Circuit Breakers
Before any dashboard refresh or executive metric export is permitted, the pipeline executes the assertions in `sql/12_reconciliation.sql`:
1. **Fanout Detection**: Verifies that attributed collections across channels match canonical collections to the exact rupee.
2. **Rate Bound Check**: Asserts that recovery rates and contact rates fall strictly within $[0\%, 100\%]$.
3. **Circuit Breaker**: If `v_production_integrity_failures` returns any rows, the pipeline throws an exception, sends a PagerDuty alert, and locks the dashboard in a safe "Audit in Progress" state, preventing leadership from acting on corrupted metrics.
