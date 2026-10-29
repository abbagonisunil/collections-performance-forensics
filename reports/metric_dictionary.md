# Audited Metric Dictionary & Forensic Definitions

**Version**: 2.1.0  
**Status**: APPROVED & AUDITED  
**Governance Standard**: Independent Forensic Analytics Standard  

---

## 1. Overview and Core Principles
Legacy collections reporting conflates **telephony volume with debtor contact**, **gross webhook logs with settled cash**, and **volume growth with operational efficiency**. This dictionary establishes mathematically rigorous, auditable definitions designed to challenge legacy metrics.

---

## 2. Comprehensive Metric Specifications

### 2.1 Account Contact Rate
* **Metric ID**: `MET-01`
* **Business Meaning**: Measures the proportion of targeted delinquent accounts with whom at least one meaningful human communication attempt was established.
* **Legacy Flaw**: Defined as `Connected Calls / Dial Attempts`. Dialer connection includes voicemail, auto-attendants, and wrong numbers; attempts count the same account 10 times.
* **Audited Definition**:
  $$\text{Contact Rate} = \frac{\text{Unique Delinquent Accounts Connected } (\ge 15\text{s})}{\text{Unique Delinquent Accounts Targeted}}$$
* **Numerator**: `COUNT(DISTINCT c.account_id) WHERE c.duration_seconds >= 15 AND d.disposition_category IN ('RPC', 'NON_RPC')`
* **Denominator**: `COUNT(DISTINCT t.account_id) WHERE t.is_suppressed = FALSE`
* **Grain**: Account-Month.
* **Exclusions**: IVR dropoffs (<15s), system busy tones, network congestion failures.
* **Reconciliation Check**: Numerator $\le$ Denominator.

---

### 2.2 Right-Party Contact (RPC) Rate
* **Metric ID**: `MET-02`
* **Business Meaning**: Measures validated contact where debtor identity is confirmed.
* **Legacy Flaw**: Defined as `Calls Tagged as RPC / Connected Calls`. Vulnerable to vendor code remapping (e.g. tagging unconfirmed ring-backs as RPC to hit SLA targets).
* **Audited Definition**:
  $$\text{RPC Rate} = \frac{\text{Unique Accounts with Verified Borrower Identity}}{\text{Unique Accounts Connected}}$$
* **Numerator**: `COUNT(DISTINCT c.account_id) WHERE d.canonical_disposition_category = 'RPC'`
* **Denominator**: `COUNT(DISTINCT c.account_id) WHERE c.duration_seconds >= 15`
* **Grain**: Account-Month.
* **Exclusions**: Calls where relative or third party answered (`NON_RPC`), wrong numbers.
* **Reconciliation Check**: RPC Accounts $\le$ Connected Accounts $\le$ Targeted Accounts.

---

### 2.3 Promise-to-Pay (PTP) Conversion Rate
* **Metric ID**: `MET-03`
* **Business Meaning**: Proportion of verified contacted accounts securing an explicit future repayment commitment.
* **Legacy Flaw**: Defined as `Total Promises Logged / Completed Calls`. Double-counts multiple non-binding promises recorded in the same shift.
* **Audited Definition**:
  $$\text{PTP Rate} = \frac{\text{Unique Accounts Securing Valid Future Commitment}}{\text{Unique RPC Accounts}}$$
* **Numerator**: `COUNT(DISTINCT p.account_id) WHERE p.promised_due_date >= CAST(p.ptp_created_time AS DATE) AND p.promised_amount > 0`
* **Denominator**: `COUNT(DISTINCT c.account_id) WHERE d.canonical_disposition_category = 'RPC'`
* **Grain**: Account-Month.
* **Exclusions**: Back-dated promises, zero-rupee commitments.
* **Reconciliation Check**: PTP Accounts $\le$ RPC Accounts.

---

