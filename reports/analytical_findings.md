# Analytical Findings & Forensic Investigation Report

**Investigation Title**: Forensic Reconstruction of Collections Performance and Driver Decomposition  
**Author**: Senior Analytics Architect & Forensic Investigation Lead  
**Scope**: 12-Month Audited Collections Trajectory across 13 Dimensions, 7 Statistical Biases, and 4 Mission Questions  

---

## Content Classification Framework
To maintain complete analytical integrity, all content in this report is strictly categorized into:
1. **[VERIFIED IMPLEMENTATION]**: Analytical code, SQL models, data contracts, and pipeline architectures implemented and verified via automated test suites.
2. **[EMPIRICAL FINDINGS]**: Findings calculated directly from actual business records. Where raw source data is unpopulated (`data/raw/` currently contains 0/17 source files), empirical metrics are explicitly reported as `AWAITING_REAL_DATA` / `NOT_VERIFIABLE`.
3. **[ILLUSTRATIVE SCENARIOS / ASSUMPTIONS]**: Quantitative examples demonstrating methodology mechanics without claiming historical company occurrence.

---

## 1. Answer to Mission Question 1: What Happened?

### 1.1 Verified Pipeline Implementation
* **Pipeline Architecture**: Rebuilt end-to-end DuckDB pipeline ([`sql/01_staging.sql`](file:///Users/sunill/.gemini/antigravity-ide/scratch/collections-performance-forensics/sql/01_staging.sql) through [`sql/12_reconciliation.sql`](file:///Users/sunill/.gemini/antigravity-ide/scratch/collections-performance-forensics/sql/12_reconciliation.sql)) tracking 12 monthly periods.
* **Separation of Ledgers**: Maintained two distinct cash reporting streams:
  1. *Reported Naive Collections*: Raw payment gateway callback events.
  2. *Audited Canonical Cash*: Gateway payments with verified settlement confirmation and deduplication.
* **Metric Standardization**: Established invariant definitions:
  - $\text{Canonical Recovery Rate} = \frac{\text{Realized Settled Cash}}{\text{Opening Eligible Loan Exposure}} \times 100$
  - $\text{Relative MoM Change} = \frac{\text{Rate}_t - \text{Rate}_{t-1}}{\text{Rate}_{t-1}} \times 100$
  - $\text{Percentage-Point Change} = \text{Rate}_t - \text{Rate}_{t-1}$
  - $\text{Absolute Collection Growth} = \text{Cash}_t - \text{Cash}_{t-1}$

### 1.2 Empirical Status
* **Status**: `AWAITING_REAL_DATA`.
* **Findings**: In the absence of raw collections records in `data/raw/`, historical monthly recovery rates, opening exposure amounts, and duplicate cash overstatements cannot be factually computed. The audit table returns status `NOT_VERIFIABLE` with zero fabricated figures.

### 1.3 Illustrative Scenario (Methodology Demonstration)
* *Demonstration Concept*: If naive reporting counts duplicate gateway webhook retries without settlement verification, apparent collections diverge sharply from realized cash.
* *Simulation Mechanics*: Under a scenario where unconfirmed webhook retries grow from 0% to 15% of payment volume, reported gross collections appear to grow at ~11% MoM, while canonical settled growth is substantially lower.

---

## 2. Answer to Mission Question 2: Why Did It Happen? (13 Dimensions)

The analytical repository implements investigation views for all 13 required business dimensions in [`sql/11_driver_analysis.sql`](file:///Users/sunill/.gemini/antigravity-ide/scratch/collections-performance-forensics/sql/11_driver_analysis.sql):

### Dimension 1: Portfolio Mix (Product Type)
* **[VERIFIED IMPLEMENTATION]**: View `v_driver_01_product_portfolio` groups loan accounts by product type (Personal Loans, Two-Wheeler, Consumer Durable), computing exposure, settled recovery, and product-specific recovery rates.
* **[EMPIRICAL STATUS]**: Awaiting raw loan portfolio ingestion.

### Dimension 2: DPD Bucket (Delinquency Cohorts)
* **[VERIFIED IMPLEMENTATION]**: View `v_driver_02_dpd_bucket` segments accounts into standardized buckets (DPD 1–30, 31–60, 61–90, 91–120, 120+). Implemented Kitagawa shift-share decomposition in [`src/statistical_analysis.py`](file:///Users/sunill/.gemini/antigravity-ide/scratch/collections-performance-forensics/src/statistical_analysis.py) separating within-cohort operational improvement from between-cohort mix shifts:
  $$\Delta R = \sum \bar{w}_k \Delta r_k + \sum \bar{r}_k \Delta w_k$$
* **[EMPIRICAL STATUS]**: Awaiting raw delinquency bucket history.

### Dimension 3: Enterprise Client
* **[VERIFIED IMPLEMENTATION]**: View `v_driver_03_client` tracks performance across originating banking and FinTech partners, auditing whether client-level contract allocations alter aggregate metrics.
* **[EMPIRICAL STATUS]**: Awaiting raw client portfolio records.

### Dimension 4: Geography (State & Region)
* **[VERIFIED IMPLEMENTATION]**: View `v_driver_04_geography` aggregates recovery rates by borrower state and digital payment adoption tier.
* **[EMPIRICAL STATUS]**: Awaiting borrower address KYC records.

### Dimension 5: Language Match
* **[VERIFIED IMPLEMENTATION]**: View `v_driver_05_language` audits call outcomes when borrower primary language matches agent dialect vs mismatched routing.
* **[EMPIRICAL STATUS]**: Awaiting dialer language preference fields.

### Dimensions 6 & 7: Agent & Agent Tenure
* **[VERIFIED IMPLEMENTATION]**: View `v_driver_06_07_agent_tenure` measures recovery per productive agent-hour, RPC rate, and PTP conversion across agent tenure cohorts (<3 months, 3–12 months, >12 months).
* **[EMPIRICAL STATUS]**: Awaiting agent session and dialer login logs.

### Dimension 8: Campaign Strategy
* **[VERIFIED IMPLEMENTATION]**: View `v_driver_08_campaign` tracks Champion vs Challenger dialer and digital outreach strategies.
* **[EMPIRICAL STATUS]**: Awaiting campaign assignment logs.

### Dimension 9: Omnichannel Conversion
* **[VERIFIED IMPLEMENTATION]**: View `v_driver_09_channel` evaluates conversion rates and cost per rupee recovered across Voice Calling, WhatsApp, SMS, and Field Operations.
* **[EMPIRICAL STATUS]**: Awaiting multi-channel outreach logs.

### Dimension 10: Telephony Vendor
* **[VERIFIED IMPLEMENTATION]**: View `v_driver_10_telephony_vendor` audits vendor disposition mapping, cross-referencing contact claims against downstream payments.
* **[EMPIRICAL STATUS]**: Telephony vendor disposition mapping analysis is implemented; empirical vendor impact is awaiting source data.

### Dimension 11: Calling Time of Day
* **[VERIFIED IMPLEMENTATION]**: View `v_driver_11_calling_hour` normalizes timestamps to Asia/Kolkata (IST) and audits connect rates by hour, flagging calls outside the 08:00–19:00 RBI regulatory window.
* **[EMPIRICAL STATUS]**: Awaiting raw CDR timestamp records.

### Dimension 12: Attempt Frequency
* **[VERIFIED IMPLEMENTATION]**: View `v_driver_12_attempt_frequency` evaluates marginal recovery yield per call attempt, detecting contact fatigue and complaint escalation beyond optimal attempt thresholds.
* **[EMPIRICAL STATUS]**: Awaiting call attempt sequence records.

### Dimension 13: Borrower Risk Tier
* **[VERIFIED IMPLEMENTATION]**: View `v_driver_13_borrower_segment` stratifies debtors by risk score, verifying whether apparent recovery gains stemmed from targeting higher-propensity accounts.
* **[EMPIRICAL STATUS]**: Awaiting borrower credit bureau scores.

---

## 3. Answer to Mission Question 3: Is the 11% Improvement Real?

### 3.1 Forensic Verdict
**Executive Conclusion**: **THE CLAIM CANNOT CURRENTLY BE VERIFIED AS A LIKE-FOR-LIKE OPERATIONAL GAIN.**

### 3.2 Analytical Audit
1. **Data Availability**: The required 12 months of production transaction and exposure records are currently unpopulated in `data/raw/`. Under strict analytical standards, the claim status is formally classified as `NOT_VERIFIABLE`.
2. **Accounting Integrity**: The 11% claim cannot be verified without distinguishing:
   - Relative MoM change: $(\text{Rate}_t - \text{Rate}_{t-1}) / \text{Rate}_{t-1} \times 100$
   - Percentage-point change: $\text{Rate}_t - \text{Rate}_{t-1}$
   - Absolute collection growth: $\text{Cash}_t - \text{Cash}_{t-1}$
3. **Mix Shift Sensitivity**: Shift-share modeling demonstrates that an apparent aggregate lift can be achieved mechanically by allocating dialer queues toward low-risk early-stage DPD cohorts without improving operational effectiveness on distressed accounts.

---

## 4. Answer to Mission Question 4: Strategic Capital Allocation (₹10 Crore)

### 4.1 Evaluation of Six Strategic Options
The financial engine ([`src/investment_model.py`](file:///Users/sunill/.gemini/antigravity-ide/scratch/collections-performance-forensics/src/investment_model.py)) models cumulative monthly net cash flows, net benefit, and ROI across all six strategic options:

| Investment Option | Total Cost (₹ Cr) | Addressable Exposure (₹ Cr) | Base Gross Recovery (₹ Cr) | Base Net Benefit (₹ Cr) | Base ROI (%) | Target Lift for +27.5% ROI |
|---|---|---|---|---|---|---|
| **Option 4: Better Borrower Targeting** | **10.0** | **250.0** | **4.00** | **-6.00** | **-60.0%** | **5.10% (₹12.75 Cr Gross)** |
| Option 5: WhatsApp / Digital Engagement | 10.0 | 180.0 | 2.52 | -7.48 | -74.8% | 7.08% (₹12.75 Cr Gross) |
| Option 1: Better Telephony Infrastructure | 10.0 | 220.0 | 1.98 | -8.02 | -80.2% | 5.80% (₹12.75 Cr Gross) |
| Option 3: AI Voice Automation | 10.0 | 160.0 | 1.92 | -8.08 | -80.8% | 7.97% (₹12.75 Cr Gross) |
| Option 6: Field Operations | 10.0 | 90.0 | 1.35 | -8.65 | -86.5% | 14.17% (₹12.75 Cr Gross) |
| Option 2: More Collection Agents | 10.0 | 150.0 | 1.20 | -8.80 | -88.0% | 8.50% (₹12.75 Cr Gross) |

### 4.2 Mathematical Proof of Legacy Financial Contradictions
Under standard corporate finance identities:
$$\text{Incremental Net Benefit} = \text{Gross Incremental Recovery} - \text{Total Incremental Cost}$$
$$\text{ROI} = \frac{\text{Incremental Net Benefit}}{\text{Total Incremental Cost}} \times 100$$
1. If Total Cost = ₹10.0 Cr and Gross Recovery = ₹4.0 Cr $\implies$ Net Benefit = **-₹6.0 Cr**, $\text{ROI} = \mathbf{-60.0\%}$ (Net Loss).
2. For a ₹10.0 Cr outlay to achieve $+27.5\%$ ROI ($+₹2.75\text{ Cr}$ Net Benefit), Gross Recovery must equal **₹12.75 Cr** (a $5.10\%$ absolute lift on ₹250 Cr exposure, not $1.60\%$).

### 4.3 Prudent Recommendation: The ₹2.0 Cr Staged Pilot
Deploying ₹10 Cr full capital upfront carries excessive downside risk. We recommend an initial **₹2.0 Crore Staged Pilot** for **Option 4: Better Borrower Targeting**:
- **Phase 1 Commitment**: ₹2.0 Cr (₹0.60 Cr setup Capex + ₹1.40 Cr 6-month Opex).
- **Target Population**: 50,000 accounts (₹60.0 Cr exposure).
- **Target Economics**: Expected lift of +3.50% $\implies$ **₹2.10 Cr Gross Recovery**, **+₹0.10 Cr Net Benefit**, breaking even in **5.3 months**.
- **Stage-Gate Condition**: Do not release the remaining ₹8.0 Cr unless Month 6 DiD confirms a causal lift $\ge 2.50\text{ pp}$ ($p < 0.05$) and verified collections $\ge ₹2.10\text{ Cr}$.
