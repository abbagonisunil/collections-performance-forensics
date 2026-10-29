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
        execute_sql_file(self.con, self.sql_dir / "09_metrics.sql")
        execute_sql_file(self.con, self.sql_dir / "10_monthly_performance.sql")
        try:
            return self.con.execute("SELECT * FROM monthly_performance_audit ORDER BY month_index;").fetchdf()
        except Exception as e:
            logger.warning(f"Error fetching monthly performance audit: {e}")
            return pd.DataFrame()

    def evaluate_11_pct_claim(self) -> Dict[str, Any]:
        """Evaluates whether the '11% month-on-month improvement' claim is verified or disproven."""
        try:
            res = self.con.execute("SELECT * FROM v_audit_verdict_11_pct_claim;").fetchone()
            if res:
                return {
                    "avg_reported_naive_mom_growth_pct": float(res[0] or 0.0),
                    "avg_audited_canonical_mom_growth_pct": float(res[1] or 0.0),
                    "growth_rate_distortion_pct": float(res[2] or 0.0),
                    "cumulative_recovery_overstatement_inr": float(res[3] or 0.0),
                    "forensic_verdict": str(res[4] or "UNVERIFIED")
                }
        except Exception as e:
            logger.warning(f"Error evaluating 11% claim: {e}")

        return {
            "avg_reported_naive_mom_growth_pct": 0.0,
            "avg_audited_canonical_mom_growth_pct": 0.0,
            "growth_rate_distortion_pct": 0.0,
            "cumulative_recovery_overstatement_inr": 0.0,
            "forensic_verdict": "DATA_AWAITING_INGESTION"
        }

    def run_reconciliation(self) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Executes reconciliation checks and invariant tests."""
        execute_sql_file(self.con, self.sql_dir / "12_reconciliation.sql")
        try:
            monetary_trail = self.con.execute("SELECT * FROM v_reconciliation_monetary_trail;").fetchdf()
            dedup_balance = self.con.execute("SELECT * FROM v_reconciliation_dedup_balance;").fetchdf()
            invariant_failures = self.con.execute("SELECT * FROM v_production_integrity_failures;").fetchdf()
            return monetary_trail, dedup_balance, invariant_failures
        except Exception as e:
            logger.warning(f"Error during reconciliation query: {e}")
            return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
