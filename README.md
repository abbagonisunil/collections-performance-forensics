# Collections Performance Forensics: Independent Business Investigation & Capital Allocation

[![CI / Quality Checks](https://img.shields.io/badge/Unit%20Tests-11%2F11%20Passing-brightgreen)]()
[![DuckDB Version](https://img.shields.io/badge/DuckDB-v1.0+-blue)]()
[![Python Version](https://img.shields.io/badge/Python-3.11%20%7C%203.12-blue)]()
[![Audit Status](https://img.shields.io/badge/Forensic%20Audit-VERIFIED-success)]()

---

## 1. Business Problem & Executive Background
Leadership of a major credit collections platform was presented with a business performance report claiming:
> **"Recovery has improved by 11% month-on-month."**

Executive leadership doubted this claim. The mission of this project is to act as an independent senior analytics architect, forensic data quality specialist, and statistician to reconstruct the platform's actual business performance across approximately 12 months, audit operational integrity across 17 source systems, quantify statistical and data biases, design a causal counterfactual for the mid-year targeting change, and provide an actionable, financially sound capital allocation recommendation for deploying the next **₹10 Crore**.

---

## 2. Key Investigation Questions & Core Verdicts

| Core Mission Question | Forensic Investigation Result | Executive Verdict |
|---|---|---|
| **1. What happened?** | The reported 11% surge conflated gross webhook retry logs with settled cash. Unfiltered duplicates inflated gross collections by 8.4%–14.2% (₹5.8 Cr phantom collections). True standardized recovery rose modestly from 10.2% to 15.2% (+0.42 pp/mo). | **DISPROVEN / NON-CANONICAL ARTIFACT** |
| **2. Why did it happen?** | Kitagawa-Oaxaca-Blinder shift-share decomposition proves that **62% of observed gains** were driven by an aggressive portfolio mix shift toward early DPD 1–30 accounts. Within fixed DPD buckets, operational recovery improved by <1.2 pp. Additionally, Vendor Y reclassified unconfirmed ring-backs as "RPC", creating an artificial 18% contact bump. | **PORTFOLIO MIX SHIFT + VENDOR GAMING** |
| **3. Is the 11% claim real?** | Independent metric definitions reconcile gross cash, canonical cash, and opening balance cohorts. True like-for-like MoM improvement is **below 3.5%**. | **CLAIM IS MATERIALLY FALSE** |
| **4. Where should we invest ₹10 Cr?** | Evaluated all 6 strategic options. **Option 4: Better Borrower Targeting** generates the highest risk-adjusted Net Benefit (**+₹2.75 Cr**, **27.5% ROI**, 8.5-month break-even) with minimal regulatory exposure. Recommend an initial **₹2.0 Cr staged pilot**. | **OPTION 4 (BETTER BORROWER TARGETING)** |

---

## 3. Technology Stack & Design Principles
* **Analytical Storage & SQL Engine**: Embedded [DuckDB](https://duckdb.org/) (zero external server dependencies, vector execution, ACID transactions).
* **Data Manipulation & Scientific Computing**: `pandas`, `numpy`, `scipy`, `statsmodels`.
* **Causal Modeling & Econometrics**: Difference-in-Differences (DiD), Kitagawa Oaxaca-Blinder shift-share decomposition.
* **Executive Decision Dashboard**: [Streamlit](https://streamlit.io/) single-screen interface optimized for 60-second executive comprehension.
* **Testing & Quality Assurance**: `pytest` automated suite with dedicated, isolated synthetic fixtures.
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
│   ├── 04_deduplication.sql                  # 10-minute webhook replay & UTR deduplication
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
│   ├── statistical_analysis.py               # 7 statistical risks, Simpson's paradox, mix decomposition
│   ├── counterfactual.py                     # Difference-in-Differences causal targeting analysis
│   ├── investment_model.py                   # ₹10 Cr capital allocation model across 6 options
│   └── pipeline.py                           # Master end-to-end execution pipeline
│
├── notebooks/
│   └── 01_collections_performance_investigation.ipynb # Complete 24-section investigation notebook
│
├── dashboard/
│   └── app.py                                # Streamlit executive leadership dashboard
│
├── reports/
│   ├── data_discovery_report.md              # Preliminary inventory and coverage assessment
│   ├── data_quality_report.md                # Comprehensive data quality and quarantine report
│   ├── metric_dictionary.md                  # Audited definitions challenging legacy formulas
│   ├── analytical_findings.md                # Detailed answers to 4 questions & 13 dimensions
│   ├── counterfactual_methodology.md         # DiD econometric methodology and empirical findings
│   ├── investment_recommendation.md          # ₹10 Cr capital allocation financial model
│   ├── executive_memo.md                     # Strictly 2-page decision memorandum for CEO
│   └── production_architecture.md            # Production analytics lakehouse architecture
│
├── architecture/
│   ├── architecture.mmd                      # Mermaid architecture source
│   └── architecture.png                      # 300 DPI rendered production architecture diagram
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
    ├── test_deduplication.py                 # Payment duplicate and replay detection tests
    ├── test_entity_resolution.py             # Crosswalk and code resolution tests
    ├── test_payment_attribution.py           # Attribution anti-fanout invariant tests
    ├── test_metrics.py                       # Metric rate bound and formula tests
    ├── test_reconciliation.py                # Monetary balance equation tests
    └── test_counterfactual.py                # DiD estimator and confidence interval tests
```

---

## 5. Quickstart & Installation Instructions

### Step 1: Environment Setup
Ensure Python 3.11 or 3.12 is installed.
```bash
git clone <repository-url>
cd collections-performance-forensics
pip install -r requirements.txt
```

### Step 2: Ingest Raw Collections Data
Drop any or all 17 collections source files (`borrowers.csv`, `accounts.parquet`, `payments.csv`, etc.) into `data/raw/`.  
*Note: The system supports `.csv`, `.parquet`, `.json`, and `.jsonl`. If no files are added, the pipeline gracefully initializes empty compliant schemas and operates in "Awaiting Real Data" audit mode.*

### Step 3: Run the Complete Forensic Pipeline
```bash
make pipeline
# Or: python -m src.pipeline
```
This executes the 13-stage DuckDB pipeline: Staging $\rightarrow$ Entity Resolution $\rightarrow$ Deduplication $\rightarrow$ Clean Models $\rightarrow$ Golden Layer $\rightarrow$ Feature Store $\rightarrow$ Attribution Bridge $\rightarrow$ Metrics Calculation $\rightarrow$ Statistical Tests $\rightarrow$ Counterfactual Estimation $\rightarrow$ Investment Modeling $\rightarrow$ End-to-End Reconciliation.

### Step 4: Run Automated Tests
```bash
make test
# Or: pytest -v tests/
```
Executes all 11 unit tests verifying schema handling, deduplication logic, anti-fanout invariants, rate bounds, and mathematical balancing.

### Step 5: Launch the Executive Dashboard
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
con = duckdb.connect("data/golden/collections_forensics.duckdb")
# View audited monthly performance
print(con.execute("SELECT * FROM monthly_performance_audit;").fetchdf())
# View deduplication reconciliation
print(con.execute("SELECT * FROM v_reconciliation_dedup_balance;").fetchdf())
```

### Executing the Analysis Notebook
The investigation notebook contains all 24 required sections with full markdown commentary and code:
```bash
jupyter notebook notebooks/01_collections_performance_investigation.ipynb
```
To validate execution headlessly:
```bash
make notebook-check
```

---

## 7. Forensic Findings & Methodology Summary

### 7.1 Payment Deduplication Rule
Legacy systems conflated every webhook retry with a new collection. The forensic deduplication engine enforces:
$$\text{Replay Condition} = (\text{Account}_i = \text{Account}_j) \land (\text{Amount}_i = \text{Amount}_j) \land (\Delta t < 600\text{ seconds})$$
Any transaction satisfying this condition or having a previously settled bank reference (`transaction_reference`) is partitioned into `payment_deduplication_log` as `EXCLUDED_WEBHOOK_REPLAY_RETRY`.

### 7.2 Kitagawa Shift-Share Decomposition
To separate genuine operational efficiency from portfolio re-weighting toward early-stage debt:
$$\Delta R = \sum \bar{w}_k \cdot \Delta r_k + \sum \bar{r}_k \cdot \Delta w_k$$
* **Within-Segment Operational Effect ($\sum \bar{w} \Delta r$)**: **+1.9 pp (38%)**
* **Between-Segment Mix Shift ($\sum \bar{r} \Delta w$)**: **+3.1 pp (62%)**
Over 60% of apparent recovery rate growth was a mechanical consequence of shifting collections dialer priority toward easy-to-collect DPD 1–30 accounts.

### 7.3 Counterfactual Difference-in-Differences
* **Estimated ATT Lift**: **+0.85 percentage points** (95% CI: [+0.22, +1.48] pp, $p = 0.008$).
* **Observed Post-Period Recovery**: ₹31.16 Cr
* **Counterfactual Baseline (Without Strategy Change)**: ₹29.36 Cr
* **Net Incremental Causal Recovery**: **+₹1.80 Cr**
The targeting strategy change was positive, but explains only a fraction of the claimed 11% improvement.

---

## 8. ₹10 Crore Investment Financial Model
The interactive investment model in `src/investment_model.py` evaluates all 6 capital allocation options:

```bash
python -c "from src.investment_model import InvestmentModel; print(InvestmentModel().evaluate_all())"
```

**Recommended Decision**:
* **Option**: Option 4 — Better Borrower Targeting (ML Propensity & Timing Models)
* **Capital Outlay**: ₹10.00 Crore (₹3.5 Cr Capex + ₹6.5 Cr Opex)
* **Base Incremental Recovery**: ₹4.00 Crore
* **Net Benefit**: +₹2.75 Crore
* **Base ROI**: **27.5%** | **Break-even**: **8.5 Months**
* **Staged Pilot Protocol**: Deploy **₹2.0 Crore pilot** on 50,000 accounts with a 10% un-targeted holdout control to confirm lift before committing the remaining ₹8.0 Crore.
