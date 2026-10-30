"""Unit tests for the ₹10 Crore capital allocation model and financial reconciliation."""

import pytest
from src.investment_model import InvestmentModel


def test_investment_model_financial_identities():
    """Verifies that Net Benefit = Gross Recovery - Total Cost, and ROI = Net Benefit / Total Cost."""
    model = InvestmentModel(capital_cr=10.0)
    df = model.evaluate_all()

    assert len(df) == 6, "Must evaluate all 6 investment options"

    for _, row in df.iterrows():
        cost = row["Total Cost (₹ Cr)"]
        gross = row["Base Incremental Recovery (₹ Cr)"]
        net = row["Base Net Benefit (₹ Cr)"]
        roi = row["Base ROI (%)"]

        # Mathematical Invariants:
        assert round(gross - cost, 2) == net, f"Net benefit violated for {row['Investment Option']}"
        assert round((net / cost) * 100.0, 1) == roi, f"ROI formula violated for {row['Investment Option']}"


def test_legacy_claim_contradiction_proof():
    """Verifies the mathematical proof that ₹4 Cr recovery, ₹2.75 Cr net benefit, and 27.5% ROI on ₹10 Cr are mutually contradictory."""
    model = InvestmentModel(capital_cr=10.0)
    recon = model.reconcile_legacy_claims()

    interp_a = recon["reconciliation"]["interpretation_a_conservative_10cr"]
    assert interp_a["total_cost_cr"] == 10.0
    assert interp_a["gross_recovery_cr"] == 4.0
    assert interp_a["net_benefit_cr"] == -6.0
    assert interp_a["roi_pct"] == -60.0

    interp_b = recon["reconciliation"]["interpretation_b_target_10cr"]
    assert interp_b["total_cost_cr"] == 10.0
    assert interp_b["gross_recovery_cr"] == 12.75
    assert interp_b["net_benefit_cr"] == 2.75
    assert interp_b["roi_pct"] == 27.5
    assert interp_b["required_lift_pct"] == 5.10


def test_staged_pilot_financial_specifications():
    """Verifies that the recommended ₹2.0 Cr staged pilot has defensible positive unit economics."""
    model = InvestmentModel(capital_cr=10.0)
    pilot = model.get_staged_pilot_specs()

    assert pilot["pilot_capital_cr"] == 2.0
    assert pilot["target_exposure_cr"] == 60.0
    assert pilot["expected_lift_rate"] == 0.035
    assert pilot["gross_incremental_recovery_cr"] == 2.10
    assert pilot["net_benefit_cr"] == 0.10
    assert pilot["roi_pct"] == 5.0
    assert pilot["pilot_break_even_months"] < 6.0


def test_cash_flow_payback_calculation():
    """Verifies that payback is derived from cumulative monthly net cash flows, not naive ratio division."""
    # Test case: Capex = 3.5 Cr, Annual Opex = 6.5 Cr, Gross Recovery = 4.0 Cr (Base scenario)
    # Since monthly recovery (0.36 Cr) < monthly opex (0.54 Cr), it never breaks even
    cf_loss = InvestmentModel.calculate_cash_flows(
        capex_inr=35_000_000,
        annual_opex_inr=65_000_000,
        annual_gross_recovery_inr=40_000_000,
        ramp_up_months=2,
        horizon_months=12
    )
    assert cf_loss["annual_net_benefit_inr"] == -60_000_000.0  # -₹6.0 Cr
    assert cf_loss["roi_pct"] == -60.0
    assert cf_loss["payback_months"] is None
    assert cf_loss["payback_str"] == "> 12 Months (No Year-1 Payback)"

    # Test case: Target scenario (Gross Recovery = 12.75 Cr)
    cf_target = InvestmentModel.calculate_cash_flows(
        capex_inr=35_000_000,
        annual_opex_inr=65_000_000,
        annual_gross_recovery_inr=127_500_000,
        ramp_up_months=2,
        horizon_months=12
    )
    assert cf_target["annual_net_benefit_inr"] == 27_500_000.0  # +₹2.75 Cr
    assert cf_target["roi_pct"] == 27.5
    assert cf_target["payback_months"] is not None
    assert 7.0 <= cf_target["payback_months"] <= 8.5


