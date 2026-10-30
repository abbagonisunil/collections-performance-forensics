# Collections Performance Forensics: Independent Business Investigation & Capital Allocation

[![CI / Quality Checks](https://img.shields.io/badge/Unit%20Tests-17%2F17%20Passing-brightgreen)]()
[![DuckDB Version](https://img.shields.io/badge/DuckDB-v1.0+-blue)]()
[![Python Version](https://img.shields.io/badge/Python-3.11%20%7C%203.12-blue)]()
[![Audit Status](https://img.shields.io/badge/Forensic%20Audit-VERIFIED-success)]()

---

## 1. Business Problem & Executive Background
Leadership of a major credit collections platform was presented with a business performance report claiming:
> **"Recovery has improved by 11% month-on-month."**

Executive leadership doubted this claim. The mission of this project is to act as an independent senior analytics architect, forensic data quality specialist, and statistician to reconstruct the platform's actual business performance across approximately 12 months, audit operational integrity across 17 source systems, quantify statistical and data biases, design a causal counterfactual for the mid-year targeting change, and provide an actionable, financially defensible capital allocation recommendation for deploying the next **₹10 Crore**.

---

## 2. Key Investigation Questions & Core Verdicts

| Core Mission Question | Forensic Investigation Result | Executive Verdict |
|---|---|---|
| **1. What happened?** | The reported 11% surge conflated gross webhook retry logs with settled cash. Unfiltered duplicate retries inflated naive collections by 8.4%–14.2%. On a standardized cohort basis, audited recovery rose from 10.2% to 15.2% (+0.42 pp/mo average trend, under 3.5% MoM relative growth). | **CLAIM IS DISPROVEN / NON-CANONICAL ARTIFACT** |
| **2. Why did it happen?** | Kitagawa shift-share decomposition proves that **62.0% of aggregate gains (+3.10 pp out of +5.00 pp)** were driven by dialer capacity shifting toward easy-to-collect DPD 1–30 debt. Within fixed non-early DPD cohorts, operational recovery was **below 1.2 pp** each. Telephony Vendor Y remapped unconfirmed ring-backs to "RPC", creating an artificial 18% contact jump without payment conversion. | **PORTFOLIO MIX SHIFT + VENDOR GAMING** |
| **3. Is the 11% claim real?** | Independent metric definitions reconcile gross cash, canonical cash, and opening balance cohorts. True like-for-like MoM improvement is **below 3.5%**. | **CLAIM IS MATERIALLY FALSE** |
| **4. Where should we invest ₹10 Cr?** | Evaluated all 6 options. Sinking ₹10 Cr upfront at baseline 1.6% lift yields **-₹6.0 Cr Net Benefit (-60% ROI)**. Achieving +27.5% ROI (+₹2.75 Cr Net Benefit) requires **₹12.75 Cr Gross Recovery** (5.10% lift). Prudent recommendation: Deploy an immediate **₹2.0 Cr Staged Pilot** for Option 4 with a 10% holdout control. | **OPTION 4 (VIA ₹2.0 CR STAGED PILOT)** |

---

## 3. Technology Stack & Design Principles
* **Analytical Storage & SQL Engine**: Embedded [DuckDB](https://duckdb.org/) (zero external server dependencies, vector execution, ACID transactions).
* **Data Manipulation & Scientific Computing**: `pandas`, `numpy`, `scipy`, `statsmodels`.
* **Causal Modeling & Econometrics**: Difference-in-Differences (DiD), Kitagawa Oaxaca-Blinder shift-share decomposition.
* **Executive Decision Dashboard**: [Streamlit](https://streamlit.io/) single-screen interface optimized for 60-second executive comprehension (connects to DuckDB in read-only mode).
* **Testing & Quality Assurance**: `pytest` automated suite with dedicated, isolated synthetic fixtures (17/17 tests passing).
* **Visualization**: `Plotly`, `Matplotlib`, `Seaborn`.

---

## 4. Repository Structure

```
collections-performance-forensics/
│
├── README.md                                 # Comprehensive project documentation
├── requirements.txt                          # Pinned dependency specifications
├── .gitignore                                # Excludes sensitive raw data, DBs, and credentials
├── .env.example                              # Environment configuration template
├── Makefile                                  # Standardized execution targets
│
├── config/
│   ├── settings.yaml                         # Global environment, timezone & threshold parameters
│   ├── source_inventory.yaml                 # Schemas & data contracts for all 17 sources
│   └── metric_definitions.yaml               # Audited metric dictionary challenging legacy definitions
│
├── data/
│   ├── raw/                                  # Immutable raw input files (CSV, Parquet, JSON)
│   ├── staging/                              # Normalized typed staging views
│   ├── clean/                                # Deduplicated records, resolved entities, and quarantine
│   ├── golden/                               # Analytical dimensions and canonical facts (DuckDB)
│   ├── features/                             # Account-level behavioral feature sets
│   └── README.md                             # Data storage guidelines and privacy policies
│
├── sql/
│   ├── 00_source_profiling.sql               # Profiling and metadata discovery queries
│   ├── 01_staging.sql                        # Schema normalization and type casting
│   ├── 02_data_quality.sql                   # Integrity assertions and quarantine views
│   ├── 03_entity_resolution.sql              # Crosswalks for borrowers, agents, and vendor codes
│   ├── 04_deduplication.sql                  # Bank UTR settlement & webhook replay deduplication
│   ├── 05_clean_models.sql                   # Normalized base tables with canonical timestamps
│   ├── 06_golden_dataset.sql                 # Dimensions and canonical fact models
│   ├── 07_payment_attribution.sql            # Omnichannel attribution bridge (4 models)
│   ├── 08_features.sql                       # Analytical feature engineering
│   ├── 09_metrics.sql                        # Audited operational metric views
│   ├── 10_monthly_performance.sql            # 12-Month reconstruction and 11% claim audit
│   ├── 11_driver_analysis.sql                # 13-Dimension forensic decomposition
│   └── 12_reconciliation.sql                # Monetary balancing and invariant assertions
│
├── src/
│   ├── __init__.py
│   ├── config.py                             # Settings and YAML schema loader
│   ├── utils.py                              # Database connections and INR currency formatting
│   ├── ingestion.py                          # Multi-format ingestion and discovery engine
│   ├── profiling.py                          # Automated source table profiler
│   ├── data_quality.py                       # DQ assertions and reliability scoring
│   ├── entity_resolution.py                  # Identity crosswalks and vendor code mapping
│   ├── deduplication.py                      # Forensic payment deduplication and overstatement audit
│   ├── timestamp_normalization.py            # UTC/IST conversion and RBI calling hours audit
│   ├── payment_attribution.py                # 4-model payment attribution bridge
│   ├── transformations.py                    # Analytical pipeline orchestrator
│   ├── metrics.py                            # Metric calculations and claim evaluator
│   ├── statistical_analysis.py               # 7 statistical risks, Simpson's paradox, Kitagawa decomposition
│   ├── counterfactual.py                     # Difference-in-Differences causal targeting analysis
│   ├── investment_model.py                   # Reconciled financial investment model across 6 options
│   ├── generate_notebook.py                  # Programmatic generator for the 24-section investigation notebook
│   └── pipeline.py                           # Master end-to-end execution pipeline
│
├── notebooks/
│   └── 01_collections_performance_investigation.ipynb # Complete 24-section investigation notebook
│
├── dashboard/
│   └── app.py                                # Streamlit executive leadership dashboard (60s CEO brief)
│
├── reports/
│   ├── data_discovery_report.md              # Preliminary inventory and coverage assessment
│   ├── data_quality_report.md                # Comprehensive data quality and quarantine report
│   ├── metric_dictionary.md                  # Audited definitions challenging legacy formulas
│   ├── analytical_findings.md                # Detailed answers to 4 questions & 13 dimensions
│   ├── counterfactual_methodology.md         # DiD econometric methodology and empirical findings
│   ├── investment_recommendation.md          # Reconciled ₹10 Cr financial model & staged pilot specs
│   ├── executive_memo.md                     # Strictly 2-page decision memorandum for CEO
│   └── production_architecture.md            # Production analytics lakehouse architecture
│
├── architecture/
│   ├── architecture.mmd                      # Mermaid architecture source
│   └── architecture.png                      # Rendered production architecture diagram
│
├── outputs/                                  # Reproducible CSV outputs and audit logs
│   ├── monthly_performance_reconstruction.csv
│   ├── forensic_investigation_summary.csv
│   ├── counterfactual_estimates.csv
│   ├── investment_model_scenarios.csv
│   └── reconciliation_monetary_trail.csv
│
└── tests/
    ├── conftest.py                           # Pytest fixtures and DuckDB test instances
    ├── fixtures/
    │   └── synthetic_fixtures.py             # Isolated mock data strictly for software testing
    ├── test_ingestion.py                     # Schema initialization and discovery tests
    ├── test_data_quality.py                  # DQ check and reliability score tests
    ├── test_deduplication.py                 # Payment duplicate, UTR, and replay detection tests
    ├── test_entity_resolution.py             # Crosswalk and code resolution tests
    ├── test_payment_attribution.py           # Attribution anti-fanout invariant tests
    ├── test_metrics.py                       # Metric rate bound and formula tests
    ├── test_reconciliation.py                # Monetary balance equation tests
    ├── test_counterfactual.py                # DiD estimator and confidence interval tests
    ├── test_statistical.py                   # Kitagawa mix decomposition mathematical identity tests
    └── test_investment_model.py              # Financial formula and legacy contradiction proof tests
```

---

## 5. Quickstart & Installation Instructions

### Step 1: Environment Setup
Ensure Python 3.11 or 3.12 is installed.
```bash
git clone https://github.com/abbagonisunil/collections-performance-forensics.git
cd collections-performance-forensics
pip install -r requirements.txt
```

### Step 2: Ingest Raw Collections Data
Drop any or all 17 collections source files (`borrowers.csv`, `accounts.parquet`, `payments.csv`, etc.) into `data/raw/`.  
*Note: The system supports `.csv`, `.parquet`, `.json`, and `.jsonl`. If no files are added, the pipeline gracefully initializes empty compliant schemas and operates in "Awaiting Real Data" audit mode with all 17 automated tests passing.*

### Step 3: Run the Complete Forensic Pipeline
```bash
make pipeline
# Or: python3 -m src.pipeline
```
Executes the 13-stage DuckDB pipeline: Staging $\rightarrow$ Source Profiling $\rightarrow$ Entity Resolution $\rightarrow$ Deduplication $\rightarrow$ Clean Models $\rightarrow$ Golden Layer $\rightarrow$ Feature Store $\rightarrow$ Timestamp Compliance $\rightarrow$ Attribution Bridge $\rightarrow$ Metrics Calculation $\rightarrow$ Statistical Tests $\rightarrow$ Counterfactual Estimation $\rightarrow$ Investment Modeling $\rightarrow$ End-to-End Reconciliation.

### Step 4: Run Automated Tests
```bash
make test
# Or: pytest -v tests/
```
Executes all 17 unit tests verifying schema handling, deduplication logic, anti-fanout invariants, rate bounds, mathematical balancing, Kitagawa decomposition identity, and financial formulas.

### Step 5: Validate the Investigation Notebook
```bash
make notebook-check
```
Executes all 24 sections of the investigation notebook headlessly from top to bottom.

### Step 6: Launch the Executive Dashboard
```bash
make dashboard
# Or: streamlit run dashboard/app.py
```
Opens the interactive executive dashboard in your browser (`http://localhost:8501`), designed for 60-second executive comprehension.

---

## 6. How to Run and Reproduce Key Artifacts

### Running SQL Queries Locally
All analytical logic is written in standard, clean DuckDB SQL:
```python
import duckdb
con = duckdb.connect("data/golden/collections_forensics.duckdb", read_only=True)
# View audited monthly performance
print(con.execute("SELECT * FROM monthly_performance_audit;").fetchdf())
# View deduplication reconciliation
print(con.execute("SELECT * FROM v_reconciliation_dedup_balance;").fetchdf())
```

---

## 7. Forensic Findings & Methodology Summary

### 7.1 Safe Payment Deduplication Architecture
Legacy systems blindly conflated webhook callbacks with new cash. The forensic deduplication engine enforces:
1. **Primary Evidence**: Stable bank transaction references (`transaction_reference` / UTR) and verified settlement timestamps (`settlement_timestamp`).
2. **Duplicate UTRs**: `EXCLUDED_EXACT_REF_DUPLICATE` partitions repeated ingestions of the same transaction reference.
3. **Legitimate Installments**: Same account and amount within 600 seconds WITH a distinct settled bank UTR are retained as `RETAINED_DISTINCT_REFERENCE`.
4. **Webhook Retries**: Rapid transactions lacking distinct bank references or settlement proof are partitioned into `payment_deduplication_log` as `EXCLUDED_WEBHOOK_REPLAY_RETRY` or `FLAGGED_CANDIDATE_RETRY_UNRESOLVED`.
5. **Reversals & Failures**: `EXCLUDED_REVERSAL_OR_FAILED` isolates reversals, chargebacks, and failed statuses.

### 7.2 Kitagawa Shift-Share Decomposition (Verified Mathematical Proof)
To isolate genuine operational efficiency from mechanical portfolio re-weighting:
$$\Delta R = \sum \bar{w}_k \cdot \Delta r_k + \sum \bar{r}_k \cdot \Delta w_k$$
where $\bar{w}_k = 0.5(w_{1,k} + w_{0,k})$ and $\bar{r}_k = 0.5(r_{1,k} + r_{0,k})$.

* **Period 0 (Pre) Rate ($R_0$)**: **10.20%** | **Period 1 (Post) Rate ($R_1$)**: **15.20%**
* **Total Observed Change ($\Delta R$)**: **+5.00 percentage points**
* **Within-Segment Operational Effect ($\sum \bar{w}_k \Delta r_k$)**: **+1.90 percentage points (38.0%)**
* **Between-Segment Mix Shift ($\sum \bar{r}_k \Delta w_k$)**: **+3.10 percentage points (62.0%)**
* **Exact Mathematical Identity**: $1.90\text{ pp} + 3.10\text{ pp} \equiv \mathbf{5.00\text{ percentage points}}$ (Sum Check Verified).

**Cohort Breakdown**:
Within fixed non-early DPD cohorts, operational rate improvement was **below 1.2 pp** each (DPD 31–60: +1.1 pp; DPD 61–90: +0.7 pp; DPD 90+: +0.2 pp). Over 62% of the aggregate 5.0 pp gain was a mechanical consequence of shifting collections dialer priority toward easy-to-collect DPD 1–30 accounts.

### 7.3 Counterfactual Difference-in-Differences
* **Econometric Model**: Panel DiD comparing treated accounts exposed to algorithmic targeting against comparable baseline control accounts.
* **Estimated ATT Lift**: **+0.85 percentage points** (95% CI: [+0.22, +1.48] pp, $p = 0.008$).
* **Observed Post-Period Recovery**: ₹31.16 Cr
* **Counterfactual Baseline (Without Strategy Change)**: ₹29.36 Cr
* **Net Incremental Causal Recovery**: **+₹1.80 Cr**  
The targeting strategy change was positive, but explains only a fraction of the claimed 11% improvement.

---

## 8. ₹10 Crore Investment Financial Model & Reconciled Decision

### Standard Financial Formulas
$$\text{Incremental Net Benefit} = \text{Gross Incremental Recovery} - \text{Total Cost}$$
$$\text{ROI (\%)} = \frac{\text{Incremental Net Benefit}}{\text{Total Cost}} \times 100\%$$

### Proof of Contradiction in Legacy Claims
1. Gross recovery of **₹4.00 Cr** on a **₹10.00 Cr** cost yields a Net Benefit of **-₹6.00 Cr (-60.0% ROI)**.
2. For a ₹10.0 Cr capital allocation to generate **+₹2.75 Cr Net Benefit** (**+27.5% ROI**), Gross Recovery must reach **₹12.75 Cr** (a **5.10% recovery lift** across ₹250 Cr addressable exposure).

### Executive Recommendation: The ₹2.0 Crore Staged Pilot
Deploying ₹10.0 Cr upfront risks sinking capital into an unproven model. We recommend structuring the investment as a **Two-Stage Gate-Review Deployment**:

* **Pilot Capital Commitment**: **₹2.00 Crore** (₹0.75 Cr Setup Capex + ₹1.25 Cr 6-Month Opex).
* **Target Cohort**: 50,000 delinquent accounts in DPD 31–90 (₹60.0 Cr addressable exposure).
* **Expected Pilot Recovery**: **₹2.10 Crore** (+3.5% lift on targeted sub-cohort).
* **Pilot Net Benefit**: **+₹0.10 Crore** (+5.0% ROI in Month 6; break-even in **5.7 months**).
* **Stage 2 Expansion Gating Rule**: Release the remaining **₹8.00 Crore** only if the 90-day randomized holdout A/B test confirms a statistically significant causal lift of $\ge 2.5\%$ ($p < 0.05$). Full-scale expansion targets ₹11.4 Cr gross recovery (+₹3.4 Cr Net Benefit, full-scale break-even at 8.5 months).
