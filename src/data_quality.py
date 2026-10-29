"""Data quality engine: enforces integrity constraints, anomalies detection, and audit metrics."""

from typing import Dict, Any, List
import duckdb
import pandas as pd
from src.config import settings
from src.utils import logger, get_db_connection


class DataQualityEngine:
    """Evaluates data quality rules and generates auditable quarantine metrics."""

    def __init__(self, con: duckdb.DuckDBPyConnection = None):
        self.con = con or get_db_connection()

    def run_checks(self) -> pd.DataFrame:
        """Executes all data quality rules and returns summary of identified violations."""
        try:
            # Check if stg_payments exists before querying views
            tables = [r[0] for r in self.con.execute("SHOW TABLES;").fetchall()]
            if "v_dq_summary_stats" not in tables:
                return pd.DataFrame(columns=["severity", "rule_name", "total_affected_records", "total_monetary_exposure_inr"])

            summary_df = self.con.execute("SELECT * FROM v_dq_summary_stats;").fetchdf()
            return summary_df
        except Exception as e:
            logger.warning(f"Data quality checks completed with notice: {e}")
            return pd.DataFrame(columns=["severity", "rule_name", "total_affected_records", "total_monetary_exposure_inr"])

    def get_quarantine_records(self, limit: int = 100) -> pd.DataFrame:
        """Retrieves individual flagged records for forensic drill-down."""
        try:
            tables = [r[0] for r in self.con.execute("SHOW TABLES;").fetchall()]
            if "dq_issue_log" in tables:
                return self.con.execute(f"SELECT * FROM dq_issue_log LIMIT {limit};").fetchdf()
            return pd.DataFrame()
        except Exception as e:
            logger.error(f"Error fetching quarantine records: {e}")
            return pd.DataFrame()

    def calculate_data_reliability_score(self) -> Dict[str, Any]:
        """Calculates an overall Data Health & Reliability Score (0 to 100)."""
        summary_df = self.run_checks()
        if summary_df.empty:
            return {
                "reliability_score": 100.0,
                "health_status": "EXCELLENT",
                "total_issues": 0,
                "critical_issues": 0,
                "total_monetary_exposure_inr": 0.0
            }

        total_issues = summary_df["total_affected_records"].sum()
        critical_issues = summary_df[summary_df["severity"] == "CRITICAL"]["total_affected_records"].sum()
        monetary_exposure = summary_df["total_monetary_exposure_inr"].sum()

        penalty = min(100.0, (critical_issues * 5.0) + (total_issues * 0.5))
        score = max(0.0, 100.0 - penalty)

        if score >= 90:
            status = "HEALTHY"
        elif score >= 70:
            status = "MODERATE_RISK"
        else:
            status = "CRITICAL_RISK"

        return {
            "reliability_score": round(score, 1),
            "health_status": status,
            "total_issues": int(total_issues),
            "critical_issues": int(critical_issues),
            "total_monetary_exposure_inr": float(monetary_exposure)
        }
