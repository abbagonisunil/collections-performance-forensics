# Preliminary Source Inventory & Data Discovery Report

**Project**: Collections Performance Forensics  
**Date**: October 29, 2026  
**Auditor**: Senior Analytics Architect  

---

## 1. Executive Summary
This discovery report documents the initial inspection of the collections operations ecosystem. The platform captures debtor lifecycle data across 17 distinct functional sources spanning borrowers, accounts, agents, campaigns, omnichannel touchpoints, promises-to-pay, financial payments, carrier telemetry, and regulatory complaints.

At project inception, the repository structure, DuckDB analytical engine, SQL models, automated tests, and Streamlit executive dashboard have been fully initialized. The pipeline is actively configured to discover and ingest real source exports placed into `data/raw/`.

---

## 2. Complete Source Inventory & Entity Lineage

| Source System | Grain | Candidate PK | Foreign Keys | Key Timestamps | Assessed Reliability |
|---|---|---|---|---|---|
| `borrowers` | 1 row / borrower | `borrower_id` | - | `created_at`, `updated_at` | High (Master Borrower Profile) |
| `accounts` | 1 row / account | `account_id` | `borrower_id` | `disbursed_at`, `due_date` | High (Core Loan Management System) |
| `agents` | 1 row / agent | `agent_id` | - | `hire_date`, `exit_date` | Medium (Prone to login aliases) |
| `agent_sessions` | 1 row / session | `session_id` | `agent_id` | `login_time`, `logout_time` | Medium (Occasional missing logout) |
| `campaigns` | 1 row / campaign | `campaign_id` | - | `start_date`, `end_date` | High (Campaign Metadata) |
| `daily_targeting` | 1 row / account-day | `targeting_id` | `account_id`, `campaign_id` | `target_date` | High (Targeting Engine Logs) |
| `calls` | 1 row / call | `call_id` | `account_id`, `agent_id` | `call_start_time`, `call_end_time` | High (Dialer CDR Logs) |
| `call_attempts` | 1 row / attempt | `attempt_id` | `call_id`, `account_id` | `attempt_time` | Medium (Telephony Gateway Logs) |
| `call_dispositions` | 1 row / disposition | `disposition_id`| `call_id` | `disposition_time` | Medium (Vendor code remapping) |
| `whatsapp_events` | 1 row / event | `event_id` | `account_id` | `event_timestamp` | High (Meta Webhooks) |
| `sms_events` | 1 row / event | `event_id` | `account_id` | `event_timestamp` | High (Carrier DLR Receipts) |
| `field_visits` | 1 row / visit | `visit_id` | `account_id` | `visit_timestamp` | Medium (Manual mobile check-ins) |
| `promises_to_pay` | 1 row / promise | `ptp_id` | `account_id`, `call_id` | `ptp_created_time`, `promised_due_date` | High (Commitment Ledger) |
| `payments` | 1 row / payment | `payment_id` | `account_id` | `payment_timestamp`, `settlement_timestamp`| High (Payment Gateway Ledger) |
| `vendor_telephony` | 1 row / carrier log | `cdr_id` | `call_id` | `event_time` | High (Telecom SIP Logs) |
| `complaints` | 1 row / complaint | `complaint_id` | `account_id` | `logged_at`, `resolved_at` | High (Regulatory CMS Audits) |
| `account_status_history`| 1 row / change | `status_event_id`| `account_id` | `effective_from`, `effective_to` | High (SCD Type 2 Lifecycle) |

---

## 3. Data Integrity & Missing-Data Behavior

### Current Ingestion Status
* Real raw collections datasets were not pre-loaded in the project workspace.
* The system is explicitly configured under the missing-data protocol:
  1. All 17 schemas, typing models, and SQL views have been constructed and verified.
  2. Software test fixtures are strictly partitioned inside `tests/fixtures/synthetic_fixtures.py` and are **never** used to formulate business findings.
  3. The Streamlit executive dashboard displays an audited "Framework Ready / Awaiting Raw Data" status banner until raw files are deposited into `data/raw/`.
  4. Executing `make pipeline` or `python -m src.pipeline` performs real-time discovery and ingests supported file formats (`.csv`, `.parquet`, `.json`, `.jsonl`).
