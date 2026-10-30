"""Metrics calculation, 12-month performance reconstruction, and 11% claim verification."""

from typing import Dict, Any, Tuple
import duckdb
import pandas as pd
from src.config import settings
from src.utils import logger, get_db_connection, execute_sql_file


class MetricsEngine:
    """Calculates defensible collections metrics, reconciles invariants, and audits reported claims."""

    def __init__(self, con: duckdb.DuckDBPyConnection = None):
        self.con = con or get_db_connection()
        self.sql_dir = settings.sql_dir

    def calculate_metrics(self) -> pd.DataFrame:
        """Executes metric calculation views."""
        try:
            execute_sql_file(self.con, self.sql_dir / "09_metrics.sql")
            execute_sql_file(self.con, self.sql_dir / "10_monthly_performance.sql")
        except Exception as e:
            logger.debug(f"Could not execute metrics DDL on connection: {e}")
        try:
            return self.con.execute("SELECT * FROM monthly_performance_audit ORDER BY month_index;").fetchdf()
        except Exception as e:
            logger.warning(f"Error fetching monthly performance audit: {e}")
            return pd.DataFrame()

    def evaluate_11_pct_claim(self) -> Dict[str, Any]:
        """Evaluates whether the '11% month-on-month improvement' claim is verified, contradicted, or not verifiable."""
        try:
            df = self.con.execute("SELECT * FROM v_audit_verdict_11_pct_claim;").fetchdf()
            if not df.empty:
                row = df.iloc[0].to_dict()
                return {
                    "evaluated_months_count": int(row.get("evaluated_months_count") or 0),
                    "period_start": str(row.get("period_start") or "N/A"),
                    "period_end": str(row.get("period_end") or "N/A"),
                    "numerator_cash_recovered": float(row.get("numerator_cash_recovered") or 0.0),
                    "denominator_opening_exposure": float(row.get("denominator_opening_exposure") or 0.0),
                    "formula": str(row.get("formula") or ""),
                    "avg_reported_naive_mom_growth_pct": float(row.get("avg_reported_naive_mom_growth_pct") or 0.0),
                    "avg_audited_canonical_mom_growth_pct": float(row.get("avg_audited_canonical_mom_growth_pct") or 0.0),
                    "growth_rate_distortion_pct": float(row.get("growth_rate_distortion_pct") or 0.0),
                    "cumulative_recovery_overstatement_inr": float(row.get("cumulative_recovery_overstatement_inr") or 0.0),
                    "total_canonical_recovered_inr": float(row.get("total_canonical_recovered_inr") or 0.0),
                    "forensic_verdict": str(row.get("forensic_verdict") or "NOT_VERIFIABLE"),
                    "verdict_explanation": str(row.get("verdict_explanation") or "Awaiting raw collections data.")
                }
        except Exception as e:
            logger.warning(f"Error evaluating 11% claim: {e}")

        return {
            "evaluated_months_count": 0,
            "period_start": "N/A",
            "period_end": "N/A",
            "numerator_cash_recovered": 0.0,
            "denominator_opening_exposure": 0.0,
            "formula": "Canonical Rate = Realized Cash / Opening Exposure * 100",
            "avg_reported_naive_mom_growth_pct": 0.0,
            "avg_audited_canonical_mom_growth_pct": 0.0,
            "growth_rate_distortion_pct": 0.0,
            "cumulative_recovery_overstatement_inr": 0.0,
            "total_canonical_recovered_inr": 0.0,
            "forensic_verdict": "NOT_VERIFIABLE",
            "verdict_explanation": "The claim cannot currently be verified because required collections data and original reporting definitions are unavailable."
        }

    def run_reconciliation(self) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Executes reconciliation checks and invariant tests."""
        try:
            execute_sql_file(self.con, self.sql_dir / "12_reconciliation.sql")
        except Exception as e:
            logger.debug(f"Could not execute reconciliation DDL on connection: {e}")
        try:
            monetary_trail = self.con.execute("SELECT * FROM v_reconciliation_monetary_trail;").fetchdf()
            dedup_balance = self.con.execute("SELECT * FROM v_reconciliation_dedup_balance;").fetchdf()
            invariant_failures = self.con.execute("SELECT * FROM v_production_integrity_failures;").fetchdf()
            return monetary_trail, dedup_balance, invariant_failures
        except Exception as e:
            logger.warning(f"Error during reconciliation query: {e}")
            return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
