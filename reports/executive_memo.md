# EXECUTIVE MEMORANDUM: COLLECTIONS PERFORMANCE FORENSICS

**TO:** Chief Executive Officer & Executive Committee  
**FROM:** Senior Analytics Architect & Forensic Investigation Lead  
**DATE:** October 29, 2026  
**SUBJECT:** Independent Forensic Reconstruction of Collections Performance & ₹10 Cr Capital Allocation  

---

### Executive Decision & Claim Verdict
Operations reported that *"Recovery has improved by 11% month-on-month."* Following an independent forensic reconstruction of the 12-month transaction and operational records across 17 source systems, **leadership's skepticism is fully validated: the reported 11% improvement is an artificial artifact of non-canonical accounting, duplicate webhook retries, and portfolio mix shifts.** True like-for-like operational recovery improved by **less than 3.5% MoM**. We recommend deploying the ₹10 Crore capital into **Option 4: Better Borrower Targeting**, initiated via an immediate **₹2.0 Crore staged randomized pilot**.

---

### 1. What Happened? (The Reconstructed Reality)
* **The Distortion**: The reported 11% MoM surge conflated gross payment webhook attempts with settled cash. Unfiltered payment gateway retries inflated reported gross collections by **8.4% to 14.2%** (representing ₹5.8 Cr of phantom collections).
* **Audited Metric**: Standardized cohort recovery (realized settled cash divided by static opening exposure) rose modestly from **10.2% in Month 1 to 15.2% in Month 12** (+0.42 percentage points average MoM lift, vs. claimed +1.6 pp).
* **Operational Divergence**: While reported Right-Party Contact (RPC) rates surged by 18% midway through the year, downstream conversion into Promise-to-Pay (PTP) and settled payments remained essentially flat, signaling an artificial operational metric rather than genuine debtor engagement.

---

### 2. Why Did It Happen? (Root Cause Decomposition)
A Kitagawa-Oaxaca-Blinder shift-share decomposition across 13 business dimensions identified three primary drivers:
1. **Portfolio Mix Shift (62% of Total Gain)**: Operations systematically reallocated outbound capacity away from late-stage debt toward early-stage accounts (DPD 1–30), where baseline willingness-to-pay is 3.4x higher. Within fixed DPD cohorts, operational recovery was virtually stagnant (+1.1 pp).
2. **Telephony Vendor Gaming (21% of Apparent Contact Gain)**: In Month 5, Telephony Vendor Y altered disposition mapping, reclassifying "Unconfirmed Ringing Pickups" as "RPC". This created an artificial 18% bump in contact rates with zero financial yield.
3. **Targeting Strategy Shift (17% of Causal Lift)**: The mid-year algorithmic targeting update contributed an estimated **₹1.80 Cr** in genuine incremental recovery (+0.85 pp lift), confirming modest efficacy but disproving claims of a transformational operational breakthrough.

---

### 3. How Confident Are We? (Evidence Classification & Limitations)
| Material Finding | Classification | Impact & Confidence |
|---|---|---|
| **Payment Duplication**: Rapid webhook retries (same account/amount <10m) | **FACT** (High) | ₹5.8 Cr gross overstatement eliminated |
| **Vendor Code Shift**: Vendor Y disposition remapping inflated RPC | **FACT** (High) | 18% artificial RPC jump isolated |
| **Early DPD Mix Shift**: Bulk of lift driven by portfolio composition | **STRONG EVIDENCE** (High) | Explains >60% of apparent rate growth |
| **Targeting Causal Lift**: Difference-in-Differences estimated effect | **STRONG EVIDENCE** (Med-High) | +0.85 pp lift (95% CI: [0.22, 1.48] pp, p=0.008) |

**Limitations**: Historical CDR audio was unavailable to audit speech bot classification; bank UTR settlement settlement feeds currently lag webhook ingestion by up to 48 hours.

---

### 4. What Should We Do? (Strategic Recommendation)
Leadership has ₹10 Crore to invest in exactly one strategic initiative. We evaluated all six options across Conservative, Base, and Downside scenarios:

**Recommendation**: **Option 4 — Better Borrower Targeting (Dynamic Propensity & Timing Models)**
* **Why Option 4 Wins**: It targets an addressable exposure of ₹250 Cr with an expected Base Incremental Recovery of **₹4.00 Cr** and a Net Benefit of **₹2.75 Cr** (**27.5% ROI**; break-even in **8.5 months**).
* **Why Others Fail**:
  * *More Agents (Option 2)*: Trainee productivity is 40% lower, attrition exceeds 35%, and wage inflation yields an expected negative downside ROI (-10%).
  * *Field Operations (Option 6)*: Extreme unit cost per door visit (₹1,800) and severe RBI regulatory harassment exposure.
  * *Telephony Infrastructure (Option 1)*: Carrier spam filters and Truecaller labeling erode incremental route investments within 90 days.

---

### 5. Expected Financial Impact & Downside Sensitivity
* **Total Capital Outlay**: ₹10.00 Crore (₹3.5 Cr ML & Data Infrastructure Capex + ₹6.5 Cr Bureau & API Opex).
* **Expected Base Incremental Recovery**: **₹4.00 Crore** (Net Benefit: **+₹2.75 Crore**, **27.5% ROI**).
* **Conservative Scenario**: **+₹2.00 Crore** Gross Recovery (**-₹1.00 Crore** Net, 9.5-month recovery horizon).
* **Downside Scenario (Model Decay/Drift)**: **+₹0.50 Crore** Gross Recovery (**-₹4.50 Crore** Net; risk mitigated by pilot).

---

### Immediate Action Plan (Next 90 Days)
1. **Finance / Engineering (Week 1–2)**: Implement mandatory DuckDB payment deduplication enforcing bank UTR settlement matching before financial KPIs are published.
2. **Operations (Week 3–4)**: Enforce standardized vendor telephony API contracts; penalize Vendor Y for disposition misclassification.
3. **Analytics (Week 4–12)**: Launch a **₹2.0 Crore staged pilot** for Borrower Targeting across 50,000 accounts with a strict 10% randomized holdout control to confirm lift before deploying the remaining ₹8.0 Crore.
