# Collections Performance Forensics: Independent Business Investigation & Capital Allocation

[![CI / Quality Checks](https://img.shields.io/badge/Unit%20Tests-21%2F21%20Passing-brightgreen)]()
[![DuckDB Version](https://img.shields.io/badge/DuckDB-v1.0+-blue)]()
[![Python Version](https://img.shields.io/badge/Python-3.11%20%7C%203.12-blue)]()
[![Implementation Status](https://img.shields.io/badge/Audit%20Status-Framework%20Verified%20%7C%20Awaiting%20Raw%20Data-orange)]()

---

## 1. Business Problem & Executive Background
Leadership of a major credit collections platform was presented with a business performance report claiming:
> **"Recovery has improved by 11% month-on-month."**

Executive leadership questioned the analytical validity of this claim. The mission of this project is to serve as an independent senior analytics architect, forensic data quality specialist, and econometrician to:
1. Reconstruct the platform's actual business performance across approximately 12 months using canonical, audited cash receipts.
2. Audit operational integrity across **17 collections source systems** and evaluate **7 forensic data risks**.
3. Decompose recovery trends across **13 business dimensions** and evaluate **7 statistical risks** (including Simpson's paradox, mix effects, and attribution window bias).
4. Establish an econometric counterfactual framework (Difference-in-Differences) to isolate the true causal impact of a mid-year borrower targeting strategy change.
5. Provide a mathematically reconciled, cash-flow-grounded capital allocation recommendation for deploying the platform's next **₹10 Crore**.

---

## 2. Analytical Integrity & Status Classification
In strict accordance with analytical integrity standards, this repository maintains a clear separation between:
* **[VERIFIED IMPLEMENTATION]**: The complete SQL analytical architecture (13 stages), Python transformation engines, econometric estimators, financial cash-flow models, Streamlit dashboard, and automated test suite (21/21 passing tests).
* **[EMPIRICAL STATUS: AWAITING REAL DATA]**: The `data/raw/` directory is currently unpopulated (0/17 source files supplied). Therefore, historical monthly rates, duplicate cash volumes, vendor RPC inflation percentages, and empirical targeting lifts are classified as **`AWAITING_REAL_DATA`** or **`NOT_VERIFIABLE`**. The platform does not present unverified benchmark values as historical company facts.
* **[ILLUSTRATIVE SCENARIOS]**: Where synthetic fixtures or benchmark formulas are used (e.g., verifying the Kitagawa mathematical identity or running financial sensitivity simulations), they are explicitly isolated, labeled as illustrative demonstrations, and tested independently.

### Investigation Questions & Executive Status

| Core Mission Question | Forensic Analytical Framework | Current Empirical Status |
|---|---|---|
| **1. What happened to recovery?** | Full monthly reconstruction engine in `src/metrics.py` and `sql/10_monthly_performance.sql` calculating opening exposure, canonical settled cash, recovery rate, relative MoM growth, percentage-point change, and duplicate amounts. | **NOT_VERIFIABLE**<br>*(Awaiting raw payment ledgers & account snapshots)* |
| **2. Why did it happen?** | Multi-factor deduplication (`sql/04_deduplication.sql`), 13-dimension decomposition (`sql/11_driver_analysis.sql`), and symmetric Kitagawa shift-share decomposition (`src/statistical_analysis.py`). | **AWAITING_REAL_DATA**<br>*(Framework fully verified; empirical vendor & mix impact pending raw data)* |
| **3. Is the 11% claim real?** | Independent claim audit comparing reported figures to canonical cohort recovery. Distinguishes relative growth from percentage-point change. | **NOT_VERIFIABLE**<br>*(Original calculation definition and raw source records unavailable)* |
| **4. Where should we invest ₹10 Cr?** | Reconciled cash-flow model evaluating all 6 choices across Base, Conservative, Upside, and Downside scenarios (`src/investment_model.py`). Proven legacy claim contradiction. | **RECOMMENDATION: OPTION 4 VIA ₹2.0 CR STAGED PILOT**<br>*(Gated rollout with 10% randomized holdout)* |

---

## 3. Technology Stack & Design Principles
* **Analytical Storage & SQL Engine**: Embedded [DuckDB](https://duckdb.org/) (zero external server dependencies, columnar vector execution, ACID transactions).
* **Data Manipulation & Scientific Computing**: `pandas`, `numpy`, `scipy`, `statsmodels`.
* **Causal Modeling & Econometrics**: Difference-in-Differences (DiD) with cluster-robust standard errors, symmetric Kitagawa Oaxaca-Blinder shift-share decomposition.
* **Executive Decision Dashboard**: [Streamlit](https://streamlit.io/) single-screen CEO briefing interface (read-only connection, graceful empty-state handling, isolated benchmark toggle).
* **Testing & Quality Assurance**: `pytest` automated suite with 21 unit tests covering all core invariants and mathematical formulas.
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
│   ├── 04_deduplication.sql                  # Multi-factor UTR, settlement, and replay deduplication
│   ├── 05_clean_models.sql                   # Normalized base tables with canonical timestamps
│   ├── 06_golden_dataset.sql                 # Analytical dimensions and canonical fact models
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
│   ├── deduplication.py                      # Multi-factor payment deduplication engine
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
    ├── test_investment_model.py              # Financial formula and legacy contradiction proof tests
    └── test_pipeline_idempotency.py          # Pipeline idempotency and empty-state handling tests
```

---

## 5. Data Requirements: All 17 Collections Source Systems
The pipeline is designed to ingest and validate 17 disparate upstream operational tables, defined in `config/source_inventory.yaml`:

| # | Source Entity | Primary Key / Grain | Expected Format | Critical Forensic Purpose |
|---|---|---|---|---|
| 1 | `borrowers` | `borrower_id` | CSV/Parquet | Demographic baseline, PII masking, crosswalks |
| 2 | `accounts` | `account_id` | CSV/Parquet | Opening balance, product category, DPD cohort |
| 3 | `agents` | `agent_id` | CSV/Parquet | Tenure, internal vs outsourced classification, vendor |
| 4 | `agent_sessions` | `session_id` | CSV/Parquet | Dialer login/logout, productive hours, idle time |
| 5 | `campaigns` | `campaign_id` | CSV/Parquet | Dialing strategy rules, operational wave targeting |
| 6 | `daily_targeting` | `target_id` / (account, date) | CSV/Parquet | Daily model scores, treatment vs control assignment |
| 7 | `calls` | `call_id` | CSV/Parquet | Telephony metadata, duration, call disposition |
| 8 | `call_attempts` | `attempt_id` | CSV/Parquet | Dialing attempt count, cadence, time of day |
| 9 | `call_dispositions` | `disposition_id` | CSV/Parquet | Canonical disposition mapping, Right-Party Contact (RPC) |
| 10 | `whatsapp_events` | `event_id` | CSV/Parquet | Delivery and read receipts for digital attribution |
| 11 | `sms_events` | `event_id` | CSV/Parquet | SMS delivery logs, payment link clicks |
| 12 | `field_visits` | `visit_id` | CSV/Parquet | Physical visit outcome, geographical coordinates |
| 13 | `promises_to_pay` | `ptp_id` | CSV/Parquet | Promise amount, target date, fulfillment status |
| 14 | `payments` | `payment_id` | CSV/Parquet | Bank UTR, settlement status, raw vs settled cash |
| 15 | `vendor_telephony` | `vendor_log_id` | CSV/Parquet | Vendor-reported RPCs for disposition gaming audit |
| 16 | `complaints` | `complaint_id` | CSV/Parquet | Harassment flags, RBI compliance breaches |
| 17 | `account_status_history` | `history_id` | CSV/Parquet | DPD migration, settlements, write-offs |

---

## 6. Execution Instructions

### Step 1: Environment Setup
Ensure Python 3.11 or 3.12 is installed.
```bash
git clone https://github.com/abbagonisunil/collections-performance-forensics.git
cd collections-performance-forensics
make setup
# Or: pip install -r requirements.txt
```

### Step 2: Source Profiling
Inspect raw files in `data/raw/` across all 17 sources:
```bash
make profile
```

### Step 3: Run the Complete Forensic Pipeline
```bash
make pipeline
# Or: python3 -m src.pipeline
```
Executes all 13 stages end-to-end: Schema Discovery $\rightarrow$ Profiling $\rightarrow$ Staging $\rightarrow$ Entity Resolution $\rightarrow$ Multi-Factor Deduplication $\rightarrow$ Clean Models $\rightarrow$ Golden Dimensions/Facts $\rightarrow$ Timestamp Normalization $\rightarrow$ Attribution Bridge $\rightarrow$ Audited Metrics $\rightarrow$ Driver Analysis $\rightarrow$ Counterfactual Modeling $\rightarrow$ Capital Allocation $\rightarrow$ Reconciliation.

### Step 4: Run Automated Tests
```bash
make test
# Or: pytest -v tests/
```
Executes all **21 automated tests** verifying schema discovery, deduplication rules, anti-fanout joins, rate bounds, Kitagawa mathematical identity, DiD unavailability/estimation, and financial cash-flow formulas.

### Step 5: Validate the Investigation Notebook
```bash
make notebook-check
```
Executes all 24 sections of `notebooks/01_collections_performance_investigation.ipynb` headlessly from top to bottom via `jupyter nbconvert`.

### Step 6: Launch the Executive Leadership Dashboard
```bash
make dashboard
# Or: streamlit run dashboard/app.py
```
Opens the interactive executive dashboard in your browser (`http://localhost:8501`), designed for a 60-second executive briefing with zero hardcoded company claims.

---

## 7. Forensic Methodologies

### 7.1 Multi-Factor Payment Deduplication Logic
Borrowers legitimately make multiple installment payments of identical amounts. Therefore, records are **never** excluded based solely on `(account_id, amount, timestamp)`. The deduplication engine (`sql/04_deduplication.sql`, `src/deduplication.py`) audits records using banking settlement evidence and classifies every record into:
1. `RETAINED_CANONICAL`: Verified bank settlement with unique transaction reference (UTR) or confirmed distinct installment.
2. `EXCLUDED_EXACT_DUPLICATE`: Identical payment event or replayed transaction reference.
3. `EXCLUDED_FAILED`: Payment transaction failed, declined, or timed out.
4. `EXCLUDED_REVERSED`: Settled payment subsequently reversed, charged back, or refunded.
5. `FLAGGED_UNRESOLVED`: Rapid succession payments lacking bank settlement proof, flagged for manual treasury reconciliation.
6. `OTHER_DOCUMENTED_DECISIONS`: Non-positive, zero, or null amounts quarantined.

### 7.2 Kitagawa Shift-Share Decomposition
To separate genuine operational collection efficiency from mechanical portfolio mix shifts:
$$\Delta R = \sum_{k} \bar{w}_k \Delta r_k + \sum_{k} \bar{r}_k \Delta w_k$$
where:
$$\bar{w}_k = \frac{w_{0k} + w_{1k}}{2}, \quad \bar{r}_k = \frac{r_{0k} + r_{1k}}{2}$$
* $\sum \bar{w}_k \Delta r_k$ = Within-Segment Operational Effect
* $\sum \bar{r}_k \Delta w_k$ = Between-Segment Mix Shift Effect
* The mathematical identity $\Delta R \equiv \text{Within Effect} + \text{Mix Effect}$ is guaranteed and verified via automated property-based testing.
* When analytical data is unpopulated, `calculate_mix_decomposition()` returns status `AWAITING_REAL_DATA` with `None` values rather than fixed benchmark figures.

### 7.3 Counterfactual Difference-in-Differences Engine
To rigorously evaluate the mid-year borrower targeting strategy change:
$$Y_{it} = \alpha + \beta_1 \text{Treated}_i + \beta_2 \text{Post}_t + \delta (\text{Treated}_i \times \text{Post}_t) + \mathbf{X}_{it}' \gamma + \varepsilon_{it}$$
* **Identification Rules**: Treatment defined by documented strategy exposure; control group established from unexposed comparable accounts; pre-treatment trends evaluated across multiple periods; standard errors clustered at the account level.
* **Failure Handling**: If control accounts cannot be established, reports `IDENTIFICATION_NOT_SUPPORTED`. If data is missing, reports `AWAITING_REAL_DATA`. The engine **never** silently falls back to fictional estimates.

### 7.4 Standardized Metric Definitions
Challenging legacy ambiguities, the metric engine (`src/metrics.py`) distinguishes:
* **Recovery Rate (%)**: $\frac{\text{Canonical Realized Cash}}{\text{Opening Eligible Exposure}} \times 100\%$
* **Relative MoM Growth (%)**: $\frac{\text{Rate}_t - \text{Rate}_{t-1}}{\text{Rate}_{t-1}} \times 100\%$
* **Percentage-Point Change (pp)**: $\text{Rate}_t - \text{Rate}_{t-1}$
* **Absolute Collection Growth (INR)**: $\text{Cash}_t - \text{Cash}_{t-1}$
* **Claim Verdict**: Standardized strictly as `SUPPORTED`, `CONTRADICTED`, or `NOT_VERIFIABLE`.

---

## 8. ₹10 Crore Investment Financial Model & Reconciled Decision

### Standard Financial Formulas
$$\text{Incremental Net Benefit} = \text{Gross Incremental Recovery} - \text{Total Incremental Cost}$$
$$\text{ROI (\%)} = \frac{\text{Incremental Net Benefit}}{\text{Total Incremental Cost}} \times 100\%$$
$$\text{Payback Period} = \text{Month where } \sum_{m=1}^{M} (\text{Incremental Cash Flow}_m) \ge 0$$

### Proof of Contradiction in Legacy Claims
1. A gross recovery of **₹4.00 Cr** against a **₹10.00 Cr** cost yields an Incremental Net Benefit of **-₹6.00 Cr (-60.0% ROI)**.
2. For a ₹10.0 Cr capital expenditure to produce **+₹2.75 Cr Net Benefit** (**+27.5% ROI**), Gross Incremental Recovery must reach **₹12.75 Cr** (a 5.10% lift across ₹250 Cr addressable exposure).

### Executive Recommendation: The ₹2.0 Crore Staged Pilot
Deploying ₹10.0 Cr upfront in an unvalidated model creates severe downside risk. We recommend structuring the investment as a **Two-Stage Gated Rollout**:
* **Stage 1 Commitment**: **₹2.00 Crore** (₹0.60 Cr Setup Capex + ₹1.40 Cr 6-Month Opex).
* **Target Cohort**: 50,000 delinquent accounts in DPD 31–90 (₹60.0 Cr addressable exposure).
* **Expected Pilot Recovery**: **₹2.10 Crore** (+3.5% lift on targeted sub-cohort).
* **Pilot Net Benefit**: **+₹0.10 Crore** (+5.0% ROI in Month 6; break-even in **5.7 months**).
* **Gated Expansion Rule**: Release the remaining **₹8.00 Crore** only if a 90-day randomized holdout A/B test confirms a statistically significant causal lift of $\ge 2.5\%$ ($p < 0.05$).

---

## 9. Known Limitations & Forensic Risks
1. **Survivorship Bias**: Accounts resolved early in the collections cycle exit the dialer queue, leaving harder-to-collect accounts over-represented in later months.
2. **Attribution-Window Censoring**: Fixed 7-day payment attribution windows may truncate lagged digital channel conversions (SMS/WhatsApp).
3. **Selection Bias**: Machine learning targeting models prioritize borrowers with high unobserved repayment propensity, requiring randomized holdouts to establish true causal lift.
4. **Data Availability**: Full empirical validation requires loading actual source extracts into `data/raw/`.

---

## 10. Data Privacy, Compliance & Security
* **PII Protection**: Borrower phone numbers, names, and PANs are hashed (`SHA-256`) during staging. No raw PII is exposed in analytical views.
* **RBI Calling Hours**: Built-in compliance checks audit dialer timestamps to flag call attempts outside the mandated 08:00–19:00 IST window.
* **Local Processing**: Analytical execution is powered entirely by embedded DuckDB. No collections data is transmitted to external cloud endpoints.
* **Audit Trail**: Every exclusion and deduplication decision is logged in immutable tables with reasons and timestamps.
