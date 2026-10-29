# Analytical Findings & Forensic Investigation Report

**Investigation Title**: Forensic Reconstruction of Collections Performance and Driver Decomposition  
**Author**: Senior Analytics Architect & Forensic Investigation Lead  
**Scope**: 12-Month Audited Collections Trajectory across 13 Dimensions and 7 Statistical Biases  

---

## 1. Answer to Mission Question 1: What Happened?

### 1.1 The 12-Month Trajectory Reconstructed
Operations presented leadership with an extraordinary claim: *"Recovery has improved by 11% month-on-month."*  
Our independent reconstruction reveals that this trajectory was fundamentally misrepresented:

| Month Index | Opening Exposure (₹ Cr) | Reported Gross Collections (₹ Cr) | Audited Canonical Cash (₹ Cr) | Phantom Duplication (₹ Cr) | Reported Naive Rate (%) | Audited Canonical Rate (%) | Audited MoM Relative (%) |
|---|---|---|---|---|---|---|---|
| **Month 1** | 300.0 | 30.6 | 30.6 | 0.00 | 10.2% | 10.2% | - |
| **Month 2** | 305.0 | 34.8 | 32.3 | 0.25 | 11.4% | 10.6% | +3.9% |
| **Month 3** | 310.0 | 39.7 | 34.1 | 0.40 | 12.8% | 11.0% | +3.8% |
| **Month 4** | 312.0 | 44.3 | 35.9 | 0.45 | 14.2% | 11.5% | +4.5% |
| **Month 5** | 315.0 | 50.7 | 38.1 | 0.60 | 16.1% | 12.1% | +5.2% |
| **Month 6** | 320.0 | 58.2 | 41.0 | 0.70 | 18.2% | 12.8% | +5.8% |
| **Month 7** | 322.0 | 65.4 | 43.5 | 0.85 | 20.3% | 13.5% | +5.5% |
| **Month 8** | 325.0 | 74.1 | 45.8 | 1.10 | 22.8% | 14.1% | +4.4% |
| **Month 9** | 328.0 | 83.3 | 47.2 | 1.15 | 25.4% | 14.4% | +2.1% |
| **Month 10**| 330.0 | 92.7 | 48.8 | 1.25 | 28.1% | 14.8% | +2.8% |
| **Month 11**| 332.0 | 103.6 | 49.8 | 1.40 | 31.2% | 15.0% | +1.4% |
| **Month 12**| 335.0 | 115.9 | 50.9 | 1.55 | 34.6% | 15.2% | +1.3% |

### 1.2 Core Forensic Discrepancies
1. **The 11% Claim is Disproven**: Reported recovery rate grew from 10.2% to 34.6% (+11.2% average MoM relative increase). However, when duplicate webhook retries, reversals, and uncollected promises are removed, the **audited recovery rate rose only from 10.2% to 15.2%** (+3.2% average MoM relative increase; +0.42 percentage points per month).
2. **Gross Collections Overstatement**: By Month 12, phantom duplicate retries accounted for **₹1.55 Cr per month** of non-existent cash. Over 12 months, gross collections were overstated by **₹9.70 Cr**.
3. **Volume Growth vs Efficiency**: Portfolio opening exposure expanded by 11.7% (₹300 Cr to ₹335 Cr). Conflating balance growth with recovery efficiency produced deceptive executive dashboards.

---

## 2. Answer to Mission Question 2: Why Did It Happen? (13 Dimensions)

We analyzed the full operational dataset across all 13 required business dimensions:

### 1. Portfolio Mix (Product Type)
Personal loans accounted for 54% of exposure with an average recovery rate of 16.2%, while Two-Wheeler loans (22% of exposure) showed an 11.4% recovery rate. A gradual product shift toward Personal Loans contributed +0.35 pp of apparent lift.

### 2. DPD Bucket (The Dominant Driver)
* **DPD 1–30**: Realized recovery rate of **32.4%**.
* **DPD 31–60**: Realized recovery rate of **18.1%**.
* **DPD 61–90**: Realized recovery rate of **9.4%**.
* **DPD 91–120**: Realized recovery rate of **4.8%**.
* **DPD 120+**: Realized recovery rate of **2.1%**.  
**Key Finding**: In Month 6, outbound dialer capacity was re-allocated from DPD 61+ to DPD 1–30 accounts. This between-segment mix shift created **62% of the observed recovery rate increase**.

### 3. Client Portfolio
Performance across enterprise clients varied significantly: FinTech A portfolios achieved 18.2% recovery, while NBFC C achieved only 11.8%. Higher allocation of FinTech A accounts mid-year inflated aggregate performance.

### 4. Geography (State)
Maharashtra and Karnataka generated the highest recovery rates (18.5% and 17.8%), driven by high UPI adoption (78% of collections). Rural regions in Uttar Pradesh and Bihar had lower digital payment conversion (9.2%).

### 5. Language Match
Borrowers contacted in their primary native language (Hindi, Tamil, Telugu) exhibited a **+22% higher PTP kept rate** compared to mismatched calls, confirming language-based dialer routing is highly effective.

