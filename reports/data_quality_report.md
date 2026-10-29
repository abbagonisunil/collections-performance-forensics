# Comprehensive Data Quality & Forensic Audit Report

**Project**: Collections Performance Forensics  
**Audit Standard**: Production Analytics Architecture & Financial Integrity Standards  
**Version**: 1.0.0 (Audited)

---

## 1. Executive Summary
This report documents the forensic data quality assessment of approximately 12 months of collections operations across 17 disparate source systems. The investigation revealed critical vulnerabilities in the legacy reporting layer:
* **Gross Collections Inflation**: Duplicate payment webhook retries and non-canonical transaction logging inflated reported recovery by **8.4% to 14.2%** (representing over ₹5.8 Cr in non-existent cash).
* **Vendor Disposition Code Remapping**: Telephony vendors altered raw disposition categories, artificially boosting Right-Party Contact (RPC) rates by **18%** without corresponding payment conversion.
* **Selection & Denominator Distortion**: Operational reporting systematically dropped uncontacted delinquent accounts from conversion denominators, creating an illusion of operational efficiency.

---

## 2. Source Inventory and Coverage Summary

| Source Name | Expected Grain | Ingestion Key | Date Coverage | Historical Completeness | Primary Key Status |
|---|---|---|---|---|---|
| `borrowers` | 1 row / borrower | `borrower_id` | 12 Months | 98.4% | Unique, 0 duplicates |
| `accounts` | 1 row / account | `account_id` | 12 Months | 99.1% | Unique, 0 duplicates |
| `agents` | 1 row / agent | `agent_id` | 12 Months | 94.2% | Multi-login aliases found |
| `agent_sessions` | 1 row / session | `session_id` | 12 Months | 91.0% | Overlapping timestamps (<3%) |
| `campaigns` | 1 row / campaign | `campaign_id` | 12 Months | 99.5% | Unique |
| `daily_targeting` | 1 row / account-day | `targeting_id` | 12 Months | 96.8% | Suppressed accounts missing scores |
| `calls` | 1 row / call | `call_id` | 12 Months | 97.5% | Compliant |
| `call_attempts` | 1 row / attempt | `attempt_id` | 12 Months | 95.0% | Compliant |
| `call_dispositions` | 1 row / disposition | `disposition_id`| 12 Months | 96.2% | Vendor code remapped Month 5 |
| `whatsapp_events` | 1 row / event | `event_id` | 12 Months | 99.0% | High reliability |
| `sms_events` | 1 row / event | `event_id` | 12 Months | 98.2% | High reliability |
| `field_visits` | 1 row / visit | `visit_id` | 12 Months | 88.5% | High location null rate (12%) |
| `promises_to_pay` | 1 row / promise | `ptp_id` | 12 Months | 97.1% | High repeat broken promises |
| `payments` | 1 row / transaction | `payment_id` | 12 Months | 99.8% | **Critical webhook duplication** |
| `vendor_telephony` | 1 row / CDR | `cdr_id` | 12 Months | 94.0% | Disconnect code drift |
| `complaints` | 1 row / ticket | `complaint_id` | 12 Months | 99.5% | 12 calling-hour violations |
| `account_status_history`| 1 row / change | `status_event_id`| 12 Months | 93.0% | SCD Type 2 gapped intervals |

---

## 3. Forensic Issue Deep-Dive & Impact Quantification

### Issue DQ-001: Duplicate Payment Ingestion via Webhook Retries
* **Issue ID**: `DQ-PAY-001`
* **Severity**: `CRITICAL`
* **Affected Source & Columns**: `payments.transaction_reference`, `payments.payment_timestamp`, `payments.account_id`
* **Detection Rule**: Exact match on `transaction_reference` OR same `account_id` + `amount_paid` within 600-second window.
* **Affected Row Count**: 4,210 duplicate events across 12 months.
* **Affected Monetary Amount**: **₹5,820,000 INR** (Direct overstatement of cash).
* **Treatment**: Applied deterministic deduplication via `sql/04_deduplication.sql`, retaining only the initial canonical transaction and logging retries in `payment_deduplication_log`.
* **Residual Uncertainty**: Minor gateway latency (<30s) on cross-bank settlements.
* **Business Impact**: Eliminated phantom recovery that artificially drove the claimed 11% MoM surge.
* **Remediation**: Implement idempotent webhook receiver with 24-hour Redis de-duplication cache.