### 2.4 PTP Kept Rate (Maturity Adjusted)
* **Metric ID**: `MET-04`
* **Business Meaning**: Evaluates whether repayment commitments materialize into settled cash within an auditable maturity window.
* **Legacy Flaw**: Unadjusted ratio of `Payments / Total Promises`. Fails to account for maturity timing (recent promises marked broken prematurely, or future payments incorrectly credited to past broken promises).
* **Audited Definition**:
  $$\text{PTP Kept Rate} = \frac{\text{Matured Promises with Settled Payment within Due Date + 3d Grace}}{\text{Total Matured Promises Exposed}}$$
* **Numerator**: `COUNT(DISTINCT p.ptp_id) WHERE pay.payment_status = 'SUCCESS' AND pay.payment_timestamp BETWEEN p.ptp_created_time AND (p.promised_due_date + INTERVAL 3 DAY)`
* **Denominator**: `COUNT(DISTINCT p.ptp_id) WHERE p.promised_due_date <= (CURRENT_DATE - INTERVAL 3 DAY)`
* **Grain**: Promise Cohort / Maturity Month.
* **Exclusions**: Immature promises (due date in future) must be censored, not classified as broken.
* **Reconciliation Check**: Kept Promises $\le$ Matured Promises.

---

### 2.5 Cohort Recovery Rate (Primary Financial Benchmark)
* **Metric ID**: `MET-05`
* **Business Meaning**: Primary financial recovery benchmark evaluating realized cash against static eligible exposure.
* **Legacy Flaw**: Ratio of `Gross Collections(Month M) / Gross Collections(Month M-1)`. This measures scale/volume expansion rather than collection efficiency, and is severely corrupted by duplicate webhook retries.
* **Audited Definition**:
  $$\text{Cohort Recovery Rate} = \frac{\text{Realized Canonical Cash Collected in Period}}{\text{Opening Eligible Delinquent Exposure at Cohort Inception}}$$
* **Numerator**: `SUM(p.amount_paid) WHERE p.payment_status = 'SUCCESS' AND p.is_canonical_payment = TRUE`
* **Denominator**: `SUM(a.opening_principal) WHERE a.status IN ('ACTIVE', 'DELINQUENT') AND a.dpd > 0`
* **Grain**: Portfolio-Month / Cohort-Month.
* **Exclusions**: Duplicate retries, reversals, refunds, chargebacks. Dynamic/closing balance must NEVER be used in denominator.
* **Reconciliation Check**: Canonical Collections = Gross Collections - Duplicates - Reversals.

---

### 2.6 Recovery Per Productive Agent-Hour
* **Metric ID**: `MET-06`
* **Business Meaning**: Operational human efficiency evaluating recovered cash against actual productive phone time.
* **Legacy Flaw**: `Total Collections / (Headcount * 8h * 22d)`. Assumes 100% attendance and zero shrinkage.
* **Audited Definition**:
  $$\text{Recovery / Agent-Hour} = \frac{\text{Eligible Collections Attributed to Human Outreach}}{\text{Productive Agent Hours (Talk Duration + Wrap Duration)} / 3600}$$
* **Numerator**: `SUM(p.amount_paid) WHERE p.attributed_channel IN ('CALL', 'PREDICTIVE_DIALER')`
* **Denominator**: `SUM(s.talk_duration_sec + s.wrap_up_duration_sec) / 3600.0`
* **Grain**: Agent-Month.
* **Exclusions**: Overlapping sessions, idle wait states, meal breaks.
* **Reconciliation Check**: Productive Hours $\le$ Total Logged-in Hours $\le$ Shift Hours.

---

### 2.7 Month-over-Month Relative Growth vs Percentage Point Change
* **Metric ID**: `MET-07`
* **Business Meaning**: Resolves ambiguity in the phrase *"Recovery improved by 11% month-on-month"*.
* **Audited Framework**:
  1. **Relative Growth Rate (%)**:
     $$\Delta\%_{\text{rel}} = \frac{\text{Rate}_M - \text{Rate}_{M-1}}{\text{Rate}_{M-1}} \times 100$$
  2. **Absolute Percentage Point Change (pp)**:
     $$\Delta\text{pp} = \text{Rate}_M - \text{Rate}_{M-1}$$
* **Rule**: Reporting must explicitly declare both metrics. A baseline rate of 10% moving to 11.1% is a +11% relative increase, but only a +1.1 pp gain.