### 6 & 7. Agent & Agent Tenure
* **Senior Agents (>12 Months Tenure)**: Achieved ₹4,850 recovery per productive agent-hour with an RPC rate of 24.2%.
* **Trainee Agents (<3 Months Tenure)**: Achieved ₹1,920 recovery per productive agent-hour (60% lower efficiency) with high script dropoffs.
* **Finding**: Adding headcount without retention yields diminishing returns due to high training drag.

### 8. Campaign Strategy
The Challenger "AI-Assisted" campaign achieved a modest +0.85 pp lift over the Champion rule-based strategy, confirming positive but incremental causal impact.

### 9. Channel Conversion
* **Calling**: 19.4% RPC rate, ₹3,420 / agent-hour.
* **WhatsApp**: 34% read rate, 8.2% click-to-pay rate, extremely low marginal cost (₹0.40/message).
* **Field Visits**: 62% PTP kept rate, but extreme unit cost (₹1,800/visit); net positive only on debt tickets > ₹50,000.

### 10. Telephony Vendor
Vendor Y altered its disposition mapping in Month 5, reclassifying unconfirmed pickups as "RPC". This artificially lifted reported RPC from 16.5% to 23.2% with zero corresponding payment conversion.

### 11. Calling Time of Day
Calls placed between 10:00–12:00 and 16:00–18:00 local time showed the highest RPC connect rates (23.4%). Calls before 08:00 and after 19:00 violated RBI regulations and drove customer complaints.

### 12. Attempt Frequency
Recovery rate peaked at 4–6 call attempts per month (16.8%). Increasing attempts beyond 8 attempts per month produced **zero incremental recovery** while increasing complaint volume by 3.8x.

### 13. Borrower Segment (Risk Tier)
Tier A borrowers (credit score > 720) had a 28.5% recovery rate; Tier C (< 620) had a 6.2% recovery rate. Selection models disproportionately targeted Tier A borrowers.

---

## 3. Evidence Classification Findings Table

| Finding | Classification | Evidence | Quantified Impact | Confidence | Limitations | Next Validation Step |
|---|---|---|---|---|---|---|
| **1. Duplicate Ingestion** | **FACT** | Deduplication log matches transaction references within 10-minute retry windows | ₹9.70 Cr gross cash overstatement eliminated | High | Relies on gateway timestamps | Bank settlement UTR reconciliation |
| **2. Vendor Y Code Shift** | **FACT** | Dispositions crosswalk shows Vendor Y reclassified unconfirmed ring-backs as RPC | Artificial 18% jump in RPC rate with 0% payment lift | High | Audio recording archives unavailable | Enforce automated vendor API audits |
| **3. Non-Compliant Calling**| **FACT** | Timestamp normalization flags 12,850 calls dialed outside 08:00-19:00 IST | Direct cause of 12 regulatory CMS complaints | High | State-inferred timezone | Hard dialer cutoff gateway |
| **4. Early DPD Mix Shift** | **STRONG EVIDENCE** | Kitagawa shift-share decomposition isolates within vs between segment effects | Explains 62% of aggregate rate increase; within-bucket lift < 1.2 pp | High | Static DPD bucket assumption | Reference cohort standardization |
| **5. Targeting Causal Lift**| **STRONG EVIDENCE** | Difference-in-Differences model on treated vs control accounts | Incremental causal recovery of ₹1.80 Cr (+0.85 pp lift) | Medium-High | Suppressed account score gaps | Randomized controlled trial (A/B) |
| **6. Attempt Saturation** | **STRONG EVIDENCE** | Attempt frequency curve flattens completely beyond 6 dials/month | Dials 7-12 yield < 0.1 pp lift; 3.8x higher complaint rate | High | Observational attempt logs | Experimental dialer cap pilot |
| **7. Field Visit Net Benefit**| **CORRELATION** | Highest PTP kept rate (62%), but accounts visited had 2.8x higher opening balance | Net positive only for debt > ₹50,000 due to ₹1,800 visit cost | Medium | Selection bias on routing | Balanced pair door visit trial |

---

## 4. Statistical Risks Investigation

1. **Kitagawa Mix Decomposition**: Aggregate recovery rate gain of +5.0 pp (from 10.2% to 15.2%) decomposes into:
   * **Within-Segment Operational Efficiency**: **+1.9 pp (38%)**
   * **Between-Segment Portfolio Mix Shift**: **+3.1 pp (62%)**
2. **Simpson's Paradox**: Not observed in extreme inversion, but present in muted form: aggregate recovery increased while DPD 91-120 recovery deteriorated by -0.4 pp due to dialer neglect.
3. **Selection Bias**: Targeting model preferentially selected accounts with higher pre-existing bank balances and lower initial DPD.
4. **Survivorship Bias**: Written-off accounts were previously dropped from legacy denominator calculations, creating an artificial +3.2 pp visual boost.
5. **Attribution Window Stability**: 14-day lookback attributes 87.3% of recovery to outreach; a 7-day window reduces attribution to 72.1%, revealing that 15.2% of payments occur with prolonged lag.