---

### Issue DQ-002: Vendor Telephony Disposition Code Remapping
* **Issue ID**: `DQ-TEL-002`
* **Severity**: `HIGH`
* **Affected Source & Columns**: `call_dispositions.disposition_code`, `call_dispositions.disposition_category`
* **Detection Rule**: Frequency distribution shift of disposition codes by vendor over monthly time series.
* **Affected Row Count**: 38,400 call records in Vendor Y queue.
* **Affected Account Count**: 14,200 unique accounts.
* **Affected Monetary Amount**: N/A (Operational metric distortion).
* **Treatment**: Built `ref_disposition_crosswalk` mapping Vendor Y's "Unconfirmed Ringing" code back to `UNREACHED`.
* **Residual Uncertainty**: Lack of audio recording archives to verify speech recognition.
* **Business Impact**: Reduced reported RPC rate from 23.2% back to genuine 19.4% baseline.
* **Remediation**: Issue contractual penalty to Vendor Y; mandate standardized API response codes.

---

### Issue DQ-003: Non-Compliant Calling Hours (RBI Regulatory Exposure)
* **Issue ID**: `DQ-TIME-003`
* **Severity**: `CRITICAL` (Compliance Risk)
* **Affected Source & Columns**: `calls.call_start_time`, `calls.account_id`
* **Detection Rule**: Timestamp normalized to `Asia/Kolkata` with `call_hour_local < 8 OR call_hour_local >= 19`.
* **Affected Row Count**: 12,850 calls dialed before 08:00 AM or after 07:00 PM local time.
* **Affected Account Count**: 6,400 accounts.
* **Treatment**: Flagged in `clean_calls.is_rbi_compliant_calling_hour = FALSE` and correlated with consumer complaint filings.
* **Residual Uncertainty**: Borrower location inferred from state master when GPS telemetry is missing.
* **Business Impact**: Direct causation of 12 regulatory grievance escalations.
* **Remediation**: Hard-lock dialer outbound gateway queues outside 08:00–19:00 IST.

---

### Issue DQ-004: Denominator Manipulation in Legacy Conversion Metrics
* **Issue ID**: `DQ-DENOM-004`
* **Severity**: `HIGH`
* **Affected Source & Columns**: Operational Daily Reporting Layer
* **Detection Rule**: Compare eligible delinquent opening exposure with reported denominator populations.
* **Affected Row Count**: 18,500 uncontacted delinquent accounts omitted.
* **Treatment**: Reconstructed standardized recovery rate using static opening principal balance: `SUM(amount_paid) / SUM(opening_principal)`.
* **Residual Uncertainty**: Account status transitions occurring mid-month.
* **Business Impact**: Restored true portfolio-wide recovery rate (14.8%) versus inflated operational rate (22.5%).
* **Remediation**: Deprecate legacy operational report; mandate golden dataset views for leadership.

---

## 4. Raw-to-Golden Monetary Reconciliation

```
[Raw Payments Ingested]
      │
      ├── Gross Ingested Cash: ₹54,020,000 INR (100.0%)
      │
      ├── (-) Webhook Replay Retries: ₹3,140,000 INR (5.8%)  ---> Quarantined
      ├── (-) Exact Transaction Duplicates: ₹1,680,000 INR (3.1%) ---> Quarantined
      ├── (-) Failed / Reversed Transactions: ₹1,000,000 INR (1.9%) ---> Quarantined
      │
      ▼
[Clean Deduplicated Payments]
      │
      └── Net Canonical Realized Cash: ₹48,200,000 INR (89.2%)
            │
            ▼
[Golden Fact Payment Table]
      │
      └── Matched to Account Dimension: ₹48,200,000 INR (100.0% Match)
            │
            ├── Attributed to Omnichannel Touches: ₹42,100,000 INR (87.3%)
            └── Organic / Self-Serve Collections: ₹6,100,000 INR (12.7%)
```

**Reconciliation Discrepancy**: **₹0.00 INR**. Every rupee is accounted for across pipeline layers.
