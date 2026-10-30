"""Executive Dashboard for Collections Performance Forensics.

Built with Streamlit for 60-second executive comprehension and leadership decision support.
Strictly adheres to data integrity: reads directly from DuckDB analytical views;
displays a transparent, professional empty state when source data is unpopulated;
isolates benchmark simulations behind an explicitly disabled-by-default methodology toggle.
"""

import sys
from pathlib import Path
from datetime import datetime
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Set project root
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.config import settings
from src.utils import get_db_connection, format_currency_inr, format_percentage
from src.metrics import MetricsEngine
from src.deduplication import DeduplicationEngine
from src.data_quality import DataQualityEngine
from src.statistical_analysis import StatisticalInvestigator
from src.counterfactual import CounterfactualAnalyzer
from src.investment_model import InvestmentModel
from src.ingestion import IngestionEngine

# Page configuration
st.set_page_config(
    page_title="Collections Forensics | Executive Brief",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Styling for sleek executive aesthetics
st.markdown("""
<style>
    .main { background-color: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }
    .kpi-card { background: white; border-radius: 8px; padding: 16px; border: 1px solid #e2e8f0; box-shadow: 0 1px 3px rgba(0,0,0,0.04); }
    .kpi-title { font-size: 0.75rem; font-weight: 600; text-transform: uppercase; color: #64748b; letter-spacing: 0.05em; margin-bottom: 4px; }
    .kpi-value { font-size: 1.55rem; font-weight: 700; color: #0f172a; margin-bottom: 2px; }
    .kpi-subtitle { font-size: 0.78rem; color: #64748b; }
    .claim-banner-alert { background-color: #fff1f2; border: 1px solid #fecdd3; border-radius: 8px; padding: 14px; margin-bottom: 16px; }
    .claim-banner-info { background-color: #f0f9ff; border: 1px solid #bae6fd; border-radius: 8px; padding: 14px; margin-bottom: 16px; }
    .empty-state-box { background-color: #f8fafc; border: 2px dashed #cbd5e1; border-radius: 8px; padding: 24px; text-align: center; margin: 12px 0; }
    .empty-state-title { font-size: 1.1rem; font-weight: 700; color: #334155; margin-bottom: 6px; }
    .empty-state-desc { font-size: 0.85rem; color: #64748b; max-width: 650px; margin: 0 auto; line-height: 1.4; }
    .status-badge { display: inline-block; padding: 4px 10px; border-radius: 12px; font-size: 0.75rem; font-weight: 600; }
</style>
""", unsafe_allow_html=True)


def load_db():
    """Connects to DuckDB in read-only mode for dashboard render."""
    return get_db_connection(read_only=True)


con = load_db()
ingestion_engine = IngestionEngine(con=con)
discovery = ingestion_engine.discover_raw_files()
available_sources = [k for k, v in discovery.items() if v["status"] == "AVAILABLE"]
has_raw_data = len(available_sources) > 0

# Check live monthly audit table
monthly_df = pd.DataFrame()
try:
    monthly_df = con.execute("SELECT * FROM monthly_performance_audit ORDER BY month_index;").fetchdf()
except Exception:
    pass

# Sidebar: Controls & Configuration
st.sidebar.title("Forensic Controls")
st.sidebar.markdown(f"**Storage Engine**: Embedded DuckDB (Read-Only)")
st.sidebar.markdown(f"**Sources Ingested**: `{len(available_sources)}/17` Available")

st.sidebar.markdown("---")
show_simulation = st.sidebar.checkbox(
    "Show Methodology Simulation (Simulated Example)",
    value=False,
    help="Displays an isolated illustrative Kitagawa shift-share scenario for methodology evaluation. Disabled by default."
)

st.sidebar.markdown("### Strategic Parameters")
selected_capital_cr = st.sidebar.slider("Capital Allocation Budget (₹ Cr)", min_value=5.0, max_value=25.0, value=10.0, step=1.0)
st.sidebar.caption("Pipeline runs headlessly via `make pipeline` or `python -m src.pipeline`.")


# ============================================================================
# SECTION A: HEADER
# ============================================================================
col_title, col_status = st.columns([3, 1])
with col_title:
    st.title("Collections Performance Forensics")
    st.caption(f"Independent Financial Investigation & ₹{selected_capital_cr:.0f} Cr Capital Allocation | Refreshed: {datetime.now().strftime('%Y-%m-%d %H:%M IST')}")

with col_status:
    if len(available_sources) == 17:
        st.markdown("""<div style='text-align: right;'><span class='status-badge' style='background-color:#dcfce7; color:#166534;'>🟢 FULL AUDIT DATA AVAILABLE</span></div>""", unsafe_allow_html=True)
    elif len(available_sources) > 0:
        st.markdown(f"""<div style='text-align: right;'><span class='status-badge' style='background-color:#fef3c7; color:#92400e;'>🟡 PARTIAL DATA ({len(available_sources)}/17)</span></div>""", unsafe_allow_html=True)
    else:
        st.markdown("""<div style='text-align: right;'><span class='status-badge' style='background-color:#e0e7ff; color:#3730a3;'>🔵 FRAMEWORK ACTIVE (AWAITING RAW DATA)</span></div>""", unsafe_allow_html=True)


# ============================================================================
# SECTION B: 60-SECOND EXECUTIVE KPI ROW
# ============================================================================
col1, col2, col3, col4, col5, col6 = st.columns(6)

if not monthly_df.empty:
    with col1:
        st.markdown(f"""<div class='kpi-card'><div class='kpi-title'>Realized Canonical Cash</div><div class='kpi-value'>{format_currency_inr(monthly_df['canonical_recovered_inr'].sum())}</div><div class='kpi-subtitle'>Audited settled payments</div></div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""<div class='kpi-card'><div class='kpi-title'>Recovery Rate</div><div class='kpi-value'>{monthly_df['canonical_recovery_rate_pct'].iloc[-1]:.1f}%</div><div class='kpi-subtitle'>Latest reporting period</div></div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""<div class='kpi-card'><div class='kpi-title'>MoM Rate Lift</div><div class='kpi-value'>{monthly_df['percentage_point_change'].mean():+.2f} pp</div><div class='kpi-subtitle'>Average monthly change</div></div>""", unsafe_allow_html=True)
    with col4:
        st.markdown(f"""<div class='kpi-card'><div class='kpi-title'>Eligible Population</div><div class='kpi-value'>{int(monthly_df['eligible_accounts'].iloc[-1]):,}</div><div class='kpi-subtitle'>Active debtor accounts</div></div>""", unsafe_allow_html=True)
    with col5:
        st.markdown(f"""<div class='kpi-card'><div class='kpi-title'>PTP Kept Rate</div><div class='kpi-value'>{monthly_df['ptp_kept_rate_pct'].mean():.1f}%</div><div class='kpi-subtitle'>Debtor promise integrity</div></div>""", unsafe_allow_html=True)
    with col6:
        st.markdown(f"""<div class='kpi-card'><div class='kpi-title'>Recovery / Agent-Hr</div><div class='kpi-value'>{format_currency_inr(monthly_df['recovery_per_agent_hour_inr'].mean())}</div><div class='kpi-subtitle'>Operational productivity</div></div>""", unsafe_allow_html=True)
else:
    # Defensible unpopulated state: no fabricated company numbers
    with col1:
        st.markdown("""<div class='kpi-card'><div class='kpi-title'>Realized Canonical Cash</div><div class='kpi-value'>Awaiting Data</div><div class='kpi-subtitle'>₹0.00 ingested</div></div>""", unsafe_allow_html=True)
    with col2:
        st.markdown("""<div class='kpi-card'><div class='kpi-title'>Recovery Rate</div><div class='kpi-value'>-- %</div><div class='kpi-subtitle'>Awaiting cohort exposure</div></div>""", unsafe_allow_html=True)
    with col3:
        st.markdown("""<div class='kpi-card'><div class='kpi-title'>MoM Rate Lift</div><div class='kpi-value'>-- pp</div><div class='kpi-subtitle'>Awaiting multi-period data</div></div>""", unsafe_allow_html=True)
    with col4:
        st.markdown("""<div class='kpi-card'><div class='kpi-title'>Eligible Population</div><div class='kpi-value'>0 Accounts</div><div class='kpi-subtitle'>data/raw/ unpopulated</div></div>""", unsafe_allow_html=True)
    with col5:
        st.markdown("""<div class='kpi-card'><div class='kpi-title'>PTP Kept Rate</div><div class='kpi-value'>-- %</div><div class='kpi-subtitle'>Awaiting promise logs</div></div>""", unsafe_allow_html=True)
    with col6:
        st.markdown("""<div class='kpi-card'><div class='kpi-title'>Recovery / Agent-Hr</div><div class='kpi-value'>--</div><div class='kpi-subtitle'>Awaiting session logs</div></div>""", unsafe_allow_html=True)


# ============================================================================
# SECTION C: 11% CLAIM INDEPENDENT AUDIT VERDICT
# ============================================================================
st.markdown("<br>", unsafe_allow_html=True)
metrics_engine = MetricsEngine(con=con)
claim_verdict = metrics_engine.evaluate_11_pct_claim()

verdict_val = claim_verdict.get("forensic_verdict", "NOT_VERIFIABLE")
if verdict_val == "SUPPORTED":
    banner_class = "claim-banner-info"
    verdict_color = "#166534"
elif verdict_val == "CONTRADICTED":
    banner_class = "claim-banner-alert"
    verdict_color = "#991b1b"
else:
    banner_class = "claim-banner-info"
    verdict_color = "#0369a1"

st.markdown(f"""
<div class='{banner_class}'>
    <div style='font-size: 1.05rem; font-weight: 700; color: {verdict_color};'>
        ⚖️ EXECUTIVE VERDICT ON THE "11% MONTH-ON-MONTH IMPROVEMENT" CLAIM: <u>{verdict_val}</u>
    </div>
    <div style='margin-top: 6px; font-size: 0.90rem; color: #334155;'>
        <strong>Audit Explanation</strong>: {claim_verdict.get('verdict_explanation')}
    </div>
    <div style='margin-top: 6px; font-size: 0.82rem; color: #64748b;'>
        <strong>Formula</strong>: <code>{claim_verdict.get('formula')}</code> &nbsp;|&nbsp;
        <strong>Evaluated Periods</strong>: <code>{claim_verdict.get('evaluated_months_count', 0)} months</code> &nbsp;|&nbsp;
        <strong>Canonical Recovered</strong>: <code>{format_currency_inr(claim_verdict.get('numerator_cash_recovered', 0.0))}</code> &nbsp;|&nbsp;
        <strong>Opening Exposure</strong>: <code>{format_currency_inr(claim_verdict.get('denominator_opening_exposure', 0.0))}</code>
    </div>
</div>
""", unsafe_allow_html=True)


# ============================================================================
# SECTION D: 12-MONTH MONTHLY PERFORMANCE & DRIVER ANALYSIS
# ============================================================================
col_chart, col_drivers = st.columns([3, 2])

with col_chart:
    st.subheader("Monthly Collections & Recovery Trajectory")
    if not monthly_df.empty:
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=monthly_df["month_index"], y=monthly_df["canonical_recovered_inr"] / 10000000,
            name="Canonical Recovered (₹ Cr)", marker_color="#0284c7"
        ))
        fig.add_trace(go.Scatter(
            x=monthly_df["month_index"], y=monthly_df["canonical_recovery_rate_pct"],
            name="Recovery Rate (%)", yaxis="y2", mode="lines+markers",
            line=dict(color="#e11d48", width=3)
        ))
        fig.update_layout(
            height=320, margin=dict(l=10, r=10, t=20, b=10),
            yaxis=dict(title="Realized Cash (₹ Cr)", gridcolor="#f1f5f9"),
            yaxis2=dict(title="Recovery Rate (%)", overlaying="y", side="right"),
            plot_bgcolor="white"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.markdown("""
        <div class='empty-state-box'>
            <div class='empty-state-title'>Awaiting Monthly Collections Records</div>
            <div class='empty-state-desc'>
                The 12-month trajectory chart requires account and payment records to be ingested into <code>data/raw/</code>.
                When raw collections tables are provided, this panel displays monthly realized canonical cash, recovery rates, and month-on-month changes.
            </div>
        </div>
        """, unsafe_allow_html=True)

with col_drivers:
    st.subheader("Strongest Supported Business Drivers")
    stat_investigator = StatisticalInvestigator(con=con)
    findings_df = stat_investigator.generate_findings_table()
    st.dataframe(
        findings_df[["Investigation Area", "Classification", "Confidence", "Limitation / Risk"]],
        use_container_width=True, hide_index=True, height=270
    )


# ============================================================================
# SECTION E: STRATEGIC CAPITAL ALLOCATION & INVESTMENT MODEL
# ============================================================================
st.markdown("<br>", unsafe_allow_html=True)
st.subheader(f"Strategic Capital Allocation: ₹{selected_capital_cr:.0f} Crore Investment Options")

inv_model = InvestmentModel(capital_cr=selected_capital_cr)
inv_df = inv_model.evaluate_all()
rec = inv_model.get_recommended_allocation()
pilot_specs = inv_model.get_staged_pilot_specs()

# Recommendation Banner
st.markdown(f"""
<div style='background-color: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 8px; padding: 14px; margin-bottom: 14px;'>
    <div style='font-size: 1.05rem; font-weight: 700; color: #166534;'>
        🎯 RECOMMENDED STRATEGY: <u>{rec['recommended_strategy']}</u>
    </div>
    <div style='margin-top: 4px; font-size: 0.88rem; color: #334155;'>
        <strong>Phase 1 Commitment</strong>: ₹{pilot_specs['total_cost_cr']:.1f} Cr over {pilot_specs['pilot_horizon_months']} months &nbsp;|&nbsp;
        <strong>Target Population</strong>: {pilot_specs['target_accounts']:,} high-propensity accounts (₹{pilot_specs['target_exposure_cr']:.0f} Cr exposure) &nbsp;|&nbsp;
        <strong>Expected Lift</strong>: +{pilot_specs['expected_lift_pct']:.2f}% &nbsp;|&nbsp;
        <strong>Incremental Recovery</strong>: ₹{pilot_specs['expected_gross_recovery_cr']:.2f} Cr &nbsp;|&nbsp;
        <strong>Net Benefit</strong>: +₹{pilot_specs['expected_net_benefit_cr']:.2f} Cr &nbsp;|&nbsp;
        <strong>Break-even</strong>: {pilot_specs['break_even_months']} months
    </div>
    <div style='margin-top: 4px; font-size: 0.82rem; color: #15803d;'>
        <strong>Stage-Gate Rule</strong>: {pilot_specs['stage_gate_criteria']}
    </div>
</div>
""", unsafe_allow_html=True)

# 6-Option Cash-Flow Model Matrix
st.dataframe(inv_df, use_container_width=True, hide_index=True)
st.caption("Cash-flow model calculates payback from cumulative monthly net cash flows (-Capex + sum(Gross Recovery - Opex)). Downside and Conservative scenarios reflect lower empirical lifts.")


# ============================================================================
# SECTION F: ISOLATED METHODOLOGY SIMULATION (DISABLED BY DEFAULT)
# ============================================================================
if show_simulation:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div style='background-color: #fffbeb; border: 1px solid #fde68a; border-radius: 8px; padding: 12px; margin-bottom: 12px;'>
        <div style='font-weight: 700; color: #92400e; font-size: 0.95rem;'>
            ⚠️ SIMULATED METHODOLOGY DEMONSTRATION (NOT REAL COMPANY DATA)
        </div>
        <div style='font-size: 0.85rem; color: #78350f;'>
            This section renders an illustrative example demonstrating the mathematical mechanics of symmetric Kitagawa shift-share decomposition
            and Difference-in-Differences counterfactual modeling. These figures are illustrative benchmarks, not historical company findings.
        </div>
    </div>
    """, unsafe_allow_html=True)

    sim_col1, sim_col2 = st.columns(2)
    with sim_col1:
        st.markdown("#### Symmetric Kitagawa Decomposition Mechanics")
        # Illustrative simulation arrays
        w0 = np.array([0.25, 0.30, 0.25, 0.20])
        w1 = np.array([0.45, 0.25, 0.18, 0.12])  # Shift to early bucket
        r0 = np.array([0.20, 0.10, 0.05, 0.02])
        r1 = np.array([0.219, 0.111, 0.057, 0.022])
        sim_decomp = StatisticalInvestigator.decompose_kitagawa(r0, r1, w0, w1)

        fig_sim = go.Figure(go.Bar(
            x=[sim_decomp["between_mix_shift_effect_pp"], sim_decomp["within_operational_effect_pp"], sim_decomp["total_change_pp"]],
            y=["Between Mix Shift", "Within Operational Lift", "Total Aggregate Change"],
            orientation="h",
            marker=dict(color=["#d97706", "#0284c7", "#0f172a"])
        ))
        fig_sim.update_layout(height=240, margin=dict(l=10, r=10, t=10, b=10), plot_bgcolor="white")
        st.plotly_chart(fig_sim, use_container_width=True)
        st.caption(f"Exact Identity Verified: {sim_decomp['within_operational_effect_pp']} pp (Within) + {sim_decomp['between_mix_shift_effect_pp']} pp (Between) = {sim_decomp['total_change_pp']} pp (Total)")

    with sim_col2:
        st.markdown("#### Counterfactual DiD Estimation Architecture")
        cf_analyzer = CounterfactualAnalyzer(con=con)
        cf_res = cf_analyzer.estimate_difference_in_differences()
        st.json({
            "analysis_status": cf_res.get("analysis_status"),
            "identification_strategy": cf_res.get("identification_strategy"),
            "treatment_definition": cf_res.get("treatment_definition"),
            "control_definition": cf_res.get("control_definition"),
            "assumptions": cf_res.get("assumptions")
        })


# ============================================================================
# SECTION G: DATA QUALITY & AUDIT DISCLOSURES
# ============================================================================
st.markdown("<br>", unsafe_allow_html=True)
with st.expander("🔍 Data Quality, 17-Source Readiness & Reconciliation Trail", expanded=False):
    tab1, tab2, tab3 = st.tabs(["17 Source Systems Inventory", "Payment Deduplication Audit", "Metric Dictionary"])

    with tab1:
        st.markdown("#### 17 Source Systems Readiness Checklist")
        src_rows = []
        for src_name, meta in discovery.items():
            f_size = meta.get("file_size_bytes", 0)
            src_rows.append({
                "Source System": src_name,
                "Expected Path": f"data/raw/{src_name}.csv",
                "Status": meta["status"],
                "File Size": f"{f_size / 1024:.1f} KB" if f_size > 0 else "0 KB",
                "Columns": meta.get("columns", "Standard schema defined")
            })
        st.dataframe(pd.DataFrame(src_rows), use_container_width=True, hide_index=True)

    with tab2:
        st.markdown("#### Deduplication Decision Enums & Monetary Reconciliation")
        dedup_engine = DeduplicationEngine(con=con)
        audit_df = dedup_engine.run_deduplication()
        if not audit_df.empty:
            st.dataframe(audit_df, use_container_width=True, hide_index=True)
        else:
            st.info("Payment deduplication log is active. Classification rules: RETAINED_CANONICAL, EXCLUDED_EXACT_DUPLICATE, EXCLUDED_FAILED, EXCLUDED_REVERSED, FLAGGED_UNRESOLVED, OTHER_DOCUMENTED_DECISIONS.")

    with tab3:
        st.markdown("#### Production Metric Dictionary")
        metrics_dict = settings.metrics.get("metrics", {})
        metric_rows = []
        for k, m in metrics_dict.items():
            metric_rows.append({
                "Metric Name": m.get("name"),
                "Formula / Definition": m.get("defensible_definition"),
                "Flaw in Naive Computation": m.get("legacy_definition")
            })
        st.dataframe(pd.DataFrame(metric_rows), use_container_width=True, hide_index=True)


# Close DuckDB connection so background test and pipeline runs do not encounter file lock contention
try:
    con.close()
except Exception:
    pass
