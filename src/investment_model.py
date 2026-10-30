"""Financial investment evaluation model for ₹10 Crore capital allocation across 6 strategic options.

Provides rigorous, mathematically verified evaluation of:
- Gross Incremental Recovery = Addressable Exposure * Lift Rate
- Incremental Net Benefit = Gross Incremental Recovery - Total Investment Cost
- ROI (%) = (Incremental Net Benefit / Total Investment Cost) * 100
- Break-even Horizon (Months) = Ramp-up Months + (Total Cost / Monthly Gross Run-rate)
- Mathematical reconciliation of legacy claim contradictions
- Risk-hedged Staged Pilot allocation (₹2.0 Cr commitment)
"""

from typing import Dict, Any, List
import pandas as pd
from src.config import settings
from src.utils import logger


class InvestmentModel:
    """Configurable financial model evaluating ROI, Net Benefit, break-even, and pilot gating."""

    def __init__(self, capital_cr: float = 10.0):
        self.capital_cr = capital_cr
        self.capital_inr = capital_cr * 10_000_000  # ₹10 Crore in INR
        self.horizon_months = 12

    def get_investment_options_specs(self) -> List[Dict[str, Any]]:
        """Defines the 6 strategic investment options with baseline unit economics and multi-scenarios."""
        return [
            {
                "id": "better_targeting",
                "name": "Option 4: Better Borrower Targeting",
                "addressable_accounts": 150_000,
                "addressable_exposure_cr": 250.0,
                "capex_inr": 35_000_000,        # ₹3.5 Cr software / ML infra / vendor data
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
        """Evaluates all 6 options across scenarios and computes financial metrics.
        
        Strictly enforces:
        Incremental Net Benefit = Gross Incremental Recovery - Total Investment Cost.
        ROI = (Incremental Net Benefit / Total Investment Cost) * 100.
        """
        specs = self.get_investment_options_specs()
        rows = []

        for s in specs:
            exposure_inr = s["addressable_exposure_cr"] * 10_000_000
            total_cost = s["total_cost_inr"]

            # Scenario recoveries (Gross Incremental Cash)
            gross_base = exposure_inr * s["base_lift_rate"]
            gross_target = exposure_inr * s.get("target_roi_lift_rate", s["base_lift_rate"])
            gross_conservative = exposure_inr * s["conservative_lift_rate"]
            gross_upside = exposure_inr * s["upside_lift_rate"]
            gross_downside = exposure_inr * s["downside_lift_rate"]

            # Incremental Net Benefit = Gross Recovery - Total Cost
            net_base = gross_base - total_cost
            net_target = gross_target - total_cost
            net_conservative = gross_conservative - total_cost
            net_upside = gross_upside - total_cost
            net_downside = gross_downside - total_cost

            # ROI (%) = Net Benefit / Total Cost
            roi_base = (net_base / total_cost) * 100.0
            roi_target = (net_target / total_cost) * 100.0
            roi_conservative = (net_conservative / total_cost) * 100.0
            roi_upside = (net_upside / total_cost) * 100.0
            roi_downside = (net_downside / total_cost) * 100.0

            # Break-even in months: ramp_up + total_cost / (gross_base / active_months)
            active_months = max(1, 12 - s["ramp_up_months"])
            monthly_gross_base = gross_base / active_months
            break_even_base_months = round(s["ramp_up_months"] + (total_cost / max(1.0, monthly_gross_base)), 1)

            # Target break-even (under target lift achieving +27.5% ROI)
            monthly_gross_target = gross_target / active_months
            break_even_target_months = round(s["ramp_up_months"] + (total_cost / max(1.0, monthly_gross_target)), 1)

            rows.append({
                "Investment Option": s["name"],
                "Total Cost (₹ Cr)": round(total_cost / 10_000_000, 1),
                "Addressable Exposure (₹ Cr)": s["addressable_exposure_cr"],
                "Base Incremental Recovery (₹ Cr)": round(gross_base / 10_000_000, 2),
                "Base Net Benefit (₹ Cr)": round(net_base / 10_000_000, 2),
                "Base ROI (%)": round(roi_base, 1),
                "Target Lift Needed for 27.5% ROI (%)": round(s.get("target_roi_lift_rate", 0.0) * 100.0, 2),
                "Target Recovery for 27.5% ROI (₹ Cr)": round(gross_target / 10_000_000, 2),
                "Target Break-even (Months)": break_even_target_months,
                "Conservative ROI (%)": round(roi_conservative, 1),
                "Downside ROI (%)": round(roi_downside, 1),
                "Base Break-even (Months)": break_even_base_months,
                "Confidence": s["evidence_strength"],
                "Main Risk": s["operational_risk"]
            })

        df = pd.DataFrame(rows)
        return df.sort_values(by="Base Net Benefit (₹ Cr)", ascending=False).reset_index(drop=True)

    @staticmethod
    def reconcile_legacy_claims() -> Dict[str, Any]:
        """Mathematically reconciles the legacy claims:
        ₹4 Cr incremental recovery, ₹2.75 Cr net benefit, ₹10 Cr capital outlay, 27.5% ROI, and 8.5-month break-even.
        
        Proof of Contradiction:
        1. Net Benefit = Gross Recovery - Total Cost.
           If Gross = ₹4.0 Cr and Total Cost = ₹10.0 Cr, then Net Benefit = 4.0 - 10.0 = -₹6.0 Cr (-60% ROI).
        2. If Net Benefit = +₹2.75 Cr on ₹10.0 Cr Total Cost, then ROI = (2.75 / 10.0) * 100 = +27.5%.
           In this case, Gross Recovery MUST equal: Total Cost + Net Benefit = 10.0 + 2.75 = ₹12.75 Cr.
           On ₹250 Cr addressable exposure, required lift is: 12.75 / 250.0 = 5.10% (510 bps).
        3. If Gross Recovery = ₹4.0 Cr and Net Benefit = +₹2.75 Cr, Total Cost MUST equal 4.0 - 2.75 = ₹1.25 Cr,
           yielding an ROI of (2.75 / 1.25) * 100 = 220%.
        4. For break-even to occur in 8.5 months on ₹10 Cr cost with 2 months ramp-up:
           Active recovery period = 6.5 months.
           Required monthly cash flow = 10.0 / 6.5 = ₹1.54 Cr/mo.
           Required annual gross recovery = ₹15.4 Cr (6.16% lift).
        """
        return {
            "finding": "Legacy claims conflate three distinct operational and financial scenarios",
            "proof_of_contradiction": [
                "Gross ₹4.0 Cr on Cost ₹10.0 Cr yields Net Benefit -₹6.0 Cr (-60% ROI), NOT +₹2.75 Cr.",
                "Net Benefit +₹2.75 Cr (27.5% ROI on ₹10 Cr) requires Gross Recovery of ₹12.75 Cr (5.10% lift).",
                "Gross ₹4.0 Cr with Net Benefit +₹2.75 Cr requires Cost of ₹1.25 Cr (220% ROI).",
                "8.5-month break-even on ₹10 Cr requires ₹15.4 Cr annualized gross recovery (6.16% lift)."
            ],
            "reconciliation": {
                "interpretation_a_conservative_10cr": {
                    "total_cost_cr": 10.0,
                    "gross_recovery_cr": 4.0,
                    "net_benefit_cr": -6.0,
                    "roi_pct": -60.0,
                    "break_even_months": 27.0,
                    "verdict": "Unviable as a 1-year full commitment. Sinks ₹10 Cr into unvalidated model."
                },
                "interpretation_b_target_10cr": {
                    "total_cost_cr": 10.0,
                    "gross_recovery_cr": 12.75,
                    "net_benefit_cr": 2.75,
                    "roi_pct": 27.5,
                    "required_lift_pct": 5.10,
                    "break_even_months": 9.8,
                    "verdict": "Achievable full-scale target if pilot demonstrates >5.0% lift on early DPD."
                },
                "interpretation_c_recommended_staged_pilot": {
                    "pilot_cost_cr": 2.0,
                    "pilot_addressable_exposure_cr": 60.0,
                    "pilot_expected_gross_cr": 2.10,
                    "pilot_net_benefit_cr": 0.10,
                    "pilot_roi_pct": 5.0,
                    "break_even_months": 5.7,
                    "verdict": "Recommended executive action: Limits downside while testing true causal lift."
                }
            }
        }

    def get_staged_pilot_specs(self) -> Dict[str, Any]:
        """Returns the complete financial specification for the recommended ₹2.0 Crore staged pilot."""
        return {
            "pilot_name": "Stage 1 Pilot: Dynamic Propensity Borrower Targeting",
            "pilot_capital_cr": 2.0,
            "pilot_duration_months": 6,
            "capex_setup_cr": 0.75,     # Feature store setup & vendor credit scoring data
            "opex_run_cr": 1.25,        # Bureau API calls & ML engineering support for 6 months
            "target_accounts": 50_000,
            "target_exposure_cr": 60.0,
            "expected_lift_rate": 0.035, # 3.5% lift on targeted sub-cohort
            "gross_incremental_recovery_cr": 2.10,
            "net_benefit_cr": 0.10,
            "roi_pct": 5.0,
            "pilot_break_even_months": 5.7,
            "gating_criteria_for_stage_2": (
                "Statistically significant causal lift >= 2.5% (p < 0.05) measured against a 10% un-contacted "
                "randomized holdout control group over 90 days of active dialing."
            ),
            "stage_2_expansion": {
                "remaining_capital_cr": 8.0,
                "projected_gross_recovery_cr": 11.40,
                "projected_net_benefit_cr": 3.40,
                "full_scale_break_even_months": 8.5
            }
        }

    def get_recommended_allocation(self) -> Dict[str, Any]:
        """Provides the defensible strategic leadership recommendation."""
        pilot = self.get_staged_pilot_specs()
        recon = self.reconcile_legacy_claims()

        return {
            "recommended_strategy": "Option 4: Better Borrower Targeting (via Staged Pilot)",
            "recommended_option": "Option 4: Better Borrower Targeting (via Staged Pilot)",
            "initial_capital_commitment_cr": pilot["pilot_capital_cr"],
            "total_budget_cr": self.capital_cr,
            "pilot_expected_recovery_cr": pilot["gross_incremental_recovery_cr"],
            "pilot_net_benefit_cr": pilot["net_benefit_cr"],
            "pilot_break_even_months": pilot["pilot_break_even_months"],
            "expected_incremental_recovery_cr": pilot["gross_incremental_recovery_cr"],
            "expected_net_benefit_cr": pilot["net_benefit_cr"],
            "expected_roi_pct": pilot["roi_pct"],
            "break_even_months": pilot["pilot_break_even_months"],
            "downside_roi_pct": -60.0,
            "mathematical_reconciliation": recon["proof_of_contradiction"],
            "verdict_rationale": (
                "Deploying the full ₹10 Cr commitment upfront into Option 4 under a baseline 1.6% lift yields "
                "a 1-year Net Benefit of -₹6.0 Cr (-60% ROI), failing break-even in Year 1. "
                "To achieve the documented +27.5% ROI (+₹2.75 Cr Net Benefit), Gross Recovery must reach ₹12.75 Cr "
                "(5.1% lift on ₹250 Cr exposure). "
                "Therefore, the only defensible corporate recommendation is an immediate ₹2.0 Cr Staged Randomized Pilot "
                "(50,000 accounts, ₹60 Cr exposure) with a 10% holdout control. This validates true causal lift while "
                "breaking even in 5.7 months, and protects ₹8.0 Cr of capital from unhedged downside risk."
            )
        }
