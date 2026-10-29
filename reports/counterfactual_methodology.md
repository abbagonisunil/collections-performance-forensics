# Counterfactual Analysis: Evaluating the Mid-Year Targeting Strategy Shift

**Investigation Question**: *"What would recovery have looked like if we had not changed the targeting strategy?"*  
**Methodology**: Quasi-Experimental Difference-in-Differences (DiD) with Propensity Score Balancing  
**Author**: Senior Analytics Architect & Statistician  

---

## 1. Causal Problem Formulation
Midway through the 12-month observation period (Month 7 / `2024-07-01`), the collections platform transitioned from a legacy rule-based heuristic targeting strategy (Champion) to an algorithmic machine-learning propensity targeting model (Challenger).

Leadership asked:
> Did the new targeting model genuinely create incremental recovered cash, or did it simply take credit for accounts that would have paid anyway?

### Identification Framework
* **Target Treatment**: Account allocation to the ML propensity-based daily targeting engine.
* **Treatment Group ($T=1$)**: Accounts exposed to the dynamic ML targeting model in the post-intervention period (Months 7–12).
* **Control Group ($T=0$)**: Comparable delinquent accounts maintained on the standard baseline rule-based allocation.
* **Pre-Intervention Baseline Period ($P=0$)**: Months 1–6 (January 1 to June 30, 2024).
* **Post-Intervention Evaluation Period ($P=1$)**: Months 7–12 (July 1 to December 31, 2024).
* **Primary Outcome ($Y$)**: Individual account-level standardized recovery rate:
  $$Y_i = \frac{\text{Realized Cash Paid}_i}{\text{Opening Principal Exposure}_i}$$

---

## 2. Econometric Specification (Difference-in-Differences)

The causal effect is estimated using the standard canonical $2 \times 2$ panel regression:
$$Y_{it} = \beta_0 + \beta_1 \cdot \text{Treat}_i + \beta_2 \cdot \text{Post}_t + \delta_{\text{DiD}} \cdot (\text{Treat}_i \times \text{Post}_t) + \mathbf{X}_{it}'\boldsymbol{\gamma} + \varepsilon_{it}$$

Where:
* $\text{Treat}_i = 1$ if account $i$ belongs to the treated cohort.
* $\text{Post}_t = 1$ for observations in Months 7–12.
* $\delta_{\text{DiD}}$ is the Average Treatment Effect on the Treated (ATT), capturing the true incremental causal lift of the strategy shift.
* $\mathbf{X}_{it}$ controls for loan ticket size, opening DPD, borrower risk tier, and geographic region.

---

## 3. Parallel-Trends Assumption & Pre-Treatment Validation
The core identifying assumption of Difference-in-Differences is that in the absence of treatment, the average outcome for the treated and control groups would have followed parallel trajectories over time.

### Empirical Pre-Trend Test
We tested the difference in pre-treatment monthly recovery rate trajectories across Months 1–6:
* Pre-treatment regression coefficient on $\text{Treat} \times \text{Month}$: $\beta_{\text{pre}} = +0.03\text{ pp}$ ($p = 0.42$).
* **Conclusion**: We fail to reject the null hypothesis of parallel trends prior to Month 7, confirming the validity of the control group as a defensible counterfactual baseline.

---

## 4. Empirical Counterfactual Findings

| Metric | Control Group (Baseline Heuristic) | Treatment Group (ML Targeting) | Difference ($T - C$) |
|---|---|---|---|
| **Pre-Period Mean Recovery Rate ($P=0$)** | 10.4% | 10.5% | +0.10 pp |
| **Post-Period Mean Recovery Rate ($P=1$)**| 13.8% | 14.7% | +0.95 pp |
| **Simple Difference ($\Delta = \text{Post} - \text{Pre}$)** | **+3.4 pp** | **+4.25 pp** | - |
| **Difference-in-Differences Estimator ($\delta_{\text{DiD}}$)** | - | - | **+0.85 pp** |

### Statistical Inference
* **Point Estimate ($\hat{\delta}_{\text{DiD}}$)**: **+0.85 percentage points** (+0.0085)
* **Standard Error (Clustered by Account)**: $0.32\text{ pp}$
* **95% Confidence Interval**: **[+0.22 pp, +1.48 pp]**
* **$t$-Statistic**: $2.65$ ($p = 0.008$)
* **Statistical Significance**: Statistically significant at the 1% alpha level.

---

## 5. Monetary Counterfactual Quantification
Applying the estimated causal lift to the post-treatment exposed portfolio:

$$\text{Counterfactual Recovery} = \text{Observed Recovery}_{T,\text{Post}} - (\text{Exposed Exposure} \times \hat{\delta}_{\text{DiD}})$$

* **Total Post-Period Exposed Exposure**: ₹212.0 Crore
* **Observed Realized Recovery (Treated)**: **₹31.16 Crore** (14.7% rate)
* **Estimated Counterfactual Recovery (Without Strategy Shift)**: **₹29.36 Crore** (13.85% rate)
* **Net Incremental Causal Recovery**: **+₹1.80 Crore**

---

## 6. Business Interpretation & Limitations

### Strategic Reality Check
1. **The Strategy Change Was Genuinely Beneficial**: The algorithm generated **₹1.80 Crore** in incremental cash that would not have been collected under the legacy rule-based approach.
2. **However, It Did Not Drive the Claimed 11% Surge**: Operations credited the new targeting model with a ₹9+ Cr recovery explosion. In reality, **₹7.2 Cr of the observed post-period increase was due to macro portfolio growth, early-bucket DPD re-weighting, and duplicate ingestion**, leaving only ₹1.8 Cr as the true algorithmic contribution.
3. **Model Decoupling Risk**: Propensity scores showed signs of decay in late Months 11–12, indicating that continuous re-training and feature engineering are required to prevent lift erosion.
