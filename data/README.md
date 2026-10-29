# Data Directory & Data Management Guide

## 1. Directory Structure

```
data/
├── raw/         # Immutable raw source exports (CSV / Parquet / JSON). PII protected, ignored by git.
├── staging/     # Normalized, typed schemas with raw codes preserved.
├── clean/       # Canonical timestamps, deduplicated records, resolved entities, quarantined records.
├── golden/      # Analytical dimensions, canonical payment facts, account-month snapshots (DuckDB database).
└── features/    # Aggregated feature tables for statistical, counterfactual, and ML models.
```

## 2. Expected Source Datasets (17 Sources)

To run the forensic investigation on real collections records, place any or all of the following source files into `data/raw/` (supported formats: `.csv`, `.parquet`, `.json`, `.jsonl`):

| Source Name | Expected Grain | Key Identifier | Description |
|---|---|---|---|
| `borrowers` | 1 row per borrower | `borrower_id` | Core borrower demographics, risk score, geography, preferred language |
| `accounts` | 1 row per account | `account_id` | Loan accounts, opening principal, current balance, product, client |
| `agents` | 1 row per agent | `agent_id` | Collection agents, tenure, skill level, manager, team |
| `agent_sessions` | 1 row per session | `session_id` | Login/logout timestamps, idle time, active dialing time |
| `campaigns` | 1 row per campaign | `campaign_id` | Collections strategy, start/end dates, target segment, channel mix |
| `daily_targeting` | 1 row per account-day | `targeting_id` | Daily target allocations, model score bucket, assigned channel |
| `calls` | 1 row per call | `call_id` | Human & dialer call records, duration, wait time, telephony vendor |
| `call_attempts` | 1 row per attempt | `attempt_id` | Dialer attempt attempts, ring time, dial status |
| `call_dispositions` | 1 row per disposition | `disposition_id`| Vendor disposition codes, sub-codes, agent notes |
| `whatsapp_events` | 1 row per WA event | `event_id` | Sent, delivered, read, button clicks, inbound responses |
| `sms_events` | 1 row per SMS event | `event_id` | SMS delivery status, link clicks, carrier responses |
| `field_visits` | 1 row per field visit | `visit_id` | Field officer visits, geo-coordinates, visit outcome |
| `promises_to_pay` | 1 row per PTP | `ptp_id` | PTP promised amount, due date, channel taken, status |
| `payments` | 1 row per transaction | `payment_id` | Cash collected, transaction timestamp, payment method, settlement status |
| `vendor_telephony` | 1 row per CDR | `cdr_id` | Carrier/telephony raw logs, disconnect cause, audio latency |
| `complaints` | 1 row per ticket | `complaint_id` | Grievance tickets, regulatory category, severity, resolution |
| `account_status_history`| 1 row per status change| `status_event_id`| Historical DPD progression, write-off, restructuring, closure |

## 3. Data Privacy & Compliance (RBI / Digital Lending Guidelines)

- **PII Redaction**: Do not commit unmasked phone numbers, names, PAN, Aadhaar, or bank account numbers to version control.
- **Local Storage**: All raw data files placed in `data/raw/` are excluded by `.gitignore`.
- **Audit Trail**: Every record modified, quarantined, or deduplicated is logged with decision codes in the clean layer decision log.

## 4. Current Status: Awaiting Raw Source Data

No external raw data was provided in the initial distribution repository. The pipeline, schemas, SQL models, tests, and dashboard are fully built and configured. When raw files are dropped into `data/raw/`, running `make pipeline` or `python -m src.pipeline` automatically ingests, validates, cleans, and builds the golden analytics database.
