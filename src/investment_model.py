"""Financial investment evaluation model for ₹10 Crore capital allocation across 6 strategic options.

Implements rigorous corporate finance cash-flow modeling:
- Gross Incremental Recovery = Addressable Exposure * Lift Rate
- Incremental Net Benefit = Gross Incremental Recovery - Total Investment Cost
- ROI (%) = (Incremental Net Benefit / Total Investment Cost) * 100
- Payback Period = Exact month where cumulative monthly net cash flow (Gross Recovery - Opex - Capex) becomes non-negative
- Scenario Analysis: Conservative, Base, Upside, Downside
- Proof of legacy claim contradictions
- Risk-hedged Staged Pilot allocation (₹2.0 Cr commitment)
"""

from typing import Dict, Any, List, Optional
import pandas as pd
from src.config import settings
from src.utils import logger


class InvestmentModel:
    """Configurable financial model evaluating ROI, Net Benefit, cash flows, payback, and pilot gating."""

    def __init__(self, capital_cr: float = 10.0):
        self.capital_cr = capital_cr
        self.capital_inr = capital_cr * 10_000_000  # ₹10 Crore in INR
        self.horizon_months = 12

    @staticmethod
    def calculate_cash_flows(
        capex_inr: float,
        annual_opex_inr: float,
        annual_gross_recovery_inr: float,
        ramp_up_months: int = 2,
        horizon_months: int = 12
    ) -> Dict[str, Any]:
        """Calculates monthly cash flows, cumulative net cash flow, and exact payback month.
        
        Initial Outlay (Capex): Incurred at month 0.
        Monthly Operating Cost: annual_opex_inr / 12.0.
        Monthly Gross Recovery: adjusted for operational ramp-up fraction.
        Monthly Net Cash Flow = Monthly Gross Recovery - Monthly Operating Cost.
        Cumulative Net Cash Flow = -Capex + sum(Monthly Net Cash Flow).
        Payback Period = Month where cumulative net cash flow turns non-negative.
        """
        monthly_opex = annual_opex_inr / float(horizon_months)

        # Operational ramp-up fractions: linear ramp during initial months, 1.0 thereafter
        ramp_weights = []
        for m in range(1, horizon_months + 1):
            if m <= ramp_up_months:
                ramp_weights.append(m / (ramp_up_months + 1.0))
            else:
                ramp_weights.append(1.0)

        sum_weights = sum(ramp_weights)
        monthly_gross_recovery = [annual_gross_recovery_inr * (w / sum_weights) for w in ramp_weights]
        monthly_net_cash_flow = [rev - monthly_opex for rev in monthly_gross_recovery]

        cum_net = -capex_inr
        cum_cash_flows = []
        payback_month: Optional[float] = None

        for m, ncf in enumerate(monthly_net_cash_flow, start=1):
            prev_cum = cum_net
            cum_net += ncf
            cum_cash_flows.append(round(cum_net, 2))

            if cum_net >= 0 and payback_month is None:
                if ncf > 0:
                    fraction = (-prev_cum) / ncf
                    payback_month = round((m - 1) + fraction, 1)
                else:
                    payback_month = float(m)

        total_net_benefit = cum_net  # at month 12
        total_cost = capex_inr + annual_opex_inr
        roi_pct = (total_net_benefit / total_cost) * 100.0 if total_cost > 0 else 0.0

        return {
            "capex_inr": capex_inr,
            "annual_opex_inr": annual_opex_inr,
            "total_cost_inr": total_cost,
            "annual_gross_recovery_inr": annual_gross_recovery_inr,
            "annual_net_benefit_inr": round(total_net_benefit, 2),
            "roi_pct": round(roi_pct, 2),
            "monthly_net_cash_flow": [round(x, 2) for x in monthly_net_cash_flow],
            "cumulative_net_cash_flow": cum_cash_flows,
            "payback_months": payback_month,
            "payback_str": f"{payback_month:.1f} Months" if payback_month is not None else "> 12 Months (No Year-1 Payback)"
        }

    def get_investment_options_specs(self) -> List[Dict[str, Any]]:
        """Defines the 6 strategic options with cost structures and multi-scenario lift parameters."""
        return [
            {
                "id": "better_targeting",
                "name": "Option 4: Better Borrower Targeting",
                "addressable_accounts": 150_000,
                "addressable_exposure_cr": 250.0,
                "capex_inr": 35_000_000,        # ₹3.5 Cr software / ML infra / vendor bureau data
                "annual_opex_inr": 65_000_000,   # ₹6.5 Cr model ops, bureau scores, data APIs
                "total_cost_inr": 100_000_000,   # ₹10.0 Cr
                "ramp_up_months": 2,
                # Scenario Lifts (on addressable exposure)
                "base_lift_rate": 0.016,         # +1.6% lift -> ₹4.0 Cr Gross (Conservative baseline)
                "target_roi_lift_rate": 0.051,   # +5.1% lift -> ₹12.75 Cr Gross (+₹2.75 Cr Net, 27.5% ROI)
                "conservative_lift_rate": 0.008, # +0.8% lift -> ₹2.0 Cr Gross
                "upside_lift_rate": 0.060,       # +6.0% lift -> ₹15.0 Cr Gross
                "downside_lift_rate": 0.002,     # +0.2% lift -> ₹0.5 Cr Gross
                "compliance_risk": "Low (RBI compliant algorithmic scoring, no consumer harassment)",
                "operational_risk": "Model drift, score decay, data pipeline latency",
                "evidence_strength": "High (Supported by DiD targeting test & behavioral scoring)"
            },
            {
                "id": "whatsapp_digital",
                "name": "Option 5: WhatsApp / Digital Engagement",
                "addressable_accounts": 180_000,
                "addressable_exposure_cr": 180.0,
                "capex_inr": 20_000_000,        # ₹2.0 Cr chatbot, integration
                "annual_opex_inr": 80_000_000,   # ₹8.0 Cr Meta conversation fees, payment gateway
                "total_cost_inr": 100_000_000,
                "ramp_up_months": 1,
                "base_lift_rate": 0.014,         # +1.4% lift -> ₹2.52 Cr Gross
                "target_roi_lift_rate": 0.0708,  # +7.08% lift needed for 27.5% ROI
                "conservative_lift_rate": 0.007,
                "upside_lift_rate": 0.025,
                "downside_lift_rate": 0.003,
                "compliance_risk": "Medium (Customer spam opt-outs, template approvals)",
                "operational_risk": "Account blocking by Meta, click dropoffs",
                "evidence_strength": "High (High digital penetration observed)"
            },
            {
                "id": "telephony_infra",
                "name": "Option 1: Better Telephony Infrastructure",
                "addressable_accounts": 200_000,
                "addressable_exposure_cr": 220.0,
                "capex_inr": 25_000_000,        # ₹2.5 Cr carrier SBCs, dynamic CLI dialer
                "annual_opex_inr": 75_000_000,   # ₹7.5 Cr PRI lines, multi-vendor carrier SIPs
                "total_cost_inr": 100_000_000,
                "ramp_up_months": 2,
                "base_lift_rate": 0.009,         # +0.9% lift -> ₹1.98 Cr Gross
                "target_roi_lift_rate": 0.058,
                "conservative_lift_rate": 0.004,
                "upside_lift_rate": 0.018,
                "downside_lift_rate": 0.002,
                "compliance_risk": "Low (TRAI / DND regulatory adherence)",
                "operational_risk": "Spam flagging of numbers by Truecaller/carriers",
                "evidence_strength": "Medium-High (Solves known connection drop problem)"
            },
            {
                "id": "ai_voice",
                "name": "Option 3: AI Voice Automation",
                "addressable_accounts": 140_000,
                "addressable_exposure_cr": 160.0,
                "capex_inr": 40_000_000,        # ₹4.0 Cr conversational LLM / TTS license
                "annual_opex_inr": 60_000_000,   # ₹6.0 Cr telephony minutes & compute
                "total_cost_inr": 100_000_000,
                "ramp_up_months": 4,
                "base_lift_rate": 0.012,         # +1.2% lift -> ₹1.92 Cr Gross
                "target_roi_lift_rate": 0.0797,
                "conservative_lift_rate": 0.005,
                "upside_lift_rate": 0.022,
                "downside_lift_rate": 0.001,
                "compliance_risk": "High (Customer consent, hallucination risk, accent barrier)",
                "operational_risk": "Low containment rate, high transfer to human agents",
                "evidence_strength": "Medium (Unproven at scale across regional languages)"
            },
            {
                "id": "field_operations",
                "name": "Option 6: Field Operations",
                "addressable_accounts": 40_000,
                "addressable_exposure_cr": 90.0,
                "capex_inr": 10_000_000,        # ₹1.0 Cr mobile devices, GPS verification
                "annual_opex_inr": 90_000_000,   # ₹9.0 Cr travel, field collection agencies
                "total_cost_inr": 100_000_000,
                "ramp_up_months": 3,
                "base_lift_rate": 0.015,         # +1.5% lift -> ₹1.35 Cr Gross
                "target_roi_lift_rate": 0.1417,
                "conservative_lift_rate": 0.006,
                "upside_lift_rate": 0.025,
                "downside_lift_rate": 0.001,
                "compliance_risk": "Critical (Strict RBI guidelines on home visits & harassment)",
                "operational_risk": "Cash embezzlement, officer safety, fake visits",
                "evidence_strength": "Medium (High PTP kept rate but very high unit cost)"
            },
            {
                "id": "more_agents",
                "name": "Option 2: More Collection Agents",
                "addressable_accounts": 90_000,
                "addressable_exposure_cr": 150.0,
                "capex_inr": 15_000_000,        # ₹1.5 Cr workstation, onboarding, seats
                "annual_opex_inr": 85_000_000,   # ₹8.5 Cr salaries (150 agents @ ₹45k/mo)
                "total_cost_inr": 100_000_000,
                "ramp_up_months": 3,
                "base_lift_rate": 0.008,         # +0.8% lift -> ₹1.20 Cr Gross
                "target_roi_lift_rate": 0.085,
                "conservative_lift_rate": 0.003,
                "upside_lift_rate": 0.015,
                "downside_lift_rate": -0.001,
                "compliance_risk": "High (Agent conduct, call harassment, script deviations)",
                "operational_risk": "High agent attrition (35%+), training overhead",
                "evidence_strength": "Low (Data shows Trainees have 40% lower RPC/hour)"
            }
        ]

    def evaluate_all(self) -> pd.DataFrame:
        """Evaluates all 6 options using cumulative cash-flow payback and ROI modeling."""
        specs = self.get_investment_options_specs()
        rows = []

        for s in specs:
            exposure_inr = s["addressable_exposure_cr"] * 10_000_000
            total_cost = s["total_cost_inr"]
            capex = s["capex_inr"]
            opex = s["annual_opex_inr"]
            ramp = s["ramp_up_months"]

            # Compute scenarios using cash-flow engine
            gross_base = exposure_inr * s["base_lift_rate"]
            cf_base = self.calculate_cash_flows(capex, opex, gross_base, ramp)

            gross_target = exposure_inr * s.get("target_roi_lift_rate", s["base_lift_rate"])
            cf_target = self.calculate_cash_flows(capex, opex, gross_target, ramp)

            gross_cons = exposure_inr * s["conservative_lift_rate"]
            cf_cons = self.calculate_cash_flows(capex, opex, gross_cons, ramp)

            gross_down = exposure_inr * s["downside_lift_rate"]
            cf_down = self.calculate_cash_flows(capex, opex, gross_down, ramp)

            rows.append({
                "Investment Option": s["name"],
                "Total Cost (₹ Cr)": round(total_cost / 10_000_000, 1),
                "Addressable Exposure (₹ Cr)": s["addressable_exposure_cr"],
                "Base Incremental Recovery (₹ Cr)": round(gross_base / 10_000_000, 2),
                "Base Net Benefit (₹ Cr)": round(cf_base["annual_net_benefit_inr"] / 10_000_000, 2),
                "Base ROI (%)": cf_base["roi_pct"],
                "Base Payback": cf_base["payback_str"],
                "Target Lift for +27.5% ROI (%)": round(s.get("target_roi_lift_rate", 0.0) * 100.0, 2),
                "Target Recovery (₹ Cr)": round(gross_target / 10_000_000, 2),
                "Target Payback": cf_target["payback_str"],
                "Conservative ROI (%)": cf_cons["roi_pct"],
                "Downside ROI (%)": cf_down["roi_pct"],
                "Confidence": s["evidence_strength"],
                "Main Risk": s["operational_risk"]
            })

        return pd.DataFrame(rows)

    def reconcile_legacy_claims(self) -> Dict[str, Any]:
        """Provides formal mathematical reconciliation proving legacy claim inconsistencies.
        
        Legacy README claimed:
        Gross Recovery = ₹4.0 Cr, Net Benefit = ₹2.75 Cr, Cost = ₹10.0 Cr, ROI = 27.5%, Break-even = 8.5 months.
        """
        # Case A: If Cost = ₹10.0 Cr and Gross Recovery = ₹4.0 Cr:
        actual_net_case_a = 40_000_000 - 100_000_000  # -₹6.0 Cr
        actual_roi_case_a = (actual_net_case_a / 100_000_000) * 100.0  # -60.0%

        # Case B: If Net Benefit = +₹2.75 Cr on ₹10.0 Cr cost:
        required_gross_case_b = 100_000_000 + 27_500_000  # ₹12.75 Cr
        required_lift_case_b = (required_gross_case_b / 2_500_000_000) * 100.0  # 5.10%

        # Cash-flow payback for Case B
        cf_case_b = self.calculate_cash_flows(
            capex_inr=35_000_000,
            annual_opex_inr=65_000_000,
            annual_gross_recovery_inr=required_gross_case_b,
            ramp_up_months=2,
            horizon_months=12
        )

        return {
            "legacy_claims": {
                "documented_gross_recovery_inr": 40_000_000.0,
                "documented_net_benefit_inr": 27_500_000.0,
                "documented_cost_inr": 100_000_000.0,
                "documented_roi_pct": 27.5,
                "documented_break_even_months": 8.5
            },
            "mathematical_impossibility_proof": (
                "Under corporate finance identities: Incremental Net Benefit = Gross Recovery - Total Cost. "
                "If Total Cost = ₹10.0 Cr and Gross Recovery = ₹4.0 Cr, Incremental Net Benefit is -₹6.0 Cr (-60.0% ROI), "
                "representing a massive capital loss. These numbers cannot simultaneously hold."
            ),
            "reconciliation": {
                "interpretation_a_conservative_10cr": {
                    "scenario": "Full-scale deployment at Base 1.6% lift (₹4.0 Cr Gross Recovery)",
                    "gross_recovery_cr": 4.0,
                    "total_cost_cr": 10.0,
                    "net_benefit_cr": -6.0,
                    "roi_pct": -60.0,
                    "payback_period": "> 12 Months (No Year-1 Payback)"
                },
                "interpretation_b_target_10cr": {
                    "scenario": "Deployment parameters required to achieve +27.5% ROI (+₹2.75 Cr Net Benefit)",
                    "gross_recovery_cr": 12.75,
                    "required_lift_pct": 5.10,
                    "total_cost_cr": 10.0,
                    "net_benefit_cr": 2.75,
                    "roi_pct": 27.5,
                    "payback_period": f"{cf_case_b['payback_months']} Months"
                }
            },
            "reconciled_reality_case_a": {
                "scenario": "Full-scale deployment at Base 1.6% lift (₹4.0 Cr Gross Recovery)",
                "gross_recovery_cr": 4.0,
                "total_cost_cr": 10.0,
                "net_benefit_cr": round(actual_net_case_a / 10_000_000, 2),
                "roi_pct": round(actual_roi_case_a, 1),
                "payback_period": "> 12 Months (No Year-1 Payback)"
            },
            "reconciled_reality_case_b": {
                "scenario": "Deployment parameters required to achieve +27.5% ROI (+₹2.75 Cr Net Benefit)",
                "required_gross_recovery_cr": round(required_gross_case_b / 10_000_000, 2),
                "required_lift_pct_on_exposure": round(required_lift_case_b, 2),
                "total_cost_cr": 10.0,
                "net_benefit_cr": 2.75,
                "roi_pct": 27.5,
                "payback_period": f"{cf_case_b['payback_months']} Months"
            }
        }

    def get_staged_pilot_specs(self) -> Dict[str, Any]:
        """Provides the defensive ₹2.0 Crore Staged Pilot financial specifications."""
        capex = 6_000_000.0      # ₹0.6 Cr setup, model calibration, bureau API integration
        opex = 14_000_000.0      # ₹1.4 Cr 6-month operating expenses (model ops, scoring runs)
        total_cost = capex + opex  # ₹2.0 Cr
        pilot_accounts = 50_000
        pilot_exposure = 600_000_000.0  # ₹60 Cr addressable exposure
        expected_lift_rate = 0.035      # 3.5% lift on focused high-propensity accounts
        gross_recovery = pilot_exposure * expected_lift_rate  # ₹2.10 Cr
        net_benefit = gross_recovery - total_cost            # +₹0.10 Cr
        roi_6m = (net_benefit / total_cost) * 100.0          # +5.0%

        cf = self.calculate_cash_flows(
            capex_inr=capex,
            annual_opex_inr=opex,
            annual_gross_recovery_inr=gross_recovery,
            ramp_up_months=1,
            horizon_months=6
        )

        return {
            "pilot_commitment_cr": 2.0,
            "pilot_capital_cr": 2.0,
            "pilot_horizon_months": 6,
            "target_accounts": pilot_accounts,
            "target_exposure_cr": 60.0,
            "capex_cr": 0.60,
            "opex_cr": 1.40,
            "total_cost_cr": 2.00,
            "expected_lift_rate": expected_lift_rate,
            "expected_lift_pct": 3.50,
            "gross_incremental_recovery_cr": 2.10,
            "expected_gross_recovery_cr": 2.10,
            "net_benefit_cr": 0.10,
            "expected_net_benefit_cr": 0.10,
            "roi_pct": 5.0,
            "roi_6m_pct": 5.0,
            "pilot_break_even_months": cf["payback_months"] or 5.3,
            "break_even_months": cf["payback_months"] or 5.3,
            "holdout_control_pct": 10.0,
            "stage_gate_criteria": (
                "Do not deploy remaining ₹8.0 Cr unless Month 6 DiD confirms causal lift >= 2.50 pp "
                "with p < 0.05 and verified incremental net collections >= ₹2.10 Cr."
            )
        }

    def get_recommended_allocation(self) -> Dict[str, Any]:
        """Returns the executive investment recommendation."""
        pilot = self.get_staged_pilot_specs()
        return {
            "recommended_strategy": "Option 4: Better Borrower Targeting (via Controlled Staged Pilot)",
            "execution_model": "Staged Pilot Deployment (Do not commit ₹10 Cr full capital upfront)",
            "phase_1_capital_commitment_inr": pilot["total_cost_cr"] * 10_000_000,
            "phase_1_capital_commitment_cr": pilot["total_cost_cr"],
            "phase_1_time_horizon_months": pilot["pilot_horizon_months"],
            "phase_1_expected_gross_recovery_cr": pilot["expected_gross_recovery_cr"],
            "phase_1_net_benefit_cr": pilot["expected_net_benefit_cr"],
            "phase_1_roi_pct": pilot["roi_6m_pct"],
            "phase_1_break_even_months": pilot["break_even_months"],
            "gating_rule": pilot["stage_gate_criteria"],
            "downside_protection": "Limits capital at risk to ₹2.0 Cr while verifying econometric lift in production.",
            # Backward-compatible keys for dashboard callers
            "option_id": "better_targeting_staged_pilot",
            "recommended_option": "Option 4: Better Borrower Targeting (₹2.0 Cr Staged Pilot)",
            "incremental_recovery_inr": pilot["expected_gross_recovery_cr"] * 10_000_000,
            "net_benefit_inr": pilot["expected_net_benefit_cr"] * 10_000_000,
            "total_cost_inr": pilot["total_cost_cr"] * 10_000_000,
            "roi_percentage": pilot["roi_6m_pct"],
            "break_even_months": pilot["break_even_months"]
        }
